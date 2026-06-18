# Group Research: group_616_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__942e8173292c

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/spc3_types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/spc3_types.h

## Purpose
Defines packed SPC-3/SPC-4 SCSI command, status, mode-page, diagnostic, persistent reservation, buffer, inquiry, REPORT LUNS, and NAA identifier wire structures used by illumos SCSI code.

## Main Interfaces
- `spc3_cmd_t`: broad SCSI opcode enum mapped to illumos `SCMD_*` constants and explicit numeric opcodes.
- `spc3_dev_type_t`, `sam4_status_t`, `spc4_protocol_id_t`, `naa_id_t`.
- Packed CDB/data layouts for INQUIRY, LOG SELECT/SENSE, MODE SELECT/SENSE, PERSISTENT RESERVE IN, READ/WRITE BUFFER, REQUEST SENSE, REPORT LUNS, SEND/RECEIVE DIAGNOSTIC, TEST UNIT READY, media serial number, and aliases.
- Mode page structures for control, control extension, disconnect/reconnect, informational exceptions, and power condition pages.
- NAA identifier layouts and helper macros including `NAA_IEEE_EXT_*`, `NAA_IEEE_REG_*`, and `NAA_IEEE_REG_EXT_*`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/cdio.h`, `sys/sysmacros.h`, `sys/scsi/generic/commands.h`, and `sys/scsi/impl/commands.h`. It relies on illumos bitfield and multi-byte SCSI access macros such as `DECL_BITFIELD*`, `SCSI_READ*`, and `SCSI_MK*`.

## Research Notes
The file uses `#pragma pack(1)` around protocol structures, so it is intended to match on-the-wire SCSI layouts rather than host-natural C layout. Several structures use one-element flexible arrays.

## Notable Risks
- Any layout, packing, endian, or bitfield change can break SCSI protocol interoperability.
- Flexible array structures must be sized from protocol length fields.
- Several opcode enum names alias the same numeric opcode for different device classes; command interpretation depends on device type and CDB format.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/spc3_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/status.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/status.h

## Purpose
Provides an implementation-specific SCSI status size constant.

## Main Interfaces
- `STATUS_SIZE`: fixed status block allocation size of 4 bytes.

## Dependencies And Relationships
No external includes. This complements generic SCSI status definitions and allocation code that needs a default status buffer size.

## Research Notes
The file is intentionally tiny and only wraps the constant in standard include guards and C++ linkage guards.

## Notable Risks
- Code assuming richer status layout must use the generic status structures, not this allocation-size constant alone.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/status.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/transport.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/transport.h

## Purpose
Defines the SCSA HBA transport interface: `scsi_hba_tran`, HBA attach/allocation APIs, packet allocation helpers, initiator-port and target-map interfaces, and minor-number conventions.

## Main Interfaces
- `scsi_hba_tran_t` and `struct scsi_hba_tran`: HBA vector table for target init/probe/free, packet start, reset, abort, capability, packet allocation, DMA lifecycle, reset notify, event callbacks, quiesce, bus reset/config/power, packet setup/teardown, FMA, iport, and target map state.
- HBA lifecycle functions: `scsi_hba_init`, `scsi_hba_fini`, `scsi_hba_attach_setup`, `scsi_hba_detach`, `scsi_hba_tran_alloc`, `scsi_hba_tran_free`.
- Packet helpers: `scsi_hba_pkt_alloc`, `scsi_hba_pkt_free`, `scsi_hba_pkt_comp`.
- Discovery/topology helpers for iports and target maps.
- Flags: `SCSI_HBA_TRAN_*`, `SCSI_HBA_ADDR_SPI`, `SCSI_HBA_ADDR_COMPLEX`, `SCSI_HBA_HBA`, `SCSI_HBA_SCSA_*`.

## Dependencies And Relationships
Kernel-only header relying on DDI/SCSA types, `sys/modctl.h`, `sys/note.h`, and types declared through `scsi_types.h` consumers. It is referenced by `scsi_address.h`, `scsi_resource.h`, and HBA drivers.

