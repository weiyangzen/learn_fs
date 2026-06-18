# Research: subset-b-005344 QLogic qla4xxx 8xxx support

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nx.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nx.h

## Purpose

`ql4_nx.h` is the hardware definition header for the qla4xxx 8xxx/NX support code. It defines the CRB address map, register offsets, PCI window layout, device-state constants, hardware semaphore addresses, interrupt register tables, ROM/flash access registers, MIU test-agent controls, and firmware minidump template entry formats consumed by `ql4_nx.c` and the rest of the qla4xxx 8xxx path.

The header is not an abstract interface. It is a register-level contract with QLogic ISP8022-class hardware and later shared 8xxx diagnostics. Most definitions are constants or packed field layouts that must match firmware and hardware documentation.

## Important APIs, Types, And Definitions

Firmware/PEG handshake constants include `PHAN_INITIALIZE_FAILED`, `PHAN_INITIALIZE_COMPLETE`, `PHAN_INITIALIZE_ACK`, `PHAN_PEG_RCV_INITIALIZED`, `CRB_CMDPEG_STATE`, `CRB_RCVPEG_STATE`, `CRB_DMA_SHIFT`, `CRB_TEMP_STATE`, and command PEG retry/delay values. Temperature helpers `qla82xx_get_temp_val()`, `qla82xx_get_temp_state()`, and `qla82xx_encode_temp()` work with `QLA82XX_TEMP_NORMAL`, `QLA82XX_TEMP_WARN`, and `QLA82XX_TEMP_PANIC`.

CRB mapping definitions are the largest part of the header. They define hub and agent IDs (`QLA82XX_HW_*_CRB_AGT_ADR`), PCI/X CRB map slots (`QLA82XX_HW_PX_MAP_CRB_*`), hub-agent encoded addresses (`QLA82XX_HW_CRB_HUB_AGT_ADR_*`), `QLA82XX_PCI_CRB_WINDOWSIZE`, `QLA82XX_PCI_CRB_WINDOW()`, and per-block base macros such as `QLA82XX_CRB_ROMUSB`, `QLA82XX_CRB_NIU`, `QLA82XX_CRB_PEG_NET_*`, `QLA82XX_CRB_PEG_MD_*`, `QLA82XX_CRB_DDR_NET`, `QLA82XX_CRB_QDR_NET`, `QLA82XX_CRB_PCIE`, `QLA82XX_CRB_TIMER`, and `QLA82XX_CRB_MAX`.

Memory range constants describe adapter address spaces: DDR network memory, OCM0/OCM1, QDR network memory, PCIe host address ranges, and the 2 MB PCI map bases such as `QLA82XX_PCI_CRBSPACE`, `QLA82XX_PCI_DIRECT_CRB`, `QLA82XX_PCI_CAMQM`, `QLA82XX_PCI_DDR_NET`, and `QLA82XX_PCI_QDR_NET`. `QLA8XXX_ADDR_IN_RANGE()` is the basic bound-check helper used by the C file.

MIU test-agent definitions include `MIU_CONTROL`, `MIU_TAG`, `MIU_TEST_AGT_*` address/data/control offsets, `MIU_TEST_AGT_ADDR_MASK`, `MIU_TA_CTL_START`, `MIU_TA_CTL_ENABLE`, `MIU_TA_CTL_WRITE`, `MIU_TA_CTL_BUSY`, and the combined control values used for reads and writes. These are central to indirect DDR/QDR memory access and minidump `RDMEM` handling.

Driver coexistence and state definitions include `QLA82XX_CRB_DRV_ACTIVE`, `QLA82XX_CRB_DEV_STATE`, `QLA82XX_CRB_DRV_STATE`, `QLA82XX_CRB_DRV_SCRATCH`, `QLA82XX_CRB_DEV_PART_INFO`, `QLA82XX_CRB_DRV_IDC_VERSION`, `enum qla_regs`, device states `QLA8XXX_DEV_COLD` through `QLA8XXX_DEV_QUIESCENT`, `MAX_STATES`, `QLA82XX_IDC_VERSION`, `ROM_DEV_INIT_TIMEOUT`, and `ROM_DRV_RESET_ACK_TIMEOUT`.

