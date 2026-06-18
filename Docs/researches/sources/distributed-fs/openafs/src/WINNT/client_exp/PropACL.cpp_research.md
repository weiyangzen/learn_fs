# sources/distributed-fs/openafs/src/WINNT/client_exp/PropACL.cpp

Purpose: implements the ACL property page shown by the Explorer shell extension for a single AFS directory/file selection.

Important APIs/functions: `CPropACL::PropPageProc`, `FillACLList`, `ShowRights`, `MakeRightsString`, `EnablePermChanges`, `OnSelChange`, `OnRemove`, `IsNameInUse`, and `OnPermChange`.

Control flow: on initialization it stores the page object in window user data, sets resources, disables editing for multi-selection, or calls `GetRights` to load normal and negative ACL arrays. Button handlers add entries via `CAddAclEntryDlg`, copy ACLs via `CCopyAclDlg`, remove selected entries, clean ACLs, or update rights checkboxes. On apply it calls `SaveACL` with the edited arrays.

State/persistence: keeps pending ACL edits in `m_Normal` and `m_Negative` arrays as name/right pairs until property sheet apply. Persistent effects occur through `SaveACL`, `CopyACL`, and `CleanACL`.

Dependencies/integration: integrates MFC property sheets, localized resources, `gui2fs` filesystem operations, ACL helper dialogs, and `CSetACLInterface` for duplicate-name validation.

Risks: list index mapping assumes normal entries precede negative entries and arrays are exact name/right pairs. Multi-select apply still references `filenames.GetAt(0)` if the sheet sends apply, though controls are disabled. Permission changes do not appear to mark the page changed for add/remove in every path.

Test signals: load rights, add duplicate names, add normal/negative entries, multi-select disabled state, checkbox-to-rights ordering, remove multiple selections, apply/save failure behavior, and copy/clean ACL flows.
