## sources/distributed-fs/openafs/src/WINNT/client_exp/submounts_dlg.h

Purpose: Declares the MFC dialog used to view and edit AFS submount registry mappings.

Important APIs/types: Public constructor/destructor and `SetAddOnlyMode` drive full-edit or one-shot-add behavior. Private helpers fill the list, apply changes, stage work, and locate staged entries.

Control flow/state: Private `m_bAddOnlyMode`, `m_strAddOnlyPath`, and `m_ToDo` govern staged registry persistence.

Dependencies/integration: Includes `resource.h` and `submount_info.h`; implementation depends on add-submount dialog and Win32 registry APIs.

Risks/tests: Verify destructor owns and deletes every staged pointer exactly once. Test `WinHelp` override and dialog resource/control ID consistency.
