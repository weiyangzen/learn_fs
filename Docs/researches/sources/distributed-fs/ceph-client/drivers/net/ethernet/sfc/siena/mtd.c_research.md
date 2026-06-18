# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mtd.c

## Purpose

`mtd.c` exposes NIC non-volatile storage partitions through the Linux MTD subsystem. It is a generic wrapper: device-specific read, write, erase, sync, and rename behavior is supplied by `efx->type` callbacks.

## Important APIs, Types, and Functions

`efx_mtd_erase()` and `efx_mtd_sync()` are MTD operation callbacks. `efx_mtd_erase()` calls `efx->type->mtd_erase()`, while sync calls `efx->type->mtd_sync()` and logs partition-specific failures.

`efx_siena_mtd_add()` initializes an array of `struct efx_mtd_partition` objects, fills their `struct mtd_info` fields, calls `mtd_rename()`, registers each partition with `mtd_device_register()`, and adds registered partitions to `efx->mtd_list`. `efx_siena_mtd_remove()` unregisters all partitions and frees the partition array. `efx_siena_mtd_rename()` renames already-registered partitions under RTNL after netdev name changes.

## Control Flow

The NIC-specific MTD probe path prepares partition objects and passes them to `efx_siena_mtd_add()` with count and stride. For each partition, this file sets one-byte writesize, marks erasable partitions writable, connects MTD callbacks, derives a name, registers the MTD device, and then appends it to the NIC list. On partial failure, it walks previously initialized entries in reverse and unregisters them.

Removal requires the netdev not be registered, then repeatedly unregisters each partition. If `mtd_device_unregister()` returns `-EBUSY`, it sleeps and retries until the partition is free. After all list entries are removed, the first partition pointer is freed, relying on the add path's array allocation convention.

## State and Persistence Behavior

State persists in `efx->mtd_list` and each partition's embedded `mtd_info`. Actual flash contents are not cached here; every MTD read/write/erase routes to NIC-type callbacks. Partition names are mutable and derived from current netdev naming. Removal can block indefinitely while users hold MTD devices busy.

## Dependencies and Integration Points

This file depends on `CONFIG_SFC_SIENA_MTD`, Linux MTD APIs, RTNL for rename assertions, `struct efx_mtd_partition` from `net_driver.h`, and NIC type callbacks for storage operations. It integrates with driver probe/remove, netdev rename handling, and user-space MTD tools.

## Risks and Test Signals

The biggest contract risk is ownership of the partition array: `efx_siena_mtd_remove()` frees the first list entry as the base pointer, so NIC-specific allocation must supply one contiguous array and preserve list order. The unregister retry loop can wait forever if a partition remains busy. Tests should cover partial registration failure, rename under RTNL, open-MTD removal behavior, read/write/erase callback propagation, and module unload with active MTD users.
