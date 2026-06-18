# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu.c

## Purpose
Platform driver for Wave5 VPU devices. It binds device-tree compatible hardware, maps registers, configures DMA, clocks, resets, SRAM, firmware, runtime PM, IRQ or polling-based completion, V4L2 device registration, and encoder/decoder video node registration.

## Important APIs, Types, and Functions
`wave5_vpu_probe()` is the main bring-up routine; `wave5_vpu_remove()` tears the device down. `wave5_vpu_wait_interrupt()` is shared by sequence setup paths. IRQ handling is split between hard IRQ `wave5_vpu_irq()`, threaded IRQ `wave5_vpu_irq_thread()`, and the fallback polling path `wave5_vpu_timer_callback()`, `wave5_vpu_irq_work_fn()`, and `irq_thread()`. `wave5_vpu_load_firmware()` requests firmware and initializes the VPU. PM callbacks call `wave5_vpu_sleep_wake()` and clock operations.

## Control Flow
Probe validates match data, sets a 32-bit DMA mask, allocates `struct vpu_device`, maps the register region, deasserts reset, enables clocks, obtains optional SRAM, initializes VDI/common memory, sets up IRQ or polling workers, registers a V4L2 device, registers decoder and encoder nodes depending on match flags, loads firmware, enables runtime PM, then sleeps the VPU. IRQ service reads interrupt reason and per-instance done bits, clears hardware interrupt registers, records picture completion into each instance kfifo, completes sequence waits, and schedules threaded processing. The thread drains per-instance IRQ status and calls `inst->ops->finish_process()`.

## State and Persistence
`struct vpu_device` persists for the platform device lifetime and owns locks, instance list, register base, common memory, SRAM metadata, clock/reset handles, IRQ or polling worker state, V4L2 device, and video devices. Per-instance completions and FIFOs are updated from IRQ context. No persistent storage is used outside requested firmware loading.

## Dependencies and Integration Points
Uses Linux platform, OF match data, firmware loader, reset/clock/runtime PM APIs, gen_pool SRAM, V4L2 registration, threaded IRQs, hrtimers, kthread workers, and Wave5 VDI/backend functions. It expects firmware `cnm/wave521c_k3_codec_fw.bin` for `ti,j721s2-wave521c`.

## Risks
The IRQ handler scans all instances and depends on firmware instance bitmaps matching `inst->id`. Fallback polling is more complex and must avoid worker/thread leaks on probe errors. Runtime resume calls sleep/wake before enabling clocks, which should be validated against hardware expectations. Remove unregisters both encoder and decoder unconditionally, so disabled capability combinations rely on unregister helpers tolerating absent devices.

## Test Signals
Probe/remove on device-tree matched systems, missing firmware path, no-IRQ fallback polling, suspend/resume and runtime autosuspend, concurrent encoder/decoder instances, interrupt storms with multiple instance IDs, reset/clock failure injection, and `v4l2-compliance` node visibility.
