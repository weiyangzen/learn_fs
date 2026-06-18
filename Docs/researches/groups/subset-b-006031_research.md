# subset-b-006031 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/fork.c -->
# sources/distributed-fs/ceph-client/kernel/fork.c

Purpose: implements the kernel task-creation and context-splitting machinery behind `fork()`, `vfork()`, legacy `clone()`, `clone3()`, kernel threads, io_uring worker creation, idle task creation, `unshare()`, and core `mm_struct` lifetime helpers. It is a central integration point between scheduler, memory management, credentials, namespaces, cgroups, pidfds, futex cleanup, signals, security, audit, perf, BPF task storage, and proc/sysctl limits.

Important APIs/types/functions: public entry points include `copy_process()`, `kernel_clone()`, `kernel_thread()`, `user_mode_thread()`, `fork_idle()`, `create_io_thread()`, `mm_alloc()`, `mmput()`, `mmput_async()`, `__mmdrop()`, `get_task_mm()`, `mm_access()`, `pidfd_prepare()`, `ksys_unshare()`, `unshare_files()`, and syscall wrappers for `fork`, `vfork`, `clone`, `clone3`, `unshare`, and `set_tid_address`. Internal helpers cover task and stack allocation (`dup_task_struct()`, `alloc_thread_stack_node()`, `free_thread_stack()`), mm duplication (`mm_init()`, `dup_mm()`, `copy_mm()`), resource sharing (`copy_fs()`, `copy_files()`, `copy_sighand()`, `copy_signal()`), clone3 validation, and ordered fork unwind labels.

Control flow: `kernel_clone()` normalizes clone flags, selects ptrace event type, calls `copy_process()`, records pid/pidfd state, handles `CLONE_VFORK` completion setup, wakes the child with `wake_up_new_task()`, emits ptrace/scheduler events, optionally waits for vfork completion, and returns the virtual pid. `copy_process()` validates illegal flag combinations, drains pending multiprocess signals, duplicates the task, copies credentials and every requested resource domain, allocates a pid, prepares pidfd output, initializes futex state, applies scheduler/cgroup hooks, publishes the task under `tasklist_lock`, installs pid links, updates fork counters, and runs post-fork notifiers. Failure paths unwind in reverse order.

State and persistence behavior: persistent kernel state includes `total_forks`, `nr_threads`, per-cpu `process_counts`, `max_threads`, task/mm/slab caches, RCU-delayed task/stack frees, optional per-cpu vmalloc stack caches, `mm_users`/`mm_count` reference counts, executable file references, and process-tree pid links. It does not persist data to disk except through proc/sysctl visibility such as `kernel/threads-max`. `exit_mm_release()` and `exec_mm_release()` integrate futex robust-list/PI cleanup before `mm_release()` clears child TID and completes vfork.

Dependencies and integration points: depends on scheduler hooks, `copy_thread()`, MM/VMA duplication, page tables, memcg, namespaces, credentials, security LSM, audit, perf, cgroups, livepatch, rseq, uprobe, io_uring, BPF storage, pidfs/pidfd, freezer-aware vfork waits, and futex private hash allocation via `futex_mm_init()`, `futex_hash_allocate_default()`, and `futex_hash_free()`.

Risks: the major risks are resource leaks on deep failure paths, inconsistent clone flag validation, races around task publication, pidfd installation, vfork completion, mm ownership and executable-file updates, lazy TLB shootdown, stack lifetime after `TASK_DEAD`, and cgroup/scheduler hooks running before the task is externally visible. Futex private-hash allocation after cgroup scheduling is intentionally not rolled back, so changes must preserve that lifetime assumption.

Test signals: useful coverage includes fork/clone/clone3 ABI tests, invalid flag matrix tests, pidfd and autoreap behavior, vfork signal/freezer interactions, RLIMIT_NPROC and `threads-max`, namespace/cgroup clone combinations, KASAN/KMSAN/lockdep fork stress, fault injection through every unwind label, futex robust-list exit after fork/exec, and unshare tests for fs/files/user/ipc/mount namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/freezer.c -->
# sources/distributed-fs/ceph-client/kernel/freezer.c

