# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gpu.h

`panthor_gpu.h` exposes Panthor GPU block lifecycle, power, cache, reset, and power-change tracing hooks.

It declares `panthor_gpu_init()`, `panthor_gpu_unplug()`, `panthor_gpu_suspend()`, `panthor_gpu_resume()`, generic block power on/off helpers, L2 power helpers, `panthor_gpu_flush_caches()`, `panthor_gpu_soft_reset()`, and `panthor_gpu_power_changed_on/off()`. Macros `panthor_gpu_power_on()` and `panthor_gpu_power_off()` expand a block type into the corresponding `<type>_PWRON`, `<type>_PWRTRANS`, `<type>_READY`, and `<type>_PWROFF` registers.

The header has no standalone runtime flow. Device, firmware, power, and hardware-dispatch code call these APIs; `panthor_hw.c` binds architecture v10-v13 operation pointers to the implementation.

No state is owned by the header. Calls manipulate `ptdev->gpu`, IRQ state, and persistent hardware registers. Dependencies are light: only Linux types and `struct panthor_device` forward declaration. Risks are macro misuse with a block type lacking the expected register names and assuming power behavior is identical across architectures. Test signals include compilation of macro users, L2 power through HW ops, reset paths on v10-v13, and cache flushes during VM updates.
