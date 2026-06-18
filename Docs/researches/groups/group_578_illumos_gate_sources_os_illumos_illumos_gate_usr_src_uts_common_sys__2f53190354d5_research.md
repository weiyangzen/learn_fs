# Group Research: group_578_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__2f53190354d5

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdbuffer.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdbuffer.h

## Purpose

`fdbuffer.h` declares the kernel `fdbuffer` abstraction used to describe file data I/O buffers backed either by VM pages or by a kernel/user address range. It is used by UFS extended vnode operations and the common `fdbuffer.c` implementation.

## Main Types

`fdb_type_t` distinguishes page-backed buffers (`FDB_PAGEIO`) from address-backed buffers (`FDB_VADDR`).

`fdb_holes_t` is a linked list of sparse file holes, each carrying an offset and length.

`fdbuffer_t` tracks buffer type, state flags, length, completed I/O count, dispatched I/O count, error and residual status, parent `buf_t`, pages/address backing, hole list, direct-I/O shadow pages, owning process, asynchronous completion callback, callback argument, and a mutex protecting asynchronous counters and state.

## Interfaces and Flags

State flags include `FDB_READ`, `FDB_WRITE`, `FDB_DONE`, `FDB_ERROR`, `FDB_ASYNC`, `FDB_SYNC`, `FDB_ICALLBACK`, and `FDB_ZEROHOLE`.

Public kernel routines create buffers (`fdb_page_create()`, `fdb_addr_create()`), register completion callbacks (`fdb_set_iofunc()`), inspect holes/errors (`fdb_get_holes()`, `fdb_get_error()`), add holes (`fdb_add_hole()`), set up `buf_t` I/O (`fdb_iosetup()`), complete I/O (`fdb_iodone()`, `fdb_ioerrdone()`), free buffers (`fdb_free()`), and initialize the subsystem (`fdb_init()`).

## Research Notes

This header is filesystem-relevant because it represents sparse-aware file data buffers and direct/page I/O state. The comments document important semantics: asynchronous users must either cover the full range or finish with `fdb_ioerrdone()`, callbacks own freeing, and zeroing of holes is deferred to avoid zeroing pages while holding UFS locks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdbuffer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdc.h

## Purpose

`fdc.h` defines private floppy disk controller and floppy unit state for the illumos floppy driver. It covers minor-number layout, media format IDs, controller/unit state machines, DMA command state, drive open tracking, and controller operation vectors.

## Main Types

`xlate_tbl_t` maps integer values to encoded controller bytes.

`struct fdattr` stores floppy media rotational speed, interleave, and format/read gap lengths.

`struct fdisk` is per-drive media state: controller object, media capabilities, I/O statistics, sector size shift, open/close semaphore, active `buf_t` queue, partition map, regular/layered/exclusive open state, current/default floppy format, controller encoding values, media-change timeout/state, eject flag, media state condition variable, and VTOC label data.

`struct fdstat` counts operations and errors.

`struct fdcsb` is the controller command/status block, including DMA handles/cookies/windows, execution state, selected drive, command/result bytes, retry counters, status, and operation flags.

`struct fdcntlr` is per-controller state: locks, I/O condition variable, selection semaphore, suspend state, device info, register/DMA/interrupt configuration, chip/mode/flags, kstats, current unit, watchdog timer, per-unit objects, motor timers/state, current cylinders, seek direction, active command block, and cached hardware register values.

`struct fcobjops` is the floppy controller operation vector.

`struct fcu_obj` is a floppy unit object with flags, lock, driver-private data, drive/media attributes, device info, unit number, operation vector, and parent controller.

## Interfaces and Constants

Minor numbers encode partition in low 3 bits and drive instance above that. Macros include `PARTITION()`, `DRIVE()`, `FDUNIT()`, and `FDCTLR()`.

Format IDs include 5.25-inch and 3.5-inch formats such as `FMT_5H`, `FMT_3H`, `FMT_3E`, and `FMT_AUTO`.

Command execution states are enumerated in `enum fxstate`; motor states and inputs are in `enum fmtrstate` and `enum fmtrinput`.

