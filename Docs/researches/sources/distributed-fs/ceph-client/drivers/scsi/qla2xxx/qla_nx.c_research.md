# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx.c

## Purpose
`qla_nx.c` implements QLogic ISP82xx/8xxx "NX" adapter support for the `qla2xxx` driver. It covers CRB and memory-window address translation, PCI/IO-space setup, flash/ROM access, firmware loading from flash or firmware blobs, IDC multi-function coordination, interrupt handling, reset and quiesce state machines, watchdog health checks, option ROM read/write, doorbell IOCB start, FCoE context reset, chip-reset cleanup, minidump template execution, LED beacon control, and explicit firmware dump triggering.

This file is the shared low-level control and recovery layer for 82xx-class adapters, with some dispatch to 8044/83xx helpers when the hardware type differs.

## Important APIs, Types, And Functions
Address translation and register access are built around `qla82xx_crb_addr_transform_setup()`, `qla82xx_pci_get_crb_addr_2M()`, `qla82xx_pci_set_crbwindow_2M()`, `qla82xx_crb_win_lock()`, `qla82xx_wr_32()`, `qla82xx_rd_32()`, `qla82xx_pci_set_window()`, `qla82xx_pci_mem_read_2M()`, `qla82xx_pci_mem_write_2M()`, direct memory read/write fallbacks, and the static CRB mapping tables.

Inter-driver coordination uses `qla82xx_idc_lock()`, `qla82xx_idc_unlock()`, `qla82xx_set_drv_active()`, `qla82xx_clear_drv_active()`, `qla82xx_set_idc_version()`, reset/quiesce ready helpers, and device-state strings from `qdev_state()`.

Firmware and flash paths include `qla82xx_rom_lock()`, `qla82xx_rom_unlock()`, `qla82xx_rom_fast_read()`, `qla82xx_flash_set_write_enable()`, `qla82xx_flash_wait_write_finish()`, `qla82xx_write_flash_dword()`, `qla82xx_pinit_from_rom()`, `qla82xx_fw_load_from_flash()`, `qla82xx_fw_load_from_blob()`, URI descriptor helpers, `qla82xx_validate_firmware_blob()`, `qla82xx_load_fw()`, and `qla82xx_start_firmware()`.

Lifecycle and PCI setup are provided by `qla82xx_iospace_config()`, `qla82xx_pci_config()`, `qla82xx_reset_chip()`, `qla82xx_config_rings()`, `qla82xx_init_flags()`, `qla82xx_load_risc()`, `qla82xx_abort_isp()`, `qla82xx_fcoe_ctx_reset()`, `qla82xx_chip_reset_cleanup()`, and `qla2x00_wait_for_fcoe_ctx_reset()`.

Interrupt handling includes `qla82xx_mbx_completion()`, `qla82xx_intr_handler()`, `qla82xx_msix_default()`, `qla82xx_msix_rsp_q()`, `qla82xx_poll()`, `qla82xx_enable_intrs()`, and `qla82xx_disable_intrs()`.

Recovery and watchdog functions include `qla82xx_device_state_handler()`, `qla82xx_device_bootstrap()`, `qla82xx_need_reset_handler()`, `qla82xx_need_qsnt_handler()`, `qla8xxx_dev_failed_handler()`, `qla82xx_check_md_needed()`, `qla82xx_check_fw_alive()`, `qla82xx_check_temp()`, `qla82xx_read_temperature()`, `qla82xx_clear_pending_mbx()`, `qla82xx_watchdog()`, and `qla82xx_set_reset_owner()`.

Option ROM and minidump support is implemented by `qla82xx_read_optrom_data()`, `qla82xx_write_optrom_data()`, `qla82xx_read_flash_data()`, flash protect/unprotect/erase helpers, `qla82xx_validate_template_chksum()`, `qla82xx_md_collect()`, minidump entry processors, `qla82xx_md_alloc()`, `qla82xx_md_free()`, `qla82xx_md_prep()`, `qla82xx_beacon_on()`, `qla82xx_beacon_off()`, and `qla82xx_fw_dump()`.

## Control Flow
Initialization starts with `qla82xx_init_flags()`, which initializes the NX hardware lock, memory windows, port number, and legacy interrupt register set. `qla82xx_iospace_config()` requests PCI regions, maps BAR0 as `nx_pcibase`, assigns `iobase` based on chip type, maps or selects the doorbell write/read pointers, and limits the adapter to one request and response queue.

