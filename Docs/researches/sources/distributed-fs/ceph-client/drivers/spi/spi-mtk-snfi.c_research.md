<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-snfi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-snfi.c

## Purpose

`spi-mtk-snfi.c` drives the SPI-NAND mode of the MediaTek NAND Flash Interface. It is a SPI-MEM controller with a pipelined on-host NAND ECC engine. The core job is translating Linux SPI-NAND page-plus-OOB expectations into the controller's sector/FDM/ECC interleaved layout, including SoC-specific bad-block-marker swaps and ECC/FDM handling.

## Important APIs, Types, and Functions

`struct mtk_snand_caps` captures sector size, maximum sectors, FDM and FDM-ECC sizes, FIFO size, BBM swap behavior, empty-page checking, status masks, and supported spare sizes. `struct mtk_snand_conf` caches selected page and OOB format. `struct mtk_snand` stores the SPI controller, clocks, NFI MMIO base, IRQ completion, caps, ECC engine/configuration, current page format, ECC stats, autofmt flag, and bounce buffer.

Core hardware helpers are `mtk_nfi_reset()`, `mtk_snand_mac_reset()`, `mtk_snand_mac_trigger()`, `mtk_snand_mac_io()`, and `mtk_snand_setup_pagefmt()`. ECC integration uses `mtk_snand_ecc_init_ctx()`, `mtk_snand_ecc_prepare_io_req()`, `mtk_snand_ecc_finish_io_req()`, and cleanup. Page operations are implemented by `mtk_snand_read_page_cache()` and `mtk_snand_write_page_cache()`. Data layout helpers include `mtk_snand_read_fdm()`, `mtk_snand_write_fdm()`, `mtk_snand_bm_swap()`, and `mtk_snand_fdm_bm_swap()`.

## Control Flow

Probe matches SoC caps, gets the external MediaTek ECC engine, maps NFI registers, enables clocks, requests the IRQ, sets a 32-bit DMA mask, switches the block to SNFI mode, applies optional sample/latch delays, sets an initial 2 KiB plus 64-byte page format, registers the pipelined ECC engine, and registers a single-chipselect SPI-MEM controller.

`supports_op` accepts standard one-byte command SPI-MEM operations, optimized page-cache operations with two-byte addresses, and smaller MAC/GPRAM operations. `adjust_op_size` keeps page operations within the configured sector-plus-spare size when not in ECC autofmt mode and keeps generic operations within the 0xa0-byte GPRAM window.

ECC prepare configures page format, sets `autofmt`, and stores ECC config. A matching page read resets MAC/NFI, programs read command/address/dummy/mode, maps DMA memory, enables decode ECC when requested, starts custom-read DMA, waits for IRQ and counters, gathers ECC stats, reads FDM registers, applies BBM swaps, handles empty-page status, and copies deinterleaved data/OOB to the caller. Page write mirrors this path: it copies caller data into the bounce buffer, performs BBM/FDM swaps, writes FDM registers, enables encode ECC when requested, starts program-load DMA, waits for completion and sector count, then disables ECC and custom mode.

Non-page operations go through MAC mode by writing command/address/dummy/data into SNF GPRAM, triggering the MAC engine, and reading back response bytes.

## State and Persistence Behavior

`nfi_cfg` persists the current hardware page format and avoids unnecessary reprogramming. `autofmt`, `ecc_cfg`, and `ecc_stats` are scoped to NAND page I/O request windows. The bounce buffer persists and is resized to fit page plus OOB. No host files are persisted; writes and erases affect the attached SPI-NAND flash, and ECC configuration influences how data and OOB are encoded on media.

## Dependencies and Integration Points

The driver integrates with SPI-MEM, MTD NAND, the NAND ECC engine API, MediaTek ECC helpers, platform/OF matching, clocks, interrupts, DMA mapping, and Linux MTD OOB layout. It advertises SPI dual/quad modes and SPI-MEM ECC capability.

## Risks and Edge Cases

The layout transformation is subtle: autofmt DMA omits ECC parity and places FDM in registers, while Linux expects contiguous page then OOB. Bad-block-marker swaps differ by SoC, so regressions can make flash incompatible with BootROM. ECC parity is intentionally inaccessible, so raw parity inspection is not supported. Page offset masking derives from `fls(page_size + oob_size)`; unexpected memory geometries should be tested carefully.

DMA cleanup paths split normal and error unmapping; missed error handling can leak mappings or copy stale data. The code assumes page operations between ECC prepare and finish are true page cache operations.

## Test Signals

Tests should cover mt7622, mt7629, and mt7986 caps; page sizes 512 through 16 KiB where supported; OOB/spare-size selection; ECC strength negotiation; raw and ECC reads/writes; empty-page reads; FDM free OOB layout; BBM swap behavior; dual/quad read and program-load templates; generic MAC commands; DMA timeout/error paths; IRQ filtering; ECC corrected/failed stats propagation; and remove/probe cleanup of ECC engine, bounce buffer, clocks, and IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mtk-snfi.c -->
