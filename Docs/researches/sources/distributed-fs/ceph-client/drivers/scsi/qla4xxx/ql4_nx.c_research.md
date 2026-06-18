# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nx.c

## Purpose

`ql4_nx.c` contains the shared 8xxx-era QLogic iSCSI adapter support used primarily by ISP8022, with additional helpers used by ISP8032/8042 minidump and device-state paths. It is the low-level bridge between the qla4xxx SCSI/iSCSI driver and the adapter's CRB registers, PCI memory windows, ROM/flash layout, firmware bootstrap sequence, inter-driver-coordination state machine, mailbox transport, minidump capture engine, and interrupt enable/disable flow.

The file is hardware-facing rather than protocol-facing. It does not implement iSCSI command handling; it provides the register accessors and recovery machinery that the higher-level qla4xxx probe, mailbox, IOCB, ISR, watchdog, and reset paths depend on.

## Important APIs, Types, And Functions

Core register and memory access helpers are `qla4_82xx_wr_32()`, `qla4_82xx_rd_32()`, `qla4_82xx_pci_get_crb_addr_2M()`, `qla4_82xx_md_rd_32()`, `qla4_82xx_md_wr_32()`, `qla4_82xx_pci_mem_read_2M()`, `qla4_82xx_pci_mem_write_2M()`, and `qla4_8xxx_ms_mem_write_128b()`. These functions translate the adapter's 128 MB CRB address space into the 2 MB PCI BAR map, select CRB windows when a register is not directly mapped, and access DDR/QDR/OCM memory through MIU test-agent registers or direct PCI mappings.

Synchronization helpers include `qla4_82xx_crb_win_lock()`, `qla4_82xx_crb_win_unlock()`, `qla4_82xx_idc_lock()`, `qla4_82xx_idc_unlock()`, `qla4_82xx_rom_lock()`, and `qla4_82xx_rom_unlock()`. The CRB-window lock uses PCI semaphore 7 under `ha->hw_lock`, the IDC lock uses semaphore 5 and may sleep, and the ROM lock uses semaphore 2 with `QLA82XX_ROM_LOCK_ID`.

Firmware and boot functions include `qla4_82xx_pinit_from_rom()`, `qla4_82xx_load_from_flash()`, `qla4_82xx_load_fw()`, `qla4_82xx_start_firmware()`, `qla4_82xx_try_start_fw()`, `qla4_82xx_cmdpeg_ready()`, and `qla4_82xx_rcvpeg_ready()`. They halt hardware blocks, replay CRB initialization entries from flash, copy bootloader/firmware content into adapter memory, release reset, and wait for command and receive PEG handshakes.

Device coordination and reset APIs are `qla4_8xxx_set_drv_active()`, `qla4_8xxx_clear_drv_active()`, `qla4_8xxx_need_reset()`, `qla4_8xxx_set_rst_ready()`, `qla4_8xxx_clear_rst_ready()`, `qla4_8xxx_device_bootstrap()`, `qla4_82xx_need_reset_handler()`, `qla4_8xxx_need_qsnt_handler()`, `qla4_8xxx_update_idc_reg()`, `qla4_8xxx_device_state_handler()`, `qla4_8xxx_load_risc()`, and `qla4_82xx_isp_reset()`. These functions manipulate `QLA8XXX_CRB_DRV_ACTIVE`, `QLA8XXX_CRB_DRV_STATE`, `QLA8XXX_CRB_DRV_IDC_VERSION`, and `QLA8XXX_CRB_DEV_STATE`.

Minidump support is centered on `qla4_8xxx_get_minidump()` and `qla4_8xxx_collect_md_data()`. The dispatcher handles template entry types such as `QLA8XXX_RDCRB`, `QLA8XXX_RDMEM`, `QLA8XXX_RDROM`, `QLA8XXX_CNTRL`, `QLA8XXX_RDOCM`, `QLA8XXX_RDMUX`, `QLA8XXX_QUEUE`, L1/L2 cache entries, and newer 83xx/8044 entries including `QLA83XX_POLLRD`, `QLA83XX_RDMUX2`, `QLA83XX_POLLRDMWR`, `QLA8044_RDDFE`, `QLA8044_RDMDIO`, and `QLA8044_POLLWR`. Supporting routines include `qla4_8xxx_minidump_pex_dma_read()`, `__qla4_8xxx_minidump_process_rdmem()`, `qla4_8xxx_minidump_process_control()`, and chip-specific ROM/DFE/MDIO handlers.

