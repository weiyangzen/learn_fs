# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-vdecsys.c

## Purpose

This MT6795 VDEC system driver registers the video decoder engine and LARB gates. It is a small subsystem provider for `"mediatek,mt6795-vdecsys"`.

## Important APIs, types, and functions

The file defines `vdec0_cg_regs`, `vdec1_cg_regs`, `GATE_VDEC()`, `vdec_clks[]`, and `vdec_desc`. It relies on `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()` through a normal OF-matched platform driver.

## Control flow, state, and persistence

Generic probe registers two inverted set/clear gates: `vdec_cken` on the `vdec_sel` parent and `vdec_larb_cken` on the `mm_sel` parent. VDEC0 uses offsets `0x0/0x4/0x0`; VDEC1 uses `0x8/0xc/0x8`. Inverted gate semantics mean the register bit polarity is opposite a normal set/clear gate. State is the hardware gate value and clock-provider registration.

## Dependencies and integration points

Dependencies are MT6795 bindings and MediaTek gate/simple helpers. It integrates with the VDEC codec driver, MMSYS/SMI/LARB paths, and topckgen parent clocks.

## Risks and test signals

Risks include inverted gate polarity mistakes and missing LARB clock enable during decode DMA. Test with video decode workloads, runtime PM, SMI/LARB access, and `clk_summary` gate transitions while the decoder is active and idle.
