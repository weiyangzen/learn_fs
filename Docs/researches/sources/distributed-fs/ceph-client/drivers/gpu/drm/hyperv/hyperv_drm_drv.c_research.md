# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_drv.c

Purpose: bus-facing top-level Hyper-V synthetic video DRM driver. It registers a PCI stub and VMBus driver, negotiates with the host, allocates/maps VRAM, initializes modeset, registers DRM, and handles remove, shutdown, suspend, and resume.

Important APIs/functions: `hyperv_vmbus_probe()` allocates `hyperv_drm_device`, connects VSP, removes conflicting apertures, sets up VRAM, sends VRAM location, initializes KMS, registers DRM, and starts clients. `hyperv_setup_vram()` allocates Hyper-V MMIO and maps it cacheable. Suspend/resume close/reopen VMBus and refresh VRAM location.

Control flow: module init refuses firmware-only DRM mode, registers the PCI stub, then the VMBus driver. Probe negotiates protocol before allocating VRAM because host-reported MMIO size is needed. Remove unplugs DRM, shuts down atomics, closes VMBus, clears drvdata, unmaps VRAM, and frees MMIO.

State and persistence: driver state is in `hyperv_drm_device`; VRAM is guest physical MMIO allocated from VMBus and mapped cacheable. Protocol state is runtime-only and renegotiated on resume.

Dependencies and integration points: depends on Hyper-V VMBus, PCI IDs for gen1 stub, aperture helpers, DRM shmem/fbdev helpers, and Hyper-V protocol/modeset files.

Risks: `hyperv_pci_probe()` is a no-op by design but still claims PCI ID as a stub. Failure to update VRAM location is nonfatal at probe but fatal on resume. Resource cleanup must match allocation state carefully. Cacheable VRAM mapping is required for ARM64 VM display behavior.

Test signals: boot in Hyper-V gen1/gen2 VMs, VMBus negotiation, DRM device registration, framebuffer console, suspend/resume, remove/unplug, and MMIO allocation failure injection.
