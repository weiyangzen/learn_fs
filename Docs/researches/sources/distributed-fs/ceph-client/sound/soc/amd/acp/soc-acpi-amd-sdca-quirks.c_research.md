# sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc-acpi-amd-sdca-quirks.c

## Purpose
`soc-acpi-amd-sdca-quirks.c` implements an AMD SoundWire/SDCA machine-check helper used to filter ACPI machine entries for RT712 VB-style devices.

## Important APIs, Types, and Functions
The exported function is `snd_soc_acpi_amd_sdca_is_device_rt712_vb(void *arg)`.

## Control Flow
The helper treats `arg` as `struct sdw_amd_ctx`, rejects null context, iterates discovered SoundWire peripherals, and returns true if any peripheral matches `SDCA_QUIRKS_RT712_VB` through `sdca_device_quirk_match()`.

## State and Persistence
The file has no mutable state. It reads the caller's discovery context and peripheral array.

## Dependencies and Integration Points
It depends on AMD SoundWire context definitions, SDCA quirk matching, and ASoC ACPI machine matching. `amd-acp70-acpi-match.c` uses it as a `machine_check` callback for the RT712 VB entry.

## Risks
The callback argument is not a traditional `snd_soc_acpi_mach` pointer, so callers must pass the AMD SoundWire context documented in the comment. A false result skips the machine entry, which can hide hardware if peripheral quirk detection is incomplete.

## Test Signals
Validate machine selection with RT712 VB peripherals present and absent, null-context behavior, and namespace import/export under `CONFIG_SND_SOC_ACPI_AMD_SDCA_QUIRKS`.
