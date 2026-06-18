# Group Research: group_614_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__b91861786574

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_var.h

## Purpose
Primary private header for the LSI/Avago/Broadcom MPT SAS HBA driver. It defines driver-wide constants, DMA/SGL limits, target/enclosure/RAID state, command tracking, hotplug topology records, per-PHY SM-HBA data, the main `mptsas_t` soft state, register/queue helper macros, debug hooks, and prototypes for the MPT SAS implementation.

## Main Interfaces
- `mptsas_target_t`, `mptsas_smp_t`, and `mptsas_enclosure_t` model SSP/STP targets, SMP expanders, and enclosure metadata.
- `mptsas_cmd_t` wraps `scsi_pkt` state with DMA cookies, SGL state, ARQ/extra-sense buffers, active-slot metadata, timeout flags, and a target pointer.
- `mptsas_slots_t` tracks outstanding commands by SMID, reserving slot zero and a final task-management slot.
- `mptsas_t` is the central HBA instance state: SCSA/SMP transports, mutexes/CVs, target refhashes, RAID config, active/wait/done queues, DMA frame regions, interrupts, firmware/diagnostic buffers, SAS PHY info, dynamic reconfiguration taskq state, UFM handle, and IOC capability flags.
- Macros cover MPI request-frame sizing, SG element sizing for MPI 2.5/IEEE SGE formats, queue removal, register doorbell access, interrupt masking, target/LUN extraction, and LUN validity checks.
- Prototypes expose command save/remove, polling, DMA allocation, firmware update/check/download, IOC reset/init, configuration page access, RAID operations, topology/PHY discovery helpers, FMA checks, and SM-HBA stats.

## Dependencies And Relationships
Includes illumos DDI/SCSI/MDI support plus MPI2 tool/config headers. It is consumed by the MPT SAS driver implementation files for transport, IOC setup, config-page traversal, RAID support, passthrough, firmware diagnostics, and hotplug event handling.

## Research Notes
The header is mostly driver state and protocol plumbing. The key design point is that normal I/O, event-ack, passthrough/config, firmware, and task-management commands all share a single command/slot framework but use distinct flags and synchronization paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpt_sas/mptsas_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/ata.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/ata.h

## Purpose
Defines ATA IDENTIFY DEVICE data layout used by the PMCS driver for SATA devices behind the SAS controller.

## Main Interfaces
- Includes `ata8-acs.h` for ATA opcodes and `atapi7v3.h` for SATA FIS structures.
- `ata_identify_t` is a 256-word structure matching the ATA IDENTIFY data block, with named fields for serial number, firmware revision, model number, and generic `wordN` placeholders for the remaining specification words.
- `LBA_CAPACITY(ati)` chooses 28-bit capacity from words 60-61 unless word 83 indicates 48-bit addressing, then builds a 64-bit capacity from words 100-103 with little-endian conversion.

## Dependencies And Relationships
Used by PMCS SATA probing/identify logic to derive target capacity and descriptive strings from IDENTIFY data returned through a SATA command.

## Research Notes
This is a wire-format header. Consumers must treat the contents as little-endian ATA words and avoid native-endian direct interpretation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/ata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/ata8-acs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/ata8-acs.h

## Purpose
Provides a compact subset of ATA8-ACS command opcodes needed by the PMCS SATA path.

## Main Interfaces
- `enum ata_opcode` maps ATA command names to opcode bytes, including reads/writes, DMA/queued/FPDMA variants, SMART, IDENTIFY, PACKET, SET FEATURES, cache flush, security commands, native max address, trusted commands, logs, and power-management commands.

## Dependencies And Relationships
Included by `ata.h` and used when building SATA host I/O FIS payloads in the PMCS driver.

## Research Notes
This header is declarative and intentionally limited to command constants. It contains a duplicate value for trusted send variants as written in the source.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/ata8-acs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/atapi7v3.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/atapi7v3.h

## Purpose
Defines the SATA Frame Information Structure formats from ATA/ATAPI-7 used by the PMCS SATA command path.

## Main Interfaces
- FIS structures include host-to-device register FIS, device-to-host register FIS, set-device-bits FIS, DMA activate/setup FIS, BIST activate FIS, PIO setup FIS, and a generic bidirectional FIS.
- FIS type constants cover `FIS_REG_H2DEV`, `FIS_REG_D2H`, `FIS_SET_DEVICE_BITS`, `FIS_DMA_ACTIVATE`, `FIS_DMA_FPSETUP`, `FIS_BIST_ACTIVATE`, `FIS_PIO_SETUP`, and `FIS_BI`.
- IDC bit constants define command, interrupt, and data indicators.
- `fis_t` reserves five dwords for common FIS payloads used by PMCS helper routines.

