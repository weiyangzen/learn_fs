# Group Research: group_613_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__cd29ce748cac

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_ioc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_ioc.h

## Purpose
Defines the Fusion-MPT MPI v2 IOC, port, event, firmware download/upload, image-header, power-management, and MPI v2.6 IO Unit Control wire formats. This is a vendor ABI header for SAS/SCSI/NVMe-capable LSI/Avago/Broadcom controllers, not normal illumos driver logic.

## Main Interfaces
- IOC initialization:
  - `MPI2_IOC_INIT_REQUEST`, `MPI2_IOC_INIT_REPLY`
  - `MPI2_IOC_INIT_RDPQ_ARRAY_ENTRY`
  - who-initialized values, version masks, RDPQ array mode, reply queue depth minimum, and MPI v2.6 NVMe SGL format flag.
- Controller/port discovery:
  - `MPI2_IOC_FACTS_REQUEST`, `MPI2_IOC_FACTS_REPLY`
  - `MPI2_PORT_FACTS_REQUEST`, `MPI2_PORT_FACTS_REPLY`
  - `MPI2_PORT_ENABLE_REQUEST`, `MPI2_PORT_ENABLE_REPLY`
  - IOC exception bits, protocol flags, capability bits, product-family references, and SAS/FC/iSCSI/tri-mode port types.
- Event framework:
  - `MPI2_EVENT_NOTIFICATION_REQUEST`, `MPI2_EVENT_NOTIFICATION_REPLY`
  - `MPI2_EVENT_ACK_REQUEST`, `MPI2_EVENT_ACK_REPLY`
  - event numbers for log/state/reset, SAS device/initiator/topology/enclosure, integrated RAID, GPIO, quiesce, notify primitives, temperature, host messages, power changes, PCIe/NVMe topology, PCIe link counters, and active cable exceptions.
- Event data structures:
  - log-entry, GPIO, temperature, host-message, power-performance, active-cable, hard-reset, task-set-full, SAS device status, IR operation, IR volume, IR physical disk, IR configuration change list, SAS discovery, SAS broadcast/notify primitives, SAS initiator/table overflow, SAS topology, enclosure, SAS PHY counter, SAS quiesce, host-based discovery PHY, PCIe device status, PCIe enumeration, PCIe topology, and PCIe link counter payloads.
- Firmware transfer and image metadata:
  - `MPI2_FW_DOWNLOAD_REQUEST`, `MPI25_FW_DOWNLOAD_REQUEST`, `MPI2_FW_DOWNLOAD_REPLY`
  - `MPI2_FW_UPLOAD_REQUEST`, `MPI25_FW_UPLOAD_REQUEST`, `MPI2_FW_UPLOAD_REPLY`
  - transaction-context SGEs for upload/download
  - `MPI2_FW_IMAGE_HEADER`, `MPI2_EXT_IMAGE_HEADER`, flash layout data, supported-device image data, init-image footer, and MPI v2.5 encrypted hash data.
- Power and control messages:
  - `MPI2_PWR_MGMT_CONTROL_REQUEST`, `MPI2_PWR_MGMT_CONTROL_REPLY`
  - `MPI26_IOUNIT_CONTROL_REQUEST`, `MPI26_IOUNIT_CONTROL_REPLY`
  - operations for persistent mapping cleanup, SAS link resets, error-log clearing, primitive send, discovery, device removal, mapping lookup, IOC parameters, fast-path enable/disable, NCQ enable/disable, shutdown, persistent connection controls, and NVMe SGL format controls.

## Dependencies And Relationships
This header assumes the core MPI type, version, SGE, and function/status definitions supplied by companion MPI headers such as `mpi2_type.h`, `mpi2.h`, and `mpi2_cnfg.h`. `mpt_sas` uses these layouts when initializing the IOC, discovering controller capabilities, handling asynchronous events, updating firmware/flash regions, and issuing SAS/PCIe control operations.

## Research Notes
The file is versioned as `02.00.30` and explicitly distinguishes MPI v2.0, v2.5, and v2.6 names. Many structures use one-element arrays as variable-length tails; consumers must size buffers from runtime count fields such as `NumElements`, `NumEntries`, `RegionsPerLayout`, `NumberOfLayouts`, or returned image lengths rather than the C `sizeof` alone. Firmware image and flash-region constants are especially relevant to ioctl paths that expose update/upload and diagnostic operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_ioc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_ra.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_ra.h

## Purpose
Defines the MPI v2 RAID Accelerator request, reply, and control-block layouts. This header exposes a small product-specific accelerator path around a controller-owned RAID accelerator CDB.

