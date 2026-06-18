# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_drv.c

## Purpose

`vbox_drv.c` is the VirtualBox DRM PCI driver entry point. It probes the VirtualBox graphics PCI device, allocates the DRM device, initializes hardware, VRAM, modesetting, IRQs, registers the DRM device, and implements suspend/resume hooks.

## Important APIs, Types, and Functions

- `vbox_pci_probe`, `vbox_pci_remove`, and `vbox_pci_shutdown`: PCI lifecycle handlers.
- `vbox_pm_suspend`, `vbox_pm_resume`, `vbox_pm_freeze`, `vbox_pm_thaw`, and `vbox_pm_poweroff`: DRM mode-config and PCI power management paths.
- `pciidlist`: matches vendor/device `0x80ee:0xbeef`.
- `driver`: `struct drm_driver` enabling modeset, GEM, atomic, cursor hotspot, GEM VRAM, and fbdev TTM helpers.
- `drm_module_pci_driver_if_modeset`: module registration controlled by the `modeset` parameter.

## Control Flow

Probe first verifies HGSMI support with `vbox_check_supported`, removes conflicting apertures, allocates `struct vbox_private` as a managed DRM device, enables PCI, then calls `vbox_hw_init`, `vbox_mm_init`, `vbox_mode_init`, and `vbox_irq_init`. After successful `drm_dev_register`, it starts generic DRM clients. Failure unwinds IRQ, mode, and hardware setup in reverse order. Remove unregisters DRM, performs atomic shutdown, and finalizes IRQ, mode, and hardware state.

## State and Persistence Behavior

`struct vbox_private` persists as the DRM device private object for the PCI device lifetime. It carries mapped VRAM/guest heap pointers, mode state, work items, locks, and protocol buffers initialized by other files. Suspend saves PCI state and moves to D3hot after DRM helper suspend; resume reenables PCI and restores DRM mode configuration.

## Dependencies and Integration Points

The file depends on PCI, aperture conflict removal, DRM managed allocation, atomic helpers, fbdev/TTM helpers, and internal setup functions from `vbox_main.c`, `vbox_ttm.c`, `vbox_mode.c`, and `vbox_irq.c`.

## Risks and Edge Cases

- `vbox_hw_init` returning `-ENOTSUPP` for missing host mode hints prevents binding to older hosts.
- Resume does not re-run `vbox_hw_init`; it relies on mapped resources and host state surviving PCI power transitions well enough for DRM helper resume.
- Failure paths share `err_hw_fini` for memory-manager and mode-init failures; `vbox_hw_fini` must tolerate partially initialized acceleration state.

## Test Signals

Probe/remove in VirtualBox VMs, suspend/resume, hibernate freeze/thaw, modeset module parameter behavior, fbdev setup, conflicting framebuffer removal, and bind failure on unsupported VBE/HGSMI IDs.
