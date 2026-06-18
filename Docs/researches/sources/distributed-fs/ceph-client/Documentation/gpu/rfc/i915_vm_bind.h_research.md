# sources/distributed-fs/ceph-client/Documentation/gpu/rfc/i915_vm_bind.h

## Purpose
`i915_vm_bind.h` is an RFC UAPI header for explicit GPU virtual-address binding in i915. It defines versioning, VM creation opt-in, VM_BIND/UNBIND ioctls, execbuffer3 submission, timeline fences, and VM-private GEM object creation.

## Important APIs, Types, and Functions
Important constants are `I915_PARAM_VM_BIND_VERSION`, `I915_VM_CREATE_FLAGS_USE_VM_BIND`, `DRM_I915_GEM_VM_BIND`, `DRM_I915_GEM_VM_UNBIND`, `DRM_I915_GEM_EXECBUFFER3`, and the corresponding `DRM_IOCTL_*` macros. Important types are `drm_i915_gem_timeline_fence`, `drm_i915_gem_vm_bind`, `drm_i915_gem_vm_unbind`, `drm_i915_gem_execbuffer3`, and `drm_i915_gem_create_ext_vm_private`. Flags include `I915_TIMELINE_FENCE_WAIT`, `I915_TIMELINE_FENCE_SIGNAL`, `I915_GEM_VM_BIND_CAPTURE`, and `I915_GEM_CREATE_EXT_VM_PRIVATE`.

## Control Flow
Userspace queries `I915_PARAM_VM_BIND_VERSION`, creates a VM with `USE_VM_BIND`, creates GEM objects, then issues VM_BIND requests mapping object ranges at GPU virtual addresses. Optional timeline fences signal asynchronous completion. VM_UNBIND removes mappings, and EXECBUFFER3 submits work by GPU VA without an execlist. Version 1 requires exact unbinds and no replacement; version 2 lifts partial/multiple unbind restrictions and allows replacement within a range.

## State and Persistence Behavior
The header stores no state. Runtime state is GPU VA space mappings, GEM object references, context engine maps, timeline syncobj points, and optional VM-private object association. Reserved fields and extension chains are persistent ABI expansion points and must be zeroed by userspace.

## Dependencies and Integration Points
Depends on DRM ioctl encoding, i915 GEM objects, VM control, syncobj/timeline fences, context user-engine maps, parallel submit structures, page-size rules for system versus local memory, and i915 error capture infrastructure.

## Risks
Risks include unordered concurrent bind/unbind calls from different CPU threads, invalid 4K/64K alignment, mixing 64K local memory and 4K system memory bindings in one 2M range, unbinding mappings still used by the GPU, invalid fence flags, and userspace assuming version 2 replacement semantics on a version 1 kernel.

## Test Signals
Test version probing, VM creation opt-in, aligned and misaligned binds, partial and multi-range unbind behavior by version, mapping replacement, aliasing the same object range, timeline-fence signaling, invalid wait flags on out fences, EXECBUFFER3 submission in VM_BIND mode, and VM-private object lifecycle.
