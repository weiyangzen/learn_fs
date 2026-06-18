## sources/distributed-fs/ceph-client/include/linux/completion.h

Purpose: This header declares the kernel completion synchronization primitive: a one-shot or reusable event object used to block tasks until another context signals completion.

Important APIs, types, and functions: `struct completion` contains a `done` counter and an `swait_queue_head`. Initializers include `COMPLETION_INITIALIZER`, `DECLARE_COMPLETION`, `DECLARE_COMPLETION_ONSTACK`, and lockdep-aware map variants. `init_completion()` initializes dynamically allocated completions, and `reinit_completion()` resets only `done` for reuse. Wait APIs include `wait_for_completion`, `_io`, `_interruptible`, `_killable`, `_state`, timeout variants, `try_wait_for_completion`, and `completion_done`. Signal APIs include `complete`, `complete_on_current_cpu`, and `complete_all`.

Control flow: Waiters enqueue on the simple wait queue when `done` is zero. Signallers increment or saturate `done` and wake waiters. `complete_all()` wakes all waiters and leaves the object in a completed state until `reinit_completion()` resets it. On-stack completion macros use runtime initialization under lockdep.

State and persistence: Completion state is entirely in `done` and the wait queue. It is in-memory synchronization state and is not persistent across object lifetime. Reinitialization intentionally keeps the wait queue intact, so it must not be used while unknown waiters remain.

Dependencies and integration points: It depends on `linux/swait.h`, scheduler wait/wake implementation, lockdep annotations, and callers throughout drivers, filesystems, and async kernel flows.

Risks and test signals: Risks include reinitializing while waiters are active, missing `complete()` on error paths, assuming `completion_done()` is a strong synchronization check, and using a normal initializer for stack objects under lockdep. Test signals are timeout tests, interruptible wait tests, `complete_all()` reuse tests, lockdep runs, and teardown paths that verify no blocked waiters remain.
