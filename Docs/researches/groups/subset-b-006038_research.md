# subset-b-006038 research

Grouped research report for the locking sources under `sources/distributed-fs/ceph-client/kernel/locking`. Each section preserves the source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/mutex.c -->
# sources/distributed-fs/ceph-client/kernel/locking/mutex.c

## Purpose
Implements the generic non-PREEMPT_RT Linux mutex and wound/wait mutex acquisition paths, plus the common `atomic_dec_and_mutex_lock()` helper that remains outside the non-RT block. A mutex is a sleeping exclusive lock with owner tracking, a wait list, optional optimistic spinning, lockdep/debug hooks, hung-task blocker integration, and lock contention tracepoints.

## Important APIs, Types, and Functions
- Public exports include `mutex_lock()`, `mutex_unlock()`, `mutex_trylock()`, `mutex_lock_interruptible()`, `mutex_lock_killable()`, `mutex_lock_io()`, `ww_mutex_lock()`, `ww_mutex_lock_interruptible()`, `ww_mutex_trylock()`, `ww_mutex_unlock()`, and `atomic_dec_and_mutex_lock()`.
- Internal fast paths are `__mutex_trylock_fast()`, `__mutex_unlock_fast()`, `__mutex_trylock_common()`, and `__mutex_trylock_or_handoff()`.
- Wait-list and handoff helpers are `__mutex_add_waiter()`, `__mutex_remove_waiter()`, `__mutex_handoff()`, `__mutex_lock_common()`, and `__mutex_unlock_slowpath()`.
- Optional spin-on-owner support uses `mutex_optimistic_spin()`, `mutex_spin_on_owner()`, `mutex_can_spin_on_owner()`, and the optimistic spin queue from `osq_lock.c`.
- Wound/wait integration comes from `ww_mutex.h` via `__ww_mutex_add_waiter()`, `__ww_mutex_check_waiters()`, `__ww_mutex_check_kill()`, and `ww_mutex_lock_acquired()`.

## Control Flow
The uncontended path tries to atomically set `lock->owner` from `0` to `current` with acquire semantics. On failure, `__mutex_lock_common()` disables preemption, records lockdep contention, tries a full owner/flag aware trylock, then optionally optimistic-spins while the owner is running. If spinning fails, the task is inserted into the circular waiter list protected by `wait_lock`, `current->blocked_on` is set, and the task sleeps in the requested state until it can pick up an explicit handoff or acquire the owner field. Unlock first attempts a release cmpxchg to clear an owner with no flags; the slow path clears or hands off ownership and queues the top waiter for wakeup.

## State and Persistence
State is in memory only. `struct mutex` stores `owner` with low-bit flags for waiters, handoff, and pickup; `first_waiter` anchors a circular list; `wait_lock` serializes slow paths; `osq` serializes optimistic spinners when enabled. Waiter records live on blocked tasks' stacks, and hung-task blocker state is updated while waiting.

## Dependencies and Integration Points
Depends on `linux/mutex.h`, `linux/ww_mutex.h`, scheduler state and wake queues, raw spinlocks, lockdep, trace events, `osq_lock`, and hung-task debugging. It integrates with scheduler blocked-on tracking through `__set_task_blocked_on()` and with exported lock contention tracepoints `contention_begin` and `contention_end`.

## Risks
The correctness-critical areas are owner flag transitions, release/acquire pairing across handoff, wakeup ordering while canceling signalable waits, and preserving wait-list order for ww_mutex deadlock avoidance. Optimistic spinning uses speculative `task_struct` owner reads and relies on preemption-disabled RCU-like lifetime protection. `mutex_unlock()` cannot be used as the final reference drop when another task may free the object immediately after observing unlock.

## Test Signals
Build coverage should include `CONFIG_DEBUG_MUTEXES`, `CONFIG_DEBUG_LOCK_ALLOC`, `CONFIG_MUTEX_SPIN_ON_OWNER`, ww_mutex users, and PREEMPT_RT disabled/enabled configurations. Runtime signals include lockdep splats, hung-task blocker reports, `contention_begin/end` tracepoints, ww_mutex `-EDEADLK` handling, and stress tests that combine signal interruption, handoff, trylock, and unlock/free races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/mutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/mutex.h -->
# sources/distributed-fs/ceph-client/kernel/locking/mutex.h

## Purpose
Private non-PREEMPT_RT mutex header defining the stack waiter record, owner flag layout, owner access helper, scheduler blocked-on helper, and debug hook declarations used by `mutex.c`.

## Important APIs, Types, and Functions
- `struct mutex_waiter` contains the wait-list link, blocked task, optional `ww_acquire_ctx`, and debug magic.
- `MUTEX_FLAG_WAITERS`, `MUTEX_FLAG_HANDOFF`, and `MUTEX_FLAG_PICKUP` occupy low bits of the owner word; `MUTEX_FLAGS` masks them.
- `__mutex_owner()` returns the owner pointer after masking flags.
- `get_task_blocked_on()` reads a task's blocked mutex under `blocked_lock`.
- Debug declarations or no-op macros provide `debug_mutex_*()` integration.

## Control Flow
This header has no independent runtime loop, but its flag layout drives the `mutex.c` state machine. The `WAITERS` flag causes unlock slow path wakeups, `HANDOFF` prevents opportunistic stealing, and `PICKUP` lets a designated waiter atomically claim ownership.

## State and Persistence
No persistent storage. It defines in-memory stack waiters and the owner-bit encoding contract for `struct mutex`.

## Dependencies and Integration Points
Included only when `CONFIG_PREEMPT_RT` is disabled. It depends on `linux/mutex.h` and task blocked-on scheduler internals. Debug hooks are supplied by the debug mutex implementation when `CONFIG_DEBUG_MUTEXES` is enabled.

