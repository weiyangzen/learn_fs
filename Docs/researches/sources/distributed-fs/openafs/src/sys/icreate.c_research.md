# sources/distributed-fs/openafs/src/sys/icreate.c

## Purpose
`icreate.c` is a small diagnostic test program for the legacy `icreate` inode syscall.

## Important APIs, types, and functions
The K&R-style `main` parses vnode, uniquifier, and data-version values, stats `/vicepa`, calls `icreate(status.st_dev, 0, 17, vnode, unique, datav)`, and prints the returned inode.

## Control flow
It stats a hard-coded vice partition, converts three arguments with `atoi`, invokes the syscall wrapper, reports errors with `perror`, and exits success or failure.

## State and persistence behavior
Successful execution creates a vice inode on the `/vicepa` device, altering filesystem/kernel inode state.

## Dependencies and integration points
It depends on non-namei inode support and the syscall wrappers built by `src/sys/Makefile.in`.

## Risks
No argument count validation appears before `argv[1..3]`, `/vicepa` is hard-coded, and magic parameter `17` is unexplained in the tool. It is unsafe outside disposable legacy test partitions.

## Test signals
Run only in a controlled legacy inode test environment. Validate missing args, absent `/vicepa`, and successful creation followed by inspection with `iopen`/`istat`.