## Dependencies And Relationships
Included by `ata.h`; consumed by PMCS SATA command building, FIS dumping, identify, and special-command handling.

## Research Notes
The comments explicitly document 28-bit and 48-bit ATA field mapping into the host-to-device register FIS, which is useful when reviewing PMCS SATA translation code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/atapi7v3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs.h

## Purpose
Principal private header for the PMC-Sierra PM8001/8x6G SAS/SATA HBA driver. It gathers the PMCS subheaders and defines the target, LUN, iport, DMA chunk, interrupt coalescing, completion-thread, and HBA soft-state structures.

## Main Interfaces
- `pmcs_xscsi_t` is target state: SATA flags, reset/recovery state, queue depths, command counters, wait/active/special queues, tag map, capacity, unit address, dtype, LUN list, and SMP device pointer.
- `pmcs_lun_t` binds a SCSI LUN number and wire-format LUN to the target and `scsi_device`.
- `pmcs_iport_t` is per-iport state, including phymap unit-address state, target map, target softstate, PHY list, and serialized SMP request state.
- `pmcs_hw_t` is the central HBA state: DDI handles, PCI/register windows, DMA queues, MPI offsets, scratch/FW log/register-dump memory, interrupts, PHY discovery tree, work pools, SCSA/SMP transports, target arrays, completion queues, interrupt coalescing, firmware metadata, and FMA receptacle data.
- `pmcs_io_intr_coal_t`, `pmcs_cq_thr_info_t`, `pmcs_cq_info_t`, and `pmcs_iocomp_cb_t` support interrupt coalescing and deferred completion processing.

## Dependencies And Relationships
Includes SCSA, SMP, SAS, DDI/FMA, MDI, byteorder, bitmap, queue, and SPC-3 type headers, then pulls in `pmcs_param.h`, `pmcs_reg.h`, `pmcs_mpi.h`, `pmcs_iomb.h`, `pmcs_sgl.h`, `ata.h`, `pmcs_def.h`, `pmcs_proto.h`, `pmcs_scsa.h`, and `pmcs_smhba.h`.

## Research Notes
This header shows the driver's core architecture: firmware MPI queues feed work structures; discovery builds a PHY tree; iports expose phymap-derived ports; and SCSA/SMP targets hang off iport target maps.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_def.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_def.h

## Purpose
Defines PMCS driver-wide data types, PHY discovery state, work-item state, firmware header format, tag architecture, work scheduling macros, tracing records, firmware event-log formats, and receptacle metadata.

## Main Interfaces
- `pmcs_dtype_t` classifies PHY contents as empty, SATA, SAS, expander, or new.
- `pmcs_phy_t` represents a physical or discovered PHY node, including tree links, device handle, link/recovery state, SAS address, iport/target back-pointers, port phymasks, SMP routing attributes, and cached SMP report/discover responses.
- `pmcwork_t` tracks one firmware command/work item, with locks, wait CV, tag, owning PHY/target, timeout, state, timestamps, abort tag, and last-use diagnostics.
- Tag macros split 32-bit firmware tags into done/non-IO/type/serial/index fields.
- Work flags and `SCHEDULE_WORK()`/`WORK_SCHEDULED()` encode offlevel tasks such as discovery, abort handling, spinup release, SATA work, queue running, DMA chunk addition, recovery, deregistration, and register dump.
- `pmcs_fw_hdr_t`, `pmcs_tbuf_t`, `pmcs_fw_event_hdr_t`, and `pmcs_fw_event_entry_t` describe firmware image and logging formats.

## Dependencies And Relationships
Uses `pmcs_hw_t`, `pmcs_iport_t`, `pmcs_xscsi_t`, and SAS/SMP types declared through `pmcs.h` includes. It is foundational for discovery, queueing, firmware update, event logging, and diagnostic code.

## Research Notes
The extensive comments around queue memory layout and tag architecture are important: they explain how host memory control areas, firmware tags, and interrupt-side completion ownership fit together.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_def.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_fwlog.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_fwlog.h

## Purpose
Defines sparse internal register ranges used by PMCS firmware forensics and register-dump collection.

