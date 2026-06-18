# File Research: sources/cow-pools/bcachefs-tools/linux/atomic64.c

Generic spinlock-backed 64-bit atomic implementation compiled when `ATOMIC64_SPINLOCK` is set. It hashes atomic variable addresses to one of 16 cacheline-padded raw spinlocks and implements read/set, arithmetic/bitwise ops, fetch ops, cmpxchg, try-cmpxchg, xchg, dec-if-positive, and add-unless.

This fallback matters on platforms lacking native 64-bit atomics.
