# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/mt8173-pm-domains.h

Purpose: MT8173 table for the generic SCPSYS PM-domain implementation, paralleling the older legacy data in `mtk-scpsys.c`.

Important data: domains are `vdec`, `venc`, `isp`, `mm`, `venc_lt`, `audio`, `usb`, `mfg_async`, `mfg_2d`, and `mfg`. It declares infra bus-protection blocks; `mm` and `mfg` have explicit protection masks, `usb` is active-wakeup, and `mfg_async` uses a domain supply.

Control flow: selected by `mediatek,mt8173-power-controller`. DT child `reg` IDs index this array; generic direct control handles regulator, clocks, SPM, SRAM, and bus protection.

State and persistence behavior: table only. The actual state is SPM status registers and optional regulator state.

Dependencies and integration points: depends on `dt-bindings/power/mt8173-power.h`, infra access-controller, and consumer drivers for video, display, USB, audio, ISP, and GPU.

Risks: MT8173 has both legacy `mediatek,mt8173-scpsys` and generic `mediatek,mt8173-power-controller` support in different drivers. DT must use the intended compatible to avoid duplicate or missing providers. GPU supply handling must match regulator naming under the domain node.

Test signals: build with both SCPSYS drivers enabled, boot each compatible path separately, and exercise video/display/GPU/USB runtime PM.
