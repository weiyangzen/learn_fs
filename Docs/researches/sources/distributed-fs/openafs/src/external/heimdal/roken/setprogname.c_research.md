# sources/distributed-fs/openafs/src/external/heimdal/roken/setprogname.c

## Purpose
Implements `setprogname` on platforms without it, setting the global program-name used by roken warning/error helpers.

## Important APIs, Types, And Functions
The exported function is `setprogname(const char *argv0)`. When native `__progname` is absent, it assigns the basename of `argv0` to the external `__progname`.

## Control Flow
The function ignores `NULL`, finds the final slash, optionally handles backslash path delimiters, then stores the basename. On Windows it duplicates the basename, lowercases it, and strips a `.exe` suffix. On Unix it points `__progname` into the original `argv0` string.

## State And Persistence
The persistent state is the process-global `__progname` pointer. Windows builds allocate memory for the stored program name and do not free it.

## Dependencies And Integration Points
`warnerr.c` and err/warn wrappers call `getprogname`, which depends on this state when the platform lacks native support. `roken.h.in` maps `setprogname` to `rk_setprogname` when needed.

## Risks And Test Signals
On Unix, the stored pointer has the lifetime of `argv0`; callers should pass stable storage. Windows retains allocated memory. Tests should cover slash and backslash paths, `.exe` stripping, case normalization, `NULL`, and warning output prefixes.
