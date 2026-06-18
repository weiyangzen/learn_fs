# Research Group subset-b-005338

This grouped report covers the QLogic qla2xxx NX/NX2 support files requested by work item `subset-b-005338`. Each section is source-path aligned and can be split directly into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx.h

## Purpose

`qla_nx.h` is the hardware contract header for the qla2xxx NX/82xx generation. It defines CRB address windows, on-chip address spaces, firmware/device state registers, IDC/coexistence fields, flash/ROM layout constants, interrupt register mappings, request/response sizing, small DMA scatter-gather helper types, and minidump template entry layouts. It does not implement runtime behavior; it supplies the symbolic register map and binary structure definitions used by `qla_nx.c`, `qla_nx2.c`, mailbox code, init code, and OS glue.

## Important APIs, Types, and Constants

- Phantom/firmware initialization states: `PHAN_INITIALIZE_FAILED`, `PHAN_INITIALIZE_COMPLETE`, `PHAN_INITIALIZE_ACK`, and `PHAN_PEG_RCV_INITIALIZED` are used when polling firmware PEG readiness.
- CRB address helpers: `QLA82XX_CRB_BASE`, `QLA82XX_REG()`, the many `QLA82XX_HW_*_CRB_AGT_ADR` and `QLA82XX_HW_PX_MAP_CRB_*` values, and `QLA82XX_PCI_CRB_WINDOW()` translate logical hardware agents into PCI CRB address windows.
- Driver coexistence/IDC registers: `QLA82XX_CRB_DRV_ACTIVE`, `QLA82XX_CRB_DEV_STATE`, `QLA82XX_CRB_DRV_STATE`, `QLA82XX_CRB_DRV_SCRATCH`, `QLA82XX_CRB_DEV_PART_INFO`, and `QLA82XX_CRB_DRV_IDC_VERSION` provide shared firmware/driver coordination state.
- Device state enum: `QLA8XXX_DEV_UNKNOWN`, `QLA8XXX_DEV_COLD`, `QLA8XXX_DEV_INITIALIZING`, `QLA8XXX_DEV_READY`, `QLA8XXX_DEV_NEED_RESET`, `QLA8XXX_DEV_NEED_QUIESCENT`, `QLA8XXX_DEV_FAILED`, and `QLA8XXX_DEV_QUIESCENT` are the shared state-machine values used by both 82xx and 8044 paths.
- IDC and firmware metadata: `QLA82XX_IDC_VERSION`, ROM init/reset timeouts, lock IDs, firmware version registers, and semaphore registers define how functions coordinate flash/CRB access.
- Interrupt contract: `struct qla82xx_legacy_intr_set`, `QLA82XX_LEGACY_INTR_CONFIG`, `ISR_*` register macros, and `PCIX_INT_VECTOR_BIT_F*` describe per-function legacy interrupt routing.
- Flash/ROM layout: bootloader, firmware, VPD, flash layout offsets, M25P SPI opcodes, unified ROM-image descriptors `struct qla82xx_uri_table_desc` and `struct qla82xx_uri_data_desc`, and image type constants identify firmware images in flash.
- Queue/IO helper types: `struct device_reg_82xx`, `struct fcp_cmnd`, `struct dsd_dma`, `struct ct6_dsd`, and queue size constants define hardware register overlay and CT6 DSD/FCP command metadata.
- Minidump template types: `struct qla82xx_md_template_hdr`, `qla82xx_md_entry_hdr_t`, and specialized entries for CRB, cache, OCM, memory, ROM, mux, and queue captures define the firmware dump binary format.
- Temperature macros and enum: `qla82xx_get_temp_val()`, `qla82xx_get_temp_state()`, `qla82xx_encode_temp()`, and `QLA82XX_TEMP_*` encode ASIC temperature state into a CRB word.

## Control Flow

There is no executable control flow in this header. Control flow is implicit in the contracts it defines:

- Firmware startup code polls `CRB_CMDPEG_STATE`/`CRB_RCVPEG_STATE` for `PHAN_INITIALIZE_COMPLETE`.
- IDC reset and quiesce handlers branch on the `QLA8XXX_DEV_*` values.
- Interrupt handlers use per-function ISR target/status/mask macros and `QLA82XX_LEGACY_INTR_CONFIG` to select the correct register set.
- Flash, ROM, and minidump routines use the packed descriptors to parse firmware-provided tables and execute capture entries.

