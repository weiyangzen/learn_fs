<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/backup_server_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/backup_server_page.cpp

Purpose: Implements the wizard page that lets the user configure or skip the Backup Server component.

Important APIs/functions: `BackupPageDlgProc` handles page initialization, Next/Back navigation, and radio-button changes. `OnInitDialog` sets wizard buttons and decides whether the backup option is selectable. `CantBackup` replaces the options with an explanatory message. `CalcOptionButtonSeparationHeight` exposes `nOptionButtonSeparationHeight` for the system-control page layout.

Control flow: The page moves forward to the partition page and back to the database page. On init, an already-configured backup server or a machine not configured/configuring as a database server hides the choice. Otherwise, it restores the `CS_DONT_CONFIGURE` or `CS_CONFIGURE` choice from `g_CfgData.configBak`.

State and persistence: Mutates only `g_CfgData.configBak` and its disabled bit. No durable writes occur; the final configuration page later starts backup-related database servers based on this flag.

Dependencies and integration points: Uses common wizard handling, `ConfiguredOrConfiguring`, `EnableStep`, resource strings, and UI helpers from the application library/toolbox. The global option-spacing value is consumed by `sys_control_page.cpp`.

Risks: The page returns `FALSE` when the common dialog proc returns true, following the local pattern but making message consumption subtle. If database state changes on prior pages, backup can be disabled and the previous selected state remains under the `CS_DISABLED` bit.

Test signals: Test already-configured backup, no database server, database configured/configuring, toggling both radio buttons, forward/back navigation, and repeated visits after database selection changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/backup_server_page.cpp -->
