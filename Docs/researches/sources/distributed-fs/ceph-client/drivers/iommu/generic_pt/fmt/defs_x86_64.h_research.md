# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_x86_64.h

## Purpose

`defs_x86_64.h` declares x86-64 Generic PT wrappers for first-stage/x86-style page tables, including address types, write attributes, table containers, configuration, and hardware-info output.

## Important APIs, Types, and Functions

- `pt_vaddr_t` and `pt_oaddr_t`: both 64-bit.
- `struct x86_64_pt_write_attrs`: descriptor bits used during entry installation.
- `struct pt_x86_64`: embeds `pt_common`.
- `struct pt_iommu_x86_64`: generated IOMMU table container.
- `struct pt_iommu_x86_64_cfg`: common hardware limits and `top_level`.
- `struct pt_iommu_x86_64_hw_info`: GCR3/root pointer and number of levels.

## Control Flow

`x86_64.h` uses these definitions to generate format callbacks, while wrapper sources expose `pt_iommu_x86_64_init` and hardware-info helpers.

## State and Persistence Behavior

The generated table object persists in caller-owned memory. `top_level` controls the initial root depth and hardware-info output.

## Dependencies and Integration Points

It integrates with Intel/AMD IOMMU code needing x86-compatible page tables and the Generic PT common ABI.

## Risks and Edge Cases

The same format is used for multiple hardware contexts with different sign-extension and encryption semantics, so callers must set feature flags and top levels correctly.

## Test Signals

KUnit should cover 4- and 5-level sign-extended x86, plus non-sign-extended AMD-style configurations, validating layout and hardware-info fields.