## Main Interfaces
- `pmcs_sparse_regs_t` describes a sparse register segment with shift address, base address, offset start/end, block flags, and optional description.
- Flags identify block starts/ends and a specific SSPA control-register bit.
- `hsst_state[]`, `sspa_state[]`, and `gsm_spregs[]` enumerate hardware/firmware forensic register blocks, including HSST, SSPA, SRC, BDMA, PCIe APP/PHY/CORE, OSSP, LMS_DSS, SSPL_6G, MBIC IOP/AAP1, SPBC, and a large GSM sparse range.

## Dependencies And Relationships
Used by PMCS register-dump/forensics routines declared in `pmcs_proto.h`. The address ranges are based on a PMC firmware forensic application note referenced in the file comment.

## Research Notes
This header contains data definitions, not just declarations, so its include pattern matters. It is a diagnostic map rather than command-path logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_fwlog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_iomb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_iomb.h

## Purpose
Defines PMC IO Message Buffer protocol constants, inbound/outbound opcodes, status values, NVRAM/VPD/register-dump payloads, IOMB header layout, and queue producer/consumer helper macros.

## Main Interfaces
- IOMB header bit macros define valid/high-priority, buffer count, outbound queue ID, category, and opcode fields.
- Inbound opcodes cover echo/info/VPD, PHY start/stop, SSP/SMP/SATA I/O, aborts, device handle registration/deregistration, local PHY control, firmware flash, GPIO, diagnostics, timestamp, port control, NVMD data, and device state.
- Outbound opcodes cover completions, async events, registration results, abort results, diagnostics, queue skipping, device handle removal, and device-state responses.
- Status constants cover generic completion, link/open connection failures, SATA/NCQ errors, SMP errors, device-state/recovery errors, NVMD/flash errors, device-registration outcomes, and SAS hardware events.
- `pmcs_get_nvmd_cmd_t`, `pmcs_set_nvmd_cmd_t`, `pmcs_vpd_header_t`, `pmcs_vpd_kv_t`, `pmcs_iomb_header_t`, and `pmcout_ssp_comp_t` model wire-format payloads.
- Queue macros implement circular IQ/OQ indexing, IQ entry acquisition, producer-index updates, DMA sync, and OQ consumer updates.

## Dependencies And Relationships
Relies on `pmcs_param.h` queue sizes, `pmcs_hw_t` queue fields from `pmcs.h`, and register accessors from `pmcs_reg.h`. It is the core hardware/firmware message protocol layer for PMCS.

## Research Notes
The comments explain directionality clearly: inbound queues are host-to-card with card-side producer doorbells, outbound queues are card-to-host with host-side consumer updates.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_iomb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_mpi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_mpi.h

## Purpose
Defines PMCS Message Passing Interface table offsets, firmware version extraction, queue configuration-table layout, general status table offsets, event queue assignment macros, log buffer registers, and fatal error controls.

## Main Interfaces
- MPI configuration offsets include signature, interface revision, firmware version, max outstanding I/O, max S/G and device handles, queue counts, GST/IQ/OQ table offsets, queue-depth information, event queues, NCQ queues, customization settings, log buffers, and fatal-error registers.
- Macros extract firmware type/variant/major/minor/micro/revision and build comparable version values.
- `PMCS_MPI_EVQSET()` and `PMCS_MPI_NCQSET()` program per-PHY outbound queues for SAS events and SATA NCQ notification.
- GST macros expose MPI state, queue freeze, heartbeats, PHY info, and recoverable error info.
- IQC/OQC macros describe per-queue configuration table slots and decode depth, entry size, interrupt coalescing count/timer/vector, and queue parameters.

## Dependencies And Relationships
Used during `pmcs_start_mpi()`, queue setup, interrupt configuration, firmware logging, heartbeat/watchdog, and fatal error handling.

## Research Notes
This header is the bridge between the driver's queue-memory allocations and the firmware's MPI configuration tables.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_mpi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_param.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_param.h

## Purpose
Collects compile-time tunable parameters and fixed sizing constants for the PMCS driver.

## Main Interfaces
- Defines maximum configuration time, max IQ/OQ counts, max ports, expansion depth, control/scratch area sizes, firmware log size/threshold, queue entry size/depth, watchdog interval, forward-progress cadence, inbound/outbound queue numbering, SGL chunk limits, interrupt vector counts, and firmware image names/offsets.
- Establishes the driver's active queue model: nine inbound queues, three outbound queues, and one fatal interrupt vector.

## Dependencies And Relationships
Included early by `pmcs.h` and used by queue allocation, MPI setup, scratch/SMP operations, firmware logging, watchdog, DMA SGL construction, and firmware update code.

