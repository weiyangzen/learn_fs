# subset-b-005323 research

Grouped research for the PM8001 PM80xx hardware-interface files in `sources/distributed-fs/ceph-client/drivers/scsi/pm8001`. Each section preserves the original source path and is intended to be split into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_hwi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_hwi.c

## Purpose

`pm80xx_hwi.c` is the SPCv/PM80xx-generation hardware interface implementation for the `pm8001` SAS/SATA host adapter driver. It provides the `pm8001_80xx_dispatch` operation table used by PM8008/8009/8018/8019/807x/8006-class chips, handles firmware readiness and MPI table setup, manages chip reset and interrupts, builds inbound MPI IOMB requests for SSP/SMP/SATA/PHY/device operations, decodes outbound completion and event IOMBs, reports fatal/non-fatal controller dumps through sysfs helpers, and integrates optional controller encryption and tracepoints.

## Important APIs, Types, and Functions

The exported or dispatch-visible entry points are `pm8001_80xx_dispatch`, `pm80xx_set_thermal_config()`, `pm8001_set_phy_profile()`, `pm8001_set_phy_profile_single()`, `pm80xx_get_fatal_dump()`, `pm80xx_get_non_fatal_dump()`, and `pm80xx_fatal_errors()`. Internal initialization helpers include `check_fw_ready()`, `init_pci_device_addresses()`, `init_default_table_values()`, table readers/writers for main/GST/inbound/outbound/PHY-attribute tables, and `mpi_init_check()`. Reset and interrupt handling are implemented by `pm80xx_chip_soft_rst()`, `pm80xx_hw_chip_rst()`, `pm80xx_chip_interrupt_enable()`, `pm80xx_chip_interrupt_disable()`, `pm80xx_chip_is_our_interrupt()`, `pm80xx_chip_isr()`, and `process_oq()`.

Request builders include `pm80xx_chip_smp_req()`, `pm80xx_chip_ssp_io_req()`, `pm80xx_chip_sata_req()`, `pm80xx_chip_phy_start_req()`, `pm80xx_chip_phy_stop_req()`, `pm80xx_chip_reg_dev_req()`, `pm80xx_chip_phy_ctl_req()`, `pm80xx_hw_event_ack_req()`, `pm80xx_set_sas_protocol_timer_config()`, `pm80xx_encrypt_update()`, and `mpi_set_phy_profile_req()`. Completion and event handlers include `mpi_ssp_completion()`, `mpi_ssp_event()`, `mpi_sata_completion()`, `mpi_sata_event()`, `mpi_smp_completion()`, `mpi_hw_event()`, `mpi_phy_start_resp()`, `mpi_phy_stop_resp()`, controller config/PHY profile/encryption response handlers, and `process_one_iomb()`.

The file uses the protocol structures and constants from `pm80xx_hwi.h`, core driver state from `struct pm8001_hba_info`, `struct pm8001_ccb_info`, `struct pm8001_device`, `struct pm8001_phy`, and `struct pm8001_port`, plus libsas/libata types such as `struct sas_task`, `struct domain_device`, `struct task_status_struct`, and `struct ata_queued_cmd`.

## Control Flow

Probe-time initialization enters through `pm80xx_chip_init()` from the dispatch table. It waits for firmware components in scratchpad 1, clears the controller fatal-error flag, discovers the MPI configuration table through scratchpad 0 BAR/offset encoding, validates the `"PMCS"` signature, derives addresses for the main, general status, inbound queue, outbound queue, interrupt vector, PHY attribute, and fatal dump tables, initializes host-side queue descriptors from DMA regions, reads firmware-provided table values, writes host updates back into the main and queue tables, and rings `SPCv_MSGU_CFG_TABLE_UPDATE`. `mpi_init_check()` then waits for the inbound doorbell bit to clear and for the GST MPI state to become `GST_MPI_STATE_INIT`, including the required post-init delay before commands are issued.