## Risks
The low-bit flag scheme depends on task pointer alignment. Any change to flag values must match every atomic owner manipulation in `mutex.c`. `__mutex_owner()` intentionally drops flag state; using it where flags matter can hide handoff or waiter transitions.

## Test Signals
Compile matrix should cover debug and non-debug mutex builds. Behavioral signals are lockdep/debug mutex warnings for bad magic, recursive locking, wait-list corruption, and owner/blocked-on mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/osq_lock.c -->
# sources/distributed-fs/ceph-client/kernel/locking/osq_lock.c

## Purpose
Implements the optimistic spin queue used by sleeping locks such as mutexes and rwsems to serialize spinners. It is an MCS-like per-CPU queue that lets only one active spinner contend on the real lock while allowing cancellation when the task needs rescheduling or detects a preempted predecessor.

## Important APIs, Types, and Functions
- `struct optimistic_spin_node` stores `next`, `prev`, `locked`, and encoded CPU id.
- `osq_lock()` enqueues the current CPU and returns true when it acquired the queue or false when it canceled.
- `osq_unlock()` passes the queue token to the next node or clears the tail.
- `osq_wait_next()` stabilizes the next pointer during unlock or unqueue.

## Control Flow
`osq_lock()` initializes the per-CPU node, swaps it into `lock->tail`, and succeeds immediately when the queue was empty. Otherwise it links behind the predecessor and waits on `node->locked` until either the predecessor unlocks or cancellation conditions hold. Cancellation unlinks the node in three steps: detach from `prev->next`, stabilize `next` or tail, then reconnect `prev` and `next`. `osq_unlock()` clears the tail in the uncontended case, otherwise wakes the recorded next node or waits until it can identify one.

## State and Persistence
State is per-CPU static `osq_node` plus the queue tail in `struct optimistic_spin_queue`. It is volatile synchronization state only; no disk persistence.

## Dependencies and Integration Points
Used by mutex and rwsem optimistic spinning. Depends on per-CPU APIs, scheduler `need_resched()`, `vcpu_is_preempted()`, SMP atomics, and memory barriers.

## Risks
The unlink protocol is race-prone: predecessor and successor nodes are static per CPU, but their pointers must be cleared and reconnected in exact order to avoid stale links. This code assumes sleeping locks do not use OSQ from interrupt context and that preemption is disabled while spinning.

## Test Signals
Signals include lock contention stress under `CONFIG_MUTEX_SPIN_ON_OWNER` and `CONFIG_RWSEM_SPIN_ON_OWNER`, preemption/virtualization stress that triggers cancellation, and lockup detection from queue corruption or missed handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/osq_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/percpu-rwsem.c -->
# sources/distributed-fs/ceph-client/kernel/locking/percpu-rwsem.c

## Purpose
Implements per-CPU read/write semaphores optimized for frequent readers. Readers usually increment a per-CPU counter without taking a global lock; writers block new readers, wait for active per-CPU counters to drain, and then hold exclusive access.

## Important APIs, Types, and Functions
- Exports `__percpu_init_rwsem()`, `percpu_free_rwsem()`, `__percpu_down_read()`, `percpu_is_read_locked()`, `percpu_down_write()`, and `percpu_up_write()`.
- Fast reader path is `__percpu_down_read_trylock()`.
- Writer exclusion is `__percpu_down_write_trylock()`.
- Slow waiter handling uses `percpu_rwsem_wait()` and `percpu_rwsem_wake_function()`.
- Reader drain test is `readers_active_check()`.

## Control Flow
Initialization allocates `read_count` per CPU, initializes `rcu_sync`, `rcuwait`, wait queue, and `block`. A reader disables preemption in the caller path, increments its CPU counter, issues a memory barrier, and succeeds if `block` is not set; otherwise it decrements and wakes the writer. A writer enters `rcu_sync`, atomically sets `block`, optionally sleeps in FIFO wait queue order, then uses `rcuwait_wait_event()` until all per-CPU counts sum to zero. Unlock clears `block` with release ordering, wakes one queued operation through the custom wait function, and exits `rcu_sync` so readers can regain the fast path after a grace period.

## State and Persistence
State is in `struct percpu_rw_semaphore`: per-CPU `read_count`, `rcu_sync rss`, `rcuwait writer`, FIFO `waiters`, and atomic `block`. No persistence beyond in-memory synchronization.

## Dependencies and Integration Points
Depends on per-CPU allocation, RCU sync, rcuwait, wait queues, scheduler state, lockdep, trace events, and atomic ordering. It is used by subsystems needing extremely cheap read-side critical sections with occasional global write exclusion.

## Risks
The memory-barrier pairs around reader count and writer block are critical. Missing `percpu_free_rwsem()` after successful init leaks per-CPU storage. Writer latency can be high with long read-side sections. The wake function intentionally wakes readers until a writer is acquired, so its return protocol must match wait queue expectations.

## Test Signals
Test with lockdep, RCU stall detection, writer starvation tests, freezer paths through the `freeze` argument, and fault injection for `alloc_percpu()` failure. Runtime tracepoints for percpu read/write contention indicate slow-path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/percpu-rwsem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qrwlock.c -->
# sources/distributed-fs/ceph-client/kernel/locking/qrwlock.c

## Purpose
Provides slow paths for queued read/write spin locks. The implementation uses a small counter field for reader/writer state and a queued `wait_lock` to serialize slow readers and writers.

## Important APIs, Types, and Functions
- Exports `queued_read_lock_slowpath()` and `queued_write_lock_slowpath()`.
- Uses `struct qrwlock` fields `cnts` and `wait_lock`.
- Uses `_QW_LOCKED`, `_QW_WAITING`, and `_QR_BIAS` from qrwlock definitions.

