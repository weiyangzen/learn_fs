<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.h

Purpose: declares the public migration/clear APIs for GPU-assisted i915 memory movement.

Important APIs: `intel_migrate_init()` and `intel_migrate_fini()` manage the GT migration context. `intel_migrate_create_context()` creates a shared-VM migration context. `intel_migrate_copy()` and `intel_context_migrate_copy()` copy scatterlist memory between source and destination placements with PAT and LMEM flags. `intel_migrate_clear()` and `intel_context_migrate_clear()` clear scatterlist memory to a value. All copy/clear APIs return the last emitted `i915_request` through `out`.

Control flow: higher-level GEM migration code calls the `intel_migrate_*` wrappers with a ww context; lower-level users that already hold a pinned migration context can call `intel_context_migrate_*` directly.

State and persistence: the only declared state is `struct intel_migrate`, whose implementation stores the pinned base context. Requests returned in `out` carry asynchronous completion state for the migration work.

Dependencies and integration points: forward-declares fences/dependencies/requests/GT/scatterlists and includes `intel_migrate_types.h`. Integrated with GEM TTM/LMEM migration paths.

Risks: callers must pass DMA-mapped scatterlists and correct PAT/LMEM flags; wrong flags program wrong PTE cacheability/local-memory bits. `out` ownership must be released by callers. Wrappers may return errors after submitting a partially completed last request.

Test signals: GEM migration tests, request/fence dependency tests, API misuse checks for null migration context, and scatterlist boundary coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate.h -->
