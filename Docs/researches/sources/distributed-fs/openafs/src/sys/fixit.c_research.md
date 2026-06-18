# sources/distributed-fs/openafs/src/sys/fixit.c

## Purpose
`fixit.c` is a root-only repair utility for legacy inode vice partitions. It increments reference counts for `#<inode>` files moved into `lost+found` by a non-AFS fsck so those inodes are not freed before the AFS fsck can reconcile them.

## Important APIs, types, and functions
The only routine is K&R-style `main`. It uses `stat`, `opendir`, `readdir`, `geteuid`, `atoi`, and OpenAFS `IINC`.

## Control flow
The command verifies effective UID 0, stats the supplied directory to get the device number, opens that directory, parses the volume id from `argv[2]`, and iterates directory entries. Every entry whose name starts with `#` is passed to `IINC(dev, d_ino, volid)`; failures are printed but do not abort the scan.

## State and persistence behavior
The utility mutates kernel/filesystem inode reference counts. It does not write files itself but is intended to be run before unmounting and running AFS-aware fsck.

## Dependencies and integration points
It depends on inode-based OpenAFS partitions, `afssyscalls.h`, kernel IOPS support, and the operational salvage/fsck procedure documented in the file header.

## Risks
There is no argc validation before using `argv[1]` and `argv[2]`. It assumes `d_ino` is the target inode and that all `#` entries under the supplied directory belong to the supplied volume. Running it against the wrong partition or volume id can corrupt reference counts.

## Test signals
Only test on disposable inode partitions. Check root enforcement, missing arguments, unreadable lost+found, entries with and without `#`, and expected `IINC` failures for unrelated volume ids.
