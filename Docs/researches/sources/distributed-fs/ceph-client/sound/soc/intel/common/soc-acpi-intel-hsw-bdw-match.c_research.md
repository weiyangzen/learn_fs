<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hsw-bdw-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hsw-bdw-match.c

## Purpose
Haswell/Broadwell ACPI machine-match table for legacy Intel SST/SOF audio boards using RT286, RT5650, RT5677, and RT5640 codecs.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_broadwell_machines[]` with entries for `INT343A`/`bdw_rt286`, `10EC5650`/`bdw-rt5650`, `RT5677CE`/`bdw-rt5677`, and `INT33CA`/`hsw_rt5640`, each with corresponding `sof-bdw-*.tplg` topology names.

## Control Flow, State, and Persistence
The file is static descriptor data; ACPI HID matching selects the machine driver and topology. No mutable state or quirk callback is present despite including DMI.

## Dependencies and Integration
Depends on ASoC ACPI match headers and is linked into the Intel match aggregate. Used by HSW/BDW CATPT/SST/SOF machine selection paths.

## Risks and Test Signals
Risks include stale topology naming for Haswell entries using Broadwell prefixes, unused DMI include indicating possible historical quirk removal, and lack of companion-codec disambiguation. Test signals are machine selection on HSW/BDW systems and successful topology load/playback/capture for each codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-hsw-bdw-match.c -->
