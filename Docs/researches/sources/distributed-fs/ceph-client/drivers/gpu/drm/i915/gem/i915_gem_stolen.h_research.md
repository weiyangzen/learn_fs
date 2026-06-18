# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_stolen.h

## Purpose
This header declares stolen-memory region setup, stolen GEM object creation, stolen-object identification, and the display stolen-memory interface.

## Important APIs, Types, and Functions
Exports are `i915_gem_stolen_smem_setup`, `i915_gem_stolen_lmem_setup`, `i915_gem_object_create_stolen`, `i915_gem_object_is_stolen`, `I915_GEM_STOLEN_BIAS`, and `i915_display_stolen_interface`.

## Control Flow
There is no executable flow. `I915_GEM_STOLEN_BIAS` reserves the first 128 KiB bias used by allocator helpers to avoid problematic low stolen addresses.

## State and Persistence Behavior
The header stores no state; implementations maintain DSM resources, `drm_mm` allocator state, and per-object stolen nodes.

## Dependencies and Integration Points
It forward-declares i915 private and GEM object types and references `struct intel_memory_region` and `struct intel_display_stolen_interface` through declarations. Display code uses the exported interface to allocate stolen memory without directly depending on GEM internals.

## Risks
The bias constant and setup entry points are part of platform allocation policy; changing them can affect BIOS framebuffer reuse and hardware workarounds.

## Test Signals
Build coverage, stolen-region setup at probe, display stolen allocation paths, and object identification tests validate the header contract.
