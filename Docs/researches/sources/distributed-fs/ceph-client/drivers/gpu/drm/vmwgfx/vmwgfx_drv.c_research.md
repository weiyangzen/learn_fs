# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_drv.c

## Purpose
This is the vmwgfx DRM driver's module, PCI, device-lifecycle, ioctl-dispatch, power-management, and top-level initialization implementation. It binds VMware SVGA2/SVGA3 PCI devices to a DRM driver, discovers hardware capabilities, initializes memory/resource/fence/KMS subsystems, registers the DRM device, and tears everything down in reverse order.

## Important APIs, types, and functions
- The `DRM_IOCTL_VMW_*` macros and `vmw_ioctls[]` table define vmwgfx private ioctl encodings, handlers, and permissions.
- Module parameters `restrict_iommu`, `force_coherent`, `restrict_dma_mask`, and `assume_16bpp` alter DMA mapping, DMA mask, and mode-filter behavior.
- `vmw_probe()` is the PCI probe entry: removes conflicting apertures, enables PCI, allocates `struct vmw_private`, loads the driver, registers DRM, enables SVGA, starts generic clients, and initializes debugfs.
- `vmw_driver_load()` is the main initialization sequence for locks, PCI resources, SVGA version/caps, DMA mode, memory limits, TTM, devcaps, GMR/MOB managers, KMS, overlay, FIFO/device request, shader model, host reporting, and PM notifier.
- `vmw_driver_unload()` performs the reverse teardown: notifier removal, software context cleanup, FIFO resource accounting, SVGA disable, KMS/overlay cleanup, memory managers, devcaps, TTM, FIFO/device release, fence manager, IRQs, object device, IDRs, and mksstat cleanup.
- `vmw_request_device()`, `vmw_request_device_late()`, `vmw_release_device_early()`, and `vmw_release_device_late()` manage SVGA enable/config/FIFO, command buffer manager, MOB object tables, dummy query BO, and fence FIFO state.
- `vmw_svga_enable()` and `vmw_svga_disable()` expose top-level SVGA/VRAM manager state changes.
- `vmw_generic_ioctl()` wraps DRM ioctl dispatch to add vmwgfx-specific encoding checks and special permission handling for EXECBUF and UPDATE_LAYOUT.
- `vmw_pm_freeze()` and `vmw_pm_restore()` implement hibernation freeze/restore by suspending KMS, evicting resources, draining FIFO resources, disabling SVGA, then rebuilding the device.

## Control flow
PCI registration is installed by `drm_module_pci_driver(vmw_pci_driver)`. On probe, `vmw_setup_pci_resources()` maps either SVGA3 register MMIO plus VRAM BARs or SVGA2 I/O ports, VRAM, and FIFO memory. `vmw_detect_version()` writes and reads `SVGA_REG_ID` to confirm SVGA2/SVGA3 compatibility. `vmw_driver_load()` then initializes all per-device locks and resource IDR/LRU lists, reads capability bitmaps, warns on unsupported hypervisors, configures virtual KMS support, chooses DMA mapping mode, reads VRAM/FIFO/display/GMR/MOB limits, installs DMA masks and IRQs, initializes TTM and VRAM managers, snapshots devcaps, creates GMR/MOB/system managers when supported, derives shader model support from caps/devcaps, initializes KMS and overlay, requests the SVGA device/FIFO, and registers PM notifications.

After successful load, `vmw_probe()` registers the DRM device, increments FIFO resource use, enables SVGA/VRAM, starts DRM clients, and creates debugfs nodes. Remove unregisters DRM and calls `vmw_driver_unload()`. Error paths in `vmw_driver_load()` are carefully labeled to unwind only initialized subsystems.

Power management has two levels. Simple suspend/resume saves PCI state and toggles device power. Hibernation freeze suspends KMS, releases pinned execbuf BOs, evicts resources, tears down early device state, swaps out TTM BOs, refuses hibernation if FIFO resources remain, disables SVGA, and performs late device release. Restore re-detects SVGA, increments FIFO resource accounting, requests the device again, enables SVGA, restarts fencing, clears suspend state, and resumes KMS when needed.

## State and persistence behavior
`struct vmw_private` is allocated as the DRM device's private object and persists for the PCI device lifetime. This file initializes most global fields: PCI identity and BAR mappings, capability bitmaps, memory limits, display limits, shader model, feature booleans (`has_gmr`, `has_mob`), locks, wait queues, TTM device, object device, fence manager, command buffer manager, FIFO state, devcap cache, KMS/overlay state, PM notifier, and resource IDRs/LRUs. SVGA register state (`enable_state`, `config_done_state`, `traces_state`) is saved before device init and restored on final release.

## Dependencies and integration points
The file integrates Linux PCI, DMA, PM notifier, aperture, module parameter, and device power APIs with DRM core, DRM GEM/TTM helpers, TTM range/resource managers, vmwgfx BO/resource/fence/FIFO/KMS/overlay/devcaps/cmdbuf/mksstat subsystems, and generated kernel version metadata. User-visible integration comes through DRM driver features, file operations, private ioctls, PRIME import/export, fbdev client setup, debugfs, and module metadata.

## Risks and edge cases
- Initialization order is dense and error-path correctness is critical. A misplaced goto can leak IRQs, TTM managers, devcaps, IDRs, or leave FIFO/SVGA state enabled.
- `vmw_device_fini()` busy-waits on `SVGA_REG_BUSY` after writing `SVGA_REG_SYNC`; a stuck device would hang this path.
- `vmw_svga_disable()` intentionally documents a possible race with new modesets because KMS lost-device notification cannot be called under an SVGA lock without lock-order problems.
- DMA mode selection is policy-driven by module parameters and memory encryption. Misconfiguration can disable GMR/MOB/3D paths or force constrained DMA masks.
- Capability-derived shader model state depends on devcap availability. If `vmw_devcaps_create()` succeeds with unexpected zero values, higher shader models are silently disabled.
- `vmw_generic_ioctl()` bypasses extra checks for EXECBUF and overrides UPDATE_LAYOUT permission checks; ioctl table and UAPI encoding changes need regression coverage.

## Test signals
Key signals include successful probe/remove on SVGA2 and SVGA3, expected capability and memory-limit logs, TTM manager debugfs entries matching `has_gmr`/`has_mob`, private ioctl permission behavior for render/master/admin clients, working KMS/fbdev startup, 3D context creation at the selected shader model, hibernation refusal when FIFO resources remain active, hibernation restore with KMS resume, and clean unload with no pinned BO assertion.
