# sources/distributed-fs/ceph-client/include/asm-generic/bitops/ext2-atomic.h

Purpose: Provides spinlock-based ext2 atomic little-endian bitmap set/clear helpers for architectures that do not use direct atomic LE operations.

Important APIs, types, and functions: Defines `ext2_set_bit_atomic(lock, nr, addr)` and `ext2_clear_bit_atomic(lock, nr, addr)` using `spin_lock()`, `__test_and_set_bit_le()`/`__test_and_clear_bit_le()`, and `spin_unlock()`.

Control flow: Acquires the provided spinlock, performs a non-atomic little-endian test-and-update, releases the lock, and returns the prior bit value.

State and persistence: Mutates caller filesystem bitmaps that become persistent through filesystem writeback.

Dependencies and integration points: Depends on spinlocks and little-endian non-atomic bitops. Used by ext2 allocation/free code on generic architectures.

Risks and test signals: Risks include callers passing the wrong lock, deadlocks from lock ordering, and bitmap corruption if mixed with lockless updates. Test concurrent ext2 allocation/free, lockdep, big-endian bitmap behavior, and fsck after stress.