Post-init sends a SAS protocol timer config page and, when the chip descriptor advertises encryption, reads scratchpad 3 to populate `pm8001_ha->encrypt_info`. A specific encryption error status triggers `pm80xx_encrypt_update()`, which sends a KEK management request to persist key state to flash.

Normal I/O starts when upper driver code allocates a CCB and calls the dispatch request functions. `pm80xx_chip_get_q_index()` maps a block request unique tag to an inbound hardware queue when a request is present. SSP and SATA builders fill controller IOMB payloads with device IDs, tags, direction bits, CDB/FIS data, total transfer length, and either direct DMA addresses or an extended PRD table built by `pm8001_chip_make_sg()`. Single-entry SGs are checked for 4 GiB boundary crossings and converted to a PRD table when needed. Optional encryption changes the opcode to `OPC_INB_SSP_INI_DIF_ENC_IO` or `OPC_INB_SATA_DIF_ENC_IO`, sets encryption enable bits and XTS mode, and derives tweak values from SCSI CDB or ATA LBA fields. SMP requests DMA-map request/response scatterlists, choose direct mode for very short frames or indirect mode for larger payloads, fill long request/response DMA descriptors, and unmap only on build failure because normal completion cleanup is handled later.

Interrupt handling disables the vector, drains the outbound queue under `oq_lock`, then reenables the vector. `process_oq()` first treats the last queue vector as the programmed fatal-error vector and checks scratchpad readiness; firmware fatal errors set `controller_fatal_error`, emit a uevent, signal `pm8001_handle_event(..., IO_FATAL_ERROR)`, and dump scratchpad registers. Otherwise it repeatedly consumes outbound IOMBs, dispatches by opcode in `process_one_iomb()`, and frees each message back to firmware with `pm8001_mpi_msg_free_set()`.

Completion handlers translate PM80xx MPI status codes into libsas task statuses. SSP/SMP/SATA success, underrun, overflow, abort, no-device, open reject, IT nexus loss, NCQ, DMA, and protocol error statuses populate `task_status_struct`, adjust residuals/open-reject reasons, decrement per-device `running_req` when appropriate, clear `SAS_TASK_STATE_PENDING`, set `SAS_TASK_STATE_DONE`, and free CCBs through the normal done or abort-aware paths. SATA completion also copies returned FIS data into `struct ata_task_resp` for protocol responses. Several transport events call `pm8001_handle_event()` to trigger broader recovery rather than completing a single task.

Hardware events update libsas-visible topology. SAS and SATA PHY-up events set port/PHY state, link rate, attached protocol/device type, frame receive buffers, attached SAS addresses, and notify libsas with `PHYE_OOB_DONE`. PHY-down, port invalid, reset timeout, recovery timeout, broadcast, and link-error events notify libsas port/PHY events, acknowledge selected firmware events back to the controller, complete pending enable/reset completions, or disconnect PHYs. PHY start/stop and config responses mostly update local state and free tags.

Fatal and non-fatal dump sysfs helpers are multi-call readers. Fatal dump reading uses the fatal dump table, BAR shifting via `MEMBASE_II_SHIFT_REGISTER`, forensic DMA memory, accumulated transfer counters, and firmware handshakes/status polling to stream chunks as hexadecimal words. Non-fatal dump reading programs the dump table with the forensic DMA buffer, rings the nonfatal dump doorbell, polls transfer status, emits continuation/done/error markers, and tracks accumulated length across reads.

## State and Persistence Behavior

Most state is volatile driver/controller state rooted in `pm8001_hba_info`: MMIO table addresses, queue tables, producer/consumer indexes, fatal dump cursors, fatal-error flags, encryption status, PHY/port topology, CCBs, and per-device running request counters. Persistent hardware state can be affected indirectly by controller firmware or flash operations: `pm80xx_encrypt_update()` stores encryption/keycard state through KEK management, `pm8001_set_phy_profile*()` sends analog PHY profile values, thermal and SAS protocol timer pages configure firmware runtime policy, and firmware/nonvolatile operations are dispatched to common PM8001 helpers from `pm8001_chips.c`.

