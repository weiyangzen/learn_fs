# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/apic.c

## Purpose
This is the central local APIC implementation for x86. It initializes and tears down the LAPIC, selects interrupt delivery mode, configures BSP/AP setup, calibrates and registers the LAPIC clockevent, handles local APIC timer/spurious/error vectors, manages x2APIC enablement, composes x86 MSI messages, and preserves LAPIC state across suspend/resume. It is the coordinating layer between APIC driver callbacks, IO-APIC routing, IRQ remapping, timer infrastructure, CPU topology, and platform firmware.

## Important APIs, Types, And Functions
Global state includes `boot_cpu_physical_apicid`, `boot_cpu_apic_version`, `apic_is_disabled`, `apic_intr_mode`, `x2apic_mode`, `lapic_timer_period`, `apic_mmio_base`, `pic_mode`, and `smp_found_config`. Public or cross-file functions include `lapic_get_maxlvt()`, `setup_APIC_eilvt()`, `setup_boot_APIC_clock()`, `setup_secondary_APIC_clock()`, `clear_local_APIC()`, `apic_soft_disable()`, `disable_local_APIC()`, `lapic_shutdown()`, `apic_intr_mode_select()`, `apic_intr_mode_init()`, `apic_ap_setup()`, `x2apic_setup()`, `enable_IR_x2apic()`, `init_apic_mappings()`, `register_lapic_address()`, `disconnect_bsp_APIC()`, `__irq_msi_compose_msg()`, and `x86_msi_msg_get_destid()`. The file also declares IDT entries for timer, spurious, and error vectors.

## Control Flow
Boot begins with command-line parsing (`lapic`, `nolapic`, `noapictimer`, `nox2apic`, `apic_extnmi`, verbosity knobs), APIC mapping via `init_apic_mappings()`/`register_lapic_address()`, and interrupt mode selection through `apic_intr_mode_select()`. `apic_intr_mode_init()` probes the active APIC backend, runs platform post-init hooks, then calls `apic_bsp_setup()`, which connects the BSP APIC, optionally forces UP topology, initializes the local APIC, enables/sets up IO-APIC, enables IRQ remapping fault handling, and updates legacy vectors. APs call `apic_ap_setup()`.

Timer setup uses `apic_validate_deadline_timer()`, `calibrate_APIC_clock()`, and `setup_APIC_timer()`. Non-deadline mode calibrates the LAPIC bus timer against jiffies/TSC and optionally PM timer, then registers a per-CPU `clock_event_device`; deadline mode uses `MSR_IA32_TSC_DEADLINE` and TSC frequency. Runtime interrupts enter `sysvec_apic_timer_interrupt()`, `sysvec_spurious_apic_interrupt()`, `spurious_interrupt()`, or `sysvec_error_interrupt()`.

## State And Persistence
Most boot configuration is `__ro_after_init`; timer calibration writes `lapic_timer_period`; x2APIC mode uses `x2apic_state` and `x2apic_mode`; EILVT reservations are tracked in atomic `eilvt_offsets`. Suspend/resume persists LAPIC register values in `apic_pm_state`, masks IO-APIC/PIC paths while restoring, and reenables IRQ remapping. Resource state is published via the `lapic_resource` late initcall.

## Dependencies And Integration Points
This file depends on `struct apic` callbacks, IO-APIC helpers (`enable_IO_APIC()`, `setup_IO_APIC()`, `mask_ioapic_entries()`), irq-remapping APIs, x86 topology registration, clockevents, ACPI PM timer, PIT/HPET availability, MCE/perf hooks, DMI quirks, syscore PM, and hypervisor hooks for x2APIC/MSI extended destination IDs. `__irq_msi_compose_msg()` is consumed by MSI, IO-APIC, DMAR, and vector-domain code.

## Risks
The highest-risk areas are hardware errata workarounds: TSC-deadline microcode filtering, LAPIC timer shutdown with counter zeroing, ISR cleanup after crash kernels, 82489DX/old APIC behavior, x2APIC disable restrictions for large APIC IDs or locked hardware, and suspend/resume ordering. Mistakes can cause lost interrupts, stuck level IRQs, bad CPU affinity, boot hangs, or unusable timers. Command-line parsing also changes global hardware policy very early.

## Test Signals
Useful signals include boot logs for APIC mode selection, `TSC deadline timer available`, LAPIC timer calibration messages, x2APIC enable/disable logs, IRQ remapping logs, spurious/error APIC counters, suspend/resume interrupt delivery, CPU hotplug AP startup, timer tick stability, MSI routing to high APIC IDs, and boot combinations with `nolapic`, `noapictimer`, `nox2apic`, `apic=verbose/debug`, and `apic_extnmi=`.
