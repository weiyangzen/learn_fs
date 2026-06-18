# Research: subset-b-005321

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_ctl.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_ctl.c

## Purpose
`pm8001_ctl.c` exposes the pm8001/pm80xx SAS/SATA HBA driver's host-facing sysfs control and diagnostic surface. It publishes read-only controller identity, firmware capability, queue-log, event-log, fatal/non-fatal dump, MPI-state, and counter attributes, plus read/write controls for logging level, non-fatal dump count, and firmware/NVMD update. The file does not implement the main I/O path; instead it bridges Linux SCSI host attributes to state collected in `struct pm8001_hba_info` and to chip-dispatch operations supplied by `pm8001_chips.h`.

## Important APIs, Types, And Functions
The public integration points are the exported attribute groups `pm8001_host_groups` and `pm8001_sdev_groups`, which are consumed by the SCSI host template/device registration path elsewhere in the driver. The host group contains attributes such as `interface_rev`, `fw_version`, `update_fw`, `aap_log`, `iop_log`, `fatal_log`, `non_fatal_log`, `gsm_log`, queue logs, SAS address, and low-level MPI counters. The SCSI device group forwards `sas_ata_sdev_attr_group`.

Most `*_show()` handlers follow the same pattern: convert `struct device *` to `struct Scsi_Host *` using `class_to_shost()`, derive `struct sas_ha_struct *` via `SHOST_TO_SAS_HA()`, then use `sha->lldd_ha` as `struct pm8001_hba_info *`. `pm8001_ctl_mpi_interface_rev_show()`, `pm8001_ctl_fw_version_show()`, `pm8001_ctl_max_out_io_show()`, `pm8001_ctl_max_devices_show()`, `pm8001_ctl_max_sg_list_show()`, and `pm8001_ctl_sas_spec_support_show()` branch on `chip_id == chip_8001` because SPC and later PM80xx chips store main configuration table fields in different union members.

Diagnostic handlers read persistent driver state and firmware-exposed memory: `pm8001_ctl_aap_log_show()` dumps two 32-byte rows from the AAP1 event-log DMA region; `pm8001_ctl_ib_queue_log_show()` and `pm8001_ctl_ob_queue_log_show()` dump 256 dwords from inbound/outbound queue memory and advance `evtlog_ib_offset`/`evtlog_ob_offset`; `pm8001_ctl_iop_log_show()` walks the IOP event log in 32-dword windows under `iop_log_lock`; `pm8001_ctl_gsm_log_show()` delegates to `pm8001_get_gsm_dump()`; and fatal/non-fatal dump readers delegate to PM80xx helper routines.

Firmware write support is centered on `pm8001_store_update_fw()`. It parses a privileged sysfs write in the form `update <firmware>` or `set_nvmd <firmware>`, uses `request_firmware()`, then calls either `pm8001_update_flash()` or `pm8001_set_nvmd()`. `pm8001_update_flash()` validates the image is at least the 28-byte header size, slices each image partition into 4 KiB chunks, populates `struct fw_control_info` inside a `struct pm8001_ioctl_payload`, submits `PM8001_CHIP_DISP->fw_flash_update_req()`, and waits on `nvmd_completion` after every chunk. `pm8001_set_nvmd()` limits the input image to 4096 bytes and sends it through `PM8001_CHIP_DISP->set_nvmd_req()`.

## Control Flow
Sysfs reads are synchronous and usually single-shot. For simple attributes, the handler reads cached configuration table or HBA fields and formats them with `sysfs_emit()`. Queue and firmware-memory logs are stateful reads: each read emits a fixed window and advances a cursor stored on `pm8001_ha`, wrapping at the queue or event-log size. BIOS version reading is a synchronous NVMD transaction: allocate 4096 bytes, issue `get_nvmd_req()` with minor function 7, wait for `nvmd_completion`, print bytes 56 through 60, then free the buffer.