Purpose: implements the generic task freezer used by system suspend/hibernate, cgroup v1 freezer state, and freezer-aware kernel threads. It decides when a task must stop, transitions eligible tasks into `TASK_FROZEN`, wakes tasks so they can enter the refrigerator, and thaws them back to either running or their saved sleep state.

Important APIs/types/functions: exported state includes `freezer_active`, `pm_freezing`, and `pm_nosig_freezing`. Public helpers are `freezing_slow_path()`, `frozen()`, `__refrigerator()`, `freeze_task()`, `__thaw_task()`, `thaw_process()`, and `set_freezable()`. Internal helpers include `fake_signal_wake_up()`, `__set_task_frozen()`, `__freeze_task()`, and `__restore_freezer_state()`. `freezer_lock` serializes freezing and thawing state transitions.

Control flow: `freezing_slow_path()` filters out `PF_NOFREEZE`, suspend-task, and OOM-victim tasks, then accepts cgroup freezing, nosignal PM freezing, or userspace PM freezing for non-kthreads. `freeze_task()` checks whether a task is freezing and not already frozen, attempts direct state conversion with `task_call_func()`, and otherwise nudges the task with a fake signal for userspace or `wake_up_state()` for kthreads. `__refrigerator()` repeatedly sets current to `TASK_FROZEN`, clears stale saved state, checks whether freezing is still active and whether a kthread stop should break the loop, schedules, then returns to `TASK_RUNNING`.

State and persistence behavior: all state is runtime-only task state and global freezer flags. `saved_state` preserves a task's original sleep state when converting `TASK_FREEZABLE`, stopped, or traced tasks to `TASK_FROZEN`; thawing restores that state when possible or wakes `TASK_FROZEN` sleepers. `set_freezable()` clears `PF_NOFREEZE` under `freezer_lock` and immediately tries to freeze if a freeze request is visible.

Dependencies and integration points: integrates with scheduler task states, `task_call_func()`, `pi_lock`, signal wakeups, kthread stop checks, suspend flags, cgroup v1 freezer, OOM victim detection, and lockdep diagnostics for freezing with locks held. `fork.c` uses `TASK_FREEZABLE` during vfork waits, so the freezer can suspend a parent blocked on child exec/exit.

Risks: races around saved state and wakeups can leave tasks stuck frozen or lose a legitimate wakeup. Freezing tasks holding locks can deadlock suspend, which is why lockdep warns unless marked unsafe. Misclassifying OOM victims, kthreads, or cgroup-frozen tasks can block suspend progress or freeze tasks that must continue running.

