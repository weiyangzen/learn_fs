# sources/distributed-fs/ceph-client/include/xen/xen-front-pgdir-shbuf.h

## Purpose
`xen-front-pgdir-shbuf.h` declares a frontend helper for sharing buffers with a Xen backend through a page-directory grant-reference scheme, supporting frontend-owned buffers and backend-allocated buffers.

## Important APIs, Types, and Functions
Core types are `struct xen_front_pgdir_shbuf` and `struct xen_front_pgdir_shbuf_cfg`. Public helpers are `xen_front_pgdir_shbuf_alloc()`, `xen_front_pgdir_shbuf_get_dir_start()`, `xen_front_pgdir_shbuf_map()`, `xen_front_pgdir_shbuf_unmap()`, and `xen_front_pgdir_shbuf_free()`.

## Control Flow
Callers prepare a config with Xenbus device, page count, optional frontend pages, buffer object, and backend-allocation mode. Allocation creates grant references and page-directory storage. The frontend publishes the directory grant start to the backend, maps backend-provided pages when needed, then unmaps and frees grants/resources during teardown.

## State and Persistence Behavior
`struct xen_front_pgdir_shbuf` tracks grant refs, directory bytes, shared pages, Xenbus device, mode-specific ops, and backend map handles. State persists for the shared buffer lifetime and is released by `free()`.

## Dependencies and Integration Points
It depends on Linux kernel types and Xen grant-table APIs. It integrates frontend drivers needing bulk shared memory with Xenbus negotiation and backend grant mapping.

## Risks and Test Signals
Risks include leaked grant references, mismatched frontend/backend allocation mode, directory layout disagreement, map-handle leaks, and freeing pages while a backend still maps them. Test signals include allocation/map/unmap/free cycles, backend-allocated and frontend-allocated modes, grant-table exhaustion, and Xenbus disconnect cleanup.