Firmware update control flow has stricter sequencing. `pm8001_store_update_fw()` checks `CAP_SYS_ADMIN`, rejects concurrent updates using `fw_status == FLASH_IN_PROGRESS`, parses the command, loads firmware from userspace firmware search paths, and calls the selected helper. The helper submits one MPI request at a time and blocks until the hardware response handler completes `pm8001_ha->nvmd_completion`. The show side, `pm8001_show_update_fw()`, maps `fw_status` through `flash_error_table` and resets non-progress status back to `FLASH_OK` after reporting.

## State And Persistence Behavior
This file changes in-memory driver state that persists for the HBA lifetime but is not persisted by the kernel itself. `logging_level`, `non_fatal_count`, event-log offsets, IOP log counters, `fw_status`, `fw_image`, and `nvmd_completion` are all fields on `struct pm8001_hba_info`. Firmware and NVMD update operations may persist data to adapter flash/NVMD through hardware commands, but this file only stages buffers and records status; the actual hardware write is implemented through the chip dispatch table.

The sysfs queue/event log cursors mean repeated reads of the same attribute are not idempotent. `ib_log`, `ob_log`, `iop_log`, and `gsm_log` expose the next window on every read and wrap when their per-log limit is reached.

## Dependencies And Integration Points
The file depends on Linux firmware loading, sysfs/device attributes, SCSI host objects, libsas host data, and the pm8001 internal HBA structure. It integrates with `pm8001_hwi.c`/PM80xx dispatch callbacks through `PM8001_CHIP_DISP->get_nvmd_req()`, `set_nvmd_req()`, and `fw_flash_update_req()`, and with PM80xx diagnostic helpers such as `pm80xx_get_fatal_dump()` and `pm80xx_get_non_fatal_dump()`. It also relies on constants and payload layouts from `pm8001_ctl.h`, chip-specific status codes from other pm8001 headers, and DMA regions allocated during adapter initialization.

## Risks And Edge Cases
Several sysfs readers use `sprintf()` directly into a sysfs buffer instead of `sysfs_emit()` or `sysfs_emit_at()`. The fixed output sizes are usually small, but queue/event dump paths should be reviewed whenever window sizes change. The firmware-update path uses `wait_for_completion()` without an obvious timeout; a lost firmware response can hang the sysfs write. `pm8001_store_update_fw()` uses string parsing and command matching based on the user-provided command length; unusually long command tokens deserve bounds review. Firmware status is a single HBA field and protects only the update path, not every NVMD user.

The log readers dereference DMA-backed memory and MMIO-derived regions directly. They depend on successful adapter initialization and valid memory-map entries; defensive null checks are limited. The IOP log reader divides by a computed `max_count` derived from firmware-reported event-log size, so corrupt or zero sizes would be risky. Firmware flashing is privileged but still high impact: it accepts any firmware file name loadable by `request_firmware()` and delegates image validation to header/chunk checks and firmware return codes.

## Test Signals
Useful test signals are sysfs visibility and formatting for all attributes, chip_8001 versus PM80xx table selection, repeated queue/event log reads with wraparound, invalid and unauthorized writes to `update_fw`, firmware load failure status, too-small and too-large firmware image handling, concurrent update rejection, successful completion propagation through `nvmd_completion`, and no regression in fatal/non-fatal dump access. Hardware or emulator coverage should verify that update chunks set `fwControl->offset`, `len`, `size`, and `retcode` correctly and that `fw_status` maps to the expected text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_ctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_ctl.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_ctl.h

## Purpose
`pm8001_ctl.h` is the small support header for the pm8001 sysfs/control implementation. It defines fixed buffer sizes, firmware/NVMD update status values, event-log read window parameters, queue-size constants, and one helper for reading dwords from the AAP1 event-log memory map.

