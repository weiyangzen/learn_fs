# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/Makefile

## Purpose
Defines how the third-generation HiNIC driver is built by kbuild. It collects the hinic3 source files into a single `hinic3.o` module or built-in object under `CONFIG_HINIC3`.

## Important Build Entries
`obj-$(CONFIG_HINIC3) += hinic3.o` registers the driver object. `hinic3-objs` lists command queue, common helpers, EQs, ethtool, filtering, hardware config/communication/device/interface, IRQ, low-level device, main, mailbox, management, netdev ops, NIC config and I/O, queue common, RSS, Rx, Tx, and WQ objects. The researched files in this work item include `hinic3_cmdq.o` and `hinic3_common.o`; many referenced symbols are supplied by the other listed objects.

## Control Flow And State
The Makefile has no runtime state, but object ordering is kbuild input for linking one composite driver. Missing entries would appear as unresolved symbols; stale entries would break compilation if files are renamed or removed.

## Dependencies And Integration Points
It is controlled by `hinic3/Kconfig`. It integrates all hinic3 subsystem objects into the kernel networking driver tree under Huawei Ethernet drivers.

## Risks And Test Signals
Risks include accidentally omitting new objects, retaining deleted ones, or failing to update the list when features move between files. Test signals are `make M=drivers/net/ethernet/huawei/hinic3`, full kernel builds with `CONFIG_HINIC3=m` and `=y`, and modpost checks for unresolved or unused exported symbols.
