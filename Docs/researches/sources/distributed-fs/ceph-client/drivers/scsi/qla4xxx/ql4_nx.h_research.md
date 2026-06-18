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
