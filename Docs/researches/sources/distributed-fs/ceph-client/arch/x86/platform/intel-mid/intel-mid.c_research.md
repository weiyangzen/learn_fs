<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/intel-mid.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/intel-mid.c

## Purpose
Overrides generic x86 initialization for Intel MID/Moorestown-style systems and installs platform-specific reboot and poweroff paths.

## Important APIs, Types, And Functions
`x86_intel_mid_early_setup()` rewires `x86_init`, `x86_platform`, `legacy_pic`, PCI init hooks, and reboot/poweroff handlers. `intel_mid_power_off()` combines PWRMU S5 command with SCU IPC cold-off, and `intel_mid_reboot()` sends SCU cold-reset.

## Control Flow
Early setup disables ROM/resource probing, MP table parsing, legacy PIC use, IO-APIC IRQ fixups, and generic ACPI reduced-hardware init. It selects LAPIC clockevent setup and marks the ISA bus as not PCI. Later shutdown paths call PWRMU/SCU helpers.

## State And Persistence
Mutates global x86 platform operation tables, `pm_power_off`, `machine_ops.emergency_restart`, and legacy PIC selection for the life of the boot.

## Dependencies And Integration Points
Depends on Intel SCU IPC, APIC clock setup, Intel MID PCI initialization, regulator constraints, and PWRMU exports from `pwr.c`.

## Risks And Edge Cases
These global overrides are only safe on true Intel MID platforms. Incorrect detection would disable standard discovery and interrupt paths. Poweroff assumes PWRMU is available before falling through to SCU IPC command handling.

## Test Signals
Boot on Intel MID without MP table probing failures, LAPIC timer operation, PCI enumeration through Intel MID arch init, and working SCU reset/poweroff are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel-mid/intel-mid.c -->
