# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_uapi.c

## Purpose

`uverbs_uapi.c` builds, validates, finalizes, and tears down the runtime uverbs API description for each RDMA device. It merges core object/method definitions and provider-specific definitions into a radix tree, disables unsupported pieces according to provider ops and support callbacks, precomputes ioctl method metadata, builds fast legacy-write dispatch arrays, and makes provider-owned pointers safe during disassociation.

## Important APIs, Types, and Functions

- `uapi_add_elm()` and `uapi_add_get_elm()` allocate radix-tree entries and handle duplicate object/method merge cases.
- `uapi_create_write()` registers legacy write/write_ex commands and marks unsupported legacy commands disabled from `uverbs_cmd_mask`.
- `uapi_merge_method()` and `uapi_merge_obj_tree()` merge declarative object trees from `DECLARE_UVERBS_*` macros.
- `uapi_merge_def()` processes definition streams including chains, object starts, write methods, provider-op requirements, and support callbacks.
- `uapi_finalize_ioctl_method()` computes mandatory-attribute bitmaps, udata presence, destroy attribute bkey, key bitmap length, and bundle sizing.
- `uapi_finalize_disable()` prunes disabled objects/methods/write methods and methods whose mandatory object type is unavailable.
- `uapi_finalize()` constructs `write_methods` and `write_ex_methods` arrays with a default not-supported handler.
- `uverbs_alloc_api()`, `uverbs_destroy_api()`, `uverbs_disassociate_api_pre()`, and `uverbs_disassociate_api()` are the external lifecycle functions.

## Control Flow

API allocation starts with an empty radix tree and driver ID, merges `uverbs_core_api`, then merges `ibdev->driver_def`. Merge operations add object entries, ioctl methods, attributes, and write commands. Capability definitions either continue or mark the current object/method disabled. After merge, `uapi_finalize_disable()` repeatedly scans and removes disabled subtrees and methods whose mandatory object dependencies disappeared. `uapi_finalize()` then scans remaining entries to finalize ioctl metadata and create indexed write dispatch tables.

During provider removal, `uverbs_disassociate_api_pre()` first sets `uverbs_dev->ib_dev` to NULL and nulls handlers for driver methods, then waits for SRCU readers. After hardware object destruction, `uverbs_disassociate_api()` nulls object type attributes and provider enum arrays so stale provider module rodata is not dereferenced.

## State and Persistence Behavior

The runtime API is stored in `struct uverbs_api`: radix tree entries for objects, ioctl methods, write methods, and attributes; driver ID; not-supported method; and legacy write dispatch arrays. It persists for the lifetime of `ib_uverbs_device` and is destroyed in `ib_uverbs_release_dev()`.

## Dependencies and Integration Points

This file consumes all `uverbs_def_obj_*` arrays from the standard type files plus `uverbs_def_write_intf` and provider `ibdev->driver_def`. It provides lookup data for `uverbs_ioctl.c`, `uverbs_main.c` legacy write handling, and device disassociation in `uverbs_main.c`. It depends heavily on key encoding helpers from `rdma_user_ioctl.h` / `uverbs_ioctl.h` and object type classes from `rdma_core`.

## Risks and Edge Cases

Risks include malformed declarative definitions, duplicate attributes, multiple NEW/DESTROY attributes in one ioctl method, driver methods retaining provider text/rodata after disassociation, disabled-object pruning leaving callable methods, and write method arrays with incorrect bounds. The code uses warnings, strict merge failures, repeated prune scans, mandatory object dependency checks, and SRCU synchronization to mitigate these risks.

## Test Signals

Test API allocation for devices with missing provider ops, driver-specific definitions, duplicate/invalid definitions, unsupported legacy `uverbs_cmd_mask` commands, object disabling cascading into methods, ioctl method metadata for mandatory attributes and destroy bkeys, write/write_ex not-supported dispatch, provider disassociation while commands run, and teardown freeing all radix entries and arrays.
