# sources/distributed-fs/ceph-client/drivers/xen/xen-front-pgdir-shbuf.c

## Purpose
`xen-front-pgdir-shbuf.c` is a helper for Xen frontend/backend protocols that share buffers through a page directory containing grant references. It supports buffers allocated locally by the frontend and buffers allocated by the backend.

## Important APIs, types, and functions
Exported APIs are `xen_front_pgdir_shbuf_alloc`, `xen_front_pgdir_shbuf_free`, `xen_front_pgdir_shbuf_get_dir_start`, `xen_front_pgdir_shbuf_map`, and `xen_front_pgdir_shbuf_unmap`. Internal types are `struct xen_page_directory` and `struct xen_front_pgdir_shbuf_ops`. Important helpers compute required grant refs, fill page directories, grant frontend pages, map/unmap backend-provided grant refs, and allocate directory/gref storage.

## Control flow
Allocation chooses backend or local ops from the config, records the Xenbus device and pages, computes grant counts, allocates the gref array and page directory, grants page-directory pages to the other end, optionally grants local buffer pages, and fills the directory. For backend-allocated buffers, later `map` reads grant references from the directory and maps them onto provided pages; `unmap` reverses those mappings. Free ends all grant accesses and frees the directory and gref array.

## State and persistence
The caller-owned `struct xen_front_pgdir_shbuf` stores runtime grants, directory memory, page array, map handles, ops, and Xenbus device pointer. Grant-table state persists only until ended or unmapped; there is no durable storage.

## Dependencies and integration points
It depends on Xen grant tables, Xenbus device IDs, balloon/page helpers, Xen ring protocol directory conventions, and the public `xen-front-pgdir-shbuf.h` interface. It integrates with Xen display and other para-virtual protocols using page-directory shared buffers.

## Risks and test signals
Risks include grant leaks on partial allocation, invalid backend grefs, map/unmap handle mismatches, off-by-one directory chaining, backend ring-order/page-count mismatch, failure paths that do not free grant references, and address conversion assumptions. Test signals include local and backend-allocated buffer setup, multi-page directories, map failure injection, repeated map/unmap/free, backend-provided bad grefs, and protocol-level display/shared-buffer smoke tests.