## Research Notes
The file documents the transition from legacy SPI addressing and deprecated `SCSI_HBA_TRAN_CLONE` to `SCSI_HBA_ADDR_COMPLEX` and iport/target-map based topology.

## Notable Risks
- `struct scsi_hba_tran` is a kernel ABI-like contract for HBA drivers; field misuse can break packet routing, DMA setup, hotplug, FMA, or MPxIO behavior.
- Minor-node macros reserve framework ranges; HBA private minors must avoid collisions.
- Target-map callbacks can activate/deactivate devices asynchronously, so locking and lifetime ownership matter.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/transport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/types.h

## Purpose
Aggregates implementation-specific SCSI subsystem includes.

## Main Interfaces
- Kernel include wrapper for common kernel, buffer, ioctl, SCSA service, transport, SMP transport, and SAS headers.
- Always includes `sys/scsi/impl/uscsi.h`.

## Dependencies And Relationships
Included by `scsi_types.h` as the final Sun/illumos implementation-specific SCSI layer. Under `_KERNEL`, it pulls in `transport.h`, `smp_transport.h`, and `scsi_sas.h`.

## Research Notes
This header defines no new data structures itself; it centralizes implementation include dependencies.

## Notable Risks
- Because it is pulled into broad SCSI include stacks, adding dependencies here can increase compile coupling across many drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/uscsi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/uscsi.h

## Purpose
Defines the user-level SCSI passthrough ioctl ABI and kernel helper interfaces for translating `uscsi_cmd` requests into SCSI packets.

## Main Interfaces
- `struct uscsi_cmd`: flags, status, timeout, CDB pointer, data buffer, lengths, residuals, request-sense buffer, and path instance.
- 32-bit syscall compatibility structure and conversion macros under `_SYSCALL32`.
- `USCSI_*` flags for read/write, reset, request sense, queue tags, path selection, PM failfast, and legacy parallel SCSI controls.
- `struct uscsi_rqs`, `RQS_OVR`, `RQS_VALID`.
- Ioctls: `USCSICMD`, `USCSIMAXXFER`.
- Kernel helpers: `scsi_uscsi_copyin`, `scsi_uscsi_pktinit`, `scsi_uscsi_handle_cmd`, `scsi_uscsi_pktfini`, copyout/free helpers.

## Dependencies And Relationships
Included by implementation SCSI types and used by target drivers such as disk, tape, generic SCSI, and SES for user passthrough and internal command handling.

## Research Notes
Some flags are explicitly not for user level, including `USCSI_NOINTR`, queue tag controls, and parallel bus controls.

## Notable Risks
- This is a user/kernel ABI; field sizes and 32-bit conversion behavior must remain compatible.
- Passthrough can issue destructive SCSI commands; validation and reserved-bit handling are important.
- `USCSI_PATH_INSTANCE` interacts with MPxIO path selection and must not accidentally pin retries to failed paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/uscsi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/usmp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/usmp.h

## Purpose
Defines the user-level Serial Attached SCSI Management Protocol passthrough ABI.

