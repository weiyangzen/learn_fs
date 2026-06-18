# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mtd.c

## Purpose
`mtd.c` adapts NIC-specific nonvolatile storage operations to the Linux MTD subsystem. It registers and unregisters per-NIC MTD partitions, wires generic erase/read/write/sync callbacks to `struct ef4_nic_type` operations, and renames partitions when the network device name changes.

## Important APIs, Types, And Functions
`ef4_mtd_erase()` calls `efx->type->mtd_erase()`, while `ef4_mtd_sync()` calls `mtd_sync()` and logs failures with the partition's device/type names. `ef4_mtd_add()` initializes each `struct ef4_mtd_partition`'s embedded `struct mtd_info`, sets `_erase`, `_read`, `_write`, and `_sync`, invokes the NIC type's `mtd_rename()`, registers each partition with `mtd_device_register()`, and records it in `efx->mtd_list`. `ef4_mtd_remove()` unregisters all partitions and frees the allocated partition array. `ef4_mtd_rename()` reapplies type-specific names under RTNL.

## Control Flow
Add walks a caller-provided array with a configurable element size, registers partitions in order, and unwinds already-registered partitions if any registration fails. Removal first checks that the netdev is not registered, then repeatedly tries to unregister each partition; `-EBUSY` causes a one-second sleep/retry loop. The list order matters because `ef4_mtd_remove()` assumes the first list entry is the base allocation returned by the type-specific probe.

## State And Persistence
Persistent state is in `efx->mtd_list`, each embedded `mtd_info`, and the NIC's NVRAM/flash behind type-specific callbacks. The code does not manipulate flash contents directly except through delegated erase/read/write/sync operations. Partition names are mutable driver-visible state tied to the netdev name.

## Dependencies And Integration Points
This file depends on Linux MTD, module ownership, slab allocation, RTNL assertions, `net_driver.h`, and the `ef4_nic_type` MTD callback set compiled under `CONFIG_SFC_FALCON_MTD`. It integrates NIC flash/EEPROM storage with userspace MTD tooling while preserving hardware-specific implementation in NIC type code.

## Risks
The unregister loop can wait indefinitely while users hold MTD devices open. `ef4_mtd_remove()` assumes all partitions live in one allocation and that list order was preserved by `ef4_mtd_add()`. Add failure returns `-ENOMEM` for any registration failure, which may hide more specific MTD errors. Calling remove while the netdev is still registered triggers a warning and risks userspace races.

## Test Signals
Signals include MTD partition creation, correct partition names before and after netdev rename, read/write/erase/sync behavior on supported hardware, clean unregister after users close devices, and unwind behavior when a later partition fails to register. Kernel warnings around registered netdev removal or failed unregisters are important failure indicators.
