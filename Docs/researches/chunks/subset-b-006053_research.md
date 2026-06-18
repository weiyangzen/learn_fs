# sources/distributed-fs/ceph-client/kernel/sched/ext.c lines 8986-9953

## Scope

This chunk covers the final `sched_ext` implementation range in `kernel/sched/ext.c`. It starts with the BPF dispatch-queue iterator helpers and ends at `scx_init()` registration through `__initcall(scx_init)`.

The code is mostly BPF-facing control-plane surface for sched_ext: kfuncs that let BPF schedulers inspect and manipulate dispatch queues, report errors and dumps, query CPU/task state, adjust CPU performance targets, read scheduler event counters, and obtain task cgroups. It also defines the "any-context" kfunc BTF set, verifier-time kfunc context filtering, and boot-time registration of kfunc sets, struct_ops, PM notifier, and `/sys/kernel/sched_ext`.

## Purpose

The range exposes stable kernel helpers to BPF schedulers while constraining where each helper can be used. It bridges BPF programs to SCX internal state such as `struct scx_sched`, `struct scx_dispatch_q`, runqueues, per-CPU event counters, dump buffers, global cpumasks, and cgroup scheduler state.

The major responsibilities are:

- Iterating user dispatch queues from BPF with `bpf_for_each()` while preserving queue ordering and cursor cleanup.
- Allowing lockless DSQ inspection and asynchronous DSQ re-enqueue requests.
- Formatting BPF-provided strings for graceful exits, fatal errors, and debug dump output.
- Providing BPF scheduler introspection helpers for CPU capacity/frequency, CPU count, NUMA node count, cpumasks, task CPU/running state, current tasks, locked runqueues, scheduler time, and aggregated SCX events.
- Returning stable scheduler cgroups for tasks when cgroup scheduling is enabled.
- Publishing the final `scx_kfunc_ids_any` BTF kfunc set and filtering all SCX kfunc calls according to BPF program type and attached `sched_ext_ops` member.
- Initializing the sched_ext BPF surface, idle tracking, struct_ops registration, PM notifications, and sysfs directory at kernel init time.

## Important APIs, Types, and Functions

