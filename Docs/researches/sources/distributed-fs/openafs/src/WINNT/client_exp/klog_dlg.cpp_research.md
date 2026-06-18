## sources/distributed-fs/openafs/src/WINNT/client_exp/klog_dlg.cpp

Purpose: Implements the token-acquisition dialog for Kerberos/AFS authentication from the Explorer extension.

Important APIs/functions: `kl_Authenticate` wraps `ka_UserAuthenticateGeneral`. `CKlogDlg::OnInitDialog` defaults the cell from `cm_GetRootCellName`; `OnOK` validates user input, calls authentication, and reports the returned reason on failure. Change handlers enable OK only when cell, name, and password are present.

Control flow/state: Dialog state is stored in `m_strName`, `m_strPassword`, and `m_strCellName`. No persistent state is written; successful authentication updates AFS token state via the auth library.

Dependencies/integration: Uses MFC DDX, `TaLocale_GetDialogResource`, `HOURGLASS`, OpenAFS `kautils`, and `cm_config`. Help routes to `GET_TOKENS_HELP_ID`.

Risks/tests: Password remains in a `CString` until dialog teardown. ANSI conversion under Unicode uses `CStringA` with process code page rather than UTF-8. Test default-cell failure, bad password reason display, Unicode principal/cell handling, empty-field OK enablement, and unavailable auth/cache manager.
