# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/chain_mode.c

## Purpose
`chain_mode.c` implements STMMAC descriptor management for chained DMA mode, where each descriptor points to the next descriptor through `des3` instead of using only ring-end bits.

## Important APIs, Types, And Functions
- `jumbo_frm()` maps a large linear skb across multiple chained TX descriptors, using 8 KiB chunks for enhanced descriptors and 2 KiB chunks for normal descriptors.
- `is_jumbo_frm()` reports whether a frame exceeds the single-descriptor buffer limit for the active descriptor format.
- `init_dma_chain()` initializes `des3` next pointers for basic or extended descriptor arrays, wrapping the last descriptor back to the first.
- `refill_desc3()` repairs RX `des3` after timestamping hardware may overwrite it on non-extended descriptors.
- `clean_desc3()` repairs TX `des3` after TX timestamping may overwrite it on the last segment.
- `chain_mode_ops` exports these callbacks to the STMMAC core as `struct stmmac_mode_ops`.

## Control Flow
During ring initialization the core calls `.init` to populate next-descriptor addresses. During TX, `.is_jumbo_frm` decides whether a jumbo linear frame must be split, and `.jumbo_frm` maps each chunk into consecutive descriptors before returning the last descriptor index. During RX refill and TX cleanup, timestamp-aware hooks restore chain pointers when hardware used the same field for timestamps.

## State And Persistence
The persistent state is hardware-visible descriptor memory. Software state is the TX/RX queue indices and DMA sidecar entries in STMMAC queues. No separate state is allocated here.

## Dependencies And Integration Points
This file depends on STMMAC queue structures, descriptor ops, DMA mapping, timestamp enable flags, descriptor sizes, and `STMMAC_NEXT_ENTRY()`. It is selected in the core `stmmac-objs` list and used when the platform is configured for chained mode.

## Risks
- Error handling in `jumbo_frm()` returns `-1` on DMA mapping failures after earlier mappings, so callers must clean partial mappings correctly.
- Address calculations cast DMA addresses to 32-bit descriptor fields, limiting applicability on hardware requiring high DMA bits in chained pointers.
- `clean_desc3()` computes a replacement pointer using queue state and timestamp flags; mistakes can corrupt the chain and stall DMA.
- Chained mode interacts subtly with IEEE 1588 timestamp overwrite behavior.

## Test Signals
Use jumbo MTU traffic in chain mode for normal and enhanced descriptors, enable RX/TX hardware timestamping, stress wraparound at the last descriptor, inject DMA mapping failures where possible, and watch for "inconsistent Rx chain" or TX timeout symptoms.