## State and Persistence Behavior

This header names both volatile MMIO/CRB state and persistent flash layout. Volatile state includes driver-active masks, driver-state acknowledgements, device state, firmware heartbeat/alive counters, PEG halt status, CRB window locks, and temperature state. Persistent state includes flash layout regions, unified ROM image descriptors, bootloader/firmware/VPD offsets, and board info magic values. The packed minidump structs also describe persistent-in-memory dump records produced after firmware failure.

## Dependencies

- Includes `<scsi/scsi.h>` for `struct scsi_lun`.
- Assumes kernel integer, endian, DMA, list, and bit macros/types supplied by surrounding qla2xxx headers before or after inclusion, including `__le16`, `__le32`, `dma_addr_t`, `struct list_head`, `BIT_*`, and `__packed`.
- Shares definitions with `qla_nx2.h`; the 8044 implementation reuses 82xx state values, minidump opcodes, MIU test-agent constants, temperature helpers, and legacy interrupt register offsets.

## Integration Points

- Included from `qla_def.h`, making these definitions visible to the qla2xxx driver.
- Used by `qla_nx.c` for 82xx initialization, firmware control, minidump handling, IDC, and legacy interrupt setup.
- Used indirectly by `qla_nx2.c` for shared device states, firmware PEG state values, MIU test-agent registers, minidump opcodes, temperature helpers, and legacy interrupt offsets.
- Referenced by mailbox/init/OS glue through exported qla82xx/qla8044 operations in `qla_gbl.h` and `qla_os.c`.

## Risks and Edge Cases

- The file encodes large hardware address maps as preprocessor macros; a wrong constant silently redirects MMIO to the wrong hardware block.
- Several CRB window aliases and repeated definitions, such as the duplicate `QLA82XX_CRB_PEG_MD_3`, depend on preprocessor replacement behavior and should be treated carefully during cleanup.
- Packed minidump and ROM descriptor structures are ABI contracts with firmware; field reordering, type-width changes, or padding changes would break parsing.
- Shared `QLA8XXX_DEV_*` enum values are cross-generation protocol values. Adding or changing values requires all IDC state-machine users to be audited.
- Endianness-sensitive fields use `__le16`/`__le32` only in some structs; code that casts raw firmware/flash buffers must continue to use the expected conversion rules.

## Test Signals

- Build coverage for the qla2xxx module with NX/82xx and 8044 support enabled catches missing symbols and struct-layout syntax issues.
- Hardware or emulator probe should verify firmware state polling reaches `PHAN_INITIALIZE_COMPLETE` and IDC state transitions reach `QLA8XXX_DEV_READY`.
- Interrupt tests should validate the legacy per-function status/mask/vector mapping.
- Flash/minidump tests should parse firmware templates and ROM image descriptors without checksum or size failures.
- Temperature and watchdog tests should confirm `qla82xx_get_temp_*` interpretation matches CRB temperature encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx2.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx2.c

## Purpose

`qla_nx2.c` implements the ISP8044/NX2-specific runtime path for the qla2xxx Fibre Channel/FCoE driver. It provides low-level MMIO and indirect CRB access, IDC and flash locking, flash optrom read/write, reset-template loading and interpretation, bootloader restart, multi-function device-state coordination, watchdog/temperature/firmware-alive checks, minidump capture, legacy interrupt handling, and the 8044 abort/fw-dump entry points wired into `struct isp_operations`.

## Important APIs and Functions

