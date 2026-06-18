# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_gpu.c

`panthor_gpu.c` manages the base GPU block: IRQ handling, DMA mask setup, coherency/L2 configuration, generic power on/off helpers, L2 power, cache flush commands, soft reset commands, and suspend/resume.

Private `struct panthor_gpu` stores the GPU IRQ wrapper, pending request lock and bitmask, waitqueue, and cache flush mutex. Public functions are `panthor_gpu_init()`, `panthor_gpu_unplug()`, `panthor_gpu_suspend()`, `panthor_gpu_resume()`, `panthor_gpu_power_changed_on/off()`, `panthor_gpu_block_power_on/off()`, `panthor_gpu_l2_power_on/off()`, `panthor_gpu_flush_caches()`, and `panthor_gpu_soft_reset()`. `PANTHOR_IRQ_HANDLER(gpu, ...)` supplies raw/threaded IRQ glue.

Init allocates state, sets DMA segment and coherent masks from probed PA bits, gets the named GPU IRQ, and requests it for fault/reset/cache-clean events. IRQ handling clears status, traces power if enabled, logs faults, clears matching pending request bits, and wakes waiters. Cache flush/reset set pending bits, write `GPU_CMD`, and wait for IRQ completion with timeout rechecks. L2 power-on programs coherency and optional ASN hash before powering L2.

State includes IRQ mask/state, `pending_reqs`, and hardware coherency/L2 settings. Dependencies are Panthor device/HW/registers, tracepoints, platform IRQs, runtime PM guards, DMA API, and exception decoding. Risks are lost wakeups, timeout races, multi-coregroup limitations, and incorrect DMA mask from bad feature probing. Tests should cover GPU faults, cache flush timeout, soft reset, suspend/resume, L2 power, power trace IRQs, and coherent/noncoherent platforms.