## Research Notes
Several values are intentionally aligned with hardware assumptions, especially `PMCS_QENTRY_SIZE`, `PMCS_CONTROL_SIZE`, and the scratch area large enough for maximum SMP request/response payloads.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_param.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_proto.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_proto.h

## Purpose
Declares PMCS driver functions and debug-printing levels used across attach/setup, firmware, queueing, discovery, SATA/SAS/SMP operations, SCSA integration, recovery, diagnostics, and iport/PHY lifetime management.

## Main Interfaces
- `pmcs_prt_level_t` and `pmcs_prt()` gate debug/error output by debug mask.
- Prototypes cover target assignment/removal, scratch acquisition, work allocation/tag lookup, aborts, SSP TMF, SATA NCQ abort, interrupt handlers, device registration, endian transforms, status/name helpers, WWN conversions, setup/MPI start/stop, firmware update/flash, echo test, PHY start/stop, iport target maps, SAS diagnostics, register dumps, resets, discovery, interrupt coalescing, IOMB status checks, SATA identify/work, DMA setup, FMA checks, NVMD access, completion processing, queue flushing, recovery, iport reference management, phymap callbacks, PHY locking/refcounts, worker thread, fatal handling, SMP serialization, SM-HBA PHY property updates, and firmware log gathering.

## Dependencies And Relationships
Depends on `pmcs_hw_t`, `pmcs_phy_t`, `pmcs_xscsi_t`, `pmcwork_t`, `pmcs_iport_t`, `pmcs_fw_hdr_t`, `pmcs_nvmd_type_t`, and related PMCS data types declared by other PMCS headers.

## Research Notes
This file is a useful index to the implementation modules: almost every major operational area of the PMCS driver has a cross-module prototype here.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_proto.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_reg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_reg.h

## Purpose
Defines PMCS PCI IDs, BAR/register-set layout, message-unit register offsets, doorbell bits, scratchpad state fields, GSM/top-level register offsets, reset bits, flash/register-dump addresses, PCI config offsets, PHY-layer registers, and register accessor prototypes.

## Main Interfaces
- PCI identity constants for vendor/device and PM8001 revisions.
- Message unit offsets and bit definitions for inbound/outbound doorbells, scratchpads, MPI initiation/freeze/unfreeze/termination, interrupt masking, AAP/IOP states, and soft-reset signatures.
- GSM register constants cover NMI enables, reset/control, parity/ECC indicators, flash regions, shared memory, I/O status table, and ring buffers.
- Top-level registers include event/error interrupt control, AXI translation, outbound doorbell auto-clear, and interrupt coalescing timer/control.
- Reset bit masks define inverted chip reset fields and soft-reset component groups.
- Accessor prototypes cover message unit, GSM, top unit, MPI/GST/IQC/OQC tables, IQ/OQ indices, and their corresponding writes.

## Dependencies And Relationships
Used by PMCS setup/reset/interrupt/MPI/register-dump code and by queue macros in `pmcs_iomb.h`.

## Research Notes
The comments document four 64 KiB PCIe memory regions and the shifted window used for broader chip register access, which is central to understanding PMCS register mapping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_reg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_scsa.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_scsa.h

## Purpose
Defines the PMCS interface to the illumos SCSA midlayer, including address/packet conversion macros, the PMCS command wrapper, status sizing, wait-queue return codes, and SCSA-facing prototypes.

## Main Interfaces
- Macros map SCSI addresses, transport structures, packets, and PMCS command wrappers to HBA/iport/target-private state.
- `pmcs_cmd_t` wraps a `scsi_pkt` with queue linkage, DMA chunk list, target/LUN pointers, firmware tag, and SATL tag.
- Prototypes cover SCSA initialization, status latching, residual setting, wait/completion queue running, target/LUN configuration, SMP child discovery/configuration, and SATA special command handling.

## Dependencies And Relationships
Included by `pmcs.h`; depends on `pmcs_hw_t`, `pmcs_cmd_t`, `pmcs_xscsi_t`, `pmcs_lun_t`, and `pmcs_dmachunk_t`. It links the PMCS firmware queueing layer to illumos target-driver packet flow.