- Register access: `qla8044_rd_reg()`, `qla8044_wr_reg()`, `qla8044_rd_direct()`, and `qla8044_wr_direct()` are the public direct register helpers. Static `qla8044_set_win_base()`, `qla8044_rd_reg_indirect()`, and `qla8044_wr_reg_indirect()` implement CRB-windowed indirect access.
- IDC locking: `qla8044_idc_lock()` and `qla8044_idc_unlock()` acquire/release the driver coexistence semaphore. `qla8044_lock_recovery()` force-recovers a stuck IDC lock using `QLA8044_DRV_LOCKRECOVERY`.
- Flash access: `qla8044_read_optrom_data()` and `qla8044_write_optrom_data()` are exported optrom operations. Internals include `qla8044_flash_lock()`, `qla8044_flash_unlock()`, `qla8044_read_flash_data()`, `qla8044_lockless_flash_read_u32()`, `qla8044_unprotect_flash()`, `qla8044_protect_flash()`, `qla8044_erase_flash_sector()`, `qla8044_write_flash_buffer_mode()`, and `qla8044_write_flash_dword_mode()`.
- Reset-template interpreter: `qla8044_read_reset_template()` loads the restart template from flash; `qla8044_process_reset_template()` dispatches opcodes to `qla8044_write_list()`, `qla8044_read_write_list()`, `qla8044_poll_list()`, `qla8044_poll_write_list()`, `qla8044_read_modify_write()`, `qla8044_pause()`, `qla8044_poll_read_list()`, and `qla8044_template_end()`.
- Firmware bootstrap: `qla8044_restart()`, `qla8044_start_firmware()`, `qla8044_copy_bootloader()`, `qla8044_ms_mem_write_128b()`, and `qla8044_check_cmd_peg_status()` stop firmware, optionally capture minidump, run init/start sequences, copy bootloader from flash to MS memory, and wait for PEG initialization.
- Device-state machine: `qla8044_device_state_handler()` coordinates `QLA8XXX_DEV_*` states. It delegates to `qla8044_device_bootstrap()`, `qla8044_need_reset_handler()`, and `qla8044_need_qsnt_handler()`.
- Driver presence and acknowledgements: `qla8044_set_idc_dontreset()`, `qla8044_clear_drv_active()`, `qla8044_clear_qsnt_ready()`, and static helpers set/clear active, reset-ready, and quiescent-ready bits.
- Watchdog and health: `qla8044_check_fw_alive()`, `qla8044_watchdog()`, and `qla8044_read_temperature()` monitor heartbeat, halt status, temperature, quiesce, and reset requests.
- Minidump capture: `qla8044_collect_md_data()` walks the minidump template and dispatches entry processors for control, CRB, memory, ROM, cache, OCM, mux, queue, poll/read/write, MDIO, DFE, RDMUX2, and PEX-DMA reads. `qla8044_get_minidump()` records success/failure flags.
- Interrupt handling: `qla8044_intr_handler()` validates legacy interrupt ownership, deasserts the legacy interrupt trigger, then handles mailbox completions, async events, and response queues.
- Recovery entry points: `qla8044_abort_isp()` drives reset recovery and `qla8044_fw_dump()` triggers dump/reset-owner flow when CNA firmware dumps are allowed.

## Control Flow

The direct/indirect register path is foundational: public helpers either read from `ha->nx_pcibase + addr` or index `qla8044_reg_tbl[]`; indirect helpers program `QLA8044_CRB_WIN_FUNC(portnum)` then access `QLA8044_WILDCARD`.

The normal device-state flow starts with `qla8044_device_state_handler()`. It updates IDC registration, locks IDC, reads `QLA8044_CRB_DEV_STATE_INDEX`, and loops until READY or failure. COLD calls `qla8044_device_bootstrap()`. INITIALIZING, QUIESCENT, and NEED_QUIESCENT wait or run quiesce handling. NEED_RESET runs reset handling. FAILED and unknown states invoke the generic failed handler.

Bootstrap first checks whether firmware is alive by observing `QLA8044_PEG_ALIVE_COUNTER_INDEX`. If alive, it sets READY. Otherwise it recovers flash lock if needed, sets INITIALIZING, unlocks IDC while firmware restart runs, then relocks IDC and either marks FAILED or READY. Firmware restart executes stop sequence, captures minidump if enabled, executes init sequence, copies bootloader, marks flash boot, executes start sequence, and waits for command PEG completion.

Reset recovery uses shared-function coordination. `qla8044_abort_isp()` marks NEED_RESET when appropriate, asks qla83xx ownership logic to select a reset owner, runs the device-state handler, clears reset-ready state, and restarts the ISP on success. `qla8044_need_reset_handler()` aborts active IO, sets this function's reset-ready bit, waits for active functions to acknowledge, removes non-acknowledging functions from `drv_active`, and lets the reset owner or function 7 perform bootstrap.

