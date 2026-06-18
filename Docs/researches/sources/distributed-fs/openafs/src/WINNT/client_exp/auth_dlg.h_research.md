# sources/distributed-fs/openafs/src/WINNT/client_exp/auth_dlg.h

Purpose: declares the authentication/token management dialog class.

Important APIs/types: `CAuthDlg : public CDialog` with `FillTokenList`, `GetSelectedCellName`, and MFC handlers for initialization, get tokens, discard tokens, and help. It owns `m_TokenList`.

Control flow: callers run the modal dialog; handlers delegate token changes to sub-dialogs.

State/persistence: in-memory listbox state only.

Dependencies/integration: uses MFC and resource ID `IDD_AUTHENTICATION`.

Risks: no include guard. Token-list item format is implicit between implementation and `gui2fs`.

Test signals: modal construction, list refresh, and selected-cell propagation to klog/unlog dialogs.
