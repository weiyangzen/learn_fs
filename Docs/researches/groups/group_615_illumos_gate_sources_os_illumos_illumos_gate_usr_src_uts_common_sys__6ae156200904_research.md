# Group Research: group_615_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__6ae156200904

Scope: `Docs/research_subset_a.md` includes `sources/os/illumos/illumos-gate`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt.h

This is the primary private header for the illumos `smrt` Smart Array SCSI HBA driver. It ties together controller state, logical/physical device tracking, DMA bookkeeping, command lifecycle flags, SCSA target integration, interrupt setup, discovery, controller reset, and event notification entry points.

Key definitions:
- Requires little-endian and little-to-high bitfield layout at compile time because the driver maps packed controller hardware structures directly.
- Defines global sizing constants: `SMRT_MAX_LOGDRV` as 64 and `SMRT_MAX_PHYSDEV` as 128.
- Defines controller initialization levels, controller status/discovery flags, command tag ranges, iport names, discovery and timeout constants, and HP vendor/device identifiers.
- `struct smrt` is the central per-controller soft state, containing devinfo pointers, config table mappings, SCSA target maps, mutex/condition variables, inflight/finish/abort command lists, discovered volumes/physicals, taskq/periodic handles, interrupt handles, DMA attributes, heartbeat/reset timestamps, and async event command state.
- `smrt_volume_t`, `smrt_physical_t`, and `smrt_target_t` model logical volumes, physical devices, and SCSA targets.
- `smrt_command_t` tracks controller command tags, type/status flags, target/controller ownership, AVL/list membership, submit/complete/expiry timestamps, abort metadata, optional SCSA/internal payloads, and DMA-backed CISS command/error buffers.
- Declares the driver’s main internal API for transport submission, interrupts, controller init/reset, discovery, SCSA HBA setup, command allocation/reuse, CISS message construction, device MMIO access, SATA WWN probing, and async event handling.

Dependencies:
- Includes the CISS and Smart Array SCSI wire-format headers: `smrt_ciss.h` and `smrt_scsi.h`.
- Depends heavily on illumos kernel DDI/SCSA types, list/AVL primitives, task queues, periodic callbacks, DMA handles, and SCSI packet/device types.

Impact:
- This header is the main contract between all `smrt` driver implementation files.
- Changes here can affect command lifetime, reset behavior, hotplug discovery, panic-time behavior, and target exposure.

Cautions:
- Command status flags encode subtle lifecycle states: polled completion, abandoned commands, reset-sent commands, abort-sent commands, and commands allowed while the controller is not fully running.
- Most controller state is protected by `smrt_mutex`; users must preserve the locking expectations described in comments.
- Hardware layout and bitfield ordering assumptions are explicit and non-portable outside little-endian systems.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt_ciss.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt_ciss.h

This header defines CISS transport constants and packed controller command/data structures for the `smrt` driver.

Key definitions:
- Defines CISS limits: `CISS_MAXSGENTRIES`, fallback scatter/gather count, and fixed 16-byte CDB length.
- Defines CISS command completion status values, transfer direction values, request attributes, and request type values.
- Defines I2O register offsets used by Smart Array controllers, including inbound/outbound post queues, interrupt registers, scratchpad, and configuration table offsets.
- Defines interrupt, doorbell, scratchpad, configuration table, and simple transport helper macros.
- `smrt_tag_t` models completion tags with reserved/error/tag-value fields.
- `SCSI3Addr_t`, `PhysDevAddr_t`, `LogDevAddr_t`, and `LUNAddr_t` model the controller’s LUN address encodings.
- `CommandList_t` is the packed controller command block with header, request block, error descriptor, and static scatter/gather descriptor array.
- `ErrorInfo_t` and `MoreErrInfo_t` describe controller error completions and embedded sense data.
- `CfgTable_t` describes the controller configuration table used to negotiate transport mode and discover controller limits.

Dependencies:
- Uses `MAX_SENSE_LENGTH`, supplied by SCSI implementation sense definitions through the broader include graph.
- Consumed directly by `smrt.h` and `smrt_scsi.h`.

Impact:
- This is a hardware ABI header. Structure layout, packing, field widths, and register constants must match controller firmware behavior.

