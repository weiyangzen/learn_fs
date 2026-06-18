# sources/distributed-fs/coda/coda-src/partition/partition.h

Purpose: public partition abstraction contract. It defines `DiskPartition`, backend private-data union, and the `inodeops` method table.

Important types/APIs: `DiskPartition` carries list linkage, mount/name/device/lock/free-space fields, backend operations, and private data. `inodeops` defines create/open/read/write/link/header/init/magic/list methods. Public functions initialize partitions, lock/unlock, find/get partitions, and report usage.

Integration/risks: includes backend headers, so the public abstraction knows both simple and ftree private types. Device numbers are persisted in RVM vnodes, making backend numbering stability important. Null method pointers are possible for backup partitions. Test signal is all server volume/inode code that compiles against this header.
