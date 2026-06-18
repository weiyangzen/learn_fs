# sources/distributed-fs/ceph-client/drivers/scsi/Makefile

## Purpose

This Makefile is the top-level Kbuild recipe for `drivers/scsi`. It maps SCSI Kconfig symbols to objects and subdirectories, defines SCSI core composite objects, records special per-object compiler flags, preserves important link ordering, and declares generated files for the SCSI device-info table and optional 53c700 firmware-script headers.

For this work item, its BusLogic/FlashPoint role is indirect but important: it builds `BusLogic.o` for `CONFIG_SCSI_BUSLOGIC`. `FlashPoint.c` is not listed as its own object because `BusLogic.c` includes it directly when `CONFIG_SCSI_FLASHPOINT` is enabled.

## Important APIs, Types, And Data

- `obj-$(CONFIG_SCSI) += scsi_mod.o` and `scsi_mod-y` compose the SCSI midlayer from `scsi.o`, `hosts.o`, `scsi_ioctl.o`, `scsicam.o`, `scsi_error.o`, `scsi_lib.o`, scan/sysfs/devinfo/logging/trace files, and conditional pieces such as DMA, constants, netlink, sysctl, procfs, debugfs, power management, device handlers, and BSG.
- Peripheral modules are assembled through `sd_mod-objs := sd.o`, conditional `sd_mod-*`, `sr_mod-objs := sr.o sr_ioctl.o sr_vendor.o`, and direct `obj-*` rules for `st.o`, `sg.o`, `ch.o`, and `ses.o`.
- Transport and helper libraries are deliberately ordered before low-level drivers: SPI, FC, iSCSI, SAS, libsas, SRP, device handlers, libfc, libfcoe, FCoE, FNIC, SNIC, and related offload drivers.
- Low-level adapter rules map many `CONFIG_*` symbols to individual objects or subdirectories, including `CONFIG_SCSI_BUSLOGIC += BusLogic.o`.
- Shared object dependencies are expressed inline, such as `53c700.o` being linked with several platform drivers, `wd33c93.o` with several Amiga/SGI drivers, `esp_scsi.o` with ESP-family drivers, and `libiscsi.o`/`libiscsi_tcp.o` with iSCSI transports.
- `CFLAGS_aha152x.o`, `CFLAGS_ncr53c8xx.o`, and generated `ncr53c8xx-flags-*` provide per-object compiler flags.
- Generated-file rules build `scsi_devinfo_tbl.c` from `include/scsi/scsi_devinfo.h` using a `sed` command, and optionally generate `53c700_d.h`/`53c700_u.h` from `53c700.scr` when `GENERATE_FIRMWARE` is set.

## Control Flow

Kbuild evaluates each `obj-$(CONFIG_...)` assignment after Kconfig has produced symbol values. Builtin objects are linked in the listed order; module objects become modules or module components. The Makefile explicitly notes that SCSI core must link first, then SCSI HBA drivers, then SCSI peripheral drivers to satisfy SCSI initialization assumptions.

The transport attribute objects appear before HBA driver objects so non-modular builds initialize transport classes before drivers register hosts. Low-level drivers and subdirectories are then appended according to the selected Kconfig symbols. Peripheral drivers are appended near the end, and `scsi_debug.o` is intentionally last so real devices probe first.

Composite object variables such as `scsi_mod-y`, `scsi_mod-$(CONFIG_...)`, `sd_mod-objs`, `hv_storvsc-y`, and `zalon7xx-objs` control the contents of larger built objects. Generated dependencies at the bottom ensure `53c700.o` waits for generated firmware headers and `scsi_sysfs.o` waits for the generated SCSI device-info table.

## State And Persistence

The Makefile has no runtime state. Its persistent effects are build artifacts: object files, modules, generated headers, and generated `scsi_devinfo_tbl.c`. `clean-files` records generated 53c700 headers that should be removed by `make clean`.

Object ordering is a persistent build contract: changing it can alter initcall and registration order in builtin kernels. The comments make this an explicit behavioral dependency rather than a cosmetic ordering choice.

## Dependencies And Integration Points

The file depends on symbols defined in `drivers/scsi/Kconfig` and subordinate Kconfig files. It integrates with the kernel Kbuild language through `obj-*`, composite object variables, `targets`, `clean-files`, `quiet_cmd_*`, `cmd_*`, `if_changed`, and explicit generated-file dependencies.

BusLogic/FlashPoint integration is split: `CONFIG_SCSI_BUSLOGIC` builds `BusLogic.o`; `CONFIG_SCSI_FLASHPOINT` is consumed by preprocessor conditionals inside `BusLogic.c`, `BusLogic.h`, and `FlashPoint.c`. There is no `obj-$(CONFIG_SCSI_FLASHPOINT)` entry, and adding one would be wrong unless the driver inclusion model changed.

Subdirectory integration is extensive. Driver families such as `aic7xxx`, `aic94xx`, `arcmsr`, `bnx2fc`, `elx`, `fcoe`, `fnic`, `isci`, `megaraid`, `mpt3sas`, `pm8001`, `qla2xxx`, `qla4xxx`, `qedi`, `qedf`, `smartpqi`, `snic`, and `device_handler` rely on this file to descend into their local Makefiles.

## Risks And Edge Cases

- Link ordering is semantically important. Moving transports after drivers or peripherals before HBAs can break registration assumptions in builtin kernels.
- Shared helper objects can be duplicated or omitted if Kconfig/object rules drift. Examples include `libiscsi.o`, `libiscsi_tcp.o`, `esp_scsi.o`, `53c700.o`, and `wd33c93.o`.
- `FlashPoint.c` is hidden behind `BusLogic.c` inclusion. Build-system cleanups that remove seemingly unused source files or add a standalone object rule can break the intended layout.
- Generated-file rules depend on exact macro patterns in `include/scsi/scsi_devinfo.h`. Changes to BLIST macro formatting may require updating `cmd_bflags`.
- Optional firmware generation under `GENERATE_FIRMWARE` is normally disabled. Builds that enable it need Perl and the script source; generated headers are otherwise expected to exist or be unused depending on configuration.
- Per-object CFLAGS must stay tied to the object name used by Kbuild. Renaming objects without updating `CFLAGS_*` silently drops compile-time options.

## Test Signals

Good test signals include `make drivers/scsi/` for selected configs, `make M=drivers/scsi` for module builds, allmodconfig/allyesconfig coverage, and targeted object builds such as `drivers/scsi/BusLogic.o`, `drivers/scsi/scsi_mod.o`, `drivers/scsi/sd_mod.o`, and selected transport drivers.

For this work item, check that `CONFIG_SCSI_BUSLOGIC=y/m` builds `BusLogic.o`, that toggling `CONFIG_SCSI_FLASHPOINT` changes the preprocessed BusLogic object content without adding a separate `FlashPoint.o`, and that `scsi_sysfs.o` properly regenerates `scsi_devinfo_tbl.c` after changes to `include/scsi/scsi_devinfo.h`.