Test signals: suspend/resume and hibernate stress, cgroup freezer tests, kthread `set_freezable()` and stop races, ptraced/stopped/freezable sleep state restoration, lockdep coverage for unsafe freezing, OOM victim exclusion, and vfork wait interaction with `TASK_FREEZABLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/freezer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/Makefile -->
# sources/distributed-fs/ceph-client/kernel/futex/Makefile

Purpose: declares the futex subsystem objects built into the kernel directory. It groups the futex implementation into core state, syscall dispatch, priority-inheritance handling, requeue handling, and wait/wake handling.

Important APIs/types/functions: the Makefile sets `CONTEXT_ANALYSIS := y`, enabling sparse/context annotations to check lock acquisition and release contracts in the futex code. `obj-y` includes `core.o`, `syscalls.o`, `pi.o`, `requeue.o`, and `waitwake.o`.

Control flow: there is no runtime flow in the Makefile. At build time, kbuild compiles all five objects unconditionally as part of the futex subsystem. Feature-specific code paths inside those objects are then controlled by C preprocessor symbols such as `CONFIG_FUTEX_PI`, `CONFIG_FUTEX_PRIVATE_HASH`, `CONFIG_FUTEX_MPOL`, `CONFIG_COMPAT`, and `CONFIG_FAIL_FUTEX`.

State and persistence behavior: no runtime state is stored here. Its state effect is build composition: omitting any object would remove syscall entry points, hash-key/cleanup state, PI paths, requeue paths, or basic wait/wake functionality.

Dependencies and integration points: depends on the surrounding `kernel/Makefile` selecting the futex directory and on each object sharing declarations from `futex.h`. The context-analysis setting is important because these files use annotated lock classes and nontrivial lock handoff patterns.

Risks: build-list drift is the primary risk. Adding a futex feature without listing its object would silently fail to link; removing context analysis would reduce static checking on a concurrency-sensitive subsystem. Reordering objects is usually unimportant, but missing shared symbols between `core`, `waitwake`, `pi`, `requeue`, and `syscalls` would surface as link failures.

Test signals: allmodconfig/defconfig builds with futex options, sparse/context-analysis runs, link tests for syscall symbols, and futex selftests that exercise wait/wake, PI, requeue, robust lists, and futex2 syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/core.c -->
# sources/distributed-fs/ceph-client/kernel/futex/core.c

Purpose: provides futex keying, hashing, queue primitives, robust-list exit cleanup, PI-state exit cleanup, per-mm private futex hash management, fault-injection hooks, and global futex hash initialization. It is the substrate used by all futex wait, wake, PI, requeue, and syscall layers.

Important APIs/types/functions: central functions are `get_futex_key()`, `futex_hash()`, `futex_setup_timer()`, `fault_in_user_writeable()`, `futex_top_waiter()`, `futex_q_lock()`, `futex_queue()`, `futex_unqueue()`, `futex_unqueue_pi()`, `futex_exec_release()`, `futex_exit_release()`, `futex_exit_recursive()`, `futex_mm_init()`, `futex_hash_free()`, `futex_hash_allocate_default()`, `futex_hash_prctl()`, and `futex_init()`. Internal structures include the global NUMA-sharded bucket array and optional `struct futex_private_hash`.

Control flow: futex operations first call `get_futex_key()` to validate alignment/access and translate user addresses into either private `(mm,address,node)` keys or shared inode/page-offset keys. `futex_hash()` maps keys to per-mm private buckets when enabled or to global NUMA buckets otherwise. Queue helpers increment waiter counters before locking, enqueue priority-sorted `futex_q` entries, and unqueue safely under RCU because `q->lock_ptr` can change during requeue. Exit paths call `futex_cleanup_begin()`, walk robust lists, repair owner-died futex words, clean PI state lists, and publish `FUTEX_STATE_DEAD` or reset to OK for exec.

State and persistence behavior: state is runtime-only: hash buckets, waiter counts, plist queues, futex keys, per-task robust-list pointers, per-task PI-state lists, and optional per-mm private hash tables. Private hash replacement uses RCU, per-cpu-to-atomic ref transitions, `mm->futex_hash_lock`, and `mmput_async()` to protect old hashes until no futex operation can reference them.

Dependencies and integration points: integrates with `mm_struct` initialization/free in `fork.c`, user memory access/GUP, shmem/inode mapping, mempolicy/NUMA node hints, rtmutex PI state, robust-list syscalls, task exit/exec, `prctl(PR_FUTEX_HASH_*)`, debugfs fault injection, and the exported helpers in `futex.h`.

Risks: incorrect key generation can alias unrelated futexes or split waiters for the same futex. Shared mapping races with truncation, swapcache movement, COW, and inode reuse are sensitive. Queue waiter barriers must preserve the no-lost-wakeup guarantee. Robust-list traversal is user-controlled and must avoid loops and bad pointers. Private hash resizing risks stale bucket pointers, missed wakeups, refcount underflow, and mm lifetime bugs.

Test signals: futex selftests for private/shared mappings, shmem/file-backed futexes, robust mutex owner death, PI owner exit, private-hash prctl resizing, NUMA/MPOL futex2 keys, fault injection, module-free builds with/without MMU, lockdep/sparse annotations, and stress tests combining clone, exit, exec, and requeue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/futex.h -->
# sources/distributed-fs/ceph-client/kernel/futex/futex.h

Purpose: defines the private interface shared by futex implementation files. It translates public futex/futex2 flags into internal flags, declares hash bucket and queue structures, defines PI state, provides waiter-counter and locking helpers, and prototypes cross-file futex operations.

Important APIs/types/functions: key types are `struct futex_hash_bucket`, `struct futex_pi_state`, `struct futex_q`, and `struct futex_vector`. Important inline APIs include `futex_to_flags()`, `futex2_to_flags()`, `futex_size()`, `futex_flags_valid()`, `futex_validate_input()`, `futex_match()`, `futex_cmpxchg_value_locked()`, `futex_get_value_locked()`, `futex_queue()`, `futex_hb_waiters_inc()`, `futex_hb_waiters_pending()`, `double_lock_hb()`, and `double_unlock_hb()`.

Control flow: syscall code converts user flags to internal flags, validates size/value constraints, and then calls wait/wake/requeue/PI functions declared here. Wait setup stores a key in `futex_q`, `futex_queue()` inserts it and releases the bucket lock, wake paths call the `wake` callback, and PI/requeue paths use `pi_state`, `rt_waiter`, `requeue_pi_key`, `requeue_state`, and `drop_hb_ref` to coordinate ownership transfer and hash-bucket lifetime.

State and persistence behavior: the header itself owns no state, but it defines the in-memory state contracts. A `futex_q` is woken when either its plist node is empty or `lock_ptr` becomes NULL, and wake code must make the plist removal visible before clearing `lock_ptr`. `futex_pi_state` lifetime is refcounted and linked into the owner's `pi_state_list`. Waiter counters use SMP barriers to synchronize wait enqueue with wake-side empty checks.

Dependencies and integration points: depends on UAPI futex definitions, rtmutex, wake queues, compat support, uaccess, cleanup classes, optional PREEMPT_RT `rcuwait`, and architecture futex atomics from `asm/futex.h`. It is included by `core.c`, `waitwake.c`, `pi.c`, `requeue.c`, and `syscalls.c`.

Risks: this header encodes lock ordering and memory barriers that callers must follow exactly. Any mismatch in `FLAGS_*` mapping, size validation, bucket double-lock ordering, PI-state lifetime, or wake callback semantics can create lost wakeups, deadlocks, invalid PI ownership, or userspace ABI regressions.

Test signals: sparse/context-analysis coverage, futex2 flag validation tests, 32-bit compat tests rejecting 64-bit futex sizes, lockdep runs through wake/requeue/PI paths, wait/wake race stress, and code review of every caller that manipulates `futex_q.lock_ptr`, `pi_state`, or waiter counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/pi.c -->
# sources/distributed-fs/ceph-client/kernel/futex/pi.c

Purpose: implements priority-inheritance futex locking and unlocking on top of rtmutexes. It maintains `futex_pi_state`, attaches waiters to owners, handles owner death/exit races, transfers ownership during unlock, and repairs user-space futex words when rtmutex ownership and user TIDs diverge.

Important APIs/types/functions: public futex-internal entry points are `refill_pi_state_cache()`, `get_pi_state()`, `put_pi_state()`, `futex_lock_pi_atomic()`, `fixup_pi_owner()`, `futex_lock_pi()`, and `futex_unlock_pi()`. Important internal helpers are `attach_to_pi_state()`, `attach_to_pi_owner()`, `handle_exit_race()`, `wake_futex_pi()`, `__fixup_pi_state_owner()`, and `lock_pi_update_atomic()`.

Control flow: `futex_lock_pi()` preallocates PI state, builds a futex key, locks the hash bucket, and calls `futex_lock_pi_atomic()`. The atomic helper either acquires an uncontended lock by updating the user word, attaches to existing PI state, or sets `FUTEX_WAITERS` and creates PI state for the owner. If blocking is needed, the waiter is queued in the futex bucket, then proxied onto the rtmutex; after wake, `fixup_pi_owner()` reconciles kernel and user-space ownership. `futex_unlock_pi()` validates that current owns the futex word, finds the top PI waiter, and either passes ownership with `wake_futex_pi()` or atomically clears the word.

State and persistence behavior: `futex_pi_state` objects are runtime refcounted and cached per current task through `pi_state_cache`. Each PI state owns an `rt_mutex_base`, an owner pointer, key, and owner-list link. User-space state is the futex word containing TID, `FUTEX_WAITERS`, and `FUTEX_OWNER_DIED`; kernel state must be kept consistent with that word except in documented immutable-user-page failure cases.

Dependencies and integration points: depends on rtmutex proxy locking, futex hash-bucket locking from `core.c`, task lookup by virtual pid, per-task `pi_lock`, futex exit state, robust-list owner death, and fault repair through `fault_in_user_writeable()`. Requeue-PI uses `futex_lock_pi_atomic()` and PI-state references to acquire locks on behalf of waiters.

Risks: this is highly concurrency-sensitive. Risks include deadlock detection regressions, owner TID mismatch, races with exiting owners between robust-list and PI-list cleanup, missing `FUTEX_WAITERS`, stale `pi_state` references, page faults while holding locks, PREEMPT_RT lock handoff issues, and inconsistent user/kernel ownership after lock stealing.

Test signals: PI futex selftests for lock, trylock, unlock, timeout, signal, owner death, robust mutexes, invalid user word manipulation, exiting owner live-lock avoidance, priority boosting/deboosting, page-fault injection during cmpxchg, requeue-PI condition-variable tests, and lockdep/rtmutex debug coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/pi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/requeue.c -->
# sources/distributed-fs/ceph-client/kernel/futex/requeue.c

Purpose: implements moving waiters from one futex key to another, including plain `FUTEX_REQUEUE`/`FUTEX_CMP_REQUEUE` and PI-aware condition-variable flows that wait on a non-PI futex and acquire a PI futex before returning.

Important APIs/types/functions: key exports are `futex_requeue()` and `futex_wait_requeue_pi()`. The file defines `futex_q_init`, the requeue-PI state machine (`Q_REQUEUE_PI_*`), and helpers `requeue_futex()`, `futex_requeue_pi_prepare()`, `futex_requeue_pi_complete()`, `futex_requeue_pi_wakeup_sync()`, `requeue_pi_wake_futex()`, `futex_proxy_trylock_atomic()`, and `handle_early_requeue_pi_wakeup()`.

Control flow: `futex_requeue()` keys source and destination futexes, locks both buckets in address order, optionally compares the source value, and either wakes the first `nr_wake` waiters or moves subsequent waiters to the destination bucket. In PI mode it validates distinct keys, restricts wake count to one, preallocates PI state, may acquire the target PI futex for the top waiter, then requeues remaining waiters onto the target rtmutex with proxy locking. `futex_wait_requeue_pi()` waits on the source futex, synchronizes with any concurrent requeue, handles early signal/timeout wakeups, and completes rtmutex acquisition or owner fixup after requeue.

State and persistence behavior: requeue changes only runtime queue state: `futex_q.key`, plist membership, `lock_ptr`, waiter counts, optional `pi_state`, `rt_waiter`, `requeue_pi_key`, `requeue_state`, and temporary hash references. PI requeue state records whether a waiter should be ignored, is in progress, has been requeued, or acquired the lock.

Dependencies and integration points: depends on hash-bucket queue primitives, PI helpers in `pi.c`, wait setup in `waitwake.c`, rtmutex proxy locking, PREEMPT_RT `rcuwait` synchronization, and syscall dispatch in `syscalls.c`. It implements the kernel side required by pthread condition variables using `FUTEX_WAIT_REQUEUE_PI` paired with `FUTEX_CMP_REQUEUE_PI`.

Risks: missed state transitions can strand waiters on the wrong bucket, lose wakeups, or corrupt rtmutex waiter state. PI requeue must reject mismatched source/target keys and incompatible waiter types. Early wakeups racing with requeue are especially risky on PREEMPT_RT because a task cannot block on both a bucket rtmutex and a proxy rtmutex.

Test signals: requeue and cmp-requeue futex selftests, pthread condvar PI tests, signal and timeout races during `FUTEX_WAIT_REQUEUE_PI`, deadlock-detection cases, target-key mismatch tests, PREEMPT_RT stress, fault injection on source/target user words, and wait-count accounting checks under heavy contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/requeue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/syscalls.c -->
# sources/distributed-fs/ceph-client/kernel/futex/syscalls.c

Purpose: provides user-facing futex syscall dispatch, robust-list syscalls, futex2 syscalls, timeout parsing, compat robust-list handling, and 32-bit time syscall support. It translates ABI arguments into internal flags and delegates actual wait/wake/requeue/PI behavior to the other futex files.

Important APIs/types/functions: syscall entry points include `set_robust_list`, `get_robust_list`, `futex`, `futex_waitv`, `futex_wake`, `futex_wait`, `futex_requeue`, compat robust-list variants, and `futex_time32`. Internal helpers include `do_futex()`, `futex_cmd_has_timeout()`, `futex_init_timeout()`, `futex_parse_waitv()`, `futex2_setup_timeout()`, and `futex_get_robust_list_common()`.

Control flow: legacy `sys_futex()` parses a timeout only for commands that use one, converts relative `FUTEX_WAIT` timeouts and absolute bitset/PI timeouts, and calls `do_futex()`. `do_futex()` maps opcodes to `futex_wait()`, `futex_wake()`, `futex_requeue()`, `futex_wake_op()`, `futex_lock_pi()`, `futex_unlock_pi()`, or `futex_wait_requeue_pi()`, while limiting `FUTEX_CLOCK_REALTIME` to supported commands. Futex2 calls validate `FUTEX2_VALID_MASK`, size/private/NUMA/MPOL flags, value width, timeout clock, and then call shared helpers.

State and persistence behavior: robust-list syscalls store per-task user pointers (`robust_list` or `compat_robust_list`) that are later consumed during exit/exec cleanup. Futex waits allocate transient `futex_vector` arrays and stack hrtimer sleepers. No durable storage is written.

Dependencies and integration points: depends on task lookup and ptrace permission checks for `get_robust_list`, time namespaces for monotonic timeout conversion, uaccess copying, compat ABI structs, futex2 UAPI structs, and all internal futex subsystem APIs. Robust-list registration is consumed by `core.c` during `futex_exit_release()`.

Risks: ABI validation mistakes can allow unsupported sizes, bad clocks, invalid masks, or misinterpreted timeouts. `get_robust_list` must serialize against exec credentials. Passing `(unsigned long)utime` as legacy `val2` for requeue-like commands preserves historical ABI but is easy to misunderstand. Futex2 currently validates only 32-bit futex sizes despite generic flag names.

Test signals: futex syscall ABI selftests, robust-list permission tests, compat and time32 coverage, futex2 wait/wake/requeue/waitv validation tests, realtime vs monotonic timeout tests under time namespaces, faulting user-pointer tests, and negative tests for unsupported command/flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/waitwake.c -->
# sources/distributed-fs/ceph-client/kernel/futex/waitwake.c

Purpose: implements ordinary futex wait and wake operations, wake-op atomic operations, multi-futex wait (`futex_waitv` backend), timeout/restart handling, and the memory-ordering protocol that prevents lost wakeups.

Important APIs/types/functions: main functions are `futex_wake()`, `futex_wake_op()`, `futex_wait_setup()`, `__futex_wait()`, `futex_wait()`, `futex_do_wait()`, `futex_wait_multiple_setup()`, `futex_wait_multiple()`, `futex_unqueue_multiple()`, and `futex_wake_mark()`. Internal helpers include `__futex_wake_mark()`, `futex_atomic_op_inuser()`, `futex_sleep_multiple()`, and `futex_wait_restart()`.

Control flow: wait setup computes the futex key, increments bucket waiter counts, locks the bucket, rereads the user value under the lock, queues only if the value still matches, sets `TASK_INTERRUPTIBLE|TASK_FREEZABLE`, and releases the lock. `__futex_wait()` sleeps, then distinguishes real wakeup from timeout, signal, or spurious wakeup by attempting to unqueue. Wake paths key the address, skip locking when waiter count is zero, scan matching bucket entries, honor bitsets, mark waiters woken, and perform actual wakeups after dropping the bucket lock. `futex_wake_op()` additionally performs an encoded atomic operation on a second futex and conditionally wakes that bucket.

State and persistence behavior: state is transient wait queue state in `futex_q`, bucket waiter counters, task sleep state, restart-block fields for interrupted timed waits, and optional hrtimer sleepers. Multi-wait stores one `futex_q` per user-supplied waiter and returns the index of a woken futex.

Dependencies and integration points: uses key/hash helpers from `core.c`, queue primitives from `futex.h`, scheduler/freezer task states, hrtimers, restart blocks, architecture futex atomic operations, signal handling, and futex2 parsing in `syscalls.c`.

Risks: the waiter-counter barriers are the critical no-lost-wakeup invariant. Reordering the value reread, queue insertion, or wake-side waiter check can block tasks forever. Wake-op must handle page faults without holding bucket locks and retry shared keys when mappings can change. Multi-wait is vulnerable to partial enqueue cleanup bugs and ambiguous wake-index reporting.

Test signals: basic wait/wake and bitset selftests, timeout and restart tests, signal interruption, spurious wake stress, `FUTEX_WAKE_OP` operation/compare matrix, fault injection on both futex addresses, `futex_waitv` multi-wait tests, private vs shared mapping races, freezer interaction during waits, and memory-ordering stress on SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/futex/waitwake.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/gcov/Kconfig

Purpose: defines configuration options for gcov-based kernel profiling and coverage export. It lets builds enable kernel gcov support, optionally instrument the whole kernel, and documents per-file/per-directory Makefile controls.

Important APIs/types/functions: configuration symbols are `GCOV_KERNEL`, `ARCH_HAS_GCOV_PROFILE_ALL`, and `GCOV_PROFILE_ALL`. `GCOV_KERNEL` depends on `DEBUG_FS` and either architectures that do not require disabling profiling instrumentation or compiler support for `no_profile_fn` attributes; it selects `CONSTRUCTORS`. `GCOV_PROFILE_ALL` depends on `GCOV_KERNEL`, architecture opt-in, and not `COMPILE_TEST`.

Control flow: this is build-time Kconfig logic only. Enabling `GCOV_KERNEL` includes the gcov support code and debugfs interface. Enabling `GCOV_PROFILE_ALL` asks the build to instrument the entire kernel, while Makefile variables such as `GCOV_PROFILE_foo.o := y/n` and `GCOV_PROFILE := y/n` select or exclude narrower scopes.

State and persistence behavior: no runtime state is stored by Kconfig, but enabled options cause runtime coverage counters and debugfs-visible gcov data to exist. Profiling data is accessed through mounted debugfs and is not persistent across reboot unless external tooling saves it.

Dependencies and integration points: integrates with compiler instrumentation, kernel constructors, debugfs, architecture support, and the `kernel/gcov` build files. It also interacts with every profiled object because instrumentation changes code size and runtime overhead.

Risks: whole-kernel profiling increases image size and slows execution. Instrumenting objects not linked into the final kernel can create linker errors, as the help text warns. Missing architecture/compiler support can create recursive instrumentation or profiling of code that must not be instrumented.

Test signals: Kconfig dependency tests across GCC/Clang and architectures, builds with `GCOV_KERNEL=y`, targeted `GCOV_PROFILE` builds, `GCOV_PROFILE_ALL` architecture builds, debugfs coverage extraction smoke tests, and negative build tests for excluded objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/Makefile -->
# sources/distributed-fs/ceph-client/kernel/gcov/Makefile

Purpose: builds the kernel gcov support objects and passes source/object tree paths to the implementation for debugfs path generation and coverage data export.

Important APIs/types/functions: `ccflags-y` defines `SRCTREE` and `OBJTREE`. `obj-y` always includes `base.o` and `fs.o` when the directory is built. GCC builds add `gcc_base.o` and `gcc_4_7.o`; Clang builds add `clang.o`. Compiler-specific objects suppress missing-prototype and missing-declaration warnings because they expose compiler-runtime callback shapes.

Control flow: this is build-time only. Kbuild selects compiler-specific backend objects through `CONFIG_CC_IS_GCC` or `CONFIG_CC_IS_CLANG`, while shared gcov list/event and filesystem support are always compiled for the gcov directory.

State and persistence behavior: no Makefile runtime state exists. The emitted macros persist into compiled objects, letting runtime code know the original source and object tree roots for exported coverage paths.

Dependencies and integration points: depends on compiler selection Kconfig symbols, the gcov base/fs implementation, and compiler-format-specific backends. It integrates with the Kconfig options that decide whether this directory is reachable and with debugfs consumers that expect stable source/object path metadata.

Risks: wrong compiler backend selection would break coverage data format parsing. Incorrect `SRCTREE`/`OBJTREE` quoting would produce unusable debugfs paths. Warning suppressions should stay limited to backend files that intentionally match compiler-generated interfaces.

Test signals: GCC and Clang gcov builds, debugfs path inspection, coverage extraction with source/object tree relocation, W=1 builds verifying warning scope, and build tests with per-file `GCOV_PROFILE` flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/base.c -->
# sources/distributed-fs/ceph-client/kernel/gcov/base.c

Purpose: maintains global gcov event state and utility serialization helpers for kernel coverage data. It enables delayed event replay once the gcov filesystem side is ready and removes module-owned profiling entries during module unload.

Important APIs/types/functions: globals are `gcov_events_enabled` and `gcov_lock`. Public helpers include `gcov_enable_events()`, `store_gcov_u32()`, and `store_gcov_u64()`. With modules enabled, `gcov_module_notifier()` and `gcov_init()` register a module notifier.

Control flow: `gcov_enable_events()` takes `gcov_lock`, enables event reporting, iterates all existing `gcov_info` records via `gcov_info_next()`, emits `GCOV_ADD` for each through `gcov_event()`, and periodically reschedules. `store_gcov_u32()` and `store_gcov_u64()` optionally write native-endian gcov words to a caller buffer and always return the byte count. On `MODULE_STATE_GOING`, the notifier walks gcov info entries, unlinks records belonging to the unloading module, and emits `GCOV_REMOVE` if events are enabled.

State and persistence behavior: state is runtime-only: a global event-enabled flag, a mutex, and linked gcov info records managed by compiler backends. Coverage counters themselves live in instrumented objects/modules; this file coordinates events and serialization, not durable storage.

Dependencies and integration points: depends on `gcov.h` backend callbacks such as `gcov_info_next()`, `gcov_event()`, `gcov_info_within_module()`, and `gcov_info_unlink()`, plus module notifier infrastructure. It integrates with the debugfs gcov filesystem, compiler-specific gcov backends, and module load/unload lifecycle.

Risks: missing locking can race debugfs readers, event replay, and module unload. Failing to unlink module gcov records before unload would leave dangling pointers. Buffer serialization assumes aligned writable caller buffers when non-NULL and native gcov endianness. Event replay must tolerate early registrations before the filesystem callback path is ready.

Test signals: gcov debugfs smoke tests, enabling events after early boot records exist, module load/unload coverage removal tests, lockdep under concurrent reads and unloads, GCC/Clang backend serialization checks, and coverage file comparison against userspace gcov tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/gcov/base.c -->
