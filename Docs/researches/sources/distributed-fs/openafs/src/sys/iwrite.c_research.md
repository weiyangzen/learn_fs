# sources/distributed-fs/openafs/src/sys/iwrite.c

## Purpose
`iwrite.c` is a legacy diagnostic program that writes a string into an inode on hard-coded `/vicepa` through the old `xiwrite` interface.

## Important APIs, types, and functions
The only routine is K&R-style `main`, using `stat`, `xiwrite`, and `atoi`.

## Control flow
It stats `/vicepa`, expects inode, offset, string, and count arguments, invokes `xiwrite(dev, inode, 17, offset, argv[3], count)`, then prints the byte count.

## State and persistence behavior
Successful execution modifies vice inode contents.

## Dependencies and integration points
It depends on legacy syscall exports, `/vicepa`, and sys test build linkage.

## Risks
It can corrupt data, has no argc check before hard-coded positional use beyond the decremented count test, hard-codes parameter `17`, and can request more bytes than the supplied string contains.

## Test signals
Use only disposable inodes; verify short writes, out-of-range offsets, oversized counts, missing `/vicepa`, and read-back through `iread`/`iopen`.
