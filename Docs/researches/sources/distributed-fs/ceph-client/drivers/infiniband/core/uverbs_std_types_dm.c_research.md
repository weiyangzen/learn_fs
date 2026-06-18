# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dm.c

## Purpose

`uverbs_std_types_dm.c` implements device memory (DM) allocation and free through ioctl uverbs. Device memory is provider-owned memory that can later back device-memory memory regions.

## Important APIs, Types, and Functions

- `uverbs_free_dm()` rejects busy DM objects and calls provider `dealloc_dm`.
- `UVERBS_METHOD_DM_ALLOC` parses length and alignment, calls provider `alloc_dm`, initializes `ib_dm` fields, attaches it to the uobject, and initializes use count.
- `UVERBS_METHOD_DM_FREE` is a declarative destroy method.
- `uverbs_def_obj_dm[]` exposes the object when `dealloc_dm` is present.

## Control Flow

Create resolves a NEW IDR handle, reads `length` and `alignment`, calls `alloc_dm(ib_dev, ucontext, attr, attrs)`, and on success fills `device`, `length`, `uobject`, `usecnt`, and `uobj->object`. Destroy is handled by the generic framework invoking `uverbs_free_dm()`.

## State and Persistence Behavior

The persistent state is `struct ib_dm` plus provider backing memory and an atomic use count. MR registration can increment `dm->usecnt`; free returns `-EBUSY` until dependent MRs are gone.

## Dependencies and Integration Points

It depends on provider `alloc_dm` and `dealloc_dm`, the current ucontext in `attrs->context`, and MR registration in `uverbs_std_types_mr.c` for `DM_MR_REG`.

## Risks and Edge Cases

Risks include provider alloc support not matching dealloc gating, invalid alignment/length accepted by provider, and use-count leaks from DM-backed MRs. The create handler explicitly checks `alloc_dm`; object definition gates on `dealloc_dm`.

## Test Signals

Test allocation with unsupported provider ops, invalid/edge length and alignment, free while MR references exist, provider dealloc failure, and DM_MR_REG bounds checking against `dm->length`.
