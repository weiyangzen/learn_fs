# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/gpmi-nand.c

## Purpose
Implements the Freescale/NXP i.MX GPMI NAND controller driver with BCH hardware ECC and DMA-driven command execution. It supports i.MX23, i.MX28, i.MX6Q, i.MX6SX, i.MX7D, and i.MX8QXP variants, including SoC-specific clocks, timing limits, BCH strengths, boot ROM bad-block-marker behavior, and runtime power management.

## Important APIs, Types, And Functions
The driver state is `struct gpmi_nand_data` from `gpmi-nand.h`: resources, timing state, BCH geometry, DMA transfer slots, buffers, NAND controller/chip, completions, and SoC devdata. Key initialization paths are `acquire_resources()`, `gpmi_init()`, `gpmi_nand_init()`, `gpmi_nand_attach_chip()`, `gpmi_init_last()`, and `bch_set_geometry()`. ECC and layout functions include `legacy_set_geometry()`, `set_geometry_by_ecc_info()`, `set_geometry_for_large_oob()`, `gpmi_bch_layout_std()`, `gpmi_ecc_read_page()`, `gpmi_ecc_write_page()`, raw page/OOB handlers, `gpmi_count_bitflips()`, and `block_mark_swapping()`. NAND operations are executed by `gpmi_nfc_exec_op()` using chained DMA descriptors built by `gpmi_chain_command()`, `gpmi_chain_wait_ready()`, `gpmi_chain_data_read()`, and `gpmi_chain_data_write()`.

## Control Flow
Probe allocates driver state, selects devdata from OF match, maps GPMI/BCH register blocks, requests BCH IRQ and DMA channel, gets clocks, enables runtime PM, initializes GPMI/BCH registers, allocates temporary DMA buffers, and runs `nand_scan()`. Attach computes final BCH geometry, installs ECC callbacks, OOB layout, optional subpage read support, and skips automatic BBT scan so the driver can run boot-specific setup and `nand_create_bbt()`. Each NAND operation resumes the device, applies pending timings, builds a DMA chain from NAND instructions, optionally programs BCH layout registers, waits for DMA and BCH completions, unmaps scatterlists, copies bounce-buffer reads back, clears BCH state, and autosuspends.

## State And Persistence
Runtime state includes mapped registers, clocks, runtime-PM state, DMA mappings, BCH completion status, computed hardware timings, BCH layout registers, auxiliary/status buffers, raw scratch buffer, and `swap_block_mark`. Persistent flash behavior is significant: BCH ECC is stored inline with payload according to computed geometry, ECC-based OOB reads mostly synthesize OOB with the block mark, raw paths extract/interleave ECC bits manually, and MX23 may transcribe bad-block markers and write an `STMP` fingerprint in the boot search area.

## Dependencies And Integration Points
Depends on raw NAND `exec_op`, MTD OOB layout, DMAengine with MXS PIO support, BCH IRQs, clocks, runtime PM, pinctrl PM, OF compatible data, NAND ECC requirement discovery, and register macros from `gpmi-regs.h` and `bch-regs.h`. It integrates with boot ROM assumptions via `nand_boot_init()`, `mx23_boot_init()`, and `gpmi_block_markbad()`.

## Risks
The physical layout is complex and compatibility-sensitive: geometry choices, GF length, metadata size, ECC strength, and block-marker swapping determine whether existing flash remains readable. Raw read/write paths must preserve bit-level interleaving and byte alignment. DMA chains support at most one data instruction and up to `GPMI_MAX_TRANSFERS`; unsupported operation shapes fail. Timeouts dump registers but leave the underlying hardware in an uncertain state until reset. MX23 BCH reset erratum and block-marker transcription are high-risk hardware-specific paths.

## Test Signals
Strong test signals include successful probe on each compatible SoC, timing negotiation for ONFI SDR/EDO modes, DMA and BCH IRQ completion, full-page ECC read/write with corrected/failed counters, raw page/OOB round trips, subpage reads on MX6-class byte-aligned parity, bad-block marking with and without swapping, MX23 transcription stamp handling, suspend/resume reinitialization, and power-management clock enable/disable coverage.
