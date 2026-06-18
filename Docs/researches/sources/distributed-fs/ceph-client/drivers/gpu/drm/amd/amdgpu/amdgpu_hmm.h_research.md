# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hmm.h

## Purpose
`amdgpu_hmm.h` declares AMDGPU HMM range state and notifier helpers, with fallback stubs when `CONFIG_HMM_MIRROR` is disabled.

## Important APIs, types, and functions
It defines `struct amdgpu_hmm_range`, which wraps `struct hmm_range` and an AMDGPU BO reference. It declares `amdgpu_hmm_range_get_pages()`, `amdgpu_hmm_range_valid()`, `amdgpu_hmm_range_alloc()`, `amdgpu_hmm_range_free()`, `amdgpu_hmm_register()`, and `amdgpu_hmm_unregister()`.

## Control flow
When HMM mirror support is enabled, callers use the implementation in `amdgpu_hmm.c`. When it is disabled, registration warns once and returns `-ENODEV`, range allocation returns NULL, validation returns false, and unregister/free are no-ops.

## State and persistence behavior
The represented state is transient: HMM PFN arrays, notifier sequence, and a BO reference. No persistent storage is involved.

## Dependencies and integration points
The header depends on Linux HMM, MMU notifier, workqueue/rwsem/interval tree headers, DRM logging for the fallback warning, and AMDGPU BO forward declarations. It is included by userptr and VM paths.

## Risks and edge cases
Callers must handle disabled-HMM stubs and NULL range allocation. The include guard name `__AMDGPU_MN_H__` is legacy-looking but functional. Code using HMM APIs must not assume `CONFIG_HMM_MIRROR` availability.

## Test signals
Build both with and without `CONFIG_HMM_MIRROR`, validate warning behavior in disabled builds, and run userptr/HMM tests in enabled builds.