Controller flags include `FCFLG_BUSY`, `FCFLG_WANT`, `FCFLG_WAITMR`, `FCFLG_WAITING`, `FCFLG_TIMEOUT`, `FCFLG_DSOUT`, and `FCFLG_3DMODE`.

Unit flags include drive-present, write-protect, characteristics-known, label-known, changed/ejected detection, 3D mode, and busy bits.

## Research Notes

This is driver-private block-device infrastructure for legacy floppy media. It matters to filesystem research because PCFS and removable-media paths can issue floppy ioctls and depend on media geometry, partition maps, label state, and media-change semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdio.h

## Purpose

`fdio.h` defines the public floppy disk ioctl ABI: media/drive characteristics, raw controller commands, direct floppy commands, and disk-change reporting.

## Main Types

`struct fd_char` describes floppy media geometry: medium type, transfer rate, cylinders, heads, sector size, sectors per track, and stepping.

`struct fd_state` returns current device state such as bytes per sector, sectors per track, step rate, data rate, and controller error.

`struct fd_drive` describes drive hardware timing/capability parameters including ejectability, search table size, write precompensation, step timing, head load/unload timing, motor timing, pin semantics, and flags.

`struct fd_search` passes a table of candidate `fd_char` entries.

`struct fd_cmd` describes a high-level floppy command with command code, flags, block number, sector count, user buffer address, and buffer length. `struct fd_cmd32` is the 32-bit syscall ABI variant.

`struct fd_raw` passes raw command/result bytes and an optional transfer buffer. `struct fd_raw32` is the 32-bit ABI variant.

## Interfaces and Constants

Disk-change flags include `FDGC_HISTORY`, `FDGC_CURRENT`, `FDGC_CURWPROT`, and `FDGC_DETECTED`.

Drive flags include `FDD_READY`, `FDD_MOTON`, and `FDD_POLLABLE`.

High-level commands include read, write, seek, rezero, format unit, and format track.

Execution flags include `FD_SILENT`, `FD_DIAGNOSE`, `FD_ISOLATE`, `FD_READ`, and `FD_WRITE`.

Raw controller opcodes include specify, read ID, sense drive, rezero, seek, sense interrupt, format, read/write commands, and deleted-data variants.

Ioctls include `FDIOGCHAR`, `FDIOSCHAR`, `FDEJECT`, `FDGETCHANGE`, `FDGETDRIVECHAR`, `FDSETDRIVECHAR`, `FDGETSEARCH`, `FDSETSEARCH`, `FDIOCMD`, `FDRAW`, and `FDDEFGEOCHAR`.

## Research Notes

This header is the stable control interface through which userland and filesystem helpers can query and manipulate floppy block-device geometry and media state. It is included by PCFS code in this tree.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdmedia.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdmedia.h

## Purpose

`fdmedia.h` supplies static default floppy media and drive tables used by the floppy driver: label format strings, media attributes, media geometries, drive timing profiles, and partition maps.

## Main Data

`deflabel_35` and `deflabel_525` are default ASCII label format strings for 3.5-inch and 5.25-inch floppies.

`fdtypes[]` maps each floppy format ID to `struct fdattr` values: rotational speed, interleave, read gap, and format gap.

`dfc_*` static `struct fd_char` instances describe default geometries such as 80x36, 80x21, 80x18, 80x15, 80x9, 77x8, 40x16, 40x9, 40x8, and 40x4.

`defchar[]` maps driver format IDs (`FMT_5H`, `FMT_3E`, etc.) to those geometries.

`dfd_350ED`, `dfd_350HD`, `dfd_525HD`, and `dfd_525DD` describe default drive timing and precompensation parameters.

`dpt_*` arrays define default `NDKMAP` partition maps for each geometry, normally with partition 0 as all but the last cylinder, partition 1 as the last cylinder, and partition 2 as the whole disk.

`fdparts[]` maps format IDs to default partition maps.

## Research Notes

Unlike most headers, this file defines static data directly. It is meant to be included by the floppy implementation to instantiate default media tables. Its storage relevance is the geometry-to-partition translation that determines how floppy block devices expose slices to filesystems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdmedia.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdsync.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdsync.h

## Purpose

`fdsync.h` is a private header for the internal `fdsync` system call. The comments state that it should not be shipped and that `fdsync` is not a public libc interface.

