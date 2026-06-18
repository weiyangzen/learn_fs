# sources/distributed-fs/ceph-client/drivers/gpu/drm/adp/Kconfig

Purpose: enables the Apple Display Pipe DRM driver for pre-DCP Apple display controllers, primarily Apple Arm touchbar hardware.

Important APIs/types/functions: defines `DRM_ADP` as a tristate depending on `DRM`, `OF`, `ARM64`, and `ARCH_APPLE || COMPILE_TEST`; selects KMS, bridge connector, display helper, KMS DMA, GEM DMA, panel bridge, videomode helpers, and MIPI DSI.

Control flow: selecting `DRM_ADP` builds both the main ADP DRM platform driver and the MIPI DSI host companion.

State/persistence: config selection only.

Dependencies/integration: integrates ADP with DRM/KMS helpers, DRM bridges/connectors, DMA-backed GEM, panel bridge, OF graph, and MIPI DSI.

Risks: missing helper selects break build/runtime bridge attachment; platform dependency must allow compile testing without exposing unsupported real platforms.

Test signals: `DRM_ADP=y/m` builds on `ARCH_APPLE` and `COMPILE_TEST`, with both ADP objects produced.