## Important APIs, Types, And Constants
The header defines `IOCTL_BUF_SIZE` as 4096, `HEADER_LEN` as 28, and firmware-image offsets used by `pm8001_update_flash()`. BIOS display logic uses `BIOSOFFSET` and `BIOS_OFFSET_LIMIT` to emit a narrow version string from NVMD data. Status codes such as `FLASH_OK`, `FAIL_OPEN_BIOS_FILE`, `FAIL_FILE_SIZE`, `FAIL_PARAMETERS`, `FAIL_OUT_MEMORY`, and `FLASH_IN_PROGRESS` are written into `pm8001_ha->fw_status` and interpreted by `pm8001_show_update_fw()`.

Diagnostic read constants include `IB_OB_READ_TIMES` for the number of dwords emitted per queue-log read, `SYSFS_OFFSET` for the 1024-byte cursor increment, and queue memory-size constants for PM80xx and PM8001 hardware. The single inline helper, `pm8001_ctl_aap1_memmap(u8 *ptr, int idx, int off)`, reads a `u32` from `ptr + idx * 32 + off` and is used by the AAP1 log sysfs show function.

## Control Flow
The header has no independent control flow. Its constants parameterize control paths in `pm8001_ctl.c`: firmware flashing slices input into 4 KiB chunks with a 28-byte header, BIOS version reads select bytes 56-60, and queue-log sysfs reads emit 256 dwords then advance by 1024 bytes.

## State And Persistence Behavior
No state is stored in this header. Its status values describe in-memory state held by `struct pm8001_hba_info`, and its queue/log sizes describe DMA/MMIO-backed regions whose cursors are stored in the HBA object.

## Dependencies And Integration Points
The header assumes Linux integer typedefs are available through including C files and is tightly coupled to `pm8001_ctl.c`. It also indirectly coordinates with firmware response status constants declared elsewhere because `pm8001_ctl.c` mixes local failure codes from this header with flash-update codes returned by firmware.

## Risks And Edge Cases
`pm8001_ctl_aap1_memmap()` casts a byte pointer to `u32 *`, which assumes alignment and native CPU access semantics suitable for the mapped buffer. The helper does not bounds-check `idx` or `off`; callers must keep indices inside the event-log window. Buffer-size constants are embedded protocol assumptions, so changing them without checking firmware IOMB and sysfs buffer limits can create truncation or overflow risks.

## Test Signals
Compile coverage should catch users of these macros. Behavioral tests should exercise firmware image sizes around 28 bytes, 4096 bytes, and multi-partition boundaries, plus repeated queue-log reads to confirm the `SYSFS_OFFSET` and `IB_OB_READ_TIMES` contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_ctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_defs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_defs.h

## Purpose
`pm8001_defs.h` provides common compile-time limits, chip identifiers, simple protocol enums, memory-region identifiers, and status constants shared across the pm8001 driver. It is the driver-wide vocabulary for chip flavor selection, PHY speeds, data directions, port types, queue capacities, memory-map regions, MPI error returns, PHY control operations, HBA state flags, and link-state values.

## Important APIs, Types, And Constants
`enum chip_flavors` identifies supported SPC/PM80xx device families, including `chip_8001`, `chip_8008`, `chip_8009`, `chip_8018`, `chip_8019`, `chip_8074`, `chip_8076`, `chip_8077`, `chip_8006`, `chip_8070`, and `chip_8072`. Many code paths branch on `chip_8001` versus later chips to select configuration table layouts and BAR-shift behavior.

`enum phy_speed` maps firmware speed bits to 1.5, 3, 6, and 12 Gbps capabilities. `enum data_direction` maps DMA direction to firmware command bits, and `enum port_type` distinguishes SAS and SATA links in per-phy state. Capacity macros define driver limits: `PM8001_MAX_CCB` 1024, `PM8001_MPI_QUEUE` 1024 entries, up to 64 inbound and outbound queues, `PM8001_CAN_QUEUE` 508, 16 phys/ports, 2048 devices, and 64 MSI-X vectors for newer hardware. IOMB sizes are 64 bytes for SPC and 128 bytes for SPCV.

