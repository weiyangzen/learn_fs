# sources/distributed-fs/openafs/src/external/heimdal/roken/strerror_r.c

## Purpose
Normalizes `strerror_r` behavior behind `rk_strerror_r` when the platform lacks a compatible POSIX-style prototype or provides the GNU string-returning variant.

## Important APIs, Types, And Functions
The exported function is `rk_strerror_r(int eno, char *strerrbuf, size_t buflen)`. MSVC uses `strerror_s`; other builds either wrap native `strerror_r` or copy `strerror(eno)` with `strlcpy`.

## Control Flow
MSVC writes into the caller buffer and, on failure, attempts a generic formatted message. GNU-style fallback calls `strerror_r`, and if the returned pointer differs from the supplied buffer, copies that string into the buffer and reports `ERANGE` on truncation. No-native fallback copies from `strerror`.

## State And Persistence
Only the caller's buffer is mutated. No module state is retained.

## Dependencies And Integration Points
`roken.h.in` either defines `rk_strerror_r` as native `strerror_r` or declares this function, letting callers use a consistent integer return interface.

## Risks And Test Signals
The MSVC fallback format string appears suspicious (`"Error % occurred."` lacks a numeric conversion), so error-path coverage matters. The non-native branch compares `strlcpy` return with `buflen` and should be tested for exact truncation. Signals include known errno messages, too-small buffers, GNU and POSIX libc variants, and invalid error numbers.
