# sources/distributed-fs/coda/coda-src/util/mkpath.c

## Purpose
Creates the directory path leading to a file name, similar to a recursive `mkdir -p` for parent directories only.

## Important APIs, Types, And Functions
`mkpath(const char *name, mode_t mode)` is the single function. It finds the last slash, temporarily truncates the string there, recursively ensures the parent path, and creates the current directory.

## Control Flow
If there is no slash, the function succeeds. Otherwise it replaces the last slash with NUL, stats the parent path, restores the slash on each return path, checks existing paths are directories, recurses for missing parents, and calls `mkdir()` for the final parent.

## State And Persistence
Persistent state is the filesystem directories created with `mode`. There is no global state.

## Dependencies And Integration Points
Depends on `string.h`, `errno.h`, `sys/stat.h`, and recursive filesystem calls. Used by Coda utilities that need to ensure parent directories before file creation.

## Risks
The prototype takes `const char *` but the implementation mutates the buffer in place; passing a string literal or read-only memory is unsafe. Concurrent creators can make `mkdir()` return `EEXIST`, which is treated as failure. Absolute root and trailing slash edge cases need care.

## Test Signals
Pass mutable paths with no parent, existing parent, nested missing parents, parent component that is a file, absolute paths, trailing slashes, concurrent creation, and read-only string inputs under sanitizers.
