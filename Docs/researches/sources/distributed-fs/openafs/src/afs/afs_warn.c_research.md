# sources/distributed-fs/openafs/src/afs/afs_warn.c

Purpose: central warning output helpers for the cache manager. It gates console and user-visible warnings through `afs_showflags`, abstracts platform print APIs, and emits a specific cache-partition-full warning.

Important APIs: `afs_warn`, `afs_warnuser`, `afs_warnall`, and `afs_WarnENOSPC`. Platform-specific internals include `afs_vprintf`, `afs_vwarn`, and `afs_vwarnuser`; AIX uses old-style varargs and explicit `/dev/console` writes via `fp_open`/`fp_write`.

Control flow: `afs_warn` emits only when `GAGCONSOLE` is set. `afs_warnuser` emits only when `GAGUSER` is set and may drop/reacquire the AFS global lock around user printf paths. `afs_warnall` avoids duplicate Linux output because console and user paths converge there. The Mariner variant logs a `warn$` record before printing.

State and persistence: no persistent state. Runtime behavior depends on `afs_showflags`, `afs_mariner`, and global lock state. `AFS_STATCNT` records call counts.

Dependencies and integration points: used across cache/volume/vcache code for operational warnings. It depends on platform kernel printf facilities, `afsincludes.h`, and stats macros. `afs_WarnENOSPC` is a higher-level signal for cache partition exhaustion.

Risks: format-string handling is kernel-side; callers must pass trusted format strings and matching arguments. Lock transitions around user output are platform-sensitive. The Darwin 8 inline path calls `printf(buf)`, so any accidental `%` generated into `buf` would be unsafe if the buffer content were not purely formatted from a trusted format string.

Test signals: verify console-only, user-only, both, and neither flag combinations; Linux duplicate suppression; AIX console path failure tolerance; Mariner logging; global-lock drop/reacquire balance; and that ENOSPC warning is user-visible.
