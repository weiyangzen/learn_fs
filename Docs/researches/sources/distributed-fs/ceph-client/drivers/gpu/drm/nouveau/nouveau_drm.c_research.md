
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_drm.c

## Purpose
Provides the main DRM driver entry point for Nouveau. It owns module parameters, PCI/platform device creation, NVIF client/device/MMU setup, global DRM driver callbacks, ioctl dispatch, client lifetime, acceleration channel initialization, suspend/resume/runtime PM, and module registration.

## Important APIs, Types, and Functions
Important externally visible functions include `nouveau_pmops_suspend()`, `nouveau_pmops_resume()`, `nouveau_pmops_runtime()`, `nouveau_drm_ioctl()`, `nouveau_platform_device_create()`, and `nouveau_drm_device_remove()`. Internal lifecycle functions include `nouveau_drm_device_new()`, `nouveau_drm_device_init()`, `nouveau_drm_device_fini()`, `nouveau_drm_device_del()`, `nouveau_drm_probe()`, and `nouveau_drm_remove()`. Client helpers are `nouveau_cli_init()`, `nouveau_cli_fini()`, and `nouveau_cli_work_queue()`. Acceleration setup is split across `nouveau_accel_init()`, `nouveau_accel_fini()`, `nouveau_accel_gr_init()`, and `nouveau_accel_ce_init()`.

## Control Flow
Module init clones a common `driver_stub` into PCI and platform drivers, evaluates `modeset`, initializes debugfs/backlight/DSM hooks, registers optional platform support, then registers the PCI driver. PCI probe verifies switcheroo readiness, creates an NVKM PCI device, removes conflicting framebuffers, allocates the DRM/NVIF device stack, enables PCI, initializes the device stack, and starts DRM client setup. Device initialization creates the shared scheduler workqueue, initializes the root client and client list, sets up VGA, TTM, BIOS, acceleration/fences/channels, display, debugfs, hwmon, SVM, DMEM, LED support, runtime PM, and finally calls `drm_dev_register()`.

Open creates a per-file `nouveau_cli`, initializes NVIF client/device/MMU/VMM and scheduler state, and links it into `drm->clients`. Postclose tears down ABI16, removes the client, and releases VMM/MMU/device/client state. Ioctl dispatch runtime-resumes the device, routes the legacy NVIF ioctl specially, otherwise calls DRM core ioctl handling, then autosuspends. PM suspend stops SVM/DMEM/LED, suspends display, evicts VRAM resources, idles kernel channels, suspends fences and the NVIF object tree, and powers PCI down. Resume reverses the NVIF, fence, VBIOS/display, LED, DMEM, and SVM steps.

## State and Persistence
Driver state is held in `struct nouveau_drm`: NVKM/NVIF objects, root and per-file clients, TTM and GEM accounting, fence backend, channel/runlist metadata, kernel channels, display state, debugfs/hwmon/LED/SVM/DMEM pointers, and audio component state. Module parameters persist for module lifetime and control debug, acceleration, modeset, atomic exposure, and runtime PM policy.

## Dependencies and Integration Points
This file connects Linux DRM core, PCI/platform buses, PM runtime, VGA switcheroo, aperture removal, NVKM/NVIF, TTM, GEM, display, hwmon, LED, SVM/DMEM, debugfs, ABI16, VM_BIND, and EXEC. The DRM ioctl table exposes legacy GEM/pushbuf/SVM ioctls plus VM_BIND and EXEC.

## Risks and Test Signals
Risk is concentrated in init/fini unwinding, runtime PM ordering, hot-unplug behavior, client cleanup while file descriptors remain open, fence/channel backend selection by class, and the D3hot/D3cold bridge quirk. Test signals include probe failure injection at every stage, module unload after open files, runtime autosuspend/resume under ioctl load, system suspend/resume, hibernation freeze/thaw, kexec shutdown, Optimus switcheroo, noaccel/headless modes, and ioctl access through render nodes.
