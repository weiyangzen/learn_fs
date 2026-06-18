# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/sama5d4_vdec_hw.c

## Purpose
Defines the Microchip/Atmel SAMA5D4 Hantro VDEC variant. It advertises G1 decoder formats, postprocessed YUYV output, codec operations, IRQ wiring, clock names, and codec capability bits.

## Important APIs, Types, And Functions
- Exports `sama5d4_vdec_variant`.
- Defines `sama5d4_vdec_fmts`, `sama5d4_vdec_postproc_fmts`, `sama5d4_vdec_codec_ops`, `sama5d4_irqs`, and `sama5d4_clk_names`.
- Uses generic G1 run/reset/init/exit functions for MPEG-2, VP8, and H.264.

## Control Flow
The Hantro core consumes the variant at probe. Userspace sees NV12 raw capture plus MPEG-2/VP8/H.264 stateless coded formats up to HD bounds. Codec jobs dispatch to generic G1 implementations, and interrupts use `hantro_g1_irq`.

## State And Persistence
Only static const tables are defined. Runtime state is owned by the Hantro core and codec-specific generic contexts. No persistent storage is touched.

## Dependencies And Integration Points
Depends on `hantro.h`, generic G1 decoder helpers, the G1 postprocessor, and a single `vdec_clk` clock resource from platform data/device tree.

## Risks And Edge Cases
The file assumes generic G1 behavior fully matches SAMA5D4 hardware. Format bounds are HD-limited; incorrect limits would affect userspace negotiation. Single-clock naming must match integration data.

## Test Signals
Probe with SAMA5D4 resources, verify `vdec_clk` acquisition, run MPEG-2/VP8/H.264 decode conformance streams, test YUYV postprocessed output, and confirm clean IRQ completion and reset behavior.
