# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-vdec.c

## Purpose

This MT6797 VDEC driver registers video decoder gates: decoder engine, active, cken, and LARB1. It provides clocks for `"mediatek,mt6797-vdecsys"`.

## Important APIs, types, and functions

Important data includes two gate-register banks, `GATE_VDEC0()`, `GATE_VDEC1()`, `vdec_clks[]`, and `vdec_desc`. The platform driver uses `mtk_clk_simple_probe()`/`remove`.

## Control flow, state, and persistence

Generic probe registers three inverted gates on `vdec0_cg_regs` at shifts 8, 4, and 0, plus one inverted LARB gate on `vdec1_cg_regs` at shift 0. Parents are `vdec_sel` and `mm_sel`. State is CCF registration and hardware gate bits.

## Dependencies and integration points

Dependencies are MT6797 clock bindings and MediaTek gate helpers. It integrates with video decoder runtime PM, V4L2 codec stack, and SMI/LARB1 memory paths.

## Risks and test signals

Risks include inverted gate misuse, missing `vdec_active`, and LARB clock dependencies. Test video decode, power-domain cycling, and clock enable/disable traces.
