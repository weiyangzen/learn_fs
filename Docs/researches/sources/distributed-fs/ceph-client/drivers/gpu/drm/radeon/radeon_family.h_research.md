# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_family.h

## Purpose

`radeon_family.h` defines the canonical Radeon chip-family enumeration and packed chip flag bits shared by KMS and non-KMS/PCI-ID code. It is the low-level taxonomy used to select ASIC functions, feature gates, memory limits, display generation behavior, and driver ownership decisions.

## Important APIs, Types, and Functions

- `enum radeon_family` lists ASIC families from `CHIP_R100` through `CHIP_MULLINS`, ending with `CHIP_LAST`.
- `enum radeon_chip_flags` defines bit masks embedded with the family in PCI ID `driver_data`: `RADEON_FAMILY_MASK`, `RADEON_FLAGS_MASK`, and flags such as mobility, IGP, single CRTC, AGP, HierZ, PCIe, new memmap, PCI, IGP GART, and PX.

## Control Flow

The header has no executable control flow. Its values drive switch statements and macro predicates throughout the driver. `radeon_drv.c` reads family values from PCI ID flags for AMDGPU/Radeon arbitration. `radeon_device.c`, `radeon_display.c`, GEM/GART/fence code, and ASIC-specific files compare families to select register layouts, memory masks, DMA behavior, GART defaults, display limits, writeback behavior, and reset paths.

## State and Persistence Behavior

The family and flags are persisted in `rdev->family` and `rdev->flags` after probe decodes PCI ID `driver_data`. The constants are ABI-like internal contracts; their numeric values must remain consistent with PCI ID tables and family-name arrays.

## Dependencies and Integration Points

This header is included by `radeon_drv.h` and transitively by driver entry code. The enum ordering is mirrored by arrays such as `radeon_family_name` in `radeon_device.c` and by many range checks like `family >= CHIP_R600` or `family >= CHIP_BONAIRE`.

## Risks and Edge Cases

- Reordering enum values would break PCI ID driver data, family-name indexing, and generation range checks.
- Adding new families requires updating name arrays, support arbitration, ASIC init tables, register family macros, and feature gates.
- Flag bits share the same integer with the low-family mask; new flags must not overlap `RADEON_FAMILY_MASK`.

## Test Signals

Build-time checks should cover PCI ID table initialization and array bounds. Runtime smoke tests should verify each supported family binds to the correct ASIC hooks, display generation checks, GART defaults, DMA masks, and SI/CIK ownership behavior.
