# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_device.c

`panthor_device.c` coordinates Panthor device bring-up, teardown, reset, runtime PM, coherency selection, user MMIO mmap faults, and exception-name decoding.

External APIs are `panthor_device_init()`, `panthor_device_unplug()`, `panthor_device_mmap_io()`, `panthor_device_resume()`, `panthor_device_suspend()`, and `panthor_exception_name()`. Helpers cover coherency probing, clock and power-domain init, reset work, dummy page cleanup, MMIO fault insertion, and resume of power/GPU/MMU/FW components.

Init sets SoC data, PM/reset/unplug state, debugfs GEM list, dummy latest-flush page, reset workqueue, clocks, power domains, devfreq, MMIO mapping, runtime PM, then initializes hardware, power, GPU, coherency, MMU, firmware, scheduler, GEM, autosuspend, and finally registers DRM. Reset work performs scheduler/FW/MMU pre-reset, soft reset, L2 power-on, MMU and FW recovery, then scheduler post-reset or device unplug. Suspend unmaps user MMIO before clocks/power go down; resume restores hardware then unmaps dummy mappings so faults remap real MMIO.

Persistent state includes `struct panthor_device` subsystem pointers, PM state, reset flags, locks, dummy page, clocks, MMIO base, and autosuspend. Dependencies span all Panthor subsystems, platform resources, runtime PM, and DRM registration. Risks are ordering bugs in init/unwind/reset, user MMIO races causing external aborts, reset versus suspend interactions, and concurrent unplug. Tests should cover probe/remove, runtime PM with MMIO mappings, forced resets, FW recovery failure, coherency mismatch, and lockdep.
