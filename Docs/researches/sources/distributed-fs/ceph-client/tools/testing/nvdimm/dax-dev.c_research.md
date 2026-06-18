# sources/distributed-fs/ceph-client/tools/testing/nvdimm/dax-dev.c

## Purpose
`dax-dev.c` overrides `dax_pgoff_to_phys()` for the nvdimm test environment. It maps DAX page offsets through synthetic nfit resources and converts vmalloc-backed test memory to real page frame numbers when needed.

## Important APIs, Types, And Functions
The key function is `phys_addr_t dax_pgoff_to_phys(struct dev_dax *dev_dax, pgoff_t pgoff, unsigned long size)`. It uses `struct dev_dax_range`, `struct range`, `range_len()`, `PHYS_PFN()`, `PFN_PHYS()`, `get_nfit_res()`, `vmalloc_to_page()`, and `page_to_pfn()`.

## Control Flow
The function walks `dev_dax->ranges`, finds the range containing the requested `pgoff`, computes the physical address, and verifies `addr + size - 1` fits in the range. If the address belongs to a synthetic nfit resource, it refuses huge alignment greater than `PAGE_SIZE`, maps the vmalloc address to a page, and returns that PFN as a physical address. Otherwise it returns the computed address. Failure returns `-1` in a `phys_addr_t`.

## State And Persistence
No local state is persisted. The function reads live `dev_dax` range data and synthetic resource registrations managed by the nfit/ndtest modules.

## Dependencies And Integration Points
This file includes the private DAX header from `drivers/dax` and the nfit test lookup interface. It is linked into the test `device_dax` module to adapt production DAX behavior to vmalloc-backed fake persistent memory.

## Risks
Returning `-1` as `phys_addr_t` relies on callers treating it as an invalid physical address. The `addr + size - 1` check can be sensitive to overflow if callers pass extreme sizes. The synthetic-resource path only supports page-sized alignment, limiting coverage for larger-aligned DAX configurations.

## Test Signals
Successful device-dax tests over nfit resources demonstrate correct pgoff-to-vmalloc PFN translation. Failures often appear as invalid PFNs, alignment rejection, or inability to map synthetic DAX ranges.
