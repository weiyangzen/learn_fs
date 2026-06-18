# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/ns-thermal.c

## Purpose
Broadcom Northstar thermal driver. It maps a PVT monitor block, ensures temperature-monitor mode is selected, reads raw status, and converts it with thermal-zone slope/offset.

## Important APIs, Types, and Functions
- `ns_thermal_get_temp()` switches `PVTMON_CONTROL0` to `SEL_TEMP_MONITOR` if needed, reads `PVTMON_STATUS`, and returns `slope * val + offset`.
- `ns_thermal_probe()` maps resource 0 with `of_iomap()`, registers OF thermal zone id 0, and stores the mapping in platform data.
- `ns_thermal_remove()` unmaps the manually mapped I/O region.

## Control Flow
Probe maps the OF node's first resource and registers an OF thermal zone. Reads correct the monitor mode if firmware/test code left it in another mode, then report the converted status value. Remove unmaps the resource.

## State and Persistence
State is the MMIO pointer stored as both zone private data and platform driver data. The monitor mode bit persists in hardware and may be rewritten on reads.

## Dependencies and Integration Points
Uses OF address mapping, platform driver core, and thermal OF slope/offset. It is not devm-managed for mapping, so remove must unmap explicitly.

## Risks and Edge Cases
- `WARN_ON(!pvtmon)` emits a warning and fails probe if mapping is absent.
- No hardware validity bit is checked; all status reads are trusted.
- Mode selection is performed during `get_temp()`, so reads can mutate hardware state.

## Test Signals
Tests should cover failed mapping, thermal zone registration failure cleanup, mode-correction write path, and conversion using DT-provided slope/offset.
