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
