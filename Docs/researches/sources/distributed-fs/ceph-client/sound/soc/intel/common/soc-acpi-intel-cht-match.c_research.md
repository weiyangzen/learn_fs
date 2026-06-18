<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cht-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cht-match.c

## Purpose
Cherry Trail ACPI machine-match table for codec-heavy tablet designs, with DMI quirks for Surface 3, missing ES8316 devices, and Lenovo Yoga Tab3 X90 ACPI irregularities.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_cherrytrail_machines[]`. Defines `cht_quirk()`, `cht_ess8316_quirk()`, `lenovo_yt3_x90_quirk()`, DMI tables, static replacement machine descriptors, companion codec lists for RT5640/RT5670/RT5645/DA7213, and entries for RT5672, RT5645, MAX98090, NAU8824, DA7213, ES8316, RT5640, RT5682, RT5651, CX2072x, PCM512x, Lenovo SST-ID fallback, and optional nocodec.

## Control Flow, State, and Persistence
Table matching is mostly static, but selected entries run DMI checks that can replace the matched machine, skip an ES8316 entry when the codec is not actually present, or match Lenovo hardware by SST ID when the codec is missing from ACPI. The selected `snd_soc_acpi_mach` data persists only as machine-driver configuration.

## Dependencies and Integration
Depends on Linux DMI, ASoC ACPI matching, and optional nocodec Kconfig. Used by Cherry Trail SST/SOF platform drivers and machine drivers shared with Bay Trail/Cherry Trail codecs.

## Risks and Test Signals
Risks include broad SST-ID fallback matching unintended systems, ES8316 skip logic suppressing valid boards with similar DMI, order-sensitive wildcard codec lists, and optional nocodec selection. Test signals are probe outcomes on Surface 3, Lenovo Yoga Tab3 X90, ES8316 CherryTrail devices, and standard RT56xx/DA7213/MAX98090 boards, plus topology load and audio path validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-cht-match.c -->