## Main Interfaces
- `MPI2_RAID_ACCELERATOR_CONTROL_BLOCK`: generic control block with reserved header words and a variable `RaidAcceleratorCDB` payload.
- `MPI2_RAID_ACCELERATOR_REQUEST`: command message containing a 64-bit control-block address and DMA engine number.
- `MPI2_RAID_ACCELERATOR_REPLY`: error/status reply with `IOCStatus`, `IOCLogInfo`, and three product-specific data words.

## Dependencies And Relationships
Depends on MPI scalar and pointer typedefs from the shared MPI header set. It is adjacent to `mpi2_raid.h`: the accelerator interface is separate from normal integrated RAID action messages, but both are controller firmware ABI definitions for RAID-related facilities.

## Research Notes
The version is `02.00.01`; the content is intentionally minimal. Most semantics are left to the firmware/product-specific RAID accelerator CDB, so this header mainly matters for exact DMA address, engine-selection, and reply-status packing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_ra.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_raid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_raid.h

## Purpose
Defines MPI v2 integrated RAID action messages and data structures for creating/deleting volumes, managing physical disks, hot spares, RAID background functions, firmware-update mode, volume indicators, and compatibility checks.

## Main Interfaces
- Action data:
  - `MPI2_RAID_ACTION_DATA`
  - `MPI2_RAID_ACTION_RATE_DATA`
  - `MPI2_RAID_ACTION_START_RAID_FUNCTION`
  - `MPI2_RAID_ACTION_STOP_RAID_FUNCTION`
  - `MPI2_RAID_ACTION_HOT_SPARE`
  - `MPI2_RAID_ACTION_FW_UPDATE_MODE`
- Request/reply:
  - `MPI2_RAID_ACTION_REQUEST`
  - `MPI2_RAID_ACTION_REPLY`
  - `MPI2_RAID_ACTION_REPLY_DATA`
- Action values include indicator query, create/delete volume, enable/disable volumes, physical disk online/offline/fail/hidden, activate/enable failed volume, firmware update mode, write-cache change, volume naming, function-rate changes, hot spare create/delete, system shutdown notification, start/stop RAID function, compatibility check, and product-specific action ranges.
- Volume and operation payloads:
  - `MPI2_RAID_VOLUME_PHYSDISK`
  - `MPI2_RAID_VOLUME_CREATION_STRUCT`
  - `MPI2_RAID_ONLINE_CAPACITY_EXPANSION`
  - `MPI2_RAID_VOL_INDICATOR`
- Compatibility payloads:
  - `MPI2_RAID_COMPATIBILITY_INPUT_STRUCT`
  - `MPI2_RAID_COMPATIBILITY_RESULT_STRUCT`

## Dependencies And Relationships
Depends on shared MPI SGEs and scalar types. It references configuration-page constants from `mpi2_cnfg.h` for RAID volume type and write-cache settings. Event progress and state changes from this command family are mirrored by integrated RAID event structures in `mpi2_ioc.h`.

## Research Notes
The file is versioned `02.00.11`. `MPI2_RAID_VOL_CREATION_NUM_PHYSDISKS` defaults to one but is deliberately build-configurable; callers must account for variable array sizing. The compatibility result encodes protocol, media type, and 4K-sector attributes, which is useful when studying controller-enforced constraints before volume creation or expansion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_raid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_sas.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_sas.h

## Purpose
Defines MPI v2 SAS-specific status values, SAS device-info bits, SMP passthrough, SATA passthrough, and pre-v2.6 SAS IO Unit Control messages.

## Main Interfaces
- SAS status constants:
  - success, invalid frame, unsupported destination/rate/protocol, STP resource busy, wrong destination, IU length errors, XFER_RDY errors, data length/offset errors, NAK/connection failure, and initiator response timeout.
- Device-info flags:
  - SEP, ATAPI, LSI, direct attach, SSP/STP/SMP target, SATA device, SSP/STP/SMP initiator, SATA host, and device type mask for no device/end device/edge expander/fanout expander.
- SMP passthrough:
  - `MPI2_SMP_PASSTHROUGH_REQUEST`
  - `MPI2_SMP_PASSTHROUGH_REPLY`
  - immediate-response flag and SAS status reporting.
- SATA passthrough:
  - `MPI2_SATA_PT_SGE_UNION`
  - `MPI2_SATA_PASSTHROUGH_REQUEST`
  - `MPI2_SATA_PASSTHROUGH_REPLY`
  - command/status FIS fields, data lengths, transfer count, and flags for diagnostic execution, FPDMA, DMA, PIO, vendor-specific, read, and write.
