# sources/distributed-fs/ceph-client/drivers/scsi/Kconfig

## Purpose

This file is the top-level Kconfig menu for Linux SCSI device support. It defines the SCSI core, peripheral device classes, transport classes, low-level host adapters, virtual SCSI adapters, debug/test drivers, architecture-specific SCSI controllers, and includes subordinate Kconfig files for large driver families.

For this work item, the key local relationship is the BusLogic/FlashPoint configuration: `SCSI_BUSLOGIC` builds the BusLogic driver and `SCSI_FLASHPOINT` optionally includes the substantial FlashPoint SCCB Manager code in `FlashPoint.c`.

## Important APIs, Types, And Data

- `menu "SCSI device support"` wraps the full SCSI configuration area.
- `SCSI_MOD`, `SCSI_COMMON`, `SCSI`, `SCSI_DMA`, `SCSI_NETLINK`, and `SCSI_PROC_FS` configure SCSI core presence, DMA helper inclusion, netlink support, and legacy `/proc/scsi`.
- Peripheral device options include `BLK_DEV_SD`, `CHR_DEV_ST`, `BLK_DEV_SR`, `CHR_DEV_SG`, `BLK_DEV_BSG`, `CHR_DEV_SCH`, and `SCSI_ENCLOSURE`.
- Debug and test options include `SCSI_LIB_KUNIT_TEST`, `SCSI_PROTO_TEST`, `SCSI_CONSTANTS`, `SCSI_LOGGING`, `SCSI_SCAN_ASYNC`, and `SCSI_DEBUG`.
- Transport options under `menu "SCSI Transports"` include SPI, Fibre Channel, iSCSI, SAS, SRP, and `source "drivers/scsi/libsas/Kconfig"`.
- `menuconfig SCSI_LOWLEVEL` gates low-level host adapters when `SCSI!=n`; the following `if SCSI_LOWLEVEL && SCSI` contains most hardware and virtual HBA options.
- `SCSI_BUSLOGIC` is a tristate PCI/HAS_IOPORT/SCSI driver option for BusLogic MultiMaster and FlashPoint adapters. `SCSI_FLASHPOINT` is a bool depending on `SCSI_BUSLOGIC && PCI && HAS_IOPORT`.
- The file pulls in subsystem-specific Kconfig files for `aic7xxx`, `aic94xx`, `hisi_sas`, `mvsas`, `esas2r`, `megaraid`, `mpt3sas`, `mpi3mr`, `smartpqi`, QLogic FC/iSCSI/FCoE, Emulex, ARM SCSI, Chelsio, PCMCIA, and SCSI device handlers.

## Control Flow

Kconfig evaluation starts with core SCSI symbols. `SCSI` depends on `BLOCK` and selects DMA support, SG pools, common SCSI code, and BSG common support when needed. Peripheral options depend on `SCSI` and add disk, tape, CD-ROM, generic SG, BSG, changer, and enclosure interfaces.

Transport symbols are evaluated only when `SCSI` is enabled. They provide attributes and helper libraries that low-level drivers select or depend on. For example, Fibre Channel, iSCSI, SAS, and SRP adapter drivers depend on their transport attribute symbols or select helper libraries.

Low-level host adapter selection is gated by `SCSI_LOWLEVEL && SCSI`. Each driver expresses platform dependencies such as `PCI`, `ISA`, `HAS_IOPORT`, `X86`, `PPC_PSERIES`, `S390`, `SBUS`, `ZORRO`, `AMIGA`, `MAC`, `ATARI`, or virtualization buses. Driver selections then feed the SCSI Makefile through matching `CONFIG_*` symbols.

For BusLogic/FlashPoint, enabling `SCSI_BUSLOGIC` causes the Makefile to build `BusLogic.o`. Enabling the separate bool `SCSI_FLASHPOINT` causes `BusLogic.c`'s `#include "FlashPoint.c"` path to compile the SCCB manager and enables FlashPoint-specific fields in `BusLogic.h`. If `SCSI_FLASHPOINT` is disabled, the BusLogic driver can still build for non-FlashPoint MultiMaster adapters without including the large SCCB manager.

## State And Persistence

Kconfig itself has no runtime state. Its persistent outputs are `.config` values and generated build headers such as `include/generated/autoconf.h`. Those symbols control object selection, conditional compilation, and module/builtin linkage.

The file defines default values for selected options, including core SCSI module behavior, `SCSI_PROC_FS` default `y`, `BLK_DEV_BSG` default `y`, `SCSI_LOWLEVEL` default `y`, Hyper-V defaulting to `HYPERV`, and driver-specific defaults for tuning options such as SYM53C8XX DMA mode and queue depths.

## Dependencies And Integration Points

The file integrates with Kbuild through `CONFIG_*` symbols consumed by `drivers/scsi/Makefile` and subdirectory Makefiles. Core symbols select or depend on block, net, DMA, procfs, sysfs/debug features, KUnit, architecture buses, target core, firmware loader, IRQ polling, SGL allocation, and transport attribute libraries.

The BusLogic/FlashPoint integration crosses three files in this work item: `Kconfig` defines `SCSI_BUSLOGIC` and `SCSI_FLASHPOINT`; `Makefile` maps `CONFIG_SCSI_BUSLOGIC` to `BusLogic.o`; and `FlashPoint.c` is conditionally included by `BusLogic.c` under `CONFIG_SCSI_FLASHPOINT`.

Subordinate `source` statements are important integration points. Moving or renaming driver-family Kconfig files without updating this file breaks menu visibility and build selection for entire SCSI driver families.

## Risks And Edge Cases

- Dependency mismatches between Kconfig and Makefile can create selectable drivers that do not build, or object rules that never activate. `SCSI_FLASHPOINT` is especially easy to misunderstand because it has no Makefile object of its own.
- Tristate and bool interactions matter. `SCSI_FLASHPOINT` is bool while `SCSI_BUSLOGIC` is tristate, so FlashPoint code is compiled into the BusLogic object when selected rather than becoming a separate module.
- Architecture-specific options must retain strict dependencies. ISA, Zorro, SBUS, old Mac, Atari, Amiga, S390, Xen, Hyper-V, virtio, and PPC options can otherwise become visible on unsupported builds.
- Some options use `depends on m || OTHER != m` constraints to avoid builtin code depending on modular transport attributes. Removing those guards can cause link failures.
- Test options such as KUnit and protocol tests must remain gated to avoid pulling test code into production configs unexpectedly.

## Test Signals

Useful verification includes `make olddefconfig`, `make menuconfig` visibility checks, `scripts/kconfig/conf --syncconfig`, and targeted builds for representative configs: core SCSI only, SCSI disk/generic modules, `SCSI_BUSLOGIC=y` with `SCSI_FLASHPOINT=n`, `SCSI_BUSLOGIC=m` with `SCSI_FLASHPOINT=y`, and allmodconfig or allyesconfig on architectures that satisfy the relevant dependencies.

For BusLogic specifically, inspect generated `.config` and preprocessor paths to ensure `CONFIG_SCSI_FLASHPOINT` changes only the included FlashPoint SCCB manager content while the Makefile continues to build `BusLogic.o`.