Queue state is shared between host memory and firmware tables. Inbound queues hold host-produced IOMBs and firmware-visible consumer indexes; outbound queues hold firmware-produced IOMBs and host-visible consumer indexes. Interrupt masks and doorbells are MMIO state. Task lifetime is guarded by CCB ownership, libsas task-state locks, queue locks, and tag allocation/freeing, but most firmware command payloads are transient stack objects copied into MPI queues by `pm8001_mpi_build_cmd()`.

## Dependencies and Integration Points

This file depends on Linux PCI/MMIO helpers through `pm8001_cr32/cw32/mr32/mw32`, SCSI/libsas/libata task and topology APIs, DMA mapping and scatterlists, block multiqueue tags, kernel completions/spinlocks/wait semantics, kobject uevents, PM8001 common helpers from `pm8001_sas.h`, `pm8001_chips.h`, and `pm8001_ctl.h`, and the tracepoints in `pm80xx_tracepoints.h`. The dispatch table is referenced by chip descriptors in `pm8001_init.c`, sysfs dump callbacks are reached through `pm8001_ctl.c`, completion tracepoints are emitted from common code in `pm8001_sas.c`, and request issue tracing is emitted for SATA I/O here.

## Risks and Edge Cases

The highest-risk code is the interrupt/completion path because it runs under outbound queue locking while some SATA error paths temporarily drop and reacquire the lock to complete tasks. Missing tag validation could turn malformed firmware tags into out-of-bounds CCB access; handlers generally trust firmware-provided tags. Task lifetime races are subtle when completions arrive after upper-layer aborts, when `t`, `t->lldd_task`, or `t->dev` is absent, or when error events call `pm8001_handle_event()` instead of normal completion. Running request counters must be decremented exactly once on each path.

DMA setup is sensitive to 4 GiB boundary handling and endian consistency. SSP builders use `cpu_to_le32()` for normal DMA addresses, while the SATA normal path stores some low/high address fields as raw `u32`; this may be intentional because of structure field types, but it is worth auditing on non-little-endian builds. SMP mapping paths rely on later cleanup to unmap successful maps. Direct SMP mode uses a controller-wide `smp_exp_mode`, so concurrent SMP commands could observe mode state globally rather than per-task if multiple SMP requests are outstanding.

Firmware readiness and reset code is hardware-timing sensitive. Doorbell and scratchpad polling use fixed sleeps and timeout counts that vary by 12G/SPC generation. Soft reset may proceed after MPI uninit failure only in a narrow bootloader-state case; fatal controller state bypasses MPI uninit. Fatal/non-fatal dump readers maintain state across sysfs reads in the HBA and can be confused by interleaved readers or partial reads. The fatal dump output uses repeated `sprintf()`/`snprintf()` into sysfs buffers, so PAGE_SIZE boundaries and accumulated formatting need careful testing.

Topology event handling assumes `phy_id` and `port_id` from firmware are valid indexes. Several events only log or partially acknowledge firmware conditions. Encryption is limited to selected READ/WRITE commands and XTS tweak derivation from 10-byte CDB or ATA fields, so other command sizes or protection modes are not covered here.

## Test Signals

Useful test signals include probe/init on each supported chip family, firmware table address validation, multi-queue inbound/outbound operation, MSI-X and non-MSI-X interrupt masking, fatal-vector behavior, clean module remove/reset, SAS/SATA PHY up/down/recovery/broadcast sequences, direct and expander-attached SATA registration, SSP/SATA/SMP normal I/O, underrun/overflow/open-reject/IT nexus loss/NCQ error completions, task abort races, SMP direct and indirect payloads, SG lists with one segment crossing 4 GiB, encrypted SAS/SATA read/write paths, thermal config response, PHY profile programming, and sysfs fatal/non-fatal dump reads across multiple PAGE_SIZE calls. Trace validation should check `pm80xx_request_issue` from SATA requests and `pm80xx_mpi_build_cmd`/`pm80xx_request_complete` from shared driver paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_hwi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_hwi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_hwi.h