Quiesce handling blocks IO with `qla2x00_quiesce_io()`, sets quiescent-ready state, waits for active functions to acknowledge, and transitions NEED_QUIESCENT to QUIESCENT. Timeout clears the DPC quiesce flag, restores READY, and clears this function's ready bit.

Minidump flow starts in `qla8044_collect_md_data()`: it rejects missing buffers or duplicate dumps, checks graceful-reset state, validates the template checksum, stamps the driver timestamp, initializes saved OCM window state, then iterates firmware template entries. Each entry is skipped if its capture mask is disabled; otherwise a type-specific processor appends data to `ha->md_dump`. The function validates that collected data equals `ha->md_dump_size`, marks `ha->fw_dumped`, and posts a firmware-dump uevent.

Interrupt flow validates `LEG_INTR_PTR_OFFSET` bit 31 and function bits, deasserts the interrupt by writing `LEG_INTR_TRIG_OFFSET`, then under `hardware_lock` reads `host_status` and dispatches mailbox completion, async event, or response queue processing before clearing `host_int`.

## State and Persistence Behavior

Persistent or semi-persistent hardware state lives in flash: reset templates, bootloader image, firmware image, optrom contents, flash status/protection bits, and minidump templates. Runtime shared state is held in CRB registers such as driver active, driver ack/state, device state, IDC version, lock IDs, IDC control, firmware alive counter, halt status, ASIC temperature, and firmware image valid. Driver-local state is maintained in `struct qla_hw_data` and `struct scsi_qla_host`, including `reset_tmplt`, `fw_dumped`, `prev_minidump_failed`, heartbeat counters, reset-owner flags, EEH/frozen flags, and DPC bits.

The file explicitly blocks SCSI requests around optrom read/write and firmware-dump flows. Flash writes erase sectors, unprotect/protect flash around the operation, and prefer buffered burst writes with dword-write fallback. Reset template memory is allocated with `vmalloc()` and freed on read errors; minidump DMA buffers are allocated with `dma_alloc_coherent()` for PEX-DMA reads and released before return.

## Dependencies

- Linux kernel APIs: `readl()`, `writel()`, `msleep()`, `mdelay()`, `udelay()`, `usleep_range()`, `jiffies`, `time_after_eq()`, `vmalloc()`, `vfree()`, `kcalloc()`, `kfree()`, DMA coherent allocation, spin/write locks, PCI helpers, SCSI request blocking, and IRQ return types.
- qla2xxx core headers: `qla_def.h` and `qla_gbl.h` provide host/adapter structures, exported qla2xxx functions, flags, logging, mailbox/response helpers, module parameters, and constants.
- Shared NX definitions: `qla_nx.h` and `qla_nx2.h` provide state values, register offsets, reset/minidump structures, flash constants, and temperature helpers.
- External qla2xxx functions used include `qla2x00_abort_isp_cleanup()`, `qla2x00_quiesce_io()`, `qla8xxx_dev_failed_handler()`, `qla83xx_reset_ownership()`, `qla82xx_restart_isp()`, `qla82xx_clear_pending_mbx()`, `qla82xx_validate_template_chksum()`, `qla82xx_mbx_completion()`, `qla2x00_async_event()`, `qla24xx_process_response_queue()`, and `qla2x00_post_uevent_work()`.

## Integration Points

- `qla_os.c` selects `qla8044_isp_ops`, wiring this file's interrupt handler, firmware dump, optrom read/write, and abort ISP operations into the adapter operation table.
- `qla_init.c` calls `qla8044_read_reset_template()` during initialization and may set IDC dont-reset behavior.
- `qla_nx.c` coordinates with 8044 paths for reset/state handling and legacy interrupt mask registers.
- `qla_mbx.c` consumes `qla8044_read_temperature()` and provides the 8044 minidump-template fetch path.
- `qla_attr.c`, `qla_os.c`, and BSG/mailbox paths use IDC locks and 8044 registers for application-triggered reset, dump, and SERDES operations.

## Risks and Edge Cases

