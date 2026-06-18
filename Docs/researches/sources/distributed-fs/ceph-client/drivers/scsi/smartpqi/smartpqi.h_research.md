# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi.h

## Purpose
Defines the hardware protocol, firmware data structures, queue layout, controller state, device state, RAID-bypass metadata, SAS transport hooks, and helper declarations for the Microchip PQI SCSI driver. It is the shared contract consumed by `smartpqi_init.c`, `smartpqi_sis.c`, and `smartpqi_sas_transport.c`.

## Important APIs, Types, And Functions
The header starts with packed hardware register and IU definitions: `pqi_device_registers`, `pqi_ctrl_registers`, `pqi_iu_header`, admin requests/responses, RAID/AIO I/O requests, task management requests, event requests/responses, vendor general requests, host memory descriptors, and AIO/RAID error information. These structures use explicit endian types and packed layout because firmware consumes them directly.

Queue and controller runtime types include `pqi_admin_queues_aligned`, `pqi_admin_queues`, `pqi_queue_group`, `pqi_event_queue`, `pqi_io_request`, `pqi_event`, and the large `pqi_ctrl_info`. `pqi_ctrl_info` is the central HBA state: PCI device, MMIO register pointers, firmware identity, controller capabilities, queue memory, IRQ mode and vector counts, SCSI host pointer, scan/reset flags, firmware feature booleans, device list, SAS host data, request pool, event array, heartbeat/offline work, synchronous request semaphore, blocked-thread accounting, OFA/controller-log memory, and removal state.

Device-facing types include CISS report-lun formats, physical/logical LUN entries, `raid_map`, `pqi_scsi_dev_raid_map_data`, `pqi_scsi_dev`, stream detection state, per-device TMF work, SAS node/port/phy wrappers, and BMIC command payloads. `pqi_scsi_dev` records bus/target/lun identity, WWID and volume ID, physical/logical flags, offline/remove/reset state, inquiry strings, SAS topology, queue depth, AIO handle, RAID bypass map and counters, encryption limits, stream history, outstanding command counters, and TMF work items.

Constants enumerate PQI request/response IU types, admin functions, PQI and CISS status codes, event types, queue sizes, queue alignment requirements, reset types/actions, firmware feature bits, CISS/BMIC opcodes, logical volume states, bus IDs, RAID map limits, and default transfer/queue limits. The inline `shost_to_hba` retrieves `pqi_ctrl_info` from SCSI host private data. External declarations expose SAS/SMP integration functions and `pqi_sas_transport_functions`.

## Control Flow
This header does not execute control flow directly, but it shapes the driver lifecycle. Initialization code maps SIS and PQI registers through `pqi_ctrl_registers`, transitions to PQI mode, reports device capabilities, allocates aligned admin/operational/event queues, fills `pqi_ctrl_info`, and creates I/O request pools sized by firmware limits. I/O submission code chooses RAID, AIO, RAID1, RAID5, or RAID6 IU formats based on `pqi_scsi_dev` state and RAID map calculations, then posts to a `pqi_queue_group`. Completion code decodes response IU types and error buffers to update SCSI command results.

Discovery code uses CISS report logical/physical LUN structures, BMIC identify payloads, VPD status definitions, and RAID map structures to build and update `pqi_scsi_dev` entries. Event code uses `pqi_event_config`, `pqi_event_response`, and event acknowledgements to schedule rescans, AIO state changes, OFA memory handling, and controller logging. Reset/offline code uses heartbeat, soft-reset, reset-register, block-request flags, and controller removal state fields in `pqi_ctrl_info`.

## State And Persistence Behavior
All declared state is in-memory driver state or DMA-coherent memory shared with controller firmware. The hardware-facing structures persist only while allocated and mapped; firmware-visible queues and host-memory descriptors must obey the alignment and packing constants. `pqi_ctrl_info` persists for the PCI device lifetime, while `pqi_scsi_dev` entries persist while devices remain discovered or retained through rescan/delete handling. No file-backed persistence is defined here.

The header encodes several state machines: controller mode (`SIS_MODE`/`PQI_MODE`), controller removal state, reset status, per-device gone/new/keep/offline/reset flags, request reference counts, event pending flags, heartbeat counters, blocked request accounting, and OFA quiesce/memory allocation work.

## Dependencies And Integration Points
The header depends on Linux SCSI host APIs, BSG/SAS transport support, PCI-owned controller code, DMA address types, endian annotations, workqueues, timers, locks, semaphores, per-CPU stats, and firmware protocols PQI, CISS, BMIC, CSMI, and SAS SMP. It integrates with Kbuild through the smartpqi composite module and with the SCSI midlayer through `Scsi_Host`, `scsi_cmnd`, `scsi_device`, SAS rphys, BSG jobs, and RAID/SAS attributes selected by Kconfig.

## Risks
The highest risk is ABI/layout drift. Packed structures, bitfields, endian fields, array sizes, queue element lengths, and alignment constants must match firmware exactly. Changes to `pqi_ctrl_info` and `pqi_scsi_dev` can affect locking, lifecycle, hotplug, reset, and I/O fast paths across multiple implementation files. RAID bypass data has many derived fields; inconsistent interpretation of RAID maps can misroute I/O. Firmware feature bits and default transfer limits gate behavior for encryption, RAID writes, OFA, logging, soft reset, and multi-LUN devices, so a wrong constant can disable required handling or enable unsupported paths.

## Test Signals
Build tests should compile all smartpqi objects with sparse/endian checking and struct layout assumptions intact. Runtime signals include controller initialization in SIS-to-PQI transition, admin queue creation/deletion, operational queue interrupt delivery, logical/physical LUN discovery, SAS transport registration, SMP passthrough, RAID bypass reads/writes for RAID 0/1/5/6, encrypted transfer limit handling, hotplug and AIO state events, LUN reset/TMF completion, heartbeat/offline detection, soft reset, OFA and controller-log memory events, and removal paths for graceful and surprise unplug.
