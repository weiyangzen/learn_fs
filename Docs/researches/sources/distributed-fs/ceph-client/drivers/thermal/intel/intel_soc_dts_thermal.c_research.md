# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_soc_dts_thermal.c

## Purpose

`intel_soc_dts_thermal.c` is the platform module that enables IOSF SoC DTS thermal zones and APIC threshold interrupts on supported Intel Atom Silvermont/Baytrail systems.

## Important APIs, Types, and Functions

Module parameter `crit_offset` sets the critical trip offset from TjMax. `soc_irq_thread_fn()` forwards threshold IRQs to `intel_soc_dts_iosf_interrupt_handler()`. `intel_soc_thermal_init()` matches CPU IDs, initializes IOSF DTS with APIC interrupts and critical trips, registers the fixed GSI, and requests a threaded IRQ. Exit frees IRQ/GSI and exits the DTS core.

## Control Flow

Init is CPU gated. It creates DTS zones first so polling remains usable even if IRQ setup fails. It then maps the fixed APIC GSI 86 and requests a threaded interrupt, warning but not failing if IRQ request fails. Exit unwinds IRQ/GSI and sensor state.

## State and Persistence Behavior

Static globals store the GSI, Linux IRQ, and DTS sensor pointer. DTS register persistence/restoration is handled by the shared IOSF implementation.

## Dependencies and Integration Points

It depends on ACPI GSI registration, x86 CPU matching, IRQ APIs, and `intel_soc_dts_iosf`. It is the APIC-interrupt frontend for the shared IOSF DTS core.

## Risks and Test Signals

Risks include fixed GSI assumptions, IRQ flag requirements matching firmware defaults, nonfatal interrupt setup leaving polling-only behavior, and `crit_offset` values that create invalid critical trips. Test signals include CPU match gating, DTS init with critical trips, GSI register/unregister, threaded IRQ forwarding, and cleanup after IRQ request failure.
