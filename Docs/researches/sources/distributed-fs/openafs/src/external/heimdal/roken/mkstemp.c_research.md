# sources/distributed-fs/openafs/src/external/heimdal/roken/mkstemp.c

## Purpose
Provides a roken fallback implementation of `mkstemp` when the platform C library does not provide one. It turns trailing `X` characters in a caller-supplied template into a process-id-derived suffix and repeatedly attempts an exclusive create until it gets a unique temporary file.

## Important APIs, Types, And Functions
The only exported function is `mkstemp(char *template)`, compiled under `#ifndef HAVE_MKSTEMP` and exposed through `roken.h` as `rk_mkstemp` on platforms missing the native function. It uses `getpid`, `strlen`, `open`, `O_RDWR | O_CREAT | O_EXCL`, mode `0600`, and `errno == EEXIST`.

## Control Flow
The implementation walks backward over trailing `X` characters, replacing them with decimal digits from the process id. It then tries `open`. On any success, or any failure other than name collision, it returns the file descriptor or `-1`. For `EEXIST`, it increments the generated suffix through digits and lowercase letters, carrying forward until a new candidate exists or the generated string is exhausted.

## State And Persistence
The caller's template buffer is modified in place and the created file persists on disk. There is no module global state. The created file descriptor is returned open and must be closed by the caller.

## Dependencies And Integration Points
This is part of Heimdal roken portability support vendored into OpenAFS. It is selected by configure-time feature detection and consumed by code including `roken.h`.

## Risks And Test Signals
The name space is weak compared with modern `mkstemp` implementations because it starts with process-id digits and then performs predictable increments. It assumes a valid template with trailing `X` characters and can underflow if misused. Useful tests cover collision retry, file mode `0600`, in-place template update, no-overwrite behavior, and native-vs-fallback configure builds.
