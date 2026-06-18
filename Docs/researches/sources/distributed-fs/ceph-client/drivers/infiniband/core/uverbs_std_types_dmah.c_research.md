# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dmah.c

## Purpose

`uverbs_std_types_dmah.c` implements DMA handle allocation/free for uverbs. A DMAH carries provider-specific DMA placement or TPH-related hints such as CPU ID, memory type, and processing hints that can be associated with later memory registration.

## Important APIs, Types, and Functions

- `uverbs_free_dmah()` rejects busy handles, calls provider `dealloc_dmah`, removes restrack, and frees the object.
- `UVERBS_METHOD_DMAH_ALLOC` allocates `struct ib_dmah`, validates optional CPU ID against the current task's allowed CPUs, parses optional enum memory type and processing hint, initializes restrack, calls provider `alloc_dmah`, attaches the object, and finalizes creation.
- `uverbs_dmah_mem_type[]` defines the accepted enum values for TPH memory type.
- `uverbs_def_obj_dmah[]` exposes the object only when both `alloc_dmah` and `dealloc_dmah` exist.

## Control Flow

Allocation starts with a zeroed driver object. Optional attributes set `cpu_id`, `mem_type`, `ph`, and corresponding `valid_fields` bits. CPU ID outside `current->cpus_ptr` returns `-EPERM`; processing hints with bits outside the low two bits return `-EINVAL`. After provider success, the object is added to restrack and stored in the uobject. Destroy uses the generic IDR destroy method and `uverbs_free_dmah()`.

## State and Persistence Behavior

State is the `ib_dmah`, provider payload, valid-field bitmap, atomic use count, uobject pointer, device pointer, and restrack resource. MRs can hold references by incrementing `dmah->usecnt`.

## Dependencies and Integration Points

The file depends on CPU mask APIs, provider `alloc_dmah`/`dealloc_dmah`, restrack, and MR registration in `uverbs_std_types_mr.c`, where `UVERBS_ATTR_REG_MR_DMA_HANDLE` can attach a DMAH to a user MR.

## Risks and Edge Cases

Risks include accepting CPU IDs outside the process affinity, invalid processing-hint bits, enum extension compatibility, provider allocation failure after restrack initialization, and use-count mismatches with MRs. The code validates these before provider call and cleans up restrack on failure.

## Test Signals

Test optional attribute combinations, CPU affinity rejection, processing-hint high-bit rejection, enum memory-type validation, provider failure cleanup, free while MR uses the handle, and restrack add/delete visibility.
