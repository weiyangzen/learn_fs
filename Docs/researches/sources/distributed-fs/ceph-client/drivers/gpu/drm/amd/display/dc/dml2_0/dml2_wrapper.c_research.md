<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.c

Purpose: provides the non-FPU public lifecycle and validation dispatch wrapper for DML2, including allocation, create, destroy, reinit, and routing between DML2.0 and DML2.1 implementations.

Important APIs/types/functions: exports `dml2_allocate_memory()`, `dml2_validate()`, `dml2_create()`, `dml2_destroy()`, and `dml2_reinit()`. Internal `dml2_init()` stores configuration, maps DCN version to DML project id, and initializes IP, SOC bounding box, and SOC states through FPU helper entry points.

Control flow: creation checks whether DML2.1 is enabled for DCN 4.01 or newer and delegates to `dml21_create()` when needed. Otherwise it allocates a zeroed `dml2_context`, initializes project-specific DML2.0 state, and returns it. Validation applies debug overrides, delegates to DML2.1 for DML2.1 contexts, calls `dml2_validate_only()` for mode-only/state-index validation, or calls `dml2_validate_and_build_resource()` for full programming validation.

State and persistence behavior: owns `dml2_context` allocation via `vzalloc`/`vfree`, with optional `DC_RUN_WITH_PREEMPTION_ENABLED` wrapping. It persists a copy of configuration in the context and refreshes DML core IP/SOC/state data on reinit.

Dependencies and integration points: depends on `dml2_internal_types.h`, DML2.0 and DML2.1 wrapper/FPU headers, and `dc_fpu.h`. It is the external DML2 API used by DC state creation and validation.

Risks and test signals: architecture dispatch must match `in_dc->debug.using_dml21`, `dce_version`, and `dml2->architecture`. Destroy delegates to DML2.1 cleanup but still frees the context afterward, so DML2.1 must not independently free the same pointer. Test signals include DCN32/35/401 create, DML2.1 create/reinit path, null validation rejection, validate-mode dispatch, and repeated reinit without stale project data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_wrapper.c -->