## Main Types

`fdsync_mode_t` selects the sync operation to perform on a file descriptor.

Values are:

`FDSYNC_FS`: sync the filesystem containing the file descriptor, corresponding to `syncfs(3C)`.

`FDSYNC_FILE`: sync outstanding file data and metadata, corresponding to `fsync(3C)`.

`FDSYNC_DATA`: sync outstanding file data only, corresponding to `fdatasync(3C)`.

## Research Notes

This file is small but directly filesystem-relevant. It defines the kernel-private dispatch mode for fd-based syncing and separates whole-filesystem sync from file and data-only sync behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fdsync.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/feature_tests.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/feature_tests.h

## Purpose

`feature_tests.h` centralizes illumos feature-test macro handling for standards namespaces, large-file compilation, compiler language levels, and visibility of extension symbols.

## Main Behavior

It derives `_POSIX_C_SOURCE` from `_POSIX_SOURCE` when needed.

It defines private implementation macros such as `__XOPEN_OR_POSIX`, `_STRICT_STDC`, `_STRICT_SYMBOLS`, `_STRICT_POSIX`, `_STDC_C99`, `_STDC_C11`, `_STDC_C17`, and `_STDC_C23`.

It detects compiler C standard levels from `__STDC_VERSION__` and compiler strictness from Sun C and GCC conventions.

It makes `_LARGEFILE64_SOURCE` and `_LARGEFILE_SOURCE` visible by default in non-strict, extension, kernel, and kmemuser contexts.

It normalizes `_FILE_OFFSET_BITS`: 64-bit builds must use 64; 32-bit builds default to 32 and allow 32 or 64.

It maps `_XOPEN_SOURCE` and `_POSIX_C_SOURCE` values onto internal `_XPG3` through `_XPG8` macros, including POSIX.1-2024 / XPG8 support.

It defines `_XOPEN_VERSION` based on the detected standard level.

It controls `_LONGLONG_TYPE`, `_RESTRICT_KYWD`, `_NORETURN_KYWD`, `_C23_UNSEQ_ATTR`, and `__EXT1_VISIBLE`.

It advertises header support macros for ISO C99, C11, C++ 1998, and DTrace version 1, while leaving `__STDC_LIB_EXT1__` undefined.

## Research Notes

This header affects nearly every public/system header, including filesystem-facing APIs such as `stat`, `statvfs`, `fcntl`, `unistd`, `uio`, and time interfaces. Large-file mode and strict symbol visibility are especially important for filesystem ABI compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/feature_tests.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fem.h

## Purpose

`fem.h` defines the kernel File Event Monitoring framework for vnode and VFS operation interception. It lets filesystem consumers install monitor stacks that wrap vnode/VFS operations and forward to the next operation in the chain.

## Main Types

`femarg_t` / `fsemarg_t` carry the current vnode, vnode pointer, VFS, or anonymous argument plus the current `fem_node`.

`fem_t` describes a vnode operation monitor: name, operation template, and full `FEM_OPS` function table.

`fsem_t` describes a VFS operation monitor: name, operation template, and full `FSEM_OPS` function table.

`struct fem_node` holds monitor/private available data, a union of FEM/vnode/FSEM/VFS operation pointers, and optional hold/release callbacks for the available data.

`struct fem_list` is a reference-counted stack of monitor nodes.

`struct fem_head` owns the monitor list under a mutex.

`femhow_t` controls install policy: `FORCE`, `OPUNIQ`, or `OPARGUNIQ`.

## Interfaces

`FEM_OPS` mirrors the vnode operation surface: open, close, read, write, ioctl, setattr/getattr, lookup/create/remove/link/rename, directory operations, symlink/readlink, fsync, inactive, fid, rwlock, locking, page operations, mmap operations, poll, dump, pathconf, security attributes, share locks, vnode events, and zero-copy buffer operations.

`FSEM_OPS` mirrors VFS operations: mount, unmount, root, statvfs, sync, vget, mountroot, freevfs, vnstate, and syncfs.

`vnext_*` routines continue from a FEM monitor to the next vnode operation. `vfsnext_*` routines continue from a FSEM monitor to the next VFS operation.

