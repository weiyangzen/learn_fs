# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_pcie_helpers.h

## Purpose
This header provides inline helpers that convert AMDGPU PCIe capability bitmasks into selected PCIe generation and lane-width values for PowerPlay hardware managers.

## Important APIs, Types, And Functions
`is_pcie_gen3_supported()` and `is_pcie_gen2_supported()` test the high platform support bits from `amd_pcie.h`.

`get_pcie_gen_support(uint32_t pcie_link_speed_cap, uint16_t ns_pcie_gen)` returns a `PP_PCIEGen*` value. It first extracts ASIC speed support bits. If the ASIC mask is exactly Gen1, Gen2, or Gen3, it returns that generation. Otherwise it uses system support bits and the requested new-state generation to choose Gen3, fall back to Gen2, or default to Gen1.

`get_pcie_lane_support(uint32_t pcie_lane_width_cap, uint16_t ns_pcie_lanes)` returns the closest supported lane count. Exact single-bit masks map directly to x1, x2, x4, x8, x12, x16, or x32. For multi-bit masks, it searches the standard lane array, keeps the requested width if supported, otherwise searches downward first and upward second.

## Control Flow
Both selection helpers are straight-line decision logic with switch statements and fallback scans. Generation selection prefers exact ASIC-only declarations before considering system capability plus the requested performance state. Lane selection prefers exact single-width declarations, then nearest lower supported width, then nearest higher supported width.

## State And Persistence
The helpers are stateless inline functions. They read passed-in capability masks and return selected values; callers persist the result in power-management state if needed.

## Dependencies And Integration Points
The header includes `amd_pcie.h` and uses `PP_PCIEGen1`, `PP_PCIEGen2`, and `PP_PCIEGen3` from the PowerPlay hardware-manager API. It is included by SMU7, Vega10, Vega12, and Vega20 hardware manager code. It also uses `pr_err()` for invalid lane capability diagnostics, relying on kernel logging availability through include context.

## Risks
`get_pcie_gen_support()` compares the extracted ASIC mask for exact equality to single-generation values. If firmware reports multiple ASIC generation bits, the code falls into the system-capability path instead of selecting the highest ASIC-supported generation directly.

`get_pcie_lane_support()` only understands the seven lane values in its local array. Unsupported requested values are returned unchanged unless they match one of those array entries. The final `if (j > 7)` check is unreachable for a failed upward search ending at `j == 7`, so the intended error log for no valid upward lane width is not emitted.

## Test Signals
Focused tests should cover exact Gen1/Gen2/Gen3 ASIC masks, multi-bit speed masks, requested Gen3 falling back to Gen2, zero lane masks, exact single lane masks, multi-lane masks with requested width supported, fallback to lower width, fallback to higher width, and invalid requested lane counts. Runtime signals are correct DPM tables and stable PCIe link behavior when forcing power/performance states.