## Main Interfaces
- `usmp_cmd_t`: request/response pointers, sizes, and timeout.
- 32-bit kernel compatibility structure and conversion macros.
- `USMPFUNC` ioctl.
- SMP request/response minimum and maximum sizes, default timeout, and SAS WWN byte size.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/ioccom.h`, and `sys/scsi/generic/smp_frames.h`. Related to SAS SMP target support and the `smp` target driver.

## Research Notes
The maximum request and response size is 1032 bytes, matching SMP frame payload expectations.

## Notable Risks
- User-provided request and response pointers cross the user/kernel boundary.
- Size checks must enforce the min/max constants to avoid malformed SMP frames.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/usmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi.h

## Purpose
Top-level global include for the illumos SCSI subsystem.

## Main Interfaces
- Includes `sys/scsi/scsi_types.h`.

## Dependencies And Relationships
Acts as the simple public entry point used by SCSI target and HBA headers to pull in the common SCSA include stack.

## Research Notes
No declarations beyond the include wrapper.

## Notable Risks
- Changes to `scsi_types.h` propagate to any consumer including this top-level header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_address.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_address.h

## Purpose
Defines SCSI device addressing for SCSA target and HBA interaction, including legacy SPI addressing, complex unit-address mode, LUN conversion, and WWN string helpers.

## Main Interfaces
- `struct scsi_address`: HBA transport pointer plus SPI target/lun/sublun or complex `scsi_device` pointer.
- Legacy aliases: `a_target`, `a_lun`, `a_sublun`.
- Unit-address property names such as `target`, `lun`, `target-port`, `lun64`, `scsi-iport`, and SAS/SATA port properties.
- `scsi_lun64_t`, `scsi_lun_t`, and SCSI LUN addressing method constants.
- Kernel helpers for LUN conversion and WWN string conversion/freeing.

## Dependencies And Relationships
Includes `sys/scsi/scsi_types.h`. Closely tied to `transport.h` flags `SCSI_HBA_ADDR_SPI`, `SCSI_HBA_ADDR_COMPLEX`, and deprecated `SCSI_HBA_TRAN_CLONE`.

## Research Notes
The file contains important compatibility commentary: `scsi_address` is embedded at the base of `scsi_device` and copied into `scsi_pkt`, constraining structure evolution.

## Notable Risks
- Target drivers should not assume `a_target`/`a_lun` are valid outside SPI-style addressing.
- Unit-address representation is primarily HBA-owned; misuse can break non-SPI transports.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_address.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_ctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_ctl.h

## Purpose
Declares SCSI control operations for capabilities, abort/reset, task management, ACA clearing, and unit-address reporting.

## Main Interfaces
- Reset levels: `RESET_ALL`, `RESET_TARGET`, `RESET_BUS`, `RESET_LUN`.
- Reset notification flags: `SCSI_RESET_NOTIFY`, `SCSI_RESET_CANCEL`.
- `SCSI_MAXNAMELEN`, `SCSI_NO_QUIESCE`.
- Kernel functions: `scsi_ifgetcap`, `scsi_ifsetcap`, `scsi_abort`, `scsi_reset`, `scsi_reset_notify`, `scsi_clear_task_set`, `scsi_terminate_task`, `scsi_clear_aca`, `scsi_ua_get_reportdev`, `scsi_ua_get`.

## Dependencies And Relationships
Includes `sys/scsi/scsi_types.h`. The declared functions route through HBA transport vectors in `scsi_hba_tran`.

## Research Notes
Separates bus reset from broader target/LUN reset levels and documents invocation paths.

## Notable Risks
- Reset and task-management calls can disrupt outstanding I/O and reservations.
- `SCSI_NO_QUIESCE` changes hotplug behavior and should be treated as a policy override.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_ctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_fm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_fm.h

## Purpose
Declares SCSI fault-management initialization, cleanup, and ereport posting helpers.

## Main Interfaces
- `scsi_fm_init(struct scsi_device *)`
- `scsi_fm_fini(struct scsi_device *)`
- `scsi_fm_ereport_post(...)` with device, path, class, ENA, devid, topology, flags, nvlist payload, and variadic payload fields.

## Dependencies And Relationships
Consumed by SCSI devices and target drivers through the kernel SCSI type include stack. Used by disk-driver FMA support in `sddef.h`.

## Research Notes
The comment asks whether init/fini should be done from child init/uninit paths, indicating it is tied to SCSI device lifecycle.

## Notable Risks
- Variadic ereport payloads require strict caller discipline.
- Incorrect path/devid/topology data can reduce fault isolation quality.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_fm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_names.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_names.h

## Purpose
Defines standard SCSI name-string prefixes and maximum string lengths.

## Main Interfaces
- Prefix strings: `SNS_EUI`, `SNS_IQN`, `SNS_MAC`, `SNS_NAA`, `SNS_WWN`.
- Maximum raw lengths for EUI, IQN, MAC, NAA, and WWN.
- Maximum full string lengths: `SNS_EUI_LEN_MAX`, `SNS_IQN_LEN_MAX`, `SNS_MAC_LEN_MAX`, `SNS_NAA_LEN_MAX`, `SNS_WWN_LEN_MAX`, `SNS_LEN_MAX`.

## Dependencies And Relationships
Standalone naming utility header for SCSI identifiers, likely used by iSCSI/SCSI unit-address and device identification code.

## Research Notes
`SNS_LEN_MAX` is set to the IQN maximum, making IQN the limiting name-string length.

## Notable Risks
- The macros using `sizeof (SNS_*)` include the terminating NUL, so callers must understand whether the length is buffer size or string payload length.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_names.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_params.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_params.h

## Purpose
Defines common SCSI sizing parameters for sense keys, tags, targets, and LUN counts.

## Main Interfaces
- `NUM_SENSE_KEYS`
- `NTAGS`
- `NTARGETS`, `NTARGETS_WIDE`, `NLUNS_PER_TARGET`
- LUN count helpers: `SCSI_1LUN_PER_TARGET`, `SCSI_8LUN_PER_TARGET`, `SCSI_16LUNS_PER_TARGET`, `SCSI_32LUNS_PER_TARGET`

## Dependencies And Relationships
Included by `scsi_types.h` and therefore broadly visible to SCSI drivers.

## Research Notes
The target/LUN constants are rooted in parallel SCSI defaults but are still used as general defaults for nexus/target drivers.

## Notable Risks
- Modern transports can exceed legacy target/LUN assumptions; drivers should not hard-code these where transport properties provide real limits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_params.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_pkt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_pkt.h

## Purpose
Defines the SCSI packet structure and packet flags, completion reasons, state bits, statistics, and transport return codes.

## Main Interfaces
- Kernel `struct scsi_pkt`: HBA private data, destination address, target private data, completion callback, flags, timeout, status/CDB pointers, residual, state, statistics, reason, allocation metadata, DMA metadata, path instance, and staging pointer.
- Packet flags: queue tags, head/nointr, parallel bus flags, uscsi flags, TLR, MPxIO noqueue/path-instance flags.
- Completion reasons: `CMD_CMPLT`, `CMD_INCOMPLETE`, DMA/transport/reset/abort/timeout/overrun, parallel SCSI failures, `CMD_DEV_GONE`.
- State and statistics bits.
- Transport returns: `TRAN_ACCEPT`, `TRAN_BUSY`, `TRAN_BADPKT`, `TRAN_FATAL_ERROR`.
- Kernel function `scsi_transport`.

## Dependencies And Relationships
Includes `sys/scsi/scsi_types.h`. Allocated through `scsi_resource.h` and transported through HBA vectors from `transport.h`.

## Research Notes
The file strongly warns that drivers must not depend on `sizeof (struct scsi_pkt)` and should allocate through SCSA packet allocation interfaces.

## Notable Risks
- Access to newer fields is only valid for correctly allocated packets.
- Misinterpreting `pkt_reason`, `pkt_state`, and `pkt_statistics` can cause bad retry or error reporting behavior.
- `FLAG_PKT_PATH_INSTANCE` must be coordinated with `pkt_path_instance` to avoid retrying failed paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_pkt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_resource.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_resource.h

## Purpose
Declares SCSA resource allocation and DMA lifecycle functions for SCSI buffers and packets.

## Main Interfaces
- Allocation callback constants: `NULL_FUNC`, `SLEEP_FUNC`.
- Packet init flags: `PKT_CONSISTENT`, `PKT_DMA_PARTIAL`, `PKT_XARQ`, legacy `PKT_CONSISTENT_OLD`.
- Kernel functions: `scsi_alloc_consistent_buf`, `scsi_init_pkt`, `scsi_destroy_pkt`, `scsi_free_consistent_buf`, `scsi_pkt_allocated_correctly`, `scsi_dmaget`, `scsi_dmafree`, `scsi_sync_pkt`, `scsi_pkt2bp`.
- Private `struct scsi_pkt_cache_wrapper` and flags `PCW_NEED_EXT_CDB`, `PCW_NEED_EXT_TGT`, `PCW_NEED_EXT_SCB`, `PCW_BOUND`.
- Defaults for CDB/private/status lengths and obsolete packet/resource allocators.

## Dependencies And Relationships
Includes `sys/scsi/scsi_types.h`. Works with `struct scsi_pkt` from `scsi_pkt.h` and HBA packet allocation from `transport.h`.

## Research Notes
The wrapper supports cached packet allocation and stores transfer window and DMA cookie state.

## Notable Risks
- Packet/buffer ownership and DMA cleanup must match allocation path.
- Obsolete interfaces remain for compatibility but should not guide new driver design.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_types.h

## Purpose
Central SCSI subsystem type/include aggregator.

## Main Interfaces
- Defines `opaque_t` as `void *` if not already defined.
- Includes base system types and parameters.
- Under `_KERNEL`, includes DDI, devops, sunddi, stat, NDI, and devctl headers.
- Includes SCSI params, address, packet, device config, control, resource, autoconf, watch, FMA, generic command/status/message/mode, and implementation types.

## Dependencies And Relationships
This is the main include stack behind `scsi.h` and most SCSI target/HBA headers.

## Research Notes
It intentionally blends generic SCSI protocol headers with illumos implementation-specific SCSI headers.

## Notable Risks
- Broad include fan-out means changes here can affect many kernel compilation units.
- User-visible and kernel-only portions are interleaved through `_KERNEL` guards.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_watch.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_watch.h

## Purpose
Declares SCSI watch service interfaces for periodic device polling and media monitoring.

## Main Interfaces
- `struct scsi_watch_result`: status, sense, actual sense length, MMC data, and packet.
- `SCSI_WATCH_IO_TIME`
- Termination flags and result constants.
- Functions: `scsi_watch_init`, `scsi_watch_fini`, `scsi_watch_request_submit`, `scsi_mmc_watch_request_submit`, `scsi_watch_request_terminate`, `scsi_watch_get_ref_count`, `scsi_watch_resume`, `scsi_watch_suspend`.

## Dependencies And Relationships
Used by disk and tape target drivers for media state monitoring. Types come through the SCSI include stack.

## Research Notes
Default watch I/O timeout is 120 seconds to support slow devices.

## Notable Risks
- Watch tokens carry lifecycle and reference-count concerns across suspend/resume and detach.
- Termination may be synchronous or asynchronous depending on flags.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_watch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sddef.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sddef.h

## Purpose
Private definition header for the illumos SCSI disk/CD target driver, covering soft-state, open maps, block-size conversion, read-modify-write support, thin provisioning, reservations, FMA telemetry, retry/throttle policy, power management, kstats, CD/DVD quirks, VPD pages, and configuration properties.

## Main Interfaces
- Minor/partition macros: `SDUNIT`, `SDPART`, `MAXPART`, `SD_GET_INSTANCE_FROM_BUF`.
- Open-count structures: `ocinfo`, `ocmap`.
- `struct sd_lun`: main disk soft-state with SCSA device pointer, request-sense resources, I/O queues, block geometry, controller/interconnect data, retry/throttle state, reservations, event callbacks, kstats, flags, PM state, media watch state, RMW state, thin provisioning, block limits, failfast queues, FMA, and CMLB handle.
- Block conversion macros: `SD_BYTES2TGTBLOCKS`, `SD_BYTES2PHYBLOCKS`, `SD_TGTBLOCKS2BYTES`, `SD_SYS2TGTBLOCK`, `SD_TGT2SYSBLOCK`.
- Non-512/RMW structures: `sd_w_map`, `sd_mapblocksize_info`, RMW flags.
- Thin provisioning: `SD_THIN_PROV_ENABLED`, `SD_THIN_PROV_READ_ZEROS`, `sd_blk_limits_t`, `sd_unmapstats_t`.
- Persistent reservation structures and service action constants.
- `struct sd_xbuf`, `struct sd_uscsi_info`, `sd_ssc_t`, FMA assessment enums, `struct sd_fm_internal`.
- Debug/logging, kstat update, retry, throttle, state, power-management, VPD, CD-ROM, and platform partition macros.

## Dependencies And Relationships
Includes `sys/dktp/fdisk.h`, `sys/note.h`, `sys/mhd.h`, and `sys/cmlb.h`, and depends heavily on SCSA, DKIO, CMLB, FMA, kstat, and buffer-layer types included by consumers.

## Research Notes
This file is a dense private map of the `sd` driver’s behavior. It distinguishes system, target, and physical block sizes; supports non-512-byte removable media through RMW; and carries extensive compatibility quirks for SCSI disks and CD/DVD devices.

## Notable Risks
- Block-size conversion and RMW range locking are data-integrity sensitive.
- Reservation/failfast state affects clustered storage correctness.
- `sd_xbuf` layering requires each layer to restore `xb_private` correctly.
- Power-management and watch-token state crosses suspend/resume, media changes, and in-flight I/O.
- Many flags encode historical device quirks; removing or renumbering them can break configured systems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sddef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/ses.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/ses.h

## Purpose
Private header for the SCSI Enclosure Services target driver, including SES/SAF-TE/SEN soft-state, object mapping, command vectors, retries, timeouts, debugging, and common command helpers.

## Main Interfaces
- SAF-TE READ/WRITE BUFFER command IDs.
- Convenience macros for SCSI packet/status/buffer/device access.
- `encvec`: enclosure operation vector for init, enclosure status, and object status get/set.
- `enctyp`: enclosure type enum for SES, SAF-TE, and SEN.
- `encobj`: enclosure object mapping entry.
- `struct ses_softc`: main driver soft-state with type/vector, object map, enclosure status, SCSI device, request sense resources, special buffer, restart timeout, open/suspend/present state, retries, devid, and embedded uscsi/request-sense buffers.
- Debug and retry macros, timeout constants, callback action codes.
- Kernel functions: `ses_log`, `ses_runcmd`, `ses_uscsi_cmd`.

## Dependencies And Relationships
Includes `sys/note.h` and `sys/scsi/targets/sesio.h`. Depends on SCSA, buffer, uscsi, sense, and DDI types supplied by C files/include context.

## Research Notes
The header contains Warlock annotations documenting protection by `scsi_device::sd_mutex` and special-buffer CV ownership.

## Notable Risks
- SES object state and special buffer fields are shared across ioctl and command paths.
- Retry weights intentionally differ for command, busy, and sense cases.
- SAF-TE and SES command semantics coexist in one driver abstraction.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/ses.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sesio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sesio.h

## Purpose
Defines user-facing SES enclosure ioctl structures, element types, status values, and control bits.

## Main Interfaces
- `ses_object`: object id, subenclosure id, element type.
- Enclosure element type constants including device, power, fan, thermal, alarm, SCC, UPS, display, SCSI target/initiator, array, SAS expander, and SAS connector.
- Overall enclosure status bits: unrecoverable, critical, noncritical, info.
- `ses_objarg`: object id and four status/control bytes.
- SES common status constants.
- Control bits for common, device, and generic element control bytes.
- Ioctls: legacy `SESIOC_IOCTL_*` and object/status operations `SESIOC_GETNOBJ`, `SESIOC_GETOBJMAP`, `SESIOC_INIT`, `SESIOC_GETENCSTAT`, `SESIOC_SETENCSTAT`, `SESIOC_GETOBJSTAT`, `SESIOC_SETOBJSTAT`.
- `struct ses_ioctl`: raw page access descriptor.

## Dependencies And Relationships
Included by `ses.h` and consumed by SES applications and driver ioctl handlers.

## Research Notes
This is the ABI boundary for enclosure management applications.

## Notable Risks
- Bitfield layout in `ses_object` is compiler/ABI-sensitive.
- Ioctls can change enclosure element state, including identify/fault/device-off controls.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sesio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sgendef.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sgendef.h

## Purpose
Private header for the generic SCSI target driver, defining ioctls, state, binding database structures, flags, retries, and error statistics.

## Main Interfaces
- Ioctls: `SGEN_IOC_READY`, `SGEN_IOC_DIAG`.
- Kernel diagnostics levels `SGEN_DIAG1` through `SGEN_DIAG3`.
- `struct sgen_errstats`: kstat counters for transport, restart, incomplete, autosense, sense, recoverable, no-sense, and unrecoverable errors.
- `sgen_state_t`: scsi device, uscsi command, command/sense buffers and packets, flags, ARQ, diagnostics, restart timeout, and kstats.
- State macros for open, suspended, busy, and exclusive flags.
- Binding database nodes for inquiry strings and device types.
- Retry/busy timeout and callback action constants.

## Dependencies And Relationships
Includes kernel synchronization, kstat, buf, and `sys/scsi/scsi.h`. Uses `uscsi_cmd` and SCSA packet/sense machinery.

## Research Notes
The driver supports binding by inquiry vendor/product strings or SCSI device type from configuration properties.

## Notable Risks
- Generic SCSI passthrough can expose broad device control.
- Busy/open/exclusive flag macros assume external synchronization by the driver.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/sgendef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/smp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/smp.h

## Purpose
Private target-driver header for SAS SMP devices.

## Main Interfaces
- Open states: `SMP_CLOSED`, `SMP_SOPENED`, `SMP_EXOPENED`.
- `smp_state_t`: SMP device pointer, mutex, open flag, condition variable, and busy flag.
- Soft-state sizing and retry constants.
- Transfer buffer flags: `SMP_FLAG_REQBUF`, `SMP_FLAG_RSPBUF`, `SMP_FLAG_XFER`.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/scsi/scsi.h`; related to the user SMP ioctl ABI in `impl/usmp.h`.

