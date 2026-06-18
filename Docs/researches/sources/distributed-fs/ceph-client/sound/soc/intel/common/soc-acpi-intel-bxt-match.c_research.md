<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-bxt-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-bxt-match.c

## Purpose
Broxton/Apollo Lake ACPI machine-match table for legacy SST/SOF I2S designs, with a DMI quirk for Apollo Lake RVP1A.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_bxt_machines[]`. Defines `apl_table`, `apl_quirk()`, codec companion lists for ES83x6 and MAX98357A/DMIC, and machine entries for ALC298, DA7219/MAX98357A, PCM512x, WM8804, TDF8532, and ES8336 dynamic topology naming.

## Control Flow, State, and Persistence
Machine selection is table-driven. The `INT34C3` TDF8532 entry invokes `apl_quirk()`, which checks DMI for Intel Apollo Lake RVP1A and rewrites `mach->id` from `dmi_id->driver_data` when needed. ES8336 uses topology quirk masks so topology suffixes are derived at runtime.

## Dependencies and Integration
Depends on Linux DMI and ASoC ACPI matching. Consumed by Intel platform driver selection during ACPI enumeration for BXT/APL systems.

## Risks and Test Signals
Risks include DMI-specific ID mutation affecting later matches, companion codec detection for DA7219/MAX98357A boards, and dynamic ES8336 topology suffix mismatch. Test signals are DMI quirk behavior on RVP1A, correct machine driver selection for each HID, SOF topology load, and playback/capture/DMIC validation on Apollo Lake boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-bxt-match.c -->