- `bpf_iter_scx_dsq_new()` initializes an opaque BPF iterator for a user DSQ. It verifies kernel/private iterator layout assumptions with `BUILD_BUG_ON()`, clears `kit->dsq` so `next()` and `destroy()` are safe after failed creation, resolves the active scheduler with `scx_prog_sched(aux)`, rejects unsupported flags, looks up the DSQ with `find_user_dsq()`, and seeds the cursor with `INIT_DSQ_LIST_CURSOR()`.
- `bpf_iter_scx_dsq_next()` returns the next queued `task_struct` by taking the DSQ raw spinlock and calling `nldsq_cursor_next_task()`. The lower-level cursor implementation only exposes tasks that were already queued when the cursor was initialized.
- `bpf_iter_scx_dsq_destroy()` removes the cursor node from the DSQ list if still linked, under the DSQ raw spinlock, and clears `kit->dsq`.
- `scx_bpf_dsq_peek()` returns `rcu_dereference(dsq->first_task)` for a user DSQ. It rejects builtin DSQs and non-existent DSQs with `scx_error()` because a lockless peek on local/global builtin queues is not supported here.
- `scx_bpf_dsq_reenq()` validates `SCX_REENQ_*` flags, defaults no filter bits to `SCX_REENQ_ANY`, resolves a local/user DSQ through `find_dsq_for_dispatch()`, and schedules asynchronous re-enqueue processing with `schedule_dsq_reenq()`.
- `scx_bpf_reenqueue_local___v2()` is the current generic wrapper for re-enqueueing the caller CPU's local DSQ via `scx_bpf_dsq_reenq(SCX_DSQ_LOCAL, 0, aux)`. The older `scx_bpf_reenqueue_local()` in the previous chunk is limited to `ops.cpu_release()`.
- `__bstr_format()` is the shared string formatter for BPF string helpers. It validates packed varargs size, copies arguments with `copy_from_kernel_nofault()`, prepares binary printf data with `bpf_bprintf_prepare()`, writes into a fixed line buffer with `bstr_printf()`, and reports failures through `scx_error()`.
- `bstr_format()` specializes `__bstr_format()` for `struct scx_bstr_buf`.
- `scx_bpf_exit_bstr()` formats a BPF message under `scx_exit_bstr_buf_lock` and calls `scx_exit(..., SCX_EXIT_UNREG_BPF, exit_code, ...)` to request graceful scheduler unregister.
- `scx_bpf_error_bstr()` uses the same serialized format buffer but exits with `SCX_EXIT_ERROR_BPF`, treating the BPF scheduler condition as fatal.
- `scx_bpf_dump_bstr()` appends formatted BPF scheduler dump text into `scx_dump_data.buf.line`, validates that it is called on the dump CPU, and flushes through `ops_dump_flush()` when the buffer fills or reaches a newline.
- `scx_bpf_cpuperf_cap()` and `scx_bpf_cpuperf_cur()` return architecture-provided CPU capacity and current frequency capacity, falling back to `SCX_CPUPERF_ONE` when there is no active scheduler or the CPU is invalid.
- `scx_bpf_cpuperf_set()` validates a target performance value, checks CPU validity, avoids ABBA deadlocks by refusing remote CPU changes while another rq is locked, optionally locks the target rq, updates `rq->scx.cpuperf_target`, and calls `cpufreq_update_util()`.
- `scx_bpf_nr_node_ids()` and `scx_bpf_nr_cpu_ids()` expose kernel topology limits to BPF.
- `scx_bpf_get_possible_cpumask()`, `scx_bpf_get_online_cpumask()`, and `scx_bpf_put_cpumask()` provide trusted global cpumask pointers for BPF verifier acquire/release semantics. `put` is intentionally empty because the masks are global and not actually refcounted.
- `scx_bpf_task_running()` and `scx_bpf_task_cpu()` expose task runtime state using `task_rq(p)->curr == p` and `task_cpu(p)`.
- `scx_bpf_cpu_rq()` returns `cpu_rq(cpu)` after scheduler and CPU validation, but emits a one-time deprecation warning through `sch->warned_deprecated_rq`.
- `scx_bpf_locked_rq()` returns `scx_locked_rq()` only when SCX currently holds an rq lock; otherwise it reports an SCX error and returns `NULL`.
- `scx_bpf_cpu_curr()` returns a remote CPU's current task through `rcu_dereference(cpu_rq(cpu)->curr)` after active scheduler and CPU validation.
- `scx_bpf_now()` gives BPF schedulers a fast per-CPU scheduler clock. With preemption disabled, it uses cached `rq->scx.clock` when `SCX_RQ_CLK_VALID` is set, otherwise reads `sched_clock_cpu(cpu_of(rq))`.
- `scx_read_events()` aggregates per-CPU `struct scx_event_stats` from `sch->pcpu` into one system-wide result with `scx_agg_event()` for the enumerated `SCX_EV_*` counters.
- `scx_bpf_events()` RCU-reads `scx_root`, returns zeroed counters if sched_ext is inactive, and copies only `min(events__sz, sizeof(*events))` bytes to tolerate BPF programs built against different `vmlinux.h` layouts.
- `scx_bpf_task_cgroup()` is compiled under `CONFIG_CGROUP_SCHED`. It validates the BPF scheduler context and task authority with `scx_kf_arg_task_ok()`, returns the task scheduler cgroup from `p->sched_task_group`, and always takes a cgroup reference with `cgroup_get()`.
- `scx_kfunc_ids_any` is the final BTF kfunc ID set for helpers allowed broadly across SCX contexts, tracing, and syscall test programs. It includes DSQ observation/re-enqueue, BPF iterators, exit/error/dump strings, CPU performance helpers, topology/cpumask helpers, task/CPU/rq helpers, clock/event helpers, and optionally task cgroup access.
- `enum scx_kf_allow_flags` and `scx_kf_allow_flags[]` define verifier-time permissions for context-sensitive kfunc groups by `sched_ext_ops` member.
- `scx_kfunc_context_filter()` is the central BPF verifier filter. It identifies which SCX kfunc set contains the target kfunc, permits or denies by BPF program type, handles early verification before `prog->aux->st_ops` is populated, rejects non-SCX struct_ops, and finally checks the attached op's allow flags.
- `scx_init()` registers all SCX kfunc sets, initializes idle tracking, registers `bpf_sched_ext_ops`, registers the PM notifier, creates `/sys/kernel/sched_ext`, and installs the global sysfs attribute group.

