# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/arasan-nand-controller.c

## Purpose
`arasan-nand-controller.c` is a raw NAND controller driver for Arasan NFC v3p10 and Xilinx ZynqMP. It implements `exec_op`, timing setup for SDR/NV-DDR, multi-chip-select handling including GPIO CS, DMA page transfers, and optional on-host hardware BCH ECC with software BCH correction workaround.

## Important APIs, Types, and Functions
Core types are `struct arasan_nfc` for controller-wide state, `struct anand` for per-chip state, and `struct anfc_op` for parsed hardware operations. Important functions include `anfc_probe()`, `anfc_remove()`, `anfc_chips_init()`, `anfc_chip_init()`, `anfc_parse_cs()`, `anfc_select_target()`, `anfc_exec_op()`, `anfc_check_op()`, `anfc_parse_instructions()`, `anfc_rw_pio_op()`, the operation-type executors, `anfc_setup_interface()`, `anfc_attach_chip()`, `anfc_detach_chip()`, `anfc_init_hw_ecc_controller()`, `anfc_read_page_hw_ecc()`, and `anfc_write_page_hw_ecc()`.

## Control Flow
Probe allocates controller state, initializes the NAND controller ops, maps registers, resets interrupt state, enables controller and bus clocks, sets a 64-bit DMA mask, parses chip-select wiring, then scans/registers each child NAND node. Per-chip init reads `reg` chip-select indexes and `nand-rb`, sets NAND options (`NAND_BUSWIDTH_AUTO`, `NAND_NO_SUBPAGE_WRITE`, `NAND_USES_DMA`), requires an MTD name/label, calls `nand_scan()`, and registers MTD.

`exec_op` first validates address cycles, transfer length, packet divisibility, and unsupported command+data patterns, then selects the target, writes timing/interface registers, adjusts bus clock if needed, parses NAND instructions into register fields, triggers the operation, waits ready/event bits, and performs PIO data transfers through `DATA_PORT_REG`. Hardware ECC read/write use DMA over full page plus optional OOB. Reads fetch OOB separately, extract hardware syndromes, run software BCH decode because the hardware BCH reporting is unreliable, correct data bits, and update ECC stats. Writes program data with hardware ECC enabled and then checks NAND status.

## State and Persistence
Persistent flash state comes from program/erase commands. Volatile state includes current CS, native/spare CS selection, bus clock rate, per-chip timing/interface registers, ECC configuration, BCH context, error-location buffers, hardware syndrome buffer, and registered MTD devices. GPIO CS descriptors are manually released on remove.

## Dependencies and Integration Points
The driver depends on OF child nodes, clocks named `controller` and `bus`, MMIO registers, DMA mapping, GPIO CS parsing via `rawnand_dt_parse_gpio_cs()`, raw NAND operation parser, BCH library, and MTD registration. It is selected by `CONFIG_MTD_NAND_ARASAN` and matches `"xlnx,zynqmp-nand-controller"` or `"arasan,nfc-v3p10"`.

## Risks
Operation support is constrained: no data-only operations, max five address cycles, max 1 MiB chunks, and packet lengths must divide into supported steps. The controller may read/write rounded-up data cycles, relying on core behavior for harmless extra bytes. Hardware BCH has a known uncorrectable-reporting bug, so the software BCH workaround is critical. Clock changes during target selection can fail and leave the bus clock disabled if re-enable fails. CS parsing rejects ambiguous native/GPIO mixes.

## Test Signals
Run DT probe tests with native CS and GPIO CS layouts, multiple child chips, SDR modes, NV-DDR modes, and the ZynqMP high-speed SDR clock workaround. NAND tests should cover read ID/status, parameter page, page read/write, OOB, erase, raw page I/O, hardware ECC corrected/uncorrectable paths, DMA mapping failures, packet length rejection, and cleanup after partial chip registration failure.
