## sources/distributed-fs/ceph-client/drivers/w1/masters/sgi_w1.c

Purpose: this platform driver exposes SGI ASIC 1-Wire hardware as a Linux w1 master.

Important APIs/types/functions: `struct sgi_w1_device` stores the memory-mapped control register, `w1_bus_master`, and optional platform `dev_id`. Bus callbacks are `sgi_w1_reset_bus()` and `sgi_w1_touch_bit()`, with polling helper `sgi_w1_wait()`.

Control flow: probe allocates state, maps one MMIO resource, assigns reset/touch callbacks, copies optional platform data `dev_id`, and registers the w1 master. Reset writes a packed pulse/sample command for reset timing, waits for DONE, delays recovery, and returns read data. Touch-bit writes timing values for read/write-one or write-zero, waits for DONE, and delays recovery after read/write-one slots.

State and persistence behavior: no persisted state. The MCR register reflects the active transaction; `dev_id` is copied into driver memory for w1 core identity.

Dependencies and integration points: depends on platform MMIO resources, optional `linux/platform_data/sgi-w1.h`, delay helpers, and w1 core.

Risks: `sgi_w1_wait()` spins without timeout until `MCR_DONE`, so wedged hardware can hang a caller. There is no runtime PM or clock handling despite including clock headers. Timing constants are hardcoded.

Test signals: probe with and without platform data, reset/touch-bit on real ASIC, missing/invalid MMIO resource, remove cleanup, and fault-injection for a never-completing MCR operation.
