# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pppcielanes.h

## Purpose

This header exposes the PCIe lane-width conversion helpers implemented in `pppcielanes.c` to the PowerPlay hardware manager code.

## Important APIs, Types, and Functions

It declares `encode_pcie_lane_width(uint32_t num_lanes)` and `decode_pcie_lane_width(uint32_t num_lanes)`. The API shape is intentionally minimal: callers provide a raw `uint32_t`, and the helper returns an 8-bit lane encoding or decoded lane count.

## Control Flow and State

The header has no executable logic and no state. It only provides include guards and extern declarations.

## Dependencies and Integration

The declarations rely on fixed-width integer types being available to includers, typically through nearby kernel or ATOM headers. The header is part of the AMDGPU PowerPlay hwmgr layer and allows table parsing, PCIe DPM, or ASIC-specific code to avoid duplicating lane mapping constants.

## Risks and Test Signals

The declarations do not document valid ranges, even though the implementation requires bounded inputs. Compile coverage catches signature drift; runtime coverage must come from consumers parsing PCIe table entries and from any tests that assert expected lane encode/decode values.
