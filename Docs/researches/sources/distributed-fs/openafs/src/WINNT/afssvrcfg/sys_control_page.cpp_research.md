<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/sys_control_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/sys_control_page.cpp

## Purpose
Implements the wizard page choosing system-control server, system-control client, or no system-control configuration.

## Important APIs, Types, And Functions
`SysControlPageDlgProc` dispatches wizard messages. `OnInitDialog` validates whether the step applies, adapts first-server layout, and initializes radio state. `CantConfig`, `EnableSysControlMachine`, and `CheckEnableNextButton` manage disabled UI and SCC machine-name requirements.

## Control Flow
Common wizard handling runs first. Radio commands write `g_CfgData.configSCS/configSCC`, enable or clear the machine edit field, and edit changes update Next-button availability. `IDNEXT` and `IDBACK` move between fixed wizard states.

## State And Persistence
Selections are stored directly in `g_CfgData`; actual persistence happens later when the wizard configures the machine. Static `hDlg` holds the current dialog.

## Dependencies And Integration Points
Uses `g_pWiz`, `g_CfgData`, resource strings, layout helpers, and step IDs `sidSTEP_TEN`/`sidSTEP_TWELVE`.

## Risks And Edge Cases
First-server layout manually hides/moves controls. Already-configured and non-FS/non-DB cases hide the choice controls. Empty SCC machine disables Next.

## Test Signals
Test all radio choices, first-server UI, already SCS/SCC, non-server disabling, and SCC machine empty/non-empty transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/sys_control_page.cpp -->