Cautions:
- The file uses `#pragma pack(1)` around wire structures.
- Several structures contain C bitfields mapped to device-defined byte layouts, so compiler and endian assumptions matter.
- The controller command list statically allocates 64 scatter/gather entries for every command, influencing memory footprint.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt_ciss.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt_scsi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt_scsi.h

This header defines Smart Array vendor-specific SCSI, CISS message, BMIC command, discovery, physical drive, and async event payload structures.

Key definitions:
- Defines CISS LUN addressing mode constants for physical devices and logical volumes.
- Defines vendor-specific CISS SCSI opcodes for read/write and reporting logical or physical LUNs.
- Defines BMIC read/write opcodes and Smart Array BMIC command IDs for identifying controllers, identifying physical devices, and event notification.
- Defines device/PHY type codes for pSCSI, SATA, SAS, expander, SES, controller, SGPIO, NVMe, and no-phy cases.
- Packed request/response structures cover:
  - `REPORT LOGICAL LUNS`
  - `REPORT PHYSICAL LUNS`
  - physical extended data variants for physical node identifiers and other physical device info
  - `IDENTIFY CONTROLLER`
  - `IDENTIFY PHYSICAL DEVICE`
  - CISS event notification request/response records
- Defines event classes/subclasses for protocol errors, hotplug, hardware/environment events, physical device state, and logical volumes.

Dependencies:
- Includes `smrt_ciss.h` for `LogDevAddr_t`, `PhysDevAddr_t`, and `LUNAddr_t`.
- Requires `SMRT_MAX_LOGDRV` and `SMRT_MAX_PHYSDEV`, which are defined by `smrt.h` before this header is included in the normal driver include path.

Impact:
- This is the driver’s command payload catalog for Smart Array firmware management commands.
- Discovery, event handling, physical device support, and SATA/SAS identification depend on these structures.

Cautions:
- Several multi-byte fields are explicitly noted as big-endian inside otherwise packed controller payloads.
- `smrt_identify_physical_drive_t` is large and firmware-version-sensitive; not every field is valid for every controller generation.
- Event notification requires a 512-byte buffer even though the exposed structure is shorter.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/smrt/smrt_scsi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/conf/autoconf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/conf/autoconf.h

This header defines SCSI subsystem autoconfiguration knobs, probe result codes, reset/selection defaults, and kernel-global SCSI configuration variables.

Key definitions:
- `SCSI_DEBUG_*` flags distinguish target-driver, library, and host-adapter debug categories.
- `SCSI_OPTIONS_*` flags configure global SCSI behavior including linked commands, tagged queueing, disconnect/reconnect, synchronous transfer, parity, FAST/WIDE/FAST20/40/80/160/320, QAS, and maximum LUN limits.
- Documents `scsi_slave()` and `scsi_probe()` behavior and their return codes.
- Defines `SCSIPROBE_*` status values and an ASCII mapping macro.
- Defines defaults for reset delay and selection timeout.
- Defines `scsi_enumeration` flags for enabling dynamic enumeration and disabling target/LUN multithreading.
- Declares kernel globals: `scsi_options`, `scsi_enumeration`, `scsi_reset_delay`, `scsi_tag_age_limit`, `scsi_watchdog_tick`, `scsi_selection_timeout`, `scsi_host_id`, and `scsi_fm_capable`.

Dependencies:
- Pure SCSI configuration header, no direct includes in the file.
- Kernel variable declarations are gated by `_KERNEL`.

Impact:
- These flags shape SCSA bus probing, target enumeration, legacy parallel SCSI negotiation, and default timeout behavior.

Cautions:
- Comments describe historical SPI behavior and legacy probing paths; many options are meaningful primarily for parallel SCSI.
- Enumeration multithreading is explicitly tied to HBA locking robustness and buggy-HBA compatibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/conf/autoconf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/conf/device.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/conf/device.h

This header defines `struct scsi_device`, the SCSA target/lun/sfunc device representation used by target drivers and HBA nexus code.

Key definitions:
- `struct scsi_device` contains:
  - `sd_address` routing information and transport pointer
  - `sd_dev` devinfo pointer
  - target driver mutex
  - HBA-private and target-private pointers
  - inquiry and request sense pointers
  - FMA capability state
  - optional MPxIO pathinfo pointer
  - flags preventing uninitialization or duplicate `tran_tgt_free`
  - `sd_tran_safe`, a compatibility hack for older non-SCSA direct-access drivers
