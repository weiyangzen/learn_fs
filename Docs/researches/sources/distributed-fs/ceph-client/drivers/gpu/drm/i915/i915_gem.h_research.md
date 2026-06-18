# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gem.h

## Purpose
`i915_gem.h` declares core GEM lifecycle, unbind, GGTT pinning, runtime suspend, and per-file open APIs, and defines GEM debug/tracing macros and shared constants.

## Important APIs, Types, and Functions
Declarations cover early init/cleanup, workqueue draining, `i915_gem_object_ggtt_pin_ww()`, `i915_gem_object_ggtt_pin()`, `i915_gem_object_unbind()`, runtime suspend, driver init/register/unregister/remove/release, and `i915_gem_open()`. It defines `I915_GEM_GPU_DOMAINS`, unbind flags (`ACTIVE`, `BARRIER`, `TEST`, `VM_TRYLOCK`, `ASYNC`), `I915_GEM_IDLE_TIMEOUT`, `GEM_QUIRK_PIN_SWIZZLED_PAGES`, and debug macros `GEM_BUG_ON`, `GEM_WARN_ON`, `GEM_TRACE`, and related variants.

## Control Flow
The header itself has only macro flow. In debug builds, `GEM_BUG_ON()` emits trace/error diagnostics and either warns or BUGs depending on config; in non-debug builds it compiles conditions through `BUILD_BUG_ON_INVALID` to preserve type checking without runtime cost. Trace macros either emit ftrace/pr_err data or compile away.

## State and Persistence Behavior
The header stores no state. Its constants define object domain masks, unbind behavior, idle timeout, and quirk bits persisted in driver/object state.

## Dependencies and Integration Points
It is included by broad GEM, GT, driver, and error paths. It depends on DRM driver types and i915 utility macros, while forward-declaring GEM object, VMA, file, private, ww context, and GTT view types.

## Risks
Macro behavior changes can alter assertions globally. Unbind flag semantics must match `i915_gem.c`; adding flags requires auditing all callers. Debug macros can have side effects in expressions if used incorrectly, so conditions should be side-effect-free.

## Test Signals
Build with `CONFIG_DRM_I915_DEBUG_GEM`, `CONFIG_DRM_I915_TRACE_GEM`, and non-debug configs; run GEM selftests and ensure assertions catch invalid lock/state conditions without affecting release builds.
