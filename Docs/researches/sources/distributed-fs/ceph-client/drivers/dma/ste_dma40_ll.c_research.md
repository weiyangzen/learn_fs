# sources/distributed-fs/ceph-client/drivers/dma/ste_dma40_ll.c

## Purpose
`ste_dma40_ll.c` converts DMA40 channel configuration and scatterlists into hardware linked-list items for physical and logical DMA40 channels. It is the register-packing layer used by `ste_dma40.c` during descriptor preparation and LCPA/LCLA programming.

## Important APIs, Types, And Functions
Public helper functions are `d40_log_cfg`, `d40_phy_cfg`, `d40_phy_sg_to_lli`, `d40_log_sg_to_lli`, `d40_log_lli_lcpa_write`, and `d40_log_lli_lcla_write`. Private helpers include `d40_width_to_bits`, `d40_phy_fill_lli`, `d40_seg_size`, `d40_phy_buf_to_lli`, `d40_log_lli_link`, `d40_log_fill_lli`, and `d40_log_buf_to_lli`.

`d40_phy_cfg` and `d40_log_cfg` translate `stedma40_chan_cfg` into default source/destination config words. Physical config sets event line, master port, transfer mode, error/terminal interrupts, packet enable/size, element width, priority, and endianness. Logical config builds LCSP1/LCSP3 defaults with increment, master port, interrupt enable, packet size, and element width bits.

## Control Flow
Physical SG conversion starts with `d40_phy_sg_to_lli`. If no fixed target address is supplied, it enables address increment. Each SG entry is passed to `d40_phy_buf_to_lli`, which splits the buffer into legal hardware segment sizes using `d40_seg_size`. Each segment is packed by `d40_phy_fill_lli`, which validates address alignment and minimum transfer size, writes element count/index, pointer, config, and link pointer, and marks terminal interrupt only on the last required segment.

Logical SG conversion is similar but writes compact logical LCSP entries instead of physical standard channel registers. `d40_log_sg_to_lli` iterates the SG list, chooses either device address or SG address, and delegates splitting to `d40_log_buf_to_lli`. Later, the main driver uses `d40_log_lli_lcpa_write` for the first active item and `d40_log_lli_lcla_write` for linked entries; both call `d40_log_lli_link` to set source/destination next offsets and terminal interrupt bits.

## State And Persistence
The file does not maintain global state. It mutates caller-owned LLI arrays and writes logical LLIs to MMIO/SRAM-backed LCPA or LCLA memory with `writel_relaxed`. The generated LLIs persist only as long as the descriptor and associated DMA-visible memory remain valid.

## Dependencies And Integration Points
The code depends on DMAEngine width constants, Linux scatterlists, register bit definitions from `ste_dma40_ll.h`, and channel config types from `ste_dma40.h`. It is tightly integrated with `ste_dma40.c` descriptor allocation: physical LLIs are DMA-mapped and synchronized by the caller, while logical LLIs are copied into LCPA/LCLA windows during transfer loading.

## Risks
Alignment and size handling are critical. `d40_phy_fill_lli` rejects unaligned data and too-small transfers, while logical fill uses `BUG_ON` if a segment exceeds `STEDMA40_MAX_SEG_SIZE`, making upstream length calculation correctness important. Both physical and logical SG conversion assign the return value repeatedly; the caller checks only the last conversion result, so source-side failures could be overwritten by destination-side conversion if not handled carefully in callers. The segment sizing logic must maintain source and destination width compatibility or residue and element counts will be wrong.

## Test Signals
Tests should exercise width mappings for 1, 2, 4, and 8 byte widths; physical LLI generation for fixed device and incrementing memory addresses; logical LCSP address splitting; cyclic physical linkback; maximum segment splitting around `STEDMA40_MAX_SEG_SIZE`; unaligned SG rejection; terminal interrupt placement; and LCPA/LCLA writes with expected next offsets.