- SAS IO Unit Control:
  - `MPI2_SAS_IOUNIT_CONTROL_REQUEST`
  - `MPI2_SAS_IOUNIT_CONTROL_REPLY`
  - operations for persistent cleanup, PHY link/hard reset, error-log clearing, primitive send, discovery, port-select signal, remove device, mapping lookup, IOC parameter set, fast-path control, NCQ control, and product-specific operations.

## Dependencies And Relationships
Uses core MPI SGE unions and scalar typedefs. MPI v2.6 replaces the SAS-specific IO Unit Control message with the generic `MPI26_IOUNIT_CONTROL_*` messages in `mpi2_ioc.h`; this header remains relevant for MPI v2.0/v2.5 products and passthrough operations.

## Research Notes
The version is `02.00.10`. SGE union comments are important: MPI v2.5 restricts some passthrough paths to IEEE 64-bit elements, while MPI v2.0 allows MPI and IEEE simple/chain variants. `MPI2_SATA_PT_REQ_PT_FLAGS_FPDMA` is explicitly MPI v2.6-and-newer even though the rest of the SAS IO Unit Control section is pre-v2.6.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_sas.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_targ.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_targ.h

## Purpose
Defines MPI v2 target-mode wire formats for posting target command buffers, receiving SSP command/task buffers, assisting target data movement, sending target status, returning standard target replies, and aborting target-mode work.

## Main Interfaces
- Command-buffer posting:
  - `MPI2_TARGET_CMD_BUF_POST_BASE_REQUEST`
  - `MPI2_TARGET_CMD_BUF_POST_LIST_REQUEST`
  - `MPI2_TARGET_BUF_POST_BASE_LIST_REPLY`
  - address-space selectors for system memory and IOC memory regions, auto-post-all flag, MSIX index range fields, and IO-index-valid reply flag.
- Target command buffers:
  - `MPI2_TARGET_SSP_CMD_BUFFER`
  - `MPI2_TARGET_SSP_TASK_BUFFER`
  - hashed source SAS address mask/shift, LUN, task attribute, CDB, task management function, managed task tag, and transfer-tag fields.
- Target assist:
  - `MPI2_TARGET_ASSIST_REQUEST` for MPI v2.0
  - `MPI25_TARGET_ASSIST_REQUEST` for MPI v2.5+
  - flags for repost, TLR, retransmit, auto status, direction, bidirectional I/O, multicast, receive-first, and MPI v2.6 escape passthrough.
  - SGL address/type encodings for v2.0 and `DMAFlags` combinations for v2.5 data/cache/interleaved/host-DIF layouts.
  - EEDP/DIF controls for tag increments, guard/app/ref checks, passthrough, strip/insert/replace/regenerate operations, escape modes, and host guard method.
- Status and replies:
  - `MPI2_TARGET_STATUS_SEND_REQUEST`
  - `MPI2_TARGET_SSP_RSP_IU`
  - `MPI2_TARGET_STANDARD_REPLY`
- Aborts:
  - `MPI2_TARGET_MODE_ABORT`
  - `MPI2_TARGET_MODE_ABORT_REPLY`
  - abort types for all command buffers, all I/O, exact I/O, exact request, request plus I/O, initiator device handle, and all commands.

## Dependencies And Relationships
Uses core MPI SGE definitions and scalar typedefs. This header is for SCSI target mode and is separate from initiator I/O, SMP/SATA passthrough, and integrated RAID headers. It shares queue, status, IOC log, VP/VF, and MSIX concepts with the rest of the MPI v2 ABI.

## Research Notes
The file is versioned `02.00.09`. It preserves both MPI v2.0 and v2.5 target-assist formats because DIF/EEDP and SGL representation changed. The SSP response IU is called out as big-endian; little-endian consumers must not treat the field order as ordinary host-native values without conversion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_targ.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_tool.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_tool.h

## Purpose
Defines MPI v2 diagnostic and toolbox command layouts used for controller maintenance: flash/NVRAM cleanup, memory move, diagnostic data upload, ISTWI access, beacon control, diagnostic CLI, text display, diagnostic buffer posting, and diagnostic buffer release.

## Main Interfaces
- Toolbox selectors:
  - clean, memory move, diagnostic data upload, ISTWI read/write, beacon, diagnostic CLI, and text display tool IDs.
- Common toolbox reply:
  - `MPI2_TOOLBOX_REPLY`
