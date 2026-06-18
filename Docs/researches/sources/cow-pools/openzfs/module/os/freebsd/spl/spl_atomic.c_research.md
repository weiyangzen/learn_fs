# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/spl_atomic.c

Fallback 64-bit atomic implementation for FreeBSD targets without native 64-bit atomic operations.

When enabled by architecture feature checks, it provides mutex-protected:
- `atomic_add_64()`
- `atomic_dec_64()`
- `atomic_swap_64()`
- `atomic_load_64()`
- `atomic_add_64_nv()`
- `atomic_cas_64()`

Kernel builds use `MTX_SYSINIT`; non-kernel builds use a constructor-initialized `pthread_mutex_t`.
