# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bnxt_re/uapi.c

## Purpose

`uapi.c` registers Broadcom-specific RDMA uverbs extensions for the `bnxt_re` driver. It exposes user objects and methods for driver notification, mmap page allocation, CQ/SRQ toggle memory mapping, user doorbell-region allocation/free, and default doorbell discovery. The file is the glue between RDMA core named-ioctl infrastructure, Broadcom UAPI definitions in `rdma/bnxt_re-abi.h`, and internal `bnxt_re` resource/mmap helpers.

## Important APIs, Types, and Functions

- `bnxt_re_search_for_cq()` and `bnxt_re_search_for_srq()` look up driver CQs/SRQs by qplib ID in `rdev->cq_hash` and `rdev->srq_hash`.
- `BNXT_RE_METHOD_NOTIFY_DRV` obtains the calling `bnxt_re_ucontext` and calls `bnxt_re_pacing_alert()` to notify the driver about pacing pressure.
- `BNXT_RE_METHOD_ALLOC_PAGE` creates `BNXT_RE_OBJECT_ALLOC_PAGE` objects for write-combining doorbell pages, DBR BAR pages, and DBR pages, inserts an mmap entry, finalizes the uobject, and returns mmap offset/length/DPI.
- `alloc_page_obj_cleanup()` removes the mmap entry and deallocates a WC DPI when the allocated-page object is destroyed.
- `BNXT_RE_METHOD_GET_TOGGLE_MEM` maps per-CQ or per-SRQ toggle pages by resource ID and returns mmap page, offset, and length.
- `get_toggle_mem_obj_cleanup()` removes the toggle-page mmap entry on object destruction.
- `BNXT_RE_METHOD_DBR_ALLOC` allocates a UC DPI, inserts a user mmap entry for its doorbell, finalizes a `BNXT_RE_OBJECT_DBR`, and returns `struct bnxt_re_db_region` plus mmap offset.
- `bnxt_re_dbr_cleanup()` removes the mmap entry and frees the UC DPI for DBR objects.
- `BNXT_RE_METHOD_GET_DEFAULT_DBR` returns the default DPI/doorbell region from the user's context.
- `bnxt_re_uapi_defs[]` chains the five named object trees into the driver's `ib_device->driver_def`.

## Control Flow

Each handler starts by retrieving the caller's `ib_ucontext`, converting it to `bnxt_re_ucontext`, then reading method attributes through uverbs helpers. Allocation flows create or discover a kernel resource, create a `bnxt_re_user_mmap_entry` with the correct `BNXT_RE_MMAP_*` flag, store the created object in the uobject, call `uverbs_finalize_uobj_create()`, and copy results back to userspace. Destroy methods are declared with `DECLARE_UVERBS_NAMED_METHOD_DESTROY`; RDMA core invokes the object cleanup callbacks to remove mmap entries and release DPI resources. The global definition array is consumed during device registration so RDMA core can route named ioctl calls to these handlers.

## State and Persistence Behavior

The file persists user-visible state through uverbs IDR objects and mmap entries. A WC page allocation may persist a context-owned `uctx->wcdpi` until object cleanup. DBR allocation persists a heap `bnxt_re_dbr_obj`, its UC DPI, and an mmap entry until destroy. Toggle-memory mappings point at CQ/SRQ pages allocated elsewhere and persist as mmap entries, not as owning references to the CQ/SRQ resource itself. Default DBR discovery does not allocate state; it reports fields already stored in the user context.

## Dependencies and Integration Points

The file depends on RDMA uverbs named-ioctl infrastructure, Broadcom ABI constants, `roce_hsi.h`, qplib resource/SP/FP/RCFW helpers, `bnxt_re` device/context definitions, mmap insertion/removal helpers, and RDMA user mmap entry lifetime rules. It integrates with `ib_verbs.c` CQ/SRQ creation, which populates the resource hash tables and toggle pages, with device registration in `main.c`, which installs `bnxt_re_uapi_defs`, and with userspace providers that know the Broadcom-specific allocation and mmap object IDs.

## Risks and Edge Cases

`BNXT_RE_METHOD_ALLOC_PAGE` copies `BNXT_RE_ALLOC_PAGE_DPI` for all allocation types, but `dpi` is assigned only for `BNXT_RE_ALLOC_WC_PAGE`; DBR BAR/page cases can return an uninitialized stack value. CQ/SRQ hash lookup in the toggle-memory path has no visible locking or uverbs object reference acquisition in this file, so resource teardown concurrency must be guaranteed elsewhere or it risks stale pointers to `uctx_cq_page`/`uctx_srq_page`. Several handlers finalize the uobject before all output copies complete; if a late `uverbs_copy_to*()` fails, cleanup/lifetime behavior depends on RDMA core's handling of a finalized object returned with error. The DBR cleanup releases the DPI and mmap entry but does not explicitly `kfree(obj)`, so ownership must be supplied by uverbs object infrastructure or this leaks. WC DPI cleanup keys off `uctx->wcdpi.dbr`; inconsistent partial allocation state could skip deallocation.

## Test Signals

Tests should cover each named method through libibverbs/provider paths: WC page allocation with `db_push` enabled and disabled, DBR BAR/page allocation and returned DPI value, mmap offset/length validity, destroy cleanup and repeated create/destroy cycles, toggle memory lookup for valid/invalid CQ and SRQ IDs, concurrent CQ/SRQ destroy versus toggle mmap requests, DBR allocation/free leak checks, default DBR reporting, notify-driver pacing calls, copy_to/copy_from fault injection after object finalization, and module unload with active or recently destroyed uverbs objects.
