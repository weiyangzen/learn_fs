# sources/distributed-fs/ceph-client/arch/x86/kernel/reboot.c

## Purpose
Implements x86 machine restart, shutdown, halt, power-off, real-mode reboot, DMI reboot-method quirks, emergency virtualization shutdown, and crash NMI CPU shootdown.

## APIs, Types, And Functions
Exports `pm_power_off` and provides `machine_power_off()`, `machine_shutdown()`, `machine_emergency_restart()`, `machine_restart()`, `machine_halt()`, `machine_crash_shutdown()`, `machine_real_restart()`, `nmi_shootdown_cpus()`, `run_crash_ipi_callback()`, and `nmi_panic_self_stop()`. State includes `reboot_emergency`, `port_cf9_safe`, `machine_ops`, `crashing_cpu`, shootdown callback, waiting counter, and `crash_ipi_issued`.

## Control Flow
`reboot_init()` applies DMI quirks unless command line reboot type was overridden, with EFI fallback for hardware-reduced ACPI. `native_machine_restart()` optionally performs clean shutdown, runs restart notifiers, then enters emergency restart. `native_machine_emergency_restart()` disables virtualization when needed, writes CMOS warm/cold reboot marker, honors EFI capsule reboot, and loops through ACPI, keyboard controller, EFI, BIOS real-mode, CF9, and triple-fault reset methods until one succeeds. `native_machine_shutdown()` stops I/O APIC, other CPUs, LAPIC, HPET, IOMMU, and guest encryption hooks. SMP crash shootdown installs an emergency local NMI handler, sends NMI to all other CPUs, runs optional callbacks, disables virtualization, and halts remote CPUs.

## State And Persistence
Reboot type/mode are global boot/runtime policy. `machine_ops` is `__ro_after_init` and can be overridden by platform code before lockdown. Crash shootdown is deliberately one-shot and leaves the emergency NMI handler installed to handle late arrivals.

## Dependencies And Integration
Depends on ACPI, EFI runtime, DMI, real-mode trampoline, CMOS/RTC lock, APIC/IO-APIC/HPET, KVM virtualization disable hooks, tboot, IOMMU shutdown, reboot fixups, panic/crash dump infrastructure, and NMI dispatch in `nmi.c`.

## Risks And Test Signals
Reboot paths run in inconsistent system states, so locking and ordering are constrained. Risks include hanging with VMX/SVM active, wrong DMI reboot method, late NMI list corruption, or shutdown ordering issues with IO-APIC/LAPIC/HPET/IOMMU. Test signals include reboot across DMI-quirked machines, kdump/crash shootdown, sysrq-B, EFI capsule reboot, virtualization host reboot, and panic NMI behavior.
