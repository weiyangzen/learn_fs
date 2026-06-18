## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context.h

### Purpose

`i915_gem_context.h` is the public internal header for GEM context operations, flag accessors, engine lookup helpers, VM helpers, ioctl declarations, iterator macros, and module setup.

### Important APIs, types, and functions

It defines inline flag helpers for closed, no-error-capture, bannable, recoverable, persistence, user-engines, and protected-content checks. It declares context open/close/release, VM and context ioctls, `i915_gem_context_lookup()`, ref helpers, VM helpers (`i915_gem_context_vm()`, `i915_gem_context_has_full_ppgtt()`, `i915_gem_context_get_eb_vm()`), engine array lock/get helpers, `for_each_gem_engine`, LUT handle allocation, module init/exit, and `i915_gem_user_to_context_sseu()`.

### Control flow

Inline helpers wrap bit operations, kref get/put, RCU-protected VM/engine access, and mutex acquisition. `i915_gem_context_get_engine()` uses an RCU read-side section to safely fetch and ref an `intel_context` by index.

### State and persistence behavior

The header does not own state but exposes safe access to `struct i915_gem_context` fields defined in `i915_gem_context_types.h`. Ref and lock helpers directly affect context lifetime and engine-array mutation ordering.

### Dependencies

It includes `i915_gem_context_types.h`, GT `intel_context.h`, scheduler, device info, and core GEM driver headers.

### Integration points

Execbuffer, perf, reset, object LUT, and ioctl code use this API to look up contexts, hold refs, choose engines, and access VMs. `for_each_gem_engine()` standardizes iteration over sparse engine arrays.

### Risks

Misusing protected RCU helpers without required locks can race context close or engine replacement. `i915_gem_context_get_eb_vm()` falls back to GGTT when full PPGTT is absent, so callers must understand address-space semantics. Flag helpers expose policy bits whose invariants are enforced in `i915_gem_context.c`.

### Test signals

Compiler/lockdep coverage, execbuffer context lookup tests, engine-index validation, and refcount leak checks around get/put paths.
