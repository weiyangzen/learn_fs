# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/Kconfig

## Purpose

`Kconfig` declares the `SCSI_BNX2_ISCSI` tristate option for QLogic NetXtreme II iSCSI offload support.

## Important APIs, Types, and Functions

There are no runtime APIs. The configuration symbol is `SCSI_BNX2_ISCSI`, with prompt `QLogic NetXtreme II iSCSI support`.

## Control Flow

Selecting the option allows the kernel build to compile the bnx2i module or link it built-in. The symbol depends on `NET` and `PCI`, and selects `SCSI_ISCSI_ATTRS`, `NETDEVICES`, `ETHERNET`, `NET_VENDOR_BROADCOM`, and `CNIC`.

## State and Persistence Behavior

The only persistent effect is the kernel configuration value stored in the build configuration. No runtime state exists in this file.

## Dependencies and Integration Points

The option ensures the SCSI iSCSI transport attributes and Broadcom CNIC networking support are present before building `bnx2i.o`. It integrates with `drivers/scsi/bnx2i/Makefile`, which uses `obj-$(CONFIG_SCSI_BNX2_ISCSI)`.

## Risks and Edge Cases

If dependencies or selects drift from actual code needs, builds may fail or runtime registration with CNIC/libiscsi may be unavailable. Over-selecting networking symbols can force in larger dependency sets than expected.

## Test Signals

Validate `m`, `y`, and disabled builds; allmodconfig coverage; dependency resolution when `NET` or `PCI` is disabled; and module load with CNIC present.
