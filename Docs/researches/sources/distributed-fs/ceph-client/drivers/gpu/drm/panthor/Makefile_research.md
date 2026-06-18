# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/Makefile

`panthor/Makefile` defines the Kbuild composition of the Panthor DRM driver. It links the subsystem objects into `panthor.o` and exposes that object through `obj-$(CONFIG_DRM_PANTHOR)`.

`panthor-y` contains devfreq, device lifecycle, driver/ioctl entry, firmware, GEM, GPU block, heap, hardware matching, MMU, power, and scheduler objects: `panthor_devfreq.o`, `panthor_device.o`, `panthor_drv.o`, `panthor_fw.o`, `panthor_gem.o`, `panthor_gpu.o`, `panthor_heap.o`, `panthor_hw.o`, `panthor_mmu.o`, `panthor_pwr.o`, and `panthor_sched.o`. `CFLAGS_panthor_gpu.o := -I$(src)` provides the local include path needed by the GPU object, notably for trace-related includes.

There is no runtime control flow or state. Build flow compiles each object and links them into a module or built-in driver based on Kconfig. Dependencies are Kbuild, `CONFIG_DRM_PANTHOR`, and the source files listed.

Risks are mostly omission risks: dropping an object can create link failures or missing runtime functionality, and dropping the GPU-specific include flag can break trace include resolution. Test signals are clean module and built-in builds, incremental builds after trace header changes, and ensuring all public symbols used across Panthor subsystems resolve.
