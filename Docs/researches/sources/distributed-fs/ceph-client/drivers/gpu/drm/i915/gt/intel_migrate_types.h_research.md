<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate_types.h

Purpose: defines the migration subsystem state embedded in `struct intel_gt`.

Important type: `struct intel_migrate` contains `struct intel_context *context`, the pinned base migration context and owner of the special migration PPGTT.

Control flow: `intel_migrate_init()` populates `context`; copy/clear operations create or borrow contexts from it; `intel_migrate_fini()` destroys and clears it.

State and persistence: the context pointer persists while migration is available for the GT. A null context means migration operations should fail with `-ENODEV`.

Dependencies and integration points: forward-declares `struct intel_context`; included by `intel_migrate.h` and GT type definitions.

Risks: lifetime is single-pointer based, so double-finalization and operations racing with teardown must be prevented by GT lifecycle ordering.

Test signals: init/fini leak checks, migration API behavior when context allocation fails, and driver unload/reload with pending migration requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_migrate_types.h -->
