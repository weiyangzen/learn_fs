# sources/distributed-fs/openafs/src/venus/test/fulltest.c

## Purpose
`fulltest.c` is a destructive filesystem smoke test for Venus/cache-manager semantics in a supplied test directory. It exercises ordinary POSIX operations that an AFS client must implement correctly: create, chmod/fchmod, stat/fstat, byte-range locks, fsync, write, truncate, read, hardlink, symlink, mkdir/rmdir, directory reads, ownership edge behavior, rename, utimes, and cleanup.

## Important APIs, Types, And Functions
The only function is `main`. It uses standard POSIX calls: `mkdir`, `chdir`, `getcwd`, `open`, `close`, `access`, `chmod`, `stat`, `fchmod`, `fstat`, `fcntl` with `F_SETLK`, `fsync`, `write`, `ftruncate`, `read`, `link`, `unlink`, `symlink`, `readlink`, `rmdir`, `fchown`, `rename`, `truncate` when available, `utimes`, and `perror`.

## Control Flow
The program requires one directory argument, creates and enters it, then runs a fixed sequence of assertions. Each failure prints a diagnostic and returns `-1` or exits with status 1. The test starts with file creation and mode checks, validates shared and write lock set/unlock, writes and truncates content, checks hardlink and symlink behavior, validates non-empty directory removal failure, attempts directory reading, verifies writes to a read-only-mode file opened read/write, renames a file and checks source/target visibility, truncates to one byte where supported, updates timestamps, removes the final file, returns to the parent, removes the test directory, and prints success.

## State And Persistence
All state is filesystem state under the caller-provided directory. A successful run cleans up its generated files and directory. Failed runs can leave partial test artifacts such as `hi`, `bye`, `tdir`, `rotest`, or the top-level test directory.

## Dependencies And Integration Points
The test depends on POSIX filesystem behavior as mediated by the AFS cache manager when the target directory is in AFS. It is built by the local Venus test makefile and does not use pioctls directly.

## Risks And Test Signals
Risks include destructive behavior in the supplied directory, assumptions about directory read behavior, unset `struct timeval tvp[2]` before `utimes`, platform exclusions for `truncate`, and returning `-1` from `main` producing platform-specific exit codes. Its primary signal is broad AFS client POSIX compatibility; failures identify which basic operation or cache consistency path is broken.
