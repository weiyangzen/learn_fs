# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/drm.h

## Purpose
`drm.h` is the central internal Tegra DRM header. It defines the top-level `struct tegra_drm`, per-client and per-context render abstractions, the generic output wrapper, framebuffer/helper prototypes, DPAUX helper prototypes, memory allocation helpers, and external platform driver declarations used by module registration.

## Important APIs, Types, and Definitions
`struct tegra_drm` stores global device state: DRM device, optional IOMMU domain, DRM MM and carveout IOVA allocators, client list, display masks, pitch alignment, CRTC count, and display hub pointer. `struct tegra_drm_client` wraps `host1x_client` with list membership, backpointer, shared channel, version, and operation table. `struct tegra_drm_context` stores a client/channel pair plus legacy and new-UAPI context state. `struct tegra_drm_client_ops` defines client-specific channel open/close, class/register validation, submit, stream ID, and memory-context support callbacks.

`struct tegra_output` wraps common output resources: OF node, device, bridge/panel/DDC/EDID/CEC/HPD resources, encoder, and connector. Inline helpers convert DRM encoder/connector and host1x client pointers back to Tegra wrappers.

## Control Flow Role
The header defines cross-file contracts rather than runtime behavior. Render clients register with `tegra_drm_register_client()`, contexts submit through `tegra_drm_submit()` or client-specific no-op fallback, outputs probe/init/exit through `output.c`, DPAUX-backed outputs find/attach/enable AUX, and framebuffer code exposes Tegra BO planes, tiling, allocation, and creation.

## State and Persistence
All types are in-memory lifetime state. `tegra_drm` is DRM-device lifetime. `tegra_drm_client` is platform/host1x-client lifetime. `tegra_drm_context` is file/context lifetime. `tegra_output` is output-device lifetime and stores connector/encoder objects embedded by value.

## Dependencies and Integration Points
The header includes host1x, IOVA, GPIO, DRM atomic/bridge/encoder/fixed/probe helper headers, Tegra UAPI, and local GEM/hub/trace headers. It connects `drm.c`, `dc.c`, `dsi.c`, `dpaux.c`, framebuffer/GEM/output code, and all declared Tegra platform drivers.

## Risks
Because this is the central internal ABI, struct layout or ownership changes can ripple through many drivers. Embedded DRM connector/encoder objects require strict cleanup ordering. `tegra_drm_client_ops` callbacks are optional in some paths but mandatory in others, so missing hooks can lead to `-ENOSYS` or crashes depending on caller assumptions. The local `DRM_FORMAT_MOD_NVIDIA_SECTOR_LAYOUT` definition is marked as a candidate for UAPI relocation, so modifier compatibility must be watched.

## Test Signals
Build coverage across all Tegra DRM objects is the main static signal. Runtime signals include correct output connector/encoder creation, client registration lists, successful context open/close/submit for engines, DPAUX helper linkage, framebuffer creation with expected tiling/modifiers, and module registration resolving all external platform-driver symbols.