- IDC lock recovery force-unlocks hardware if the lock owner appears stale. Incorrect owner detection or timing can disrupt another active function.
- Several flows intentionally unlock IDC while performing long operations and relock later; race coverage depends on shared device-state protocol correctness.
- Reset-template parsing trusts firmware-provided sizes and offsets after signature/checksum validation. Corrupt but checksum-valid templates could drive invalid indirect register writes or pointer advancement.
- Flash write operations assume sector-aligned offset/length as noted by comments; callers passing unaligned lengths could skip tail data because write loops are based on whole sectors and 64-dword bursts.
- MMIO indirect access depends on correct CRB window programming per port. Failures are logged, but many callers aggregate or ignore return values in loops.
- Minidump collection bounds checks `data_collected > ha->md_dump_size`, not every per-entry predicted size before writing, so malformed templates could overrun the dump buffer before the next iteration detects excess.
- `qla8044_minidump_process_rdmem()` returns `QLA_SUCCESS` on MIU busy timeout after unlocking, which may leave partial dump data while signaling success.
- Watchdog and interrupt code run in timing-sensitive contexts and depend on DPC flags to defer heavy reset work.
- Some poll loops use hardware-provided or template-provided wait counts; zero or very small delays can create tight loops, while large values can delay recovery.

## Test Signals

- Build the qla2xxx driver with ISP8044/NX2 support and warnings enabled; the file is tightly coupled to packed structs and exported prototypes.
- Initialization tests should read and validate the reset template, then drive COLD to READY with command PEG reaching `PHAN_INITIALIZE_COMPLETE`.
- Multi-function reset tests should cover all active functions acknowledging, one function failing to acknowledge, reset-owner selection, function 7 fallback, dont-reset handling, and EEH/frozen paths.
- Flash tests should cover optrom read, sector erase, buffered writes, fallback dword writes, status-register protection/unprotection, lock timeout, and lock recovery.
- Watchdog tests should simulate heartbeat progress, heartbeat stall, unrecoverable halt status, NEED_RESET, NEED_QUIESCENT, temperature warning, and temperature panic.
- Minidump tests should cover each supported template entry type, capture-mask skipping, PEX-DMA success/fallback, checksum failure, duplicate dump rejection, graceful-reset suppression, and dump-size mismatch.
- Interrupt tests should inject spurious legacy interrupts, wrong function bits, mailbox completions, async events, and response queue interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx2.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx2.h

## Purpose

`qla_nx2.h` is the ISP8044/NX2 hardware-definition companion to `qla_nx2.c`. It defines 8044 register offsets, address ranges, flash command constants, reset-template opcodes and layouts, minidump entry layouts, IDC metadata, CRB register indices, and PEX-DMA descriptors. The header is a binary and MMIO contract rather than an implementation file.

## Important APIs, Types, and Constants

- IDC/reset coordination: `QSNT_ACK_TOV`, `INTENT_TO_RECOVER`, `PROCEED_TO_RECOVER`, `IDC_LOCK_RECOVERY_*`, `DONTRESET_BIT0`, `GRACEFUL_RESET_BIT1`, and IDC version constants describe multi-function recovery protocol fields.
- Address helpers: 8044 DDR/QDR/OCM/PCI address ranges and `addr_in_range()` support validated MS memory access in the implementation.
- Register map: `QLA8044_FLASH_*`, `QLA8044_DRV_LOCK*`, `QLA8044_CRB_*`, `QLA8044_PEG_*`, `QLA8044_FW_*`, `QLA8044_LINK_*`, semaphore, mailbox, reset, and interrupt-related offsets define the 8044 CRB/MMIO surface.
- Flash constants: lock timeouts, sector size, status ready value, erase/write command signatures, burst sizing, SPI control bits, and status-register write patterns drive optrom erase/write paths.
- Reset-template ABI: `struct qla8044_reset_template_hdr`, `struct qla8044_reset_entry_hdr`, `struct qla8044_poll`, `struct qla8044_rmw`, `struct qla8044_entry`, `struct qla8044_quad_entry`, and `struct qla8044_reset_template` define the flash-resident restart template and the driver's interpreter state.
- Reset opcodes: `OPCODE_WRITE_LIST`, `OPCODE_READ_WRITE_LIST`, `OPCODE_POLL_LIST`, `OPCODE_POLL_WRITE_LIST`, `OPCODE_READ_MODIFY_WRITE`, `OPCODE_SEQ_PAUSE`, `OPCODE_SEQ_END`, `OPCODE_TMPL_END`, and `OPCODE_POLL_READ_LIST` are consumed by `qla8044_process_reset_template()`.
- Minidump ABI: `struct qla8044_minidump_template_hdr` plus entry structures for CRB, cache, OCM, memory, PEX-DMA memory, ROM, mux, queue, pollrd, rddfe, rdmdio, pollwr, rdmux2, and pollrdmwr match firmware-provided dump templates.
- IDC information: `struct qla8044_idc_information` packages request descriptor and auxiliary IDC fields.
- CRB direct-register indices: `enum qla_regs` and `CRB_REG_INDEX_MAX` define the valid indices for `qla8044_rd_direct()`/`qla8044_wr_direct()`.
- PEX-DMA: `struct qla8044_pex_dma_descriptor` defines the descriptor written into MS memory to accelerate minidump memory reads.

