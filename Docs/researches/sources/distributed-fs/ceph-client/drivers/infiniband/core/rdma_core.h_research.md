# sources/distributed-fs/ceph-client/drivers/infiniband/core/rdma_core.h

## Purpose
`rdma_core.h` is the internal interface for uverbs core object management and runtime API dispatch metadata. It exposes the object lifetime functions implemented in `rdma_core.c` and defines the in-memory representation of ioctl/write method tables used by the uverbs syscall machinery.

## Important APIs, types, and functions
- Object APIs: `uverbs_get_uobject_from_file()`, `uverbs_finalize_object()`, `uobj_destroy()`, `uverbs_destroy_ufile_hw()`, `setup_ufile_idr_uobject()`, and `release_ufile_idr_uobject()`.
- Attribute helpers: `uverbs_output_written()`, `uverbs_get_cleared_udata()`, `uverbs_fill_udata()`, and `uverbs_get_handler_fn()`.
- Runtime API metadata: `struct uverbs_api_ioctl_method`, `struct uverbs_api_write_method`, `struct uverbs_api_attr`, and `struct uverbs_api`.
- Lookup helpers: `uapi_get_object()` and `uapi_get_method()`.
- API lifecycle: `uverbs_alloc_api()`, `uverbs_disassociate_api_pre()`, `uverbs_disassociate_api()`, and `uverbs_destroy_api()`.

## Control flow and behavior
`uapi_get_object()` turns an object ID into a radix-tree object entry, with `UVERBS_IDR_ANY_OBJECT` represented as `ERR_PTR(-ENOMSG)` so wildcard lookups can be handled specially by lookup code. `uapi_get_method()` validates the legacy write command word, checks for unsupported flag bits, chooses normal or extended write method arrays, and returns `-EOPNOTSUPP` for out-of-range command indexes. The method structs hold dispatch function pointers, disabled bits, driver-method flags, mandatory attribute bitmaps, bundle sizing data, and udata/response metadata used later by ioctl validation and handler invocation.

## State, persistence, and dependencies
This header defines no storage of its own, but describes persistent runtime state in `struct uverbs_api`: a radix tree of API object/method/attribute definitions, write method arrays, driver ID, and a reusable unsupported-method descriptor. It depends on Linux `idr`, radix tree infrastructure, uverbs ioctl type definitions, and core RDMA verbs types.

## Integration points
Included by uverbs core implementation, ioctl/write dispatch code, object definition builders, and cleanup/disassociation logic. The extern `uverbs_def_obj_*` declarations tie generated/static uAPI definition arrays into API construction.

## Risks and test signals
Risks are command flag validation drift, mismatched bundle sizing, stale handler pointers during disassociation, and accidental changes to `ERR_PTR(-ENOMSG)` wildcard semantics. Test signals include ioctl parser tests for invalid object IDs and command bits, uAPI construction tests validating radix keys, and hot-unplug tests that exercise API disassociation before and during command dispatch.