- Declares public kernel interfaces `scsi_probe()` and `scsi_unprobe()`.
- Declares private property access/update/remove/free helpers for device/path properties.
- Declares `SCSI_HBA_ADDR_COMPLEX` helper interfaces: `scsi_address_device()`, `scsi_device_hba_private_set()`, and `scsi_device_hba_private_get()`.
- Declares obsolete `scsi_slave()` and `scsi_unslave()`.

Dependencies:
- Includes `sys/scsi/scsi_types.h`.
- Uses kernel types such as `dev_info_t`, `kmutex_t`, `scsi_address`, and `scsi_hba_tran`.

Impact:
- This is a central SCSA ABI/API structure for target drivers.
- It documents how device private data, HBA private data, inquiry data, and MPxIO path properties are associated with target device nodes.

Cautions:
- The structure has historical compatibility fields and warnings about older `SCSI_HBA_TRAN_CLONE` and direct-access drivers overwriting transport vectors.
- The optional `SCSI_SIZE_CLEAN_VERIFY` padding exists to detect driver dependencies on structure size.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/conf/device.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/commands.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/commands.h

This generic SCSI header defines standard command opcodes, CDB group sizing, service action constants, MMC event constants, and command-name mappings.

Key definitions:
- Defines CDB group ID extraction and expected CDB lengths for command groups 0, 1, 2, 4, and 5.
- Defines SCSI command opcodes for common, direct-access, sequential-access, printer, processor, WORM, read-only, MMC, variable-length, persistent reservation, security protocol, maintenance, and service-action commands.
- Includes read/write variants for 6-byte, 10-byte, 12-byte, and 16-byte command formats.
- Defines service actions for read capacity/read long/write long, target port groups, supported operations/management, timestamps, device identifiers, priorities, and media serial.
- Defines `SCSI_CMDS_KEY_STRINGS`, a large opcode-to-string initializer used by decoding/logging helpers.
- Includes generic inquiry and sense definitions, then implementation-specific command definitions.

Dependencies:
- Includes `generic/inquiry.h`, `generic/sense.h`, and `impl/commands.h`.

Impact:
- This is the generic opcode namespace used throughout SCSA and SCSI target/HBA drivers.
- The command string macro feeds diagnostics and error reporting.

Cautions:
- Some opcodes overlap by device type, and the string mapping intentionally combines aliases.
- `ATAPI_CAPABILITIES` is explicitly noted as not being a command code and not belonging in this file.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/commands.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/dad_mode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/dad_mode.h

This header defines direct-access device mode sense/select constants and selected direct-access mode page layouts.

Key definitions:
- Defines direct-access mode header device-specific bits: write protect and DPO/FUA support.
- Defines medium type constants for direct-access/floppy-like media.
- Defines direct-access mode page codes for error recovery, format, geometry, flexible disk, verify error recovery, caching, media types, notch/partition, and power condition.
- Defines structures:
  - `mode_err_recov` for SCSI-2/3 error recovery parameters
  - `mode_format` for format parameters
  - `mode_geometry` for rigid disk drive geometry
  - `mode_cache_scsi3` for SCSI-3 caching parameters
- Defines page length constants and rotational position locking values.

Dependencies:
- Uses `struct mode_page` from `generic/mode.h`; this header is normally included by that file after `mode_page` is defined.

Impact:
- Target drivers and disk code use these structures to parse and build MODE SENSE/MODE SELECT payloads for direct-access devices.

Cautions:
- The structures use endian-dependent bitfield branches.
- Comments note incompatibilities with older SCSI/CCS variants defined in `impl/mode.h`; callers must distinguish by returned page length.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/dad_mode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/inquiry.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/inquiry.h

This header defines standard SCSI INQUIRY data layout, device type constants, qualifier/response-format constants, VPD header/descriptor structures, and power-management capability property bits.

