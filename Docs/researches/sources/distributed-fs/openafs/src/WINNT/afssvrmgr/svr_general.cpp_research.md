# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_general.cpp

Purpose: Provides server preference initialization/saving and server context-menu construction.

Important APIs/functions: `Server_LoadPreferences` restores or initializes `SERVER_PREF` defaults for alert thresholds, warning flags, window state, monitor/open state, and tree expansion. `Server_SavePreferences` stores preferences. `Server_ShowPopupMenu` and `Server_ShowParticularPopupMenu` show empty/server-specific context menus with checked/disabled items based on view state, monitor state, and open property windows.

Control flow: Preferences default to monitored until dispatch later decides otherwise. Empty menu checks server view mode and icon view and disables close-all if no server property windows are cached. Server menu toggles open/close/monitor and disables sensitive operations for unmonitored servers.

State and persistence: Persists `SERVER_PREF` via `RestorePreferences`/`StorePreferences`. Reads globals `gr.fPreview`, `gr.fVert`, `gr.diHorz/diVert`, `gr.fOpenMonitors`, and display icon view.

Dependencies/integration: Uses prop cache, display helpers, alert defaults, menu helpers, and identity user params.

Risks: Monitor state is initialized optimistically and corrected elsewhere; early UI may briefly show monitored behavior. Context-menu gating is UI-only and must be mirrored by command handlers.

Test signals: First-load prefs, restored prefs, monitored/unmonitored server menus, open/close state, empty-area view checks, close-all enablement, and preference save after tree expansion/window state changes.
