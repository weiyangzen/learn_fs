# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bo_list.c

## Purpose
`amdgpu_bo_list.c` implements user-managed buffer-object lists used by AMDGPU command submission. It copies BO list entries from userspace, resolves GEM handles to AMDGPU BO references, orders non-userptr BOs by priority, separates userptr entries, tracks special GDS/GWS/OA resources, stores lists in per-file IDR handles, and frees lists with RCU-safe lifetime management.

## Important APIs, types, and functions
The main APIs are `amdgpu_bo_list_create()`, `amdgpu_bo_list_get()`, `amdgpu_bo_list_put()`, `amdgpu_bo_create_list_entry_array()`, and `amdgpu_bo_list_ioctl()`. Internal helpers are `amdgpu_bo_list_free_rcu()`, `amdgpu_bo_list_free()`, `amdgpu_bo_list_entry_cmp()`, and `amdgpu_bo_list_destroy()`. Constants define max priority, bucket count, and a 128K entry cap.

## Control flow
The ioctl first copies userspace entry data with `amdgpu_bo_create_list_entry_array()`, handling both current ABI entry size and smaller/larger compatible entry sizes. Create builds a flexible `struct amdgpu_bo_list`, looks up each GEM handle in the caller's DRM file, references the BO, rejects userptr BOs from another process, places non-userptr entries from the front and userptr entries from the back, clamps priority, records special-domain objects, traces entries, sorts only the non-userptr prefix by priority, initializes the list mutex, and returns the list. The ioctl then allocates an IDR handle for create, removes and drops a handle for destroy, or atomically replaces a handle for update.

Lookup is RCU-protected: `amdgpu_bo_list_get()` finds the IDR entry and takes a kref unless it is already zero. Release decrements the kref; final free unreferences all BOs and schedules RCU freeing of the flexible allocation after destroying the mutex.

## State and persistence behavior
BO lists are per-DRM-file runtime objects stored in `fpriv->bo_list_handles` under `fpriv->bo_list_lock`. Each list stores referenced BO pointers, optional BO VA/range metadata for command submission, priority, invalidation flags, special resource pointers, `first_userptr`, entry count, a kref, RCU head, and a command-submission mutex. No persistent state exists beyond the file descriptor lifetime.

## Dependencies and integration points
The file depends on DRM GEM handle lookup, AMDGPU BO reference helpers, TTM userptr ownership checks, Linux IDR, RCU, kref, sort, uaccess helpers, tracepoints, and the AMDGPU BO-list UAPI structures. It integrates directly with command submission, which later reserves, validates, and maps the listed BOs.

## Risks and edge cases
Large user-supplied `bo_number` values are capped, but memory pressure from near-limit lists is still significant. Compatibility copying must zero-fill missing fields to avoid uninitialized priorities or handles. Userptr BO ownership is checked against `current->mm`; shared or stale process contexts must be rejected. Destroy silently succeeds for nonexistent IDs. Update must drop the old list only after replacement succeeds. Sorting excludes userptr entries, so code consuming the list must honor `first_userptr`.

## Test signals
Signals include BO list create/update/destroy/get for valid and invalid handles, ABI size compatibility, priority clamping and ordering, userptr same-mm and cross-mm behavior, GDS/GWS/OA detection, near-limit entry counts, concurrent lookup/destroy RCU behavior, and command submission with mixed userptr and non-userptr entries.
