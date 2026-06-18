# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_prop.cpp

Purpose: Implements server property sheets. The General tab shows server status/capacity/addresses and supports auth/address changes. The Scout tab configures monitoring warnings and auto-refresh.

Important APIs/functions: `Server_ShowProperties` builds cached problems/general/scout property sheets. `Server_General_DlgProc` handles init, auth toggles, and address change. `Server_General_OnEndTask_InitDialog` renders `taskSVR_PROP_INIT` data. `Server_General_OnAuth` dispatches `taskSVR_SETAUTH` after warning for disable. `Server_General_OnChangeAddr` runs the address modal and starts `taskSVR_CHANGEADDR`. `Server_Scout_DlgProc` and helpers load/apply warning preferences through `taskSVR_SCOUT_INIT`/`taskSVR_SCOUT_APPLY`.

Control flow: General tab disables controls until status task returns, then enables auth/address controls and displays aggregate count, capacity, allocation, and addresses. Scout tab disables all controls until preference init returns, then initializes checkboxes and spinners for aggregate-full, fileset-full, service stop, server timeout, VLDB/server mismatch, aggregate allocation/no-server, and auto-refresh minutes.

State and persistence: General auth/address changes are remote server state via tasks. Scout apply sends `SVR_SCOUT_APPLY_PACKET`, which represents preference fields and auto-refresh period; persistence handled by task/server preference code. Spinners enforce percentage/minute bounds.

Dependencies/integration: Depends on `svr_address.h`, `svr_general.h`, `problems.h`, `propcache.h`, alert/preference structures, and task dispatch.

Risks: `WM_CTLCOLORLISTBOX` creates a new brush without ownership management. Auth disable warning is UI-only; task must still enforce authorization. Scout controls are enabled broadly after init; command handlers for all checkboxes must keep dependent controls in sync. Auto-refresh stores minutes but task code must convert to ticks consistently.

Test signals: Failed status/preference init, address list display, auth enable/disable confirmation, address change OK/cancel, each scout warning toggle and spinner, auto-refresh toggle, apply failure, and property sheet caching.
