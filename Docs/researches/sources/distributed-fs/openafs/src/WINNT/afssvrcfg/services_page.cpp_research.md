<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/services_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/services_page.cpp

## Purpose
Implements the Services property page for the Windows OpenAFS server configuration tool, letting administrators toggle file, database, backup, system-control server, and system-control client roles.

## Important APIs, Types, And Functions
`ServicesPageDlgProc` handles dialog messages. `ShowInitialConfig`, `ShowServiceStates`, `CheckEnableBak`, and `CheckEnableSc` synchronize controls with `g_CfgData`. `PrepareToConfig` maps UI deltas to `CONFIG_STATE` values and calls the external `Configure`.

## Control Flow
Initialization snapshots current service state, sets checkbox/status/action text, and bolds labels. Command handlers toggle requested state and recompute dependencies. Apply computes local deltas, handles the last-database-server confirmation/forced unconfigure path, gathers admin/system-control info, updates `g_CfgData`, runs configuration, refreshes current config, and redraws state.

## State And Persistence
Dialog-static booleans track running and requested state; `szScMachine` tracks SCC target. Durable changes are indirect through `Configure`; admin reuse/password fields in `g_CfgData` are adjusted after success/failure.

## Dependencies And Integration Points
Depends on `afscfg.h`, resource IDs, admin-info/current-config helpers, property-sheet dirty state, and the configuration engine.

## Risks And Edge Cases
Backup depends on DB; SCS/SCC are mutually exclusive and require FS or DB. Unconfiguring the last DB server can unconfigure all roles and exit. `bDbParial` is misspelled and never set here; SCC machine text is enabled before copying `g_CfgData.szSysControlMachine`.

## Test Signals
Cover role combinations, dependency disabling, SCC machine validation, last-DB cancellation/acceptance, credential failure/reuse, and property-sheet changed/unchanged transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/services_page.cpp -->
