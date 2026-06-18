<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.c

## Purpose
`vs_dc.c` is the platform driver for VeriSilicon DC hardware. It probes resources, sets DMA mask, controls clocks/resets, maps MMIO through regmap, identifies the chip, requests IRQs, initializes DRM, and handles remove/shutdown.

## Important APIs, Types, and Functions
Important items include `vs_dc_regmap_cfg`, OF match table for `verisilicon,dc`, `vs_dc_irq_handler()`, `vs_dc_probe()`, `vs_dc_remove()`, `vs_dc_shutdown()`, and the `module_platform_driver()` registration.

## Control Flow
Probe validates an OF node and downstream port count, enforces `VSDC_MAX_OUTPUTS`, sets a 32-bit coherent DMA mask, allocates `struct vs_dc`, obtains optional shared resets, enables core/AXI/AHB clocks, gets IRQ, deasserts resets, maps MMIO, initializes regmap, reads chip identity, verifies DT port count against hardware display count, fetches per-output pixel clocks, requests IRQ, stores drvdata, and calls `vs_drm_initialize()`. Errors after reset deassert reassert resets. Remove finalizes DRM and asserts resets. Shutdown runs DRM atomic shutdown.

## State and Persistence Behavior
Persistent driver state is `struct vs_dc`: regmap, clocks, resets, DRM device pointer, and chip identity. Hardware reset and clocks persist while the platform device is bound. IRQ state routes through DRM vblank handling.

## Dependencies and Integration Points
The file integrates platform devices, OF graph, reset controller, common clock, DMA API, regmap MMIO, IRQs, chip identity from `vs_hwdb.c`, and DRM setup in `vs_drm.c`.

## Risks
The IRQ handler reads `VSDC_TOP_IRQ_ACK` as status and delegates clearing semantics to hardware/regmap assumptions; if the register is write-to-clear, behavior needs verification. Display-count mismatch between DT and hardware aborts probe. Reset assertion on all late failures is important because clocks are devm-managed. A 32-bit DMA mask constrains framebuffer placement.

## Test Signals
Probe tests should cover no OF node, no ports, too many ports, unsupported identity, missing pix clocks, IRQ failure, reset failure, and DRM init failure. Runtime tests should cover vblank IRQ delivery, shutdown path, and unbind/rebind reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.c -->