Firmware startup is coordinated by `qla82xx_load_risc()`, which routes 82xx hardware into `qla82xx_device_state_handler()` and 8044 hardware into 8044-specific handlers. The 82xx handler takes the IDC lock, marks this function active on first initialization, records IDC version, reads `QLA82XX_CRB_DEV_STATE`, and loops until the device becomes ready or fails. State `DEV_COLD` triggers `qla82xx_device_bootstrap()`, `DEV_INITIALIZING` sleeps and retries, `DEV_NEED_RESET` invokes reset coordination, `DEV_NEED_QUIESCENT` invokes quiesce coordination, `DEV_FAILED` disables the board, and `DEV_READY` releases the lock successfully.

`qla82xx_device_bootstrap()` decides whether firmware reset/start is needed by checking reset ownership and the PEG alive counter. If firmware must be started, it writes `DEV_INITIALIZING`, drops IDC lock while `qla82xx_start_firmware()` runs, then reacquires the lock and writes `DEV_READY` on success or `DEV_FAILED` on failure. `qla82xx_start_firmware()` scrubs DMA shift and PEG state registers, calls `qla82xx_load_fw()`, then waits for command and receive PEG state handshakes.

Firmware loading first runs `qla82xx_pinit_from_rom()`, which halts hardware engines and PEGs, applies a software reset, reads CRB initialization address/value pairs from flash, translates CRB addresses, skips protected or inappropriate registers, writes initialization values with required delays, and clears PEG state. `qla82xx_load_fw()` then prefers firmware from flash unless module policy forces blob loading. Blob loading validates either legacy flash-ROM-image magic or unified ROM image product tables, copies bootloader and firmware image data into adapter memory through 2M memory writes, writes a magic ready marker, and releases firmware from reset.

Register access is layered. `qla82xx_rd_32()` and `qla82xx_wr_32()` translate CRB addresses into direct 2M mappings when possible or take the CRB window lock and program `CRB_WINDOW_2M` for indirect access. Memory reads/writes choose MIU test-agent access for DDR/QDR ranges when possible and fall back to direct PCI memory window mapping for OCM or unusual sizes/ranges.

Interrupt handling either checks legacy interrupt vector/state registers or runs directly for MSI-X. It clears target interrupt status, reads host interrupt/status registers, dispatches mailbox completion, asynchronous event, or response queue work, clears `host_int`, invokes mailbox completion handling, and unmasks legacy interrupts when needed. The MSI-X response queue handler directly processes `qla24xx_process_response_queue()`.

Reset flow starts with `qla82xx_abort_isp()`. It marks NIC-core reset handler active, takes IDC lock, sets reset owner/device state, runs the device-state handler, clears reset-ready, and restarts the ISP on success. On failure, it uses retry counters and `ISP_ABORT_RETRY` to either schedule another attempt or disable the board through `reset_adapter()`.

The watchdog samples device state, temperature, and firmware heartbeat. Temperature panic sets unrecoverable state and clears pending mailbox commands. `DEV_NEED_RESET`, `DEV_NEED_QUIESCENT`, and `DEV_FAILED` set DPC flags. Stalled heartbeat triggers register dumps, optional unrecoverable classification from halt status, firmware-hung state, and premature mailbox completion.

Minidump collection validates the firmware-provided template checksum, checks capture mask levels, stores driver info, walks each template entry, skips entries outside the driver capture mask, executes control/read/cache/queue/ROM/memory entry processors, verifies the collected byte count, marks `ha->fw_dumped`, and posts a firmware-dump uevent.

## State And Persistence
There is no driver-owned filesystem persistence. Persistent runtime state lives in `struct qla_hw_data`, hardware CRB/flash registers, firmware state registers, and allocated firmware/minidump buffers.

Address-window state includes `ha->crb_win`, `ha->qdr_sn_window`, `ha->ddr_mn_window`, `ha->curr_window`, `ha->mn_win_crb`, `ha->ms_win_crb`, `ha->nx_pcibase`, `ha->iobase`, and doorbell pointers. The CRB transform table is static global state initialized once.

IDC and recovery state is stored in hardware registers such as `QLA82XX_CRB_DRV_ACTIVE`, `QLA82XX_CRB_DRV_STATE`, `QLA82XX_CRB_DEV_STATE`, and driver flags such as `nic_core_reset_owner`, `nic_core_reset_hdlr_active`, `quiesce_owner`, `isp82xx_fw_hung`, `isp82xx_no_md_cap`, `DFLG_DEV_FAILED`, and DPC flags.

