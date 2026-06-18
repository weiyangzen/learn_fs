# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_trace_lrc.h

Purpose: Defines a focused tracepoint for logical ring context timestamp updates.

Important APIs/types/functions: `TRACE_EVENT(xe_lrc_update_timestamp)` records the `struct xe_lrc *`, old timestamp, new `lrc->ctx_timestamp`, LRC fence-context name, and device id.

Control flow: LRC update paths call the tracepoint after updating or while comparing timestamp state, passing the old timestamp so the trace entry can show old/new values.

State and persistence behavior: The tracepoint is observational only. It snapshots LRC timestamp values and string data from the fence context.

Dependencies and integration points: Includes GT and LRC headers and uses `gt_to_xe((lrc)->fence_ctx.gt)` to derive the device name. Integrated with LRC/context restore or accounting paths that maintain `ctx_timestamp`.

Risks: Callers must pass an initialized LRC with a valid `fence_ctx.gt` and name. Timestamp trace interpretation depends on call-site semantics, especially whether `old` is pre-update or last-observed state.

Test signals: Run workloads that update LRC timestamps and inspect trace output for monotonic or expected old/new transitions per context.