## Purpose

`pm80xx_hwi.h` is the PM80xx/SPCv firmware-interface contract used by `pm80xx_hwi.c` and the common PM8001 driver code. It defines inbound and outbound MPI opcodes, packed IOMB request/response layouts, hardware event/status code values, controller configuration-table offsets, queue-table offsets, scratchpad/reset/MMIO register offsets, encryption/thermal/SAS timer constants, and timeout values.

## Important APIs, Types, and Functions

There are no functions in this header. The important API surface is the collection of constants and packed structures that must match firmware ABI. Opcode defines cover inbound requests such as `OPC_INB_PHYSTART`, `OPC_INB_SSPINIIOSTART`, `OPC_INB_SMP_REQUEST`, `OPC_INB_SATA_HOST_OPSTART`, `OPC_INB_LOCAL_PHY_CONTROL`, `OPC_INB_SET_CONTROLLER_CONFIG`, `OPC_INB_REG_DEV`, encryption opcodes, KEK/DEK management, and outbound completions/events such as `OPC_OUB_SSP_COMP`, `OPC_OUB_SMP_COMP`, `OPC_OUB_SATA_COMP`, `OPC_OUB_HW_EVENT`, `OPC_OUB_DEV_REGIST`, and SPCv-specific response opcodes.

Core IOMB structures include `struct mpi_msg_hdr`, `phy_start_req`, `phy_stop_req`, `sata_completion_resp`, `hw_event_resp`, `thermal_hw_event`, `reg_dev_req`, `dereg_dev_req`, `dev_reg_resp`, `local_phy_ctl_req`, `hw_event_ack_req`, `phy_start_resp`, `phy_stop_resp`, `ssp_completion_resp`, `sata_event_resp`, `ssp_event_resp`, `smp_req`, `smp_completion_resp`, `task_abort_req`, diagnostic request/response structs, `set_dev_state_req`, `sata_start_req`, `ssp_ini_tm_start_req`, `ssp_info_unit`, `ssp_ini_io_start_req`, `ssp_dif_enc_io_req`, flash/NVM structs, controller config structs, `kek_mgmt_req`, `dek_mgmt_req`, PHY profile structs, `SASProtocolTimerConfig_t`, and SPCv response structs.

The header also defines bitfield `struct sas_identify_frame_local` separately for little- and big-endian bitfield order, data-plane response status values (`IO_SUCCESS`, `IO_UNDERFLOW`, `IO_OPEN_CNX_ERROR_*`, `IO_XFER_*`, encryption/DIF errors), hardware event values (`HW_EVENT_SAS_PHY_UP`, `HW_EVENT_PHY_DOWN`, `HW_EVENT_BROADCAST_CHANGE`, reset/recovery events), port states, and register/table offsets such as `MSGU_IBDB_SET`, `MSGU_ODMR`, `MSGU_SCRATCH_PAD_*`, `MAIN_*`, `GST_*`, `PSPA_*`, `IB_*`, `OB_*`, `SPC_REG_SOFT_RESET`, and `MEMBASE_II_SHIFT_REGISTER`.

## Control Flow

This file has no runtime control flow, but it determines the control flow in `pm80xx_hwi.c`: opcodes select cases in `process_one_iomb()`, hardware event constants select cases in `mpi_hw_event()`, status constants select cases in SSP/SMP/SATA completion handlers, and table/register offsets determine how initialization, reset, interrupts, and dump capture read or write hardware state. The struct layouts also dictate what payload fields request builders populate before calling `pm8001_mpi_build_cmd()` and what fields completion handlers decode after firmware writes an outbound IOMB.

