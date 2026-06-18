# sources/distributed-fs/openafs/src/util/hputil.c

Purpose: Supplies missing compatibility routines for HP-UX builds.

Important APIs: Under `AFS_HPUX_ENV`, defines `utimes()` for pre-HPUX 10.20 using `utime()`, `setlinebuf()` using `setbuf(file, NULL)`, and `psignal()` that prints a simple signal message to stderr.

Control flow and state: No persistent state. Each helper is a thin wrapper around the available libc API.

Dependencies and integration: Includes `<utime.h>` when compiling for HP-UX and OpenAFS platform config headers. These functions allow common code to compile without platform-specific call-site branches.

Risks and test signals: The `utimes()` shim loses microsecond precision because `utime()` only preserves seconds. `psignal()` does not translate signal names. Build coverage on HP-UX is the main signal; there are no local tests.