Management routines include `fem_init()`, `fem_create()`, `fem_free()`, `fem_install()`, `fem_is_installed()`, `fem_uninstall()`, `fem_getvnops()`, `fem_setvnops()`, and the analogous `fsem_*` routines.

## Research Notes

This is a core filesystem extension point. It supports NFS delegation behavior, SMB filesystem event interception, portfs hooks, and common VFS/vnode interception. Monitor lists are copy/reconfigured stacks, so modules cannot assume a fixed list identity after installation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc.h

## Purpose

`fc.h` is the global include wrapper for the Fibre Channel transport subsystem.

## Main Interfaces

The header only includes `<sys/fibre-channel/fc_types.h>` and provides the include guard `_FC_H`.

## Research Notes

This is an umbrella entry point used by Fibre Channel adapter drivers and transport consumers. Storage relevance comes from Fibre Channel being a block/SCSI transport layer rather than from any direct filesystem logic in this wrapper.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc_appif.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc_appif.h

## Purpose

`fc_appif.h` defines Fibre Channel application/transport-visible protocol structures: topology constants, CT headers, World Wide Names, service parameters, login payloads, name-server command buffers, RLS/RNID payloads, and NPIV creation entries.

## Main Types

`fc_ct_header_t` is a Common Transport header with endian-dependent bitfields for revision, initial node ID, FC service type/subtype, options, command/response, AIU size, reason/explanation, and vendor field.

`la_wwn_t` represents an 8-byte World Wide Name as raw bytes, two 32-bit words, or parsed NAA/nport/WWN fields.

`svc_param_t` and `com_svc_t` hold class/common service parameters.

`ls_code_t` stores an ELS code in endian-dependent layout.

`la_els_logi_t` is the ELS login payload with common service parameters, port/node WWNs, class 1-3 service parameters, reserved data, and vendor version.

`fc_ns_cmd_t` passes name-server commands with request/response payload pointers and a response CT header. 32-bit syscall variants exist under `_SYSCALL32`.

`fc_rls_acc_t`, `la_els_rls_t`, and `la_els_rls_acc_t` describe Read Link Status request/accept data.

`fc_rnid_t`, `la_els_rnid_t`, `fc_rnid_hdr_t`, and `la_els_rnid_acc_t` describe RNID node identification data.

`la_npiv_create_entry_t` describes an NPIV virtual port creation request with virtual node/port WWNs and vindex.

## Constants

Topology constants include unknown, private loop, public loop, fabric, point-to-point, and no-name-server states. `FC_IS_TOP_SWITCH()` identifies switched topologies.

Remote port states include invalid, valid/logged out, and logged in.

WWN, firmware revision, FCode revision, RNID data format, and RNID length constants are also defined.

## Research Notes

This header is part of the storage transport ABI. Its structures are used by Fibre Channel drivers and ioctl paths to exchange protocol records with transport and userland tooling. Endian-dependent bitfields are central to wire-format correctness.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc_appif.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc_types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc_types.h

## Purpose

`fc_types.h` defines common Fibre Channel transport types, sysevent names, reset/DMA behavior enums, and kernel-only FC transport include aggregation.

## Main Types

`fc_hba_state_change_t` is a 64-bit state-change tracker.

`fc_portid_t` is an endian-dependent 24-bit FC port identifier plus private loop LILP position.

`fc_hardaddr_t` is an endian-dependent 24-bit hard address.

`fc_porttype_t` stores an FC port type byte.

`fc_reset_action_t` specifies how an FCA should return commands after reset: none, all, or only outstanding commands.

`fc_dma_behavior_t` controls streaming DMA behavior for unaligned buffers.

`fc_fcp_dma_t` selects whether FCP command/response allocation should use DVMA space.

`fc_ulp_rscn_info_t` carries ULP RSCN count information; zero is the invalid count sentinel.

## Interfaces and Includes

Sysevent class/subclass strings cover FC port attach/detach/online/offline/RSCN and target/device add/remove/online/offline events.

In kernel builds, the header aggregates FC protocol, link, name-server, FLA, FC-AL, transport control, error, ioctl, FCP, DDI, and devctl headers.

## Research Notes

