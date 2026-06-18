# sources/distributed-fs/ceph-client/drivers/misc/vcpu_stall_detector.c

## Purpose
`vcpu_stall_detector.c` drives a virtual per-vCPU watchdog/stall detector device, intended for QEMU. It periodically reloads per-CPU MMIO counters and panics the guest if the virtual device raises a stall interrupt.

## Important APIs, Types, and Functions
`struct vcpu_stall_detect_config` stores global clock, timeout, IRQ, MMIO base, platform device, and CPU hotplug state. `struct vcpu_stall_priv` stores a per-CPU hrtimer and initialization flag. Runtime callbacks are `vcpu_stall_detect_timer_fn()`, `vcpu_stall_detector_irq()`, `start_stall_detector_cpu()`, and `stop_stall_detector_cpu()`. Platform lifecycle is `vcpu_stall_detect_probe()` and `vcpu_stall_detect_remove()`.

## Control Flow
Probe allocates per-CPU detector state, maps MMIO, reads optional `clock-frequency` and `timeout-sec` DT properties with range validation, optionally requests a percpu PPI, and installs a dynamic CPU hotplug online state. When a CPU starts, the driver writes that vCPU's clock frequency, load count, and status registers, initializes a pinned hrtimer, and starts it at half the timeout. The hrtimer reloads the per-vCPU counter and re-arms itself. If the device interrupt fires, the ISR panics the kernel. Remove unregisters the hotplug state, frees the percpu IRQ, and stops all initialized timers.

## State and Persistence
Global config is a single static instance, so the driver assumes one device. Per-CPU hrtimer initialization state is allocated devm-percpu. Hardware state is per-vCPU MMIO register blocks. No persistent state exists.

## Dependencies and Integration Points
The driver depends on platform devices, OF matching for `qemu,vcpu-stall-detector`, MMIO access, hrtimers, CPU hotplug, percpu IRQs, and kernel panic handling.

## Risks and Edge Cases
`start_stall_detector_cpu()` uses `this_cpu_ptr()` instead of `per_cpu_ptr(..., cpu)`, relying on CPU hotplug callback execution context matching the target CPU. Remove calls `cpuhp_remove_state()` before stopping timers, which should offline callbacks but still deserves race testing. The IRQ handler unconditionally panics, so false positives are severe. Property validation rejects values equal to the max constants because it uses `<`, not `<=`.

## Test Signals
Validate DT property defaults and range warnings, per-CPU MMIO offsets, CPU hotplug start/stop behavior, hrtimer reload cadence, optional PPI request/free, panic on injected stall interrupt, remove-time timer cancellation, and multi-device rejection assumptions.
