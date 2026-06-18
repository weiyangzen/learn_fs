# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6797-mm.c

## Purpose

This MT6797 multimedia clock driver registers MMSYS gates for SMI, MDP, display, DSI, DPI, MJC/LARB4, and supporting fake-engine clocks. It supplies display and media pipelines.

## Important APIs, types, and functions

The file defines `mm0_cg_regs`, `mm1_cg_regs`, `GATE_MM0()`, `GATE_MM1()`, `mm_clks[]`, and `mm_desc`. Binding is via platform device id `"clk-mt6797-mm"` and generic `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()`.

## Control flow, state, and persistence

MM0 gates use offsets `0x104/0x108/0x100`; MM1 gates use `0x114/0x118/0x110`. The platform-device probe registers the descriptor from `driver_data` and creates the clock provider. Gates are normal set/clear. State persists in hardware register bits and in CCF registrations.

## Dependencies and integration points

Dependencies are MT6797 clock bindings plus MediaTek gate/platform helpers. Parent clocks include `mm_sel`, `dpi0_sel`, `mjc_sel`, and `clk26m`. Consumers include DRM display, MDP, DSI/DPI, SMI/LARB, and multimedia runtime-PM users.

## Risks and test signals

Risks include platform-device binding mismatch, display gate shifts, and missing LARB/MJC clocks for memory transactions. Test with display scanout, DSI/DPI interfaces, MDP operations, and suspend/resume.