This header is foundational for the illumos FC storage stack. It ties FC transport protocol types to SCSI/FCP consumers and supplies the kernel include surface used by FCA drivers such as `emlxs` and `qlc`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fc_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs.h

## Purpose

`emlxs.h` is the main umbrella header for the Emulex LightPulse Fibre Channel/FCoE adapter driver.

## Main Interfaces

It defines `DRIVER_NAME` as `"emlxs"` and includes the driver’s OS, FCIO, hardware, mailbox, queue, IOCB, firmware, adapter database, message, event, thread, configuration, DFC library, FC, device, DFC, and extern headers.

Conditional includes add DH-CHAP authentication, COMSTAR target mode (`SFCT_SUPPORT`), SAN diagnostics, dump support, and Menlo support.

## Research Notes

This file contains no data structures of its own beyond the driver name. Its importance is dependency composition: including `emlxs.h` brings in the complete driver-private interface surface for the Emulex FCA, which is a storage transport driver backing FC/FCoE block devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_adapters.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_adapters.h

## Purpose

`emlxs_adapters.h` defines the Emulex/ATTO adapter identity database: adapter model enum values, PCI vendor/device/subsystem IDs, JEDEC IDs, chip capability flags, model descriptors, firmware IDs, interrupt limits, SLI support, channel counts, and conditional static model tables.

## Main Types

`emlxs_adapter_t` enumerates supported adapter models across generations: DragonFly, Centaur, Pegasus, Thor, Helios, Zephyr, Hornet, Saturn, BE2/BE3/BE4, Lancer FC/FCoE Gen5/Gen6, ATTO Celerity, and Prism Gen7 FC, plus Oracle-branded and excluded variants.

`emlxs_model_t` describes one model: adapter ID, PCI IDs, model strings, manufacturer, feature flags, chip family, firmware ID, interrupt limits, SLI mask, channel count, and program-type byte arrays for firmware/boot/SLI images.

## Constants and Tables

Vendor IDs include Emulex, ATTO, and OCE. Subsystem vendor IDs include Emulex, HP, IBM, Fujitsu, Cisco, Hitachi, and ATTO.

PCI IDs cover legacy SBUS/PCI devices through 64Gb FC adapters and FCoE OneConnect devices.

Model flags describe interrupt support (`INTx`, MSI, MSI-X), end-to-end authentication, GPIO LEDs, Oracle branding/exclusion, and unsupported status.

Chip flags distinguish DragonFly through Prism Gen7, plus grouped BE and Lancer-family masks.

SLI masks describe SLI2, SLI3, and SLI4 support.

Under `EMLXS_MODEL_DEF`, the file defines `emlxs_sbus_model[]`, `emlxs_pci_model[]`, and model counts. These tables include detailed descriptions and capabilities for each supported adapter.

## Research Notes

This header is hardware-enablement data for the FC storage driver. Matching PCI identity to model capabilities determines which firmware, SLI mode, interrupt type, authentication support, and FC/FCoE behavior the driver enables.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_adapters.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_config.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_config.h

## Purpose

`emlxs_config.h` defines driver tunable metadata and, when `DEF_ICFG` is set, the default configuration table for the Emulex FCA driver.

## Main Types

`emlxs_config_t` stores one tunable: name string, low/high/default/current values, flags, and help text.

`emlxs_cfg_parm_t` enumerates all tunable parameters. They cover console/log verbosity, IOCB and transfer sizing, unsolicited buffers, network-on, ACK0, topology, link speed, node count, interrupt coalescing delay/count, ALPA assignment, ADISC, power management, firmware checks, discovery/link/offline timeouts, LILP, PCI max read, heartbeat/reset/timeout controls, I/O tags, dynamic memory, FMA, MSI, SLI mode, NPIV, DH-CHAP authentication, target mode, work queues, persistent linkdown, patch enablement, target reset behavior, FCoE FCF timing, delayed discovery, request recovery qualifier mode, and performance hints.

## Constants and Tables

`EMLXS_CFG_STR_SIZE` is 32 and `EMLXS_CFG_HELP_SIZE` is 81.

`PARM_HIDDEN` marks hidden parameters; other flag names such as dynamic, reset, link, boolean, and hex are consumed from surrounding driver headers.