Key definitions:
- `struct scsi_inquiry` models standard inquiry data with separate bitfield layouts for little-to-high and high-to-little systems.
- The structure covers peripheral device type/qualifier, removable bit, version fields, response data format, feature bits, vendor/product/revision IDs, serial/reserved area, SPI-3 byte 56 fields, version descriptors, and padding to 132 bytes.
- Defines peripheral device type constants such as direct, sequential, printer, processor, WORM, optical, changer, array controller, enclosure services, RBC, OSD, ADC, well-known, unknown, and mask values.
- Defines device qualifier values and `DTYPE_NOTPRESENT`.
- Defines response data format constants through SPC-4.
- Defines TPGS failover mode constants.
- Defines VPD page header and identification descriptor structures.
- Defines `pm-capable` property bit masks for SCSI power-management/logging capabilities.
- Includes implementation-specific inquiry additions.

Dependencies:
- Includes `impl/inquiry.h` at the end.

Impact:
- This is the canonical SCSA structure for standard inquiry data and device identification.
- It feeds target-driver attach decisions, diagnostic naming, property generation, and multipath/device identity logic.

Cautions:
- The file contains many deprecated/obsolete SPC fields that are preserved for ABI/source compatibility.
- Driver code must mask `inq_dtype` with `DTYPE_MASK` when checking device type because qualifier bits share the byte.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/inquiry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/message.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/message.h

This header defines parallel SCSI message byte constants and helper macros for classifying message lengths/types.

Key definitions:
- Defines fixed one-byte messages such as command complete, save/restore data pointer, disconnect, initiator error, abort, reject, nop, parity error, linked complete, device reset, abort tag, clear queue, ACA, and LUN reset.
- Defines extended message constants for synchronous negotiation, wide transfer, identify extended, and parallel protocol.
- Defines parallel protocol optional flags for IU, DT, and QAS.
- Defines fixed two-byte queue tag messages.
- Defines identify-message masks and legacy pre-SCSI-3 LUN/target-routine fields.
- Provides `IS_IDENTIFY_MSG`, `IS_IDENTIFY_MSG_SCSI3`, `IS_EXTENDED_MSG`, `IS_2BYTE_MSG`, and `IS_1BYTE_MSG`.

Dependencies:
- No external includes in the file.

Impact:
- Used by legacy/parallel SCSI transport code to parse and emit message phases.

Cautions:
- Several definitions are explicitly pre-SCSI-3 only; SCSI-3 users should use the SCSI-3 identify helper.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/message.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/mode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/mode.h

This generic SCSI header defines common MODE SENSE/MODE SELECT headers, block descriptors, mode page headers, mode page constants, and common mode page structures.

Key definitions:
- Defines 6-byte and 10-byte mode parameter headers.
- Defines block descriptors and macros to locate block descriptors and mode pages inside a mode response.
- Defines common `struct mode_page` with endian-dependent page code/saveable bitfields.
- Defines page-control values for current/changeable/default/saved pages.
- Defines common mode page codes, including disconnect/reconnect, format, geometry, caching, peripheral device, control mode, power condition, informational exceptions, and all pages.
- Defines structures for:
  - disconnect/reconnect page
  - generic caching page
  - peripheral device page
  - SCSI-3 control mode page
  - informational exceptions page
  - power condition page
  - log parameter control
  - start/stop cycle counter log
- Includes direct-access device mode definitions and implementation-specific mode variants.

Dependencies:
- Includes `generic/dad_mode.h` and `impl/mode.h`.

Impact:
- This is the common mode-page parsing/building contract for target drivers.
- It bridges standard mode pages and illumos implementation-specific legacy forms.

Cautions:
- Pointer arithmetic macros assume well-formed buffer layout and caller-provided type correctness.
- Several structures use endian-dependent bitfields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/mode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/persist.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/persist.h

This header defines SCSI persistent reservation command constants and wire-format structures for Persistent Reserve In/Out and related TransportID data.

Key definitions:
- Defines Persistent Reserve In service actions: read keys, read reservation, report capabilities, and read full status.
- Defines persistent reservation scope and type codes.
- Defines Persistent Reserve Out service actions: register, reserve, release, clear, preempt, preempt-abort, register-and-ignore-existing-key, and register-move.
- Defines TransportID sizes and protocol-related constants for FC, SPI, SBP, SRP, and iSCSI.
- Defines endian-variant structures for:
  - PR IN CDB
  - read reservation/key response descriptors
  - reservation type capability bits
  - report capabilities response
  - generic/FC/iSCSI/SRP TransportID forms
  - read full status descriptors
  - PR OUT CDB
  - PR OUT parameter lists
  - register-and-move parameter list

