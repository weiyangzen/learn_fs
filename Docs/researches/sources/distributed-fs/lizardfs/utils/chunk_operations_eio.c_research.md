# sources/distributed-fs/lizardfs/utils/chunk_operations_eio.c

Purpose: LD_PRELOAD-style fault injection library for chunk file I/O. It overrides `pread`, `pwrite`, `close`, and `fsync` and returns `-1/EIO` for selected file names, letting integration tests verify chunkserver behavior under I/O errors.

Important APIs/functions: `read_filename()` resolves an fd through `/proc/self/fd/<fd>`. `err_on_operation()` checks that the path contains `/chunk_`, then looks for operation-specific substrings such as `pread_EIO`, `pwrite_EIO`, `close_EIO`, `fsync_EIO`, or far-offset variants such as `pread_far_EIO`. The overridden libc symbols lazily resolve the real function with `dlsym(RTLD_NEXT, ...)`.

Control flow: every intercepted call first derives the filename. Non-chunk paths pass through unchanged. Matching chunk paths fail immediately when the always-fail token is present. For `pread` and `pwrite`, the `*_far_EIO` token only triggers when `offset > 102400`; `close` and `fsync` pass offset zero to the same helper.

State and persistence: no persistent state is written. Process-local static function pointers cache libc symbol lookups. Behavior is encoded entirely in the current fd target path, so renames or symlinks affect matching through `/proc/self/fd`.

Dependencies/integration: depends on glibc dynamic linking, `_GNU_SOURCE`, `/proc`, and POSIX file APIs. It is intended for test process environments via `LD_PRELOAD`.

Risks and test signals: `sprintf` into fixed 1024-byte buffers can truncate/overflow if unexpected fd strings or names are used, and `close` failure injection can leak descriptors in tests unless callers handle it. Concurrency is acceptable for static pointer initialization in normal tests but not formally synchronized. Test signals are successful pass-through for non-chunk files, exact EIO/error propagation for each trigger, far-offset threshold boundaries, and preserving original function behavior when no trigger matches.
