# sources/distributed-fs/ceph-client/drivers/scsi/arcmsr/arcmsr.h

## Purpose
`arcmsr.h` is the shared hardware contract for the Areca ARC11xx/12xx/16xx/188x SCSI RAID driver. It defines driver limits, PCI device IDs, firmware message opcodes, memory-mapped register layouts for adapter generations A through F, command/control data structures, adapter state, CCB state, sense data layout, interrupt bit definitions, and the small exported interface used by `arcmsr_attr.c`.

## Important APIs, types, and constants
- Driver identity and tunables include `ARCMSR_NAME`, `ARCMSR_DRIVER_VERSION`, queue-depth bounds, transfer-size bounds, target/lun limits, and API buffer sizes.
- Management message ABI is represented by `struct CMD_MESSAGE`, `struct CMD_MESSAGE_FIELD`, `ARCMSR_MESSAGE_*` control codes, and `ARCMSR_MESSAGE_RETURNCODE_*` values. These are used by SCSI `READ_BUFFER`/`WRITE_BUFFER` management commands and by sysfs binary attributes.
- DMA scatter/gather descriptors are `struct SG32ENTRY` and `struct SG64ENTRY`; `IS_SG64_ADDR` marks 64-bit SG entries in the firmware CDB stream.
- `struct ARCMSR_CDB` is the firmware command descriptor sent for ordinary SCSI commands. It carries bus/target/lun, CDB bytes, data length, flags, device status, sense data, and variable SG entries.
- Adapter register maps are split by hardware family: `MessageUnit_A`, `MessageUnit_B`, `MessageUnit_C`, `MessageUnit_D`, `MessageUnit_E`, and `MessageUnit_F`. The layouts encode doorbells, message buffers, post/done queues, reset registers, and completion queue indices.
- `struct AdapterControlBlock` is the central per-host state object: adapter type, `pci_dev`, `Scsi_Host`, mapped register union, coherent DMA regions, locks, circular management queues, device map, firmware metadata, timers, work item, interrupt state, queue sizing, CCB pool, completion queue, and optional XOR host-buffer allocation state.
- `struct CommandControlBlock` binds one SCSI command to one firmware CDB, physical address, state flags, and free-list linkage.
- Exported declarations connect this header to implementation files: `arcmsr_write_ioctldata2iop`, `arcmsr_Read_iop_rqbuffer_data`, `arcmsr_clear_iop2drv_rqueue_buffer`, `arcmsr_get_iop_rqbuffer`, `arcmsr_host_groups`, `arcmsr_alloc_sysfs_attr`, and `arcmsr_free_sysfs_attr`.

## Control flow and state model
The header establishes an adapter-type dispatch model. `AdapterControlBlock.adapter_type` selects the proper `MessageUnit_*` register layout and per-generation doorbell/queue protocols in `arcmsr_hba.c`. CCBs live in a coherent DMA pool and cycle through free-list, posted, firmware-owned, done, and completed states via `startdone` and `ccboutstandingcount`. Management traffic uses in-memory circular `rqbuffer`/`wqbuffer` rings with `rqbuf_*` and `wqbuf_*` indices protected by dedicated locks.

## Persistence behavior
The file itself has no persistent storage. Runtime state is volatile kernel memory plus device firmware-visible coherent DMA memory. Firmware metadata copied into `firm_model`, `firm_version`, `device_map`, queue limits, and PIC status persists only for the lifetime of the host instance. Timers periodically refresh firmware device maps and optionally firmware time, but those are not durable driver-side stores.

## Dependencies and integration points
The header depends on Linux interrupt, PCI, DMA, SCSI, timer, workqueue, and sysfs concepts through the structures consumed by `arcmsr_hba.c` and `arcmsr_attr.c`. Its register definitions integrate directly with Areca firmware specs and with the PCI ID table. The exported `arcmsr_host_groups` integrates read-only host attributes into the SCSI host template.

## Risks and edge cases
- Register layouts and bit definitions are hardware ABI; mistakes can cause lost interrupts, firmware hangs, or wrong reset behavior.
- Several adapter generations share helper paths but not identical semantics, especially Type F host buffers and Type E/F toggle doorbells.
- Queue and SG limits are negotiated from firmware configuration; mismatches between `ccbsize`, SG page sizing, and firmware limits can corrupt command DMA.
- `AdapterControlBlock` carries many independent locks and flags. Callers must obey the intended lock ownership for CCB free lists, post/done queues, and management buffers.
- `devstate` is bounded by `ARCMSR_MAX_TARGETID` and `ARCMSR_MAX_TARGETLUN`; command paths must not address outside these limits.

## Test signals
- Build coverage should compile all adapter-type branches and validate packed SG/CDB layout assumptions.
- Probe tests should verify firmware config parsing populates host limits and firmware strings correctly.
- Runtime signals are successful SCSI host registration, sysfs host attributes, interrupt delivery, command completion under load, management buffer read/write behavior, hotplug device-map changes, suspend/resume, abort, and bus reset.
