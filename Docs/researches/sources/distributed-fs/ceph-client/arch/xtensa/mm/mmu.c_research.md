# sources/distributed-fs/ceph-client/arch/xtensa/mm/mmu.c

Purpose: Initializes Xtensa MMU state, ASID caches, highmem/fixmap page tables, PKMAP page table, and KIO TLB mappings.

Important APIs, types, and functions: per-CPU `asid_cache`, `init_pmd()`, `fixedrange_init()`, `paging_init()`, `init_mmu()`, and `init_kio()`.

Control flow: Highmem builds allocate low-memory PTE pages for fixmap and pkmap PMDs, clear PTEs, and install PMD entries. `init_mmu()` resets TLBCFG where applicable, initializes KIO, flushes all local TLBs, initializes RASID to first user ASID, and sets PTEVADDR. `init_kio()` writes cached and bypass KIO mappings for spanning-way PTP MMU when DT may update physical base.

State and persistence: Per-CPU ASID cache starts at `ASID_USER_FIRST`; page tables are allocated by memblock; special MMU registers and TLB entries are initialized.

Dependencies and integration: Called from early `init_arch()` and secondary CPU bring-up; depends on TLB helpers, highmem, fixed map constants, DT-derived `xtensa_kio_paddr`, and `initialize_mmu` register helpers.

Risks: Early memblock PTE allocation failure panics; KIO mapping offsets are architecture-specific; failing to reset RASID/PTEVADDR leaves undefined MMU state; highmem layout must avoid temporary mapping overlap.

Test signals: MMU boot on primary and secondary CPUs, highmem/fixmap use, KIO device access, ASID rollover/context tests, and DT KIO base override.