Key state carriers referenced in this chunk include `struct scx_sched`, `struct scx_dispatch_q`, `struct bpf_iter_scx_dsq_kern`, `struct bpf_iter_scx_dsq`, `struct scx_dsq_list_node`, `struct scx_bstr_buf`, `struct scx_dump_data`, `struct scx_event_stats`, `struct scx_sched_pcpu`, `struct rq`, `struct task_struct`, `struct task_group`, `struct cgroup`, `struct bpf_prog`, `struct bpf_prog_aux`, and `struct btf_kfunc_id_set`.

## Control Flow

DSQ iterator creation starts from a BPF-visible `struct bpf_iter_scx_dsq`. The kernel casts it to `struct bpf_iter_scx_dsq_kern`, proves that the hidden kernel layout fits the opaque BPF layout, initializes the iterator as failed-safe, and then binds it to a user DSQ if the calling BPF program has an active `struct scx_sched`. Iteration steps take the DSQ lock, advance the cursor through `nldsq_cursor_next_task()`, and return one task at a time. Destruction is called regardless of creation success, so both `new()` and `destroy()` are defensive around `kit->dsq == NULL`.

DSQ observation and re-enqueue have different consistency models. `scx_bpf_dsq_peek()` is explicitly lockless and returns only a point-in-time first-task pointer for user DSQs. `scx_bpf_dsq_reenq()` instead schedules deferred work: it disables preemption for stable current-CPU/rq assumptions, validates flags, resolves the DSQ, and delegates to `schedule_dsq_reenq()`. The deferred path records local or user DSQ re-enqueue requests in per-rq lists and kicks deferred processing, avoiding direct queue walking from arbitrary BPF call contexts.

The BPF string helpers run through a shared formatting pipeline. `__bstr_format()` treats the BPF-supplied data as packed 64-bit varargs, rejects misaligned or oversized argument blocks, copies the data through nofault kernel reads, prepares the format with the BPF bprintf machinery, writes into a bounded line buffer, and cleans up temporary printf state. Exit and error helpers serialize access to the global `scx_exit_bstr_buf` before calling `scx_exit()`. Dump helpers use the per-dump `scx_dump_data` buffer, append at `dd->cursor`, and flush through `ops_dump_flush()` on newline or overflow.

CPU performance helpers first establish scheduler and CPU validity. Read helpers simply return architecture capacity/frequency scale values. The setter additionally handles lock ordering: if an SCX callback already holds an rq lock, it only allows setting the same rq's target to avoid cross-rq ABBA deadlocks. Without an existing locked rq, it locks the target rq, updates the rq clock, writes `rq->scx.cpuperf_target`, notifies schedutil via `cpufreq_update_util()`, and unlocks.

Topology, cpumask, task, and rq helpers are small read paths but carry verifier and locking assumptions. Cpumask getters use BPF acquire/release annotations even though the returned masks are immutable globals. `scx_bpf_locked_rq()` requires an SCX-held rq lock and emits an SCX error otherwise. `scx_bpf_cpu_curr()` is RCU-protected to safely read a remote rq's `curr`. `scx_bpf_now()` disables preemption so `this_rq()` and the cached rq clock belong to a stable CPU for the whole read.

Event aggregation flows from BPF into `scx_bpf_events()`, then under RCU to the current root scheduler. If `scx_root` is present, `scx_read_events()` walks all possible CPUs and aggregates the explicitly listed event counters from each `sch->pcpu`. If not, the output is zeroed. The final copy is size-clamped so BPF-side ABI size drift cannot corrupt memory.

Cgroup lookup under `CONFIG_CGROUP_SCHED` reads the scheduler's task-group view rather than the generic task cgroup pointer. The function defaults to the root cgroup, validates scheduler/task authority, selects `tg_cgrp(p->sched_task_group)` when allowed, takes a reference, and returns a non-NULL cgroup pointer to BPF.

Verifier filtering starts by classifying the kfunc ID against all SCX BTF sets: unlocked, select_cpu, enqueue/dispatch, dispatch, cpu_release, idle, and any. Non-SCX kfuncs are allowed. `BPF_PROG_TYPE_SYSCALL` can call unlocked, select_cpu, idle, and any helpers, which supports BPF test-run style programs. Non-struct_ops programs can only call always-safe `any` or idle helpers. SCX struct_ops programs are allowed through if the target kfunc is in `any` or idle; otherwise the attached struct_ops member offset indexes `scx_kf_allow_flags[]`, and the matching bit must allow the context-sensitive set.