## State and Persistence Behavior

The header itself stores no runtime state. It defines the binary representation of transient IOMBs exchanged through DMA queues and the layout of firmware-persistent or firmware-owned MMIO tables. Some constants control persistent or semi-persistent controller behavior when used by implementation code, such as PHY profiles, encryption key management, event-log buffers, thermal thresholds, SAS protocol timers, fatal dump tables, and NVM/flash partition operations.

All structures are packed and 4-byte aligned where the firmware ABI expects dword IOMB layout. Fields are mostly `__le32`/`__le64`, so callers must convert CPU endian values before queueing requests and convert firmware values after reading completions.

## Dependencies and Integration Points

The header depends on `<linux/types.h>` and `<scsi/libsas.h>` for fixed-width types, endian annotations, SAS address sizes, and SAS frame/FIS types. It is included by `pm80xx_hwi.c` and may be consumed by common PM8001 helper code that handles shared responses. It forms the local mirror of firmware documentation, so changes must remain synchronized with controller firmware for all chip generations that share `pm8001_80xx_dispatch`.

## Risks and Edge Cases

The main risk is ABI drift or layout mismatch. A wrong opcode, field offset, alignment, endian annotation, or structure size can cause firmware to interpret host requests incorrectly or the driver to mis-handle completions. The header contains very large status enumerations with sparse and overlapping-looking values; adding new statuses without updating completion switch logic can lead to generic failures. One define appears malformed, `IO_XFR_ERROR_DEK_INDEX_OUT_OF_BOUNDS0x2046`, which lacks the normal separation between name and value and is a candidate audit target if this code is built with encryption error paths enabled.

The duplicate definitions for `MBIC_AAP1_ADDR_BASE`, `MBIC_IOP_ADDR_BASE`, and `GSM_ADDR_BASE` should be kept consistent if modified. Bitfield `sas_identify_frame_local` depends on kernel bitfield-order macros; unsupported architectures fail compilation intentionally. Queue/table offsets are byte offsets even where comments mention dwords, so callers must not accidentally multiply them.

## Test Signals

Useful validation includes compiling this driver on little- and big-endian configurations, checking `sizeof()` and field offsets for every firmware IOMB struct against the controller specification, exercising every outbound opcode handled by `process_one_iomb()`, injecting representative status/event values, verifying endian conversions with sparse or smatch, and building with encryption/DIF-related code paths enabled. Runtime tests should correlate MMIO table offsets and queue descriptors programmed by `pm80xx_hwi.c` with firmware-reported values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_hwi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_tracepoints.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_tracepoints.c

## Purpose

`pm80xx_tracepoints.c` is the tracepoint definition translation unit for the PM80xx trace events. It defines `CREATE_TRACE_POINTS` and includes `pm80xx_tracepoints.h`, causing the kernel tracepoint machinery to instantiate the trace events declared in the header exactly once.

## Important APIs, Types, and Functions

The file exports no normal functions or data structures. Its important API is build/link integration with the Linux tracing macros: `CREATE_TRACE_POINTS` must be defined before including the event header so `TRACE_EVENT()` declarations in `pm80xx_tracepoints.h` produce tracepoint objects rather than only declarations.

## Control Flow

There is no runtime control flow in this file. At build time, it participates in the trace-event generation pattern. At runtime, the instantiated tracepoints are called from other driver files, including PM8001 common command-build/completion paths and PM80xx SATA request issue paths.

## State and Persistence Behavior

The file does not manage persistent state. Runtime state is maintained by the kernel ftrace/perf/tracefs infrastructure when users enable or disable the generated events. Event records are transient trace-buffer entries.

## Dependencies and Integration Points

It depends on `pm80xx_tracepoints.h`, which in turn depends on `<linux/tracepoint.h>` and `pm8001_sas.h`. It must be linked into the same module/object set as the driver code that calls `trace_pm80xx_*()` helpers; otherwise callers would have declarations but no definitions.

