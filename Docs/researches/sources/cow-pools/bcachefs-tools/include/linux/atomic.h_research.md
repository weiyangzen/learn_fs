# File Research: sources/cow-pools/bcachefs-tools/include/linux/atomic.h

Purpose: userspace implementation of Linux atomic types and operations using compiler `__atomic` builtins.

Key contents:
- Defines `atomic_t`, `atomic_long_t`, and `atomic64_t`.
- Provides low-level atomic read/set/add/sub/and/or/exchange/cmpxchg macros.
- Provides memory barrier macros and acquire/release helpers.
- `DEF_ATOMIC_OPS()` generates the standard Linux atomic API for `atomic` and `atomic_long`, and usually `atomic64`.
- Includes fallback declarations for `ATOMIC64_SPINLOCK` platforms.

Important interactions:
- Core shim for code that expects Linux atomic APIs.
- Memory ordering is conservative in places: several SMP barriers map to sequentially consistent fences.
