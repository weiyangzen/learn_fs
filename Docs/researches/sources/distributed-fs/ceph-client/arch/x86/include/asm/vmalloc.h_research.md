# sources/distributed-fs/ceph-client/arch/x86/include/asm/vmalloc.h

Purpose: Advertises whether x86 can use huge-page mappings for vmalloc/vmap areas.

Important APIs/types/functions: Under `CONFIG_HAVE_ARCH_HUGE_VMAP`, `arch_vmap_pud_supported(pgprot_t prot)` exists on x86-64 and returns whether boot CPU has `X86_FEATURE_GBPAGES`; `arch_vmap_pmd_supported(pgprot_t prot)` returns whether boot CPU has `X86_FEATURE_PSE`.

Control flow: Generic vmalloc/vmap code calls these hooks before using PUD- or PMD-sized mappings.

State and persistence: No local state. It reads boot CPU feature state.

Dependencies and integration points: Depends on `asm/cpufeature.h`, `asm/page.h`, and `asm/pgtable_areas.h`; integrates with vmalloc mapping creation and TLB/page-table code.

Risks: Returning true without hardware support would create invalid page tables. Returning false loses performance but is safer. The `prot` argument is currently unused, so future protection-specific constraints must be added carefully.

Test signals: Huge-vmap boot tests, vmalloc stress tests, page-table validation, and CPU-feature matrix builds.
