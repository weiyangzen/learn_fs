# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu_private.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu_private.h` is the private MMU page-table base programming interface in the Intel AtomISP CSS driver. It declares `sh_css_mmu_set_page_table_base_index(hrt_data base_index)`, a lower-level setup hook for programming the L1 page-table base after ISP power-up.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_MMU_PRIVATE_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

The intended flow is early CSS/MMU initialization: set the L1 base once, then rely on protection against later modification.

## State and Persistence Behavior

The persistent state is hardware configuration, so ordering relative to power-up and MMU cache invalidation is critical.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include treating an index as a byte address on platforms where `l1_base_is_index` differs, and attempting to reprogram after the hardware protects the base.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 21 lines, 526 bytes.
