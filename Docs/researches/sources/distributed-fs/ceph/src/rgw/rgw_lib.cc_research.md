# sources/distributed-fs/ceph/src/rgw/rgw_lib.cc

Purpose: Implements the embedded librgw frontend/process used by RGW-as-a-library clients such as NFS-style integrations. It initializes RGW subsystems, processes in-memory requests through normal RGW operation machinery, and manages mounted filesystem garbage collection.

Important APIs and functions: `RGWLibProcess::run()`, `handle_request()`, `process_request()`, `start_request()`, and `finish_request()` execute regular and continued requests. `RGWLibFrontend::init()` creates the process. `RGWLib::init()` and `stop()` initialize and shut down the RGW daemon stack. `RGWLibIO::set_uid()` loads a user. `RGWLibRequest::read_permissions()` builds bucket/object policies. `RGWHandler_Lib::authorize()` grants full control to the cached user.

Control flow: Initialization calls `rgw_global_init()`, sets librgw defaults, arms an init timeout, initializes frontends, common Ceph state, perf counters, HTTP clients, storage, APIs, LDAP, opslog, signal handling, tracepoints, frontends, Lua, and optionally dedup. Request processing constructs `RGWLibIO` and `req_state`, initializes the request/handler, initializes the `RGWOp`, authorizes, transforms legacy auth info if needed, reads policies, verifies op mask/permissions/params, then executes and completes the op. Continued requests split execution into start and finish callbacks.

State and persistence: `g_rgwlib` is the global instance pointer. `RGWLibProcess` tracks mounted `RGWLibFS` instances, a generation counter, and a shutdown flag. Its run loop periodically calls filesystem GC and user update based on namespace expiration config. Requests mutate normal RGW backend state through SAL and RGW operations.

Dependencies and integration points: Depends on `rgw_main`, RGW REST/op/auth/log/process infrastructure, `RGWLibFrontend`, `RGWLibFS`, perf counters, signal handlers, timers, and Ceph global initialization. It deliberately reuses standard RGW op logic rather than a separate object path.

Risks: Authorization is simplified and grants full control to the supplied user, so correctness relies on mount-time identity handling. `abort_req()` increments failed counters but does not emit HTTP responses. The GC loop releases and reacquires its mutex around filesystem calls and restarts iteration when generation changes.

Test signals: Tests should cover init failure cleanup, request init/auth/policy failures, admin permission override, continued request lifecycle, mounted filesystem registration churn during GC, shutdown signal cleanup, and `set_uid()` user load failures.
