# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/drm.c

## Purpose
`drm.c` is the top-level Tegra DRM/host1x driver. It registers the host1x DRM driver and all Tegra display/engine platform drivers, allocates and registers the DRM device, wires atomic modesetting, manages per-file contexts, provides legacy/staging render ioctls, submits host1x jobs, manages shared IOMMU/GEM carveout allocation, initializes debugfs, and handles system suspend/resume/shutdown.

## Important APIs, Types, and Functions
The DRM driver object is `tegra_drm_driver`; host1x integration is `host1x_drm_driver`; platform subdrivers are listed in `drivers[]`. Mode configuration uses `tegra_atomic_check()` and `tegra_atomic_commit_tail()`. Client registration exports `tegra_drm_register_client()` and `tegra_drm_unregister_client()`. IOMMU helpers are `host1x_client_iommu_attach()` and `host1x_client_iommu_detach()`. Shared allocation helpers are `tegra_drm_alloc()` and `tegra_drm_free()`.

The main UAPI submit path is `tegra_drm_submit()`, which validates command buffers, relocations, syncpoints, pins host1x jobs, submits them, and returns a fence value. Per-file setup/cleanup is in `tegra_drm_open()` and `tegra_drm_postclose()`.

## Control Flow
Module init first refuses to load when firmware-only DRM drivers are requested, then registers the host1x DRM driver and the Tegra platform drivers. `host1x_drm_probe()` allocates `drm_device` and `tegra_drm`, optionally creates an IOMMU paging domain, initializes mode config and polling, initializes all host1x subdevices, computes display masks and IOMMU carveout/GEM apertures if explicit IOMMU attachment was used, prepares the display hub, initializes VBLANK, resets mode config, removes conflicting firmware framebuffers if CRTCs exist, disables modeset/atomic features if no CRTC exists, registers the DRM device, and starts DRM clients.

Atomic commit uses the display-hub-specific sequence when `tegra->hub` exists: disables, hub commit, plane commit, enables, hardware done, wait for vblanks, cleanup, and post-commit bandwidth handling. Without hub it delegates to `drm_atomic_helper_commit_tail_rpm()`.

`tegra_drm_submit()` copies user command buffer, relocation, and syncpoint arrays; rejects unsupported wait checks and multiple syncpoint increments; allocates a host1x job; validates gather word count, object existence, offset alignment, and object bounds; resolves relocation BO references; obtains the syncpoint; assigns class/register validators; pins and submits the job; stores the resulting fence threshold; drops all GEM references and job references on exit.

## State and Persistence
`struct tegra_drm` persists the DRM pointer, optional IOMMU domain, explicit-IOMMU flag, DRM MM allocator, carveout IOVA domain parameters, client list, pitch alignment, display masks, CRTC count, and display hub pointer. Each open file receives `struct tegra_drm_file` with legacy IDR contexts, xarray contexts, syncpoints, and a mutex. Each render context stores the client, host1x channel, legacy id, new-UAPI mappings, and optional memory context. State is process/device lifetime only.

## Dependencies and Integration Points
The file integrates with DRM core, DRM atomic helpers, fbdev/client setup, PRIME/GEM helpers, host1x bus, Tegra GEM/UAPI code, display hub/DC/output drivers, Linux IOMMU/IOVA/drm_mm, runtime PM on clients, firmware framebuffer aperture removal, debugfs, and all listed Tegra platform subdrivers.

## Risks
The submit path is security-sensitive because it copies user pointers and patches command streams; alignment, bounds, syncpoint, and relocation checks are critical. IOMMU policy is subtle: the driver avoids GART, requires host1x consistency, and may tear down an allocated domain if no client attaches explicitly. Error paths in probe must unwind mode config, hub, IOMMU, iova cache, host1x subdevices, and DRM refs in the right order. The no-CRTC case intentionally clears modeset features, so render-only SoCs depend on that path. Legacy staging ioctls and new UAPI coexist in per-file cleanup.

## Test Signals
Signals include successful module init/unload, DRM registration with and without display CRTCs, correct platform subdriver binding, IOMMU aperture debug logs and debugfs `iova` output, host1x client register/unregister, render job submission with valid and invalid gathers/relocs, GEM tiling/flag ioctls under staging, clean per-file close cleanup, suspend/resume through DRM helpers, and no leaked IOVA/DRM MM ranges after buffer allocation/free.
