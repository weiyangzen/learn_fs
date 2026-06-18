## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context.c

### Purpose

`i915_gem_context.c` implements i915 GEM context uAPI, context lifetime, engine-set construction, VM handles, delayed proto-context realization, scheduler attributes, persistence/cancellation behavior, SSEU configuration, protected-content constraints, reset stats, and module cache setup.

### Important APIs, types, and functions

Public functions include `i915_gem_init__contexts()`, `i915_gem_context_open()`, `i915_gem_context_close()`, `i915_gem_context_release()`, `i915_gem_context_lookup()`, `i915_gem_context_create_ioctl()`, `i915_gem_context_destroy_ioctl()`, `i915_gem_context_getparam_ioctl()`, `i915_gem_context_setparam_ioctl()`, `i915_gem_context_reset_stats_ioctl()`, `i915_gem_vm_create_ioctl()`, `i915_gem_vm_destroy_ioctl()`, `i915_gem_user_to_context_sseu()`, `i915_gem_engines_iter_next()`, and module init/exit.

Core internal flows include proto-context creation/registration/finalization, user engine parsing (`set_proto_ctx_engines_*()`), default/user engine realization, `intel_context_set_gem()`, stale-engine fenced release, `kill_engines()`, `context_close()`, and parameter get/set handlers for live and proto contexts.

### Control flow

File open initializes xarrays for real contexts, proto contexts, and VM handles, then creates/registers context 0 immediately. Context create validates flags and ban state, builds a proto-context with default user flags, applies `CONTEXT_CREATE_EXT_SETPARAM` extensions, and either registers the proto-context for lazy finalization or creates a real context immediately on newer graphics versions. `i915_gem_context_lookup()` first checks the real context xarray; if absent, it locks the proto-context table, creates the real context, registers it, erases the proto entry, and closes the proto state.

Real context creation allocates a context, creates or references a VM, copies user flags and scheduler attributes, builds either default engines or user-defined physical/balanced/parallel engines, sets GEM backpointers and VM references in each `intel_context`, optionally creates a shared timeline syncobj, and takes PXP runtime wakerefs for protected contexts. Close removes the context from xarrays/lists, unpins engines, fences active contexts until idle, clears handle lookup tables, revokes or kills outstanding work depending on persistence and hangcheck, and releases references through deferred work.

### State and persistence behavior

Persistent per-file state lives in `drm_i915_file_private::{context_xa, proto_context_xa, vm_xa, proto_context_lock}`. Persistent per-context state includes refs, VM, RCU engine array, scheduler priority, user flags, protected-content wakeref, syncobj, hang/reset counters, LUT radix tree, client links, and stale engine list. Hardware persistence is through `intel_context` objects and in-flight requests that may outlive userspace handles until fenced idle release completes.

### Dependencies

The file depends on xarray, kref, RCU, mutexes, radix tree, DRM syncobj, shmem helpers, i915 scheduler/request/context/engine APIs, PPGTT creation, GuC/execlists capability checks, PXP, user-extension parsing, reset/heartbeat helpers, and i915 client accounting.

### Integration points

Context lookup is used by execbuffer and perf paths. The context ioctls are registered in `i915_driver.c`. VM create/destroy exposes per-file PPGTT handles used by context parameters. Engine arrays map execbuf engine indices to physical, virtual, or parallel `intel_context` instances. Protected-content flags integrate with PXP and runtime PM. Client runtime accounting accumulates per-engine execution time during engine release.

### Risks

The delayed proto-context model is concurrency-sensitive: context lookup, setparam, destroy, and create finalization all synchronize through `proto_context_lock`. Live context state is split across `ctx->mutex`, `engines_mutex`, RCU, and stale-engine fences, so ordering mistakes can leak contexts or allow use-after-close. Persistence disabling depends on preemption and engine reset support. Parallel engines require permanent pinning after ring-size setup. Protected content requires bannable and non-recoverable constraints plus PXP liveness. Some getparam/setparam reads are intentionally unserialized or debug-only, carrying race risk by design.

### Test signals

Signals include igt context create/destroy/setparam/getparam, VM create/destroy, engine arrays with load-balance/bond/parallel extensions, GuC and non-GuC paths, SSEU validation on Gen11, persistent and non-persistent close behavior, client ban handling, protected-content creation, execbuf lookup races with destroy, reset stats after hangs, and selftests included under `CONFIG_DRM_I915_SELFTEST`.
