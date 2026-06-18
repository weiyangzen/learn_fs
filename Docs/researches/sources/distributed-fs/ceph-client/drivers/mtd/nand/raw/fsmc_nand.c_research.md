# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsmc_nand.c

## Purpose
Implements the ST/SPEAr Flexible Static Memory Controller NAND driver. It maps separate NAND data, command, address, and FSMC register regions; negotiates NAND timings; supports optional DMA or programmed I/O; configures hardware ECC for older 1-bit and revision-8 8-bit modes; and registers the NAND as an MTD device.

## Important APIs, Types, And Functions
`struct fsmc_nand_data` embeds `nand_controller`, `nand_chip`, AMBA-style PID, bank, clock, DMA channels, completions, timing configuration, and mapped I/O/register addresses. Timing is handled by `fsmc_calc_timings()`, `fsmc_nand_setup()`, and `fsmc_setup_interface()`. Data movement goes through `fsmc_exec_op()`, `fsmc_read_buf()`, `fsmc_write_buf()`, and DMA helpers. ECC uses `fsmc_enable_hwecc()`, `fsmc_read_hwecc_ecc1()`, `fsmc_correct_ecc1()`, `fsmc_read_hwecc_ecc4()`, `fsmc_bch8_correct_data()`, and `fsmc_read_page_hwecc()`.

## Control Flow
`fsmc_nand_probe()` parses DT configuration, maps named resources, enables the clock, reads the AMBA-style ID, initializes optional DMA, applies static DT timings if present, installs controller ops, scans one NAND chip, and registers MTD. `fsmc_exec_op()` handles command/address/data/wait instructions directly through memory-mapped command/address/data windows. Attach chooses ECC behavior based on controller revision and requested ECC engine.

## State And Persistence
Runtime state includes applied timing registers, DMA completions, mapped bank register state, and ECC mode. Persistent flash state is normal NAND content plus OOB/ECC layout. Suspend disables the clock; resume re-enables it, reapplies static timings when present, and resets the NAND. Removal unregisters MTD, cleans NAND, disables the bank, and releases DMA channels.

## Dependencies And Integration Points
Depends on raw NAND controller ops, MTD OOB layout, clock framework, platform named resources, optional DMAengine memcpy channels, OF properties (`bank-width`, `nand-skip-bbtscan`, `timings`, `bank`), and software Hamming correction helpers for the 1-bit hardware syndrome path.

## Risks
`host->mode` defaults to zero in the shown code, so DMA paths are present but not selected unless external/platform data changes it. Revision-8 ECC requires a strict data-then-ECC OOB read sequence and supports only specific OOB sizes. Erased-page handling for BCH8 is heuristic and can hide or over-report errors near the correction limit. Timing math rejects SDR modes with `tRC_min < 30000`, limiting high-speed support.

## Test Signals
Validate resource mapping by name, AMBA ID logging, timing negotiation and DT timing fallback, 8-bit/16-bit bus access, DMA and PIO paths where enabled, ECC1 and ECC4 layouts, BCH8 erased-page behavior, suspend/resume with NAND reset, and MTD read/write/erase with corrected/failed ECC counters.
