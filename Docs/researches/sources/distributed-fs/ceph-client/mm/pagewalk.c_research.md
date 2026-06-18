# sources/distributed-fs/ceph-client/mm/pagewalk.c

## Purpose
`pagewalk.c` is the generic page-table walking engine. It walks user, VMA-scoped, mapping-scoped, kernel, debug, and hugetlb ranges through callback tables, optionally installs missing PTEs for internal MM users, and provides `folio_walk_start()` for safely resolving one VMA address to a folio while holding the relevant page-table lock.

## Important APIs, Types, And Functions
- `walk_page_range()`, `walk_page_range_mm_unsafe()`, `walk_page_range_vma()`, `walk_page_range_vma_unsafe()`, and `walk_page_vma()` walk user VMAs.
- `walk_kernel_page_table_range()`, `walk_kernel_page_table_range_lockless()`, and `walk_page_range_debug()` walk page tables not necessarily backed by VMAs.
- `walk_page_mapping()` walks all VMAs that map an address-space index range.
- `walk_pgd_range()`, `walk_p4d_range()`, `walk_pud_range()`, `walk_pmd_range()`, and `walk_pte_range()` implement recursive descent.
- `walk_hugetlb_range()` handles hugetlb VMAs.
- `check_ops_safe()` rejects public callback sets that try to install PTEs.
- `folio_walk_start()` resolves one address to a normal or optional zero folio and leaves `fw->ptl` held until `folio_walk_end()`.

## Control Flow
Range walkers validate arguments and locking expectations, build an `mm_walk`, and iterate VMAs or raw page-table ranges. At each level the walker handles holes through `pte_hole`, invokes the level callback if present, respects `walk->action` values such as `ACTION_AGAIN`, `ACTION_CONTINUE`, and `ACTION_SUBTREE`, splits huge PMD/PUD entries when lower-level callbacks require PTE descent, and allocates missing lower tables only for unsafe internal callers with `install_pte`. Hugetlb VMAs use a separate hstate-sized loop and `hugetlb_walk()`. Kernel/debug walkers set `no_vma`, avoid normal user PTE locking, and rely on caller-provided synchronization. `folio_walk_start()` performs a single-address descent, locks PUD/PMD/PTE huge or table entries, filters through `vm_normal_page*()` and optional zeropage handling, and returns the folio while keeping enough state in `struct folio_walk` to unlock later.

## State And Persistence Behavior
State is transient in `struct mm_walk`, callback private data, and `struct folio_walk`. The file can allocate page-table pages only through internal unsafe `install_pte` use. Otherwise it does not persist data; it takes and releases mmap/VMA/page-table locks and may split huge page-table entries as a side effect when callbacks need lower-level traversal.

## Dependencies And Integration Points
It depends on generic page-table macros, mmap/VMA locking, optional per-VMA locks, hugetlb locking, THP split helpers, `update_mmu_cache()`, kernel TLB/cache expectations, VMA interval trees, address-space reverse mapping, and exported `include/linux/pagewalk.h` callback contracts. It underpins pagemap/smaps, clear_refs, NUMA/mempolicy tools, kernel page-table dumpers, and internal MM code that walks mappings.

## Risks
- Public walkers must not allow arbitrary PTE installation; `check_ops_safe()` is a security and correctness boundary.
- Locking requirements differ for user, VMA, mapping, kernel, and debug walkers; misuse can race page-table teardown.
- Huge entry splitting has side effects and must be avoided when callbacks only want higher-level entries.
- Positive callback returns are caller-defined but internal VMA test positive values mean skip; confusing these can prematurely abort or mask errors.
- `folio_walk_start()` returns a folio without a reference and with a lock held; callers must not use it after `folio_walk_end()` unless they acquired a short-term ref.

## Test Signals
- Walk ranges with holes, folded levels, THP PMD/PUD entries, hugetlb VMAs, PFNMAP VMAs, and kernel page tables.
- Exercise callback combinations: upper-level only, PTE-only, hole callbacks, pre/post VMA, `test_walk`, and internal `install_pte`.
- Verify required mmap/per-VMA locks with lockdep for safe, unsafe, debug, and mapping walkers.
- Use `folio_walk_start()` on normal pages, huge leaves, zeropages, and invalid addresses.
