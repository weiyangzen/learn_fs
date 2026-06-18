# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gem.c

## Purpose
`amdgpu_gem.c` implements AMDGPU GEM object operations and user-facing GEM ioctls. It creates device and userptr BOs, maps them to userspace, tracks per-file VM BO associations, handles metadata and placement operations, updates GPU virtual-address mappings, lists process handles, creates dumb display buffers, and exposes GEM debugfs state.

## Important APIs, types, and functions
Important exported functions include `amdgpu_gem_object_create()`, `amdgpu_gem_force_release()`, `amdgpu_gem_create_ioctl()`, `amdgpu_gem_userptr_ioctl()`, `amdgpu_gem_mmap_ioctl()`, `amdgpu_gem_wait_idle_ioctl()`, `amdgpu_gem_metadata_ioctl()`, `amdgpu_gem_va_ioctl()`, `amdgpu_gem_op_ioctl()`, `amdgpu_gem_list_handles_ioctl()`, `amdgpu_mode_dumb_create()`, `amdgpu_mode_dumb_mmap()`, `amdgpu_gem_timeout()`, and `amdgpu_debugfs_gem_init()`. GEM object hooks are collected in `amdgpu_gem_object_funcs`.

## Control flow
Object creation builds `amdgpu_bo_param`, forces VRAM wipe-on-release, calls `amdgpu_bo_create_user()`, and returns the embedded GEM object. GEM open rejects foreign userptr mm ownership and invalid always-valid use, locks the BO and VM page directory with DRM exec, creates or references a `bo_va`, attaches an eviction fence, and for dynamic DMA-buf imports in compute VMs validates and fences the BO with KFD process eviction state. Close detaches eviction fences, drops `bo_va` references, clears freed VM mappings when ready, and fences the BO with resulting page-table work. Fault handling reserves the TTM BO, notifies AMDGPU before faulting pages, and falls back to a dummy page after unplug.

Ioctls validate flags and domains, create BOs with fallback from required CPU access or VRAM-only placement, create userptr BOs with HMM/MMU-notifier registration and optional upfront validation, return mmap offsets only for CPU-accessible non-userptr objects, wait on BO reservation fences, get/set metadata and tiling, mutate VM mappings through map/unmap/clear/replace operations, optionally export VM update fences to syncobj timelines, change placement, report create or mapping info, list all handles for a file, and create aligned dumb buffers in display-supported domains.

## State and persistence behavior
Runtime state lives in GEM handles, TTM BOs, AMDGPU BO flags/domains/metadata, `amdgpu_bo_va` mappings, VM page tables, HMM userptr registration, reservation fences, syncobj timeline points, and per-file object IDRs. No data is persisted by this file beyond BO memory contents while objects live. Metadata and mappings are kernel runtime state exposed through ioctls.

## Dependencies and integration points
It depends on DRM GEM/TTM helpers, DRM exec locking, syncobj timelines, dma-buf imports, HMM/userptr support, AMDGPU BO/VM/display/dma-buf/XGMI/KFD/user-queue eviction code, dma-resv, and debugfs. Its ioctl entry points are registered by `amdgpu_drv.c`.

## Risks and edge cases
User input validation is broad: flags, domains, addresses, VA holes, reserved ranges, metadata sizes, and placement changes all need strict checks. VM updates must merge page-table and BO mapping fences so userspace does not miss PDE updates. Object open/close lock ordering with BOs, VM PDs, eviction fences, and KFD process locks is sensitive. Userptr write access requires registration; foreign-mm userptr sharing is rejected. `amdgpu_gem_userptr_ioctl()` has an early `-ENOMEM` path after range allocation failure that bypasses `drm_gem_object_put()`, which is a code-review risk to verify against surrounding ownership expectations. Handle listing can race object table changes and returns `-EAGAIN` if counts change.

## Test signals
Signals include GEM create fallback paths, TMZ encrypted buffer rejection when disabled, GDS/GWS/OA no-CPU-access creation, always-valid BO behavior, mmap permission checks, userptr validation and MMU invalidation, metadata get/set, VA map/unmap/clear/replace across reserved ranges and VM holes, syncobj timeline fence export, placement changes with imported/userptr/XGMI BOs, dumb buffer allocation/pitch alignment, fd close mapping cleanup, debugfs GEM info, and handle-list retry behavior.
