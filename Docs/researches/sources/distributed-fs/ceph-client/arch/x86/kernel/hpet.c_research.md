# sources/distributed-fs/ceph-client/arch/x86/kernel/hpet.c

## Purpose
Implements x86 HPET discovery, MMIO mapping, clocksource registration, legacy replacement clockevent, MSI per-CPU clockevents, hotplug handling, optional `/dev/hpet` reservation, suspend/resume restoration, and RTC interrupt emulation.

## Important APIs, Types, And State
Defines `struct hpet_channel`, `struct hpet_base`, globals `hpet_address`, `hpet_blockid`, `hpet_msi_disable`, `boot_hpet_disable`, `hpet_force_user`, and exported `is_hpet_enabled()` plus many RTC-emulation exports under `CONFIG_HPET_EMULATE_RTC`. Core APIs include `hpet_enable()`, `hpet_late_init()`, `hpet_disable()`, clockevent state callbacks, MSI domain helpers, and `read_hpet()`.

## Control Flow
Command-line parsing handles `hpet=disable,force,verbose` and `nohpet`. `hpet_enable()` checks capability and PC10 damage, maps MMIO, validates config register and period, computes frequency, allocates channel records, sanitizes global/channel config, validates counting, registers the clocksource, and if legacy routing is supported registers channel 0 as global clockevent. Late init optionally force-enables HPET, reserves a device channel, selects MSI clockevent channels, reserves platform timers, and registers CPU hotplug callbacks. MSI channels use an IRQ domain, allocate vectors, request IRQs, set affinity, and register per-CPU clockevents. RTC emulation uses channel 1 one-shot compares to synthesize UIE/AIE/PIE events.

## Dependencies And Integration Points
Depends on ACPI/quirk-provided `hpet_address`, clocksource/clockevents, generic MSI IRQ domains, x86 vector domain, APIC affinity, CPU hotplug state machine, `/dev/hpet` platform code, RTC core, PM suspend/resume, MWAIT/PC10 CPUID/MSR heuristics, and legacy IRQ replacement.

## Risks And Test Signals
Risks include unreliable HPET hardware, comparator programming races, forced HPET on PC10-damaged systems, incorrect channel reservation conflicts, MSI domain allocation failures, stale RTC emulation state, and slow HPET reads under high CPU counts. Tests include boot with/without HPET, `nohpet`/force/verbose, legacy IRQ mode, MSI per-CPU timers, CPU hotplug, suspend/resume, RTC alarm/update/periodic emulation, clocksource selection, and warnings for invalid config/counting/period.