- Clean and memory tools:
  - `MPI2_TOOLBOX_CLEAN_REQUEST`
  - `MPI2_TOOLBOX_MEM_MOVE_REQUEST`
  - clean flags for boot services, manufacturing/persistent pages, current/backup firmware, MegaRAID, initialization, SBR/SBR backup, HII, controller, IMR firmware, MR NVDATA, all-but-MPB, entire flash, flash, SEEPROM, and NVSRAM.
- Diagnostic upload:
  - `MPI2_TOOLBOX_DIAG_DATA_UPLOAD_REQUEST`
  - `MPI2_DIAG_DATA_UPLOAD_HEADER`
- ISTWI:
  - `MPI2_TOOLBOX_ISTWI_READ_WRITE_REQUEST`
  - `MPI2_TOOLBOX_ISTWI_REPLY`
  - actions for read, write, sequence, reserve bus, release bus, and reset; flags for auto reserve/release and page address.
- Beacon, CLI, and text display:
  - `MPI2_TOOLBOX_BEACON_REQUEST`
  - `MPI2_TOOLBOX_DIAGNOSTIC_CLI_REQUEST`
  - `MPI25_TOOLBOX_DIAGNOSTIC_CLI_REQUEST`
  - `MPI2_TOOLBOX_DIAGNOSTIC_CLI_REPLY`
  - `MPI2_TOOLBOX_TEXT_DISPLAY_REQUEST`
- Diagnostic buffers:
  - `MPI2_DIAG_BUFFER_POST_REQUEST`
  - `MPI2_DIAG_BUFFER_POST_REPLY`
  - `MPI2_DIAG_RELEASE_REQUEST`
  - `MPI2_DIAG_RELEASE_REPLY`
  - buffer types for trace, snapshot, and extended; extended utilization type; release-on-full and immediate-release flags.

## Dependencies And Relationships
Uses MPI SGE unions and scalar typedefs. `mptsas_ioctl.h` exposes higher-level userland diagnostic actions that correspond to these firmware buffer operations. Firmware image-region constants in `mpi2_ioc.h` align with many of the clean-tool flags.

## Research Notes
The file is versioned `02.00.14`. Diagnostic CLI has separate MPI v2.0 and v2.5 request layouts because the SGE format changed. Diagnostic buffer post includes 23 product-specific words, so callers should preserve/round-trip vendor data rather than assuming illumos owns those fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_tool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_type.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_type.h

## Purpose
Provides the basic scalar and pointer typedefs used by MPI v2 headers when the older `mpi_type.h` definitions have not already been included.

## Main Interfaces
- `MPI2_POINTER`: defaults to `*`, but can be overridden before inclusion for environments that need a different pointer qualifier.
- Integer typedefs:
  - `S8`, `U8`, `S16`, `U16`
  - `S32`, `U32`, with a FreeBSD-specific `int32_t`/`uint32_t` branch and a Unix/ARM/Alpha/PPC branch using `int`/`unsigned int`.
  - `S64`, `U64` as structs containing low/high 32-bit words, not native 64-bit integer typedefs.
- Pointer typedefs:
  - `PS8`, `PU8`, `PS16`, `PU16`, `PS32`, `PU32`, `PS64`, `PU64`.

## Dependencies And Relationships
This is the base type substrate for all `mpi2_*` ABI headers in this group. The `#ifndef MPI_TYPE_H` guard avoids redefining basic types if the MPI v1 type header is already present.

## Research Notes
The version is `02.00.01`. The `S64`/`U64` struct representation is significant for ABI layout: it encodes 64-bit quantities as two 32-bit words and should not be silently replaced with a compiler-native `uint64_t` in packed firmware message definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpi/mpi2_type.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_ioctl.h

## Purpose
Defines the illumos `mpt_sas` user/kernel ioctl ABI for adapter information, firmware update, adapter reset, raw MPI passthrough, event queues, PCI info, firmware diagnostics, register access, disk topology queries, and enclosure LED control.

## Main Interfaces
- Ioctl command numbers:
  - `MPTIOCTL_GET_ADAPTER_DATA`
  - `MPTIOCTL_UPDATE_FLASH`
  - `MPTIOCTL_RESET_ADAPTER`
  - `MPTIOCTL_PASS_THRU`
  - `MPTIOCTL_EVENT_QUERY`
  - `MPTIOCTL_EVENT_ENABLE`
  - `MPTIOCTL_EVENT_REPORT`
  - `MPTIOCTL_GET_PCI_INFO`
  - `MPTIOCTL_DIAG_ACTION`
  - `MPTIOCTL_REG_ACCESS`
  - `MPTIOCTL_GET_DISK_INFO`
  - `MPTIOCTL_LED_CONTROL`