Dependencies:
- Uses standard integer types and bitfield order macros from the surrounding illumos environment.

Impact:
- Used by storage stack components implementing reservations, clustering, fencing, and multipath coordination.

Cautions:
- Many structures use trailing single-element arrays for variable-length payloads.
- Multi-byte fields are wire-format byte arrays rather than host-order integers in many structures.
- Correct bitfield interpretation depends on `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/persist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sas.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sas.h

This header defines simplified common SAS address frame, open address frame, SSP command/response IU, link-rate, protocol, and task-management constants.

Key definitions:
- Defines `sas_identify_af_t` and `sas_open_af_t` for SAS address frames, excluding trailing CRC.
- Defines SAS address frame type, device type, protocol, support, connection rate, SATA support, and attached-name offset constants.
- Defines `sas_ssp_cmd_iu_t` for SSP command information units and `sas_ssp_rsp_iu_t` for SSP response information units.
- Defines task attributes, response data presence values, response/TMF result codes, task management function codes, PHY number limits, and maximum SMP payload size.

Dependencies:
- Includes `sys/sysmacros.h` for `DECL_BITFIELD*` helpers.

Impact:
- Provides shared SAS protocol structures for HBA/SAS code without pulling in the full SMP frame catalog.

Cautions:
- Comments note the definitions are simplified/reduced from SAS-2 material.
- Structures include variable trailing payloads and exclude CRC where noted.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sas.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sense.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sense.h

This header defines standard SCSI sense data structures, sense key constants, descriptor-format sense headers/descriptors, descriptor type constants, and includes implementation-specific sense helpers.

Key definitions:
- Defines legacy non-extended `struct scsi_sense`.
- Defines fixed-format `struct scsi_extended_sense` and constants for fixed/deferred/descriptor/vendor-specific sense formats.
- Provides `SCSI_IS_DESCR_SENSE()` helper.
- Defines standard sense key constants from no sense through reserved.
- Defines descriptor-format sense header and descriptor structures for:
  - information
  - command-specific information
  - sense-key-specific data
  - FRU
  - stream commands
  - block commands
  - ATA status return
  - vendor-specific data
- Defines descriptor type constants.
- Includes implementation-specific sense definitions.

Dependencies:
- Includes `impl/sense.h` at the end.
- Uses endian-dependent bitfield branches.

Impact:
- Central to SCSI error interpretation and auto-request-sense handling.
- Used by diagnostic, retry, block/tape, and HBA code.

Cautions:
- Fixed-format and descriptor-format sense must be detected before parsing.
- Variable-length descriptor data requires caller length validation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sense.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sff_frames.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sff_frames.h

This header defines SFF-8485 GPIO-over-SMP frame formats and register structures.

Key definitions:
- Defines SFF request and response frame headers, distinct from generic SAS SMP frame formats.
- Defines GPIO register type and configuration register index enums.
- Defines packed structures for GPIO configuration registers, receive registers, transmit registers, general-purpose receive/transmit config registers, and register arrays.
- Defines drive error, locate, and activity LED/control enums.
- Defines read GPIO register request/response and write GPIO register request payloads.

Dependencies:
- Includes `sys/sysmacros.h` for `DECL_BITFIELD*`.
- Uses `#pragma pack(1)` for wire/register layouts.

Impact:
- Supports enclosure/backplane GPIO access for SFF-8485 devices, such as drive activity/error/locate signaling.

Cautions:
- The response typedef for `sff_read_gpio_resp` is named `smp_response_frame_t`, which can be confusing because generic SMP frames also define a type with that name in another header.
- GPIO GP register arrays are explicitly little-endian.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sff_frames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/smp_frames.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/smp_frames.h

This large header defines SAS-1.1/SAS-2 SMP frame constants and packed request/response structures for expander management.

Key definitions:
- Defines SMP frame types, function codes, and result codes.
- Defines packed generic request/response frame headers and CRC size/minimum length helpers.
- Defines request/response structures for many SAS-2 SMP functions, including:
  - Report General
  - Report Manufacturer Information
  - Report Self Configuration Status
  - Report Zone Permission Table
  - Report Zone Manager Password
  - Report Broadcast
  - Discover
  - Report PHY Error Log
  - Report PHY SATA
  - Report Route Information
  - Report PHY Event
  - Discover List
  - Report PHY Event List
  - Report Expander Route Table List
  - Configure General
  - Enable/Disable Zoning
  - Zoned Broadcast
  - Zone Lock/Activate/Unlock
  - Configure Zone Manager Password
  - Configure Zone PHY Information
  - Configure Zone Permission Table
  - Configure Route Information
  - PHY Control
  - PHY Test Function
  - Configure PHY Event
