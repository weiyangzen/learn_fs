# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-acpi-mach.c

## Purpose
`amd-acpi-mach.c` provides non-SoundWire ACP ACPI machine match tables for Renoir, Rembrandt, ACP63, and ACP70 legacy ACP configurations.

## Important APIs, Types, and Functions
It exports `snd_soc_acpi_amd_acp_machines[]`, `snd_soc_acpi_amd_rmb_acp_machines[]`, `snd_soc_acpi_amd_acp63_acp_machines[]`, and `snd_soc_acpi_amd_acp70_acp_machines[]`. It also defines codec-list quirk descriptors for RT1019 and MAX98360A amplifiers.

## Control Flow
ACPI machine selection code scans the revision-appropriate exported array. Entries match primary codec/device IDs and optional secondary codec lists through `snd_soc_acpi_codec_list`, then instantiate the named machine driver such as `acp3xalc56821019`, `rembrandt-acp`, `acp63-acp`, or `acp70-acp`.

## State and Persistence
Only static table data is present. The tables are exported for other modules and remain constant for module lifetime.

## Dependencies and Integration Points
The file depends on `sound/soc-acpi.h` and the platform/machine drivers named in `.drv_name`. `acp-pci.c` points `chip->machines` at these arrays based on PCI revision.

## Risks
Overlapping IDs such as `RTL5682` rely on codec-list quirks to distinguish amplifier combinations. A wrong `drv_name` breaks platform-driver binding. New ACPI IDs need matching board data in machine drivers, not just table entries.

## Test Signals
Boot ACPI matching for Renoir/Rembrandt/ACP63/ACP70, correct machine driver names, secondary amplifier detection for RT1019/MAX98360A, and fallback termination at empty array entries.