When `DEF_ICFG` is defined, `emlxs_cfg[]` must be in the exact enum order and provides min/max/default/flags/help text for every enabled parameter, with conditional entries for node throttle, FMA, max RRDY, MSI, DHCHAP, and SFCT.

## Research Notes

This is the driver’s configuration schema. Storage behavior affected here includes maximum I/O size, link topology/speed, discovery timing, NPIV virtual ports, authentication, FCoE failover timing, target mode, and persistent link state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_config.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_device.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_device.h

## Purpose

`emlxs_device.h` defines the global driver control structure for the Emulex FCA driver.

## Main Types

`emlxs_device_t` tracks:

`hba_count`: number of active HBAs.

`hba[MAX_FC_BRDS]`: pointers to HBA instances.

`lock`: global device lock.

`drv_timestamp` and `log_timestamp`: driver/log timing metadata.

`log[MAX_FC_BRDS]`: per-board message log pointers.

Conditional dump file pointers for text, dump, and CEE dump files are present under `DUMP_SUPPORT`.

## Research Notes

The comment states this structure must match `./mdb/msgblib.c`, indicating debugger/tooling ABI coupling. It is global driver state rather than per-I/O state, but it coordinates all FC adapter instances visible to the driver.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_device.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dfc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dfc.h

## Purpose

`emlxs_dfc.h` defines the driver-facing DFC ioctl command envelope, command numbers, error codes, and high-level returned information structures for Emulex diagnostics/configuration/control.

## Main Types

`dfc_t` is the main command envelope: command, flag, and four buffer/data slots. `dfc32_t` is the 32-bit kernel-side ABI variant.

`sd_bucket_info_t` is conditionally defined for SAN diagnostics latency buckets.

`dfc_hbainfo_t` returns extensive HBA identity, VPD, firmware, driver, topology, port, supported type/speed, fabric, node count, and PCI location data.

`dfc_node_t` returns remote FC node identifiers, RPI/XRI, flags, and service parameters.

`dfc_hbastats_t` returns FC link and frame statistics.

`dfc_drvstats_t` returns driver counters for link, mailbox, IOCB, FCP, ELS, CT, IP, unsolicited buffers, and conditional DH-CHAP counters.

`dfc_tgtport_stat_t` is conditionally defined for target-mode I/O buckets and FCT counters.

`dfc_vportinfo_t` returns NPIV virtual port state, WWNs, symbolic names, and ULP state.

## Commands and Errors

Command numbers cover HBA, I/O, link, node, event, revision, dump region, HBA stats, driver stats, FCIO passthrough, config get/set, events, mailbox, ELS, CT, CT response, Menlo, SCSI, diagnostics, loopback, reset, PCI/flash/memory/control-register access, NPIV, DH-CHAP auth, target stats, persistent linkdown, FCoE FCF/DCBX/QoS, and SAN diagnostics.

Error codes start at `0x200` and distinguish system/driver/HBA/I/O errors, argument/copyin/copyout problems, timeouts, resource exhaustion, offline/online state, NPIV failures, auth failures, Menlo/linkdown cases, and SAN diagnostic errors.

## Research Notes

This is a privileged storage-adapter management ABI. It exposes low-level adapter operations, firmware/flash/register access, FC protocol passthrough, NPIV, authentication, FCoE, and diagnostic controls that can materially affect block-device availability.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dfc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dfclib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dfclib.h

## Purpose

`emlxs_dfclib.h` defines the shared DFC library/driver data structures and constants for board discovery, mailbox commands, firmware/config access, CT vendor commands, NPIV, DH-CHAP management, FCP command/response layout, and FCoE information.

## Main Types

Board discovery types include `brdinfo_t` and `dfc_brdinfo_t`.

DMA/buffer descriptors include `ulp_bde_t` and `ulp_bde64_t`.

Mailbox command payloads include read service parameters, read revision, dump, dump4, update config, SLI config, read config, read log, log status, read event log, `dfc_mailbox_t`, and `dfc_mailbox4_t`.

FCoE config-region records include `tlv_fcoe_t`, `tlv_fcfconnectentry_t`, and `tlv_fcfconnectlist_t`.

