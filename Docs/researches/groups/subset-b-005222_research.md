# Research: subset-b-005222

This grouped report covers the FlashPoint SCCB manager and the top-level Linux SCSI Kconfig/Makefile files under `sources/distributed-fs/ceph-client/drivers/scsi/`. Each file section is bounded for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/FlashPoint.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/FlashPoint.c

## Purpose

`FlashPoint.c` is the BusLogic/Mylex FlashPoint SCCB Manager embedded into the Linux BusLogic SCSI host adapter driver. It is included directly by `BusLogic.c`, not compiled as an independent object, and is active only when `CONFIG_SCSI_FLASHPOINT` is enabled. When disabled, the file exposes only external prototypes for the FlashPoint entry points.

The implementation manages FlashPoint Harpoon-family PCI SCSI adapters at the register level. It probes the hardware, reads or repairs EEPROM/NVRAM settings, initializes bus-master DMA and the SCSI automation engine, starts and aborts SCCBs, handles interrupts and SCSI phases, performs synchronous/wide/tag negotiation, manages disconnect/reselect queues, runs SCAM ID assignment, and reports completions back through SCCB callbacks.

## Important APIs, Types, And Data

- `struct sccb_mgr_info` mirrors `struct fpoint_info` from `BusLogic.h` and carries adapter discovery results: I/O base, host ID, firmware revision, per-target negotiation masks, termination flags, model, BIOS translation data, and relative card number.
- `struct sccb` overlays the FlashPoint-specific tail of `struct blogic_ccb`. It stores the SCSI CDB, data pointer/length, sense pointer, callback, target/lun, host and target status, internal transfer counters, SG progress, tag, SCSI message/state, saved CDB for auto request sense, and queue links.
- `struct sccb_card` is the per-adapter runtime object returned as the card handle. It owns `currentSCCB`, `ioPort`, command count, disconnect queue table, scan cursor, global flags, host ID, and optional `struct nvram_info`.
- `struct sccb_mgr_tar_info` is per-card/per-target state: select queue head/tail, contingent allegiance, tag queue count, busy LUN table, disconnect queue indexes, EEPROM negotiation value, current sync register value, and target status flags.
- Global tables `FPT_BL_Card[MAX_CARDS]`, `FPT_sccbMgrTbl[MAX_CARDS][MAX_SCSI_TAR]`, `FPT_scamInfo[MAX_SCSI_TAR]`, and `FPT_nvRamInfo[MAX_MB_CARDS]` hold all manager state for up to eight cards.
- Public entry wrappers map typed BusLogic calls to internal SCCB-manager functions: `FlashPoint_ProbeHostAdapter`, `FlashPoint_HardwareResetHostAdapter`, `FlashPoint_ReleaseHostAdapter`, `FlashPoint_StartCCB`, `FlashPoint_AbortCCB`, `FlashPoint_InterruptPending`, and `FlashPoint_HandleInterrupt`.
- Hardware access is through `RD_HARPOON`, `WR_HARPOON`, `RDW_HARPOON`, `WRW_HARPOON`, and 32-bit Harpoon I/O helpers. The many `hp_*` offsets, phase bits, automation opcodes, EEPROM commands, and SCSI signal definitions describe the chip programming model.

## Control Flow

Probe starts in `FlashPoint_ProbeHostAdapter()`. It validates the Harpoon vendor/device IDs, initializes static manager tables on first use, decides whether existing firmware/BIOS state is usable, reads NVRAM stack data or EEPROM, derives per-target sync/disconnect/wide/fast/ultra masks, programs termination bits, detects narrow versus wide support, reads BIOS translation information from ARAM, installs the phase dispatch table, and marks the card present.

`FlashPoint_HardwareResetHostAdapter()` allocates or reuses a `struct sccb_card` slot, initializes per-card and per-target queues, reinitializes bus-master and SCSI/Xbow hardware, loads the default automation map, sets host ID registers, applies parity and termination policy, optionally resets the SCSI bus and SCAM state, loads target negotiation preferences, and marks the SCCB manager present through the hardware semaphore.

`FlashPoint_StartCCB()` validates target and LUN, calls `FPT_sinits()` to initialize manager fields, marks the manager active, and either queues the SCCB or selects it immediately. Selection is delegated to `FPT_ssel()`, which reserves LUN/tag/disconnect slots, loads automation RAM with ID/tag/CDB/negotiation messages, handles reset and abort messages, and starts Harpoon target selection.

Interrupt handling enters `FlashPoint_HandleInterrupt()`. It disables card interrupts, samples bus-master extended status, then loops over enabled Harpoon interrupts. It handles bad ISR conditions through `FPT_SccbMgr_bad_isr()`, command completion through `FPT_autoCmdCmplt()`, disconnects through `FPT_queueDisconnect()`, reselects through `FPT_sres()` followed by phase decode, data-count interrupts through `FPT_schkdd()`, bus-free events through `FPT_phaseBusFree()`, BIOS tickles, and new-command scheduling through `FPT_queueSearchSelect()`.

