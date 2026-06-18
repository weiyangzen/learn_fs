# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkcif/rkcif-dev.c

Purpose: platform driver for the Rockchip CIF/VIP/VICAP device. It owns compatible matching, resource acquisition, media/v4l2 device registration, async sensor binding, top-level IRQ dispatch, runtime PM, and entity registration/unregistration.

Important APIs/types/functions: defines PX30 and RK3568 clock lists and `struct rkcif_match_data`, OF match table for `"rockchip,px30-vip"` and `"rockchip,rk3568-vicap"`, `rkcif_probe()`, `rkcif_remove()`, runtime PM callbacks, notifier callbacks, and shared `rkcif_isr()`. `rkcif_register()` calls DVP then MIPI registration; `rkcif_unregister()` unwinds in reverse.

Control flow: probe allocates `struct rkcif_device`, matches SoC data, maps registers, requests a shared IRQ, gets clocks, reset, optional GRF regmap, enables runtime PM, initializes media/v4l2 devices, initializes async notifier, registers DVP/MIPI entities, then registers the notifier. When a remote subdev binds, `rkcif_notifier_bound()` creates fwnode links to the interface sink pad; notifier completion registers subdev nodes. The IRQ handler calls DVP and MIPI ISRs and returns handled if either consumed the interrupt. Runtime resume enables clocks; runtime suspend resets the CIF block and disables clocks.

State and persistence: state lives in `struct rkcif_device`, including match data, clock/reset handles, base address, optional GRF, interface array, media device, v4l2 device, and notifier. Runtime PM state is kernel-managed; no disk persistence.

Dependencies/integration: integrates with platform resources, DT/fwnode graph, syscon GRF, reset controller, clk bulk API, runtime PM, V4L2 async notifier, media controller, DVP/MIPI modules, and shared stream/interface abstractions.

Risks: `devm_request_irq()` uses `IRQF_SHARED` and passes `dev` as context; both DVP and MIPI sub-ISRs must ignore unrelated interrupts. Runtime suspend performs a reset because it cannot reset on resume without disrupting IOMMU; this makes suspend/resume ordering important for active DMA users. If DVP/MIPI registration returns `-ENODEV`, the platform keeps probing, so DT endpoints determine which interfaces appear. Cleanup order must match registration because async notifier and media entities retain graph references.

Test signals: platform probe/remove on both compatibles, failure injection at media/v4l2/notifier/entity registration points, runtime PM suspend/resume under active and idle states, shared IRQ behavior when only DVP or MIPI is present, and async sensor link creation from DT endpoints.
