# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bo_list.h

## Purpose
`amdgpu_bo_list.h` defines the private BO-list data structures and helper prototypes shared between AMDGPU ioctl handling and command submission. It describes how a list stores BO references, associated VM metadata, priorities, userptr split point, and special resources.

## Important APIs, types, and functions
Important types are `struct amdgpu_bo_list_entry` and `struct amdgpu_bo_list`. Entries hold `bo`, optional `bo_va`, priority, optional HMM range, and a user-invalidation flag. Lists hold RCU/kref lifetime fields, special `gds_obj`, `gws_obj`, `oa_obj` pointers, `first_userptr`, `num_entries`, a command-submission mutex, and a flexible entry array. Prototypes expose list get/put, UAPI entry-array copying, and list creation. Iteration macros cover all entries or only userptr entries.

## Control flow
The header has no executable flow. It defines the contracts implemented in `amdgpu_bo_list.c` and consumed by command-submission paths: callers obtain a referenced list by handle, iterate entries, lock `bo_list_mutex` while using it for submission, and release it with `amdgpu_bo_list_put()`.

## State and persistence behavior
The structures describe runtime-only per-file BO-list state. Lifetime is kref and RCU based; the flexible array is immutable in size after creation but entries can carry submission-time metadata such as BO VA and HMM range.

## Dependencies and integration points
The header depends on `drm/amdgpu_drm.h` for UAPI structures, forward declarations for AMDGPU BO/VA/file-private types, Linux RCU/kref/mutex primitives through includers, and HMM range support. It is part of the command-submission and BO-list ioctl boundary.

## Risks and edge cases
Flexible-array allocation size must match `num_entries`, and iteration macros assume `entries` is valid through `num_entries`. `first_userptr` partitions non-userptr from userptr entries; incorrect maintenance would break userptr-specific reservation/validation. The list mutex protects command-submission access, not IDR lifetime by itself.

## Test signals
Compile coverage, BO-list ioctl tests, command submission with special resources, userptr-only and mixed lists, and RCU/kref lifetime tests are the relevant signals.
