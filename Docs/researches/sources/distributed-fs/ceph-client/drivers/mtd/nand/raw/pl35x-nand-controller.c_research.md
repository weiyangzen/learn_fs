# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/pl35x-nand-controller.c

Purpose: this is the ARM PL35X/PL353 NAND controller driver used on Xilinx-style SMC systems. It implements raw NAND `exec_op`, SDR timing programming, optional hardware Hamming ECC, OOB layout selection, and one child NAND chip behind the SMC.

Important APIs, types, and functions: `struct pl35x_nandc` owns configuration/data MMIO windows, the NAND controller, selected chip, assigned chip-select bitmap, and temporary ECC buffer. `struct pl35x_nand` stores chip state, CS, address-cycle count, cached ECC config, and timings. Core helpers include `pl35x_nand_exec_op()`, `pl35x_nfc_setup_interface()`, `pl35x_nand_read_page_hwecc()`, `pl35x_nand_write_page_hwecc()`, `pl35x_nand_recover_data_hwecc()`, and `pl35x_nand_attach_chip()`.

Control flow: probe maps the parent AMBA SMC registers plus the NAND data resource, resets controller state by disabling/clearing interrupts, setting 8-bit bus width, bypassing ECC, and programming ECC command triggers, then scans child nodes. Per operation, `pl35x_nfc_exec_op()` selects the chip, applies cached timings/ECC config, and runs a parser that packs command/address/data/wait-ready phases into SMC command/data accesses. Hardware ECC page read/write paths enable APB ECC mode, issue controller-specific page commands, use the special `ECC_LAST` data access on the final transfer, read/write OOB ECC bytes, poll ECC completion, and return to bypass mode.

State and persistence: cached per-chip timing and ECC registers are restored on target selection. On-flash state includes optional flash BBT use and legacy descriptors for on-die ECC. The driver has no explicit PM; hardware register state is initialized at probe and updated during attach/setup.

Dependencies and integration points: it depends on the AMBA parent resource, `memclk` from the parent DT node for timing conversion, raw NAND parser APIs, MTD OOB layout helpers, and compatible `arm,pl353-nand-r2p1`. Hardware ECC supports only 1-bit/512-byte correction and page sizes from 512 bytes through 2 KiB.

Risks: hardware ECC is limited and rejects larger pages or unsupported OOB sizes, so DT/NAND requirements must match. The `ECC_LAST` controller quirk prevents generic ECC helpers and makes last-transfer sizing sensitive. `setup_interface()` obtains `memclk` on each call and has empirical timing adjustments for fast modes. Only one CS is supported. Timeouts on controller interrupt or ECC busy polling indicate stalled hardware.

Test signals: child-node probe with exactly one CS, timing setup across SDR modes, 8/16-bit bus switching for forced byte operations, raw `exec_op` reads/writes, hardware ECC read/write with 16- and 64-byte OOB layouts, ECC correction/failure accounting, BBT behavior, and timeout logs from SMC/ECC polling.
