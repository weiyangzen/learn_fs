<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_pmtmr.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_pmtmr.h

## Purpose
`acpi_pmtmr.h` declares ACPI PM timer constants and early read/suspend callback helpers for x86 PM timer users.

## Important APIs, types, and functions
It defines `PMTMR_TICKS_PER_SEC`, `ACPI_PM_MASK`, and `ACPI_PM_OVRRUN`. With `CONFIG_X86_PM_TIMER`, it declares `acpi_pm_read_verified()`, `pmtmr_ioport`, `acpi_pm_read_early()`, and suspend/resume callback registration/unregistration. Without the config, `acpi_pm_read_early()` returns zero.

## Control flow
Early readers check `pmtmr_ioport`; if present, they read the verified PM timer value and mask it to 24 bits. Callback registration lets one consumer observe suspend/resume transitions.

## State and persistence behavior
`pmtmr_ioport` is global platform state. The callback registration persists until unregistered.

## Dependencies and integration points
The header depends on clocksource masks and x86 ACPI PM timer support. It integrates clock calibration, early timekeeping, and suspend/resume paths.

## Risks and test signals
Risks include treating zero as a valid timer when no IO port exists, 24-bit wrap handling mistakes, and callback lifetime issues. Test signals include PM timer calibration, suspend/resume callback invocation, early boot reads, and non-x86/disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_pmtmr.h -->
