# sources/distributed-fs/ceph-client/drivers/scsi/hpsa_cmd.h

## Purpose

`hpsa_cmd.h` defines the packed CISS/HPSA command ABI shared between the Smart Array driver and controller firmware. It supplies status codes, SCSI/BMIC opcodes, LUN encodings, command-list and error-info layouts, I/O accelerator mode 1 and mode 2 command formats, task-management request formats, configuration/transport tables, RAID map structures, report-LUN payloads, and large BMIC identify/sense data structures.

## Important APIs, Types, and Functions

- Status and task-management constants include `CMD_SUCCESS`, `CMD_TARGET_STATUS`, transport and hardware error codes, driver-local `CMD_CTLR_LOCKUP`, and `CISS_TMF_*` result values.
- SCSI/VPD/BMIC constants define inquiry/report opcodes, logical-volume state values, cache flush and firmware flash commands, physical-device identify commands, diagnostic options, and subsystem/storage-box sense commands.
- `struct raid_map_data` and `struct raid_map_disk_data` describe logical-to-physical accelerator mapping, encryption flags, disk layout, striping, row counts, and per-entry I/O accelerator handles.
- `struct ReportLUNdata`, `struct ext_report_lun_entry`, and `struct ReportExtendedLUNdata` define logical and extended physical LUN discovery payloads.
- `union LUNAddr`, `union SCSI3Addr`, `struct PhysDevAddr`, and `struct LogDevAddr` encode the 8-byte CISS LUN address formats used in command headers.
- `struct CommandListHeader`, `struct RequestBlock`, `struct ErrDescriptor`, `struct SGDescriptor`, `union MoreErrInfo`, and `struct ErrorInfo` form the normal CISS command, S/G, and error contract.
- `struct CommandList` wraps the hardware command record with driver-private state: bus address, controller pointer, command type, command index, completion wait, Linux `scsi_cmnd`, work item, accelerator physical-disk pointer, retry flag, device pointer, and an aligned `atomic_t refcount`.
- `struct io_accel1_cmd`, `struct io_accel2_cmd`, `struct ioaccel2_sg_element`, and `struct io_accel2_scsi_response` define bypass command formats and completion/error responses.
- `struct hpsa_tmf_struct` defines I/O accelerator mode 2 task-management requests.
- `struct CfgTable` and `struct TransTable_struct` expose firmware transport capabilities, active mode, command limits, heartbeat, driver support, task-management support, event notify bits, block-fetch values, reply queue count/size, and reply queue addresses.
- `struct bmic_identify_controller`, `struct bmic_identify_physical_device`, `struct bmic_sense_subsystem_info`, and `struct bmic_sense_storage_box_params` carry detailed firmware inventory, physical-drive, enclosure, health, endurance, path, and encryption-key metadata.

## Control Flow and State

This header contains no executable driver flow beyond a compile-time `static_assert` that keeps `CommandList.refcount` properly aligned for architectures that reject unaligned atomics. Runtime flow is imposed by the C files that allocate these structures in DMA-coherent memory, fill little-endian fields, submit them through the access methods in `hpsa.h`, and interpret the returned `ErrorInfo` or accelerator response. The ABI state is mostly transient per command, but `CfgTable`, `TransTable_struct`, report-LUN data, RAID maps, and BMIC identify data are cached by the driver to shape topology, queue limits, offload decisions, and health reporting.

## Dependencies and Integration Points

The file depends on Linux fixed-width types, endian annotations, packing/alignment attributes, `BUILD_BUG`/`static_assert` support, `atomic_t`, `struct scsi_cmnd`, `struct completion`, and HPSA-private forward declarations. It is consumed by `hpsa.h` and the HPSA implementation whenever commands are allocated, initialized, DMA-mapped, submitted, completed, or decoded. The structures are also the contract with controller firmware, so their packing and byte ordering are integration points as important as C function signatures.

## Risks

- Packed hardware structures are layout-sensitive; changing field order, alignment, sizes, or endian conversions can break firmware communication.
- `CommandList` must remain 128-byte aligned and keep `refcount` naturally aligned despite containing packed hardware substructures.
- CISS completion tags reuse low address bits for mode/error/block-fetch metadata, so command pool alignment and tag masking must remain consistent with `COMMANDLIST_ALIGNMENT`, `DIRECT_LOOKUP_SHIFT`, and mode-specific command types.
- Large BMIC structures encode many firmware-defined offsets. Partial initialization or short DMA buffers can misinterpret drive health, encryption, path, or enclosure data.
- Accelerator command paths have separate S/G limits and response formats. Mixing normal CISS, ioaccel1, and ioaccel2 fields risks bad DMA, missing sense data, or incorrect residual reporting.

## Test Signals

- Compile-time assertions and `sizeof`/offset-sensitive build coverage should catch accidental alignment regressions.
- Hardware or emulator tests should validate inquiry/report-LUN discovery, BMIC identify/controller parameter commands, normal CISS S/G I/O, and both I/O accelerator modes when supported.
- Fault-path tests should inspect sense copying, residual counts, task-management responses, accelerator-disabled status, and controller lockup marking.
- Discovery tests should confirm RAID map parsing, physical-drive inventory, logical-volume status states, encryption flags, and queue-depth limits derived from BMIC data.
