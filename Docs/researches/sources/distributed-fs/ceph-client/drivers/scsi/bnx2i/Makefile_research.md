# sources/distributed-fs/ceph-client/drivers/scsi/bnx2i/Makefile

## Purpose

`Makefile` defines how the bnx2i iSCSI offload driver is built.

## Important APIs, Types, and Functions

The composite object `bnx2i-y` consists of `bnx2i_init.o`, `bnx2i_hwi.o`, `bnx2i_iscsi.o`, and `bnx2i_sysfs.o`. `obj-$(CONFIG_SCSI_BNX2_ISCSI) += bnx2i.o` connects the composite object to the Kconfig symbol.

## Control Flow

There is no runtime flow. At build time, Kbuild compiles the listed objects into `bnx2i.o` when `SCSI_BNX2_ISCSI` is enabled.

## State and Persistence Behavior

No runtime state exists. The file controls build artifact composition.

## Dependencies and Integration Points

It integrates with the kernel Kbuild system and the local Kconfig. The listed objects provide module init/CNIC registration, hardware queue and completion handling, libiscsi transport operations, and sysfs attributes.

## Risks and Edge Cases

Omitting any object can produce missing symbols or a module that registers but lacks required transport or sysfs behavior. Adding objects in the wrong directory or with mismatched config guards can break incremental builds.

## Test Signals

Build with `CONFIG_SCSI_BNX2_ISCSI=m` and `y`, inspect that `bnx2i.o` includes all four objects, and run modpost for unresolved symbols.
