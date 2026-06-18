# sources/distributed-fs/openafs/src/WINNT/client_exp/copy_acl_dlg.h

Purpose: declares the ACL copy dialog class.

Important APIs/types: `CCopyAclDlg : public CDialog`; public getters `GetToDir`, `GetClear`, and setter `SetFromDir`; MFC controls for OK, source, target, and clear checkbox.

Control flow: caller sets source, runs dialog, then reads target/clear options.

State/persistence: local dialog fields only.

Dependencies/integration: MFC and resource ID `IDD_COPY_ACL`.

Risks: no include guard; target validation details are hidden in implementation.

Test signals: construction from ACL property page and option propagation to `CopyACL`.
