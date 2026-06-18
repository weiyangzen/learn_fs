# `sources/distributed-fs/ceph-client/mm/hugetlb_cma.h`

## Purpose
`hugetlb_cma.h` is the internal interface between core HugeTLB code and the optional CMA backend. It declares the real CMA helpers when `CONFIG_CMA` is enabled and provides no-op or false/NULL/zero inline stubs when CMA is disabled, allowing `hugetlb.c` to call the same API regardless of configuration.

## Important APIs, Types, And Functions
- Allocation/free declarations under `CONFIG_CMA`: `hugetlb_cma_alloc_frozen_folio()`, `hugetlb_cma_free_frozen_folio()`, and `hugetlb_cma_alloc_bootmem()`.
- Policy/query declarations: `hugetlb_cma_exclusive_alloc()`, `hugetlb_cma_total_size()`, `hugetlb_cma_validate_params()`, and `hugetlb_early_cma()`.
- Non-CMA stubs return safe defaults: allocation functions return `NULL`, `hugetlb_cma_exclusive_alloc()` and `hugetlb_early_cma()` return `false`, `hugetlb_cma_total_size()` returns `0`, and free/validate functions do nothing.

## Control Flow
The header itself has no dynamic control flow. Preprocessor selection determines whether callers link to `hugetlb_cma.c` or compile inline fallback behavior. In non-CMA builds, `hugetlb.c` naturally falls back to non-CMA allocation paths because the CMA allocation helper returns `NULL` and the exclusive-allocation predicate is false.

## State And Persistence Behavior
The header defines no state. It controls visibility of state owned by `hugetlb_cma.c` when CMA is enabled and makes that state appear absent when CMA is disabled.

## Dependencies And Integration Points
The API uses `struct folio`, `struct hstate`, `struct huge_bootmem_page`, `gfp_t`, and `nodemask_t` from core mm/HugeTLB headers. It is included by `hugetlb.c` and `hugetlb_cma.c`.

## Risks
- Stub behavior must stay semantically aligned with `hugetlb.c` expectations. A non-CMA build relies on `NULL` allocation and `false` exclusivity to preserve fallback behavior.
- Any new CMA helper added in `hugetlb_cma.c` should also get a non-CMA stub here, otherwise configuration-specific build failures or `#ifdef` leakage will occur.
- The include guard uses `_LINUX_HUGETLB_CMA_H`; conflicting names would cause missing prototypes in internal mm builds.

## Test Signals
- Build both `CONFIG_CMA=y` and `CONFIG_CMA=n` kernels.
- In non-CMA builds, verify gigantic allocation either uses architecture-supported non-CMA paths or fails cleanly without unresolved symbols.
- In CMA builds, verify callers link to real implementations and boot parameter validation is active.
