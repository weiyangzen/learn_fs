<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.h

Purpose: declares render null-state rodata and runtime renderstate object APIs.

Important APIs and types: `struct intel_renderstate_rodata` holds relocation offsets, batch dwords, and batch item count. `RO_RENDERSTATE(_g)` builds extern rodata definitions for generated Gen-specific null-state files. `struct intel_renderstate` stores ww context, rodata, VMA, and batch/aux offsets and sizes. Functions are `intel_renderstate_init()`, `intel_renderstate_emit()`, and `intel_renderstate_fini()`.

Control flow: callers initialize a renderstate for a pinned context, emit it into an `i915_request`, then finalize to unpin and release resources.

State and persistence: renderstate state is temporary per initialization/emission sequence; rodata objects are static build-time constants.

Dependencies and integration points: includes GEM ww support and forward-declares request/context/VMA types. Integrated with generated renderstate sources and render engine initialization paths.

Risks: the `RO_RENDERSTATE` macro assumes generated symbol naming conventions. Callers must call fini after successful init, including no-rodata cases where only context/ww state may be held.

Test signals: compile/link coverage for generated rodata, renderstate emit tests, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_renderstate.h -->
