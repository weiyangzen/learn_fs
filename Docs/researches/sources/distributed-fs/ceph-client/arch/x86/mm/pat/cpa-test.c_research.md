# sources/distributed-fs/ceph-client/arch/x86/mm/pat/cpa-test.c

## Purpose
This file implements a boot-time/kernel-thread self-test for change-page-attribute (CPA) operations. It randomly changes a software PTE bit over direct-map pages, verifies page-table splitting and attributes, then reverts the changes.

## Important APIs, Types, and Functions
- `pageattr_test()` performs one test pass over random direct-map ranges.
- `print_split()` counts 4 KiB, large, 1 GiB, executable, and missed mappings and validates coverage against `max_pfn_mapped`.
- `do_pageattr_test()` runs the test repeatedly every 30 seconds until failure or stop.
- `start_pageattr_test()` starts the kernel thread via `device_initcall()`.
- The test exercises `change_page_attr_set()`, `change_page_attr_clear()`, and `cpa_set_pages_array()`.

## Control Flow and State
The test allocates a bitmap covering `max_pfn_mapped`, samples `NTEST` random PFNs, limits each range to uniform page protections and unused bitmap entries, then sets `_PAGE_CPA_TEST` through three CPA call styles. It verifies the first PTE has the test bit and was split to 4 KiB level. After all mutations, it clears the bit and verifies reversion. `print` limits detailed split output to the first pass.

## Dependencies and Integration Points
The file depends on direct-map page tables, CPA/cacheflush internals, random number generation, vmalloc, kthreads, and `lookup_address()`. It is only meaningful in debug/test configurations where `_PAGE_CPA_TEST` exists.

## Risks
Because it mutates direct-map attributes, failures indicate serious CPA bugs and trigger warnings. Random selection must avoid overlapping ranges and mixed protections to keep expected results meaningful. The repeated thread can add boot/runtime noise if enabled unintentionally.

## Test Signals
Expected logs start with `CPA self-test:` and eventually `ok.` on the first pass. Failures print bad PTEs, unexpected page levels, coverage mismatches, or reverting errors, followed by `NOT PASSED`.
