# sources/distributed-fs/ceph-client/drivers/mtd/mtdconcat.c

Purpose: generic MTD concatenation layer. It constructs a virtual `mtd_info` spanning multiple compatible subdevices and routes read/write/OOB/erase/lock/sync/suspend/bad-block operations to the correct child by translating offsets.

Important APIs/types/functions: `struct mtd_concat`, `mtd_concat_create()`, `mtd_concat_destroy()`, `concat_read()`, `concat_write()`, `concat_writev()`, `concat_read_oob()`, `concat_write_oob()`, `concat_erase()`, `concat_lock()/unlock()/is_locked()`, `concat_block_isbad()`, `concat_block_markbad()`. It depends on child MTD operation wrappers and compatibility checks for type, flags, write/OOB geometry, callbacks, and erase regions.

Control flow: create allocates a flexible concat object, copies base geometry from subdevice 0, enables callbacks when the corresponding master supports them, verifies all children are compatible, accumulates total size/bad-block stats, sets OOB layout, and builds uniform or variable erase-region metadata. Operation callbacks iterate children, skip offsets before the target child, limit each sub-operation to child size, update retlen/oobretlen, and continue across boundaries. Erase validates alignment against the virtual erase-region map before issuing per-child erases.

State and persistence: concat owns only virtual metadata and subdevice pointers; data persists in child MTDs. Bad-block and ECC stats are aggregated into the virtual device.

Risks and test signals: cross-device boundary handling is the core risk, especially OOB buffer pointer updates and vector write splitting. Compatibility rejects mixed OOB/ECC geometry but still allows writeability flag differences. Tests should cover reads/writes/OOB spanning boundaries, variable erase regions, lock ranges, bad-block propagation, panic writes, incompatible children, and destroy freeing erase-region metadata.
