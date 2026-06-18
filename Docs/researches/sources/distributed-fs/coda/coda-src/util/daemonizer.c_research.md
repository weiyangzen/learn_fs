# sources/distributed-fs/coda/coda-src/util/daemonizer.c

## Purpose
Implements daemon startup helpers: double-fork detachment, pidfile creation/locking, and a parent notification pipe for readiness.

## Important APIs, Types, And Functions
`daemonize()` forks into the background and returns the child-to-parent pipe fd to the final daemon. `update_pidfile()` writes and locks the pidfile. `gogogo()` writes a readiness byte to the parent. `check_child_completion()` waits in the original parent for that byte.

## Control Flow
`daemonize()` creates a pipe, forks; the parent waits for pipe readiness and exits with success/failure. The first child calls `setsid()`, changes to `/`, forks again, exits in the intermediate process, closes most fds in the final child, redirects stdin, and returns the pipe writer. `update_pidfile()` opens/locks/truncates/writes the pid and keeps the lock fd open. `gogogo()` sends the readiness byte and closes the pipe.

## State And Persistence
Persistent state is the pidfile and, on Cygwin, a companion `.lk` lockfile. In-process static fd state keeps locks alive. No other daemon state is persisted.

## Dependencies And Integration Points
Depends on Unix process, fd, select, and `coda_flock` portability wrappers. Used by Coda daemons that want controlled background startup.

## Risks
If the daemon never calls `gogogo()`, the launching parent blocks indefinitely. Only stdin is redirected; stdout/stderr remain caller-managed. `daemonize()` closes fds up to `FD_SETSIZE`, which may miss higher descriptors. Pid string assumes pid fits in 10 characters plus newline.

## Test Signals
Start daemons that call and omit `gogogo()`, verify parent exit codes, pidfile locking prevents duplicate starts, Cygwin lockfile path behavior, closed fd inheritance, working directory `/`, and stdout/stderr redirection by callers.
