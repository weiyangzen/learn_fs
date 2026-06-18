# sources/distributed-fs/ceph-client/drivers/spi/spi-amlogic-spifc-a4.c

## Purpose

`spi-amlogic-spifc-a4.c` is a SPI-MEM flash-controller driver for Amlogic A4-class hardware. It supports raw SPI flash transfers and integrates a pipelined on-host NAND ECC engine for SPI NAND page read/write operations.

The controller uses a command FIFO, DMA-address commands, raw transfer-size fields, bus-width configuration, and an info buffer for ECC metadata/OOB bytes.

## Important APIs, types, and functions

- `struct aml_sfc` stores clocks, SPI controller, regmap, capability data, ECC engine, DMA addresses, scratch buffers, transfer flags, RX tuning, and chip-select state.
- `struct aml_sfc_ecc_cfg` and `struct aml_sfc_caps` describe supported BCH ECC layouts.
- `aml_sfc_wait_cmd_finish()`, `pre_transfer()`, and `end_transfer()` manage command FIFO sequencing and chip-select idle cycles.
- `aml_sfc_send_cmd()`, `send_addr()`, and `send_cmd_addr_dummy()` emit SPI-MEM command phases.
- `aml_sfc_dma_buffer_setup()` and `release()` map data and info buffers and program DMA address commands.
- `aml_sfc_raw_io_op()` handles non-ECC raw data transfers.
- `aml_sfc_read_page_hwecc()` and `write_page_hwecc()` use hardware BCH ECC, data/info scratch buffers, and OOB packing/unpacking.
- `aml_sfc_ecc_*` callbacks implement NAND on-host hardware ECC engine operations.
- `aml_sfc_setup()` applies SPI mode and clock settings.

## Control flow

Probe allocates a SPI controller, reads match data, maps the register block through regmap, allocates a combined data/info buffer, enables clocks, enables SPI mode, sets a 32-bit DMA mask, registers a NAND ECC engine, reads optional `amlogic,rx-adj`, fills controller callbacks/capabilities, and registers the SPI controller.

`exec_op()` selects chip select, emits pre-transfer idle/setup cycles, writes command/address/dummy phases, configures data bus width, then chooses the hardware-ECC page path for recognized SPI NAND page-cache opcodes when ECC is active and not raw. Otherwise it uses raw DMA transfer. ECC prepare/finish callbacks set transfer flags according to NAND page request mode and update MTD ECC stats after reads.

## State and persistence behavior

Hardware state persists in `SFC_SPI_CFG`, command FIFO, DMA address commands, clock rate, and CS selection. Software transfer flags in `sfc->flags` describe the current NAND page request mode (`DATA_ONLY`, `OOB_ONLY`, `DATA_OOB`, `AUTO_OOB`, `RAW_RW`, `HWECC`). ECC context is allocated per NAND device and stored both in `nand->ecc.ctx.priv` and `sfc->priv`. Scratch buffers are device-managed and reused across transfers.

## Dependencies and integration points

The driver depends on platform/OF (`amlogic,a4-spifc`), regmap-mmio, gate/core clocks, DMA mapping, SPI-MEM, MTD SPI NAND, and NAND ECC engine infrastructure. It advertises `mem_caps.ecc = true`, dual/quad/octal TX/RX mode bits, two chipselects, and min/max frequencies.

## Risks and edge cases

- The source contains duplicated lines in `aml_sfc_send_addr()` (`u8 val;`) and `aml_sfc_write_page_hwecc()` (`if (sfc->flags & SFC_AUTO_OOB)`), which would need cleanup in a compile-checked tree.
- `aml_sfc_wait_cmd_finish(sfc, 0)` in normal end-transfer converts to a zero timeout in regmap polling; behavior depends on polling helper semantics and may be too aggressive.
- DMA-safe buffer checks require 8-byte alignment and `virt_addr_valid()`; unaligned caller buffers are copied, adding allocation failure paths.
- ECC flag state is shared in `struct aml_sfc`; overlapping operations are expected to be serialized by the SPI/NAND stack.
- OOB layout assumes BCH8 info bytes and two user bytes per step.
- The hardware-ECC page path recognizes opcodes by command value and depends on NAND ECC prepare/finish sequencing to set data/OOB flags.

## Test signals

Build with SPI-MEM, MTD, and NAND ECC support. Runtime tests should cover raw SPI NOR-style reads/writes, SPI NAND page reads/writes with hardware ECC, raw NAND mode, OOB-only and data+OOB modes, ECC correction and uncorrectable errors, DMA buffer alignment fallbacks, dual/quad/octal opcode bus widths, clock clamping, and two chipselects.
