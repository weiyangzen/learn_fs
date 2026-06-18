# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/Kconfig

## Purpose
This Kconfig fragment declares the build-time option for the Broadcom MPI3 Storage Controller driver. `CONFIG_SCSI_MPI3MR` controls whether the `mpi3mr` SCSI/RAID controller driver is omitted, built in, or built as a module.

## Important APIs, Types, And Functions
The only symbol is `config SCSI_MPI3MR`, a tristate prompt named "Broadcom MPI3 Storage Controller Device Driver". It depends on `PCI` and `SCSI`, selects `BLK_DEV_BSGLIB` for block/scatter-gather helper support, and selects `SCSI_SAS_ATTRS` for SAS transport/sysfs attributes.

## Control Flow
Kconfig evaluation exposes this option only when PCI and SCSI support are enabled. If the user or defconfig enables it, the symbol value is consumed by the local Makefile through `obj-$(CONFIG_SCSI_MPI3MR) += mpi3mr.o`, which controls compilation and module/built-in linkage.

## State And Persistence
The selected value is persisted in the kernel build configuration, normally `.config`, and determines whether the driver is available in the resulting kernel/module set. It does not manage runtime device state itself.

## Dependencies And Integration Points
The option integrates with the kernel SCSI driver menu, PCI subsystem, SCSI core, block BSG library, SAS transport attributes, and the `drivers/scsi/mpi3mr/Makefile`. The help text identifies supported hardware as MPI3-based Storage and RAID controllers.

## Risks And Edge Cases
Because `SCSI_SAS_ATTRS` is selected unconditionally, builds that enable the driver also pull in SAS transport attribute support even for deployments focused on PCIe/NVMe controller personalities. Missing `PCI` or `SCSI` hides the option completely, so defconfigs for this hardware must enable those parents.

## Test Signals
Configuration tests should verify `n`, `m`, and `y` builds where applicable; that enabling `SCSI_MPI3MR` selects `BLK_DEV_BSGLIB` and `SCSI_SAS_ATTRS`; and that the resulting object linkage follows the Makefile for built-in and module builds.
