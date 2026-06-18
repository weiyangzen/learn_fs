<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-arl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-arl-match.c

## Purpose
Arrow Lake ACPI match data for SSP codec boards and SoundWire topologies, including newer function-topology support for CS42L43/CS35L56 and RT722/RT1320 configurations.

## APIs, Types, and Functions
Exports `snd_soc_acpi_intel_arl_machines[]` and `snd_soc_acpi_intel_arl_sdw_machines[]`. Defines SSP codec lists for ES83x6, RT5682, and LT6911 HDMI, endpoint/address descriptors for CS42L43, CS35L56, RT711/RT711-SDCA, RT722, RT1316, and RT1320, and multiple `snd_soc_acpi_link_adr` arrays with `sof_sdw_get_tplg_files` hooks.

## Control Flow, State, and Persistence
Static tables select machine drivers/topologies based on ACPI HID/codec lists or SoundWire link masks. Several SoundWire matches share topology filenames while function topology expansion derives additional topology files from endpoint/function data. No mutable state persists in this file.

## Dependencies and Integration
Depends on ASoC ACPI match headers, SSP common helpers, and `sof-function-topology-lib.h`. Integrated by the Intel ACPI match aggregate and consumed by SOF platform and SoundWire machine selection.

## Risks and Test Signals
Risks include function topology metadata mismatching physical endpoints, shared topology filenames hiding hardware differences, missing LT6911 companion checks for SSP HDMI designs, and link-mask collisions among CS42L43/CS35L56 variants. Test signals are ARL ACPI match selection, generated function topology file list correctness, SoundWire link enumeration, and validation of headset, speaker aggregation, HDMI-SSP, and RT722/RT1320 playback/capture paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-arl-match.c -->