Flash and system information helpers include `qla4_8xxx_get_flash_info()`, `qla4_8xxx_find_flt_start()`, `qla4_8xxx_get_flt_info()`, `qla4_82xx_get_fdt_info()`, `qla4_82xx_get_idc_param()`, `qla4_82xx_read_flash_data()`, `qla4_8xxx_stop_firmware()`, and `qla4_8xxx_get_sys_info()`. Mailbox and interrupt helpers include `qla4_82xx_queue_mbox_cmd()`, `qla4_82xx_process_mbox_intr()`, `qla4_8xxx_intr_enable()`, `qla4_8xxx_intr_disable()`, `qla4_82xx_enable_intrs()`, `qla4_82xx_disable_intrs()`, `qla4_8xxx_enable_msix()`, and `qla4_8xxx_check_init_adapter_retry()`.

Important local data structures and tables are `crb_128M_2M_map`, `qla4_82xx_crb_hub_agt`, `crb_addr_xform`, `qdev_state`, and `MD_MIU_TEST_AGT_RDDATA`. Hardware/template structures consumed here are defined in `ql4_nx.h` and neighboring qla4xxx headers.

## Control Flow

Register access starts by translating an adapter CRB offset. `qla4_82xx_pci_get_crb_addr_2M()` rejects offsets outside `QLA82XX_CRB_MAX`, maps CAMQM specially, translates direct sub-blocks through `crb_128M_2M_map`, and returns `1` for addresses that need the indirect CRB window. `qla4_82xx_rd_32()` and `qla4_82xx_wr_32()` then acquire `ha->hw_lock`, take the CRB-window semaphore, program `CRB_WINDOW_2M`, perform the read/write, and release the window only for indirect cases.

Adapter memory access has two paths. DDR/QDR memory normally uses MIU test-agent registers with 16-byte aligned reads and read-modify-write for unaligned writes. If an address is outside the DDR bound check or points at OCM/QDR direct windows, the direct path programs the MN/MS window register, validates that the access does not cross a hardware window, maps the PCI BAR page if needed, and performs byte/word/dword/qword MMIO access.

Firmware startup flows through `qla4_8xxx_load_risc()`. It clears stale interrupt state, calls `qla4_8xxx_device_state_handler()`, initializes request/response rings, and requests IRQs. The state handler first updates IDC active/version registers, then loops on the shared device state. `DEV_READY` exits, `DEV_COLD` calls `qla4_8xxx_device_bootstrap()`, `DEV_INITIALIZING` waits, `DEV_NEED_RESET` delegates to the 82xx or 83xx reset handler, `DEV_NEED_QUIESCENT` acknowledges quiesce, and failure/default states run dead-adapter cleanup.

For 82xx bootstrap, `qla4_8xxx_device_bootstrap()` checks whether another function already has live firmware by watching the PEG alive counter. If recovery or a dead counter requires a restart, it sets `DEV_INITIALIZING`, drops the IDC lock around the firmware restart, optionally captures a minidump, calls `qla4_82xx_try_start_fw()`, reacquires IDC, and either marks `DEV_READY` or `DEV_FAILED`.

The 82xx firmware restart sequence retrieves flash offsets, performs `qla4_82xx_start_firmware()`, clears command/receive PEG status, calls `qla4_82xx_load_fw()`, waits for `PHAN_INITIALIZE_COMPLETE`/`PHAN_INITIALIZE_ACK`, records PCIe link width, and waits for receive PEG initialization. `qla4_82xx_pinit_from_rom()` is the most invasive phase: it disables I2Q/NIU paths, halts SRE/EPG/timers/PEGs, asserts global reset, reads the flash CRB-init table signature and address/value pairs, translates each internal CRB address to PCI CRB space, skips sensitive registers, replays writes with required delays, and resets PEG caches.