Initialization is ordered around BPF visibility. `scx_init()` first registers all kfunc ID sets needed by verifier lookup, then initializes idle tracking, then registers `sched_ext_ops` as BPF struct_ops. Only after that does it register PM notifications and create the `/sys/kernel/sched_ext` kset and global sysfs group. Failures return immediately with `pr_err()` and prevent later initialization stages from publishing partial interfaces.

## State and Persistence Behavior

DSQ iterator state is temporary and owned by the BPF iterator object. The hidden kernel state stores a cursor node, target DSQ pointer, and optional slice/vtime fields used by DSQ move helpers defined earlier. Cursor list linkage persists across `next()` calls and is removed by either iteration exhaustion or `destroy()`.

`struct scx_dispatch_q` state is persistent while the scheduler and its custom DSQs live. This chunk reads `dsq->first_task`, `dsq->nr`, `dsq->lock`, and list/cursor state. It does not create DSQs, but it can trigger deferred re-enqueue processing for local and user DSQs.

`scx_exit_bstr_buf` is a single global formatting buffer protected by `scx_exit_bstr_buf_lock`. It persists for module lifetime and serializes BPF exit/error message formatting to avoid concurrent helper calls corrupting the shared line/data buffers.

`scx_dump_data` is a global dump-session carrier. Earlier dump setup marks the dump CPU and initializes cursor/prefix/seq buffer fields; this chunk's dump kfunc appends into it and flushes lines. The dump CPU gate prevents arbitrary CPUs from writing into an active dump session.

CPU performance target state persists in `rq->scx.cpuperf_target` until overwritten. Reads of CPU capacity/frequency are transient architecture queries; `cpufreq_update_util()` integrates the target with schedutil/cpufreq state outside this file.

The global cpumask helpers return persistent kernel masks, not dynamically allocated references. The BPF verifier's acquire/release model is simulated so BPF can treat the pointers as trusted while kernel memory management remains unchanged.

Event counters persist per scheduler per CPU in `sch->pcpu[*].event_stats`. `scx_bpf_events()` creates a stack aggregate and copies it to BPF without mutating the source counters.

`scx_kfunc_ids_any`, the context-sensitive kfunc ID sets from earlier chunks, `scx_kf_allow_flags[]`, and `scx_kfunc_context_filter()` are long-lived registration metadata used by the BPF verifier after `scx_init()`. They do not change at runtime.

`scx_kset` persists after successful init as the `/sys/kernel/sched_ext` kset. The global sysfs attribute group installed in this chunk exposes sched_ext state and control files defined earlier in the source.

## Dependencies and Integration Points

- BPF kfunc infrastructure: `__bpf_kfunc`, `__bpf_kfunc_start_defs()`, `__bpf_kfunc_end_defs()`, `BTF_KFUNCS_START/END`, `BTF_ID_FLAGS`, kfunc flags such as `KF_IMPLICIT_ARGS`, `KF_RCU`, `KF_RCU_PROTECTED`, `KF_RET_NULL`, `KF_ITER_NEW/NEXT/DESTROY`, `KF_ACQUIRE`, and `KF_RELEASE`, and `register_btf_kfunc_id_set()`.
- BPF struct_ops integration: `bpf_sched_ext_ops`, `sched_ext_ops`, `register_bpf_struct_ops()`, `BPF_PROG_TYPE_STRUCT_OPS`, `prog->aux->st_ops`, and `prog->aux->attach_st_ops_member_off`.
- BPF verifier and test-run integration: `BPF_PROG_TYPE_SYSCALL`, `BPF_PROG_TYPE_TRACING`, `btf_id_set8_contains()`, and the early verification pass where `prog->aux->st_ops` is not yet set.
- DSQ internals: `find_user_dsq()`, `find_dsq_for_dispatch()`, `nldsq_cursor_next_task()`, `INIT_DSQ_LIST_CURSOR()`, DSQ locks, DSQ list nodes, `SCX_DSQ_*` IDs, and deferred re-enqueue helpers.
- Scheduler/runqueue state: `this_rq()`, `cpu_rq()`, `task_rq()`, `scx_locked_rq()`, rq locks, `rq->scx.clock`, `rq->scx.flags`, `SCX_RQ_CLK_VALID`, and `rq->scx.cpuperf_target`.
- CPU and topology APIs: `ops_cpu_valid()`, `nr_cpu_ids`, `nr_node_ids`, `cpu_possible_mask`, `cpu_online_mask`, `arch_scale_cpu_capacity()`, `arch_scale_freq_capacity()`, `sched_clock_cpu()`, and `smp_processor_id()`.
- cpufreq/schedutil integration: `cpufreq_update_util()` is invoked when BPF changes the SCX CPU performance target.
- Exit and dump machinery: `scx_exit()`, `scx_error()`, `SCX_EXIT_UNREG_BPF`, `SCX_EXIT_ERROR_BPF`, `ops_dump_flush()`, `dump_line()`, and the dump setup/teardown logic earlier in `ext.c`.
- BPF string formatting internals: `copy_from_kernel_nofault()`, `bpf_bprintf_prepare()`, `bstr_printf()`, `bpf_bprintf_cleanup()`, `MAX_BPRINTF_VARARGS`, and `SCX_EXIT_MSG_LEN`.
- RCU and locking: `guard(rcu)`, `guard(preempt)`, raw spinlocks with IRQ save/restore, `rcu_dereference()`, `smp_load_acquire()`, `READ_ONCE()`, and rq lock helpers.
- Cgroup scheduler integration: `CONFIG_CGROUP_SCHED`, `p->sched_task_group`, `tg_cgrp()`, `cgrp_dfl_root`, `cgroup_get()`, and `scx_kf_arg_task_ok()`.
- Subsystem init: `scx_idle_init()`, `register_pm_notifier(&scx_pm_notifier)`, `kset_create_and_add()`, `scx_uevent_ops`, `kernel_kobj`, `sysfs_create_group()`, and `scx_global_attr_group`.

