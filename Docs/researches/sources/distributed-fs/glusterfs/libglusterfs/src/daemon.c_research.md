# sources/distributed-fs/glusterfs/libglusterfs/src/daemon.c

## Purpose
This file implements GlusterFS daemonization helpers. It is a small wrapper around fork/session detachment, optional `chdir("/")`, and optional standard stream redirection to `/dev/null`.

## Important APIs, types, and functions
`os_daemon_return(int nochdir, int noclose)` forks and returns the fork result to the parent while completing daemon setup in the child. `os_daemon(int nochdir, int noclose)` calls that helper and exits the parent with `_exit(0)` when fork succeeded.

## Control flow
`os_daemon_return()` calls `fork()`. The parent receives the child PID and returns it. The child calls `setsid()`, optionally changes directory to root, and optionally reopens stdin, stdout, and stderr to `DEVNULLPATH`. `os_daemon()` converts the positive parent return into process exit, leaving only the child to continue with return 0 or -1.

## State and persistence behavior
The file changes process state: parent/child split, session leadership, current working directory, and standard file descriptors. It writes no persistent data and allocates no heap state.

## Dependencies and integration points
It includes `glusterfs/daemon.h` for `DEVNULLPATH` and public declarations. Startup code uses these helpers to detach long-running daemons while preserving the option to keep cwd or standard streams for foreground/debug modes.

## Risks and edge cases
The implementation performs a single fork, not the classic double-fork pattern, so the child remains a session leader and could acquire a controlling terminal later. If `chdir("/")` fails, execution continues unless later stream reopening fails; the return code can be overwritten by subsequent success. `freopen()` failure returns -1 but may leave some streams already redirected.

## Test signals
Tests should cover parent return of child PID, child return 0, `nochdir` preserving cwd, `noclose` preserving streams, failure injection for `fork`, `setsid`, `chdir`, and each `freopen`, plus integration startup tests that verify foreground mode does not daemonize.