`enum memory_region_num` names DMA memory regions: AAP1 event log, IOP event log, NVMD buffer, firmware flash buffer, forensic memory, and the base count used to derive queue-memory region indices. `USI_MAX_MEMCNT` expands this base count by inbound/outbound queues plus producer/consumer index regions. `enum mpi_err` is used by queue consumption paths as success, busy, or failure. `enum phy_control_type` is the local PHY-control command vocabulary. `enum pm8001_hba_info_flags` distinguishes init-time from run-time behavior.

## Control Flow
The file has no executable control flow. It shapes control flow in C files by fixing array bounds, queue loops, state-machine comparisons, and branch conditions. For example, HWI queue initialization iterates to `pm8001_ha->max_q_num` within the maximums defined here, task scanning uses `PM8001_MAX_CCB`, fatal cleanup may scan `PM8001_MAX_DEVICES`, and completion decoding uses direction and port type values from these enums.

## State And Persistence Behavior
The definitions describe state stored elsewhere, especially `pm8001_hba_info`, per-device entries, queue tables, memory-map entries, and PHY structures. They do not persist anything by themselves. Hardware flash/NVMD persistence is represented only indirectly through memory-region and size constants.

## Dependencies And Integration Points
This header is included by pm8001 driver sources and is coupled to firmware ABI limits. It integrates with libsas by aligning PHY speed and port type concepts with SAS/SATA topology handling. It also integrates with Linux block/SCSI limits through `PM8001_MAX_IO_SIZE`, `PM8001_MAX_DMA_SG`, and `PM8001_MAX_SECTORS`.

## Risks And Edge Cases
Because these are global limits, increasing any queue, device, CCB, or DMA scatter-gather macro can change memory allocation sizes, MMIO table layout expectations, and firmware-visible queue descriptors. `PM8001_MAX_IO_SIZE` determines derived SG and sector limits, so mismatches with firmware or block-layer constraints can cause I/O mapping failures. Chip flavor additions require synchronized updates in dispatch selection, table parsing, and sysfs code; this header alone does not enforce complete support.

## Test Signals
Compile-time test signals include array bounds, switch exhaustiveness in chip dispatch, and no overflow in memory-region count calculations. Runtime signals include correct queue allocation sizes, proper SCSI queue depth, correct link-rate translation, and successful operation across chip_8001 and newer PM80xx hardware families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_hwi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_hwi.c

## Purpose
`pm8001_hwi.c` is the SPC/PM8001 hardware-interface implementation behind the pm8001 driver's chip dispatch table. It initializes the adapter firmware interface, programs MPI configuration and queue tables, handles reset and interrupt processing, consumes outbound IOMBs, translates firmware completions into libsas/SCSI task status, handles SAS/SATA topology events, builds inbound MPI commands for SSP/SMP/SATA I/O and management, and supports NVMD, firmware flash, forensic dump, and device-state operations.

## Important APIs, Types, And Functions
The file exports the SPC dispatch object `pm8001_8001_dispatch`. Its methods include chip initialization/reset/unmap, interrupt enable/disable/ISR, outbound queue processing, PRD building, SMP/SSP/SATA request submission, PHY start/stop/control, device register/deregister, task abort, SSP task management, NVMD get/set, firmware flash update, device-state set, SAS reinitialization, and fatal error handling.

Initialization helpers include `read_main_config_table()`, `read_general_status_table()`, `read_inbnd_queue_table()`, `read_outbnd_queue_table()`, `init_default_table_values()`, and update counterparts that write firmware-visible config and queue descriptors. `pm8001_bar4_shift()` programs the BAR4 translation window and verifies the write. `check_fw_ready()`, `mpi_init_check()`, `mpi_uninit_check()`, `soft_reset_ready_check()`, `pm8001_chip_soft_rst()`, and `pm8001_hw_chip_rst()` implement firmware readiness and reset sequencing.

