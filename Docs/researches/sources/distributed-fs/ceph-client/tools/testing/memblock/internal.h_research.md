<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/internal.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/internal.h

## Purpose

`internal.h` supplies minimal `mm/internal.h`-style definitions needed to compile kernel `mm/memblock.c` in the user-space simulator. It replaces unrelated MM behavior with stubs while preserving the symbols memblock expects.

## Important APIs, Types, and Functions

It optionally enables `memblock_debug`, defines `pr_warn_ratelimited()` as `printf`, defines `K(x)`, declares `mirrored_kernelcore`, stubs `struct page`, `page_address()`, `virt_to_page()`, `memblock_free_pages()`, `accept_memory()`, `deferred_pages_enabled()`, `kasan_reset_tag()`, `__is_kernel()`, `init_deferred_page()`, and `__SetPageReserved()`. It declares `free_reserved_area()` and `free_reserved_page()` for simulator linkage.

## Control Flow

Most functions are no-ops or call `BUG()` for paths the simulator should not exercise. `for_each_valid_pfn` is reduced to a simple numeric loop. These definitions let memblock code compile while making accidental page-allocator paths obvious.

## State and Persistence Behavior

State is limited to global booleans such as `mirrored_kernelcore` and optional `memblock_debug`. It does not persist memory; real test memory state is managed by common test helpers and the memblock arrays.

## Dependencies and Integration Points

The header integrates kernel memblock implementation with user-space tests. It depends on simulator-provided `PAGE_SHIFT`, `BUG`, `printf`, `phys_addr_t`, and related kernel types from included tool headers.

## Risks and Edge Cases

The file defines `for_each_valid_pfn` twice, which is harmless only because the definitions are equivalent. BUG stubs are useful guardrails but can abort tests if new memblock paths legitimately need page conversion. No-op memory acceptance and deferred-page behavior mean those kernel paths are not functionally tested.

## Test Signals

Successful simulator compilation is the primary signal. Runtime should not hit `BUG()` through `page_address()` or `virt_to_page()`. Enabling `MEMBLOCK_DEBUG=1` should produce memblock debug printing without changing assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/internal.h -->