## Risks and Edge Cases

The key risk is duplicate or missing tracepoint instantiation. Defining `CREATE_TRACE_POINTS` in more than one translation unit would create duplicate symbol problems, while omitting this file from the build would break tracepoint linkage. Because this file only includes the header, any event field/type mismatch risk lives in the header and call sites.

## Test Signals

Build and load the `pm8001` driver with tracing enabled, confirm trace events appear under the `pm80xx` trace system, and enable the events while issuing I/O to verify that request issue, request completion, and MPI build records are emitted without linker or runtime tracepoint warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_tracepoints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_tracepoints.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_tracepoints.h

## Purpose

`pm80xx_tracepoints.h` declares the PM80xx trace events used by the PM8001 driver. It defines the `pm80xx` trace system and provides tracepoints for request issue, request completion, and MPI command building so controller id, PHY, host tag, opcode, ATA opcode, queue indexes, and outstanding request counts can be observed through kernel tracing.

## Important APIs, Types, and Functions

The trace API generated by this header consists of `trace_pm80xx_request_issue()`, `trace_pm80xx_request_complete()`, and `trace_pm80xx_mpi_build_cmd()`, plus the usual enabled/static key helpers generated by `TRACE_EVENT()`. `pm80xx_request_issue` and `pm80xx_request_complete` take controller id, PHY id, host tag, controller opcode, ATA opcode, and running request count. `pm80xx_mpi_build_cmd` takes controller id, opcode, host tag, inbound queue index, producer index, and consumer index.

Each event uses `TP_STRUCT__entry()` to record fixed-width scalar fields, `TP_fast_assign()` to copy arguments into the trace entry, and `TP_printk()` to format a compact human-readable record. The include guard supports `TRACE_HEADER_MULTI_READ`, and the bottom of the file sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE pm80xx_tracepoints` before including `<trace/define_trace.h>`.

## Control Flow

There is no ordinary control flow, but the tracepoint macros generate conditional tracing code at call sites. When disabled, calls are low-overhead static-key checks. When enabled through tracefs/perf/ftrace, each call records the declared fields into the tracing ring buffer and formats them with the `TP_printk()` strings. The header is included normally by implementation files for declarations, and once by `pm80xx_tracepoints.c` with `CREATE_TRACE_POINTS` to instantiate definitions.

## State and Persistence Behavior

The header stores no driver state. Trace enablement and buffered event records are owned by the kernel tracing subsystem. The recorded fields are snapshots of volatile driver state such as `running_req`, queue PI/CI values, and controller/ATA opcodes at the time of the call.

## Dependencies and Integration Points

The header depends on `<linux/tracepoint.h>` and `pm8001_sas.h` for type context. Call sites include SATA request issue in `pm80xx_hwi.c`, MPI command-build tracing in common PM8001 hardware code, and request completion tracing in PM8001 task completion code. The `TRACE_INCLUDE_PATH .` setting assumes the trace header is found relative to the compilation context used by the driver build.

## Risks and Edge Cases

Tracepoint field types must match call-site argument types. The request events store ATA opcode as `u16`, while some call sites pass zero or command-byte values; wider or signed future inputs would be truncated. The `running_req` snapshot is informational and may race with concurrent increments/decrements. The header includes driver headers from a tracepoint header, so dependency expansion must remain safe for tracepoint generation. Moving the file or changing build include paths requires updating `TRACE_INCLUDE_PATH`.

## Test Signals

Build tests should ensure the trace header can be included by multiple C files and instantiated once. Runtime signals include presence of `pm80xx:pm80xx_request_issue`, `pm80xx:pm80xx_request_complete`, and `pm80xx:pm80xx_mpi_build_cmd` in tracefs, formatted fields matching expected controller/queue/tag values under I/O, and no duplicate tracepoint symbol errors when the module is rebuilt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm80xx_tracepoints.h -->
