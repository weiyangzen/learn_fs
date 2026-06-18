## sources/distributed-fs/openafs/src/WINNT/client_exp/unlog_dlg.cpp

Purpose: Implements the dialog and helper for discarding AFS tokens.

Important APIs/functions: `kl_Unlog` calls `ktc_ForgetAllTokens` when the cell is empty or `ktc_ForgetToken` for the `afs` service principal in a specific cell. `OnInitDialog` defaults the cell using `cm_GetRootCellName`; `OnOK` invokes token removal and closes only on success.

Control flow/state: Dialog state is the cell-name string and OK control enablement. Token state is external to the process in the AFS credential/cache-manager layer.

Dependencies/integration: Uses MFC, OpenAFS token/auth APIs, `cm_config`, and `ShowHelp` with `DISCARD_TOKENS_HELP_ID`.

Risks/tests: Current UI disables OK for empty cell, preventing the `ktc_ForgetAllTokens` branch from the dialog even though the helper supports it. `strcpy(server.cell, astrCellName)` needs length validation. Test root-cell default, specific-cell unlog, all-token helper use, unavailable AFS service, and long/Unicode cell names.
