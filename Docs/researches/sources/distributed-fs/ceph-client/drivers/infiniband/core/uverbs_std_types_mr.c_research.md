# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_mr.c

## Purpose

`uverbs_std_types_mr.c` implements memory-region operations for the ioctl uverbs ABI: user MR registration, dma-buf MR registration, device-memory MR registration, MR query, MR advice, and MR destroy. It is the main path that exposes user memory and provider memory to RDMA hardware with lkey/rkey results.

## Important APIs, Types, and Functions

- `uverbs_free_mr()` calls `ib_dereg_mr_user()` with provider udata.
- `UVERBS_METHOD_ADVISE_MR` passes SGE lists and advice/flags to provider `advise_mr`.
- `UVERBS_METHOD_DM_MR_REG` validates zero-based access, DM bounds, access flags, and registers an MR over `ib_dm`.
- `UVERBS_METHOD_QUERY_MR` returns lkey, rkey, length, and optional IOVA.
- `UVERBS_METHOD_REG_DMABUF_MR` registers an MR from an external dma-buf fd through provider `reg_user_mr_dmabuf`.
- `UVERBS_METHOD_REG_MR` handles both traditional address-backed user memory and an fd-backed dma-buf mode, plus optional DMAH attachment.
- `uverbs_def_obj_mr[]` registers the object when `dereg_mr` exists.

## Control Flow

Traditional `REG_MR` reads IOVA and length, then enforces exactly one backing mode: `ADDR` without fd offset/fd, or `FD` plus `FD_OFFSET` without `ADDR`. It validates page-offset alignment between IOVA and backing address/offset, optionally resolves a DMAH, validates access flags, and calls either `reg_user_mr` or `reg_user_mr_dmabuf`. On success it initializes MR fields, increments PD and optional DMAH use counts, adds restrack, stores the uobject, finalizes creation, and returns lkey/rkey.

`REG_DMABUF_MR` is a dedicated dma-buf path with offset/length/IOVA/fd attributes. `DM_MR_REG` resolves PD and DM, requires `IB_ZERO_BASED`, checks access flags and offset/length bounds against `dm->length`, calls provider `reg_dm_mr`, increments PD/DM use counts, and returns keys. `ADVISE_MR` resolves a PD, copies an allocated SGE array, and delegates to provider `advise_mr`.

## State and Persistence Behavior

MR state persists as `struct ib_mr` with device, PD, type, optional DM/DMAH, uobject, lkey/rkey, length, IOVA, restrack resource, and dependent use counts. Destroy delegates to `ib_dereg_mr_user()`, which must unwind PD/DM/DMAH references according to MR type.

## Dependencies and Integration Points

The file depends on provider ops `reg_user_mr`, `reg_user_mr_dmabuf`, `reg_dm_mr`, `dereg_mr`, and `advise_mr`; access validation via `ib_check_mr_access`; DM objects from `uverbs_std_types_dm.c`; DMAH objects from `uverbs_std_types_dmah.c`; dma-buf support from provider registration hooks; and restrack.

## Risks and Edge Cases

High-risk areas are memory access flag validation, page-offset alignment, mutually exclusive backing attributes, DM length arithmetic, optional DMAH use-count handling, and provider support differences between traditional and dma-buf registration. Returning keys after finalization means copy-to-user failure can cause create abort paths, so `uverbs_finalize_uobj_create()` and generic bundle cleanup must correctly deregister the hardware object on later failure.

## Test Signals

Test traditional registration, dma-buf registration through both `REG_MR` and `REG_DMABUF_MR`, invalid combinations of `ADDR`/`FD`/`FD_OFFSET`, page-offset mismatches, unsupported access flags, optional DMAH reference accounting, DM MR bounds and `IB_ZERO_BASED` requirement, query outputs, advise SGE array sizing, provider failures after MR allocation, and destroy reference cleanup.
