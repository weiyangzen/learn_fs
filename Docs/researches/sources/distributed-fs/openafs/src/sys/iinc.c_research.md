# sources/distributed-fs/openafs/src/sys/iinc.c

## Purpose
`iinc.c` is a diagnostic command that increments a vice inode reference count on a specified partition.

## Important APIs, types, and functions
The K&R-style `main` uses `stat`, `atoi`, and the `IINC` macro from `afssyscalls.h`.

## Control flow
It validates two positional arguments, stats the partition, prints device/inode details, calls `IINC(st_dev, inode, 17)`, reports failure, and exits.

## State and persistence behavior
Successful execution increments kernel/filesystem inode reference state for the selected vice inode.

## Dependencies and integration points
It is one of the sys test utilities and depends on the same legacy inode syscall path as fileserver salvage tooling.

## Risks
The volume/id parameter is hard-coded to `17`, the failure label says `iopen`, and arbitrary increments can leak or misassociate inodes.

## Test signals
Use with disposable test inodes; pair with `idec` and `istat` to verify link/reference changes and error paths.
