# sources/distributed-fs/openafs/src/venus/test/owntest.c

## Purpose
`owntest.c` tests whether a caller can modify mode bits and timestamps on a writable file that may be owned by someone else. It is aimed at AFS ownership/permission semantics where write access through ACLs may not align with local Unix ownership.

## Important APIs, Types, And Functions
The only function is `main`. It uses `chmod`, `gettimeofday`, `utimes`, `stat`, `perror`, and `exit`. It expects a single pathname argument.

## Control Flow
The program validates its argument count, prints a start message, changes the target file to read-only mode `0444`, changes it back to `0666`, sets access and modification times to two times in the past, stats the file, verifies the modification time stuck, prints `Done.`, and exits 0. Any syscall failure exits with `errno`; a mismatched modification time exits 1.

## State And Persistence
The test intentionally persists changes to the target file's mode and timestamps. It does not restore the original mode or times, so it should be run only on disposable fixtures.

## Dependencies And Integration Points
It depends on POSIX metadata syscalls as implemented by the local filesystem or AFS cache manager. In AFS, it provides a focused signal for ACL-mediated metadata updates separate from Unix owner identity.

## Risks And Test Signals
Risks include destructive metadata changes, typoed usage text, assuming second-resolution mtime equality, and platform differences in permission checks for non-owner metadata operations. A passing run signals that chmod and utimes changes are accepted and visible via stat for the selected target.