Ring/IOMB mechanics are handled by `pm8001_mpi_msg_free_get()`, `pm8001_mpi_build_cmd()`, `pm8001_mpi_msg_consume()`, `pm8001_mpi_msg_free_set()`, `process_oq()`, and `process_one_iomb()`. Completion handlers include `mpi_ssp_completion()`, `mpi_ssp_event()`, `mpi_sata_completion()`, `mpi_sata_event()`, `mpi_smp_completion()`, `pm8001_mpi_task_abort_resp()`, `pm8001_mpi_reg_resp()`, `pm8001_mpi_dereg_resp()`, `pm8001_mpi_get_nvmd_resp()`, `pm8001_mpi_set_nvmd_resp()`, `pm8001_mpi_fw_flash_update_resp()`, and `pm8001_mpi_set_dev_state_resp()`.

Topology and deferred error handling are split between interrupt-time handlers and workqueue recovery. `mpi_hw_event()` decodes hardware events and delegates SAS/SATA up/down handling to `hw_event_sas_phy_up()`, `hw_event_sata_phy_up()`, and `hw_event_phy_down()`. `pm8001_handle_event()` queues `pm8001_work_fn()`, which performs operations unsuitable for hard IRQ context, such as task query/abort, I_T nexus reset/event handling, NCQ link abort, and fatal-error cleanup.

## Control Flow
Adapter bring-up starts with `pm8001_chip_init()`: read PCI device ID, shift BAR4 for 8081/0x0042 controllers, poll firmware scratchpad readiness, derive main/general/inbound/outbound table addresses from scratchpad 0, initialize default host-side table values from DMA memory regions, read firmware tables, write updated main and queue tables back, apply PHY SSC/open-retry tuning for non-8081 hardware, notify firmware with `SPC_MSGU_CFG_TABLE_UPDATE`, verify MPI state, then set interrupt coalescing registers.

Command submission builds a packed payload defined in `pm8001_hwi.h`, allocates an inbound ring slot under the inbound queue lock, copies and zero-pads the payload, writes a valid MPI header with opcode/category/response queue/buffer count, and updates the firmware producer-index doorbell. SSP, SATA, SMP, task-management, device registration, PHY, NVMD, and firmware update functions are mostly payload builders around this common `pm8001_mpi_build_cmd()` path.

Interrupt handling disables the relevant interrupt source, drains the outbound queue, dispatches every valid IOMB by opcode, frees the outbound ring entry by advancing the consumer index, and re-enables interrupts. `process_one_iomb()` is the central opcode switch from firmware response opcodes to completion/event handlers. Completion handlers locate the CCB by firmware tag, derive the `sas_task`, set `task_status.resp/stat/residual/open_rej_reason`, update `running_req` where applicable, free the CCB, set SAS task-state bits, and invoke `task_done()` unless the upper layer already aborted the task.

Hardware events update libsas topology. SAS phy-up copies the identify frame, sets target protocol to SSP or SMP, updates link rates, emits `PHYE_OOB_DONE`, records attached SAS address under `frame_rcvd_lock`, optionally delays at run time for disk spin-up, and notifies `PORTE_BYTES_DMAED`. SATA phy-up copies the D2H FIS, synthesizes or extracts a SAS address, marks SATA protocol, and notifies libsas. Broadcast/link/error events acknowledge firmware where required and notify libsas port/phy events.

## State And Persistence Behavior
The file maintains volatile HBA state in `pm8001_hba_info`: configuration table snapshots, queue descriptors, producer/consumer indices, memory-map regions, PHY/port attachment state, SAS address, CCB table, device table, logging/dump cursors, completions, and firmware status side effects. It also changes hardware-visible persistent state through NVMD and firmware flash update commands, and may change controller runtime state through reset, PHY control, device registration, and SAS reinitialization.

