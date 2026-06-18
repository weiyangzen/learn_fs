# sources/distributed-fs/openafs/src/util/errmap_nt.c

Purpose: Provides a small Windows-to-POSIX error translation routine so NT platform code can report Unix-like `errno` values to the rest of OpenAFS.

Important APIs and state: Exports `nterr_nt2unix(long ntErr, int defaultErr)`. Also defines global `nterr_lastNTError`, intentionally useful in core dumps for older LWP-based binaries.

Control flow: The function stores the incoming NT error code in `nterr_lastNTError`, then maps selected Win32 errors to POSIX-style values: invalid parameters to `EINVAL`, missing files/paths/drives to `ENOENT`, access denial to `EACCES`, disk full to `ENOSPC`, memory failures to `ENOMEM`, pipe errors to `EPIPE`, sharing/pipe busy to `EBUSY`, and so on. Unknown errors return the caller-provided default.

Dependencies and integration: Includes `windows.h` and `afs/errmap_nt.h`. Used by Windows shims such as `readdir_nt.c` and other code needing stable cross-platform error semantics.

Risks and test signals: The mapping is intentionally incomplete; callers must choose a sensible `defaultErr`. `nterr_lastNTError` is global and unsynchronized, so it is diagnostic only in threaded code. There is no local unit test in this subset; Windows directory and socket error paths indirectly exercise it.
