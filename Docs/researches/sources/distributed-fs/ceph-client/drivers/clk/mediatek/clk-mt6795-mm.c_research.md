# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-mm.c

## Purpose

This MT6795 MMSYS driver registers multimedia and display gates. It covers SMI, MDP, display overlays/RDMA/WDMA/color/AAL/gamma/UFOE/split/merge/OD, display PWM, DSI, DPI, and related multimedia clocks.

## Important APIs, types, and functions

The important definitions are `mm0_cg_regs`, `mm1_cg_regs`, `GATE_MM0()`, `GATE_MM1()`, `mm_gates[]`, and `mm_desc`. Unlike most OF-matched files, it binds through a `platform_device_id` table named `"clk-mt6795-mm"` and uses `mtk_clk_pdev_probe()`/`mtk_clk_pdev_remove()`.

## Control flow, state, and persistence

The platform-device probe receives `mm_desc` through `driver_data`, registers the two gate banks, and publishes clocks. MM0 uses offsets `0x104/0x108/0x100`; MM1 uses `0x114/0x118/0x110`. All gates use set/clear semantics. State is hardware gate state and clock-provider registration.

## Dependencies and integration points

Dependencies are MT6795 clock bindings and the MediaTek gate/simple platform helper code. Parent clocks are mainly `mm_sel`, with display pixel paths also using `pwm_sel`, `dsi0_dig`, `dsi1_dig`, and `dpi0_sel`. The file integrates with display, DRM, MDP, SMI/LARB, DSI, DPI, and display PWM consumers.

## Risks and test signals

Risks include shifted display gates causing blank panels, incorrect platform-device binding, and parent mismatch with topckgen. Test with DRM modeset, MDP pipeline use, SMI/LARB activity, DSI/DPI panels, and suspend/resume clock gating.
