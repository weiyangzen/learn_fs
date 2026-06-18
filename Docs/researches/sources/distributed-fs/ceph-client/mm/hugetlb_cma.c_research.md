# `sources/distributed-fs/ceph-client/mm/hugetlb_cma.c`

## Purpose
`hugetlb_cma.c` provides the HugeTLB-specific CMA backend used primarily for gigantic huge pages. It parses `hugetlb_cma=` and `hugetlb_cma_only=` boot parameters, reserves per-node or distributed CMA regions early in boot, allocates/free frozen compound folios from those regions, and exposes policy helpers used by the core hugetlb allocator.

## Important APIs, Types, And Functions
- Static state: `hugetlb_cma[MAX_NUMNODES]`, `hugetlb_cma_size_in_node[]`, `hugetlb_cma_only`, and `hugetlb_cma_size`.
- Runtime allocation: `hugetlb_cma_alloc_frozen_folio()` tries the requested node first, then allowed nodes unless `__GFP_THISNODE` is set; successful folios are tagged with `folio_set_hugetlb_cma()`.
- Runtime free: `hugetlb_cma_free_frozen_folio()` releases CMA-backed frozen folios with `cma_release_frozen()`.
- Boot allocation: `hugetlb_cma_alloc_bootmem()` reserves early CMA chunks for gigantic boot pages, can fall back across `hugetlb_bootmem_nodes`, and records `HUGE_BOOTMEM_CMA` and the `struct cma *` in `struct huge_bootmem_page`.
- Parameter parsing: `cmdline_parse_hugetlb_cma()` supports total-size syntax and node-specific `node:size[,node:size]` syntax; `cmdline_parse_hugetlb_cma_only()` parses a boolean.
- Reservation setup: `hugetlb_cma_reserve()` validates architecture support, minimum region size, node validity, and then calls `cma_declare_contiguous_multi()` for each selected node.
- Policy helpers: `hugetlb_cma_exclusive_alloc()`, `hugetlb_cma_total_size()`, `hugetlb_cma_validate_params()`, and `hugetlb_early_cma()`.
- Architecture hook: weak `arch_hugetlb_cma_order()` returns 0 unless an architecture provides the gigantic CMA alignment/order.

## Control Flow
`early_param("hugetlb_cma", ...)` parses requested CMA size before normal init. A single size is stored in `hugetlb_cma_size`; node-specific entries accumulate into both per-node and total sizes. `hugetlb_cma_only=` is parsed as a boolean and later invalidated if no CMA size was requested.

During early memory setup, `hugetlb_cma_reserve()` returns immediately if no size was requested or the architecture does not provide a CMA order. It warns if the order is not truly gigantic, builds the bootmem node mask, drops invalid node-specific requests, validates each region is at least one huge CMA allocation unit, computes a per-node size for non-specific requests, and declares named CMA areas such as `hugetlb0`. If all declarations fail, `hugetlb_cma_size` is reset to zero so later allocation paths know CMA is unavailable.

At hugetlb boot allocation time, `hugetlb_early_cma()` returns true for gigantic hstates when the architecture lacks regular huge bootmem allocation and `hugetlb_cma_only` is active. `hugetlb_cma_alloc_bootmem()` then reserves from the node's CMA area, optionally falling back to another bootmem node, and annotates the bootmem record so later conversion initializes CMA pageblocks and later frees use the CMA path.

At runtime, `hugetlb_cma_alloc_frozen_folio()` only participates if `hugetlb_cma_size` is nonzero. It allocates a frozen compound page from the requested node's CMA area, then falls back across the supplied nodemask when allowed. `hugetlb.c` tries this path for gigantic allocations before falling back to contiguous allocation unless `hugetlb_cma_only` forbids fallback.

## State And Persistence Behavior
CMA regions are declared during boot and persist for the life of the kernel in `hugetlb_cma[]`. `hugetlb_cma_size` doubles as both requested-size accounting and a runtime availability flag. CMA-backed boot pages carry `HUGE_BOOTMEM_CMA` and a CMA pointer until gathered by `hugetlb.c`; runtime folios carry the `hugetlb_cma` folio flag so `free_huge_folio()` returns them to CMA instead of the buddy allocator.

## Dependencies And Integration Points
This file depends on CMA allocation APIs (`cma_declare_contiguous_multi()`, `cma_alloc_frozen_compound()`, `cma_release_frozen()`, `cma_reserve_early()`), memblock/boot node discovery through `hugetlb_bootmem_nodes`, architecture setup hooks, and core HugeTLB hstate helpers. `hugetlb.c` consumes its allocation, free, size, exclusivity, parameter validation, and early-CMA predicates. `hugetlb_internal.h` and `hugetlb_cma.h` provide the declarations and fallback stubs.

## Risks
- `hugetlb_cma_only` changes allocation semantics by preventing fallback to `alloc_contig_frozen_pages()` for gigantic pages; incorrect validation could leave systems unable to allocate huge pages.
- Node-specific parsing mutates total size as invalid nodes are discovered; tests should verify mixed valid/invalid node lists do not overstate available CMA.
- The architecture-provided CMA order is critical. If too small or zero, reservations are rejected or warned because gigantic huge page assumptions break.
- Runtime allocation fallback across `nodemask` must respect `__GFP_THISNODE`; violating this would break node-specific pool semantics.
- Early CMA boot records must be marked so later bootmem conversion initializes CMA pageblocks and later frees use CMA release.

## Test Signals
- Boot with total and node-specific `hugetlb_cma=` values and verify logs show expected per-node reservations and invalid-node warnings.
- Boot with `hugetlb_cma_only=true` with and without a valid CMA size and verify `hugetlb_cma_validate_params()` disables exclusivity when no CMA exists.
- Allocate and free gigantic huge pages and confirm CMA-backed folios carry the CMA flag and are released through `cma_release_frozen()`.
- Test `__GFP_THISNODE` and nodemask-constrained allocation for node-local behavior.
- On architectures without `arch_hugetlb_cma_order()`, verify the warning and zero effective CMA availability.
