# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_gsccs.h

Purpose: Declares the GSC-CS PXP backend API and timeout constants.

Important APIs/types: `GSC_PENDING_RETRY_MAXCOUNT`, `GSC_PENDING_RETRY_PAUSE_MS`, `GSCFW_MAX_ROUND_TRIP_LATENCY_MS`, init/fini, session create/end, and readiness predicate. Stubs are provided when PXP is disabled.

Control flow: Header only; timeout macro combines base HECI reply latency with retry budget.

State/persistence: No state, but APIs operate on `pxp->gsccs_res`.

Dependencies/integration: Includes GSC HECI submit header for latency constants. Used by top-level PXP and PM/debugfs timeout logic.

Risks: Timeout constant influences user-visible readiness/termination waits; too short yields false timeout, too long delays suspend and debugfs operations. Disabled-config stubs return no readiness.

Test signals: Build across config variants and timeout behavior in PXP start/end paths.