ROM/flash and semaphore definitions include ROMUSB global and ROM offsets, `ROM_LOCK_DRIVER`, `QLA82XX_ROM_LOCK_ID`, `QLA82XX_CRB_WIN_LOCK_ID`, `PCIE_SEM2_LOCK/UNLOCK`, `PCIE_SEM5_LOCK/UNLOCK`, `PCIE_SEM7_LOCK/UNLOCK`, `PCIE_SETUP_FUNCTION`, and `PCIE_SETUP_FUNCTION2`.

Interrupt definitions include target status/mask register offsets for functions 0 through 7, MSI trigger register offsets, `ISR_INT_*` address macros, `ISR_MSI_INT_TRIGGER()`, `ISR_IS_LEGACY_INTR_IDLE()`, `ISR_IS_LEGACY_INTR_TRIGGERED()`, per-function vector bits, and `QLA82XX_LEGACY_INTR_CONFIG`, an initializer for `struct qla4_8xxx_legacy_intr_set` defined elsewhere.

Minidump definitions include entry type constants such as `QLA8XXX_RDCRB`, `QLA8XXX_RDMEM`, `QLA8XXX_RDROM`, `QLA8XXX_CNTRL`, `QLA83XX_POLLRD`, `QLA83XX_RDMUX2`, `QLA83XX_POLLRDMWR`, `QLA8044_RDDFE`, `QLA8044_RDMDIO`, and `QLA8044_POLLWR`; control opcodes such as `QLA8XXX_DBG_OPCODE_WR`, `RW`, `AND`, `OR`, `POLL`, `RDSTATE`, `WRSTATE`, and `MDSTATE`; driver flags `QLA8XXX_DBG_SKIPPED_FLAG` and `QLA8XXX_DBG_SIZE_ERR_FLAG`; and structures `qla8xxx_minidump_entry_hdr`, `_crb`, `_cache`, `_rdocm`, `_rdmem`, `_rdrom`, `_mux`, and `_queue`.

## Control Flow Enabled By The Header

The CRB constants enable a two-stage register access flow. Callers present a 128 MB CRB-space offset; `ql4_nx.c` uses the block/sub-block maps and `QLA82XX_CRB_*` base macros to decide whether the register is directly reachable in the 2 MB BAR or needs `CRB_WINDOW_2M`. Hub-agent mappings are also used to translate flash CRB-init entries into PCI CRB addresses during firmware bootstrap.

The memory range and MIU constants enable indirect reads and writes to adapter memory. The C file checks an address against DDR/QDR/OCM ranges, programs `MIU_TEST_AGT_ADDR_LO/HI`, starts the agent with `MIU_TA_CTL_START_ENABLE` or `MIU_TA_CTL_WRITE_START`, polls `MIU_TA_CTL_BUSY`, and reads or writes data words through the MIU data registers.

The device-state constants define the inter-driver-coordination state machine. Drivers set active bits, compare reset acknowledgement bits, transition `QLA8XXX_CRB_DEV_STATE` through cold, initializing, ready, reset, quiescent, and failed states, and use IDC version/timeout constants to coordinate multiple PCI functions on one adapter.

The interrupt definitions configure the legacy interrupt path. During PCI setup, a function-specific row from `QLA82XX_LEGACY_INTR_CONFIG` supplies the vector bit, target status register, target mask register, and MSI trigger register. ISR code later reads `ISR_INT_VECTOR`/`ISR_INT_STATE_REG`, checks legacy-triggered status, clears the target status register, and updates the target mask.

The minidump structures define a firmware-authored bytecode-like template. The collection engine reads `entry_type`, `entry_size`, capture masks, loop counts, addresses, strides, poll masks, and state indices from these structures, then dispatches to register, memory, ROM, cache, queue, mux, control, and chip-specific handlers. Control entries can write, read/write, mask, poll, and update saved template state.

## State And Persistence