Information structures include `dfc_ioinfo_t`, `dfc_linkinfo_t`, `dfc_traceinfo_t`, `dfc_cfgparam_t`, `dfc_nodeinfo_t`, `dfc_vpd_t`, `dfc_destid_t`, `dfc_loopback_t`, `dfc_drvinfo_t`, `dfc_regevent_t`, binding-list structures, CT request structures, NPIV virtual port/resource/link/node structures, DH-CHAP config/password/status structures, FCP command/response structures, send-SCSI/FCP command info, and FCoE FCF list structures.

## Constants

Mailbox command codes cover shutdown, firmware load/run, NVRAM, diagnostics, link init/down/config, ring config/reset, read config/status/revision/link, login/unlogin, dump, update/download, MSI, SLI config, RPI/VFI/FCFI/VPI operations, and feature requests.

Event masks cover link, RSCN, CT, multipulse, dump, temperature, vport RSCN, SAN diagnostic events, and FCoE events.

Capability masks distinguish online/offline diagnostic operations, endian mode, SLI support, memory/flash/PCI/control-register access, configuration support, CT, HBA API, and SBUS.

Vendor-unique CT opcodes cover adapter/server/HBA/port/driver attributes, statistics, firmware verification/download/upgrade, HBA reset/diagnostics, security/access/key tables, SCSI target mapping and report-luns/inquiry/read-capacity, persistent binding, node/address discovery, loopmap, beacon, and PCI register access.

NPIV constants define result codes, vport states, options, readiness checklist bits, and vport attributes.

FCP constants define SCSI status, FCP response validity/residual bits, task attributes, task management bits, and read/write flags.

## Research Notes

This is the largest DFC ABI header and contains many wire/hardware layouts with endian-dependent bitfields. It connects userland management tools, driver ioctl handling, mailbox firmware commands, FC protocol operations, NPIV, FCoE, and FCP/SCSI data paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dfclib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dhchap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dhchap.h

## Purpose

`emlxs_dhchap.h` defines Emulex DH-CHAP / FC-SP authentication constants, driver state records, negotiation payload layouts, challenge/reply/success/reject message layouts, and Diffie-Hellman group data structures. Its contents are active only under `DHCHAP_SUPPORT`.

## Main Types

`emlxs_auth_cfg_t` stores authentication configuration for a local/remote entity pair: timeout, mode, bidirectional flag, authentication type priorities, hash priorities, DH group priorities, reauthentication interval, status/time, node pointer, and list links.

`emlxs_auth_key_t` stores local/remote password metadata and bytes for an entity pair, with node pointer and list links.

`emlxs_auth_misc_t` stores challenge values, public/session keys, and responder-side private/public/session key state.

`emlxs_port_dhc_t` stores per-port fabric authentication state, status, and time.

`emlxs_node_dhc_t` stores per-node authentication state-machine state, previous state, discovery reference count, auth config/key copies, response timeouts, transaction IDs, initiator/responder flags, negotiated hash/group/bidirectional values, WWN, misc key/challenge state, reauth timing/status, fabric vendor, expected success, deferred I/O pointers, flags, and parent config/key pointers.

Negotiation payload structures include `AUTH_NEGOT_PARAMS_*`, `AUTH_MSG_HDR`, `AUTH_MSG_NEGOT_*`, and null-DH variants.

Message structures include `DHCHAP_REPLY_HDR`, `DHCHAP_CHALL_NULL`, `DHCHAP_CHALL`, `AUTH_RJT`, and `DHCHAP_SUCCESS_HDR`.

`DH_GROUP` describes a Diffie-Hellman group ID, length, and value.

## Constants

The header defines password types, auth modes, protocol IDs, hash IDs, DH group IDs, ELS AUTH message codes, endian-adjusted FC-SP constants, hash lengths, reject reason/explanation codes, maximum message sizes, parameter tags, fabric and node state-machine values, node events, reauth states, fabric vendor IDs, and per-node flags.

It declares a weak reference to `random_get_pseudo_bytes`.

## Research Notes

This header is security-critical for Fibre Channel authentication. It controls how the driver authenticates fabric/target peers and how authentication state can block or defer I/O. The code supports MD5/SHA1 and NULL/1024/1280/1536/2048 DH groups, with many structures reflecting FC-SP wire layout and endian requirements.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_dhchap.h -->