## Research Notes
Kernel-only state is guarded by `_KERNEL`.

## Notable Risks
- Open/busy state must be serialized to prevent overlapping SMP management operations.
- SMP commands can alter or query SAS expander topology.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/smp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/ssddef.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/ssddef.h

## Purpose
Backward-compatibility wrapper for old `ssd` semantics.

## Main Interfaces
- Forces `__fibre` to be defined if absent.
- Includes the real disk target header `sun/sys/scsi/targets/sddef.h`.

## Dependencies And Relationships
Compatibility layer for consumers expecting `ssddef.h`; actual definitions live in `sddef.h`.

## Research Notes
The file says `ssddef.h` is expected to become obsolete.

## Notable Risks
- The include path uses `sun/sys/...`, so build environments must preserve legacy include aliases.
- Defining `__fibre` changes conditional semantics in old consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/ssddef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/stdef.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/stdef.h

## Purpose
Private definition header for the SCSI tape target driver, covering drive types/options, mode pages, density/log/tape-alert data, tape positioning, recovery metadata, soft-state, reservations, timeouts, debug macros, and media/error thresholds.

## Main Interfaces
- Tape drive type constants mapped to `mtio.h` values.
- Stable drive option flags such as variable block, QIC/reel, backspace support, buffered writes, compression, reserve/release behavior, WORM, cleaning bit variants, and valid option mask.
- Log page and TapeAlert constants/enums.
- `struct st_drivetype`: configured drive identity, block size, options, retries, density/media tables, and command timeouts.
- Mode page layouts: compression, device configuration, SAS LUN, sequence mode, report supported operation codes, report density support, read block limits.
- Position types and structures: `tapepos_t`, short/long/extended READ POSITION data, `read_pos_data_t`.
- Command attribute and recovery structures.
- `struct scsi_tape`: main tape soft-state with SCSA device, queues, special buffers, mode data, drive table, position, state, retry/throttle, media state, RQS, reservations, error stats, x86 contiguous memory, recovery taskq, unit attention, multipath, and TLR state.
- Reservation flags and persistent reservation service action constants.
- Timeout/retry constants and SPACE command encoding macros.

