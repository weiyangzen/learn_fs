
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_object.h

## Purpose
Defines the public BO interface for AMDGPU memory management. It exposes the core `amdgpu_bo` structures, BO creation parameters, VM mapping records, reservation/refcount helpers, GPU address helpers, suballocation helpers, and all function prototypes implemented by object and suballocation code.

## Important APIs, Types, and Functions
`struct amdgpu_bo_param` carries allocation size, alignment, domain, preferred domain, flags, TTM type, reservation object, destroy callback, and XCP partition selector. `struct amdgpu_bo_va_mapping` and `struct amdgpu_bo_va` model VM mappings, invalid/valid mapping lists, PT update fence state, XGMI flag, and queue reference state. `struct amdgpu_bo` wraps `ttm_buffer_object`, placement state, kmap state, flags, VM pointer, parent, optional MMU notifier, KFD memory, and XCP ID. `struct amdgpu_bo_user` adds tiling and metadata; `struct amdgpu_bo_vm` appends flexible VM entries.

## Control Flow
The header supplies inline adapters used throughout the driver: `ttm_to_amdgpu_bo`, `amdgpu_mem_type_to_domain`, `amdgpu_bo_reserve`, `amdgpu_bo_unreserve`, `amdgpu_bo_size`, GPU-page sizing, mmap offset, explicit-sync check, and encryption check. Callers build `amdgpu_bo_param`, call creation helpers, reserve before metadata/address operations, pin when a fixed GPU address is required, and unreserve/unref on completion.

## State and Persistence Behavior
The state model is reservation-centered: most mutable fields are protected by the BO reservation or VM page-directory reservation as documented inline. Mapping lists and queue references persist for the lifetime of a BO/VM relationship, while metadata persists only on user BOs until replacement or destruction. The XCP ID is immutable after creation except as encoded by the allocation parameters.

## Dependencies and Integration Points
Includes DRM AMDGPU UAPI definitions, the broad `amdgpu.h` device model, resource cursors, and optional MMU notifier support. Function prototypes connect this header to GEM ioctl handling, TTM callbacks, VM code, KFD, debugfs, and the DRM suballocator-backed SA manager.

## Risks and Test Signals
Risks are primarily contract mismatches: using user-only helpers on kernel BOs, accessing mapping lists without the documented reservation lock, failing to account for `AMDGPU_BO_MAX_PLACEMENTS`, and forgetting that `xcp_id_plus1 == 0` means any partition. Test signals include lockdep coverage for reservation rules, VM map/unmap stress, metadata ioctl tests, encrypted/explicit-sync flag behavior, and SA allocation/free tests.
