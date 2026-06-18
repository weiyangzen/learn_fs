# sources/distributed-fs/ceph-client/sound/soc/amd/acp-config.c

## Purpose
`acp-config.c` selects AMD ACP audio configuration paths and publishes ACPI machine tables for SOF-enabled AMD platforms. It decides whether a PCI ACP device should use SOF, legacy, or legacy-only-DMIC behavior using PCI revision, ACPI properties, and DMI quirks.

## Important APIs, Types, And Functions
The exported API is `snd_amd_acp_find_config()`. `snd_amd_acp_acpi_find_config()` reads `acp-audio-config-flag`. `config_table` maps selected DMI systems to `FLAG_AMD_SOF` or `FLAG_AMD_LEGACY`. `acp70_acpi_flag_override_table` suppresses ACPI flag use for a specific ASUS system. Exported machine arrays include `snd_soc_acpi_amd_sof_machines`, `snd_soc_acpi_amd_vangogh_sof_machines`, `snd_soc_acpi_amd_rmb_sof_machines`, `snd_soc_acpi_amd_acp63_sof_machines`, and `snd_soc_acpi_amd_acp70_sof_machines`.

## Control Flow
For revision zero, config selection returns 0. For ACP 7.0 or newer, the function returns 0 on the ASUS override or reads the ACPI integer flag, defaulting to legacy-only DMIC. For older revisions, it scans DMI entries matching the PCI device and returns the configured flags, updating global `acp_quirk_data`. SOF machine arrays then let ASoC/SOF matching pick driver names, codec-list quirks, firmware names, topology files, and platform data.

## State And Persistence
Persistent module state is `acp_quirk_data`, exported indirectly as `pdata` to matched machine drivers. The ACPI machine arrays are static exported tables consumed by platform/SOF probing.

## Dependencies And Integration Points
The file depends on ACPI, DMI, PCI, `../sof/amd/acp.h`, `mach-config.h`, and ASoC ACPI machine matching. It bridges low-level ACP PCI detection with machine-driver and SOF firmware/topology selection.

## Risks And Edge Cases
DMI matching is exact for many systems and broad for Google systems, so table order and specificity matter. ACP 7.x relies on BIOS ACPI flags except for overrides; incorrect firmware properties can route to the wrong stack. `acp_quirk_data` is global, so multi-device assumptions should be considered.

## Test Signals
Tests should cover revision zero, pre-7.0 DMI hits/misses, ACP7 ACPI property values, ASUS override behavior, SOF machine matching for listed codec IDs, firmware/topology filename selection, and multi-platform module load ordering.
