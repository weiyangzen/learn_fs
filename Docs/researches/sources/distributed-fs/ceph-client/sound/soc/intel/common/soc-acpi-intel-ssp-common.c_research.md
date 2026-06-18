# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-ssp-common.c

## Purpose
Provides Intel ACPI SSP machine-driver helper routines for detecting board codec and amplifier parts by ACPI HID and mapping those parts to topology filename suffixes and printable names.

## Important APIs, Types, And Functions
The private `struct codec_map` binds user-visible part names, topology suffixes, ACPI HIDs, and `enum snd_soc_acpi_intel_codec` values. `snd_soc_acpi_intel_detect_codec_type()` scans the `codecs[]` table with `acpi_dev_present()`. `snd_soc_acpi_intel_detect_amp_type()` does the same for `amps[]`. `snd_soc_acpi_intel_get_codec_name()`, `snd_soc_acpi_intel_get_codec_tplg_suffix()`, and `snd_soc_acpi_intel_get_amp_tplg_suffix()` provide reverse lookups. All helpers are exported in the `SND_SOC_ACPI_INTEL_MATCH` namespace.

## Control Flow, State, And Persistence
The file is table-driven and keeps no persistent runtime state. Detection is first-match-wins, so table ordering matters. The amp table intentionally places monolithic codec/amp-capable parts after dedicated amp parts to avoid selecting a codec as an amp too early.

## Dependencies And Integration Points
Depends on ACPI enumeration, `sound/soc-acpi.h`, and Intel SSP ACPI HID definitions from `sound/soc-acpi-intel-ssp-common.h`. SOF and machine matching code use the exported helpers while completing topology filenames and choosing machine quirks.

## Risks And Test Signals
Risks are stale HID/suffix mappings, duplicate enum entries across codec and amp lists, and unexpected selection caused by table ordering. Test signals include ACPI mock systems with each HID, topology-name completion tests for codec plus amp combinations, and kernel logs showing the detected part names through `dev_dbg()`.