## Risks and Edge Cases

- BPF iterator cleanup must be correct after both successful and failed `new()`. The BPF iterator contract calls `next()` and `destroy()` regardless of `new()` result, so `kit->dsq` must be initialized to `NULL` before any failure path.
- The opaque BPF iterator ABI depends on `struct bpf_iter_scx_dsq_kern` fitting inside `struct bpf_iter_scx_dsq` with matching alignment. Any future hidden-state expansion must preserve these compile-time checks or deliberately change the BPF ABI.
- DSQ iteration intentionally excludes tasks enqueued after iterator creation. Changing cursor sequencing or list movement could expose newly queued tasks, loop indefinitely, or make virtual-time iteration appear to move backward.
- `scx_bpf_dsq_peek()` is lockless and can return a stale snapshot. BPF schedulers must not assume the returned task remains queued or first by the time a later locked operation runs.
- `scx_bpf_dsq_peek()` treats invalid use as scheduler errors for builtin or missing DSQs. A BPF scheduler probing IDs without care can self-disable through `scx_error()`.
- `scx_bpf_dsq_reenq()` uses `find_dsq_for_dispatch()`, which falls back to a global DSQ after reporting some invalid dispatch targets. That behavior is appropriate for dispatch verdicts but should be understood by callers expecting a hard failure for every bad DSQ ID.
- Re-enqueue scheduling is blocked while bypass depth is nonzero. BPF logic that relies on reenqueues during PM or disable bypass may observe no effect.
- The string helpers format under raw spinlocks for exit/error. Formatting work must remain bounded and non-sleeping; adding sleepable operations there would be invalid.
- BPF-provided string varargs are copied from kernel memory with nofault semantics. Incorrect `data__sz` validation would risk bad reads or formatting corruption, so size, alignment, and NULL checks are security relevant.
- `scx_bpf_dump_bstr()` is CPU-affine to the active dump CPU. Calling it from any other context is treated as an SCX error, which can turn a diagnostic misuse into scheduler disablement.
- `scx_bpf_cpuperf_set()` must preserve rq lock ordering. Allowing remote rq changes while a different rq is locked would risk ABBA deadlock in scheduler callbacks.
- `scx_bpf_cpu_rq()` is deprecated because returning raw remote rq pointers is easy to misuse. New code should prefer `scx_bpf_locked_rq()` for locked local rq access or `scx_bpf_cpu_curr()` for remote current-task reads.
- `scx_bpf_now()` is only monotonic non-decreasing for calls on the same CPU. BPF schedulers comparing timestamps across CPUs can still observe time going backward.
- `scx_bpf_events()` intentionally clamps output size. New fields added to `struct scx_event_stats` will be silently omitted for older BPF programs, and zero-filled/missing fields should be handled in user space.
- `scx_bpf_task_cgroup()` returns a referenced cgroup even on fallback to root. BPF callers must pair it with the expected release path or leak verifier-tracked references.
- `scx_kfunc_context_filter()` indexes `scx_kf_allow_flags[]` by attached struct_ops member offset. The table must remain synchronized with `struct sched_ext_ops` op indices and context-sensitive BTF sets; missing an op entry denies its context-sensitive helpers.
- The verifier filter deliberately allows all SCX kfuncs during an early pass before `st_ops` is set, expecting a later verifier pass to enforce restrictions. If BPF core behavior changes, this may need revisiting.
- `scx_init()` has no cleanup for some earlier successful registration steps if a later stage fails. That follows common initcall assumptions but means partial init failure paths should be scrutinized if sched_ext becomes unloadable or retryable.