- Defines enums and helpers for zone group counts, report types, broadcast types, link rates, device types, routing attributes, PHY event sources, zoning save modes, zoning enable operations, PHY operations, and PHY test functions.
- Defines bitmap helpers for 128/256-zone permission descriptors and route PHY bitmaps.

Dependencies:
- Includes `sys/sysmacros.h` for `DECL_BITFIELD*`.
- Uses `#pragma pack(1)` for frame layouts.

Impact:
- This is the core SMP wire-format catalog for SAS expander discovery, topology inspection, zoning, route management, PHY diagnostics, and PHY control.

Cautions:
- Many structures use trailing one-element arrays for variable-length descriptor lists.
- The macro `SMP_DISCOVER_RESP()` compares against `SMP_FUNCTION_ACCEPTED`, while the enum defines `SMP_RES_FUNCTION_ACCEPTED`; this visible mismatch may depend on another compatibility define elsewhere or may be a latent typo.
- Multi-byte protocol fields are represented as integer types in packed structures, so caller code must still handle SAS/SMP byte ordering correctly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/smp_frames.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/status.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/status.h

This header defines SCSI status byte layout, auto-request-sense status layout, and status code masks/constants.

Key definitions:
- `struct scsi_status` maps the one-byte SCSI status block into endian-dependent bitfields for check condition, condition met, busy, intermediate status, SCSI-2 modifier, and vendor/reserved bits.
- `struct scsi_arq_status` combines original command status, request-sense packet status/reason/residue/state/statistics, and embedded extended sense data.
- Defines `SECMDS_STATUS_SIZE`.
- Defines byte-level status constants such as good, check, met, busy, intermediate, reservation conflict, terminated, queue full, ACA active, and task abort.
- Includes implementation-specific status deviations.

Dependencies:
- Uses `struct scsi_extended_sense` from generic sense definitions.
- Includes `sys/scsi/impl/status.h`.

Impact:
- Used by SCSA packet completion and error handling, especially when auto-request-sense is enabled.

Cautions:
- Status bitfields are compiler/bit-order dependent; byte masks are safer for raw status values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/status.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/commands.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/commands.h

This implementation-specific command header defines `union scsi_cdb`, CDB field aliases, big-endian unaligned read/write helpers, command-forming macros, direct-access defect/capacity structures, and kernel command setup functions.

Key definitions:
- Defines `SCSI_CDB_SIZE` as group 4 size and keeps deprecated `CDB_SIZE`.
- `union scsi_cdb` overlays CDBs as:
  - generic opaque byte array
  - word array
  - common command/lun/tag fields
  - group 0, group 1/2, group 4, and group 5 structured layouts
- Provides numerous field alias macros for legacy accessors.
- Provides `SCSI_READ16/24/32/40/48/64` and `SCSI_WRITE16/24/32/40/48/64` macros for unaligned big-endian protocol fields.
- Provides CDB field construction/extraction macros for group 0/1/4/5 addresses and counts.
- Provides legacy `MAKECOM_*` packet/CDB construction macros.
- Defines format/defect list structures and capacity structures including 16-byte read capacity response.
- Declares kernel helper functions `makecom_*` and `scsi_setup_cdb()`.

Dependencies:
- Included by `generic/commands.h`.
- Relies on command group constants from the generic command header include order.

Impact:
- This is a foundational SCSA command construction API.
- Its macros influence many target and HBA drivers that build CDBs directly.

Cautions:
- Many macros expand to comma expressions or multiple assignments and must be used carefully in statement contexts.
- Legacy `MAKECOM_*` macros are pre-SCSI-3 and comments recommend `scsi_setup_cdb()`.
- `SCSI_WRITE48` appears inconsistent: the macro parameter list names `Sr40_Val`, while the body references `Sr48_Val` in the high 32-bit expression and `Sr40_Val` in the low 16-bit expression. This should be treated cautiously by any consumer or refactor.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/commands.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/inquiry.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/inquiry.h

