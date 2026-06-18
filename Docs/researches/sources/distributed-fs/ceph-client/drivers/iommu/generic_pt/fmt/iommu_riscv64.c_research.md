# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/iommu_riscv64.c

## Purpose

`iommu_riscv64.c` instantiates the Generic PT IOMMU template for RISC-V 64-bit Sv39/Sv48/Sv57 page tables.

## Important APIs, Types, and Functions

- `#define PT_FMT riscv` and `#define PT_FMT_VARIANT 64`: select the RISC-V 64 format.
- `PT_SUPPORTED_FEATURES`: enables sign extension, RISC-V Svnapot 64 KiB contiguous mappings, and DMA-incoherent handling.
- Inclusion of `iommu_template.h`: generates RISC-V namespaced IOMMU page-table functions.

## Control Flow

Compilation expands template code with RISC-V format callbacks. Runtime control flow is in generated map/unmap/init paths from `iommu_pt.h` and descriptor logic from `riscv.h`.

## State and Persistence Behavior

State lives in generated `pt_iommu_riscv_64` objects and RISC-V PTE memory, with optional sign-extended address ranges and Svnapot contiguous entries.

## Dependencies and Integration Points

It integrates with RISC-V IOMMU drivers that need Generic PT roots and with KUnit format configurations for Sv39/Sv48/Sv57.

## Risks and Edge Cases

Svnapot contiguous entries are only valid at level 0 and require feature gating. DMA-incoherent feature use requires cache-maintenance support through the generic template.

## Test Signals

Run RISC-V Generic PT KUnit for Sv39, Sv48, Sv57, with and without Svnapot, including sign-extension upper-range mapping tests.
