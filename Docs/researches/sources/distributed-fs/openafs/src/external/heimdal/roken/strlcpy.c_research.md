# sources/distributed-fs/openafs/src/external/heimdal/roken/strlcpy.c

## Purpose
Provides a fallback `strlcpy` implementation for platforms missing the BSD function.

## Important APIs, Types, And Functions
The exported function is `strlcpy(char *dst, const char *src, size_t dst_sz)`, mapped to `rk_strlcpy` as needed. MSVC 2005+ uses `strncpy_s(..., _TRUNCATE)` and still returns `strlen(src)`.

## Control Flow
The generic implementation copies up to `dst_sz` bytes, stopping at NUL. If the destination fills before the source ends, it forces the last byte to NUL when possible and returns the number of bytes copied plus the remaining source length, matching the attempted source length.

## State And Persistence
The destination buffer is mutated. No global state is used.

## Dependencies And Integration Points
Many roken shims depend on `strlcpy` for bounded string copies, including `strerror_r`.

## Risks And Test Signals
The generic loop can call `strlen` on the post-copy source pointer, so source must be NUL-terminated. Tests should verify return values under no truncation, truncation, `dst_sz == 0`, single-byte destination, and MSVC secure CRT behavior.
