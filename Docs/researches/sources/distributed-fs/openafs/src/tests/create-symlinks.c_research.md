<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-symlinks.c -->
# sources/distributed-fs/openafs/src/tests/create-symlinks.c

## Purpose
Stress-creates many numeric symlinks and verifies all link targets remain stable.

## Important APIs, Types, and Functions
functions: creat_symlinks, verify_contents, usage, main

## Control Flow
Parses count and optional verbose flag, creates symlinks named `0..count-1` to the constant target `kaka`, then reads every symlink back with `readlink` and compares the content.

## State and Persistence Behavior
Persists count-sized directory entries in the current directory and leaves cleanup to the surrounding harness.

## Dependencies and Integration Points
OpenAFS build headers (`afsconfig.h`, `afs/param.h`) and libc/POSIX calls; BSD-style err/warn reporting

## Risks and Test Signals
Exercises directory mutation, symlink creation, link target storage, and MAXPATHLEN-sized read buffers.

## Source Notes
Read as C program; 138 source lines; generated from manifest group `subset-b-007804` in source-tree order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/create-symlinks.c -->
