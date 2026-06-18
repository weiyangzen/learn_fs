# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pppcielanes.c

## Purpose

This file provides the small PCIe lane-width codec used by AMD PowerPlay table handling. ATOM/VBIOS power tables encode lane counts as compact numeric fields, while driver-facing code often needs actual lane counts such as 1, 2, 4, 8, or 16.

## Important APIs, Types, and Functions

`encode_pcie_lane_width(uint32_t num_lanes)` indexes `pp_r600_encode_lanes` and maps a physical lane count to a BIOS lane code. `decode_pcie_lane_width(uint32_t num_lanes)` indexes `pp_r600_decoded_lanes` and maps an encoded value back to a lane count. The tables treat unsupported widths as `0`; decode slot `0` maps to 16 lanes, matching the historical R600 encoding convention.

## Control Flow and State

Both exported functions are pure table lookups with no branching, allocation, hardware access, locking, or persistent state. All state is immutable static const data in the translation unit.

## Dependencies and Integration

The file includes Linux integer types, ATOM BIOS headers, and `pppcielanes.h`. It integrates with PowerPlay table parsers and ASIC hwmgr code that need to translate between VBIOS PCIe records and internal PCIe state descriptions.

## Risks and Test Signals

There are no bounds checks on either index. Callers must only pass `num_lanes <= 16` to encode and encoded values within the 8-entry decode table. Invalid input can read past static arrays in kernel context. Test signals are narrow: unit-style checks for known lane mappings, boot-time parsing of VBIOS PCIe tables, and runtime PCIe DPM state reporting.
