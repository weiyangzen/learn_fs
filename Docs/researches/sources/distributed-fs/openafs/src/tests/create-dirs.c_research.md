<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-dirs.c -->
# sources/distributed-fs/openafs/src/tests/create-dirs.c

## Purpose
Creates a requested number of numeric directories to stress mkdir and directory entry creation.

## Important APIs, Types, And Functions
Defines `creat_dirs`, `usage`, and `main`. Uses `strtol`, `snprintf`, `mkdir`, and `err`.

## Control Flow
Parses one numeric argument, loops from `0` to `count-1`, creates a directory named by the loop index with mode `0777`, and exits on first failure.

## State And Persistence
Leaves all created directories in the current directory.

## Dependencies And Integration Points
Used by shell/harness tests for directory creation workloads.

## Risks And Test Signals
Existing numeric directory names cause failure. Success is all requested directories created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-dirs.c -->