Firmware blob state is held in `ha->hablob`, `ha->fw_type`, `ha->file_prd_off`, flash region offsets, and firmware version fields. Minidump state uses `ha->md_tmplt_hdr`, `ha->md_tmplt_hdr_dma`, `ha->md_template_size`, `ha->md_dump`, `ha->md_dump_size`, `ha->fw_dumped`, and `ha->prev_minidump_failed`.

Flash writes modify adapter option ROM persistently. `qla82xx_write_optrom_data()` unprotects flash, erases sectors, writes dwords, and reprotects flash, so that path has real device persistence even though the driver does not write host files.

## Dependencies And Integration Points
The file depends on `qla_def.h` for qla2xxx host/HBA definitions, hardware constants, logging, mailbox/DPC flags, firmware request helpers, minidump types, and 8044/83xx helper prototypes. It depends on PCI APIs, MMIO accessors including 64-bit non-atomic helpers, delays, ratelimit logging, vmalloc/vfree, SCSI request blocking, and firmware blob APIs through qla2xxx request wrappers.

It integrates with qla2xxx common firmware paths (`qla2x00_request_firmware()`, `qla2x00_get_fw_version()`, `qla2x00_abort_isp_cleanup()`, `qla82xx_restart_isp()`, `qla2x00_try_to_stop_firmware()`, `qla2x00_wait_for_chip_reset()`, `qla24xx_process_response_queue()`, `qla2x00_async_event()`, mailbox completion handling, and minidump template fetch functions).

It coordinates with other PCI functions and possibly other drivers through IDC hardware semaphores and shared CRB state registers. Correct operation requires all functions to honor `DRV_ACTIVE`, `DRV_STATE`, `DEV_STATE`, reset-ready, and quiesce-ready protocols.

## Risks And Edge Cases
CRB and memory window programming is lock-sensitive. Indirect CRB accesses take both `ha->hw_lock` and hardware semaphore 7; memory-window accesses manipulate shared window registers. Missing locks or using the wrong accessor can send reads/writes to the wrong hardware region.

Several low-level functions use `BUG_ON()` for invalid CRB translations. Bad offsets from new callers can panic the kernel rather than returning an error.

Firmware loading crosses persistent flash, firmware blob parsing, memory-window writes, and hardware reset sequencing. Partial blob validation, endian mistakes, or skipped CRB writes can leave the device in `DEV_FAILED` or a state that requires host reset.

IDC state-machine logic relies on all active PCI functions acknowledging reset or quiesce bits. Timeouts intentionally force state transitions in some paths, but that can race with another function still completing I/O.

Flash update paths persist changes to adapter ROM. Sector erase/write failures, wrong `fdt_block_size`, or interrupted updates can corrupt option ROM contents. Although flash is reprotected afterward, failures during unprotected windows matter.

Watchdog and reset paths can prematurely complete mailbox commands when firmware is hung. That avoids indefinite waits, but callers must be prepared for mailbox completion without real firmware response.

Minidump execution interprets firmware-provided templates as command streams that read/write registers and poll hardware. Bad templates, wrong capture masks, insufficient dump sizing, or access timeouts can fail collection or skip entries. The code validates checksums and total size but still performs hardware operations from template contents.

## Test Signals
Build coverage should include 82xx and 8044 configurations, MSI-X and legacy interrupt paths, firmware blob support, and minidump support.

Initialization tests should cover PCI region request/map failures, doorbell mapping modes, CRB direct and indirect access, memory reads/writes across supported sizes and boundary conditions, IDC lock timeout, active-driver register initialization from `0xffffffff`, and device states `READY`, `COLD`, `INITIALIZING`, `NEED_RESET`, `NEED_QUIESCENT`, `QUIESCENT`, and `FAILED`.

Firmware tests should exercise flash load success/failure, forced blob load, legacy blob validation, unified ROM image product-table selection, bootloader/firmware copy failure, command and receive PEG handshake timeout, and firmware version change triggering minidump resource reallocation.

Interrupt tests should cover legacy interrupt filter/unmask, MSI-X default and response handlers, mailbox completion, async events, response queue dispatch, host interrupt clearing, and PCI disconnect reads.

Recovery tests should inject watchdog heartbeat stalls, temperature warning/panic, halt status unrecoverable bits, device need-reset/need-quiescent states, reset acknowledgment timeout, quiesce timeout, abort retry exhaustion, FCoE context reset, and chip-reset cleanup with and without firmware hung.

Flash/minidump tests should cover optrom read/write sector boundaries, flash unprotect/protect failures, erase failure, dword write failure, minidump checksum failure, capture mask filtering, control opcode polling timeout, RDCRB/RDMEM/RDROM/cache/queue entries, dump-size mismatch, duplicate dump prevention, and forced dump without minidump capture.
