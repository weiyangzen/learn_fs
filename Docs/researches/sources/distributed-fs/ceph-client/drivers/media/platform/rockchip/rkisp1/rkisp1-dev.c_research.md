# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkisp1/rkisp1-dev.c

Purpose: base platform driver for RKISP1. It owns DT matching, SoC feature data, IRQ setup, clocks/PM domains/gasket resources, media and V4L2 device registration, entity registration/linking, async sensor notifier, runtime PM, top-level IRQ dispatch, and module registration.

Important APIs/types/functions: defines `struct rkisp1_isr_data`, notifier callbacks, runtime PM callbacks, `rkisp1_create_links()`, entity register/unregister helpers, top-level `rkisp1_isr()`, SoC info for PX30, RK3399, and i.MX8MP, clock/PM-domain init helpers, `rkisp1_probe()`, and `rkisp1_remove()`. Feature data controls MIPI CSI2, selfpath, dual crop, main stride, 34-bit DMA, BLS, and companding availability.

Control flow: probe allocates `rkisp1_device`, sets DMA mask based on `DMA_34BIT`, initializes `stream_lock`, maps registers, requests SoC-defined IRQs by name or index, initializes clocks and optional PM domains, gets i.MX8MP gasket regmap/id when needed, enables runtime PM, briefly resumes to read CIF ID, initializes media/v4l2 devices, initializes CSI PHY when supported, registers ISP/resizer/capture/stats/params/CSI entities, creates fixed media links, registers async sensor notifier, and initializes debugfs. The notifier scans DT endpoints, maps port 0 to CSI2 and port 1 to parallel/BT656, adds remote fwnodes, and on bind creates sensor-to-CSI or sensor-to-ISP links. Runtime suspend disables IRQ handling with a memory barrier, synchronizes IRQs, disables clocks, and selects sleep pinctrl; resume selects default pinctrl, enables clocks, and re-enables IRQ handling.

State and persistence: all runtime state is in `struct rkisp1_device`. The async notifier stores sensor endpoint metadata until cleanup. `irqs_enabled` gates shared IRQ handlers across suspend/resume. No filesystem persistence.

Dependencies/integration: platform/OF graph, V4L2 fwnode async notifier, media controller, pinctrl, runtime PM, PM domains, clk bulk, syscon regmap for i.MX8MP, CSI/ISP/resizer/capture/stats/params modules, and optional debugfs. It is the top-level object linked by the Makefile/Kconfig.

Risks: endpoint parsing is strict: port 0 requires MIPI CSI2 feature and port 1 requires PARALLEL or BT656. IRQ dispatch order matters; capture ISR runs before ISP ISR to preserve frame sequence. Shared IRQ lines require each ISR to return `IRQ_NONE` quickly when disabled or status is empty. Error unwind must mirror the multi-entity registration order. i.MX8MP optional `pclk` compatibility and gasket configuration add variant-specific complexity.

Test signals: probe/remove on PX30, RK3399, and i.MX8MP compatibles; DT endpoint variations for MIPI and parallel sensors; runtime suspend/resume with IRQ storms; failure injection for clocks, IRQs, media registration, CSI init, and notifier registration; media graph topology inspection; and streaming with all supported path counts.
