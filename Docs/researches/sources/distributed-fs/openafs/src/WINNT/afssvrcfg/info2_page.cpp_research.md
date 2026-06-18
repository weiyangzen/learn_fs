<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info2_page.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info2_page.cpp

Purpose: Implements the second wizard information page, collecting admin credentials/UID for a new first server or admin credentials plus CellServDB host for joining an existing cell.

Important APIs/functions: `InfoPage2DlgProc`, `OnInitDialog`, `CheckEnableButtons`, `SavePageInfo`, `ShowPageInfo`, and `UseNextUid`. It uses `FIRST_SERVER_STEP` and `NOT_FIRST_SERVER_STEP` to disable the irrelevant wizard state dynamically.

Control flow: The page enables Next only when required fields are populated and password verification matches when visible. First-server mode collects admin name, password, password verification, and either next UID or explicit UID. Existing-cell mode collects admin name/password and a host name to fetch CellServDB. Next proceeds to file-server selection; Back returns to the first info page.

State and persistence: Writes `g_CfgData.szAdminName`, `szAdminPW`, `bUseNextUid`, `szAdminUID`, and `szCellServDbHostname`. No durable writes until final config creates/logs in with the admin principal.

Dependencies and integration points: Uses wizard state-disable notifications, spin control helpers, resource IDs, and global config state. Final config uses these credentials for token acquisition, admin principal creation, and CellServDB enumeration.

Risks: No explicit validation of hostname, UID range beyond spinner range, or admin name syntax here. Passwords are kept in global memory. `lstrncpy` may not guarantee null termination at maximum length.

Test signals: Test first-server and existing-cell page selection, password mismatch, empty fields, UID toggle/spinner boundaries, navigation persistence, and overlong admin/password/hostname input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/info2_page.cpp -->
