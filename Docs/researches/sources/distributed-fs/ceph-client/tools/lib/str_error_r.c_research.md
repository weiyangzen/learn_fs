# sources/distributed-fs/ceph-client/tools/lib/str_error_r.c

Purpose: Provides `str_error_r()`, a portable wrapper with GNU-like return semantics that always returns the caller-provided buffer while using XSI `strerror_r()`.

Important APIs/types/functions: `char *str_error_r(int errnum, char *buf, size_t buflen)` calls `strerror_r()`, formats an internal-error message into `buf` if it fails, and returns `buf`.

Control flow: Undefines `_GNU_SOURCE` before including string headers to force XSI behavior. On success, the platform fills `buf`; on nonzero return, `snprintf()` writes a diagnostic.

State and persistence: Stateless; caller owns the buffer.

Dependencies/integration: Includes libc `string.h`, `stdio.h`, and `<linux/string.h>`. Used by tools code expecting GNU `strerror_r()`-style string return while remaining compatible with musl and other libc implementations.

Risks: If the build environment still exposes GNU semantics despite `_GNU_SOURCE` handling, the return type expectations can conflict. Very small buffers truncate diagnostics. Passing a null buffer or zero length is caller error.

Test signals: Build and run on glibc and musl, test known/unknown errno values, tiny buffer sizes, and callers that immediately print the returned pointer.
