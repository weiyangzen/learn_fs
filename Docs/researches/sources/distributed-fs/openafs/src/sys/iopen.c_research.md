# sources/distributed-fs/openafs/src/sys/iopen.c

## Purpose
`iopen.c` is a diagnostic utility that opens a vice inode by number and dumps its contents to stdout.

## Important APIs, types, and functions
It defines `Usage` and K&R-style `main`. Important APIs are `stat`, `strtoull` or `atoi` depending on `AFS_64BIT_IOPS_ENV`, `PrintInode`, `IOPEN`, `read`, and `write`.

## Control flow
The command requires `<partition> <inode>`, obtains the partition device, parses the inode with the correct width, prints the planned open, calls `IOPEN(dev, ino, O_RDONLY)`, then reads five-byte chunks and writes them to stdout until EOF.

## State and persistence behavior
It opens and reads kernel inode state but does not intentionally modify data.

## Dependencies and integration points
It depends on `afssyscalls.h`, inode width macros, and the syscall wrappers in `libsys.a`.

## Risks
Output is raw file content, so binary data may corrupt terminal output. `printf("ino=%" AFS_INT64_FMT)` can be mismatched when `Inode` is not 64-bit. Direct inode reads bypass normal file authorization and should be restricted to repair/test contexts.

## Test signals
Verify behavior for 32-bit and 64-bit inode builds, invalid inode strings, missing partition, unreadable inode, and known small test files.
