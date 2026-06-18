# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt-trace.h

Purpose: Declares trace events for RTRS client connection/path state transitions and reconnect/error-recovery diagnostics.

Important APIs/types/functions: Defines `TRACE_SYSTEM rtrs_clt`, declares enum symbols for `RTRS_CLT_*` states, maps them through `show_rtrs_clt_state()`, declares event class `rtrs_clt_conn_class`, and instantiates `rtrs_clt_reconnect_work`, `rtrs_clt_close_conns`, and `rtrs_rdma_error_recovery` events via `DEFINE_CLT_CONN_EVENT()`.

Control flow: Each event takes a `struct rtrs_clt_path *`, captures the path state, reconnect attempts, session max reconnect attempts, fail/success reconnect counters, and kobject session/path name, then formats a trace line with symbolic state and counters.

State and persistence: The header stores no runtime state itself, but it defines trace event fields copied from `rtrs_clt_path`, `rtrs_clt_sess`, and path stats at the emission point.

Dependencies and integration: Depends on Linux tracepoint macros plus `rtrs-clt.h` definitions being visible in the translation unit that creates tracepoints. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE rtrs-clt-trace` match the local trace header build pattern.

Risks: The `memcpy()` of `kobject_name(&clt_path->kobj)` into a fixed `NAME_MAX` array assumes a valid, NUL-terminated name within bounds; trace output can be confusing if kobject lifetime is racing with path destruction. Enum mappings must stay synchronized with client state enum values. Test signals include trace event enablement during reconnect, close, and RDMA error recovery; state-name formatting for each enum; and build coverage when trace headers are included multiple times.
