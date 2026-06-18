# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acp70-acpi-match.c

## Purpose
`amd-acp70-acpi-match.c` defines ACPI SoundWire machine tables for ACP 7.0/7.1 platforms. It extends ACP63-style layouts with newer Realtek, Cirrus, TI, and SDCA/RT712 VB-specific match cases, and provides both legacy and SOF SoundWire machine entries.

## Important APIs, Types, and Functions
The exported arrays are `snd_soc_acpi_amd_acp70_sdw_machines[]` and `snd_soc_acpi_amd_acp70_sof_sdw_machines[]`. It defines endpoint/address/link tables for RT711/RT1316/RT714, RT722, RT1320, RT721 with TAS2783 amps, RT712 VB, CS42L43/CS42L45, CS35L56, and CS35L63 layouts. One machine entry uses `snd_soc_acpi_amd_sdca_is_device_rt712_vb()` as `machine_check`.

## Control Flow
Runtime ACPI/SoundWire matching scans these tables and instantiates `amd_sdw` or `amd_sof_sdw` when link masks and address descriptors match. The RT712 VB entry adds a machine-check callback that inspects discovered SDCA peripheral quirks before accepting the entry.

## State and Persistence
The file is static table data only. Machine arrays persist for module lifetime.

## Dependencies and Integration Points
It depends on `soc-acpi-amd-sdca-quirks.h`, `sound/soc-acpi.h`, and `mach-config.h`. `drv_name`, topology filenames, and firmware filenames must align with the AMD SoundWire machine drivers and SOF firmware packaging.

## Risks
Because many entries share identical link masks, ordering and machine-check specificity are important. Endpoint numbers document codec-specific functions such as RT721/RT722 DMIC versus amp paths; wrong endpoint counts can create missing or extra DAI links. Conditional namespace import must match the SDCA quirk config.

## Test Signals
Validate ACP70/71 systems for all listed layouts, especially RT1320/RT722 link-order variants, RT712 VB machine-check filtering, RT721 plus TAS2783 speaker aggregation, SOF RT722 topology loading, and generated component strings showing expected amp/mic counts.
