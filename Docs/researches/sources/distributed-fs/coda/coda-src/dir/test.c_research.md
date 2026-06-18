# sources/distributed-fs/coda/coda-src/dir/test.c

## Purpose
Small legacy command-line driver for checking and optionally salvaging a directory by numeric file id.

## APIs, Types, and Functions
K&R-style `main()` calls `DInit(20)`, `DirOK()`, optional `DirSalvage()`, and `DFlush()`. It parses one or two integer arguments with `atoi()`.

## Control Flow, State, and Persistence
With one argument it checks the source fid; with two it checks and then salvages from source to target. It initializes the old directory buffer cache and flushes it before exit. Persistence occurs through the legacy directory storage touched by `DirSalvage()`.

## Dependencies and Integration
Depends on old `coda_dir.h` buffer/salvage APIs and a working legacy directory backend.

## Risks and Test Signals
Risks include K&R C, missing includes/prototypes in the snippet, a `printf("DirOK returned %d.\n")` bug that omits the value, weak argument validation, and reliance on legacy APIs. Test signals are `DirOK` output, salvage return code, and subsequent readability of the target directory.
