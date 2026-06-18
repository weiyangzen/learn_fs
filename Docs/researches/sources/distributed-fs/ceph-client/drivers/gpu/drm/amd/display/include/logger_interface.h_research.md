# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/logger_interface.h

Purpose: Declares display logging/tracing entry points and convenience macros that map DC events to DRM/kernel logging categories. It also provides one-shot not-implemented logging and performance/display statistics helpers.

Important APIs and types: Functions `update_surface_trace`, `post_surface_trace`, and `context_clock_trace` emit structured DC traces. Macros include `DAL_LOGGER_NOT_IMPL`, `DC_ERROR`, `DC_SYNC_INFO`, connection logging helpers (`CONN_DATA_DETECT`, `CONN_DATA_LINK_LOSS`, `CONN_MSG_LT`, `CONN_MSG_MODE`), DTN logging wrappers, `PERFORMANCE_TRACE_START/END`, `DISPLAY_STATS_*`, and `LOG_GAMMA_WRITE`.

Control flow: Callers include this header, rely on an in-scope `dc_ctx`, `dc`, `log_ctx`, or `link` depending on macro, and emit logging through lower-level macros from `logger_types.h`. `DAL_LOGGER_NOT_IMPL` uses a static local guard so each call site logs only once.

State and persistence: Most macros are stateless wrappers. `DAL_LOGGER_NOT_IMPL` persists a per-call-site static boolean. Performance macros store local timestamp variables and conditionally log when debug flags are set.

Dependencies and integration points: Includes `logger_types.h`; references `dc`, `dc_context`, `dc_link`, `dc_surface_update`, `resource_context`, `dc_state`, DRM logging, and DM timestamp helpers. Integrated throughout display detection, link training, mode setting, performance tracing, and gamma debug code.

Risks: Macro APIs rely on ambient variable names and can fail or log wrong context if used outside expected scopes. `LOG_GAMMA_WRITE` is empty in this header, so gamma distribution logging compiles away unless overridden. One-shot static logging is not reset across device lifetimes.

Test signals: Compile coverage for macro call sites, dynamic debug output for detection/link training/mode set, performance trace enablement, and confirmation that not-implemented warnings are rate-limited.
