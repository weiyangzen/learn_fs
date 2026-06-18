# sources/distributed-fs/openafs/src/external/heimdal/roken/strnlen.c

## Purpose
Implements `strnlen` for platforms lacking it: bounded measurement of a NUL-terminated string.

## Important APIs, Types, And Functions
The single exported function is `strnlen(const char *s, size_t len)`, usually macro-mapped to `rk_strnlen` by `roken.h`.

## Control Flow
The function increments an index until either `len` bytes have been inspected or `s[i]` is NUL, then returns the count.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
Used directly or indirectly by safer string helpers such as `strlcat` when native `strnlen` is unavailable.

## Risks And Test Signals
The caller must pass a valid pointer to at least `len` readable bytes. Tests should cover NUL before limit, no NUL within limit, zero length, and macro mapping in missing-feature builds.
