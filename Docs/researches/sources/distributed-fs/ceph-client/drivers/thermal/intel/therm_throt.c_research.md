# sources/distributed-fs/ceph-client/drivers/thermal/intel/therm_throt.c

## Purpose

`therm_throt.c` is the x86 Intel thermal interrupt and throttling event core. It configures local APIC thermal vectors and MSR interrupt enables, counts/logs core/package thermal and power-limit events, exposes per-CPU sysfs counters, and calls platform/HFI threshold callbacks.

## Important APIs, Types, and Functions

Key state types are `_thermal_state` and per-CPU `struct thermal_state`. Exported callback pointers are `platform_thermal_notify`, `platform_thermal_package_notify`, and `platform_thermal_package_rate_control`. Public functions include `thermal_clear_package_intr_status()`, `intel_thermal_interrupt()`, `x86_thermal_enabled()`, `therm_lvt_init()`, and `intel_init_thermal()`. CPU hotplug callbacks initialize work, HFI, APIC unmasking, and sysfs groups.

## Control Flow

CPU thermal initialization verifies APIC/ACPI/clock-modulation support, respects BIOS SMI ownership, masks the APIC vector, initializes clear masks, enables threshold/power-limit/HFI MSR interrupts, enables TM1, and marks throttling enabled. Device init later registers CPU hotplug if enabled. Runtime interrupt handling clears HWP status, reads core/package thermal MSRs, notifies platform threshold handlers, tracks throttling/power-limit state transitions, and forwards HFI updates. Delayed work rate-limits logs while throttling remains active.

## State and Persistence Behavior

Per-CPU counters, timestamps, rate-control fields, and work items persist while CPUs are online. Sysfs exposes counts and throttle durations. APIC LVT and MSR interrupt configuration are per-CPU hardware state.

## Dependencies and Integration Points

It depends on x86 APIC/MSR features, CPU hotplug, sysfs CPU devices, HFI hooks, package temp thermal callbacks, and weak HWP notification override. `thermal_interrupt.h` exposes callback and clear APIs to peer drivers.

## Risks and Test Signals

Risks include BIOS SMI ownership detection, interrupt clear-mask correctness, APIC mask/unmask ordering with HFI, delayed work on CPU offline, platform callback rate control, and optional `int_pln_enable` changing power-limit behavior. Test signals include boot thermal init, CPU online/offline sysfs lifecycle, threshold interrupts, package temp callback integration, HFI event forwarding, throttling duration counters, and HWP status clearing.
