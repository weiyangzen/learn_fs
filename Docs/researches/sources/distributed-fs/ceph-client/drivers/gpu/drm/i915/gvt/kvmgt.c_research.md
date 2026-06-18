# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/kvmgt.c

## Purpose
`kvmgt.c` is the KVM/VFIO mediated-device backend for Intel GVT-g. It exposes vGPUs as VFIO PCI-like devices, routes userspace accesses to GVT emulation, manages opregion and EDID regions, registers KVM page tracking, pins and DMA-maps guest pages, owns the GVT service thread, and registers module-level GVT ops.

## Important APIs, Types, And Functions
Private types include `vfio_region`, `vfio_edid_region`, `kvmgt_pgfn`, and `gvt_dma`. Device ops are `intel_vgpu_dev_ops`; mdev ops are `intel_vgpu_mdev_driver`; GVT core ops are `intel_gvt_vgpu_ops`. Important functions include vGPU probe/remove/init/open/close/read/write/mmap/ioctl, region-info handling, `intel_gvt_set_opregion`, `intel_gvt_set_edid`, page-track add/remove, DMA map/pin/unmap, GVT device init/clean/resume, and module init/exit.

## Control Flow
Module load installs GVT ops and registers the mdev driver. GVT init allocates `intel_gvt`, initializes MMIO, engine MMIO context, firmware, IRQs, GTT, workload scheduler, policy, parser, service thread, types, idle vGPU, debugfs, and mdev parent. VFIO probe allocates the device; `.init` creates the vGPU; `.open_device` registers KVM page tracking and activates it; `.close_device` releases GVT state, unregisters page tracking, destroys caches, and drops MSI eventfd.

VFIO reads/writes decode region indices: config space goes to config emulation, BAR0 to MMIO emulation, BAR2 to aperture IO mapping, and custom regions to opregion/EDID ops. `mmap` supports only shared BAR2 aperture mappings. `ioctl` handles VFIO info, region/IRQ setup, reset, plane query, and dmabuf retrieval.

## State And Persistence
State includes VFIO device fields, region array, MSI eventfd, protected-GFN hash, DMA rbtrees keyed by GFN/DMA address, cache entry refcounts, debugfs counters, KVM page-track notifier, service thread/waitqueue/request bits, vGPU IDR, type definitions, idle vGPU, and mdev parent. DMA cache entries pin guest pages and must be released on VFIO DMA unmap, explicit unmap, close, or teardown.

## Dependencies And Integration Points
The file bridges VFIO, mdev, KVM page tracking, eventfd, DMA mapping, debugfs, i915/GVT core, GTT, display/dmabuf helpers, config/MMIO emulation, scheduler, and service requests.

## Risks
Guest memory mapping is high risk: partial pin unwind, contiguous PFN assumptions, DMA refcount balance, stale page protection, and close/unmap ordering can leak or corrupt mappings. VFIO region arithmetic and sparse mmap caps must match ABI expectations. `intel_gvt_init_device` has long, order-sensitive error unwinding.

## Test Signals
Test mdev type listing/availability, vGPU create/open/close without cache leaks, VFIO config/BAR0/BAR2 access, aperture mmap bounds, MSI eventfd delivery, EDID hotplug, opregion reads, page-track callbacks, DMA refcount balance, service-thread vblank/scheduling, suspend/resume restore, and module unload.
