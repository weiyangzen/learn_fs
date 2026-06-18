# sources/distributed-fs/openafs/src/external/heimdal/roken/flock.c

Purpose: provides a portable `flock()`-style advisory locking fallback as `rk_flock()` when the system lacks native `flock`.

Important APIs/types/functions: `rk_flock(int fd, int operation)` supports `LOCK_SH`, `LOCK_EX`, `LOCK_UN`, and `LOCK_NB`.

Control flow: on POSIX with `fcntl`, builds a whole-file `struct flock`, chooses blocking or nonblocking command, maps lock operations to read/write/unlock locks, and calls `fcntl()`. On Windows, maps the fd to a HANDLE and uses `LockFileEx()`/`UnlockFileEx()` with whole-file ranges and errno translation. Otherwise returns -1.

State and persistence behavior: mutates OS advisory lock state for the file description or handle. No heap state.

Dependencies and integration points: roken compatibility for code expecting BSD-style file locking across Unix and Windows.

Risks: `fcntl` locks and BSD `flock` locks have different semantics around process ownership and descriptor inheritance. Windows error mapping is approximate. Unsupported fallback returns -1 without setting a specific errno in the final branch.

Test signals: shared/exclusive/unlock behavior, nonblocking conflict errors, invalid operation EINVAL, and Windows errno translation if applicable.
