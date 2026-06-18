# sources/distributed-fs/openafs/src/WINNT/client_exp/clear_acl_dlg.h

Purpose: declares the clear-ACL options dialog.

Important APIs/types: `CClearAclDlg : public CDialog`, `GetSettings(BOOL& bNormal, BOOL& bNegative)`, resource ID `IDD_CLEAR_ACL`, and checkbox booleans.

Control flow: callers run modal dialog then inspect selected settings.

State/persistence: local checkbox state only.

Dependencies/integration: uses MFC and resource IDs.

Risks: no include guard; validation policy is not explicit.

Test signals: inclusion from ACL-management UI and expected checkbox settings after user interaction.
