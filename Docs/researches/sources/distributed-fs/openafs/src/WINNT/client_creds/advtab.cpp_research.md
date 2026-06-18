# sources/distributed-fs/openafs/src/WINNT/client_creds/advtab.cpp

Purpose: implements the Advanced tab in `afscreds.exe`, exposing AFS service status/start/stop/autostart controls, Control Panel launch, and tray startup preference.

Important APIs/functions: `Advanced_DlgProc` dispatches dialog events; `Advanced_OnServiceTimer` queries `TransarcAFSDaemon` status/config and updates UI; `Advanced_OnChangeService` changes service start type or starts/stops the service; `Advanced_OnOpenCPL` launches `afs_config.exe`; `Advanced_OnStartup` persists tray startup configuration and shortcut state.

Control flow: initialization sets the startup checkbox and begins a service polling timer. Service operations open SCM/service handles with required access, perform `ChangeServiceConfig`, `StartService`, or `ControlService`, then restart polling and refresh tabs when transitions settle. On start, drive mappings are attempted and KFW token renewal may run.

State/persistence: reads service state and start type from SCM; writes `ShowTrayIcon` under the client service parameter registry key and updates the Startup shortcut through `Shortcut_FixStartup`.

Dependencies/integration: integrates with `Main_RepopulateTabs`, drive mapping functions (`TestAndDoMapShare`, `TestAndDoUnMapShare`), KFW renewal, `TaLocale`, and the Windows SCM.

Risks: service-handle cleanup is uneven in the stop path; error capture can be generic if SCM calls fail before `GetLastError`. Repeated `TestAndDoMapShare` calls happen in polling and status refresh. Requires administrative rights for service configuration.

Test signals: service missing/stopped/running/pending UI states, start/stop failures, auto-start registry updates, mapping renewal on service start, and behavior under non-admin users.
