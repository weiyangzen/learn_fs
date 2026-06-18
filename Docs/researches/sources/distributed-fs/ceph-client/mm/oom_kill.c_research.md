# sources/distributed-fs/ceph-client/mm/oom_kill.c

## Purpose

`oom_kill.c` implements Linux out-of-memory victim selection, diagnostics, kill signaling, OOM reaping, OOM killer disable/enable coordination, memory-cgroup OOM handling, and the `process_mrelease` syscall. It is invoked when reclaim and allocation fallback cannot satisfy memory demand.

For Ceph-client workloads, this code matters under heavy page-cache, writeback, metadata, or network-buffer pressure. It decides whether a Ceph process, helper, or unrelated task is killed when system or memcg memory is exhausted.

## Important APIs, Types, And Functions

- Sysctl state: `panic_on_oom`, `oom_kill_allocating_task`, and `oom_dump_tasks`.
- Locks and counters: exported `oom_lock`, `oom_adj_mutex`, `oom_victims`, `oom_victims_wait`, and `oom_killer_disabled`.
- Victim scoring and selection: `oom_badness()`, `constrained_alloc()`, `oom_evaluate_task()`, and `select_bad_process()`.
- Eligibility helpers: `oom_cpuset_eligible()`, `find_lock_task_mm()`, `oom_unkillable_task()`, `task_will_free_mem()`, and `process_shares_mm()`.
- Diagnostic helpers: `dump_header()`, `dump_tasks()`, `dump_task()`, `dump_oom_victim()`, and `should_dump_unreclaim_slab()`.
- OOM reaper under `CONFIG_MMU`: `__oom_reap_task_mm()`, `oom_reap_task_mm()`, `oom_reap_task()`, `oom_reaper()`, `wake_oom_reaper()`, and `queue_oom_reaper()`.
- Kill path: `mark_oom_victim()`, `__oom_kill_process()`, `oom_kill_process()`, and `oom_kill_memcg_member()`.
- Public controls: `exit_oom_victim()`, `oom_killer_enable()`, `oom_killer_disable()`, `register_oom_notifier()`, `unregister_oom_notifier()`, `out_of_memory()`, `pagefault_out_of_memory()`, and `process_mrelease()`.

## Control Flow

`oom_init()` starts the `oom_reaper` kernel thread on MMU builds and registers VM sysctls. Runtime OOM handling enters `out_of_memory()` with an `oom_control` describing allocation context, gfp mask, order, zonelist, nodemask, and optional memcg.

The first stage handles bypasses. If the OOM killer is disabled, it returns false. For global OOM, notifier callbacks get a chance to free memory; if they report freed pages, the OOM path succeeds without killing. If current is already exiting or has a fatal path that will free memory, it is marked as an OOM victim and queued for reaping. GFP contexts without `__GFP_FS` avoid global OOM killing because I/O-less reclaim is not compensated here.

`constrained_alloc()` classifies the allocation as global, cpuset-constrained, mempolicy-constrained, or memcg-constrained and sets `oc->totalpages` to the appropriate scoring universe. `check_panic_on_oom()` enforces `panic_on_oom` policy, with special handling for constrained OOM and sysrq OOM.

If `oom_kill_allocating_task` is enabled and current is eligible, current is selected. Otherwise `select_bad_process()` scans either memcg tasks or all processes. `oom_evaluate_task()` filters unkillable tasks, tasks outside the OOM domain, existing OOM victims that may still free memory, and tasks with unusable scores. It chooses `oom_task_origin()` tasks immediately or the highest `oom_badness()` score. `oom_badness()` scores RSS, swapents, and page-table memory, adjusted by `oom_score_adj`, while excluding init, kthreads, `OOM_SCORE_ADJ_MIN`, already reaped `MMF_OOM_SKIP`, and vfork-in-progress tasks.

`oom_kill_process()` first checks whether the selected task is already exiting and likely to free memory. If so, it marks and reaps without logging a full kill. Otherwise it rate-limits diagnostics, prints memory/task context, resolves an optional memcg OOM group, and calls `__oom_kill_process()`. The kill function locks a thread with a live `mm`, grabs the mm, sends `SIGKILL`, marks the victim with `TIF_MEMDIE`, records events, kills other user processes sharing the same mm across thread groups, and queues the mm for reaping unless init pins it.

The OOM reaper waits for queued victims, sleeps briefly after kill through a timer, then tries to take `mmap_read_trylock()` and walks VMAs in reverse. It skips hugetlb and PFNMAP, reaps anonymous or private mappings with `zap_vma_for_reaping()`, sets `MMF_UNSTABLE`, retries a bounded number of times, then sets `MMF_OOM_SKIP` and drops the queued task reference. This hides the mm from later OOM selection.

`process_mrelease(pidfd, flags)` lets userspace reclaim an exiting process's anonymous/private memory proactively. It validates flags, resolves a pidfd, locks a task with an mm, requires `task_will_free_mem()` or already completed reaping, and invokes `__oom_reap_task_mm()` under `mmap_read_lock_killable()`.

## State And Persistence Behavior

OOM decisions are transient, but they mutate task and mm state. Victims get `TIF_MEMDIE`, `signal->oom_mm`, `MMF_OOM_REAP_QUEUED`, `MMF_UNSTABLE`, and eventually `MMF_OOM_SKIP`. `oom_victims` tracks victims in flight so `oom_killer_disable()` can wait. The reaper list is protected by a spinlock and uses task references until reaping completes.

Sysctls persist runtime policy until changed. The notifier chain persists registered subsystems that can respond to global OOM before killing.

## Dependencies And Integration Points

This file depends on task lists and locking, memcg, cpuset, mempolicy, reclaim, slab diagnostics, tracepoints, sysctl, pidfd, freezer, credentials, mmu notifiers, and VMA zapping. It integrates with page allocation, page fault handling, memory cgroups, suspend/freezer behavior, and userspace OOM tooling.

Ceph-client integration is indirect through memory use. Ceph workloads in cgroups can trigger memcg OOM, and Ceph page-cache pressure can contribute to global OOM. `oom_score_adj`, cgroup OOM grouping, and dirty/writeback behavior all affect whether Ceph-related processes are selected.

## Risks And Edge Cases

- Victim scoring is heuristic and can be skewed by `oom_score_adj`, memcg limits, cpuset/mempolicy constraints, and shared mm users.
- Existing OOM victims can abort further selection to avoid over-killing, potentially prolonging stalls if the victim cannot exit.
- Reaper races with exit paths and mmap locks; it uses trylock/retry to avoid deadlocks but may fail and mark skip after diagnostics.
- Killing processes sharing an mm must avoid init and kthreads; pinned init mm disables reaping for that mm.
- `panic_on_oom=2` is fatal except sysrq OOM; `panic_on_oom=1` only panics for unconstrained OOM.
- GFP_NOFS global allocation failures can return without killing, relying on caller/reclaim behavior.
- `process_mrelease()` only works for tasks already exiting or already reaped; otherwise it returns `-EINVAL`.

## Test Signals

- Kernel selftests and stress workloads should cover global OOM, memcg OOM, cpuset/mempolicy-constrained OOM, sysrq OOM, and `oom_score_adj` exclusion.
- Verify sysctl behavior for panic, allocating-task kill, and task dump output.
- Exercise OOM reaper tracepoints, `MMF_OOM_SKIP`, and `process_mrelease()` with exiting processes.
- Cgroup tests should validate OOM group kill and protected memory reporting.
- Ceph-oriented stress tests should run metadata and writeback-heavy clients under memcg limits to observe expected victim selection and absence of kernel deadlock.
