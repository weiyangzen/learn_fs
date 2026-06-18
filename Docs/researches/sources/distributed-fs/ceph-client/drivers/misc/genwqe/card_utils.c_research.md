# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_utils.c

## Purpose
`card_utils.c` supplies shared GenWQE utilities: endian-aware MMIO accessors with error injection, custom GenWQE CRC32, coherent DMA allocation, user-page pinning and DMA mapping, SGL construction with first/last-page bounce buffers, reset/interrupt helpers, FFDC register collection, VF virtual-window register access, base-clock decoding, and trap control.

## Important APIs, Types, and Functions
Key functions include `__genwqe_writeq()`, `__genwqe_readq()`, `__genwqe_writel()`, `__genwqe_readl()`, `genwqe_read_app_id()`, `genwqe_init_crc32()`, `genwqe_crc32()`, `__genwqe_alloc_consistent()`, `__genwqe_free_consistent()`, `genwqe_user_vmap()`, `genwqe_user_vunmap()`, `genwqe_alloc_sync_sgl()`, `genwqe_setup_sgl()`, `genwqe_free_sync_sgl()`, `genwqe_card_reset()`, `genwqe_set_interrupt_capability()`, `genwqe_read_ffdc_regs()`, `genwqe_ffdc_buff_size()`, `genwqe_ffdc_buff_read()`, `genwqe_read_vreg()`, `genwqe_write_vreg()`, `genwqe_base_clock_frequency()`, `genwqe_stop_traps()`, and `genwqe_start_traps()`.

## Control Flow
MMIO helpers reject injected failures, missing mappings, or offline PCI channels and convert to/from big-endian hardware representation. User mapping pins pages with `pin_user_pages_fast()`, maps each page for DMA, and later unmaps and unpins with dirty marking according to write direction. SGL allocation creates coherent descriptor memory and bounce buffers for partial first/last pages, copies user data into bounce buffers for input, emits chained 8-entry SGL blocks, and copies bounce output back during free. FFDC helpers walk global, unit, secondary, extended-error, trap, and trace registers into arrays used by debugfs.

## State and Persistence
Global CRC32 lookup state lives in `crc32_tab` after initialization. DMA mapping state is held in caller-owned `dma_mapping` and `genwqe_sgl` structures. Reset and trap functions modify hardware registers; no file-system persistence exists.

## Dependencies and Integration Points
This file is used by nearly all GenWQE modules. It depends on PCI DMA APIs, page pinning, I/O accessors, GenWQE register constants, `card_ddcb.h` SGL formats, and debugfs/sysfs/device code that consumes its helpers.

## Risks and Edge Cases
DMA mappings are bidirectional even when comments note read/write refinement. SGL size allocation can fail for large user ranges due to coherent-order limits. Partial-page bounce handling is subtle and must preserve data on writable mappings. MMIO helpers silently return all-ones on failures, so callers must distinguish real register values from error sentinels where possible.

## Test Signals
Run CRC32 known-vector tests, MMIO endian/error-injection tests, pin/unpin leak checks, SGL descriptor decoding for aligned and unaligned buffers, first/last-page copyback tests, FFDC register array bounds tests, reset on old bitstreams, and MSI allocation fallback/error paths.
