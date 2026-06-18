# sources/distributed-fs/orangefs/src/io/description/pvfs-request.c

Purpose: implements the public PVFS request/datatype construction API and exposes elementary datatypes such as `PVFS_BYTE`, `PVFS_INT`, and `PVFS_DOUBLE`.

Important APIs/functions: `PVFS_Request_contiguous()`, `PVFS_Request_vector()`, `PVFS_Request_hvector()`, `PVFS_Request_indexed()`, `PVFS_Request_hindexed()`, `PVFS_Request_struct()`, and `PVFS_Request_resized()` build `PINT_Request` graphs. Query helpers include `PVFS_Request_extent()`, `PVFS_Request_size()`, `PVFS_Request_lb()`, `PVFS_Request_ub()`, and `PVFS_Address()`. `PVFS_Request_commit()` delegates packing to `PINT_request_commit()`, and `PVFS_Request_free()` releases dynamic request graphs.

Control flow: `PINT_subreq()` initializes a datatype node around an old request, computes bounds, aggregate bytes, nesting, and an estimated `num_contig_chunks`, and increments the referenced old request. Indexed/struct constructors build `sreq` chains in reverse order. `PINT_reqstats()` folds sequence-chain stats and de-duplicates shared `ereq` nesting contributions. Commit allocates one contiguous array when nested size is positive, packs the request, and returns the packed region through the caller's pointer.

State and persistence: elementary requests are static globals with `refcount = -1` and are never freed. Dynamic request trees use refcounts and heap allocation. Packed requests use one heap region and `committed < 0`.

Dependencies/integration: relies on `pint-request.h` internals while presenting `pvfs2-request.h` API. Flow setup expects committed or uncommitted `PINT_Request` objects with accurate aggregate size and depth.

Risks: constructors largely skip malloc failure checks after the first allocation path; `PVFS_Request_commit()` sets `*reqp = NULL` for zero-nested requests, which may surprise callers; `PVFS_Request_free()` manually walks `sreq` chains and could mishandle non-tree sharing outside the expected graph; C `long` and `long double` sizes are hard-coded as 4 and 8 bytes here. Test signals should cover all constructor families, shared subrequests, refcounts, negative stride vectors, resized lower/upper bounds, commit/free cycles, and static datatype free no-ops.
