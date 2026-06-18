# sources/distributed-fs/coda/coda-src/partition/ftreeifs.h

Purpose: private option/state structure for the ftree partition backend.

State: defines `RESOURCEDB` as `FTREEDB` and `struct part_ftree_opts` with depth, width, computed logwidth, resource fd, next counter, free bitmap, and lock.

Dependencies/risks: depends on LWP locks and bit vectors. The structure is embedded in `union PartitionData`, so layout matters to `partition.h` and `ftreeifs.c`. The lock field is not meaningfully used in the implementation, which is a concurrency risk.