Queue state is shared between host memory and firmware MMIO/PCI windows: inbound queues use host `producer_idx` and firmware consumer index, while outbound queues use firmware producer index and host `consumer_idx`. Reset paths deliberately alter MMIO registers, scratchpads, BAR translation, parity-check controls, GPIO output state, and top-level reset bits.

## Dependencies And Integration Points
The implementation depends on Linux PCI/MMIO helpers, DMA scatter-gather mapping, workqueues, spinlocks, completions, libsas task and topology APIs, ATA task structures, tracepoints, and pm8001 internal allocation helpers. It integrates with the rest of the driver through `pm8001_sas.h`, `pm8001_chips.h`, `pm8001_hwi.h`, `pm8001_ctl.h`, `pm80xx_tracepoints.h`, CCB/tag helpers, device lookup/free helpers, fatal-dump helpers, and chip dispatch selection. It is also tightly coupled to the firmware MPI ABI expressed as opcodes, response status codes, packed payload structs, scratchpad bits, and register offsets.

## Risks And Edge Cases
This file is concurrency and hardware-ordering sensitive. Ring indices are protected by queue/HBA spinlocks, but completion handlers also interact with task-state locks and upper-layer aborts; ordering bugs can cause double completion, leaked CCBs, or missed `running_req` decrements. Some completion paths return early when task pointers are unexpected and may rely on higher-level cleanup. `wait_for_completion()` users in control paths depend on these handlers always completing the right object.

Reset and BAR-shift code writes many magic register values and uses polling delays; incorrect chip identification or interrupted sequencing can leave the adapter inaccessible. Firmware readiness and MPI init/uninit use fixed one-second busy waits. Several handlers decode firmware tags directly into `ccb_info[tag]`, so corrupted tags would be dangerous unless validated elsewhere. The fatal-error work path scans all CCBs and devices and performs broad cleanup; it should be stress-tested with mixed internal and SCSI tasks.

DMA handling requires balanced mapping and unmapping. SMP request setup unmaps on immediate submission failures, while normal completion unmapping is likely handled by common task cleanup; that division should be preserved. SATA NCQ error handling may trigger libata link aborts asynchronously. Status translation is extensive and protocol-specific; adding firmware status codes requires updating the switch tables to avoid defaulting to misleading SCSI results.

## Test Signals
High-value tests include adapter initialization on chip_8001 and 8081-like BAR-shift hardware, queue full behavior in `pm8001_mpi_msg_free_get()`, valid/invalid outbound IOMB dispatch, interrupt drain with MSI-X and legacy interrupts, successful SSP/SATA/SMP completions, every major firmware error-status translation, upper-layer abort races, task-management abort responses, direct and expander-attached SATA address handling, SAS/SATA phy-up/down notifications, broadcast-change acknowledgement, NVMD get/set completion ordering, firmware flash chunk completion, soft reset readiness and recovery, and fatal-error cleanup under outstanding I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_hwi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_hwi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_hwi.h

## Purpose
`pm8001_hwi.h` defines the SPC/PM8001 hardware-interface ABI used by `pm8001_hwi.c`: inbound and outbound MPI opcodes, packed IOMB request/response payloads, hardware event/status values, register offsets, scratchpad/reset bit definitions, NVMD constants, and device-registration result codes. It is the firmware wire-format contract for the SPC generation of the driver.

## Important APIs, Types, And Constants
The opcode blocks map host-to-firmware requests such as `OPC_INB_PHYSTART`, `OPC_INB_SSPINIIOSTART`, `OPC_INB_SMP_REQUEST`, `OPC_INB_REG_DEV`, `OPC_INB_SATA_HOST_OPSTART`, `OPC_INB_LOCAL_PHY_CONTROL`, `OPC_INB_FW_FLASH_UPDATE`, `OPC_INB_GET_NVMD_DATA`, `OPC_INB_SET_NVMD_DATA`, and `OPC_INB_SAS_RE_INITIALIZE`, plus firmware-to-host responses such as `OPC_OUB_HW_EVENT`, `OPC_OUB_SSP_COMP`, `OPC_OUB_SMP_COMP`, `OPC_OUB_SATA_COMP`, `OPC_OUB_SATA_EVENT`, `OPC_OUB_SSP_EVENT`, abort responses, NVMD responses, and device-state responses.

