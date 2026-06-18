# sources/distributed-fs/ceph-client/drivers/iommu/generic_pt/fmt/vtdss.h

## Purpose

`vtdss.h` implements Generic PT callbacks for Intel VT-d second-stage 3-, 4-, and 5-level page tables.

## Important APIs, Types, and Functions

- Format constants: 52-bit output, 57-bit VA, 4 KiB granule/table memory, 64-bit entries, top level up to 4.
- Descriptor bits: R/W, A/D, SNP, output address, and page-size `PS`.
- `vtdss_pt_table_pa`, `vtdss_pt_entry_oa`, `vtdss_pt_can_have_leaf`, `vtdss_pt_load_entry_raw`.
- `vtdss_pt_install_leaf_entry`, `vtdss_pt_install_table`, `vtdss_pt_attr_from_entry`.
- Dirty helpers and software-bit helpers for ignored descriptor bits.
- `vtdss_pt_iommu_set_prot`, `vtdss_pt_iommu_fmt_init`, `vtdss_pt_iommu_fmt_hw_info`.

## Control Flow

Entries with neither R nor W are empty. Level 0 entries are leaves; levels 1 and 2 can be leaves when `PS` is set; higher levels are table-only. Mapping protection sets R/W and optionally SNP for forced coherence. The force-writeable feature rejects read-only mappings for nested-parent domains affected by an erratum.

## State and Persistence Behavior

Translations are stored in second-stage PTEs. Dirty state uses the VT-d D bit and Generic PT can clear or set it atomically. Software bits are stored in ignored descriptor positions for DMA-incoherent table-flush markers.

## Dependencies and Integration Points

The format is consumed by Intel IOMMU nested translation code through generated `pt_iommu_vtdss_*` APIs. It depends on Generic PT common/template headers and Linux bitfield helpers.

## Risks and Edge Cases

- VT-d second-stage has no independent present bit, so descriptor classification depends on R/W bits.
- Force-writeable domains intentionally reject read-only mappings and log a rate-limited erratum message.
- Software-bit allocation must avoid bits with architectural meaning across all entry levels.
- Dirty clearing requires a following IOTLB flush to synchronize hardware writes.

## Test Signals

KUnit should verify 3/4/5-level roots, 4 KiB/2 MiB/1 GiB mappings, dirty read/clear, force-coherence SNP bit, force-writeable rejection, software-bit operations, and hardware-info address-width encoding.
