# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_pcie.h

## Purpose
This header centralizes AMDGPU PCIe link speed and lane-width capability bitmasks. It encodes both platform/chipset support and ASIC hardware support in one 32-bit capability value.

## Important APIs, Types, And Constants
Speed capability masks use low bits for ASIC support (`CAIL_ASIC_PCIE_LINK_SPEED_SUPPORT_GEN1` through `GEN5`, mask `0x0000FFFF`, shift 0) and high bits for driver/platform support (`CAIL_PCIE_LINK_SPEED_SUPPORT_GEN1` through `GEN5`, mask `0xFFFF0000`, shift 16).

Lane-width masks follow the same split: ASIC support uses low bits for x1, x2, x4, x8, x12, x16, and x32; platform/driver support uses the corresponding high bits. Defaults are `AMDGPU_DEFAULT_PCIE_GEN_MASK`, `AMDGPU_DEFAULT_PCIE_MLW_MASK`, and `AMDGPU_DEFAULT_ASIC_PCIE_MLW_MASK`.

## Control Flow
The header has no executable logic. Callers include it to compose default masks, filter VBIOS/firmware/platform capabilities, and pass capability values into helpers or power-management code.

## State And Persistence
No state is stored in this header. The masks are compile-time constants. Runtime state lives in AMDGPU device and power-management structures that store supported PCIe generations and lane widths.

## Dependencies And Integration Points
It is included by many AMDGPU SOC, KMS, device, DPM, SMU, KFD, and legacy power-management files. `amd_pcie_helpers.h` depends directly on these masks to choose requested PCIe generation and lane width. ACPI ATCS PCIe requests in `amd_acpi.h` are a related platform-control interface.

## Risks
The split low/high encoding must stay consistent across all callers. Confusing ASIC bits with platform bits can make the driver request an unsupported generation or lane width. The default generation mask includes platform Gen1/Gen2 and ASIC Gen1/Gen2/Gen3 but not newer Gen4/Gen5, so newer hardware paths need explicit capability population rather than relying only on defaults.

## Test Signals
Compile coverage through all include sites catches macro renames. Unit-style tests around capability construction should verify the low/high masks and shifts. Runtime test signals include DPM-reported PCIe capabilities, link retraining, forced performance levels, suspend/resume link restoration, and KFD interop on systems with different lane widths.