- Adapter and PCI structures:
  - `mptsas_pci_bits_t`
  - `mptsas_adapter_data_t`
  - `mptsas_pci_info_t`
  - adapter type constants for SAS-2 and SAS-3.
- Firmware and passthrough:
  - `mptsas_update_flash_t`
  - `mptsas_pass_thru_t`
  - data-direction constants for none/read/write/both.
- Event queue:
  - `MPTSAS_EVENT_QUEUE_SIZE`
  - `MPTSAS_MAX_EVENT_DATA_LENGTH`
  - `mptsas_event_query_t`
  - `mptsas_event_enable_t`
  - `mptsas_event_entry_t`
  - `mptsas_event_report_t`
- Firmware diagnostics:
  - `mptsas_diag_action_t`
  - `mptsas_fw_diag_register_t`
  - `mptsas_fw_diag_unregister_t`
  - `mptsas_fw_diag_query_t`
  - `mptsas_fw_diag_release_t`
  - `mptsas_diag_read_buffer_t`
  - action constants for register, unregister, query, read buffer, and release; error/flag constants for UID, post/release, app-owned, valid buffer, firmware buffer access, reregister, and force release.
- Register/disk/LED:
  - `mptsas_reg_access_t` with IO and memory read/write command constants.
  - `mptsas_disk_info_t`, `mptsas_get_disk_info_t`, and kernel-only `mptsas_get_disk_info32_t`.
  - `mptsas_led_control_t` and constants for set/get plus identify/fail/OK-to-remove LEDs.

## Dependencies And Relationships
Includes `sys/types.h` and uses illumos fixed-width types plus `caddr32_t` under `_KERNEL` for 32-bit compatibility. The pass-through, flash, event, and diagnostic payloads bridge userland management tools to MPI firmware messages defined in the `mpi2_*` headers in this group.

## Research Notes
This file is an externally visible ABI and must remain alignment-conscious for 32-bit and 64-bit applications. It uses integer-encoded user pointers (`uint64_t`) in several structures, while `mptsas_get_disk_info_t` uses a typed pointer and provides an explicit 32-bit kernel compatibility form. That split is a key detail for copyin/copyout and model conversion.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_smhba.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_smhba.h

## Purpose
Declares SM-HBA support interfaces and property names for the illumos `mpt_sas` driver. It is the header for exposing SAS HBA/PHY metadata, sysevents, and PHY kstats through the Solaris/illumos SM-HBA model.

## Main Interfaces
- SM-HBA property names:
  - `MPTSAS_NUM_PHYS`
  - `MPTSAS_NUM_PHYS_HBA`
  - `MPTSAS_SMHBA_SUPPORTED`
  - `MPTSAS_DRV_VERSION`
  - `MPTSAS_HWARE_VERSION`
  - `MPTSAS_FWARE_VERSION`
  - `MPTSAS_SUPPORTED_PROTOCOL`
  - `MPTSAS_VIRTUAL_PORT`
  - `MPTSAS_MANUFACTURER`
  - `MPTSAS_SERIAL_NUMBER`
  - `MPTSAS_MODEL_NAME`
  - `MPTSAS_VARIANT`
- Device-info helpers:
  - `IS_ATAPI_DEVICE(x)`
  - `IS_SATA_DEVICE(x)`
  - `DEVINFO_DIRECT_ATTACHED`
- SM-HBA functions:
  - `mptsas_smhba_setup()`
  - `mptsas_smhba_show_phy_info()`
  - `mptsas_smhba_set_all_phy_props()`
  - `mptsas_smhba_set_one_phy_props()`
  - `mptsas_smhba_log_sysevent()`
  - `mptsas_create_phy_stats()`
  - `mptsas_update_phy_stats()`
  - `mptsas_destroy_phy_stats()`
  - `mptsas_smhba_phy_init()`
  - `mptsas_smhba_phy_state_update()`

## Dependencies And Relationships
Includes `sys/nvpair.h` for `data_type_t` and `sys/scsi/adapters/mpt_sas/mptsas_var.h` for driver types such as `mptsas_t`, `mptsas_phymask_t`, and `smhba_info_t`. It complements the lower-level MPI SAS headers by publishing discovered PHY/device state as illumos device properties, sysevents, and kstats.

## Research Notes
The header is small but sits on an important observability boundary: it maps controller/SAS device data into OS-visible SM-HBA properties. The `IS_ATAPI_DEVICE` and `IS_SATA_DEVICE` masks align with SAS device-info flags, so callers must pass the same device-info bitfield used by MPI/SAS discovery code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_smhba.h -->