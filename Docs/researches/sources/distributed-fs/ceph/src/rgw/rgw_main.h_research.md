## sources/distributed-fs/ceph/src/rgw/rgw_main.h

Purpose: declares the RGW daemon application coordinator and pauser aggregation helpers.

Important APIs/types: `RGWPauser` aggregates `RGWRealmReloader::Pauser` instances. `rgw::AppMain` owns frontends, REST dispatcher, Lua/dedup background services, LDAP, scheduler, rate limiter, realm reloader/watcher, period pusher, config store, site config, process environment, and context pool holder. Public initialization methods split RGW startup into storage, frontends, perf counters, HTTP clients, APIs, LDAP, opslog, tracing, Lua, KMS, and dedup phases.

Control flow: `AppMain` is constructed by `main()` or librgw, initialized in phases, then shut down through `shutdown()`. `rest_filter()` allows sync modules to wrap REST managers; `set_logging()` marks REST managers for operation logging.

State and persistence: `AppMain` owns long-lived process services and `RGWProcessEnv`, including the active SAL driver. Static `ops_log_file` is the process-level file log sink.

Dependencies/integration: central integration point for RGW frontends, realm reload, Lua background, RADOS features, config store, scheduling, and rate limits.

Risks and test signals: init/shutdown ordering is critical because many members hold non-owning references into `env.driver` and `CephContext`. Tests should verify pauser propagation, frontend-free librgw modes, realm reload with Lua/dedup paused, and static ops-log file cleanup.
