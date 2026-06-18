# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_mman.c

## Purpose
Implements i915 GEM mmap support: legacy CPU mmap ioctl, fake-offset mmap-offset ioctl, CPU and GTT fault handlers, mapping revocation, dumb-buffer offsets, framebuffer mmap, and the DRM file mmap hook.

## Important APIs and Functions
Key functions are `i915_gem_mmap_ioctl()`, `i915_gem_mmap_gtt_version()`, `vm_fault_cpu()`, `vm_fault_gtt()`, `vm_access()`, `i915_gem_object_release_mmap_gtt()`, `i915_gem_object_release_mmap_offset()`, `mmap_offset_attach()`, `__assign_mmap_offset()`, `i915_gem_mmap_offset_ioctl()`, `i915_gem_mmap()`, and `i915_gem_fb_mmap()`. `struct i915_mmap_offset` nodes connect object mmap types to DRM fake offsets.

## Control Flow
Modern mmap begins with `i915_gem_mmap_offset_ioctl()`, which validates flags/extensions, looks up and locks the object, creates or reuses an mmap-offset node, grants the DRM file one-shot access, and returns the fake offset. The `mmap()` syscall enters `i915_gem_mmap()`, resolves the node under the DRM VMA manager with RCU-safe object ref acquisition, then installs i915 VMA operations and page protections via `i915_gem_object_mmap()`.

CPU faults lock and pin pages, compute the object offset from the fake node, and remap scatterlist backing with `remap_io_sg()`. GTT faults take runtime PM, ww-lock and pin pages, bind a mappable or partial GGTT VMA with eviction fallback, reject incoherent snoopable access, pin fences, calculate virtual address/PFN bounds, remap GGTT aperture PFNs, mark userfault tracking, and set dirty/write state. Revocation paths zap mappings while holding the required GGTT/runtime-PM serialization.

## State and Persistence Behavior
Persists mmap offset nodes in `obj->mmo.offsets`, file-specific VMA-node allowances, `obj->userfault_count`, `userfault_link`, `vma->mmo`, `obj->mm.dirty`, VMA page protections, and a shared anonymous mmap singleton file. Runtime suspend clears userfault state and unmaps TTM VMA nodes.

## Dependencies and Integration Points
Integrates with DRM VMA offset manager, Linux mm fault APIs, anon inodes, runtime PM, GGTT/eviction/fence helpers, object pin/map APIs, TTM mmap hooks, user extensions, and framebuffer mmap users.

## Risks
Fake-offset lifetime and access control must be correct to avoid stale object access. GTT faults require runtime PM and GGTT mutex serialization. Snoopable non-LLC GTT access is rejected to prevent corruption. Revocation must reliably zap CPU PTEs after eviction, fence loss, or runtime suspend. Readonly mappings must reject write faults.

## Test Signals
Includes `selftests/i915_gem_mman.c` under selftest config. IGT mmap-offset, GTT/WC/WB/UC mmap, suspend/resume revocation, framebuffer mmap, and fault-injection tests are relevant. `trace_i915_gem_object_fault()` helps inspect fault behavior.
