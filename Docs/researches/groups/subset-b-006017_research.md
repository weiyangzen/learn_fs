# subset-b-006017 Research

Grouped source research for BPF lock, stack trace, verifier-state, and program stream support in `sources/distributed-fs/ceph-client/kernel/bpf`. Each source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/rqspinlock.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/rqspinlock.c

## Purpose
`rqspinlock.c` implements resilient queued spinlocks for BPF-facing lock kfuncs. It adapts the kernel queued spinlock/MCS slow path with bounded waits, timeout reporting, and AA/ABBA deadlock detection so BPF programs using `struct bpf_res_spin_lock` can fail lock acquisition instead of spinning forever. It also exposes BTF kfuncs for normal and IRQ-save lock/unlock pairs and emits diagnostic stream output when a lock violation is detected.

## Important APIs, Types, and Functions
The file defines `struct rqspinlock_timeout` for timeout bookkeeping and exports the per-CPU `rqspinlock_held_locks` array of `struct rqspinlock_held`. `is_lock_released()` tests masked lock-word state with acquire ordering. `check_deadlock_AA()` detects attempts to reacquire a lock already held by the current CPU, while `check_deadlock_ABBA()` scans other CPUs' held-lock tables to catch common lock-order inversions. `check_timeout()` combines the timeout deadline with periodic deadlock checks.

`resilient_tas_spin_lock()` is the fallback test-and-set implementation for architectures without queued spinlocks. Under `CONFIG_QUEUED_SPINLOCKS`, `resilient_queued_spin_lock_slowpath()` is the main slow path: it handles pending-bit acquisition, MCS queueing, timeout unwind, queue destruction, and handoff to the next waiter. The BPF kfuncs are `bpf_res_spin_lock()`, `bpf_res_spin_unlock()`, `bpf_res_spin_lock_irqsave()`, and `bpf_res_spin_unlock_irqrestore()`. `rqspinlock_register_kfuncs()` registers them for `BPF_PROG_TYPE_UNSPEC` at `late_initcall`.

## Control Flow
Fast-path acquisition happens outside this file through `res_spin_lock()`. Once slow path is entered, the caller has already reserved a held-lock tracking entry. The fallback TAS path repeatedly reads `lock->val`, attempts `atomic_try_cmpxchg()`, and calls `RES_CHECK_TIMEOUT()` while spinning; on failure it releases the held-lock entry before returning `-EDEADLK` or `-ETIMEDOUT`.

The queued path first handles a transient `_Q_PENDING_VAL`, tries to become the pending waiter, and waits for the locked bit to clear using `res_smp_cond_load_acquire()`. If pending acquisition times out, it clears the pending bit and releases the tracking entry. If contention remains, it enters the MCS queue: allocates a per-CPU qnode, encodes the tail, publishes it with `xchg_tail()`, links to any previous node, waits for predecessor handoff, then waits for locked/pending bits to clear. Deadlock findings avoid destructive queue teardown where possible; timeout findings try to clear the tail or signal the next node with `RES_TIMEOUT_VAL` so queued waiters can unwind. Successful queue-head acquisition either atomically clears the tail and sets locked or sets the lock bit and wakes the next waiter.

The kfunc wrappers disable preemption, optionally save/disable local IRQs, call `res_spin_lock()`, and restore preemption/IRQs on failure. Unlock kfuncs call `res_spin_unlock()` and restore the corresponding execution state.

## State and Persistence Behavior
All state is kernel runtime state. The lock word lives in the caller-provided `rqspinlock_t`/`bpf_res_spin_lock`. Per-CPU held-lock state records the locks held or being acquired and is used for diagnostics and deadlock detection. Per-CPU `rqnodes` store nested MCS queue nodes, bounded by `_Q_MAX_NODES`. Timeout state is stack-local per acquisition attempt. No state is persisted across program unload, reboot, or map serialization.

## Dependencies and Integration Points
The implementation depends on qspinlock internals (`../locking/qspinlock.h`, `mcs_spinlock.h`, `lock_events.h`), architecture support from `asm/rqspinlock.h`, BPF kfunc/BTF registration, trace lock contention events, preemption/IRQ primitives, and BPF stream diagnostics from `bpf_stream_stage`. It integrates with verifier-side lock reference tracking through the BPF resilient spin-lock kfunc ABI and with BPF program lookup/file-line reporting through `bpf_prog_find_from_stack()` and stream stack dumps.

