# File Research: sources/cow-pools/bcachefs-tools/include/linux/bit_spinlock.h

Purpose: userspace bit spinlock implementation using atomic bit operations plus futex wait/wake.

Key contents:
- `do_futex()` maps a bit number within an `unsigned long` bitmap to the correct 32-bit futex word, handling 64-bit endian layout.
- `bit_spin_lock()` atomically sets the target bit with acquire semantics and waits with futex while contended.
- `bit_spin_unlock()` clears the bit with release semantics and wakes waiters.
- `bit_spin_wake()` wakes waiters without unlocking.

Important interactions:
- Provides blocking bit-lock semantics for userspace code ported from Linux.
- Depends on futex headers and userspace RCU futex support.