## Research Notes
The header separates normal command flow from SATA special queue handling, matching the target flags in `pmcs_xscsi_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_scsa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_sgl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_sgl.h

## Purpose
Defines the PMCS external DMA scatter/gather list representation and chunk-management hooks.

## Main Interfaces
- `pmcs_dmasgl_t` is the hardware SGL entry with low/high DMA address, length, and flags.
- `PMCS_DMASGL_EXTENSION` marks an SGL entry as pointing to another SGL array.
- `PMCS_SGL_CHUNKSZ` derives chunk size from `PMCS_SGL_NCHUNKS`.
- `pmcs_dmachunk_t` tracks a linked chunk with virtual SGL array pointer, DMA address, access handle, and DMA handle.
- Prototypes declare DMA load/unload and initialization of newly allocated DMA chunks into the free list.

## Dependencies And Relationships
Consumes sizing from `pmcs_param.h` and command/HBA types from `pmcs.h`. Used by SCSA command DMA mapping before IOMBs are posted.

## Research Notes
The comments note that chunk bookkeeping avoids using reserved firmware fields in SGL entries, preserving compatibility with future firmware revisions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_sgl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_smhba.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_smhba.h

## Purpose
Declares SM-HBA property names and helper routines for exposing PMCS HBA, iport, target, PHY, and device attributes.

## Main Interfaces
- Property string constants include number of PHYs, SM-HBA support, driver/hardware/firmware versions, supported protocol, manufacturer, serial number, and model name.
- `pmcs_smhba_add_hba_prop()`, `pmcs_smhba_add_iport_prop()`, and `pmcs_smhba_add_tgt_prop()` add individual typed properties.
- `pmcs_smhba_set_scsi_device_props()` and `pmcs_smhba_set_phy_props()` populate sets of SM-HBA properties.
- `pmcs_smhba_log_sysevent()` emits SM-HBA related sysevents.

## Dependencies And Relationships
Includes `sys/nvpair.h` for `data_type_t` and relies on PMCS HBA/iport/target/PHY types from the surrounding include chain.

## Research Notes
This is administrative/observability support rather than I/O-path logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/pmcs/pmcs_smhba.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/scsi_vhci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/scsi_vhci.h

## Purpose
Global include for illumos SCSI virtual HCI multipathing. It defines kernel-private packet/LUN/path/HBA state, failover module interfaces, persistent reservation helpers, path operation descriptors, ioctl ABI structures, and multipath ioctl command numbers.

## Main Interfaces
- Kernel macros map transports, packets, SCSI addresses, VHCI packets, and path-private structures; hold/release LUNs during failover/reservation-sensitive operations; and count outstanding path commands.
- `vhci_pkt` links target-driver packets to physical HBA packets and records binding path, init-packet arguments, retry/original packet state, and VHCI packet flags.
- `scsi_vhci_lun_t` tracks per-virtual-LUN locks, transient/failover state, active pathclass, failover ops, reservation/PGR state, path update state, LUN reset support, sector size, and failover support mode.
- `scsi_vhci_priv_t` is pathinfo client-private state with per-path command count, associated physical `scsi_device`, external failover watch token, and new-path cleanup marker.
- `scsi_vhci_t` is VHCI soft state with device info, HBA transport, taskqs, reset notification list, config flags, and MPAPI private state.
- `scsi_failover_ops` defines the pluggable failover module ABI: probe/unprobe, activate/deactivate, get opinfo, ping, sense analysis, and pathclass iteration.
- Userland structs and constants define path property buffers, path info, ioctl arguments, controller switching, and `SCSI_VHCI_*` ioctl subcommands.

## Dependencies And Relationships
Includes task queues, multi-host disk support, MDI/MPAPI headers, and SCSI adapter MPAPI definitions. Used by the scsi_vhci driver and failover modules such as TPGS and symmetric failover providers.

## Research Notes
The header has both kernel and userland sections. The failover contract is modular, while the ioctl ABI exposes client/PHCI path queries and administrative path state changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/scsi_vhci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/scsi_vhci_tpgs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/scsi_vhci_tpgs.h

## Purpose
Defines TPGS-specific constants and a helper prototype for SCSI VHCI target-port-group failover support.

## Main Interfaces
- Retry constant `STD_FO_MAX_CMD_RETRIES` for standard failover polling when transport errors or rejected commands occur.
- TPGS access states include active optimized, active non-optimized, standby, unavailable, and transitioning.
- Sense ASC/ASCQ constants identify state transition, state changed, invalid parameter list, invalid command opcode, and target-port accessibility states.
- `vhci_tpgs_get_target_fo_mode()` reports target failover mode, state, extended logical failover capability, and preferred status for a `scsi_device`.

## Dependencies And Relationships
Used by the TPGS failover module and VHCI failover logic to interpret ALUA/TPGS access states and sense data.

## Research Notes
This is a small policy/protocol companion header for the broader failover ABI in `scsi_vhci.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/scsi_vhci_tpgs.h -->