This implementation-specific inquiry header defines illumos/Sun inquiry sizing and property-name conventions.

Key definitions:
- Defines `SUN_MIN_INQLEN` as the minimum useful inquiry length through the RDF field.
- Defines `SUN_INQSIZE` as `sizeof (struct scsi_inquiry)`.
- Defines inquiry property names:
  - `inquiry-device-type`
  - `inquiry-vendor-id`
  - `inquiry-product-id`
  - `inquiry-revision-id`
  - `inquiry-serial-no`
- Declares kernel helper `scsi_ascii_inquiry_len()`.

Dependencies:
- Included by `generic/inquiry.h`, after `struct scsi_inquiry` is defined.

Impact:
- Provides the property bridge between raw SCSI inquiry data and devinfo/HBA target properties.

Cautions:
- Comments note property values may be richer than the raw fixed-width inquiry fields, especially for SATA revision strings and serial/capacity values obtained outside standard inquiry bytes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/inquiry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/mode.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/mode.h

This implementation-specific mode header defines legacy and vendor-specific mode sense/select variants.

Key definitions:
- Defines `modeheader_seq` for sequential-access mode headers.
- Defines CCS-era direct-access error recovery page `mode_err_recov_ccs`.
- Maps `_reserved_ins` to `ins` for CCS format-page compatibility.
- Defines SCSI-2 cache page `mode_cache` and CCS cache page `mode_cache_ccs`.
- Defines older SCSI-2 control page `mode_control`.
- Defines Emulex MD21 vendor-unique format parameters.
- Defines CD-ROM speed mode page constant and `mode_speed`.

Dependencies:
- Included by `generic/mode.h`, relying on prior definitions of `struct mode_page` and `struct block_descriptor`.

Impact:
- Preserves compatibility with older device mode-page formats and vendor-specific direct-access hardware.

Cautions:
- Multiple structures are explicitly incompatible with newer generic versions; consumers must use returned mode-page length/version to select the correct layout.
- Contains legacy hardware-specific definitions that should not be generalized to modern devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/mode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/scsi_reset_notify.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/scsi_reset_notify.h

This header defines SCSI HBA reset notification registration state and helper prototypes.

Key definitions:
- `struct scsi_reset_notify_entry` stores:
  - target `scsi_address`
  - callback function
  - callback argument
  - next-list pointer
- Lock lint annotation states entries are protected by the lock passed as an argument.
- Declares kernel helpers:
  - `scsi_hba_reset_notify_setup()`
  - `scsi_hba_reset_notify_tear_down()`
  - `scsi_hba_reset_notify_callback()`

Dependencies:
- Includes `sys/note.h` and `sys/scsi/scsi_types.h`.

Impact:
- Used by adapter drivers to maintain target-driver reset notification callback lists.

Cautions:
- Correct use depends on callers passing and holding the intended mutex during list manipulation/callback flow.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/scsi_reset_notify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/scsi_sas.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/scsi_sas.h

This header defines illumos SAS implementation interfaces, SAS PHY mapping helpers, kstat structures, protocol/link-rate constants, phy-info property names, phy-mask/depth property names, and SAS event strings.

Key definitions:
- Kernel-only phymap API:
  - create/destroy a SAS phymap
  - add/remove PHY mappings
  - look up unit addresses and private data
  - convert PHY to unit address and unit address to physical iterator
- Defines SAS PHY kstat class and documents kstat name formatting.
- Defines kstat structures for SAS port protocol stats, port stats, and PHY stats.
- Defines supported protocol bits for SSP, STP, SMP, and SATA.
- Defines SAS negotiated physical link-rate constants.
- Defines `phy-info` property names for phy ID and min/max/current link rates.
- Defines target/attached/receptacle phy-mask property names and target-port depth property.
- Defines sysevent class/subclass/type/payload strings for SAS HBA broadcasts and PHY events.

Dependencies:
- Includes `sys/types.h` and `sys/scsi/impl/usmp.h`.
- Kernel phymap APIs are gated by `_KERNEL`.

Impact:
- This is the SCSA/SAS implementation-facing header for topology mapping, stats export, properties, and event publication.

