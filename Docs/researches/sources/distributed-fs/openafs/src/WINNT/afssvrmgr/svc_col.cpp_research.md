# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_col.cpp

Purpose: Provides default service list column configuration and text formatting for service rows.

Important APIs/functions: `Services_SetDefaultView` initializes `VIEWINFO` with all available columns and default shown columns. `Services_GetAlertCount` delegates to `Alert_GetCount`. `Services_GetColumnText` returns formatted text for name, type, params, notifier, state, dates, and last error.

Control flow: Column text is pulled from `SERVICE_PREF::ssLast` stored in the service identity user param. Name can include server prefix when requested. Params/notifier sanitize CR/LF/tab to spaces. Date columns use `FormatTime`; start/stop combined column labels date based on current running/stopped state.

State and persistence: Uses a rotating static buffer array sized by `nSERVICECOLUMNS`; callers must consume text before enough subsequent calls overwrite it. View preferences are written into caller-provided `VIEWINFO`.

Dependencies/integration: Depends on `svc_col.h`, alert system, service status/preference structures, and localization strings.

Risks: Static buffers are not thread-safe and limit nested use. If `GetUserParam()` is missing, most columns return empty text. `svccolLASTERROR` always formats an error number if status exists, even if zero.

Test signals: Service rows with no loaded prefs, each service type/state, multiline params/notifier, invalid dates, show-server-name mode, and repeated column callbacks.
