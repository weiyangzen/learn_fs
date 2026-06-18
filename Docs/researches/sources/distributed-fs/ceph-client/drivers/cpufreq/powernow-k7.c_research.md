<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.c

## Purpose

Implements AMD K7 PowerNow frequency and voltage scaling using either BIOS PSB/PST tables or ACPI performance objects. It handles Athlon mobile-era FID/VID transitions and A0 stepping errata.

## APIs, Types, And Functions

Important types are local PSB/PST structs, ACPI control decoding, and the global `powernow_table`. `check_powernow()` probes CPUID capabilities, `powernow_decode_bios()` scans low BIOS memory for `AMDK7PNOW!`, `powernow_acpi_init()` builds state from ACPI, and `powernow_target()` writes FID/VID MSRs. `change_FID()` and `change_VID()` manipulate `MSR_K7_FID_VID_CTL` using bit layouts from `powernow-k7.h`.

## Control Flow

Late init registers the driver only if CPUID reports PowerNow capability. CPU init recalibrates `cpu_khz`, derives FSB from current FID, rejects non-CPU0 policies, then prefers BIOS PST unless DMI or `acpi_force` selects ACPI. BIOS tables are matched on CPUID, FSB, max FID, and start VID. ACPI states are translated to FID/VID pairs and may correct reported MHz values. The target path reads current FID, computes old/new rates, applies A0 interrupt masking when needed, then lowers frequency before voltage when going down or raises voltage before frequency when going up.

## State And Persistence

Global mutable state includes capability flags, FSB, min/max speeds, settling latency, `have_a0`, and allocated `powernow_table`; ACPI state is retained in `acpi_processor_perf` when used. Hardware state persists in K7 FID/VID MSRs. Exit unregisters ACPI performance data and frees the table.

## Dependencies And Integration Points

Uses x86 CPUID/MSR access, ACPI processor performance support, DMI blacklist matching, BIOS physical memory scanning, recalibration helpers, and cpufreq table verification. It optionally exposes ACPI BIOS limit handling.

## Risks And Test Signals

Malformed firmware tables can program unsafe FID/VID pairs; the driver contains explicit warnings and DMI disablement for known broken Acer BIOSes. Half multipliers are invalidated for A0/ACPI errata. Test signals include decoded PST/ACPI entries, SGTC calculation, min/max logs, current frequency read from `MSR_K7_FID_VID_STATUS`, and successful fallback from BIOS to ACPI on missing PST data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.c -->
