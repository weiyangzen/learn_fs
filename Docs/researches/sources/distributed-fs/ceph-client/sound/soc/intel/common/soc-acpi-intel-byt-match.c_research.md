<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-byt-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-byt-match.c

## Purpose
Bay Trail ACPI machine-match table for tablet/laptop audio codecs, including DMI overrides for systems whose ACPI IDs are ambiguous or incorrect.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_baytrail_machines[]`. Defines DMI callbacks for RT5672 and Point of View P1006W overrides, static override machines `byt_rt5672` and `byt_pov_p1006w`, `byt_quirk()`, codec companion lists for RT5640/WM5102/DA7213/RT5645, and machine entries for RT5640, RT5651, WM5102, DA7213, ES8316, RT5682, RT5645, MAX98090, CX2072x, and optional nocodec.

## Control Flow, State, and Persistence
The first RT5640-compatible entry can call `byt_quirk()`, which runs the DMI table and returns a different static machine descriptor for known systems. Otherwise matching proceeds through ACPI HID or companion codec lists. No state persists except the selected machine data passed to the platform driver.

## Dependencies and Integration
Depends on Linux DMI, ASoC ACPI match helpers, and optional `CONFIG_SND_SOC_INTEL_BYT_CHT_NOCODEC_MACH`. Used by Intel Bay Trail SST/SOF platform selection.

## Risks and Test Signals
Risks include broad DMI matches selecting the wrong override, wildcard companion IDs taking precedence over more specific entries, optional nocodec exposure on production systems, and topology filenames shared with Cherry Trail-era drivers. Test signals are DMI-quirked device probes, ACPI matching for each codec HID, SOF topology load, and audio routing validation on known Bay Trail tablets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-byt-match.c -->
