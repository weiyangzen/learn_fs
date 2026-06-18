<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/help.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/help.cpp

Purpose: Registers WinHelp context mappings for all wizard pages, config-manager pages, and modal dialogs in the AFS server configuration UI.

Important APIs/functions: `RegisterWizardHelp` registers overview and control-level help for intro, info, file/db/backup/partition/root/replication/system-control/config pages and password prompt. `RegisterConfigToolHelp` registers help for partition creation, partitions/services pages, admin-info, password, salvage, and salvage-results dialogs. Static `IDH_*` values and `DWORD` arrays map resource control IDs to help topic IDs.

Control flow: `afscfg.cpp` calls the appropriate registration function before showing the wizard or property sheet. Dialog procedures then delegate `WM_HELP`/`IDHELP` handling to `AfsAppLib_HandleHelp`.

State and persistence: No durable state in this file; registrations populate app-library process-global help tables.

Dependencies and integration points: Depends on resource IDs and `WINNT/afsapplib` help registration. It must stay synchronized with dialog templates and localized help content.

Risks: Help IDs are hand-maintained static integers; mismatches are easy and not compile-checked. `IDD_CONFIG_SERVER_PAGE` is registered for wizard help, while the config-manager modal uses `IDD_CONFIG_SERVER`, so coverage depends on which dialog invokes app-library help. WinHelp is legacy.

Test signals: Press Help/F1 on every dialog/control, verify overview pages, verify config-manager vs wizard registrations, and check for stale control IDs after resource changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/help.cpp -->
