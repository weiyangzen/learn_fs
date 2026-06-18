# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_kms.c

## Purpose
Provides common KMS/display initialization and lifecycle glue for MSM display backends. It wires DRM mode config, IRQ installation, vblank enable/disable work, display IOMMU VM creation, suspend/resume helpers, shutdown, and post-init client/poll setup.

## Important APIs, Types, and Functions
- `msm_drm_kms_init()` is the main KMS initialization path.
- `msm_drm_kms_uninit()`, `msm_drm_kms_unregister()`, `msm_drm_kms_post_init()`, and `msm_kms_shutdown()` handle teardown, unregister shutdown, polling, client setup, and platform shutdown.
- `msm_crtc_enable_vblank()` and `msm_crtc_disable_vblank()` queue ordered work to backend vblank hooks.
- `msm_kms_init_vm()` creates a kernel-managed display GPUVM using the MDP or MDSS IOMMU device.
- `msm_kms_pm_prepare()` and `msm_kms_pm_complete()` wrap DRM mode config suspend/resume.
- Static IRQ helpers call backend `msm_kms_funcs` hooks.

## Control Flow
Initialization removes conflicting firmware framebuffers, initializes display snapshot support, calls the backend `priv->kms_init()`, sets DRM mode config callbacks, runs backend hardware init, moves panel connectors, creates per-CRTC FIFO event workers, initializes vblank, installs IRQ under runtime PM, and resets mode config. Vblank control is deferred through the ordered KMS workqueue so enable/disable happens in process context. Uninit flushes that workqueue before uninstalling IRQs, destroys event workers, finalizes polling/snapshots, uninstalls IRQ under runtime PM, and calls backend destroy.

## State and Persistence
State lives in `priv->kms` and `struct drm_device`: mode_config callbacks, IRQ requested flag, KMS workqueue, event threads, display snapshot state, and optional display VM. State is in-memory and device-lifetime scoped.

## Dependencies and Integration Points
Depends on DRM mode config, atomic helpers, vblank helpers, client setup, aperture removal, MSM display snapshot, MSM GEM VM/MMU, backend `msm_kms_funcs`, runtime PM, and kthread workers. It integrates with IOMMU fault handling by capturing a display snapshot once per attach on display faults.

## Risks
Risks include vblank work racing IRQ uninstall, event-thread teardown ordering, runtime PM imbalance around IRQ install/uninstall, missing IOMMU devices for display VM, and backend hook assumptions. The code flushes the workqueue before IRQ uninstall and rate-limits fault snapshots with `fault_snapshot_capture`.

## Test Signals
Signals include successful DRM registration, vblank enable/disable on each CRTC, IRQ install/uninstall, suspend/resume via mode_config helper, display IOMMU fault snapshot capture, clean shutdown after registration, and no workqueue activity after uninit.