## Dependencies And Relationships
Includes DDI, synchronization, kstat, SCSI types, generic sense, `mtio.h`, and taskq headers. Uses `struct scsi_pkt`, `struct uscsi_cmd`, SCSA watch tokens, and tape ioctl/minor semantics.

## Research Notes
The header supports both legacy and logical tape positioning, several bitfield layouts for different host endianness, and a large amount of historical drive behavior compatibility.

## Notable Risks
- Drive option flag values are explicitly stable and must not be renumbered.
- SPACE command encoding depends on `size_t` width.
- Tape position recovery, filemark/EOM state, and WORM/write-protect behavior are correctness sensitive.
- Bitfield protocol structures depend on `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/targets/stdef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda.h

## Purpose
Public SD/MMC/SDIO common framework header for host adapter drivers and SD-card clients.

## Main Interfaces
- SD command indexes `sda_index_t`, including normal commands and application commands.
- Response classes `sda_rtype_t`, including busy variants.
- R1/R5/R7/OCR status and capability bit macros.
- `sda_cmd_t`: command descriptor with index, response type, flags, argument, response words, block counts/sizes, residual, DMA handle/cookie, and kernel address.
- Command flags for read, write, auto CMD12, and private framework state.
- `sda_prop_t`: host/card properties for insertion, write protect, LED, clock, bus width, OCR, capabilities, and high speed.
- `sda_fault_t` and `sda_err_t`.
- `sda_ops_t`: host controller operations for command, get/set property, poll, reset, halt.
- Host lifecycle functions: init/fini ops, alloc/free, attach/detach, suspend/resume, detect, fault, transfer, log.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/note.h`. Implemented by the SD-card framework and used by host controller drivers.

