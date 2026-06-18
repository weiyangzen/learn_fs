# sources/distributed-fs/openafs/src/external/heimdal/roken/strlcat.c

## Purpose
Provides a fallback `strlcat` implementation for platforms missing the BSD function.

## Important APIs, Types, And Functions
The exported function is `strlcat(char *dst, const char *src, size_t dst_sz)`, mapped to `rk_strlcat` by `roken.h` when needed. It uses `strnlen_s`, `strnlen`, or `strlen` depending on platform support.

## Control Flow
The function computes the existing destination length bounded by `dst_sz` when possible. If the destination buffer is already full or malformed relative to the supplied size, it returns `len + strlen(src)` without writing. Otherwise it appends via `strlcpy(dst + len, src, dst_sz - len)` and returns the total length it tried to create.

## State And Persistence
The destination buffer may be modified and NUL-terminated if space allows. No global state exists.

## Dependencies And Integration Points
Used by roken and downstream code as a safer concatenation primitive in missing-feature builds.

## Risks And Test Signals
When no bounded `strnlen` exists, the fallback `strlen(dst)` can read past `dst_sz` for unterminated input. Tests should cover empty/full buffers, truncation return values, one-byte buffers, unterminated destination under supported bounded builds, and native-vs-fallback macro mapping.
