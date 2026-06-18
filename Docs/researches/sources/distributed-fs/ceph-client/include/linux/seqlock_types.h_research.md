# sources/distributed-fs/ceph-client/include/linux/seqlock_types.h

Purpose: `seqlock_types.h` contains the type definitions for sequence counters, associated-lock sequence counters, and `seqlock_t` without exposing the full API body.

Important APIs/types/functions: It defines `seqcount_t`, `seqcount_raw_spinlock_t`, `seqcount_spinlock_t`, `seqcount_rwlock_t`, `seqcount_mutex_t`, and `seqlock_t`. The `SEQCOUNT_LOCKNAME()` macro generates associated-lock structures with optional lock pointers under lockdep or PREEMPT_RT. `seqlock_t` contains a `seqcount_spinlock_t` and `spinlock_t`.

Control flow: No functions execute here. The generated type layout enables API macros in `seqlock.h` to associate counters with serialization locks and to support PREEMPT_RT reader progress.

State and persistence behavior: `seqcount_t` stores the sequence value and optional lockdep map. Associated variants store the actual `seqcount_t` plus optional lock pointer. `seqlock_t` embeds both sequence counter and spinlock for persistent synchronization state.

Dependencies and integration points: It depends on lockdep, mutex, and spinlock type headers. It integrates with the main seqlock API and with object definitions that need seqlock fields without all inline helpers.

Risks: Conditional `__SEQ_LOCK()` layout means structure size changes with lockdep/PREEMPT_RT. Writers must still follow the contracts documented in comments: serialization, non-preemptibility, and avoiding pointer-protected data for lockless readers.

Test signals: Compile structure users under lockdep, PREEMPT_RT, and minimal configs; static initializers; associated-lock pointer initialization; and ABI-sensitive embedded structure layout review.
