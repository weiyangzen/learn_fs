# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/fsl_upm.c

## Purpose
Provides a NAND controller driver for Freescale LocalBus User-Programmable Machine configurations. The UPM supplies command and address bus waveforms, while normal memory-mapped byte I/O transfers NAND data. The driver offers a compact `exec_op` implementation and uses software Hamming ECC.

## Important APIs, Types, And Functions
`struct fsl_upm_nand` embeds `nand_controller`, `nand_chip`, `struct fsl_upm`, I/O base, UPM command/address pattern offsets, optional ready/busy GPIOs per chip, multi-chip address-line offsets, and current chip selection. `fun_probe()` parses device-tree properties and resources. `func_exec_instr()` executes individual NAND instructions through `fsl_upm_start_pattern()`, `fsl_upm_run_pattern()`, `fsl_upm_end_pattern()`, byte I/O, and ready waits. `fun_exec_op()` selects the target chip and runs the instruction list.

## Control Flow
Probe maps the memory resource, finds the matching UPM by physical address, reads `fsl,upm-addr-offset` and `fsl,upm-cmd-offset`, optionally reads `fsl,upm-addr-line-cs-offsets`, acquires indexed ready/busy GPIOs, initializes the NAND controller, and calls `fun_chip_init()`. Chip initialization binds the first child node as the NAND flash, builds an MTD name from the resource and node, scans `mchip_count` targets, and registers the MTD.

## State And Persistence
The driver stores only runtime controller state: selected multi-chip number, address-line offsets, GPIO descriptors, and UPM pattern metadata. Persistent flash changes are delegated to raw NAND operations: page writes, erases, OOB, and software ECC data. Removal unregisters the MTD and calls `nand_cleanup()`.

## Dependencies And Integration Points
Depends on raw NAND `exec_op`, MTD registration, Freescale localbus UPM helpers from `asm/fsl_lbc.h`, device-tree properties, memory-mapped I/O, and optional GPIO ready/busy handling through `nand_gpio_waitrdy()`.

## Risks
Only the first child node is used as flash description. Multi-chip count is capped below `NAND_MAX_CHIPS`, and chip-select offsets must match board wiring exactly. Data transfers are byte-wide in this driver even if UPM width is wider for command/address encoding. Missing ready/busy GPIO falls back to software waits, which can be slower or less precise.

## Test Signals
Good signals are successful UPM lookup, correct parsing of pattern offsets and multi-chip offsets, READID via UPM command/address patterns, software-ECC page read/write success, GPIO-ready wait behavior versus soft wait fallback, multi-target selection, and clean unregister/remove.
