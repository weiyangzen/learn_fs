# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/hantro_g2.c

## Purpose
Provides common G2 decoder interrupt/reset behavior and shared decoded-buffer layout calculations for G2 codecs.

## Important APIs, Types, And Functions
Exports `hantro_g2_irq`, `hantro_g2_reset`, `hantro_g2_check_idle`-adjacent reset behavior through active polling, and offset helpers `hantro_g2_chroma_offset`, `hantro_g2_motion_vectors_offset`, `hantro_g2_luma_compress_offset`, and `hantro_g2_chroma_compress_offset`.

## Control Flow And State
`hantro_g2_irq` validates the IRQ bit, clears interrupt status via masked register writes, gates clock, finishes success on `DEC_RDY_INT`, logs recoverable/error status bits, and only reports buffer error once the hardware is no longer running. `hantro_g2_reset` uses hardware abort and waits until decode enable clears to avoid programming a running block.

## Dependencies And Integration Points
Used by G2 HEVC and VP9 backends and variants. Offset helpers depend on negotiated `ref_fmt`, HEVC SPS-derived MV sizing, and compressed reference-size helpers from `hantro_hw.h`.

## Risks And Test Signals
The reset path busy-waits with `mdelay(1)` until inactive and warns that programming a running IP can hang the CPU. Tests should cover successful IRQ, bus/error/timeout IRQ status, abort handling, watchdog reset, and buffer-size calculations for 8-bit/10-bit HEVC with and without compression.
