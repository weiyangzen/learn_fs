# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable.h

Purpose: implements the main x86 page-table API consumed by generic MM: protection transformations, native or paravirt entry setters, entry predicates and flag manipulation, page-table walking helpers, access/dirty/young operations, PTI top-level cloning helpers, swap metadata helpers, protection-key access checks, and safe setter wrappers.

Important APIs, types, and functions: major exports include `pgprot_noncached()`, `pgprot_encrypted/decrypted()`, page-table dump functions, `early_top_pgt`, `__early_make_pgtable()`, `pgd_lock`, `pgd_list`, `pgd_page_get_mm()`, native `set_pte/pmd/pud/p4d/pgd` fallbacks, `pte_*`, `pmd_*`, `pud_*`, `p4d_*`, and `pgd_*` flag/pfn/present/none/bad/same/modify helpers, `lookup_address*()`, `kernel_map/unmap_pages_in_pgd()`, local get-and-clear helpers, access/young/dirty operations such as `ptep_set_access_flags()` and `pmdp_set_access_flags()`, huge get-and-clear, write-protect helpers using cmpxchg, `pmdp_establish()`, `pudp_establish()`, PTI pointer conversion helpers, `clone_pgd_range()`, page-level size helpers, MMU cache no-ops, swap soft-dirty/uffd-wp/exclusive helpers, `pte_flags_pkey()`, `__pte_access_permitted()`, `pfn_modify_allowed()`, zapped-entry checks, SGX memory failure/platform-page hooks, and `set_pte/pmd/pud/p4d/pgd_safe()`.

Control flow: most operations are inline transformations around entry values and page-table memory. Critical updates call page-table check hooks, preserve hardware dirty semantics for shadow stacks, use atomic exchanges where races with hardware or other CPUs matter, and duplicate top-level PTI entries when cloning PGDs.

State and persistence: mutates in-memory page tables, page-table tracking lists, and boot mappings. There is no disk persistence.

Dependencies and integration points: integrates with generic MM, TLB flush code, PTI, PKRU/pkeys, CoCo encryption, KMSAN/debug WX page dumps, paravirt, page-table check, THP, swap, userfaultfd, NUMA balancing, SGX, and L1TF mitigation.

Risks: this is a core MM contract. Flag mistakes can create writable/executable mappings, shadow-stack-invalid PTEs, stale TLBs, incorrect swap metadata, or L1TF exposure. Safe setters must only be used when existing present entries are identical or non-present.

Test signals: x86 MM selftests, fork/exec/mmap/mprotect/munmap, THP split/collapse, swap soft-dirty and uffd-wp tests, PTI enabled/disabled, debug-WX checks, page-table-check, pkeys/PKRU access tests, SGX memory failure, and KVM/Xen paravirt page-table paths.
