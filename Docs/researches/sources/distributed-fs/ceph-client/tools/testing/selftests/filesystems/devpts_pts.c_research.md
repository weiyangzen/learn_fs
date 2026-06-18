# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/devpts_pts.c

## Purpose
Validates `TIOCGPTPEER` and `/proc/<pid>/fd` symlink behavior for standard, invalid, and non-standard devpts mounts in a private mount namespace.

## Important APIs, Types, And Functions
Uses `unshare(CLONE_NEWNS)`, devpts mounts, bind mounts, `open` on ptmx, `unlockpt`, `ioctl(TIOCGPTPEER)`, `setsid`, `TIOCSCTTY`, `dup2`, `readlink`, `fork`, and `waitpid`. Helpers include `terminal_dup2()`, `terminal_set_stdfds()`, `login_pty()`, `wait_for_pid()`, `resolve_procfd_symlink()`, `do_tiocgptpeer()`, and three `verify_*` functions.

## Control Flow
The program skips unless stdin is a terminal, creates a private mount namespace, makes mounts private, tests `/dev/ptmx` bind-mounted from `/dev/pts/ptmx`, tests an invalid bind to a regular temp file expecting failure, then unmounts `/dev/pts`, mounts a new devpts instance at a temporary path, and verifies procfd symlinks point to that mountpoint.

## State And Persistence
Modifies mount namespace only: bind mounts/unmounts `/dev/ptmx` and `/dev/pts` inside the private namespace and creates temp mountpoints/files.

## Dependencies And Integration Points
Requires terminal stdin, mount namespace privileges, devpts, ptmx, and `TIOCGPTPEER` support.

## Risks
The test is skipped without a TTY, making automated coverage environment-dependent. Temporary cleanup uses `unlink` on directories in some branches, which may be imperfect but namespace exit discards mounts.

## Test Signals
Success is valid procfd symlink prefix for slave ptys, failure for invalid ptmx bind, and skip if `TIOCGPTPEER` is unsupported.
