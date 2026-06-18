# sources/distributed-fs/coda/coda-src/partition/inodeops.c

Purpose: compatibility dispatch layer that exposes inode operations by `Device` number rather than requiring callers to hold a `DiskPartition *`.

APIs and flow: `icreate`, `iopen`, `iinc`, `idec`, `iread`, and `iwrite` call `DP_Find(devno)` and then dispatch through the partition's `inodeops` table. `get_header` and `put_header` dispatch directly from an already known `DiskPartition *`.

State/dependencies: depends on global `DiskPartitionList` populated by `DP_Init` and backend method tables. Risks include null method pointers for backup partitions, silent `0`/`-1` returns when a device is missing, and no validation of backend capabilities. Test signal is any partition test using legacy inode APIs.