## Research Notes
The header warns that consumers must not depend on `sizeof (struct sda_cmd)`.

## Notable Risks
- Command completion and transfer callbacks must respect private command flags.
- OCR and response bit handling controls card initialization and capability selection.
- Host and client APIs are distinct and should not be mixed outside the framework.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda_impl.h

## Purpose
Private SD-card framework implementation header defining slot/host soft-state and internal command, initialization, memory-card, nexus, and slot-management functions.

## Main Interfaces
- `sda_slot_t` and `struct sda_slot`: per-slot state including host/private pointers, child devinfo, insertion/failure/init/suspend/detect/fault state, OCR/RCA/clock, current transfer, command/abort lists, ops copy, recursive slot lock, event lock/CV, task queues, cfgadm timestamps, parsed CID/CSD/card geometry, write-protect fields, and block-device handle.
- Slot flags: writable, 4-bit, IF_COND, MMC, SD memory, SDIO, SDHC, memory/SD masks.
- Slot capabilities: no PIO, high speed, 4-bit.
- `struct sda_host`: devinfo, slot count/array, DMA attributes, nexus linkage, attach/open flags.
- Property helper macros `sda_setprop`, `sda_getprop`.
- Internal functions for command allocation/submission/completion, card initialization, memory card block-device operations, nexus open/close/ioctl/bus control, slot lifecycle, power, transfer, fault, and logging.

## Dependencies And Relationships
Includes list, synchronization, block-device, DDI/SunDDI, and public `sys/sdcard/sda.h`. Used by the SD-card framework implementation files.

## Research Notes
The slot has two locking domains: recursive slot ownership via `s_lock` and event notification via `s_evlock`.

## Notable Risks
- Slot state transitions cross task queues, hotplug detection, suspend/resume, and transfer completion.
- Duplicate `sda_slot_reset` declarations appear in the prototype list.
- Parsed CID/CSD geometry feeds block-device read/write behavior, so bit extraction and address shift handling are data-path sensitive.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sdcard/sda_impl.h -->