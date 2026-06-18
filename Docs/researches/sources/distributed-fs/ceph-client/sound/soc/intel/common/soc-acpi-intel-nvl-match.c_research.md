<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-nvl-match.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-nvl-match.c

## Purpose
Nova Lake placeholder ACPI match data with SoundWire mockup topology entries for early validation.

## APIs, Types, and Functions
Exports sentinel-only `snd_soc_acpi_intel_nvl_machines[]` and `snd_soc_acpi_intel_nvl_sdw_machines[]` containing three `sof_sdw` entries based on mockup headset/two-amp/mic, headset/one-amp/mic, and mic/headset/one-amp link arrays.

## Control Flow, State, and Persistence
No mutable runtime state exists. SoundWire mockup entries match synthetic link masks and select reused NVL topology filenames for validation.

## Dependencies and Integration
Depends on ASoC ACPI match headers and `soc-acpi-intel-sdw-mockup-match.h`. Integrated into the Intel match aggregate for early platform bring-up/testing.

## Risks and Test Signals
Risks include mockup-only coverage not matching production NVL hardware, topology filenames inherited from older RT711/RT1308/RT715 patterns, and no SSP machine entries. Test signals are build/export success, mockup SoundWire enumeration, and SOF topology load in NVL validation environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/common/soc-acpi-intel-nvl-match.c -->
