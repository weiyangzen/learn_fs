# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_general.cpp

Purpose: Provides service preference loading/saving and default log-name inference.

Important APIs/functions: `Services_GuessLogName` maps known service names to log filenames. `Services_LoadPreferences` restores `SERVICE_PREF`, initializes defaults if absent, initializes alerts, and stores guessed log file on first creation. `Services_SavePreferences` writes current service preferences.

Control flow: On load, `RestorePreferences` fills the struct; if missing, defaults are set (`fWarnSvcStop`, alert defaults, guessed log path) and immediately stored. `Alert_Initialize` runs for restored and new prefs.

State and persistence: Persists `SERVICE_PREF` by identity via `StorePreferences`. The `szLogFile` preference is used by log viewing.

Dependencies/integration: Depends on global preference helpers, alert helpers, and service identities.

Risks: Log-name mapping is hard-coded and case-insensitive but limited to known services. Immediate store on first load writes guessed defaults even before user action.

Test signals: First-load defaults, restored prefs, unknown/upclient/upserver services with empty log, and save failure propagation.