## Control Flow

There is no standalone control flow except the inline `addr_in_range()` predicate. The reset-template and minidump structures define data-driven control flow for `qla_nx2.c`: firmware supplies a sequence of opcodes or dump entries, and the C file dispatches on these numeric command/type values. CRB index enum values also constrain direct register reads and writes through `qla8044_reg_tbl[]`.

## State and Persistence Behavior

The header defines the shape of persistent flash content, including reset templates, bootloader/firmware image locations, optrom sector operations, and minidump templates. It also names runtime CRB state that persists across cooperating PCI functions while the adapter is powered: driver active/presence, driver acknowledgement, device state, IDC version, IDC control, lock ownership, firmware heartbeat, halt status, ASIC temperature, NPAR state, and link state/speed registers. `struct qla8044_reset_template` is driver-local runtime state containing parsed template offsets, interpreter indices, scratch array values, and end/error flags.

## Dependencies

- Assumes inclusion through `qla_def.h` or related qla2xxx headers that already provide kernel integer types, `bool`, `u64`, `uint*_t`, `__packed`, bit macros, and shared 82xx definitions such as `MIU_TA_CTL_*`.
- Shares minidump entry type constants and debug opcodes with `qla_nx.h`; `qla_nx2.c` mixes 8044-specific structures with 82xx minidump opcodes.
- The packed structures are consumed by firmware/flash parsing code and cannot be treated as ordinary in-memory-only C structs.

## Integration Points

- Included from `qla_def.h`, making 8044 definitions visible driver-wide.
- `qla_nx2.c` is the primary consumer for every register constant, reset opcode, and packed structure in this header.
- `qla_init.c`, `qla_mbx.c`, `qla_attr.c`, `qla_os.c`, and BSG/mailbox paths reference selected constants and exported 8044 operations through `qla_gbl.h`.
- `struct qla8044_reset_template` is embedded in `struct scsi_qla_host`, so reset template state is per virtual host.

## Risks and Edge Cases

- Packed reset/minidump structures are firmware ABI. Alignment, padding, and field-width changes would corrupt parsing.
- Many constants encode hardware magic values with limited self-description. Changing them requires hardware documentation or empirical validation.
- `addr_in_range()` uses inclusive low/high bounds; callers must pass the correct maximum address and ensure transfer size does not extend beyond the range after the starting address is accepted.
- `CRB_REG_INDEX_MAX` must stay synchronized with `enum qla_regs` and `qla8044_reg_tbl[]`; mismatch can reject valid registers or allow out-of-bounds table access.
- Reset-template sizes and offsets are fixed around `QLA8044_RESTART_TEMPLATE_SIZE`; larger future templates would require implementation changes.
- Flash burst constants constrain optrom writes to 2 through 64 dwords; callers and flash descriptors must agree with those constraints.

## Test Signals

- Compile-time coverage should catch missing constants or struct type changes in `qla_nx2.c`.
- Firmware-template tests should validate that reset-template headers with `RESET_TMPLT_HDR_SIGNATURE` and `QLA8044_RESET_SEQ_VERSION` parse into correct init/start/stop offsets.
- Minidump tests should validate that each packed entry layout matches firmware-provided template sizes and entry-type dispatch.
- Flash tests should exercise sector erase, status writes, and buffer/dword write modes using the constants here.
- IDC tests should verify lock recovery state bits, owner encoding, and dont-reset/graceful-reset controls across multiple functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx2.h -->
