## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_context_types.h

### Purpose

`i915_gem_context_types.h` defines the data structures backing GEM context uAPI and internal engine mappings: engine arrays, iterators, proto engines, proto contexts, and realized GEM contexts.

### Important APIs, types, and functions

Key types are `struct i915_gem_engines`, `struct i915_gem_engines_iter`, `enum i915_gem_engine_type`, `struct i915_gem_proto_engine`, `struct i915_gem_proto_context`, and `struct i915_gem_context`. Important fields include RCU/fence-backed engine arrays, physical/balanced/parallel engine descriptions, proto VM/user flags/scheduler/user engines/PXP state, live context engines/syncobj/VM/client/ref/release work/user flags/protected content/scheduler/hang counters/LUT/name/stale engines.

### Control flow

The header has no executable control flow, but its comments describe the proto-context delayed-realization model. User configuration starts in `i915_gem_proto_context` and is converted into an immutable or semi-mutable `i915_gem_context` when lookup/submission requires a real context.

### State and persistence behavior

These structures hold most persistent GEM context state. Engine arrays are freed through RCU/fence completion. Proto contexts persist in `proto_context_xa` until finalized or destroyed. Live contexts persist while referenced by userspace handles, requests, engine arrays, VM mappings, and release work.

### Dependencies

It depends on Linux atomic/list/llist/kref/mutex/radix-tree/rbtree/RCU types, GT `intel_context_types.h`, scheduler attributes, and i915 software fences.

### Integration points

The definitions are consumed by `i915_gem_context.c`, execbuffer, request/context code, client accounting, LUT/VMA mapping, and scheduler integration. The uAPI comments document compatibility assumptions for Mesa, media driver, and compute-runtime behavior.

### Risks

The structures encode locking contracts: proto modifications exposed to userspace require `proto_context_lock`, `engines` uses RCU plus `engines_mutex`, and handle LUTs use `lut_mutex`. Field layout and semantics affect uAPI compatibility. Protected content, persistence, and recoverability flags have cross-field invariants that must be maintained by setters.

### Test signals

Context uAPI tests, RCU/list debug coverage, engine replacement/destruction tests, proto-context SETPARAM compatibility tests, and memory-leak/refcount validation during context close.
