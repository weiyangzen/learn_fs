# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gem.h

## Purpose
`amdgpu_gem.h` declares AMDGPU GEM object helpers, ioctl handlers, dumb-buffer helpers, and the user-settable GEM create flag mask.

## Important APIs, types, and functions
It defines `AMDGPU_GEM_DOMAIN_MAX`, `gem_to_amdgpu_bo()`, declares `amdgpu_gem_object_funcs`, and prototypes all major GEM helpers and ioctls implemented in `amdgpu_gem.c`. `AMDGPU_GEM_CREATE_SETTABLE_MASK` lists flags userspace may set during GEM creation, including CPU access controls, VM always-valid, explicit sync, wipe-on-release, encryption, DCC, discardable, and coherence/cache flags.

## Control flow
The header has no executable control flow. It defines the external contract used by the DRM ioctl table, display dumb-buffer paths, BO users, and debugfs initialization.

## State and persistence behavior
No state is allocated here. The macro `gem_to_amdgpu_bo()` maps DRM GEM objects to their containing AMDGPU BO runtime state.

## Dependencies and integration points
It depends on DRM AMDGPU UAPI definitions and DRM GEM core types. It is the bridge between driver registration in `amdgpu_drv.c` and GEM implementation in `amdgpu_gem.c`.

## Risks and edge cases
The settable-mask macro is an important UAPI validation boundary; adding a flag here permits userspace to request it through GEM create. Prototype drift breaks ioctl registration. `gem_to_amdgpu_bo()` assumes every passed GEM object is an AMDGPU BO.

## Test signals
Build coverage, ioctl flag validation, GEM create tests for every settable flag, and imported-object paths validate this header.
