## sources/distributed-fs/ceph-client/arch/arm/mm/idmap.c

### Purpose
Builds and uses static identity page tables for reboot/reset code that must run with predictable virtual-to-physical mappings while disabling the MMU.

### Important APIs, Types, And Functions
Important globals are `idmap_pgd` and `arch_phys_to_idmap_offset`. Main routines are `init_static_idmap`, `identity_mapping_add`, `idmap_add_pud`, `idmap_add_pmd`, and `setup_mm_for_reboot`.

### Control Flow
Early init allocates a PGD, maps `__idmap_text_start` to `__idmap_text_end` with section/PMD entries, preserving kernel image PMDs under LPAE where needed, and flushes cache to make page tables visible. Reboot setup switches to `idmap_pgd`, flushes branch predictor, and flushes TLBs on ASID-capable systems.

### State, Dependencies, And Integration
State is `idmap_pgd` and physical offset metadata marked `__ro_after_init`. Depends on page table allocation, CPU architecture checks, XIP handling, HWCAP_LPAE, proc-fns `cpu_switch_mm`, and section symbols. Integration points are CPU reset/reboot and low-level idmap text.

### Risks And Test Signals
Risks include incomplete identity range coverage, bad section attributes on ARMv5/XScale, page-table visibility without cache flush, and TLB conflicts from ASID reuse. Test reboot/kexec-like reset paths, LPAE and non-LPAE builds, XIP builds, and CPU reset on hardware.
