# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_drv.h

Purpose: shared private header for the HIBMC DRM driver. It defines the driver-private object graph, VGA DDC state, conversion helpers, init hooks, and power/IRQ/debugfs declarations.

Important APIs/types: `struct hibmc_vdac` embeds the VGA encoder, connector, I2C adapter, and bit-bang data. `struct hibmc_drm_private` embeds MMIO pointer, DRM device, primary plane, CRTC, VDAC, and DP. Container helpers convert connectors/devices to private structs. Function declarations connect DE, VDAC, DDC, DP, debugfs, power mode/gate, and HPD ISR modules.

Control flow: included by all HIBMC C files to share private layout and cross-module APIs. Probe allocates `struct hibmc_drm_private` around `struct drm_device`; downstream modules fill the embedded subobjects during KMS init.

State and persistence: defines the in-memory runtime state for the whole HIBMC driver. It does not store persistent configuration beyond what each embedded object holds.

Dependencies and integration points: depends on Linux GPIO/I2C bit-bang headers, DRM framebuffer types, and DP public hardware header. Integrates PCI driver, display engine, VDAC, I2C, DP, and debugfs files.

Risks: embedded DRM objects require stable lifetime and cleanup order. Adding connectors or CRTCs requires updating clone masks and mode config assumptions. Container helpers assume the passed objects are exactly the embedded HIBMC instances.

Test signals: compile coverage, KMS init/cleanup, connector-to-private conversions in EDID/HPD paths, and module unload validate this shared contract.
