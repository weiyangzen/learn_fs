# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acp63-acpi-match.c

## Purpose
`amd-acp63-acpi-match.c` defines ACPI SoundWire machine tables for ACP 6.3 platforms. It enumerates supported SoundWire address/link layouts and maps them to either legacy `amd_sdw` or SOF `amd_sof_sdw` machine drivers with topology/firmware metadata where needed.

## Important APIs, Types, and Functions
The exported arrays are `snd_soc_acpi_amd_acp63_sof_sdw_machines[]` and `snd_soc_acpi_amd_acp63_sdw_machines[]`. The file defines many `snd_soc_acpi_endpoint`, `snd_soc_acpi_adr_device`, and `snd_soc_acpi_link_adr` tables for Realtek RT711/RT1316/RT714/RT722 and Cirrus CS42L43/CS42L45/CS35L56/CS35L63 combinations.

## Control Flow
There is no runtime function flow in this file. ACPI machine selection code scans the exported arrays, matches `link_mask` and address tables against discovered SoundWire peripherals, and instantiates the named machine driver. Endpoint metadata describes aggregation, group positions, and endpoint numbers consumed by SoundWire utility parsing.

## State and Persistence
All tables are static constant data except exported machine arrays. They persist for module lifetime and do not change at runtime.

## Dependencies and Integration Points
It depends on `sound/soc-acpi.h` and `mach-config.h`. The `drv_name` values must correspond to platform drivers in `acp-sdw-legacy-mach.c` and `acp-sdw-sof-mach.c`; topology and firmware filenames must exist for SOF entries.

## Risks
Address constants are exact hardware IDs; a transposed link/user/instance value can prevent matching or route endpoints incorrectly. Aggregated speaker group positions must align with codec driver channel maps. Table order can matter when multiple entries share link masks.

## Test Signals
Boot-time ACPI matching on each supported ACP63 design, successful machine driver instantiation, generated DAI links for jack/amp/DMIC endpoints, four-speaker aggregation channel mapping, and SOF topology load for the RT711/RT1316/RT714 entry are key signals.
