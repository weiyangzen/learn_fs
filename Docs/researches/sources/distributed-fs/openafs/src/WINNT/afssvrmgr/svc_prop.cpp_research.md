# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_prop.cpp

Purpose: Implements service property sheets. The General tab shows status, type, params, notifier, start/stop dates, warning preference, start/stop/restart controls, and log viewer. The BOS-only tab configures restart schedules.

Important APIs/functions: `Services_ShowProperties` builds cached property sheets with problems/general/BOS tabs. `PropSheet_AddBOSTab` conditionally adds BOS tab. `Services_General_DlgProc` handles refresh, apply, and service control commands. `Services_General_OnEndTask_InitDialog` renders `taskSVC_PROP_INIT` data. `Services_BOS_DlgProc` and related helpers get/set restart times via `taskSVC_GETRESTARTTIMES` and `taskSVC_SETRESTARTTIMES`.

Control flow: General tab registers object-change notifications and refreshes on `evtRefreshStatusEnd` for the target service. Init disables controls until async status returns; success enables controls, formats status and dates, sanitizes params/notifier, and checks stop-warning prefs based on service and cell/server preference data. Start command restarts BOS but starts non-BOS; stop command invokes `Services_Stop`; view log invokes `Services_ShowServiceLog`. BOS tab populates recurrence controls, loads schedule asynchronously, and applies schedule packets.

State and persistence: General apply sends `SVC_PROP_APPLY_PACKET` with warning preference. BOS apply sends `SVC_RESTARTTIMES_PARAMS`. Actual preference and BOS restart-time persistence is in tasks/service APIs.

Dependencies/integration: Uses `svc_general.h`, `svc_startstop.h`, `svc_viewlog.h`, `propcache.h`, `problems.h`, time controls, alert/problem tabs, and notification dispatch.

Risks: The general tab creates a brush on each `WM_CTLCOLOR*`-like path in related code patterns; here main risks are stale async refreshes and disabling buttons during starting/stopping. BOS detection is by literal service name `"BOS"`. `Services_BOS_OnApply` does not use the dialog as task target, so failures may be reported elsewhere or not directly in this tab.

Test signals: Property sheet caching, failed status refresh, running/starting/stopping/stopped services, BOS vs non-BOS controls, warn-stop apply failure, view-log path, BOS schedule load/apply, and notification-triggered refresh.
