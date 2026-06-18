# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_vtdss.h

## Purpose

`defs_vtdss.h` declares the Intel VT-d second-stage Generic PT type wrappers used by `vtdss.h` and generated IOMMU page-table code.

## Important APIs, Types, and Functions

- `typedef u64 pt_vaddr_t`, `typedef u64 pt_oaddr_t`: 64-bit IOVA/output address types.
- `struct vtdss_pt_write_attrs`: descriptor bits for second-stage entries.
- `struct pt_vtdss`: common second-stage page-table state.
- `struct pt_iommu_vtdss`: generated IOMMU table container.
- `struct pt_iommu_vtdss_cfg`: common hardware limits and `top_level`.
- `struct pt_iommu_vtdss_hw_info`: exported second-stage root pointer and address-width encoding.

## Control Flow

The file provides compile-time names and layouts. `vtdss.h` binds them to Generic PT callback names and `iommu_vtdss.c` exports generated functions.

## State and Persistence Behavior

State lives in the embedded `pt_common` and `pt_iommu` in caller-provided storage. Hardware-info output reflects the current top table pointer and top-level encoding.

## Dependencies and Integration Points

It is part of the internal Generic PT ABI used by Intel IOMMU nested/second-stage support.

## Risks and Edge Cases

The `top_level` setting must match hardware address-width encoding. Mismatched layout between this header and `vtdss.h` would break container conversions.

## Test Signals

KUnit configurations for 3-, 4-, and 5-level second-stage tables validate this header's configuration and hardware-info path.
