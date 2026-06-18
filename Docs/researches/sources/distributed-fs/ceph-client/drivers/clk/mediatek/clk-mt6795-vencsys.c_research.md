# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-vencsys.c

## Purpose

This MT6795 VENC system driver registers video encoder, JPEG encoder/decoder, and LARB gates. It provides the `"mediatek,mt6795-vencsys"` clock provider for media codecs.

## Important APIs, types, and functions

Key definitions are `venc_cg_regs`, `GATE_VENC()`, `venc_clks[]`, and `venc_desc`. Binding and registration use `of_match_clk_mt6795_vencsys[]`, `mtk_clk_simple_probe()`, and `mtk_clk_simple_remove()`.

## Control flow, state, and persistence

Generic simple probe registers four inverted set/clear gates using offsets `0x4/0x8/0x0`, with shifts 0, 4, 8, and 12. Parents are `venc_sel` for codec engines and `venc_sel` for the LARB gate. Hardware gate state persists until reset or runtime clock operations change it.

## Dependencies and integration points

The file depends on MT6795 clock bindings and MediaTek gate/simple helpers. It integrates with V4L2 codec drivers, JPEG blocks, SMI/LARB, and the topckgen `venc_sel` parent.

## Risks and test signals

Risks are gate polarity and shift mistakes, plus the module description says "vdecsys" even though the driver is VENC. Test with video encode/JPEG workloads, runtime PM, and clock summary transitions for all four gates.
