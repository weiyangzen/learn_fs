# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/daemon.h

## Purpose
Declares GlusterFS daemonization helpers and the canonical null-device path used when detaching a process from the terminal.

## APIs, Types, and Functions
`DEVNULLPATH` is `/dev/null`. `os_daemon_return(int nochdir, int noclose)` and `os_daemon(int nochdir, int noclose)` expose daemon setup variants. The parameters follow the standard daemon convention: optionally avoid changing directory and optionally avoid closing standard descriptors.

## Control Flow, State, and Persistence
The header carries no state. Implementations are expected to fork/session-detach, redirect descriptors to `DEVNULLPATH` when requested, and return status in the variant-specific manner.

## Dependencies and Integration
Integrated by process startup paths for `glusterfs`, `glusterfsd`, and management daemons. It interacts with PID files, `glusterfs_ctx_t.daemon_pipe`, logging startup, and service managers.

## Risks and Test Signals
Risks include descriptor leaks, double-fork error handling, changing cwd unexpectedly, and daemonizing under supervisors that expect foreground mode. Test signals are startup tests for `--no-daemon` and daemon modes, stderr/stdout closure checks, PID-file correctness, and failure injection around fork, setsid, chdir, and opening `/dev/null`.
