# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_drv.c

## Purpose

`radeon_drv.c` is the Linux module, PCI, DRM driver, IOCTL, and power-management entry point for the Radeon KMS driver. It declares module parameters, exposes supported PCI IDs, selects whether Radeon or AMDGPU should bind SI/CIK devices, probes PCI devices, wraps DRM IOCTLs with runtime PM, and registers the `drm_driver` and `pci_driver`.

## Important APIs, Types, and Functions

- Global module parameters such as `radeon_modeset`, `radeon_gart_size`, `radeon_dpm`, `radeon_runtime_pm`, `radeon_use_pflipirq`, `radeon_si_support`, and `radeon_cik_support` configure broad driver behavior.
- `radeon_support_enabled()` arbitrates SI/CIK ownership against AMDGPU support and module parameters.
- `radeon_pci_probe()` removes conflicting apertures, allocates `struct radeon_device` embedded in DRM, enables PCI, loads KMS, registers DRM, and starts generic DRM client setup.
- PM callbacks `radeon_pmops_*()` route system sleep, hibernation, runtime suspend/resume/idle, and PX power transitions to `radeon_suspend_kms()` and `radeon_resume_kms()`.
- `radeon_drm_ioctl()` obtains a runtime PM reference around `drm_ioctl()`.
- `radeon_ioctls_kms[]`, `radeon_driver_kms_fops`, and `kms_driver` define the KMS ABI surface.
- `radeon_module_init()` and `radeon_module_exit()` register/unregister the PCI driver and ATPX handler.

## Control Flow

Module init disables binding when firmware-only drivers are requested and modeset was not forced, then registers ATPX and the PCI driver. PCI probe rejects disabled ASIC families or switcheroo-deferred devices, removes firmware framebuffer apertures, allocates the DRM/Radeon device, enables PCI, installs driver data, calls `radeon_driver_load_kms()`, registers the DRM device, and creates initial DRM clients with a conservative fb format for very small VRAM devices.

IOCTL calls enter `radeon_drm_ioctl()` from file ops, take a runtime-PM reference, dispatch through DRM's IOCTL table, and drop the reference. Runtime suspend only allows PX devices, disables polling, suspends KMS without client notification, saves/disables PCI, and powers down via ATPX or PCI D-state; runtime resume reverses that and calls `radeon_resume_kms()`.

## State and Persistence Behavior

Module parameters are global mutable configuration consumed throughout the driver. PCI probe persists `struct drm_device` in PCI drvdata and stores `struct radeon_device` as `dev_private`. Runtime PM state is represented in DRM `switch_power_state`, PCI power state, and autosuspend state.

## Dependencies and Integration Points

The file integrates Linux module/PIC infrastructure, DRM core, DRM GEM mmap/read/poll/open/release helpers, aperture removal, fb client setup, VGA switcheroo, runtime PM, MMU notifier synchronization, and all KMS/GEM/CS/info IOCTL implementations in other Radeon files.

## Risks and Edge Cases

- Many module parameters are read globally without local locking; they are mostly immutable after load but permissions vary.
- Runtime suspend refuses non-PX devices and active CRTCs, so display state drives power behavior.
- Probe error path disables PCI but relies on devm/DRM unload behavior for already-initialized driver state.
- Legacy non-KMS IOCTL numbers remain in the table as `drm_invalid_op`; ABI numbering must not be disturbed.

## Test Signals

Test PCI binding and rejection for SI/CIK with AMDGPU options, module parameter parsing via sysfs/modprobe, runtime PM on PX systems, IOCTLs waking suspended devices, compat IOCTL routing, probe failure cleanup, DRM client setup on low-VRAM boards, and module unload after open/render-node use.
