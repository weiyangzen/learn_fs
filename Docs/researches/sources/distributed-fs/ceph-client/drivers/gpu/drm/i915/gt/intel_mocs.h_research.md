<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.h

Purpose: documents the MOCS programming model and declares GT/engine initialization entry points.

Important APIs: `intel_mocs_init(struct intel_gt *gt)` initializes GT-global MOCS and L3CC state; `intel_mocs_init_engine(struct intel_engine_cs *engine)` initializes per-engine MOCS state where needed; `intel_set_mocs_index(struct intel_gt *gt)` caches selected MOCS indices into GT state.

Control flow: GT setup calls global init and index selection; engine setup or reset calls per-engine init under forcewake. The header comment explains that batches reference table indices rather than direct cacheability values.

State and persistence: the header itself stores no state; hardware MOCS tables and `gt->mocs` selected indices are the persistent effects.

Dependencies and integration points: forward-declares GT and engine structures. Integrated with context workaround batches, BLT/migration command emission, and platform cacheability ABI.

Risks: callers must ensure forcewake is active for engine initialization as required by implementation. Missing init after reset can leave stale cacheability registers.

Test signals: MOCS selftests, reset register reprogramming checks, and command streams using UC/WB indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_mocs.h -->