Reset handling uses shared IDC state. `qla4_82xx_isp_reset()` sets `DEV_NEED_RESET` if the device is ready and marks the caller as reset owner. `qla4_82xx_need_reset_handler()` disables interrupts if online, records reset acknowledgement in `DRV_STATE`, waits for all active functions to acknowledge, clears reset-owner state, and forces `DEV_COLD` unless another function is already initializing. The regular state handler then performs bootstrap.

Minidump collection is template-driven. `qla4_8xxx_collect_md_data()` writes a driver timestamp into the template, seeds saved-state fields for 83xx/8044, walks each entry, checks the capture mask, dispatches on entry type, advances the destination pointer, and marks skipped entries by adding their capture size to `ha->fw_dump_skip_size`. Some failures abort collection; unsupported or masked entries are marked skipped. `qla4_8xxx_get_minidump()` exposes the result by setting `AF_82XX_FW_DUMPED` and emitting a `FW_DUMP=<host_no>` uevent.

Mailbox and interrupt flow is thinner. `qla4_82xx_queue_mbox_cmd()` writes mailbox input registers 1..N, writes mailbox 0 last to wake firmware, then asserts `HINT_MBX_INT_PENDING`. `qla4_82xx_process_mbox_intr()` checks `host_int`, sets `mbox_status_count`, calls the common interrupt-service routine, and unmasks legacy interrupt target status if interrupts remain enabled. `qla4_82xx_enable_intrs()` and `qla4_82xx_disable_intrs()` send mailbox commands and update the legacy target mask register.

## State And Persistence

Persistent software-visible device state is stored in hardware CRB registers shared by all PCI functions on the adapter. `QLA8XXX_CRB_DEV_STATE` records cold/initializing/ready/reset/quiescent/failed state. `QLA8XXX_CRB_DRV_ACTIVE` records which functions have active drivers, and `QLA8XXX_CRB_DRV_STATE` records reset or quiesce acknowledgements. For ISP8022 the function occupies four bits; for ISP8032/8042 it occupies one bit. IDC version registers coordinate driver compatibility.

`ha` carries volatile runtime state including `nx_pcibase`, CRB/MN/MS window values, register tables, flash layout offsets, reset/init timeouts, firmware dump buffers, capture masks, flags such as `AF_FW_RECOVERY`, `AF_82XX_FW_DUMPED`, `AF_8XXX_RST_OWNER`, `AF_INTERRUPTS_ON`, and PCI interrupt configuration. Static globals cache CRB transform data (`crb_addr_xform`, `qla4_8xxx_crb_table_initialized`) and warning/timeout tunables.

Firmware and flash data persist on adapter flash, not in this file. The code reads FLT/FDT, iSCSI CHAP/DDB region metadata, bootloader, firmware image, and IDC timeout values from flash. Firmware minidumps persist in the driver's allocated `ha->fw_dump` buffer until userspace collects or the driver tears it down. Hardware register writes persist only until adapter reset, power cycle, or another function/driver changes the same shared register.

## Dependencies And Integration Points

The file depends on Linux kernel MMIO, PCI, DMA, locking, jiffies/time, delay, and uevent APIs. It includes `ql4_def.h`, `ql4_glbl.h`, `ql4_inline.h`, and `linux/io-64-nonatomic-lo-hi.h`. It relies on qla4xxx-wide structures such as `struct scsi_qla_host`, `struct isp_operations`, firmware dump template structures, flash layout structures, mailbox constants, interrupt bit definitions, and adapter-type helpers `is_qla8022()`, `is_qla8032()`, and `is_qla8042()`.

`ql4_os.c` wires these functions into `qla4_82xx_isp_ops`: firmware start/restart, reset, direct and indirect register access, IDC lock/unlock, ROM-lock recovery, mailbox queueing, mailbox interrupt processing, interrupt handler, and system-info retrieval. `ql4_glbl.h` exports the externally used APIs. `ql4_isr.c`, `ql4_mbx.c`, `ql4_iocb.c`, `ql4_dbg.c`, `ql4_attr.c`, and `ql4_os.c` call the direct register, state, reset, interrupt, and memory helpers from normal driver paths.

