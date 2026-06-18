# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_guc.c

Purpose: Instantiates GuC communication and engine activity tracepoints declared in `xe_trace_guc.h`.

Important APIs/types/functions: Contains no exported functions; it creates generated tracepoint definitions for GuC CT flow-control, CTB H2G/G2H messages, and GuC engine activity events.

Control flow: Defines `CREATE_TRACE_POINTS` before including `xe_trace_guc.h`, except for sparse checker builds. The Linux tracepoint machinery turns the header macros into concrete trace event definitions.

State and persistence behavior: No independent runtime state. Generated tracepoint symbols persist as part of the built driver.

Dependencies and integration points: Depends on `xe_trace_guc.h`; call sites in GuC CT and engine activity code use the generated events.

Risks: Duplicate instantiation or missing build inclusion causes tracepoint linkage issues. The checker guard must be preserved to keep static analysis clean.

Test signals: Build validation plus runtime visibility of `xe_guc_ct_*`, `xe_guc_ctb_*`, and `xe_guc_engine_activity` events under the Xe trace subsystem.
