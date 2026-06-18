# sources/distributed-fs/ceph-client/sound/soc/amd/mach-config.h

## Purpose
`mach-config.h` is the shared AMD ASoC machine-configuration contract used by ACP legacy, SOF, SoundWire, and Pink Sardine PCI drivers. It defines common configuration flags, the AMD ACP PCI device ID, extern declarations for ACPI machine tables, and `struct config_entry`, the DMI/device table shape used by `acp-config.c` to choose between SOF and legacy machine paths.

The header is intentionally small but sits on a key policy boundary: PCI and SOF drivers call `snd_amd_acp_find_config()` from `acp-config.c`, which uses the flags and table type declared here to decide whether a given system should bind a SOF driver, a legacy driver, DMIC-only mode, SoundWire machines, or no driver in that lane.

## Important APIs, types, and constants
Important constants:

- `FLAG_AMD_SOF`, `FLAG_AMD_SOF_ONLY_DMIC`, `FLAG_AMD_LEGACY`, and `FLAG_AMD_LEGACY_ONLY_DMIC` are bit flags used as configuration outcomes and quirks. They are defined with `BIT(n)` and therefore depend on Linux bit helpers being available through included headers.
- `ACP_PCI_DEV_ID` is `0x15E2`, the common AMD ACP PCI device ID used by the configuration lookup and by related PCI drivers.

Extern machine arrays:

- `snd_soc_acpi_amd_sof_machines`
- `snd_soc_acpi_amd_rmb_sof_machines`
- `snd_soc_acpi_amd_vangogh_sof_machines`
- `snd_soc_acpi_amd_acp63_sof_machines`
- `snd_soc_acpi_amd_acp63_sdw_machines`
- `snd_soc_acpi_amd_acp63_sof_sdw_machines`
- `snd_soc_acpi_amd_acp70_sof_machines`
- `snd_soc_acpi_amd_acp70_sdw_machines`
- `snd_soc_acpi_amd_acp70_sof_sdw_machines`

These arrays are consumed by platform/SOF matching code to locate `struct snd_soc_acpi_mach` descriptors.

`struct config_entry` contains `u32 flags`, `u16 device`, and `const struct dmi_system_id *dmi_table`. `acp-config.c` instantiates arrays of this type to match PCI device IDs and DMI systems.

## Control flow
The header itself has no executable control flow. The main flow enabled by it is:

1. ACP/SOF PCI code includes this header and calls `snd_amd_acp_find_config(pci)`.
2. `acp-config.c` checks PCI revision and either reads `acp-audio-config-flag` from ACPI for ACP 7.0+ or scans `config_entry` DMI rows for older platforms.
3. The returned flag controls whether a driver continues probing or defers to another lane. For example, `ps/pci-ps.c` returns `-ENODEV` when a nonzero config flag is defined, allowing the selected SOF/legacy path to own the hardware.
4. Machine table externs are used by SOF and ACP machine-selection code to bind the right topology/driver for ACPI IDs and SoundWire links.

## State and persistence behavior
The header stores no state. It declares static configuration categories and external machine table symbols. The stateful part lives in `acp-config.c`, where `acp_quirk_data` stores the selected flag for machine table private data. The outcome depends on platform firmware data: PCI revision, ACPI properties, and DMI strings.

## Dependencies and integration points
The header includes `<sound/soc-acpi.h>` for `struct snd_soc_acpi_mach`. It also uses `struct dmi_system_id` in `struct config_entry`; the concrete users include Linux DMI headers before instantiating tables. Integration points found in this tree include:

- `sound/soc/amd/acp-config.c`, which defines `snd_amd_acp_find_config()` and several machine arrays.
- AMD ACP legacy/common PCI code under `sound/soc/amd/acp/`.
- Pink Sardine PCI code `sound/soc/amd/ps/pci-ps.c`.
- SOF AMD PCI drivers under `sound/soc/sof/amd/`.
- ACP63/ACP70 ACPI match files that define machine tables declared here.

## Risks and edge cases
Configuration flags decide driver ownership. A wrong flag can bind the wrong audio stack, suppress the intended PCI driver, or expose only DMIC when SoundWire/SOF support should be active. DMI matching is brittle because vendor/product/version strings must exactly match firmware. For ACP 7.0+ systems, ACPI `acp-audio-config-flag` is authoritative except for the explicit ASUS override in `acp-config.c`; missing or bad firmware properties can alter probe behavior.

The shared `ACP_PCI_DEV_ID` constant also means unrelated ACP generations pass through the same top-level matching path, so revision checks in consumers remain important.

## Test signals
Good validation includes:

- Build tests for AMD ASoC and SOF configurations that include this header.
- Boot/probe logs on systems in the DMI table and on ACP7.x systems with ACPI `acp-audio-config-flag`.
- Confirmation that exactly the intended PCI/SOF/legacy driver binds and that alternative drivers return `-ENODEV`.
- ALSA card enumeration and topology loading for the selected machine table.
- DMI/ACPI regression tests when adding a platform quirk or new machine array declaration.
