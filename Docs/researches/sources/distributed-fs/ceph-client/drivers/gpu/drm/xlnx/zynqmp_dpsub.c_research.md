# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dpsub.c

## Purpose

`zynqmp_dpsub.c` is the platform-driver lifecycle for the Xilinx ZynqMP DisplayPort Subsystem. It allocates subsystem state, initializes clocks and DT topology, probes DP/display/KMS/audio components, and coordinates teardown, shutdown, and system sleep.

## Important APIs, Types, And Functions

Important helpers are `zynqmp_dpsub_init_clocks()`, `zynqmp_dpsub_parse_dt()`, `zynqmp_dpsub_probe()`, `zynqmp_dpsub_remove()`, `zynqmp_dpsub_shutdown()`, and exported `zynqmp_dpsub_release()`. PM callbacks use DRM mode-config helper suspend/resume.

## Control Flow

Probe allocates `struct zynqmp_dpsub`, sets a 44-bit DMA mask and 32-bit max segment size, initializes reserved memory, enables the APB clock, selects video/audio clocks from PL live or PS fallback sources, parses OF graph ports, enables runtime PM, probes DP first, probes the display controller, registers the DP bridge, initializes DRM/KMS if DMA mode is enabled, initializes optional audio, and reports success. Error paths unwind DRM, bridge, display, DP, PM, clocks, reserved memory, and manual allocation as needed.

## State And Persistence Behavior

Persistent subsystem state includes clock handles/source flags, connected port bitmask, `dma_enabled`, DRM/bridge/disp/layers/dp pointers, DMA alignment, and optional audio state. Runtime PM and APB clock state persist while the driver is bound. In DRM-managed mode, release is tied to DRM device cleanup.

## Dependencies And Integration Points

It depends on platform resources, OF graph, reserved memory, DMA masks, common clocks, PM runtime, DRM bridge/atomic helpers, and local DP/DISP/KMS/audio modules. It matches `xlnx,zynqmp-dpsub-1.7`.

## Risks And Test Signals

Risks include backward-compatible DT behavior without ports, rejecting multiple live inputs, requiring PL clock for live video, unsupported live audio/PL outputs, probe unwind differences before/after DRM allocation, and APB clock lifetime. Test old and new DT topologies, DMA and live modes, missing clocks, reserved-memory presence, probe deferral, module remove, shutdown, and suspend/resume.
