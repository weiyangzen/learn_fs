<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/db_server_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/db_server_page.cpp

Purpose: Implements the wizard page for configuring or skipping this host as a database server and collecting a System Control Machine hostname for CellServDB propagation.

Important APIs/functions: `DBServerPageDlgProc`, `OnInitDialog`, `ConfigMsg`, `EnableSCM`, `ShowPageInfo`, and `SavePageInfo`.

Control flow: First-server mode forces database configuration and hides choices. Otherwise, the page restores the database selection, enables the SCM edit field only when configuring DB service, saves the SCM field on Next/Back, and navigates between file-server and backup-server pages.

State and persistence: Mutates `g_CfgData.configDB` and `g_CfgData.szSysControlMachine`. No durable writes occur until the final config step starts database services and possibly updates CellServDB through that SCM.

Dependencies and integration points: Uses common wizard handling, UI helpers, resource strings, and `CFG_DATA` shared state. The final config page consumes the DB flag to choose db/bak and CellServDB restart steps.

Risks: No validation is performed on the SCM hostname here. First-server mode returns early without showing existing page info. Disabling the SCM field does not clear stale `szSysControlMachine`.

Test signals: Test first-server forced mode, already-configured mode, configure/don't configure toggles, SCM enable/disable and persistence, and navigation preserving edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/db_server_page.cpp -->
