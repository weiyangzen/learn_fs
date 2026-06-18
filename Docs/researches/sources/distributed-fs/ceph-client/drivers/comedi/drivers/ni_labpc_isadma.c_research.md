# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_isadma.c

## Purpose
`ni_labpc_isadma.c` provides optional ISA DMA support for Lab-PC ISA boards. It is split from the common driver so non-ISA bus front ends can share common logic without always depending on ISA DMA.

## Important APIs, Types, And Functions
The module exports `labpc_setup_dma()`, `labpc_drain_dma()`, `labpc_handle_dma_status()`, `labpc_init_dma_chan()`, and `labpc_free_dma_chan()`. `labpc_suggest_transfer_size()` computes a DMA buffer size targeting at most one third of a second per transfer and respecting sample size and descriptor max size. `handle_isa_dma()` drains current DMA data, reprograms the descriptor when more data is expected, and clears the board DMA terminal-count interrupt.

## Control Flow
The ISA front end calls `labpc_init_dma_chan()` after common attach if an IRQ exists. Only DMA channels 1 and 3 are accepted; a single read buffer of `0xff00` bytes is allocated. During command setup, common code calls `labpc_setup_dma()` when it selects `isa_dma_transfer`. That computes descriptor size, clamps to remaining count for count-limited commands, programs the ISA DMA controller, and sets `CMD3_DMAEN | CMD3_DMATCINTEN` in the common command-register shadow. On interrupts, common code calls `labpc_handle_dma_status()`; if terminal count or external stop status is present, `handle_isa_dma()` drains and optionally reprograms DMA.

`labpc_drain_dma()` disables host DMA to get residue, computes received samples, updates `devpriv->count`, adjusts next descriptor size, and writes samples from the DMA buffer to the Comedi async buffer.

## State And Persistence
The persistent DMA pointer lives in `devpriv->dma`. The active descriptor's `size`, `maxsize`, `virt_addr`, and channel are maintained by Comedi ISA DMA helpers. `devpriv->count` and `devpriv->cmd3` are shared with common command/interrupt code.

## Dependencies And Integration Points
The file depends on `comedi_isadma`, `ni_labpc.h`, `ni_labpc_regs.h`, and `ni_labpc_isadma.h`. It exports GPL symbols consumed by `ni_labpc_common.c` and `ni_labpc.c` when `CONFIG_COMEDI_NI_LABPC_ISADMA` is enabled.

## Risks
DMA sizing uses integer frequency calculations and can overflow/underestimate for unusual trigger values if command validation changes. Residue handling is critical for external stop triggers. Only channels 1 and 3 are valid; invalid channels silently leave DMA unavailable. Shared mutation of `cmd3` means common code must write the command register after DMA setup.

## Test Signals
Tests should cover valid/invalid DMA channel allocation, descriptor size for timer and non-timer commands, count-limited clamping, sample-size alignment, residue-to-sample conversion, count decrement and leftover calculation, reprogramming when leftover remains, terminal-count status detection for Lab-PC+ and Lab-PC-1200, interrupt clear write, and free path with null DMA.
