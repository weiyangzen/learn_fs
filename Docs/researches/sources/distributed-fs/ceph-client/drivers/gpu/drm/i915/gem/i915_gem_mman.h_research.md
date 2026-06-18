# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_mman.h

## Purpose
Declares GEM mmap entry points and mmap cleanup helpers used by i915 and DRM framebuffer paths.

## Important APIs
Exports `i915_gem_mmap_gtt_version()`, `i915_gem_mmap()`, `i915_gem_dumb_mmap_offset()`, `__i915_gem_object_release_mmap_gtt()`, `i915_gem_object_release_mmap_gtt()`, `i915_gem_object_runtime_pm_release_mmap_offset()`, `i915_gem_object_release_mmap_offset()`, and `i915_gem_fb_mmap()`.

## Control Flow
No logic in the header. Implementations manage object mmap-offset RB trees, DRM VMA nodes, VMA fault operations, and runtime-PM-safe revocation.

## State and Persistence Behavior
No state is stored here. The declared helpers mutate object mmap nodes and userfault tracking in implementation code.

## Dependencies and Integration Points
Includes Linux `mm_types`/types and forward-declares DRM/file/object structures. Used by DRM mmap setup, framebuffer mapping, object teardown, runtime suspend, and ioctl code.

## Risks and Test Signals
Callers must choose revocation helpers appropriate to their locking/runtime-PM context. Build coverage and `i915_gem_mman.c` selftests validate the interface.
