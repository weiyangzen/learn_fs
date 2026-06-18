# sources/distributed-fs/openafs/src/WINNT/client_exp/PropACL.h

Purpose: declares the ACL property page class for the Explorer extension.

Important types/APIs: `CPropACL` derives from `PropertyPage` and `CSetACLInterface`; it overrides `PropPageProc` and `IsNameInUse`. Private helpers manage ACL display, permission checkbox state, selection, removal, and permission string construction.

Control flow: no implementation. The class is instantiated with selected filenames and invoked through property sheet callbacks.

State/persistence: `m_Normal` and `m_Negative` hold pending ACL entries until apply.

Dependencies/integration: depends on `PropBase.h`, resource IDs, and `add_acl_entry_dlg.h` for the duplicate-name interface.

Risks: class stores ACLs as flat `CStringArray` pairs rather than a typed structure, making index mistakes easy.

Test signals: class construction from filename array, property page callback routing, and add-entry duplicate checks through the interface.
