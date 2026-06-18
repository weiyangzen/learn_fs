# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_lrc.c

Purpose: Instantiates the logical-ring-context timestamp tracepoint declared in `xe_trace_lrc.h`.

Important APIs/types/functions: No direct APIs; it emits generated tracepoint definitions for `xe_lrc_update_timestamp`.

Control flow: Defines `CREATE_TRACE_POINTS` then includes the LRC trace header, guarded away from sparse checker runs.

State and persistence behavior: No mutable driver state. Only generated tracepoint metadata and symbols are produced.

Dependencies and integration points: Depends on `xe_trace_lrc.h`; LRC code calls the generated tracepoint when context timestamp changes.

Risks: Standard tracepoint instantiation risks: duplicate definitions, missing build entry, or checker incompatibility if the guard is removed.

Test signals: Build the driver and confirm `xe_lrc_update_timestamp` appears in the Xe trace event namespace when LRC timestamp updates are exercised.
