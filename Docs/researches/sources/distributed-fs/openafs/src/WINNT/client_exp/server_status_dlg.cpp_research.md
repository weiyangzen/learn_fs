## sources/distributed-fs/openafs/src/WINNT/client_exp/server_status_dlg.cpp

Purpose: Implements the server-status dialog that triggers cache-manager server probing.

Important APIs/functions: `OnShowStatus` calls `CheckServers` with scope and fast-probe state. Radio handlers switch between local, all, and specified-cell modes. `GetCellNameText` reads the edit control; `CheckEnableShowStatus` gates the command when a specific cell is selected.

Control flow/state: Dialog state is `m_bFast`, `m_nCell`, and the cell-name edit. `Save` is a stub returning `FALSE`.

Dependencies/integration: Calls `gui2fs.cpp::CheckServers`, uses `WHICH_CELLS`, MFC DDX, resources, and `SERVER_STATUS_HELP_ID`.

Risks/tests: The header file is named `server_status_dlg.H` in the source tree while the requested research output covers only the `.cpp`. Test case-sensitive builds, radio state transitions, empty specified-cell behavior, fast/all/local flags, and cache-manager errors.
