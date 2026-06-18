# sources/cloud-native/fuse-overlayfs/src/sys/process.rs

## Purpose
`sys/process.rs` contains process-level libc wrappers for daemonization and effective-UID discovery.

## Important APIs, Types, And Functions
`daemonize` forks, exits the parent, creates a new session, redirects stdin/stdout/stderr to `/dev/null`, closes the extra fd, and changes directory to `/`. `geteuid` returns the current effective UID.

## Control Flow
Mount setup can call `daemonize` before worker threads exist. On fork, the parent exits successfully while the child detaches. Any fork, setsid, or dup2 failure logs and exits with status 1.

## State And Persistence
This changes process identity/lifecycle state, stdio fds, session membership, and cwd. It writes no filesystem state except opening `/dev/null`.

## Dependencies And Integration Points
The CLI/mount layer uses this module when running in background mode and for privilege decisions. It depends on libc and `log::error`.

## Risks
`daemonize` exits the process on failure and should only run before multi-threading. It does not do a double fork, write pidfiles, or report child startup success to the parent. Redirecting stdio can hide later diagnostics unless logging is configured elsewhere.

## Test Signals
No direct tests. Container-driven mount tests indirectly require foreground/background process behavior in normal fuse-overlayfs invocation paths.
