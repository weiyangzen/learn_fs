# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-venc.c

## Purpose

This MT6797 VENC driver registers four inverted video encoder subsystem gates under `"mediatek,mt6797-vencsys"`.

## Important APIs, types, and functions

Key definitions are `venc_cg_regs`, `GATE_VENC()`, `venc_clks[]`, `venc_desc`, and the OF platform driver. Generic MediaTek simple probe/remove perform registration.

## Control flow, state, and persistence

The driver registers gates at shifts 0, 4, 8, and 12 using offsets `0x4/0x8/0x0`. `venc_0` is parented by `mm_sel`; the remaining gates use `venc_sel`. Hardware gate state persists until reset or CCF operations change it.

## Dependencies and integration points

It depends on MT6797 bindings and gate helpers. Consumers are video encode/JPEG blocks and associated media runtime-PM code.

## Risks and test signals

Risks are wrong gate polarity/parent selection and failure to enable `mm_sel` for the LARB-like path. Test video encode, JPEG paths, runtime PM, and clk summary.
