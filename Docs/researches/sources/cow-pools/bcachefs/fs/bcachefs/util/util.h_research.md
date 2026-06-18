# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/util.h

## Summary
Declares and defines bcachefs’ general utility interface, including compatibility shims, print helpers, parsing helpers, rate-control structures, bio helpers, kthread wait macros, memory movement helpers, array helpers, percpu helpers, bit helpers, error-propagation macros, memalloc guard classes, mempool shims, wait-bit timeout helpers, and percpu initialization support.

## Main Contents
- Debug macro `EBUG_ON()`.
- Endianness and type-detection macros.
- Kernel-version compatibility helpers such as `bio_inline_vecs()` and `bdev_rot()`.
- `bch2_kvmalloc()` wrapper.
- Printbuf aliases and UUID/date/time print helpers.
- Human-readable integer parsing declarations.
- Stacktrace darray type and backtrace APIs.
- `struct bch_ratelimit` and `struct bch_pd_controller`.
- Sysfs helper macros for PD controller fields.
- Bio mapping/submission/copy/debug APIs.
- `kthread_wait()` and `kthread_wait_freezable()`.
- u64-specialized memcpy/memmove helpers.
- array insertion/removal and gap-buffer helpers.
- percpu sum/set/accumulate helpers.
- little-endian bit helpers.
- flag mapping macros.
- `try()` and `errptr_try()`.
- scoped `memalloc_flags` guard.
- `wait_on_bit_io_timeout()`.
- `bch2_alloc_percpu_init()`.

## Important Behavior
Many functions are inline for hot paths, including memory movement and percpu helpers. On x86-64, u64 copy/move helpers use `rep movsq` assembly when KMSAN is not enabled. `try()` returns immediately on nonzero errors, creating a compact error-propagation idiom used throughout bcachefs.

## Risks
This header is a wide dependency surface. Macro helpers can evaluate arguments in non-obvious contexts, and some helpers assume alignment, non-overlap direction, or external synchronization. Version shims and userspace/kernel conditional paths must be kept synchronized with supported build targets.
