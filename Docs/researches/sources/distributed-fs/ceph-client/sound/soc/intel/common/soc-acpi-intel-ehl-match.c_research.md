<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ehl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ehl-match.c

## Purpose
Elkhart Lake ACPI match table for the RT5660 machine driver.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_ehl_machines[]` with one `10EC5660` entry mapping to `ehl_rt5660` and `sof-ehl-rt5660.tplg`.

## Control Flow, State, and Persistence
No executable control flow or persistent state exists beyond the static match entry and sentinel. ACPI HID matching selects the machine data for platform probe.

## Dependencies and Integration
Depends on ASoC ACPI match headers and the Intel match aggregate. Consumed by EHL SOF platform selection.

## Risks and Test Signals
Risks are limited to boards needing companion-codec or topology variants not represented by the single entry. Test signals are RT5660 EHL probe, topology load, and playback/capture validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ehl-match.c -->
