<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/apwd.c -->
# sources/distributed-fs/openafs/src/tests/apwd.c

## Purpose
Tests pathname reconstruction and current-working-directory behavior, including libc `getcwd`, a direct Linux `getcwd` syscall path when available, a classic inode-walking implementation, and a Linux `/proc/self/cwd` implementation.

## Important APIs, Types, And Functions
Important helpers include `initial_string`, `expand_string`, `guarantee_room`, `getcwd_classic`, optional `getcwd_proc`, optional `getcwd_syscall`, `test_1`, `test_it`, `usage`, and `main`. It uses `lstat`, `opendir/readdir`, `readlink`, buffer growth, `agetarg`, and verbose logging.

## Control Flow
The classic implementation walks upward using `..`, compares device/inode pairs to root, scans parent directories to find the current name, and prepends path components into a dynamically growing buffer. `test_1` compares each implementation with libc `getcwd`, including caller-supplied buffers, allocated buffers, ERANGE growth behavior, and overwrite guards. `main` parses `--verbose`/`--help`, writes diagnostics to fd 4 when available, and runs libc, syscall, classic, and proc variants according to platform macros.

## State And Persistence
No persistent filesystem writes are intended. It allocates transient buffers and writes verbose diagnostics to file descriptor 4 or `/dev/null`.

## Dependencies And Integration Points
`checkpwd` invokes this binary. It validates directory/inode behavior of the filesystem under test, including mount-point transitions, direct kernel getcwd behavior, Linux procfs behavior, and buffer boundary handling.

## Risks And Test Signals
`guarantee_room` uses `opr_min(*size * 2, len)`, which appears inverted for ensuring room and may not grow enough. Filesystems with unstable inode/device reporting will fail classic reconstruction. Signals are zero exit and matching custom/libc paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/apwd.c -->
