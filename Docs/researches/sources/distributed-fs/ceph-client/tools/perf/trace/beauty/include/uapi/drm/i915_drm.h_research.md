# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/drm/i915_drm.h

## Purpose

`i915_drm.h` is a mirrored Linux UAPI header for the Intel i915 DRM driver. In this `tools/perf/trace/beauty/include/uapi` tree it gives perf trace's "beauty" decoders the same ioctl command numbers, structures, flags, and enum values used by userspace talking to `/dev/dri/*` i915 devices. It covers uevents, extension chains, engine classes, i915 PMU encodings, DRM ioctl offsets, GEM object management, execbuffer submission, contexts, i915 perf streams, query blobs, memory regions, and protected-content creation.

## Important APIs, Types, and Constants

Key API groups are `struct i915_user_extension`; `enum drm_i915_gem_engine_class`; `struct i915_engine_class_instance`; `I915_PMU_ENGINE_*` and `I915_PMU_*` encodings; `DRM_I915_*` ioctl offsets and `DRM_IOCTL_I915_*` macros; GEM structs such as `drm_i915_gem_create`, `mmap_offset`, `set_domain`, `relocation_entry`, `exec_object2`, `execbuffer2`, `busy`, `caching`, `set_tiling`, `wait`, and `userptr`; execution flags `EXEC_OBJECT_*` and `I915_EXEC_*`; context structures and params; engine-map load-balance/bond/parallel-submit extensions; perf OA formats, perf properties, stream ioctls, and records; `DRM_I915_QUERY_*` query IDs and query structs; and memory-region / GEM create-extension structs.

## Control Flow and Integration

The header itself has no executable control flow. Its ABI flow is userspace issuing an i915 DRM ioctl, the ioctl macro encoding command/direction/struct type through DRM helpers, the matching struct crossing the user/kernel boundary, and the i915 driver validating flags, handles, context IDs, engine identifiers, placement rules, and extension chains before writing output fields such as handles, mmap offsets, query lengths, fence fds, perf streams, or memory-region information.

In perf, the file integrates as source data for symbolic ioctl and bitmask decoding. It is especially important for decoding `DRM_IOCTL_I915_GEM_CREATE`, `GEM_EXECBUFFER2`, `GEM_CONTEXT_CREATE_EXT`, `QUERY`, `PERF_OPEN`, and `GEM_CREATE_EXT` traces.

## State and Persistence Behavior

The header stores no state, but describes stateful driver objects: GEM handles scoped to a DRM file, context IDs with scheduler/engine/VM/protected-content configuration, VM IDs, i915 perf stream fds, and protected-content objects tied to PXP session state. Some properties are immutable at creation time, especially memory placement and newer caching/PAT policy.

## Dependencies and Integration Points

It depends on `drm.h` plus Linux UAPI integer and ioctl types. It is coupled to the i915 kernel driver, Mesa/Intel userspace, intel-gpu-tools, perf i915 PMU support, DRM syncobj/sync_file APIs, and discrete-GPU memory-region semantics.

## Risks

Numeric ioctl offsets are ABI and must not be renumbered or given holes. Unknown flag masks and MBZ fields must remain visible and strict. Removed API numbers are still reserved. `__u64` pointer fields require 32/64-bit compatibility awareness. Extension chains are user pointers and should not be blindly dereferenced by trace tooling. `DRM_IOCTL_I915_GEM_MMAP_OFFSET` aliases the `GEM_MMAP_GTT` command slot with a newer struct interpretation.

## Test Signals

Compile a minimal TU including the header; compare `DRM_IOCTL_I915_*` values against kernel UAPI; decode traces for GEM create, execbuffer2, context create, query, perf open, and create-ext; unit-check `I915_EXEC_*`, `EXEC_OBJECT_*`, context params, query IDs, memory classes, and perf record types; and verify unknown bits remain visible.
