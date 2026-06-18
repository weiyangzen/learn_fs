# sources/distributed-fs/openafs/src/WINNT/client_config/tab_general.cpp

## Purpose
`tab_general.cpp` implements the General tab: service status/start/stop, cell and gateway settings, integrated logon authentication, tray icon preference, validation, restart prompts, and status polling.

## Important APIs, Types, and Functions
Key routines include `GeneralTab_DlgProc`, `GeneralTab_OnInitDialog`, `GeneralTab_VerifyCell`, `GeneralTab_OnApply`, `GeneralTab_OnRefresh`, `GeneralTab_OnTimer`, `GeneralTab_OnStartStop`, `GeneralTab_AskIfStopped`, `GeneralTab_DoStartStop`, `fIsCellInCellServDB`, and `Status_DlgProc`.

## Control Flow
Initialization starts a refresh timer and loads current configuration. Apply first commits Hosts and Advanced tabs, validates gateway/cell state, writes changed cell/logon/tray/gateway values, and for Win9x gateway changes contacts the gateway and fixes drive mappings. The timer polls service state, opens/closes a modeless starting/stopping dialog, refreshes all tabs on state changes, and calls `TestAndDoMapShare` for drive remapping after service start. Start/stop commits config as needed and controls `TransarcAFSDaemon` through SCM.

## State and Persistence Behavior
The file tracks transient service UI state in a static `l` struct. Persistent state includes registry-backed cell/gateway/logon/tray settings and service state outside the process. `g.fNeedRestart` controls restart prompts after changes requiring AFSD restart.

## Dependencies and Integration Points
It integrates with `Config_*`, `HostsTab_CommitChanges`, `AdvancedTab_CommitChanges`, CellServDB/DNS cell validation, Windows SCM, drive-map logon hooks, and Control Center mode.

## Risks and Edge Cases
Cell-name conversion assumes ASCII. `fIsCellInCellServDB` has an unused `done:` label and combines registry, file, and DNS lookup with different failure semantics. Start/stop operations set warning flags and then rely on timer polling rather than synchronous service-state waits. Partial commits in Hosts/Advanced can persist before General validation fails.

## Test Signals
Tests should cover valid/invalid cells from registry, CellServDB and DNS; admin versus non-admin UI gating; start, stop, restart, and failure paths; gateway contact on non-NT mode; integrated logon flag persistence; and restart prompt behavior after advanced changes.