## Test Signals

- BPF iterator tests should cover successful user DSQ iteration, reverse iteration, invalid flags returning `-EINVAL`, missing scheduler returning `-ENODEV`, missing DSQ returning `-ENOENT`, `next()` after failed `new()`, and `destroy()` after partial iteration.
- Iterator ordering tests should enqueue tasks before and after iterator creation and verify that only the pre-existing tasks are returned.
- DSQ peek tests should cover user DSQ first-task snapshots, empty DSQs returning `NULL`, builtin DSQ rejection, missing DSQ rejection, and RCU-safe use from BPF contexts with `KF_RCU_PROTECTED`.
- Re-enqueue tests should validate defaulting zero filter flags to `SCX_REENQ_ANY`, rejection of invalid flags, local DSQ re-enqueue, `SCX_DSQ_LOCAL_ON | cpu`, user DSQ re-enqueue, builtin unsupported DSQ errors, and no-op behavior while bypassing.
- Exit/error string tests should cover valid formatted messages, misaligned `data__sz`, oversized varargs, NULL data with nonzero size, invalid format preparation, nofault copy failure, graceful `SCX_EXIT_UNREG_BPF`, and fatal `SCX_EXIT_ERROR_BPF`.
- Dump tests should cover calls only from `ops.dump()`/`dump_cpu()`/`dump_task()` on the configured CPU, multi-call line assembly, newline flushing, buffer overflow flushing, and formatting failure diagnostic output.
- CPU performance tests should cover valid capacity/current reads, invalid CPUs falling back to `SCX_CPUPERF_ONE`, rejecting `perf > SCX_CPUPERF_ONE`, same-rq updates while rq lock is held, remote-rq rejection while another rq is locked, unlocked remote updates, and observable schedutil target changes.
- Topology/cpumask tests should verify `nr_cpu_ids`, `nr_node_ids`, possible/online cpumask acquire/release verifier behavior, and safe reads across CPU hotplug.
- Task/rq helper tests should cover running versus queued/sleeping tasks, task CPU reads under RCU, deprecated `scx_bpf_cpu_rq()` warning only once per scheduler, `scx_bpf_locked_rq()` success under SCX rq lock, and error return without a locked rq.
- Clock tests should verify that repeated `scx_bpf_now()` calls on one CPU do not go backward, use cached rq clock while `SCX_RQ_CLK_VALID` is set, and fall back to `sched_clock_cpu()` outside valid rq-clock windows.
- Event counter tests should cover zero output with no `scx_root`, aggregation across all possible CPUs, each listed `SCX_EV_*` counter, and truncated copy behavior with smaller BPF-side struct sizes.
- Cgroup tests should cover valid task cgroup returns, fallback to root when scheduler/task validation fails, reference acquisition/release, and stability across concurrent cgroup moves as seen through `p->sched_task_group`.
- Verifier tests should cover non-SCX kfunc passthrough, syscall program permissions, tracing program access to `any` helpers, non-SCX struct_ops rejection, early `st_ops == NULL` allowance followed by final enforcement, each `sched_ext_ops` op's allowed kfunc groups, and denial of context-sensitive helpers from unlisted ops.
- Init tests should cover failure injection for each kfunc set registration, `scx_idle_init()`, `register_bpf_struct_ops()`, PM notifier registration, kset creation, and sysfs group creation, plus successful creation of `/sys/kernel/sched_ext`.

## Chunk Boundary Notes

This chunk depends heavily on earlier `ext.c` sections for scheduler enable/disable, DSQ allocation and movement, deferred re-enqueue processing, dump setup, task authority checks, per-CPU event accounting, cgroup scheduler plumbing, and the context-sensitive kfunc sets registered before `scx_kfunc_ids_any`. The final per-file document should merge this chunk with the previous kfunc sections so the BPF scheduler API, verifier restrictions, and init sequence read as one continuous sched_ext control-plane surface.
