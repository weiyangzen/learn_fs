# sources/distributed-fs/ceph-client/sound/soc/amd/acp/amd-sdw-acpi.c

## Purpose
`amd-sdw-acpi.c` provides a small ACPI helper for AMD SoundWire controller discovery. It reads the firmware-reported SoundWire manager bitmap and stores the active link mask in caller-supplied context.

## Important APIs, Types, and Functions
The exported function is `amd_sdw_scan_controller(struct sdw_amd_acpi_info *info)`.

## Control Flow
The helper fetches the ACPI device from `info->handle`, reads `mipi-sdw-manager-list` as a `u32`, counts enabled bits, validates the count against `info->count`, rejects zero-manager systems, logs discovery, and stores the bitmap in `info->link_mask`.

## State and Persistence
The function owns no persistent state. It writes discovery output into the caller's `sdw_amd_acpi_info` object.

## Dependencies and Integration Points
It depends on ACPI fwnode property APIs, bit counting, and SoundWire AMD data structures. It is exported under namespace `SND_AMD_SOUNDWIRE_ACPI` for AMD SoundWire controller/ACPI selection code.

## Risks
Firmware property absence, zero bitmap, or count overflow all return `-EINVAL`; caller code must distinguish unsupported from malformed firmware only through logs. The helper assumes a single `u32` property value.

## Test Signals
Test ACPI devices with no property, zero managers, one/two managers, and a bitmap exceeding caller capacity. Logs should show discovered manager count and link mask consumers should instantiate matching ACPI machine tables.
