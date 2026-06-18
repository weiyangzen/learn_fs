# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/riscv.h

## Purpose

`riscv.h` implements the Generic PT format callbacks for RISC-V page tables, including Sv39/Sv48/Sv57 64-bit roots and optional Svnapot 64 KiB contiguous mappings.

## Important APIs, Types, and Functions

- Format constants for entry size, max VA/OA, granule, table size, top physical mask, and max top level.
- RISC-V PTE bits: V/R/W/X/U/G/A/D/RSW, PPN fields, PBMT, and NAPOT bit.
- `riscvpt_table_pa`, `riscvpt_entry_oa`, `riscvpt_entry_num_contig_lg2`, `riscvpt_contig_count_lg2`.
- `riscvpt_load_entry_raw`: classifies invalid, table, and leaf entries.
- `riscvpt_install_leaf_entry` and `riscvpt_install_table`: write PTEs and table pointers.
- `riscvpt_iommu_set_prot`: converts IOMMU protection flags to RISC-V R/W/X/A/D/U bits.
- `riscvpt_iommu_fmt_init` and `riscvpt_iommu_fmt_hw_info`: choose Sv mode and export root PPN/mode.

## Control Flow

The generated Generic PT mapper calls RISC-V callbacks for descriptor operations. Leaves are valid if any R/W/X bit is set or at level 0. Non-leaf tables are valid entries without R/W/X. Svnapot 64 KiB mappings write a run of level-0 entries with the N bit and 64 KiB PPN encoding.

## State and Persistence Behavior

Translation state is stored in RISC-V PTEs. The format does not implement dirty helper callbacks for Generic PT dirty tracking even though it sets A/D bits for mappings; dirty behavior is descriptor-level, not exported through `read_and_clear_dirty`.

## Dependencies and Integration Points

It depends on `defs_riscv.h`, Generic PT helpers, Linux bitfield/log2 APIs, and RISC-V IOMMU hardware consumers that need `iosatp`-style root fields.

## Risks and Edge Cases

- `riscvpt_install_leaf_entry` has a FIXME asking whether a RISC-V leaf write needs `cmpxchg`.
- Svnapot support is only valid for 64-bit level-0 entries and must be feature-gated.
- Protection conversion rejects mappings with no R/W/X permission; callers must request a supported combination.
- `riscvpt_num_items_lg2` uses `sizeof(u64)` even though the header has a 32-bit conditional type branch.

## Test Signals

Run KUnit across Sv39/Sv48/Sv57, upper sign-extended ranges, Svnapot 64 KiB entries, permission combinations including `IOMMU_NOEXEC`, table-pointer encode/decode, and hardware-info mode values.
