<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info_page.cpp

Purpose: Implements the first wizard information page for choosing first-server vs existing-cell setup, entering the cell name, and setting/verifying the server principal password for a first server.

Important APIs/functions: `InfoPageDlgProc`, `OnInitDialog`, `CheckEnableButtons`, `SavePageInfo`, `ShowPageInfo`, and `IsFirstServer`.

Control flow: The page enables Next when a cell name exists and, for first-server mode, both server password fields are non-empty and match. First-server selection enables server-principal/password controls; existing-cell selection disables them. Next advances to the first-server admin page state, with the next page deciding which of its two templates is enabled.

State and persistence: Writes `g_CfgData.szCellName`, `szServerPW`, and `bFirstServer`. The server password is later used to create/set the AFS server principal key.

Dependencies and integration points: Uses common wizard handling, UI helpers, resource strings, and `CFG_DATA` limits. Later pages and final config depend heavily on `bFirstServer`.

Risks: Cell-name validation here only checks length/non-empty; syntax validation is not applied. Password truncation can make a verified UI password differ from stored value if over limit. The principal label/control is enabled but no principal value is saved in this file.

Test signals: Test first-server and existing-cell toggles, password mismatch, max-length cell/password input, empty cell, back/next persistence, and downstream page disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info_page.cpp -->
