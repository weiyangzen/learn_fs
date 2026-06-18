# sources/distributed-fs/coda/coda-src/librepair/dir.cc

## Purpose
Tiny legacy diagnostic program for printing host directory entries as seen by the client-side repair environment.

## APIs, Types, and Functions
K&R-style `main()` calls `opendir()`, `readdir()`, and prints `d_ino`, `d_reclen`, `d_namlen`, and `d_name` from `struct direct`.

## Control Flow, State, and Persistence
It opens the directory named by `argv[1]`, prints each entry, and exits. No persistent state is changed.

## Dependencies and Integration
Depends on old dirent/direct fields and libc directory APIs. It appears to be a standalone test aid rather than part of the repair library build target.

## Risks and Test Signals
Risks include missing argument checks, outdated `struct direct` portability, K&R style, and no `closedir()`. Test signal is successful listing of expanded replica directories during manual debugging.
