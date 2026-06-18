# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_amdv1.h

## Purpose

`defs_amdv1.h` declares the AMDv1-specific Generic PT table containers, configuration, write attributes, and hardware-info structures consumed by `amdv1.h` and external drivers.

## Important APIs, Types, and Functions

- `typedef u64 pt_vaddr_t`, `typedef u64 pt_oaddr_t`: AMDv1 uses 64-bit virtual and output addresses.
- `struct amdv1pt_write_attrs`: descriptor bits passed from protection conversion to PTE installation.
- `struct pt_amdv1`: embeds `struct pt_common`.
- `struct pt_iommu_amdv1`: embeds `struct pt_iommu` plus AMDv1 common state.
- `struct pt_iommu_amdv1_cfg`: common hardware limits and `starting_level`.
- `struct pt_iommu_amdv1_hw_info`: root physical pointer and AMD mode.

## Control Flow

The header supplies type names that `amdv1.h` binds through `#define pt_write_attrs`, `pt_iommu_table`, and container helpers. Drivers pass `pt_iommu_amdv1_cfg` to the generated `pt_iommu_amdv1_init` and receive root/mode information via generated hardware-info APIs.

## State and Persistence Behavior

Runtime state is the embedded `pt_common` and `pt_iommu` inside caller-owned table storage. The configuration is input-only; hardware-info is output-only.

## Dependencies and Integration Points

It integrates with `linux/generic_pt/common.h` and the generated symbols exported from `iommu_amdv1.c`.

## Risks and Edge Cases

The header is small but ABI-sensitive inside the kernel: container layout must match `amdv1.h`, and `starting_level` must agree with the hardware DTE mode expected by callers.

## Test Signals

Compile coverage should validate external users can include the header and call generated init/hw-info functions. KUnit indirectly validates `starting_level` configurations and the root/mode export structure.