The minidump routines are also integrated with 83xx/8044-specific code through shared template types, `qla4_83xx_*` flash/register helpers, PEX DMA constants, and 8044 DFE/MDIO entry formats. The C file therefore sits at the boundary between the 82xx implementation and later 8xxx diagnostic machinery.

## Risks

The register accessors use `BUG_ON(rv == -1)` for invalid CRB offsets, so bad register tables or caller offsets can panic the kernel rather than failing softly. Window programming is shared hardware state; missed locking, wrong lock class, or reentrant calls under the wrong lock can corrupt unrelated MMIO accesses. The IDC and ROM locks spin or sleep for large timeout counts, so hardware semaphore failure can produce long stalls during probe or recovery.

Firmware bootstrap is high risk because it writes many CRB registers from flash-derived data. Corrupt flash, bad CRB address translation, or an incorrect skip list can reset blocks unexpectedly or wedge the adapter. `qla4_82xx_pinit_from_rom()` intentionally skips PCI/function-enable, core clock, SMB, DDR, and cold-reboot magic writes; changes here need hardware validation.

Memory access code has alignment and bounds hazards. MIU read/write paths support only small sizes and depend on careful 8-byte/16-byte packing. Direct PCI memory fallback maps BAR pages dynamically and rejects accesses that cross a hardware window, but callers still need to pass valid sizes and addresses. `qla4_8xxx_ms_mem_write_128b()` requires 128-bit alignment and count semantics that match its descriptor users.

Minidump collection trusts firmware-provided template sizes and offsets while checking only aggregate `data_collected` against `ha->fw_dump_size`. Incorrect entry sizes can desynchronize the walk, and several handlers write data based on template counts. PEX DMA fallback logic allocates DMA buffers in chunks; errors must free the currently allocated coherent buffer exactly once.

Reset coordination risks are multi-function races and stale shared state. The 82xx path uses four-bit function fields while 83xx/8044 uses one bit; mixing those encodings would cause reset acknowledgement or active-driver detection failures. Timeout behavior can mark the device failed while another function is slow to initialize.

Interrupt control combines mailbox commands, hardware target masks, MSI/MSI-X state, and legacy status registers. A missed unmask or wrong target mask can leave the adapter silent; an over-eager unmask in a recovery path can re-enter the ISR while state is inconsistent.

## Test Signals

Build signals include successful compilation of qla4xxx with ISP82xx/83xx/8044 support and no sparse/endian warnings around minidump template fields. Probe signals include successful BAR mapping, flash FLT/FDT discovery or documented fallback defaults, IDC version compatibility logs, transition to `HW State: READY`, request/response ring initialization, and IRQ attachment.

Runtime hardware tests should cover direct and windowed CRB reads/writes, DDR/QDR/OCM memory access through `qla4_82xx_pci_mem_read_2M()` and `qla4_82xx_pci_mem_write_2M()`, mailbox command completion, legacy interrupt masking/unmasking, MSI-X allocation fallback behavior, and `GET_SYS_INFO` population of MAC, serial, model, and port counts.

Recovery tests should force firmware heartbeat loss or adapter reset, observe `DEV_NEED_RESET` to `DEV_COLD` to `DEV_READY`, verify all active functions acknowledge reset in `DRV_STATE`, confirm interrupts are disabled during reset, and ensure `AF_FW_RECOVERY` clears only after successful reset. Flash/firmware tests should validate boot from flash, CRB-init replay, command PEG and receive PEG handshakes, and safe failure to `DEV_FAILED` on corrupt firmware.

Diagnostic tests should enable minidump capture, trigger firmware recovery, verify a non-empty dump buffer with the template followed by captured data, verify skipped-entry flags and skip-size accounting, confirm `FW_DUMP=<host_no>` uevents, and exercise 82xx ROM reads plus 83xx/8044-specific minidump entries where hardware is available.
