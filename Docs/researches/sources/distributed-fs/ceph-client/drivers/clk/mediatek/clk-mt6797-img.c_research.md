# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-img.c

## Purpose

This MT6797 imgsys driver registers image subsystem gates for FDVT, DPE, DIP, and LARB6. It provides the `"mediatek,mt6797-imgsys"` clock domain for camera/imaging blocks.

## Important APIs, types, and functions

Important definitions are `img_cg_regs`, `GATE_IMG()`, `img_clks[]`, `img_desc`, and the OF match table. The driver is descriptor-only and uses `mtk_clk_simple_probe()`/`mtk_clk_simple_remove()`.

## Control flow, state, and persistence

The generic probe registers four normal set/clear gates at offsets `0x4/0x8/0x0`, all parented by `mm_sel`. The gate shifts are 11, 10, 6, and 0. Hardware gate state and the CCF provider are the only lasting state.

## Dependencies and integration points

Dependencies are `clk-mtk.h`, `clk-gate.h`, and `dt-bindings/clock/mt6797-clk.h`. It integrates with image processing, face detection, depth/dual-pixel processing, DIP, and SMI LARB6 consumers.

## Risks and test signals

Risks include shifted gate IDs and lack of image pipeline clocking under runtime PM. Test camera/imaging pipelines, LARB6 DMA, and gate toggling in `clk_summary`.
