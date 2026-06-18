# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/vic.c

## Purpose

`vic.c` implements the Tegra Video Image Compositor host1x client and platform driver. It initializes the VIC Falcon firmware engine, registers VIC as a Tegra DRM render client, manages channel/syncpoint/IOMMU/runtime PM state, loads SoC-specific firmware, boots the Falcon, configures stream IDs and clock gating, and exposes submit/memory-context capability callbacks to the Tegra DRM UAPI.

## Important APIs, Types, and Functions

- `struct vic_config` describes firmware filename, client version, and stream-ID support per SoC.
- `struct vic` embeds `struct falcon`, Tegra DRM client state, host1x channel, clock/reset/MMIO resources, firmware capability state, and SoC config.
- `vic_boot()` programs stream IDs and clock gating, boots Falcon firmware, handles old firmware FCE microcode setup, and waits for idle.
- `vic_init()` attaches IOMMU, requests channel and syncpoint, registers the Tegra DRM client, and inherits DMA parameters from host1x.
- `vic_exit()` unregisters the client, forces runtime suspend, releases syncpoint/channel/IOMMU, and frees firmware memory according to whether a shared IOMMU group was used.
- `vic_load_firmware()` reads, allocates, maps, loads, and classifies firmware; it also decides whether memory-context isolation is usable.
- `vic_runtime_resume()` and `vic_runtime_suspend()` gate clock/reset and boot/stop the engine.
- `vic_open_channel()`, `vic_close_channel()`, and `vic_can_use_memory_ctx()` are client operation helpers.
- `vic_probe()` and `vic_remove()` are platform-driver hooks.

## Control Flow

Probe coerces the DMA mask from the host1x parent, allocates `struct vic`, obtains SoC config, allocates syncpoint storage, maps MMIO, gets and maxes the clock, obtains reset when no PM domain owns it, initializes Falcon state, fills host1x and Tegra DRM client descriptors, registers the host1x client, and enables autosuspended runtime PM.

When the host1x client initializes, VIC attaches to the IOMMU, requests a host1x channel and syncpoint, registers with Tegra DRM so userspace can open channels by class, and borrows DMA parameters from host1x. Runtime resume enables the clock, deasserts reset, loads firmware if not already loaded, and boots the Falcon. Runtime suspend stops the channel, asserts reset, delays, and disables the clock.

Firmware loading is serialized by a static mutex. It reads the SoC firmware blob, allocates firmware memory either with DMA coherent memory or Tegra DRM shared-domain allocation, loads firmware into the Falcon image, maps shared-domain memory for cache maintenance if needed, then inspects the FCE data offset to disable memory contexts for old firmware that accesses FCE through data buffer stream IDs. Booting later writes stream IDs when supported, enables clock gating, boots Falcon, optionally sends FCE method setup for old firmware, and waits idle.

## State and Persistence Behavior

VIC platform state persists in `struct vic`. Firmware memory is allocated once and reused across runtime resumes. `vic->can_use_context` persists after firmware inspection and informs UAPI channel-open/submission behavior. The host1x channel and syncpoint are owned for the registered client lifetime. Runtime PM autosuspend releases engine power after job release through submission code.

Firmware allocation/free differs by IOMMU grouping: non-group clients use `dma_alloc_coherent()`/`dma_free_coherent()`, while grouped clients use `tegra_drm_alloc()`/`tegra_drm_free()` plus `dma_map_single()`/`dma_unmap_single()` for physical cache maintenance.

## Dependencies and Integration Points

This file depends on platform resources, clock/reset/runtime PM, host1x client/channel/syncpoint/IOMMU APIs, Tegra DRM client registration/allocation helpers, Falcon firmware helpers, Tegra stream-ID helpers, device-tree compatible matching, and firmware files under `nvidia/tegra*/`. It exposes `tegra_drm_submit`, stream-ID offset, and memory-context capability through `tegra_drm_client_ops`.

## Risks and Edge Cases

- `vic_load_firmware()` uses one static mutex for all VIC instances, which is simple but serializes firmware loading globally.
- The cleanup path after `dma_map_single()` failure in grouped mode calls `tegra_drm_free()` but does not undo a successful `dma_map_single()` before later failures unless `vic_exit()` runs; the immediate failure path should be reviewed for map/unmap balance.
- Old firmware disables context isolation, reducing process isolation; the warning is once-only and depends on firmware header magic values.
- `vic_exit()` returns early if unregistering the client fails, leaving resources allocated.
- Runtime resume failure unwinds reset/clock but keeps loaded firmware memory for reuse.
- Reset handling differs when a PM domain exists; assumptions about reset ownership must match device-tree and genpd behavior.

## Test Signals

Tests and validation should cover probe failures at each resource, IOMMU attach absence versus error, channel/syncpoint allocation failures, firmware missing/corrupt cases, old versus new FCE firmware offsets, stream-ID programming on SID-capable SoCs, runtime PM resume/suspend cycles, autosuspend after submitted jobs, memory-context capability reporting, and unload/reload memory cleanup for grouped and non-grouped IOMMU cases.
