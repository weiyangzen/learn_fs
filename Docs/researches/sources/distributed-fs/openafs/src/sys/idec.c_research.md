# sources/distributed-fs/openafs/src/sys/idec.c

## Purpose
`idec.c` is a diagnostic command that decrements a vice inode reference count on a specified partition.

## Important APIs, types, and functions
The only routine is K&R-style `main`, using `stat`, `atoi`, and the `IDEC` macro from `afssyscalls.h`.

## Control flow
The command checks for at least two positional arguments, stats the partition path to obtain `st_dev`, prints the operation, calls `IDEC(st_dev, inode, 17)`, reports failure, and exits.

## State and persistence behavior
It mutates kernel/filesystem inode reference state and can make an inode eligible for deletion.

## Dependencies and integration points
It requires legacy inode IOPS support through `libsys.a` and is built as a `tests` target from `src/sys/Makefile.in`.

## Risks
The volume/id parameter is hard-coded to `17`, the error message says `iopen` on `IDEC` failure, and misuse can destroy data on a vice partition.

## Test signals
Use only disposable vice partitions; test missing args, invalid partition, invalid inode, and decrement behavior paired with `iinc`/`istat`.
