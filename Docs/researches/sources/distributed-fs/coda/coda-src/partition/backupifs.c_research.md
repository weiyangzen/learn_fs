# sources/distributed-fs/coda/coda-src/partition/backupifs.c

Purpose: dummy partition backend for backup-system entries. It registers an `inodeops_backup` table with only `init` implemented; all inode methods are null.

Flow/state: `b_init` stats the configured partition directory and returns its device number, storing no private data. This lets backup partitions participate in the partition registry without supporting normal inode file operations.

Dependencies/risks: depends on `Partent` accessors, `partition.h`, and Coda assertions. Any caller that tries to invoke null inode methods on a backup partition will crash; type checks must happen before operation dispatch. Test signal is `DP_Init` accepting backup entries.
