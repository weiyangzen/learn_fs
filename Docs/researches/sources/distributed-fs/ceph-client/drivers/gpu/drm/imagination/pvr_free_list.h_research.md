# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_free_list.h

## Purpose
Declares the PowerVR freelist object model and APIs used by ioctl creation, HWRT setup, firmware grow/reconstruct callbacks, and file teardown.

## Important APIs, types, and functions
- `struct pvr_free_list_node` represents one host allocation inserted into a firmware freelist stack.
- `struct pvr_free_list` stores the object refcount, device pointer, userspace stack BO, FW structure object, firmware ID, page accounting, grow policy, memory block list, HWRT list, and GPU address.
- `pvr_free_list_create()`, `pvr_destroy_free_lists_for_file()`, `pvr_free_list_put()`, `pvr_free_list_add_hwrt()`, and `pvr_free_list_remove_hwrt()` provide lifecycle and relationship management.
- `pvr_free_list_lookup()` looks up file handles; `pvr_free_list_lookup_id()` looks up firmware IDs with `kref_get_unless_zero()`.
- `pvr_free_list_process_grow_req()` and `pvr_free_list_process_reconstruct_req()` are firmware-event entry points.

## Control flow
The header has only inline lookup/reference flow. File-handle lookup locks `pvr_file->free_list_handles`, loads the pointer, and takes a normal reference. Firmware-ID lookup locks `pvr_dev->free_list_ids` and avoids resurrecting objects already in release by using `kref_get_unless_zero()`.

## State and persistence
It defines all long-lived freelist state. The lock protects mutable page counters and the memory/HWRT lists; xarrays provide external handles and firmware ID lookup. References persist across HWRT and firmware callback use until `pvr_free_list_put()` reaches zero.

## Dependencies and integration points
Depends on `pvr_device`, Linux `kref`, `list_head`, `mutex`, `xarray`, UAPI create arguments, and Rogue FWIF request structs. It is consumed by HWRT, job/resource teardown, FWCCB processing, and ioctl handlers that create/destroy free lists.

## Risks
Callers must balance lookups with `pvr_free_list_put()`. The header exposes enough struct fields that implementation invariants, especially lock coverage around page counts and lists, can be violated by future callers if not kept private by convention.

## Test signals
Build coverage catches FWIF type drift and lookup signature mismatches. Runtime tests should verify handle lookup, FW ID lookup during concurrent teardown, and paired add/remove of HWRT list nodes.
