# sources/distributed-fs/ceph-client/sound/soc/amd/acp/soc-acpi-amd-sdca-quirks.h

## Purpose
`soc-acpi-amd-sdca-quirks.h` declares the optional SDCA machine-check helper and provides a false-returning stub when the quirk helper is not enabled.

## Important APIs, Types, and Functions
The key API is `snd_soc_acpi_amd_sdca_is_device_rt712_vb(void *arg)`, either as an external declaration or static inline stub depending on `CONFIG_SND_SOC_ACPI_AMD_SDCA_QUIRKS`.

## Control Flow
Including ACPI match tables can call the helper unconditionally. With the config disabled, the inline stub always rejects the special machine entry.

## State and Persistence
The header owns no state.

## Dependencies and Integration Points
It is included by `amd-acp70-acpi-match.c`. The enabled implementation is in `soc-acpi-amd-sdca-quirks.c`.

## Risks
When the config is disabled, RT712 VB-specific entries are never selected. Function signature uses `void *`, so type mismatches are only caught by runtime behavior.

## Test Signals
Build both enabled and disabled configurations. Runtime matching should select RT712 VB only when the config and peripheral quirk detection are available.
