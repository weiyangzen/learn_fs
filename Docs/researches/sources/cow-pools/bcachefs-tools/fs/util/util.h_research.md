# File Research: sources/cow-pools/bcachefs-tools/fs/util/util.h

Purpose: Broad utility header for kernel/userspace portability, allocation, printing, parsing, bio helpers, and low-level macros.

Key APIs and behavior:
- Provides debug `EBUG_ON`, endian detection, type compatibility macros, kernel-version shims, and allocation helpers.
- Re-exports printbuf APIs under shorter names.
- Declares human-readable string parsers, print helpers, backtrace helpers, time-stat renderers, rate limiter, and PD controller APIs.
- Defines list, array, gap-buffer, sort, percpu, qstr, bit, flag-mapping, and error-propagation helpers.
- Declares bio helpers and kthread wait macros.
- Provides u64 copy/move helpers that intentionally bypass some fortify limitations for array-like storage.
- Defines memalloc guard class and wait-bit IO timeout wrapper.

Integration:
- Included by many utility and VFS files.
- Depends on closure, darray, printbuf, mean_and_variance, and time_stats.

Risks and invariants:
- Many helpers are macros with side effects and type assumptions.
- Some compatibility shims are kernel-version-sensitive.
- Low-level memory helpers expect caller-provided object-size correctness.
