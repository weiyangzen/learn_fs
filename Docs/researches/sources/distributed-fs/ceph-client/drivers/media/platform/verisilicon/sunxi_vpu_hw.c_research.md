# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/sunxi_vpu_hw.c

## Purpose
Defines the Allwinner Hantro G2 VP9 decoder variant, including tiled raw formats, postprocessed formats, VP9 codec ops, clock setup, reset hook, IRQ wiring, and variant flags.

## Important APIs, Types, And Functions
- Exports `sunxi_vpu_variant`.
- Defines `sunxi_vpu_dec_fmts`, `sunxi_vpu_postproc_fmts`, `sunxi_vpu_hw_init()`, `sunxi_vpu_reset()`, `sunxi_vpu_codec_ops`, `sunxi_irqs`, and `sunxi_clk_names`.
- Uses generic G2 VP9 run/done/init/exit helpers and `hantro_g2_postproc_ops`.

## Control Flow
Probe selects the variant, sets the module clock to 300 MHz in init, exposes NV12_4L4/P010_4L4 tiled decode targets and VP9 coded input up to UHD, and dispatches jobs to G2 VP9 operations. Reset goes through the reset controller, and completion uses the generic G2 IRQ handler.

## State And Persistence
Only static tables are owned here. Runtime state is in Hantro core/G2 VP9 contexts. The module clock rate persists for the active device lifetime.

## Dependencies And Integration Points
Depends on two clocks named `mod` and `bus`, a reset controller, generic G2 VP9 decoder support, and postprocessing support. Variant flags `double_buffer`, `legacy_regs`, and `late_postproc` tune Hantro core behavior for this hardware.

## Risks And Edge Cases
Clock-rate programming assumes the first clock is the module clock. Format step size is 32 rather than the common macroblock step, so negotiation must match G2 tiling requirements. Variant flags are critical for register layout and postproc timing.

## Test Signals
Verify probe clock/reset resources, VP9 conformance decode on 8-bit and 10-bit streams, postprocessed NV12/P010 output, UHD boundary sizes, double-buffer behavior, and reset recovery.