## Risks and Test Signals
The highest risks are queue unwind races on timeout, stale or incomplete per-CPU held-lock tables causing false positive or missed deadlock reports, mismatched preemption/IRQ restore paths, architecture-specific qspinlock assumptions, and fairness loss when qnode allocation falls back to trylock. Test signals include BPF selftests for successful lock/unlock, AA deadlock, ABBA deadlock, timeout under a stuck holder, nested NMI/IRQ contexts, IRQ-save flag restore, stream diagnostics, lockdep/trace contention events, and builds with and without `CONFIG_QUEUED_SPINLOCKS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/rqspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/rqspinlock.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/rqspinlock.h

## Purpose
`rqspinlock.h` provides the small helper needed by the resilient queued spinlock slow path to update only the tail portion of a qspinlock word while preserving the current locked and pending bits. It is local support code for `rqspinlock.c`, not a general public BPF API.

## Important APIs, Types, and Functions
The header includes `../locking/qspinlock.h` and defines one inline helper, `try_cmpxchg_tail(struct qspinlock *lock, u32 tail, u32 new_tail)`. The function repeatedly reads `lock->val`, verifies that the observed `_Q_TAIL_MASK` still equals the caller's expected `tail`, combines the current `_Q_LOCKED_PENDING_MASK` bits with `new_tail`, and attempts `atomic_try_cmpxchg_relaxed()`.

## Control Flow
Callers use this helper when the queue head needs to clean up or replace the queue tail, especially during resilient timeout handling. If another waiter has already changed the tail, the helper returns `false` immediately. If only the locked/pending bits changed, the helper recomputes the new composite word and retries until the relaxed cmpxchg succeeds or the tail becomes stale.

## State and Persistence Behavior
The helper does not own state. It modifies the qspinlock's atomic 32-bit word in place. The design intentionally preserves volatile locked/pending state observed during the retry loop while replacing only the tail code.

## Dependencies and Integration Points
The helper depends on qspinlock bit layout macros such as `_Q_TAIL_MASK` and `_Q_LOCKED_PENDING_MASK`, plus Linux atomic operations. `rqspinlock.c` uses it when a timed-out MCS queue head attempts to reset the tail to zero without requiring 16-bit cmpxchg support on all architectures.

## Risks and Test Signals
The main risk is lock-word corruption if qspinlock bit masks or layout change without updating this helper. Ordering is relaxed by design and relies on the `smp_wmb()` before `xchg_tail()` and on initialized MCS node visibility, so tests should stress timeout cleanup under concurrent lock/unlock and pending-bit churn. Build coverage across architectures without 16-bit cmpxchg is also important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/rqspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/stackmap.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/stackmap.c

## Purpose
`stackmap.c` implements `BPF_MAP_TYPE_STACK_TRACE` storage and the BPF helpers that collect stack ids or raw stack data. It captures kernel or user callchains, optionally converts user instruction pointers to build-id plus file-offset records, hashes traces into a preallocated map, and exposes stack extraction/deletion operations to syscalls.

## Important APIs, Types, and Functions
`struct stack_map_bucket` stores freelist linkage, trace hash, frame count, and flexible trace data. `struct bpf_stack_map` embeds `struct bpf_map`, owns a contiguous preallocated element pool, a per-CPU freelist, bucket count, and bucket pointer table. `stack_map_alloc()` validates map attributes, allocates the bucket table, obtains perf callchain buffers, and preallocates all stack buckets. `stack_map_free()` releases the pool, freelist, map, and callchain buffers.

`stack_map_calculate_max_depth()` applies skip count and `sysctl_perf_event_max_stack`. `stack_map_get_build_id_offset()` resolves user IPs to `struct bpf_stack_build_id` entries using mmap lookup and build-id parsing, with IP fallback when lookup is unsafe. `__bpf_get_stackid()` hashes a callchain, compares or replaces buckets, and implements `BPF_F_FAST_STACK_CMP` and `BPF_F_REUSE_STACKID`. Helper front ends include `bpf_get_stackid()`, `bpf_get_stackid_pe()`, `bpf_get_stack()`, `bpf_get_stack_sleepable()`, `bpf_get_task_stack()`, `bpf_get_task_stack_sleepable()`, and `bpf_get_stack_pe()`. Syscall/map operations include `bpf_stackmap_extract()`, lookup-and-delete, get-next-key, delete, mem-usage, and map ops registration through `stack_trace_map_ops`.

## Control Flow
Map creation rejects unsupported flags, wrong key/value sizes, zero entries, oversized stack depth, and `max_entries` values that could overflow `roundup_pow_of_two()`. It rounds the hash table to a power of two, allocates `struct bpf_stack_map` plus bucket pointers, reserves global callchain buffers, then populates a freelist with fixed-size bucket objects.

For `bpf_get_stackid()`, the helper validates flags, collects a perf callchain for kernel or user frames, applies skip/max-depth logic, hashes IP data, and looks up the target bucket by `hash & (n_buckets - 1)`. A matching hash may return immediately with `BPF_F_FAST_STACK_CMP`; otherwise the helper performs full data comparison. Build-id mode allocates a candidate bucket before comparison so IPs can be translated to build-id records. On collision without `BPF_F_REUSE_STACKID`, it returns `-EEXIST`; otherwise it atomically swaps in the new bucket and returns any old bucket to the freelist.

For raw stack helpers, `__bpf_get_stack()` validates flags and element size, obtains a callchain from an input perf sample, a task stack, or `get_perf_callchain()`, copies IPs or build-id records to the caller buffer, zero-fills unused space, and clears the output buffer on validation/fault errors. Perf-event variants reuse sampled callchains when `PERF_SAMPLE_CALLCHAIN` is present and split kernel/user regions by scanning for `PERF_CONTEXT_USER`.

## State and Persistence Behavior
The map persists while its BPF map reference count is nonzero. Bucket storage is preallocated at map creation, and buckets move between the per-CPU freelist and the bucket table with atomic `xchg()`. Stack ids are not stable across replacement collisions when `BPF_F_REUSE_STACKID` is used. Build-id translation depends on the current task's `mm` and VMA state at capture time. There is no disk persistence; userspace must extract map values if it wants durable stack traces.

## Dependencies and Integration Points
The file depends on BPF map infrastructure, perf callchain APIs, stacktrace support, per-CPU freelists, build-id parsing, VMA lookup, RCU, mmap lock/unlock irq work, task stack access, BTF ids, and helper prototype registration in other BPF dispatch code. It integrates with perf-event BPF contexts, tracing helpers, syscall map operations, and userspace consumers that read stack trace map entries.

## Risks and Test Signals
Risk areas include hash collision behavior, build-id fallback correctness under mmap lock contention or missing `current->mm`, buffer clearing on errors, 32-bit stacktrace IP widening, crosstask user-stack rejection, `trace->nr` restoration in perf-event paths, and freelist exhaustion. Test signals include stack map creation flag validation, kernel/user stackid collection, build-id and raw-IP modes, fast-compare collisions, reuse vs `-EEXIST`, lookup-and-delete semantics, get-next-key iteration under RCU, sleepable stack helpers, task stack helpers, and KASAN/KCSAN stress for concurrent delete/extract/update-by-helper paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/stackmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/states.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/states.c

## Purpose
`states.c` implements BPF verifier state pruning, equivalence, liveness cleanup, precision propagation, and loop/SCC bookkeeping. It decides when a verifier path can be stopped because a previously explored state is at least as conservative, while preserving scalar ID relationships, reference ownership, stack metadata, iterator convergence rules, and precision/read marks needed for later safety checks.

## Important APIs, Types, and Functions
The exported entry points are `bpf_is_state_visited()` and `bpf_update_branch_counts()`. `bpf_is_state_visited()` is called at verifier checkpoints to clean the current state, compare it against states stored for the current instruction, detect loops, propagate precision, add SCC backedges, evict unhelpful states, or store a new checkpoint. `bpf_update_branch_counts()` decrements parent branch counts as paths finish, exits SCC visits, and frees eligible verifier states.

SCC helpers include `compute_scc_callchain()`, `scc_visit_lookup()`, `scc_visit_alloc()`, `maybe_enter_scc()`, `maybe_exit_scc()`, `add_scc_backedge()`, `incomplete_read_marks()`, and `propagate_backedges()`. State comparison helpers include `range_within()`, `check_ids()`, `check_scalar_ids()`, `regsafe()`, `stacksafe()`, `refsafe()`, `func_states_equal()`, and `states_equal()`. Cleanup and precision helpers include `clean_verifier_state()`, `__clean_func_state()`, `propagate_precision()`, `mark_all_scalars_imprecise()`, and the late-init `unbound_reg_init()`.

## Control Flow
At each checkpoint, `bpf_is_state_visited()` decides whether adding a new state is worthwhile based on force-checkpoint flags, jump history, and processed instruction/jump deltas. It first calls `clean_verifier_state()` to mark dead registers uninitialized and poison dead stack halves, while preserving special stack slots such as dynptrs, iterators, and IRQ flags. It then scans the explored-state list for the instruction.

If it finds an in-progress state with remaining branches, it performs loop handling rather than normal pruning. Iterator `next` calls, `may_goto`, and callback calls use specialized equivalence checks to prove convergence without declaring valid iterator loops infinite. Otherwise, exact same-state loops with unchanged iterator depths, may-goto depth, and callback unroll depth are rejected as infinite loops. If the path is not pruned, heuristics may suppress adding another checkpoint inside tight loops.

If it finds a completed state, it compares old and current state. When old state has incomplete read marks because an SCC visit still has pending backedges, comparison is stricter (`RANGE_WITHIN`) and a copy of the current state is attached as a backedge. On a hit, precision from the old equivalent state is propagated into the current state and the function returns `1` to tell the verifier this path can stop. On misses, hit/miss counters drive eviction to `env->free_list`, where states are freed only when not referenced, branchless, and not needed for incomplete SCC read marks.

When no equivalent state is found and heuristics allow it, a new `bpf_verifier_state_list` is allocated, singular IDs are cleared, scalar precision may be reset for capable users, the current state is copied, SCC entry is recorded if the instruction is inside a strongly connected component, and the current state points back to the new checkpoint as parent.

## State and Persistence Behavior
State is entirely verifier-runtime memory. `env->explored_states` holds checkpoint states by instruction, `env->free_list` holds evicted but still possibly referenced states, and `env->scc_info` stores per-SCC/per-callchain visit records and backedges for one `do_check_common()` run. Parent links, branch counts, `hit_cnt`/`miss_cnt`, `num_backedges`, and `peak_states` drive memory lifecycle and accounting. No verifier state persists beyond the program verification attempt.

## Dependencies and Integration Points
The file depends on `linux/bpf_verifier.h` definitions for register, stack, reference, iterator, callback, and SCC metadata. It calls verifier helpers for liveness queries, stack-slot liveness, precision marking, state copy/free, jump history, explored-state lookup, logging, force checkpoints, callbacks, and instruction classification. It directly affects verifier behavior for loops, callbacks, open-coded iterators, resilient lock references, IRQ flags, dynptrs, packet/map pointers, arena pointers, and scalar precision.

## Risks and Test Signals
Incorrect pruning can accept unsafe programs or reject safe ones. Specific risks include broken scalar ID remapping, mishandled `BPF_ADD_CONST` relationships, stack half-slot cleanup destroying metadata needed by dynptr/iterator/IRQ logic, premature freeing of states still needed by SCC backedges, under-propagated precision/read marks in cyclic control flow, and false infinite-loop detection around iterators or async callbacks. Test signals include verifier selftests for scalar linked IDs, pointer range pruning, stack spill equivalence, uninitialized stack mode, dynptr and iterator stack slots, resilient lock reference matching, callback recursion/async callbacks, `may_goto`, bounded and unbounded loops, SCC precision propagation, and memory-accounting limits for non-capable users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/states.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/stream.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/stream.c

## Purpose
`stream.c` implements per-BPF-program stdout/stderr style streams used by BPF diagnostics and kfuncs. It provides lockless append paths for formatted messages, mutex-protected userspace reads, staging buffers for atomic multi-line commits, and stack-dump formatting that can annotate BPF instruction pointers with source file and line information.

## Important APIs, Types, and Functions
Internal stream element helpers are `bpf_stream_elem_init()`, `bpf_stream_elem_alloc()`, `__bpf_stream_push_str()`, `bpf_stream_consume_capacity()`, `bpf_stream_release_capacity()`, and `bpf_stream_push_str()`. Backlog/read helpers are `bpf_stream_backlog_peek()`, `bpf_stream_backlog_pop()`, `bpf_stream_backlog_fill()`, `bpf_stream_consume_elem()`, and `bpf_stream_read()`. Public program lifecycle/read functions are `bpf_prog_stream_init()`, `bpf_prog_stream_free()`, and `bpf_prog_stream_read()`.

The BPF kfuncs are `bpf_stream_vprintk()` and `bpf_stream_print_stack()`. Staging APIs used by in-kernel diagnostics include `bpf_stream_stage_init()`, `bpf_stream_stage_free()`, `bpf_stream_stage_printk()`, `bpf_stream_stage_commit()`, and `bpf_stream_stage_dump_stack()`. `dump_stack_cb()` is the architecture stack-walk callback that formats symbols and BPF file/line annotations.

## Control Flow
Producers validate stream ids with `bpf_stream_get()`, reserve capacity atomically, allocate a `bpf_stream_elem`, copy the string, and push it onto an `llist_head`. `bpf_stream_vprintk()` prepares binary printf arguments with `bpf_bprintf_prepare()`, formats into a BPF printf buffer, pushes the formatted bytes excluding the terminating NUL, and cleans up. Staged logging accumulates elements on a local `bpf_stream_stage`; commit reserves total capacity once, drains the stage list, finds its tail, and appends the batch to the program stream.

Readers call `bpf_prog_stream_read()`, which takes the stream mutex, moves the lockless log list into FIFO backlog order with `llist_reverse_order()`, and copies element data to userspace. Elements can be partially consumed; `consumed_len` is restored if `copy_to_user()` fails. Fully consumed elements release capacity and are freed.

Stack dump flow prints a CPU/UID/PID/comm header, prints `Call trace:`, walks the architecture BPF stack, resolves each IP through `bpf_prog_ksym_find()`, optionally maps it to BPF source file/line with `bpf_prog_get_file_line()`, and appends formatted frames to the stage before commit by the caller.

## State and Persistence Behavior
Each `struct bpf_prog_aux` owns two `struct bpf_stream` instances, indexed as `BPF_STDOUT` and `BPF_STDERR`. A stream tracks atomic queued capacity, a lockless producer log, a mutex-protected FIFO backlog, and backlog head/tail pointers. Elements persist until read or program stream free. Capacity is bounded by `BPF_STREAM_MAX_CAPACITY`; staged logs are temporary and must be freed or committed. No data persists after the BPF program is freed.

## Dependencies and Integration Points
The file depends on BPF program and aux structures, BPF memory allocation (`kmalloc_nolock`/`kfree_nolock`), linked-list primitives, mutexes, atomics, userspace copy helpers, BPF printf formatting buffers, credentials/current task state, architecture BPF stack walking, kallsyms-like BPF program lookup, and source-line lookup. It integrates with `rqspinlock.c` diagnostics through `bpf_stream_stage`, and with user-facing program stream read paths elsewhere in BPF filesystem or syscall plumbing.

## Risks and Test Signals
Important risks include capacity leaks on failed staged commits with a non-empty list, FIFO ordering mistakes when moving from lockless log to backlog, partial-read accounting bugs, `copy_to_user()` rollback errors, allocation in contexts where `kmalloc_nolock()` can fail, and stack dump recursion or symbol lookup races. Test signals include concurrent producers with userspace readers, stdout/stderr id validation, capacity-limit enforcement, partial reads over element boundaries, read fault rollback, program teardown with unread log/backlog data, `bpf_stream_vprintk()` argument validation, staged multi-line commit ordering, stack dump formatting, and integration tests that verify resilient-spinlock violations appear on stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/stream.c -->