Packed request/response structs define the exact IOMB payloads: `mpi_msg_hdr`, `phy_start_req`, `phy_stop_req`, SATA FIS wrappers, `sata_completion_resp`, `hw_event_resp`, `reg_dev_req`, `dereg_dev_req`, `dev_reg_resp`, `local_phy_ctl_req/resp`, `hw_event_ack_req`, `ssp_completion_resp`, `sata_event_resp`, `ssp_event_resp`, `general_event_resp`, `smp_req`, `smp_completion_resp`, `task_abort_req/resp`, diagnostic commands, `set_dev_state_req/resp`, `sas_re_initialization_req`, `sata_start_req`, `ssp_ini_tm_start_req`, `ssp_ini_io_start_req`, `fw_flash_Update_req/resp`, and NVMD get/set structures.

The header also defines firmware event/status vocabularies: `HW_EVENT_*`, port states, `IO_*` completion codes, flash/NVMD mode bits, `DEVREG_*` registration statuses, MSGU register offsets, MSI-X table offsets, scratchpad state bits, main/general status table offsets, BAR-shift/reset register addresses, GSM/MBIC/GPIO addresses, and masks such as `OPCODE_BITS`, `NDS_BITS`, `PDS_BITS`, `SHIFT_REG_64K_MASK`, and `SHIFT_REG_BIT_SHIFT`.

## Control Flow
There is no executable control flow, but the file drives runtime switches in `pm8001_hwi.c`. Inbound opcodes select the firmware command built by request helpers. Outbound opcodes select the completion handler in `process_one_iomb()`. `HW_EVENT_*` values select topology handling in `mpi_hw_event()`. `IO_*` values select SCSI/libsas status translation in SSP/SATA/SMP completion handlers. Register and scratchpad constants control initialization, interrupt masking, BAR shifting, soft reset, and forensic dump reads.

## State And Persistence Behavior
The packed structs represent transient messages in inbound/outbound DMA rings. Register constants name hardware state that persists until reset or firmware changes it. NVMD and firmware flash request/response structures are used for persistent adapter-storage operations, but the header stores no state itself.

## Dependencies And Integration Points
The header includes Linux integer types and `scsi/libsas.h` because several payloads embed `struct sas_identify_frame`, `struct dev_to_host_fis`, and `struct ssp_response_iu`. It is tightly integrated with `pm8001_hwi.c` and any code that builds or decodes SPC IOMBs. It also binds the driver to little-endian firmware fields through `__le32` and `__le64`, packed layout, and 4-byte alignment attributes.

## Risks And Edge Cases
Because this header is an ABI contract, struct layout, alignment, field size, and opcode values must not change casually. Flexible or variable protocol data is represented with packed fixed-size IOMBs and in one case a trailing `ssp_response_iu`; users must ensure they do not overrun the configured IOMB size. Duplicate or stale constants can hide firmware-generation differences, and the warning around `IO_ERROR_UNKNOWN_GENERIC` indicates status numbering is used as an index elsewhere. Endianness mistakes are easy because all firmware fields must be converted at the use site.

## Test Signals
Compile-time assertions or build warnings around packed struct sizes would be valuable. Runtime validation should cover representative inbound command payloads, outbound opcode dispatch, IO status translation for common and rare `IO_*` values, hardware event decoding, register offset access during init/reset, NVMD direct and indirect modes, and firmware flash response statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_hwi.h -->
