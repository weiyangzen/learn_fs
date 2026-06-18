# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/defs_riscv.h

## Purpose

`defs_riscv.h` declares the RISC-V Generic PT format types for 32-bit and 64-bit variants, including entry width, address types, write attributes, table containers, configuration, and hardware-info output.

## Important APIs, Types, and Functions

- `pt_riscv_entry_t`: `u32` under `PT_RISCV_32BIT`, otherwise `u64`.
- `pt_vaddr_t` and `pt_oaddr_t`: RISC-V virtual and output address types.
- `struct riscvpt_write_attrs`: descriptor bits for PTE installation.
- `struct pt_riscv`: common format state.
- `struct pt_iommu_riscv_64`, `pt_iommu_riscv_64_cfg`, `pt_iommu_riscv_64_hw_info`: generated 64-bit IOMMU table ABI.

## Control Flow

`riscv.h` consumes these definitions to select PPN masks and container names, then `iommu_pt.h` generates the exported RISC-V IOMMU operations.

## State and Persistence Behavior

The structures hold in-memory page-table state and generated hardware control values such as root PPN and `iosatp` mode. Configuration fields are consumed during initialization and not persisted separately.

## Dependencies and Integration Points

It integrates with the generic page-table common ABI and RISC-V IOMMU drivers that need Sv39/Sv48/Sv57-compatible root information.

## Risks and Edge Cases

The conditional 32-bit type branch is present even though the listed wrapper instantiates RISC-V 64. Layout and symbol names must remain aligned with `riscv.h` macros.

## Test Signals

Build RISC-V 64 format and KUnit configurations for Sv39, Sv48, and Sv57, including Svnapot-enabled cases, to verify these definitions support generated APIs.
