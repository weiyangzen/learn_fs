# sources/distributed-fs/openafs/src/external/heimdal/roken/write_pid.c

## Purpose
Implements helpers for writing and deleting daemon pid files, plus a fallback `pidfile` interface.

## Important APIs, Types, And Functions
Exports `pid_file_write(const char *progname)`, `pid_file_delete(char **filename)`, and, when native `pidfile` is absent, `pidfile(const char *bname)`. Private fallback state is `static char *pidfile_path`; `pidfile_cleanup` deletes it at process exit.

## Control Flow
`pid_file_write` formats `_PATH_VARRUN + progname + ".pid"`, opens it for writing, writes the process id, closes it, and returns the allocated path. `pid_file_delete` unlinks and frees a stored path. `pidfile` writes once, defaults the basename from `getprogname`, and registers cleanup with `atexit` or `on_exit`.

## State And Persistence
The pid file persists on disk until cleanup or explicit deletion. The fallback stores one process-global pidfile path pointer.

## Dependencies And Integration Points
Declared through `roken-common.h` and mapped by `roken.h.in`. Used by daemon-style code needing portable pidfile behavior.

## Risks And Test Signals
There is no locking or stale-pid validation, and `_PATH_VARRUN` may not be writable. Tests should cover write/delete, cleanup registration, `NULL` basename behavior, unwritable directories, and duplicate `pidfile` calls.
