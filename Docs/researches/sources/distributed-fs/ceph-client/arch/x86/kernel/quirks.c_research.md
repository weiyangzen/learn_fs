# sources/distributed-fs/ceph-client/arch/x86/kernel/quirks.c

## Purpose
Collects PCI/DMI-driven x86 platform workarounds for chipset IRQ balancing, HPET discovery/resume, HPET MSI disable, AMD NUMA node tagging, AMD scrub errata, Intel RAS copy-machine-check behavior, and Apple machine detection.

## APIs, Types, And Functions
Exports `x86_apple_machine`; defines `force_hpet_address` and HPET resume state. Important functions include Intel IRQ balance quirk, multiple HPET force-enable/resume helpers for Intel ICH, VIA VT8237, ATI, NVIDIA, Intel e6xx, `force_hpet_resume()`, AMD NB NUMA quirk, AMD scrub workaround, Intel RAS capability quirks, and `early_platform_quirks()`.

## Control Flow
PCI fixup macros attach quirk functions to chipset IDs at header, early, or final phases. HPET helpers inspect chipset config registers, optionally require `hpet=force`, set `force_hpet_address`, cache devices for resume, and later reprogram registers in `force_hpet_resume()`. IRQ balancing quirk disables irqdebug/affinity on affected Intel MCH revisions. NUMA quirk derives device node from AMD northbridge config. RAS quirks enable fragile machine-check copy behavior based on server capability bits.

## State And Persistence
Quirk decisions persist in globals such as `force_hpet_address`, `force_hpet_resume_type`, cached PCI device, `hpet_msi_disable`, device NUMA nodes, machine-check copy mode, and `x86_apple_machine`.

## Dependencies And Integration
Depends on PCI fixup infrastructure, HPET timer setup, DMI, IRQ affinity/debug code, NUMA node APIs, machine-check recovery, platform data for Apple machines, and chipset-specific config registers.

## Risks And Test Signals
Quirk code writes undocumented or chipset-specific registers, so false positives can break timers or platform behavior. Resume paths depend on cached devices remaining valid. Test signals include HPET boot/resume logs, timer stability, irq affinity behavior on old Intel platforms, NUMA placement on AMD NB devices, machine-check copy recovery tests, and DMI detection on Apple hardware.
