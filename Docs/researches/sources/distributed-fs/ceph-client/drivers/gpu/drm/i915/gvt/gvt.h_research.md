# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/gvt.h

## Purpose
`gvt.h` is the central private header for Intel GVT-g vGPU support. It aggregates subsystem headers, defines core device and vGPU structures, global resource accounting, MMIO metadata, firmware state, submission state, display state, memory aperture helpers, lifecycle APIs, and utility helpers for GPA access and runtime MMIO access.

## Important Types And APIs
Key structs include `intel_gvt_device_info` for platform limits and MMIO/GTT geometry, `intel_vgpu` for each mediated vGPU, `intel_gvt` for device-global state, `intel_vgpu_submission` for per-engine workload/execlist state, `intel_vgpu_display` for EDID/port/SBI state, `intel_vgpu_cfg_space`, `intel_vgpu_irq`, `intel_vgpu_gm`, `intel_gvt_mmio`, and `intel_gvt_firmware`. It declares vGPU lifecycle APIs, resource allocation/reset/free APIs, firmware load/free, opregion/EDID setup, config-space emulation, hotplug, workload scanning, failsafe mode, debugfs hooks, page tracking, and DMA map/unmap helpers.

## Control Flow And State
This header establishes the object graph used by the implementation files in this subset. `intel_gvt` owns global locks, `intel_gt`, IDR of vGPUs, global MMIO/GTT/firmware/IRQ/scheduler state, service thread state, command table, mdev type metadata, and debugfs root. Each `intel_vgpu` owns its VFIO device, locks, status bits, resource slices, virtual config/MMIO, GTT state, display state, submission queues, page tracking, dmabuf state, MSI trigger, and DMA mapping caches. Inline helpers manipulate service requests, PCI BAR config fields, MMIO attribute flags, and guest physical memory reads/writes.

## Dependencies And Integration Points
`gvt.h` includes almost every GVT subsystem header and i915 GT/display/VFIO/KVM page-tracking interfaces. The files in this work item depend heavily on it: `edid.c` uses display and virtual register fields, `execlist.c` uses submission/workload/event state, `fb_decoder.c` uses display/GTT helpers, `firmware.c` uses device info and firmware buffers, and `gtt.c` uses aperture macros, GPA access, runtime PM wrappers, and DMA/page-track declarations.

## Risks And Edge Cases
Because it is a central header, changes have broad compile and ABI impact inside the driver. Several macros perform direct pointer arithmetic into virtual MMIO/config-space buffers and assume valid offsets/alignment. GM aperture/hidden range macros are used for security-sensitive address validation. `intel_gvt_read_gpa()` and `intel_gvt_write_gpa()` require the vGPU to be attached and pass through VFIO DMA operations; callers must handle `-ESRCH` and guest memory faults.

## Test Signals
Compile coverage across all GVT objects is essential after any header change. Runtime signals include correct vGPU creation/destruction, resource accounting, MMIO attribute behavior, guest config reads/writes, GM range validation, GPA read/write failure handling for detached vGPUs, service thread wakeups, and no regressions in EDID, execlist, framebuffer decode, firmware, and GTT paths that consume these definitions.
