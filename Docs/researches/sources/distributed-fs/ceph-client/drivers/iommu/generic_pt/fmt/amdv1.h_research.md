# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/amdv1.h

## Purpose

`amdv1.h` defines the Generic PT format implementation for AMD IOMMU v1 host page tables. It supplies all format callbacks required by `pt_common.h` and `iommu_pt.h`: descriptor decode/encode, supported page sizes, table installation, protection conversion, dirty handling, and hardware-info extraction.

## Important APIs, Types, and Functions

- Format constants: 64-bit entries, 4 KiB table memory, max VA/OA sizes, top-level range, and top physical mask.
- Descriptor bits: present, dirty, next-level/page-size code, output address, force coherence, I/O read/write.
- `amdv1pt_table_pa`, `amdv1pt_entry_oa`, `amdv1pt_entry_num_contig_lg2`: address and contiguous-size decoding.
- `amdv1pt_possible_sizes`: exposes nearly all power-of-two page sizes while excluding 512 GiB due to a hardware bug.
- `amdv1pt_load_entry_raw`, `amdv1pt_install_leaf_entry`, `amdv1pt_install_table`, `amdv1pt_clear_entries`.
- Dirty helpers: `amdv1pt_entry_is_write_dirty`, `amdv1pt_entry_make_write_clean`, `amdv1pt_entry_make_write_dirty`.
- IOMMU callbacks: `amdv1pt_iommu_set_prot`, `amdv1pt_iommu_fmt_init`, `amdv1pt_iommu_fmt_hw_info`.

## Control Flow

The wrapper source defines `PT_FMT amdv1` and includes this header before `iommu_pt.h`. Generic mapping code calls the format callbacks to create AMDv1 PTEs. Leaf installation writes either one entry for base page size or a run of identical entries for contiguous mappings, using AMD's next-level size encoding. Table installation uses atomic `cmpxchg64` and sets IR/IW on intermediate entries so permissions are controlled by leaves.

## State and Persistence Behavior

The format stores all translation state in AMDv1 PTE words. Dirty state is hardware/software-visible through the `D` bit and may span a contiguous run. Optional SME encryption features set or clear memory-encryption bits in table and leaf addresses.

## Dependencies and Integration Points

It depends on `defs_amdv1.h` for per-table structs, `pt_defs.h`, Linux bitfield helpers, SME memory encryption helpers, and Generic PT's `struct pt_iommu` ABI. It integrates with IOMMUFD dirty tracking and KUnit format configuration.

## Risks and Edge Cases

- Contiguous size encoding is nontrivial and relies on low OA bits; wrong alignment would corrupt the decoded page size.
- 512 GiB pages are deliberately excluded for a hardware bug.
- SME encryption is inferred from table encryption features and `IOMMU_MMIO`, not an explicit higher-level encrypted mapping flag.
- Dirty cleaning clears all entries in a contiguous run and relies on later TLB synchronization.

## Test Signals

KUnit should cover all AMDv1 page sizes except the excluded 512 GiB case, contiguous entry encode/decode, dirty read/clear/set, SME table/leaf encoding, force-coherence bit generation, top mode export, and failure for invalid `starting_level`.
