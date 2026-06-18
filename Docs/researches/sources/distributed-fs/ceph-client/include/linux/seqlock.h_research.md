# sources/distributed-fs/ceph-client/include/linux/seqlock.h

Purpose: `seqlock.h` implements sequence counters and seqlocks: concurrency primitives optimized for lockless readers that retry when writers update protected data. It also provides associated-lock seqcount variants, latch seqcounts for NMI-safe double-buffering, seqlock writer/reader APIs, and scoped read helpers.

Important APIs/types/functions: Core APIs include `seqcount_init()`, `SEQCNT_ZERO()`, associated lock initializers (`seqcount_spinlock_init()` etc.), `read_seqcount_begin()`, `read_seqcount_retry()`, raw read variants, `write_seqcount_begin/end()`, raw write variants, `raw_write_seqcount_barrier()`, `write_seqcount_invalidate()`, latch APIs (`seqcount_latch_init()`, `read_seqcount_latch()`, `write_seqcount_latch_begin/write/end()`), `seqlock_init()`, `DEFINE_SEQLOCK()`, `read_seqbegin()`, `read_seqretry()`, write seqlock variants, exclusive read-lock variants, `read_seqbegin_or_lock()`, `need_seqretry()`, `done_seqretry()`, IRQ-save variants, and `scoped_seqlock_read()`.

Control flow: Lockless readers sample an even sequence, read protected fields, then retry if the sequence changed. Writers increment to odd, apply updates with ordering barriers, then increment to even. Associated-lock seqcounts assert or use lock state for writer serialization; on PREEMPT_RT, readers of preemptible associated locks may briefly take/release the writer lock to let preempted writers complete. Seqlocks embed a spinlock and sequence counter for automatic writer serialization.

State and persistence behavior: State is the sequence counter value, optional associated lock pointer, and embedded seqlock spinlock. Odd sequence means a writer is active; even sequence means stable. Latch seqcounts use the low bit to select one of two copies while writers update the inactive copy.

Dependencies and integration points: It depends on compiler annotations, cleanup attributes, KCSAN, lockdep, mutex/spinlock APIs, preemption control, barriers, and processor relax. It is used by timekeeping, networking, VFS, and other read-mostly data paths.

Risks: Protected data must not contain pointers whose lifetime can disappear under lockless readers. Plain seqcount writers must be externally serialized and non-preemptible; interrupt/BH disabling is required when readers can run there. Missing retry loops or barriers produce torn reads. PREEMPT_RT behavior changes writer/reader progress assumptions.

Test signals: Lockless reader retry loops, writer serialization lockdep assertions, PREEMPT_RT builds, KCSAN instrumentation, IRQ/BH writer variants, latch double-buffer correctness under NMI-like reads, raw barrier users, scoped read helper codegen, and pointer-lifetime misuse review.
