# sources/distributed-fs/ceph-client/lib/zstd/common/zstd_common.c

## Purpose
`zstd_common.c` exports the common version and error-management entry points for the kernel Zstd library. It is intentionally small and wraps constants/macros from the public Linux Zstd header and the private error subsystem.

## Important Functions
`ZSTD_versionNumber()` returns `ZSTD_VERSION_NUMBER`; `ZSTD_versionString()` returns `ZSTD_VERSION_STRING`; `ZSTD_isError()` wraps `ERR_isError()` after undefining the inline alias from `zstd_internal.h`; `ZSTD_getErrorName()`, `ZSTD_getErrorCode()`, and `ZSTD_getErrorString()` expose private error names and enum conversion to external callers.

## Control Flow and State
There is no mutable state or persistence. Every function is a direct, deterministic accessor or wrapper. The only notable control-flow detail is that `ZSTD_DEPS_NEED_MALLOC` is defined before including common headers, but this kernel dependency layer maps malloc/calloc to always fail, keeping this common module free of dynamic allocation.

## Dependencies and Integration Points
The file includes `error_private.h` and `zstd_internal.h`, which pulls in `<linux/zstd.h>` and shared Zstd constants. These functions are exported ABI-like helpers for compression/decompression callers that need to identify error-coded `size_t` results.

## Risks and Test Signals
Risks are low but ABI-visible: version constants must match the bundled implementation, and error wrappers must not conflict with macro aliases. Tests should verify that known error codes are detected, names are stable/non-null, enum conversion is consistent, and the reported version matches the Linux Zstd header compiled with this source.
