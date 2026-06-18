# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_drv.c

Purpose: This is the QXL PCI DRM driver entry point. It matches QXL PCI devices, manages probe/remove/shutdown and power-management transitions, registers DRM ioctls, and defines the `struct drm_driver`.

Important APIs, types, and functions: `qxl_pci_probe()`, `qxl_pci_remove()`, `qxl_pci_shutdown()`, `qxl_drm_release()`, suspend/resume/freeze/thaw/restore helpers, `qxl_ioctls[]`, `qxl_driver`, and `qxl_pci_driver`. Module parameters include `modeset` and `num_heads`.

Control flow: Probe rejects devices older than revision 4, allocates `struct qxl_device` with `devm_drm_dev_alloc()`, enables PCI, removes conflicting apertures, grabs legacy VGA I/O for old VGA revisions, initializes the QXL device, initializes modeset, starts polling, registers DRM, and starts DRM clients. Remove unregisters DRM, shuts down atomic state, stops polling, and releases VGA resources; final device cleanup happens through the DRM `.release` callback. PM freeze suspends mode config, destroys monitor object, evicts surfaces/VRAM, waits command/release rings idle, and saves PCI state; resume resets or reinitializes device state and recreates monitors.

State and persistence: Driver-level persistent state includes PCI drvdata, module parameters, DRM registered state, VGA arbitration ownership, and QXL device allocations. On suspend, host-visible surfaces and VRAM are evicted and monitor state is rebuilt rather than persisted.

Dependencies and integration points: Integrates Linux PCI, VGA arbitration, aperture helpers, DRM module helpers, atomic suspend/resume helpers, fbdev TTM ops, PRIME import hooks, QXL KMS/device/object/ioctl code, and PM core.

Risks: Cleanup ordering is explicitly noted as non-trivial: `qxl_device_fini()` is in `.release`, not `pci_remove()`. Busy waits for command ring idle can spin if the host stops consuming commands. Revision checks and VGA legacy I/O handling are critical for older virtual devices.

Test signals: PCI probe/remove cycles, module unload, suspend/resume/hibernate, revision 3 rejection, VGA and display-other class devices, all DRM ioctls, fbdev client setup, and QEMU/SPICE smoke tests.