Cautions:
- Phymap callbacks return and manage unit-address private data; lifetime rules need to be followed by HBA/iport drivers.
- Link-rate values mirror SAS-2 definitions but are exposed as illumos property constants.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/scsi_sas.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/sense.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/sense.h

This implementation-specific sense header defines illumos pseudo sense keys, sense buffer sizing constants, legacy Emulex aliases, descriptor templates, and format-neutral sense parsing prototypes.

Key definitions:
- Defines Sun pseudo sense keys for driver-detected fatal errors, timeouts, EOF/EOT/BOT, length errors, and wrong media.
- Defines `NUM_IMPL_SENSE_KEYS`, `SENSE_LENGTH`, `MAX_SENSE_LENGTH`, and `SUN_MIN_SENSE_LENGTH`.
- Provides legacy aliases for Emulex controller-specific extended sense fields.
- Defines `struct scsi_descr_template`.
- Declares descriptor-format helper `scsi_find_sense_descr()`.
- Declares format-neutral helpers for sense key, ASC, ASCQ, information, command-specific information, extended sense field access, and validation.
- Defines validation return codes and flags for unusable/fixed/descriptor sense, buffer overflow, and deferred sense.

Dependencies:
- Included by `generic/sense.h` after standard sense structures are defined.

Impact:
- Provides the implementation helper layer used by code that wants to parse fixed and descriptor sense without duplicating format checks.

Cautions:
- Pseudo sense keys exceed legal standard SCSI sense key values by design.
- Callers should validate buffer length/format before interpreting optional fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/sense.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/services.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/services.h

This header declares implementation services for SCSI polling, packet allocation, name decoding, error reporting, logging, capability string tables, and interconnect type constants.

Key definitions:
- Defines `scsi_key_strings` and `scsi_asq_key_strings` lookup table structures.
- Declares packet helpers `scsi_poll()`, `get_pktiopb()`, and `free_pktiopb()`.
- Declares string/decoder helpers for device type, completion reason, message, command, sense key, extended sense key, and ASC/ASCQ.
- Declares generic and vendor-unique SCSI error message functions.
- Declares `scsi_log()` with printf-like checking.
- Declares global `scsi_state_bits` and `sense_keys`.
- Defines SCSI error severity constants.
- Defines SCSI capability indexes and `SCSI_CAP_ASCII`.
- Defines SCSI version constants.
- Defines interconnect type constants and strings for SPI, Fibre, 1394, SSA, fabric, USB, ATAPI, iSCSI, IB/SRP, SATA, and SAS.
- Defines compatibility alias `scsi_cmd_decode`.

Dependencies:
- Kernel-only content is gated by `_KERNEL`.
- Depends on sense-key counts from the sense headers and SCSA packet/device types from the include context.

Impact:
- This is the common diagnostics and capability support surface for SCSI framework and drivers.

Cautions:
- Capability arrays are index-sensitive; additions must update indexes, ASCII mapping, and maximum values consistently.
- Error reporting APIs accept driver-supplied command/ASC tables and FRU decoders, so callers control part of diagnostic interpretation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/services.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/smp_transport.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/smp_transport.h

This header defines the kernel SMP transport abstraction for SAS expander/SMP devices.

Key definitions:
- Defines SMP device properties: `smp-device`, `smp-wwn`, and `report-manufacturer`.
- Defines `smp_address_t` containing expander WWN and transport vector.
- Defines `smp_device_t` containing SMP address, devinfo pointer, HBA-private pointer, and target-private pointer.
- Defines `smp_pkt_t` with request/response buffers and sizes, timeout, errno-style completion reason, and retry indication.
- Defines `smp_hba_tran` transport vector with HBA private data and `init`, `free`, and `start` callbacks.
- Declares HBA/iport setup and teardown APIs.
- Declares target/framework APIs `smp_probe()` and `smp_transport()`.
- Declares private SMP device property get/lookup/update/remove/free helpers.

Dependencies:
- Includes `sys/types.h` and `sys/scsi/impl/usmp.h`.
- Kernel content is gated by `_KERNEL`.

Impact:
- Provides the transport/framework bridge for issuing SMP requests to SAS expanders and managing SMP child devices.

Cautions:
- `smp_pkt_reason` is described as a code from `errno.h`, not an SMP result code.
- Property helper flags are simplified compared with `scsi_device` property helpers and only model device-node properties.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/smp_transport.h -->