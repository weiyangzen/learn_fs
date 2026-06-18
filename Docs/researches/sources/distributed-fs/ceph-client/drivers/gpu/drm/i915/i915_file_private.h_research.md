# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_file_private.h

## Purpose
`i915_file_private.h` defines the per-open DRM file state used by GEM contexts, proto-contexts, VMs, client accounting, and client ban scoring.

## Important APIs, Types, and Functions
`struct drm_i915_file_private` stores the owning `drm_i915_private`, either `drm_file *file` or RCU head for deferred free, `proto_context_lock`, `proto_context_xa`, `context_xa`, `vm_xa`, default BSD engine selection, ban scoring fields, hang timestamp, and `i915_drm_client *client`. Ban constants are `I915_CLIENT_SCORE_HANG_FAST`, `I915_CLIENT_FAST_HANG_JIFFIES`, `I915_CLIENT_SCORE_CONTEXT_BAN`, and `I915_CLIENT_SCORE_BANNED`.

## Control Flow
The header has no executable code. `i915_gem_open()` allocates and initializes the structure, context creation and lookup populate the xarrays, postclose tears contexts down and frees it through RCU, and hang/context-ban logic updates `ban_score` and `hang_timestamp`.

## State and Persistence Behavior
The structure persists for one DRM file lifetime. Proto-contexts allow userspace to configure a context ID through UAPI before it is finalized into a full `i915_gem_context`; `proto_context_lock` serializes both proto-context manipulation and finalization. `context_xa` and `vm_xa` persist live context/VM handles. Ban score persists across contexts owned by the file and prevents more work after threshold.

## Dependencies and Integration Points
It integrates DRM file-private storage, GEM context UAPI, xarray handle allocation, VM handles, client fdinfo accounting, and context-ban/hangcheck policy. The detailed comments document why proto-context locking is deliberately broad.

## Risks
The proto-context/context xarray split is race-prone if any path bypasses `proto_context_lock`. File-private free is RCU-deferred, so users must respect lifetime rules. Ban score constants affect denial-of-service mitigation and must be consistent with hang accounting expectations.

## Test Signals
IGT context create/setparam/getparam/destroy tests, VM create/destroy tests, concurrent context lookup/finalization, file close during active contexts, client ban tests after rapid hangs, and RCU/lockdep coverage.
