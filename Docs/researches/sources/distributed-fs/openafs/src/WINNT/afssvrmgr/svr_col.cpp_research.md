# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_col.cpp

Purpose: Provides default server list view settings and server row column text.

Important APIs/functions: `Server_SetDefaultView_Horz` and `Server_SetDefaultView_Vert` initialize horizontal/vertical server `VIEWINFO`. `Server_GetAlertCount` delegates to alerts. `Server_GetColumnText` formats server name, first address, and quick status/alert description.

Control flow: Column formatting reads `SERVER_PREF::ssLast` from identity user param for address; status uses `Alert_GetQuickDescription` with fallback to no-alerts text.

State and persistence: Uses rotating static buffers sized by `nSERVERCOLUMNS`; caller-provided `VIEWINFO` receives default columns and sort.

Dependencies/integration: Used by display code and column callbacks.

Risks: Only the first address is shown. Static buffers are not thread-safe. Missing preferences produce empty address but still can show alert status.

Test signals: Server with no prefs, multiple addresses, alert/no-alert states, vertical vs horizontal defaults, and repeated callback usage.
