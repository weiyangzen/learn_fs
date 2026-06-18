# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/plane.c

Purpose: common Tegra DRM plane state, framebuffer pinning, format conversion, memory-bandwidth estimation, legacy blending/transparency state, and interconnect setup.

Important APIs/functions: `tegra_plane_funcs` provides atomic plane operation hooks. Reset/duplicate/destroy manage `struct tegra_plane_state`, including IOVA/map arrays and bandwidth fields. `tegra_plane_prepare_fb()` calls DRM GEM prepare then pins framebuffer BOs to DC-visible IOVAs; cleanup unpins. `tegra_plane_state_add()` performs DRM plane clipping/visibility checks, calculates bandwidth, and marks the DC state plane update bit. `tegra_plane_format()` maps DRM FourCC formats to Tegra window color-depth values and byte-swap modes. `tegra_plane_format_is_yuv()` and indexed helpers classify hardware formats. Legacy helpers emulate opaque formats and update sibling blending state. `tegra_plane_interconnect_init()` obtains memory ICC paths.

Control flow and state: plane atomic state stores mappings for up to three planes, tiling/format/swap, reflect flags, legacy blending, opacity, and bandwidth. Pinning selects `map->phys` for non-group display paths requiring contiguous memory or BO IOVA for grouped/shared-domain paths.

Dependencies/integration: integrates DRM atomic/GEM helpers, host1x BO pinning, Tegra framebuffer/BO helpers, DC state, interconnect framework, and hardware color-depth constants from DC headers.

Risks: framebuffer cleanup assumes `state->crtc` still identifies a DC. Bandwidth is an estimate and intentionally ignores some layout effects except tiled x2. Legacy transparency forces sibling planes into the atomic state when zpos/opacity changes. Multi-plane YUV pitch constraints are enforced by callers such as hub.

Test signals: atomic plane updates/disables, mmap/imported BO scanout, fragmented BO rejection without IOMMU group, all supported FourCC mappings, zpos/alpha changes, ICC path acquisition, and bandwidth votes.
