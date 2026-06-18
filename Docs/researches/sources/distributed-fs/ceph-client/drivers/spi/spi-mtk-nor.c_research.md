<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-nor.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-nor.c

## Purpose

`spi-mtk-nor.c` is a MediaTek SPI NOR controller driver focused on SPI-MEM flash operations. It supports optimized memory reads through controller DMA, small generic program/register-style transactions through the PRGDATA/SHIFT register windows, page program using buffered or unbuffered paths, optional IRQ-driven DMA completion, and runtime PM around controller clocks.

## Important APIs, Types, and Functions

`struct mtk_nor_caps` describes SoC DMA address width and an extra dummy bit needed by newer IP. `struct mtk_nor` stores controller, device, MMIO base, coherent bounce buffer, clocks, current SPI frequency, write-buffer state, IRQ/completion state, high-DMA flag, and caps.

Operation selection is driven by `mtk_nor_supports_op()`, `mtk_nor_adjust_op_size()`, `mtk_nor_match_read()`, and `mtk_nor_match_prg()`. Execution helpers include `mtk_nor_cmd_exec()`, `mtk_nor_reset()`, `mtk_nor_set_addr()`, `mtk_nor_setup_bus()`, `mtk_nor_dma_exec()`, `mtk_nor_read_dma()`, `mtk_nor_read_bounce()`, `mtk_nor_read_pio()`, `mtk_nor_pp_buffered()`, `mtk_nor_pp_unbuffered()`, and `mtk_nor_spi_mem_prg()`. The SPI core fallback message path uses `mtk_nor_transfer_one_message()` with a six-byte maximum message size.

## Control Flow

Probe maps the controller, gets required and optional clocks, loads SoC caps, sets the DMA mask, allocates a host controller, allocates an aligned coherent bounce buffer, enables clocks, initializes registers, optionally requests an IRQ, enables runtime PM, and registers the controller.

For SPI-MEM operations, the driver first validates that command bus width is single-bit and that the address/data/dummy combination maps to either optimized read, page program, or small PRG mode. `adjust_op_size` constrains DMA reads to alignment and timeout-safe sizes, constrains page program to 128-byte buffered chunks or one byte for unbuffered writes, and constrains fallback PRG transactions to the small register windows.

`exec_op` sends no-address or nonstandard operations through `mtk_nor_spi_mem_prg()`. Data-out with 3- or 4-byte addresses uses buffered page program for 128 bytes or unbuffered single-byte write. Matching reads set the address and bus mode, use PIO for one byte, otherwise use DMA directly into the caller buffer or through the coherent bounce buffer if the destination is not 16-byte aligned. DMA read failures trigger a controller reset and one retry.

## State and Persistence Behavior

Runtime state includes the cached write-buffer enable state (`wbuf_en`), high-DMA support, optional IRQ completion, and the coherent bounce buffer. Register state includes bus-width mode, four-byte address mode, write-buffer enable, write-enable/status-poll disable bits, and DMA address registers. Runtime PM disables and re-enables all clocks but does not persist user data.

Persistent effects occur on the external NOR flash when upper layers issue program/erase/status commands; the driver itself stores no file-backed state.

## Dependencies and Integration Points

The driver integrates with SPI-MEM, SPI controller registration, platform devices, OF compatible strings `mediatek,mt8173-nor`, `mt8186-nor`, and `mt8192-nor`, DMA mapping/coherent allocation, interrupts, completions, clocks, and runtime/system PM. It is intended to be consumed by SPI NOR and MTD layers through `spi_mem`.

## Risks and Edge Cases

The coherent bounce buffer allocation is checked for 16-byte virtual alignment even though DMA alignment also matters to hardware; the allocation size includes extra alignment slack but the code does not adjust to an aligned offset. `mtk_nor_pp_buffered()` writes data four bytes at a time and assumes adjusted page-program lengths are compatible with that loop. DMA timeout calculations depend on `spi_freq`; incorrect clock rates can produce too-short polling timeouts. IRQ is optional, so both interrupt and polling completion paths need coverage.

The fallback message path has a small maximum size and manually packs all transfer bytes into PRGDATA in reverse register order; it is useful for simple SPI messages but not a full general-purpose controller.

## Test Signals

Validation should cover supported read opcodes and dummy cycles, single/dual/quad reads, 3-byte and 4-byte addresses, one-byte PIO reads, aligned DMA reads, unaligned bounce reads, DMA retry after reset, 128-byte buffered page program, one-byte unbuffered writes, small command/status reads through PRG mode, IRQ and polling completion paths, runtime suspend/resume, and probe failures for DMA mask, clocks, IRQ request, and controller registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-nor.c -->
