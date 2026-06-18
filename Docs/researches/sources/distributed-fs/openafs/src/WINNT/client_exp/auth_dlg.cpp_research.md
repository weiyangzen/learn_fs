# sources/distributed-fs/openafs/src/WINNT/client_exp/auth_dlg.cpp

Purpose: implements the Explorer extension authentication dialog showing current AFS tokens and launching get/discard token dialogs.

Important APIs/functions: `CAuthDlg` constructor, `OnInitDialog`, `OnGetTokens`, `OnDiscardTokens`, `FillTokenList`, `GetSelectedCellName`, and `OnHelp`.

Control flow: initialization configures hidden tab stops so each list item can include an invisible cell-name field, then fills the list from `GetTokenInfo`. Get/discard buttons create `CKlogDlg` or `CUnlogDlg`, seed them with the selected cell, and refresh the token list on success.

State/persistence: no local persistence; token state is changed by klog/unlog dialogs and `gui2fs` token operations.

Dependencies/integration: depends on `gui2fs`, `klog_dlg`, `unlog_dlg`, MFC listbox controls, localized resources, and help IDs.

Risks: hidden cell parsing depends on tab-delimited `GetTokenInfo` string format. If no token is selected, an empty cell is passed to dialogs, which must handle default behavior.

Test signals: empty token list, multiple token entries, selected-cell parsing, get-token success/failure, discard-token success/failure, and help display.
