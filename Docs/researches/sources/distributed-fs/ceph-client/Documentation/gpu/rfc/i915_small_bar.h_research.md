# sources/distributed-fs/ceph-client/Documentation/gpu/rfc/i915_small_bar.h

## Purpose
`i915_small_bar.h` is an RFC UAPI header documenting proposed i915 memory-region and GEM-create extensions for systems where only part of device local memory is CPU visible through the PCI BAR.

## Important APIs, Types, and Functions
Important types are `struct __drm_i915_memory_region_info` and `struct __drm_i915_gem_create_ext`. Key fields include `probed_size`, `unallocated_size`, `probed_cpu_visible_size`, `unallocated_cpu_visible_size`, object `size`, returned `handle`, `flags`, and extension chain pointer. Key constants are `I915_GEM_CREATE_EXT_FLAG_NEEDS_CPU_ACCESS`, `I915_GEM_CREATE_EXT_MEMORY_REGIONS`, and `I915_GEM_CREATE_EXT_PROTECTED_CONTENT`.

## Control Flow
Userspace first queries memory regions through `DRM_I915_QUERY_MEMORY_REGIONS`, compares total device memory with CPU-visible memory, and decides whether an allocation needs CPU access. GEM creation then uses `drm_i915_gem_create_ext` semantics with memory-region placement extensions and optionally sets `NEEDS_CPU_ACCESS`. The kernel uses the hint to prefer CPU-visible device memory or fall back to system memory when required.

## State and Persistence Behavior
The header itself stores no state. ABI state lives in queried region accounting and GEM object placement. `unallocated_*` fields are estimates and require privileges for reliable accounting. Reserved fields are MBZ and preserve future extension space.

## Dependencies and Integration Points
Depends on i915 DRM UAPI types such as `drm_i915_query_item`, `drm_i915_query`, `drm_i915_gem_memory_class_instance`, `i915_user_extension`, memory-region placement extensions, protected-content extension support, and userspace Mesa/media drivers that allocate local-memory buffers.

## Risks
Risks include older kernels reporting zero CPU-visible fields, userspace omitting the system-memory fallback placement, expensive fault-time migration when CPU access was not hinted, incompatibility with flat CCS requirements, and ABI mistakes around reserved MBZ fields or privilege-dependent accounting.

## Test Signals
Exercise memory-region queries on full-BAR and small-BAR systems, create local-memory objects with and without `NEEDS_CPU_ACCESS`, test fallback to system memory under CPU-visible pressure, verify older-kernel error behavior, and run userspace allocation paths that CPU-map buffers after GPU use.
