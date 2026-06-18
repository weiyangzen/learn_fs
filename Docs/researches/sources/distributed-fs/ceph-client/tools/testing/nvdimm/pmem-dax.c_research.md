# sources/distributed-fs/ceph-client/tools/testing/nvdimm/pmem-dax.c

## Purpose
`pmem-dax.c` overrides pmem direct-access behavior for the test environment. It adapts `__pmem_direct_access()` so vmalloc-backed fake nvdimm resources can be exposed through DAX paths.

## Important APIs, Types, And Functions
The key function is `long __pmem_direct_access(struct pmem_device *pmem, pgoff_t pgoff, long nr_pages, enum dax_access_mode mode, void **kaddr, unsigned long *pfn)`. It uses `is_bad_pmem()`, `get_nfit_res()`, `vmalloc_to_page()`, `page_to_pfn()`, `PHYS_PFN()`, and pmem fields such as `data_offset`, `phys_addr`, `virt_addr`, `size`, `pfn_pad`, and `bb`.

## Control Flow
The function computes a byte offset from `pgoff` plus pmem data offset, rejects bad blocks with `-EIO`, and then branches on whether the target physical address belongs to an nfit test resource. Synthetic resources return a direct kernel address and a vmalloc-derived PFN, capped to one page. Non-test resources return production-style address/PFN data and either the requested page count when badblocks exist or the remaining good PFN span.

## State And Persistence
No local state persists. The function reads badblock state from the pmem device and resource membership from the nfit test registry.

## Dependencies And Integration Points
It depends on pmem internals, libnvdimm headers, Linux DAX interfaces, and the nfit test lookup API. It is linked into the test `nd_pmem` module alongside real `drivers/nvdimm/pmem.o`.

## Risks
The synthetic path intentionally limits DAX to one page at a time because backing memory is vmalloc-based. Tests that expect multi-page direct mappings over fake resources must account for this. Badblock checks operate before synthetic-resource handling, so injected badblocks still prevent direct access.

## Test Signals
Correct signals are successful namespace/DAX accesses over fake nfit resources, valid `kaddr` values, and PFNs corresponding to vmalloc pages. Error signals include `-EIO` for bad pmem and unexpectedly short direct-access spans.