Most header definitions are immutable constants. They describe persistent hardware and firmware contracts rather than owning state. The actual mutable state lives in adapter registers, flash contents, firmware minidump templates, the driver's `ha->reg_tbl`, `ha->nx_legacy_intr`, and runtime buffers.

Hardware state represented by this header includes PEG initialization status, temperature state, firmware version registers, device and driver coordination registers, semaphore lock registers, ROM controller state, interrupt status/mask registers, and MIU test-agent status. These values persist as hardware state until reset, power loss, firmware changes, or another function writes them.

Minidump template structures are persistent across the collection flow in the sense that firmware supplies a template buffer, the driver updates fields such as `driver_flags`, and captured data is appended according to `entry_capture_size`. The header establishes the binary layout that makes those in-memory updates meaningful.

## Dependencies And Integration Points

`ql4_nx.h` depends on constants and types from the qla4xxx driver and Linux integer types. The comment notes that `struct qla4_8xxx_legacy_intr_set` is defined in `ql4_def.h`; `enum qla_regs` indexes are consumed by `ha->reg_tbl` and by inline helpers `qla4_8xxx_rd_direct()`/`qla4_8xxx_wr_direct()`. The minidump structures are consumed directly by `ql4_nx.c` and interoperate with additional 83xx/8044 minidump structures defined in neighboring headers.

The header is integrated with `ql4_os.c` via the 82xx ops table, with `ql4_isr.c` via interrupt macros, with `ql4_dbg.c` and `ql4_os.c` via halt/alive/temp registers, with flash-layout parsing through ROMUSB constants, and with reset/recovery paths through the shared `QLA8XXX_DEV_*` states.

## Risks

The main risk is register-map correctness. A wrong base, window slot, hub-agent address, interrupt register, or MIU offset sends MMIO to the wrong hardware block. Because the C file often treats these constants as trusted and may call `BUG_ON()` on invalid CRB translation, table errors can become kernel crashes or adapter wedges.

Multi-function state encoding is subtle. `QLA8XXX_CRB_DRV_ACTIVE` and `QLA8XXX_CRB_DRV_STATE` are shared registers, but ISP8022 and ISP8032/8042 use different per-function bit layouts in the C code. The constants are shared, so readers must not assume identical bit semantics across chip families.

The header contains dense, low-level macros with repeated names and aliases, including a repeated `QLA82XX_CRB_PEG_MD_3` definition and references to some map symbols whose definitions are not adjacent in the file. Such patterns are typical of vendor hardware maps but increase maintenance risk during refactors.

Minidump structures must match firmware byte layout exactly. Changing field types, sizes, or alignment would break template parsing. Several fields are small packed control bytes embedded in 32-bit layouts, so endian conversion and structure padding deserve attention when moving code across architectures.

Interrupt macros assume the legacy interrupt state machine bit layout and function-to-register mapping. Incorrect `QLA82XX_LEGACY_INTR_CONFIG` initialization can cause missed interrupts, unacknowledged interrupts, or interrupts delivered to the wrong function.

## Test Signals

Header-level validation comes mostly through builds and hardware behavior. A successful qla4xxx build with no macro redefinition or missing-symbol failures is the first signal. Probe-time logs should show valid CRB register reads, firmware version reads, alive-counter movement, IDC state transitions, and successful legacy interrupt configuration.

Register tests should cover direct CRB windows, indirect CRB windows, CAMQM, ROMUSB, MN/MS memory windows, MIU test-agent reads/writes, semaphore lock/unlock paths, and temperature/alive/halt registers. Interrupt tests should verify all configured function vector bits and target masks on hardware that exposes multiple functions.

Minidump tests should parse real firmware templates using every defined base entry family: CRB, memory, ROM, mux, queue, OCM, L1/L2 cache, control, 83xx poll/mux/read-modify-write, and 8044 DFE/MDIO/poll-write. Captured dump size plus skipped size should equal the template-advertised total size.

Recovery tests should exercise every `QLA8XXX_DEV_*` state transition and verify that timeout constants from flash or defaults produce bounded behavior. Flash tests should validate ROM lock, fast read, FLT/FDT parsing, firmware bootstrap, and fallback paths when flash headers are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_nx.h -->