## Control Flow
Slow readers in interrupt context do not queue; they spin with acquire semantics until no writer holds the lock. Process-context readers subtract their speculative read bias, queue on `wait_lock`, re-add the reader bias, wait until the writer-locked bit clears, and release the queue head. Writers take `wait_lock`, try to set `_QW_LOCKED` directly when no readers exist, otherwise set `_QW_WAITING` and spin until the counters equal waiting-only, then atomically promote to locked.

## State and Persistence
State is the in-memory `cnts` atomic and embedded queue spinlock. No external persistence.

## Dependencies and Integration Points
Depends on architecture spinlock primitives, SMP atomics, trace lock events, and interrupt context checks. Integrated under the raw rwlock implementation on architectures selecting queued rwlocks.

## Risks
Reader behavior differs in interrupt context to avoid blocking behind a queued writer that is not yet owner. Writer fairness depends on setting `_QW_WAITING` so new readers observe pending writer state. Memory ordering in `atomic_cond_read_acquire()` and `atomic_try_cmpxchg_acquire()` is required for critical-section ordering.

## Test Signals
Stress with mixed interrupt/process readers, writer-heavy contention, lockdep, and trace `LCB_F_READ`/`LCB_F_WRITE` contention. Regression symptoms are writer starvation, reader admission while writer locked, or deadlocks on `wait_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qrwlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qspinlock.c -->
# sources/distributed-fs/ceph-client/kernel/locking/qspinlock.c

## Purpose
Implements the queued spinlock slow path for compact 32-bit `qspinlock` words. It combines a pending-bit fast handoff with an MCS-style per-CPU queue encoded into the tail bits, and can recursively include itself to generate paravirtualized spinlock slow paths.

## Important APIs, Types, and Functions
- Exports `queued_spin_lock_slowpath()`.
- Maintains per-CPU `qnodes[_Q_MAX_NODES]`.
- Uses helpers from `qspinlock.h`: `encode_tail()`, `decode_tail()`, `grab_mcs_node()`, `xchg_tail()`, `clear_pending_set_locked()`, and `set_locked()`.
- Uses PV callback aliases `pv_init_node()`, `pv_wait_node()`, `pv_kick_node()`, and `pv_wait_head_or_lock()`.
- Defines the `nopvspin` early parameter when paravirt spinlocks are enabled.

## Control Flow
The slow path first handles a pending-only transient, then tries to set the pending bit when the lock has no queue. If it becomes pending, it waits for the locked byte to clear and atomically becomes owner. If contention exists, it allocates a per-CPU MCS node by nesting index, initializes it, optionally retries the lock, publishes its encoded tail with `xchg_tail()`, links after a predecessor, and waits until it reaches queue head. At head, it waits for locked and pending bits to clear or lets PV code acquire; then it either clears the tail and takes the lock or sets only the locked byte and wakes its successor.

## State and Persistence
State is a compact lock word containing locked, pending, and tail fields, plus per-CPU queue nodes. It is volatile only. Nested contexts are limited to task, softirq, hardirq, and nmi; overflow falls back to direct trylock spinning.

## Dependencies and Integration Points
Depends on architecture qspinlock definitions, MCS spinlock helpers, per-CPU storage, trace lock events, optional PV spinlocks, and lock event counters. This is the slow path behind architecture `queued_spin_lock()`.

## Risks
The 32-bit encoding relies on architecture support for atomic byte/halfword operations and CPU count fitting in tail bits. Memory barriers before tail publication and acquire waits at queue head are correctness-critical. Node nesting overflow is rare but intentionally less fair. PV generation through recursive inclusion can be fragile when macros change.

## Test Signals
SMP lock torture, nested interrupt locking, high CPU-count builds, paravirt and native build matrix, `nopvspin` boot parameter tests, and lock event counters for pending, slowpath, no-node, and node-index usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qspinlock.h -->
# sources/distributed-fs/ceph-client/kernel/locking/qspinlock.h

## Purpose
Shared internal definitions for queued spinlock slow paths. It defines per-CPU queue node layout, tail encoding/decoding, pending-bit manipulation, tail exchange, and locked-byte setting.

## Important APIs, Types, and Functions
- `struct qnode` embeds `struct mcs_spinlock` and optional PV padding.
- `_Q_MAX_NODES` sets the maximum nesting level to four.
- `encode_tail()` and `decode_tail()` map CPU and nesting index into/from the lock tail bits.
- `grab_mcs_node()` computes the node for a nesting index.
- `clear_pending()`, `clear_pending_set_locked()`, `xchg_tail()`, `queued_fetch_set_pending_acquire()`, and `set_locked()` operate on architecture-specific qspinlock fields.

## Control Flow
This header supplies inline operations used by `qspinlock.c`. There are two implementations of pending/tail operations depending on whether pending bits occupy a byte; byte-capable architectures can write subfields directly, while others update the full atomic word with compare/exchange loops.

## State and Persistence
No independent state besides the qnode layout. It defines how the `qspinlock` word and per-CPU nodes are interpreted.

## Dependencies and Integration Points
Depends on asm-generic qspinlock and MCS spinlock definitions, per-CPU accessors, and architecture qspinlock field layout. Included by both native and paravirtual slow-path generation.

## Risks
Incorrect tail encoding can make CPU 0/index 0 indistinguishable from no-tail, hence the CPU-plus-one encoding. Changing `_Q_PENDING_BITS` behavior affects memory ordering and atomic field updates. `xchg_tail()` uses relaxed semantics because callers must publish fully initialized MCS nodes first.

## Test Signals
Compile on architectures with and without 8-bit pending fields, CPU-count boundary builds, qspinlock torture, and KCSAN/lockdep signals around tail publication and successor wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qspinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qspinlock_paravirt.h -->
# sources/distributed-fs/ceph-client/kernel/locking/qspinlock_paravirt.h

## Purpose
Implements paravirtual queued spinlocks, replacing long busy-waits in guests with hypervisor wait/kick operations. It extends qspinlock with a slow locked value, per-node vCPU state, a lock-to-node hash table, and hybrid queued/unfair lock stealing.

## Important APIs, Types, and Functions
- `enum vcpu_state` tracks `VCPU_RUNNING`, `VCPU_HALTED`, and `VCPU_HASHED`.
- `struct pv_node` overlays qspinlock MCS nodes with CPU and state.
- `__pv_init_lock_hash()` allocates the PV hash table.
- `pv_hybrid_queued_unfair_trylock()`, `set_pending()`, and `trylock_clear_pending()` implement hybrid acquisition.
- `pv_hash()` and `pv_unhash()` map lock addresses to halted nodes.
- `pv_wait_node()`, `pv_kick_node()`, `pv_wait_head_or_lock()`, `__pv_queued_spin_unlock_slowpath()`, and `__pv_queued_spin_unlock()` implement wait/kick protocol.

## Control Flow
An incoming waiter may briefly steal the lock while no pending bit is set. Queued nodes initialize PV state and may halt early if their predecessor vCPU is not running. Queue-head waiters set pending to suppress stealing, try to acquire for a bounded spin, then hash themselves and store `_Q_SLOW_VAL` so unlock can find and kick them. Unlock normally cmpxchg-releases `_Q_LOCKED_VAL` to zero; if the byte is `_Q_SLOW_VAL`, it unhashes the queue-head node, releases the lock, and kicks that vCPU.

## State and Persistence
State is in-memory: qspinlock locked byte values, per-node vCPU state, and a boot-allocated open-addressed hash table sized to possible CPUs. No persistent storage.

## Dependencies and Integration Points
Requires architecture paravirt hooks `pv_wait()` and `pv_kick()`, `asm/qspinlock_paravirt.h` thunk support, memblock/hash allocation, qspinlock stat wrappers, and debug locks.

## Risks
Hash table correctness is critical: a slow-value unlock assumes exactly one discoverable hash entry. Ordering between hash insertion, `_Q_SLOW_VAL`, unhash, and wake/kick is enforced with barriers and must not be weakened. Hybrid unfair stealing improves light contention but depends on pending-bit discipline to avoid starving queued vCPUs.

## Test Signals
Boot and lock torture under overcommitted virtual machines, PV hash hop counters, kick/wake latency counters, corrupted slow-value warnings, `nopvspin` comparison, and stress of halted/running predecessor transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qspinlock_paravirt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qspinlock_stat.h -->
# sources/distributed-fs/ceph-client/kernel/locking/qspinlock_stat.h

## Purpose
Adds optional qspinlock and PV qspinlock lock-event accounting. When lock event counts and paravirt spinlocks are enabled, it provides debugfs-style read support and wraps `pv_wait()`/`pv_kick()` to measure latency.

## Important APIs, Types, and Functions
- `lockevent_read()` formats raw counters or derived averages.
- `lockevent_pv_hop()` accumulates PV hash probe counts.
- `__pv_kick()` measures kick latency and records per-target kick time.
- `__pv_wait()` measures wake latency and counts kicks that woke the current CPU.
- `pv_kick` and `pv_wait` are macro-redefined to wrappers when enabled.

## Control Flow
Reads locate the event id from inode private data, sum per-CPU counters, and for latency or hash-hop events divide by the relevant kick count. PV wait/kick wrappers timestamp with `sched_clock()` around the hypercall or after wake and add results into lockevents.

## State and Persistence
State consists of per-CPU `lockevents[]` from `lock_events.h` and per-CPU `pv_kick_time`. It is runtime diagnostic state only.

## Dependencies and Integration Points
Depends on `CONFIG_LOCK_EVENT_COUNTS`, optional `CONFIG_PARAVIRT_SPINLOCKS`, scheduler clock, simple read buffer helpers, and qspinlock PV code that calls `lockevent_pv_hop()`.

## Risks
Instrumentation must not perturb locking semantics. Per-CPU `pv_kick_time` is a best-effort timing channel and can be overwritten by concurrent events on the target CPU. Derived averages depend on nonzero denominator counters.

## Test Signals
Enable lock event counts and verify readable counters for PV latency, hash hops, kicks, waits, and wakeups. Compare zero-overhead stubs when the config is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/qspinlock_stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rtmutex.c -->
# sources/distributed-fs/ceph-client/kernel/locking/rtmutex.c

## Purpose
Core real-time mutex implementation with priority inheritance, used by rt_mutex APIs, PI futexes, and PREEMPT_RT substitutions for mutexes and spin/rwlocks. It manages owner encoding, priority-ordered wait queues, owner PI trees, chain walking, deadlock detection, wakeup handoff, and slow lock/unlock paths.

## Important APIs, Types, and Functions
- Owner helpers: `rt_mutex_set_owner()`, `rt_mutex_clear_owner()`, `mark_rt_mutex_waiters()`, `fixup_rt_mutex_waiters()`, and cmpxchg acquire/release helpers.
- Ordering helpers: `rt_waiter_node_less()`, `rt_mutex_enqueue()`, `rt_mutex_dequeue()`, `rt_mutex_enqueue_pi()`, and `rt_mutex_dequeue_pi()`.
- PI propagation: `rt_mutex_adjust_prio()`, `task_blocks_on_rt_mutex()`, `remove_waiter()`, and `rt_mutex_adjust_prio_chain()`.
- Acquisition and release: `try_to_take_rt_mutex()`, `rt_mutex_slowtrylock()`, `__rt_mutex_trylock()`, `__rt_mutex_slowlock()`, `rt_mutex_slowlock()`, `__rt_mutex_lock()`, `rt_mutex_slowunlock()`, and `__rt_mutex_unlock()`.
- RT lock support: `rtlock_slowlock_locked()` and `rtlock_slowlock()` under `RT_MUTEX_BUILD_SPINLOCKS`.

## Control Flow
Fast acquisition cmpxchg's owner from NULL to current when no waiters bit is present. Slow acquisition takes `wait_lock`, marks the waiters bit to force serialization, tries again, then enqueues a stack waiter in the lock waiters rbtree and links the top waiter into the owner's `pi_waiters` rbtree. If the owner is blocked, `rt_mutex_adjust_prio_chain()` walks at most `max_lock_depth` links, requeueing waiters as priorities/deadlines change and detecting cycles when configured. A blocked task loops trying to take the lock, checking signals/timeouts/ww kills, optionally spinning on an on-CPU owner, and scheduling. Unlock either fast cmpxchg-releases owner or slow-path deboosts current, sets owner to waiter-transitional state, queues the top waiter, and wakes after dropping `wait_lock`.

## State and Persistence
`rt_mutex_base` holds `owner` with a low waiters bit, raw `wait_lock`, and cached rbtree of waiters. Each task has `pi_lock`, `pi_waiters`, and `pi_blocked_on`. Waiter objects are stack-allocated for normal waits or supplied by futex proxy paths. No disk persistence.

## Dependencies and Integration Points
Depends on scheduler priority/deadline APIs, `rt_mutex_setprio()`, wake queues, task state helpers, lock events, lockdep/debug hooks, optional ww_mutex code, and trace lock events. Included directly by `rtmutex_api.c`, `rwsem.c` RT code, and `spinlock_rt.c` with build macros selecting exported subsets.

## Risks
Priority-inheritance chain walking is high risk: reverse lock ordering requires trylock/retry, task lifetime relies on references, and stale chain observations must be revalidated. Waiters bit transitions are deliberately transient and must be fixed before leaving slow paths. Deadlock handling differs for ww_mutex cycles, debug builds, futex full chain walks, and RT locks. Wakeup ordering includes a deliberate preempt-disable region to avoid inversion between deboost and wake.

## Test Signals
RT mutex torture, PI futex tests, scheduler priority/deadline changes while blocked, `max_lock_depth` sysctl, ww_mutex deadlock tests, PREEMPT_RT spinlock substitution stress, lockdep, KCSAN, and lock event counters for slow acquire/sleep/deadlock/wake paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rtmutex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rtmutex_api.c -->
# sources/distributed-fs/ceph-client/kernel/locking/rtmutex_api.c

## Purpose
Builds public rt_mutex APIs on top of `rtmutex.c`, exposes PI futex proxy operations, registers the `kernel.max_lock_depth` sysctl, and, under PREEMPT_RT, provides regular mutex APIs backed by rt_mutex internals.

## Important APIs, Types, and Functions
- Public rt_mutex exports: `rt_mutex_base_init()`, `rt_mutex_lock()`, `rt_mutex_lock_interruptible()`, `rt_mutex_lock_killable()`, `rt_mutex_trylock()`, `rt_mutex_unlock()`, and debug nested variants.
- Futex APIs: `rt_mutex_futex_trylock()`, `__rt_mutex_futex_trylock()`, `__rt_mutex_futex_unlock()`, `rt_mutex_futex_unlock()`, `rt_mutex_init_proxy_locked()`, `rt_mutex_proxy_unlock()`, `__rt_mutex_start_proxy_lock()`, `rt_mutex_start_proxy_lock()`, `rt_mutex_wait_proxy_lock()`, and `rt_mutex_cleanup_proxy_lock()`.
- PI maintenance: `rt_mutex_adjust_pi()` and `rt_mutex_postunlock()`.
- PREEMPT_RT mutex exports mirror regular mutex functions with rtmutex backing.

## Control Flow
`__rt_mutex_lock_common()` wraps lockdep acquire, calls `__rt_mutex_lock()`, and releases lockdep on failure. Trylock uses `__rt_mutex_trylock()` and acquires lockdep only on success. Futex proxy start attempts direct ownership for a target task, otherwise enqueues the supplied waiter with full chainwalk deadlock detection; wait then blocks on that waiter, and cleanup races with possible late ownership by trying to take the lock before removing the waiter. PREEMPT_RT mutex wrappers call the same rtmutex core while preserving normal mutex lockdep names and I/O-wait handling.

## State and Persistence
Adds global in-memory `max_lock_depth` exposed through sysctl. All lock state remains inside `rt_mutex`, `rt_mutex_base`, supplied futex waiters, and task PI fields.

## Dependencies and Integration Points
Depends on `rtmutex.c` with `RT_MUTEX_BUILD_MUTEX`, proc sysctl registration, lockdep, futex PI callers, wake queues, and PREEMPT_RT mutex substitution. The proxy APIs integrate with futex pi_state lifetime rules and hash bucket locking.

## Risks
Proxy locking is sensitive to races where the owner releases while a waiter is being enqueued or cleaned up. `rt_mutex_start_proxy_lock()` removes the waiter on failure while `__rt_mutex_start_proxy_lock()` deliberately does not, so caller contracts differ. PREEMPT_RT mutex behavior differs from non-RT mutex in PI and sleeping spinlock interactions.

## Test Signals
PI futex selftests, robust futex timeout/signal cleanup, lockdep class checks for futex proxy locks, `max_lock_depth` sysctl changes, PREEMPT_RT mutex API compatibility tests, and debug task-free checks for nonempty PI trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rtmutex_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rtmutex_common.h -->
# sources/distributed-fs/ceph-client/kernel/locking/rtmutex_common.h

## Purpose
Private rt_mutex shared header defining waiter data structures, wake queue wrapper, futex proxy prototypes, waiter-tree helpers, initialization helpers, and debug stubs used by rtmutex implementation units.

## Important APIs, Types, and Functions
- `struct rt_waiter_node` stores rbtree entry, priority, and deadline sort keys.
- `struct rt_mutex_waiter` contains lock wait-tree node, owner PI-tree node, task, lock pointer, wake state, and optional ww context.
- `struct rt_wake_q_head` wraps regular wake queues and a PREEMPT_RT special rtlock task.
- Helpers include `rt_mutex_has_waiters()`, `rt_mutex_waiter_is_top_waiter()`, `rt_mutex_top_waiter()`, `task_has_pi_waiters()`, `task_top_pi_waiter()`, `__rt_mutex_base_init()`, `rt_mutex_init_waiter()`, and `rt_mutex_init_rtlock_waiter()`.

## Control Flow
The inline helpers provide the low-level checks used throughout `rtmutex.c`: cached-leftmost rbtree lookup chooses the top waiter, task PI trees choose the top donor, initialization clears rbtree nodes and owner state, and debug helpers poison waiters in debug builds.

## State and Persistence
Defines in-memory waiter/tree layouts only. Waiters are typically stack-allocated and are valid only while the task is blocked or a futex proxy operation owns their lifetime.

## Dependencies and Integration Points
Depends on `linux/rtmutex.h`, task wake queues, debug locks, rbtrees through included kernel headers, and scheduler task fields. Also provides prototypes consumed by futex PI and RCU code paths.

## Risks
`rt_mutex_waiter_is_top_waiter()` is a speculative pointer comparison and assumes callers respect locking/lifetime rules. `task_top_pi_waiter()` assumes a nonempty tree. Waiter initialization and cleanup poisoning help detect use-after-free in debug builds, but production builds rely on exact stack lifetime discipline.

## Test Signals
Compile with and without `CONFIG_RT_MUTEXES` and `CONFIG_DEBUG_RT_MUTEXES`; run PI lock tests that enqueue/dequeue waiters, verify debug poisoning catches stale waiter use, and lockdep checks for wait_lock/pi_lock ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rtmutex_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rwbase_rt.c -->
# sources/distributed-fs/ceph-client/kernel/locking/rwbase_rt.c

## Purpose
Common PREEMPT_RT base implementation for rw semaphores and rwlocks backed by an rt_mutex plus an atomic reader count. It gives writers priority inheritance through rt_mutex while allowing fast reader increments when no writer has removed the reader bias.

## Important APIs, Types, and Functions
- Reader helpers: `rwbase_read_trylock()`, `__rwbase_read_lock()`, `rwbase_read_lock()`, `__rwbase_read_unlock()`, and `rwbase_read_unlock()`.
- Writer helpers: `rwbase_write_lock()`, `rwbase_write_trylock()`, `rwbase_write_unlock()`, `rwbase_write_downgrade()`, `__rwbase_write_unlock()`, and `__rwbase_write_trylock()`.
- Behavior is parameterized by macros supplied by `rwsem.c` or `spinlock_rt.c` for scheduling, signal handling, and rtmutex operations.

## Control Flow
Readers first try to increment `readers` while it is negative, meaning `READER_BIAS` is present. If fast path fails, a reader takes the underlying rtmutex slow path under `wait_lock`, increments readers once no writer is active, drops `wait_lock`, and unlocks the rtmutex. Writers first lock the rtmutex, subtract `READER_BIAS` to force new readers slow, then wait under `wait_lock` until active readers drain and set `WRITER_BIAS`. Unlock restores reader bias with release ordering and unlocks the rtmutex; downgrade restores bias while accounting the writer as one reader.

## State and Persistence
State is in `struct rwbase_rt`: an `rt_mutex_base` plus atomic `readers` counter carrying reader bias and writer bias. No persistence.

## Dependencies and Integration Points
Included by both `rwsem.c` and `spinlock_rt.c` after defining macro adapters. Integrates with rtmutex PI, wake queues, scheduler/task state preservation, lock trace events, and lockdep in wrappers.

## Risks
The implementation is intentionally not writer-fair for readers on RT; writer starvation is documented as possible. Fast-path acquire/release ordering must pair with writer bias changes. Macro adapter mistakes can break signal behavior for semaphores versus non-signalable RT rwlocks.

## Test Signals
PREEMPT_RT rwsem and rwlock tests with mixed readers/writers, writer starvation stress, signalable `down_write_killable()` paths, lockdep for rtmutex nesting, and trace contention for RT read/write waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rwbase_rt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rwsem.c -->
# sources/distributed-fs/ceph-client/kernel/locking/rwsem.c

## Purpose
Implements Linux read/write semaphores. In non-PREEMPT_RT builds it uses a packed atomic count, owner hints, wait list, handoff, and optimistic spinning. In PREEMPT_RT builds it substitutes the common rtmutex-backed `rwbase_rt.c` implementation. The common bottom half exports the public rwsem API and lockdep annotations.

## Important APIs, Types, and Functions
- Public exports include `down_read()`, `down_read_interruptible()`, `down_read_killable()`, `down_read_trylock()`, `down_write()`, `down_write_killable()`, `down_write_trylock()`, `up_read()`, `up_write()`, `downgrade_write()`, and debug nested/non-owner variants.
- Non-RT count bits include writer locked, waiters, handoff, readfail, and shifted reader count.
- Non-RT slow paths include `rwsem_down_read_slowpath()`, `rwsem_down_write_slowpath()`, `rwsem_mark_wake()`, `rwsem_try_write_lock()`, `rwsem_wake()`, and `rwsem_downgrade_wake()`.
- Optimistic spinning uses `rwsem_optimistic_spin()`, `rwsem_spin_on_owner()`, and OSQ.

## Control Flow
Readers add `RWSEM_READER_BIAS` with acquire semantics; if no failure bits are set, they mark reader-owned and enter. Otherwise they may steal when no writer/handoff exists or enqueue as read waiters. Writers cmpxchg from unlocked to writer-locked; on failure they may spin on the current owner, then enqueue as write waiters. `rwsem_mark_wake()` grants batches of front-of-queue readers in two passes or wakes a front writer. Handoff is set by long-waiting or RT/DL writers to prevent indefinite stealing. Unlock readers subtract bias and wake when only waiters remain; unlock writers clears owner, releases writer bit, and wakes waiters. PREEMPT_RT maps these operations to `rwbase_rt` while keeping the same public API.

## State and Persistence
Non-RT state is in `count`, `owner`, `wait_lock`, `first_waiter`, optional `osq`, and stack `rwsem_waiter` entries. RT state is `rwbase` with rtmutex and reader counter. State is in-memory only.

## Dependencies and Integration Points
Depends on scheduler state, wake queues, lockdep, hung-task blocker, lock events, trace events, OSQ, rtmutex/rwbase in RT builds, and exported rwsem APIs consumed across kernel subsystems.

## Risks
Packed count transitions are complex: handoff, waiters, reader grant batching, and downgrade must update flags and reader counts atomically. Owner is partly a debugging/spinning hint and may be stale for readers. Optimistic reader-owned spinning uses a time heuristic and nonspinnable flag. PREEMPT_RT semantics differ in fairness and PI behavior.

## Test Signals
rwsem lock torture, mmap-sem-like reader-heavy stress, RT/DL waiter scenarios, signalable reader/write waits, downgrade tests, non-owner debug APIs, hung-task blocker reports, lock event counters for sleep/wake/handoff/spinning, and PREEMPT_RT build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/rwsem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/semaphore.c -->
# sources/distributed-fs/ceph-client/kernel/locking/semaphore.c

## Purpose
Implements generic counting semaphores. Unlike mutexes, semaphores allow multiple acquisitions, `up()` can be called by a different task or interrupt, and `down_trylock()` uses the historical inverted return convention.

## Important APIs, Types, and Functions
- Exports `down()`, `down_interruptible()`, `down_killable()`, `down_trylock()`, `down_timeout()`, `up()`, and `sem_last_holder()`.
- Internal waiters use `struct semaphore_waiter` with list link, task, and `up` flag.
- Slow paths are `__down()`, `__down_interruptible()`, `__down_killable()`, `__down_timeout()`, `__down_common()`, `___down_common()`, and `__up()`.

## Control Flow
All public operations take `sem->lock` with irqsave because trylock/up may run from interrupt context and callers historically use successful `down()` in such contexts. Fast down decrements `count` when positive. Contended down enqueues a stack waiter on the circular wait list, sets task state, drops the spinlock, schedules with optional timeout, and returns when `__up()` marks `waiter.up`. Interruptible and killable variants remove the waiter and return `-EINTR`; timeout returns `-ETIME`. `up()` increments count when no waiters exist or removes the first waiter, marks it up, and wakes it outside the spinlock.

## State and Persistence
`struct semaphore` stores raw spinlock, integer count, and `first_waiter`; optional hung-task `last_holder` records the last acquiring task. State is in-memory only.

## Dependencies and Integration Points
Depends on scheduler sleep APIs, raw spinlocks, wake queues, ftrace/trace lock events, hung-task blocker hooks, and exported semaphore API.

## Risks
Semaphore ownership is intentionally loose, so it cannot provide mutex-style owner debugging. The inverted `down_trylock()` return value is a migration hazard. Waiter lifetime is stack-based and protected by the spinlock plus the `up` flag protocol. `last_holder` is diagnostic only and can be approximate when `up()` comes from a non-holder.

## Test Signals
Semaphore selftests should cover count > 1, interruptible/killable wait interruption, timeout, `up()` from interrupt context, FIFO wake behavior, hung-task holder reporting, and conversion tests that catch inverted trylock handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/semaphore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/spinlock.c -->
# sources/distributed-fs/ceph-client/kernel/locking/spinlock.c

## Purpose
Provides out-of-line raw spinlock and raw rwlock API functions for SMP/debug builds, plus generic lock-break spinning variants when configured. These wrappers connect architecture raw lock primitives with preemption/interrupt state, lockdep annotations, exports, and profiling boundaries.

## Important APIs, Types, and Functions
- Exports raw spin APIs such as `_raw_spin_trylock()`, `_raw_spin_lock()`, `_raw_spin_lock_irqsave()`, `_raw_spin_unlock_irqrestore()`, and `_raw_spin_lock_nested()`.
- Non-RT exports raw rwlock APIs such as `_raw_read_lock()`, `_raw_write_lock()`, `_raw_write_lock_nested()`, and their irq/bh/unlock variants.
- `BUILD_LOCK_OPS()` generates preemption-friendly lock-break loops when generic lockbreak is enabled without debug lock allocation.
- `in_lock_functions()` reports whether an address lies in lock text.
- `lockdep_assert_in_softirq_func()` is exported for PREEMPT_RT prove-locking builds.

## Control Flow
Most functions are thin noinline wrappers around inline `__raw_*` operations unless the config inlines them elsewhere. Under generic lockbreak, generated loops disable preemption, try the raw lock, re-enable preemption on failure, and relax toward the owner before retrying. IRQ and BH variants preserve interrupt/softirq state around those lock attempts. Debug lock allocation variants perform explicit lockdep acquire before contended raw spin acquisition.

## State and Persistence
No lock state is owned here except optional per-CPU `__mmiowb_state`. The functions mutate caller-supplied raw spin/rwlocks and CPU interrupt/preemption state.

## Dependencies and Integration Points
Depends on architecture raw lock operations, preemption, interrupt APIs, lockdep, debug locks, MMIO write barriers, and exported kernel symbol users. Raw rwlock wrappers are omitted under PREEMPT_RT because RT rwlocks are implemented elsewhere.

## Risks
Changing stack frames can affect architecture profiling. IRQ/BH/preemption ordering must remain exact or lockdep and interrupt masking semantics break. Generic lockbreak trades fairness and preemptibility against raw spin behavior and must not be used where lockdep assumes interrupts remain disabled through acquire.

## Test Signals
Build matrix for inline/non-inline, generic lockbreak, debug lock allocation, PREEMPT_RT, and MMIOWB. Runtime signals include lockdep reports, interrupt state assertions, profiling `in_lock_functions()`, and raw spin/rwlock torture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/spinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/spinlock_debug.c -->
# sources/distributed-fs/ceph-client/kernel/locking/spinlock_debug.c

## Purpose
Implements DEBUG_SPINLOCK validation for raw spinlocks and, on non-PREEMPT_RT, raw rwlocks. It initializes debug metadata, checks magic/owner/CPU recursion, records owners, and emits emergency diagnostics on misuse.

## Important APIs, Types, and Functions
- Exports `__raw_spin_lock_init()` and, non-RT, `__rwlock_init()`.
- Spin debug helpers: `spin_dump()`, `spin_bug()`, `debug_spin_lock_before()`, `debug_spin_lock_after()`, and `debug_spin_unlock()`.
- Raw spin operations: `do_raw_spin_lock()`, `do_raw_spin_trylock()`, and `do_raw_spin_unlock()`.
- Non-RT rwlock operations: `do_raw_read_lock()`, `do_raw_read_trylock()`, `do_raw_read_unlock()`, `do_raw_write_lock()`, `do_raw_write_trylock()`, and `do_raw_write_unlock()`.

## Control Flow
Initialization sets lockdep maps when enabled, raw architecture lock state, magic value, owner sentinel, and owner CPU. Lock operations validate magic and recursion before acquiring the architecture lock, then record current task and CPU. Unlock validates lock state, owner task, and owner CPU, clears owner metadata, and releases the architecture lock. Trylock records ownership only on success and asserts UP trylock failures as impossible.

## State and Persistence
Debug fields live inside raw spinlock/rwlock structures: magic, owner, and owner CPU. No persistence beyond live kernel objects.

## Dependencies and Integration Points
Depends on architecture spin/rwlock primitives, debug locks, lockdep, NMI/delay support, PID/task info for diagnostics, MMIO write-barrier hooks for spinlocks, and exported debug lock initialization APIs.

## Risks
Diagnostics call `debug_locks_off()` to avoid repeated reports; after the first serious failure, later issues may be suppressed. Owner checks are meaningful only for exclusive spin/write locks, not read locks. PREEMPT_RT excludes raw rwlock debug implementation here.

## Test Signals
Enable DEBUG_SPINLOCK and intentionally exercise bad magic, recursion, wrong owner, wrong CPU, double unlock, and UP trylock behavior. Expected signals are emergency printk reports, stack dumps, and lockdep map initialization checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/spinlock_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/spinlock_rt.c -->
# sources/distributed-fs/ceph-client/kernel/locking/spinlock_rt.c

## Purpose
Provides PREEMPT_RT substitutions for regular spinlocks and rwlocks. Instead of raw busy-waiting, these locks are backed by rtmutexes, preserve task state while blocking, disable migration, and hold RCU read-side state to approximate non-RT spinlock semantics.

## Important APIs, Types, and Functions
- Spinlock exports: `rt_spin_lock()`, `rt_spin_lock_nested()`, `rt_spin_lock_nest_lock()`, `rt_spin_unlock()`, `rt_spin_lock_unlock()`, `rt_spin_trylock()`, `rt_spin_trylock_bh()`, and `__rt_spin_lock_init()`.
- Rwlock exports: `rt_read_lock()`, `rt_read_trylock()`, `rt_read_unlock()`, `rt_write_lock()`, `rt_write_lock_nested()`, `rt_write_trylock()`, `rt_write_unlock()`, and `__rt_rwlock_init()`.
- Internal helpers include `rtlock_lock()`, `__rt_spin_lock()`, `__rt_spin_trylock()`, and macro adapters for `rwbase_rt.c`.

## Control Flow
Spin lock acquisition checks reschedule rules, acquires lockdep, tries rtmutex owner cmpxchg, and falls back to `rtlock_slowlock()`. On success it enters RCU read-side and disables migration. Unlock releases lockdep, enables migration, exits RCU, and release-cmpxchg's the rtmutex or slow-unlocks. Rwlocks use `rwbase_rt.c`: reads and writes acquire through the rwbase reader/writer protocol, then enter RCU and disable migration; unlock reverses those state changes and releases the rwbase lock.

## State and Persistence
State is in the lock's embedded `rt_mutex_base` or `rwbase_rt`, lockdep map, task saved wait state, migration disable count, and RCU nesting. No persistent storage.

## Dependencies and Integration Points
Depends on `rtmutex.c` with `RT_MUTEX_BUILD_SPINLOCKS`, `rwbase_rt.c`, lockdep, RCU preempt depth, migration control, softirq controls for `_bh`, and PREEMPT_RT scheduler helpers such as `schedule_rtlock()`.

## Risks
These locks may sleep, so code assuming non-RT spinlocks are always atomic must use raw spinlocks where required. Correct preservation/restoration of task state prevents missed wakeups while blocked on rtlocks. RCU and migration ordering differs subtly between read and write unlock paths and must preserve non-RT semantics.

## Test Signals
PREEMPT_RT lock torture, sleep-in-spinlock audits, lockdep nesting tests, `rt_spin_trylock_bh()` softirq state tests, migration/RCU nesting assertions, rtlock contention traces, and rwlock reader/writer starvation stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/spinlock_rt.c -->
