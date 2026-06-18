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
