# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/TaAfsUsrMgr.h

Purpose: central umbrella header for AFS Account Manager, analogous to Server Manager's `svrmgr.h`.

Important API/types: defines common size constants, registry paths under `HKCU\Software\OpenAFS\AFS Account Manager`, help filename, `ICONVIEW`, `GLOBALS`, and `GLOBALS_RESTORED`. `GLOBALS` stores app/window handles, admin-server client id, active cell ASID, credentials, and search patterns. `GLOBALS_RESTORED` stores main/action window placement, views for users/groups/machines/actions, icon modes, warning/show flags, refresh rate, last tab, create defaults, and user search parameters. Declares global `g`, `gr`, `Quit`, `PumpMessage`, and `StartThread`.

Control flow contract: almost every Account Manager source includes this header to get shared state, task prototypes, display/general helpers, property dialogs, and error data.

State and persistence: defines the binary settings state persisted by the Account Manager. Version `wVerGLOBALS_RESTORED` guards restore compatibility.

Dependencies/integration: includes `TaLocale`, `TaAfsAdmSvrClient`, `AfsAppLib`, resource/help headers, user/group property headers, `task.h`, `display.h`, `general.h`, and `errdata.h`.

Risks/test signals: broad inclusion couples unrelated modules and makes global state easy to mutate. Struct layout changes require version bumps and default initialization. Tests should cover settings restore defaults, command-line opening, active cell/client id initialization, and view persistence.