SCSI phase work is table-driven. `FPT_phaseDecode()` indexes `FPT_s_PhaseTbl` by the current SCSI phase and calls data-out, data-in, command, status, message-out, message-in, or illegal-phase handlers. Data phases use `FPT_dataXferProcessor()` and either `FPT_busMstrDataXferStart()` or `FPT_busMstrSGDataXferStart()`. Status and message paths update target status, handle `COMMAND_COMPLETE`, `MESSAGE_REJECT`, `RESTORE_POINTERS`, `DISCONNECT`, `SAVE_POINTERS`, `IGNORE_WIDE_RESIDUE`, SDTR, WDTR, aborts, target reset, and auto request sense.

Completion funnels through `FPT_queueCmdComplete()`. It applies underrun filtering, converts host/target status to SCCB status, restores a saved CDB after auto sense, updates residual counts for residual commands, manages low-power clock stop, removes disconnect queue entries, invokes the SCCB callback, clears `currentSCCB`, and schedules another command.

## State And Persistence

Runtime state is mostly in static global arrays, indexed by card and target. It is not dynamically allocated by this file and persists for the lifetime of the included BusLogic driver. Per-command mutable state is stored in the SCCB tail embedded in BusLogic CCBs.

Hardware-persistent state includes FlashPoint EEPROM/NVRAM contents. `FPT_DiagEEPROM()` verifies the firmware signature and checksum, then writes default EEPROM contents when invalid. SCAM device ID strings can be persisted by `FPT_scsavdi()` when `F_UPDATE_EEPROM` is set. `FlashPoint_ReleaseHostAdapter()` writes NVRAM-backed state back to the chip stack/ARAM or clears the stack marker when no NVRAM state exists.

The file also persists negotiated target state in memory: sync/wide/tag support, contingent allegiance, busy LUNs, disconnect tags, and queue depth. These are reset by bus reset, target reset, negotiation rejection, timeout, and table-init helpers.

## Dependencies And Integration Points

The source depends on `BusLogic.h` definitions because it is included from `BusLogic.c`. The internal `struct sccb_mgr_info` and `struct sccb` are intentionally layout-compatible with `struct fpoint_info` and `struct blogic_ccb`; the inline wrappers cast between the BusLogic-facing types and FlashPoint-internal types.

It integrates with the SCSI midlayer indirectly through BusLogic. BusLogic discovers PCI FlashPoint adapters, fills `adapter->fpinfo`, calls the FlashPoint probe/reset functions, passes CCBs into `FlashPoint_StartCCB()`, asks `FlashPoint_InterruptPending()` and `FlashPoint_HandleInterrupt()` from its IRQ path, and calls `FlashPoint_AbortCCB()` and `FlashPoint_ReleaseHostAdapter()` for error handling and teardown.

The code requires PCI I/O port access, SCSI protocol constants and messages, request-sense and status definitions, and BusLogic scatter/gather segment layout. It relies on Harpoon-specific I/O registers, ARAM/SGRAM switching, EEPROM bit-banging, hardware semaphores shared with BIOS, and SCAM bus handshakes.

## Risks And Edge Cases

- The file relies on strict structure layout compatibility with BusLogic CCB and fpoint structures. Any change to `BusLogic.h` fields under `CONFIG_SCSI_FLASHPOINT` must preserve the overlay contract.
- Many polling loops wait on hardware bits with no scheduler interaction and, in several paths, no strong timeout. Broken hardware or lost bus signals can hang the CPU in interrupt or reset paths.
- Queue accounting is delicate: `cmdCounter`, `discQCount`, target queue counts, tag counts, and busy LUN bits are updated from many error, disconnect, abort, and completion branches. A missed decrement can strand commands or corrupt disconnect lookup.
- Scatter/gather arithmetic treats `DataLength` as byte length of the SG table for SG commands and indexes `struct blogic_sg_seg` in a non-obvious way. Residual and restart paths are high risk for off-by-one and partial-segment bugs.
- Bus-master abort and FIFO-drain paths convert hardware faults into `SCCB_BM_ERR`, `SCCB_GROSS_FW_ERR`, parity, underrun, and overrun statuses. Error precedence matters because later code often sets a status only when it is still zero.
- EEPROM repair and SCAM persistence write nonvolatile adapter state. Regressions can change adapter identity, target ID assignments, termination defaults, or checksum contents.
- `FPT_default_intena` is global rather than per-card. In mixed-card or SCAM-level differences, interrupt-enable assumptions can leak across adapters.
- The fallback `#else` branch declares external functions when FlashPoint support is disabled, so callers must still be compiled in a way that does not require missing definitions unless `CONFIG_SCSI_FLASHPOINT` paths are eliminated.

## Test Signals

Build signals include compiling `drivers/scsi/BusLogic.o` with and without `CONFIG_SCSI_FLASHPOINT`, checking that `BusLogic.c` inclusion of `FlashPoint.c` sees the expected `struct blogic_ccb` layout, and verifying no new sparse warnings around I/O casts or pointer truncation.

Runtime signals include PCI FlashPoint probe logs, correct host adapter ID/model/termination reporting, successful hardware reset, successful SCSI scan, command completion under simple read/write, auto request sense on check condition, disconnect/reselect with tagged and untagged I/O, abort and target reset behavior, selection timeout handling, parity/bus-master fault paths, and SCAM ID assignment on legacy and SCAM-capable buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/FlashPoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/Kconfig -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/Makefile -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/Makefile -->
