# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/mtd.c

Purpose: this file adapts NIC-specific flash/NVRAM operations to the Linux MTD subsystem. It registers SFC firmware partitions as `struct mtd_info` devices and delegates erase/read/write/sync/rename behavior to the active `efx_nic_type`.

Important APIs: `efx_mtd_add()` initializes and registers an array of `struct efx_mtd_partition`; `efx_mtd_remove()` unregisters every partition and frees the partition allocation; `efx_mtd_rename()` refreshes partition names under RTNL. Internal wrappers are `efx_mtd_erase()`, `efx_mtd_sync()`, and `efx_mtd_remove_partition()`.

Control flow: add iterates partition records using the supplied stride, fills MTD callbacks, sets `MTD_WRITEABLE` unless `MTD_NO_ERASE` is present, asks the NIC type to rename the partition, registers it, and appends it to `efx->mtd_list`. On partial failure it unregisters already-created partitions in reverse and returns `-ENOMEM`. Remove waits out `-EBUSY` unregister results by sleeping and retrying, then unlinks list nodes and finally frees the first allocation block.

State and dependencies: persistent state is the in-memory `efx->mtd_list`; actual flash state lives on the device. Dependencies include `linux/mtd/mtd.h`, RTNL assertions for rename, and NIC type MTD callbacks.

Risks and tests: registration failure cleanup relies on list ordering and a single allocation block. `efx_mtd_remove()` warns if called while the netdev is registered. Test signals include MTD partition registration, read/write/erase/sync through firmware, rename after netdev rename, busy unregister handling, and probe failure cleanup.
