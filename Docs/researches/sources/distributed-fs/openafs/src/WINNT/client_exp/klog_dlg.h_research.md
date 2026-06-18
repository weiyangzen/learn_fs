## sources/distributed-fs/openafs/src/WINNT/client_exp/klog_dlg.h

Purpose: Declares the `CKlogDlg` MFC dialog used to obtain AFS tokens.

Important APIs/types: The class exposes `SetCellName`, dialog ID `IDD_KLOG_DIALOG`, bound controls for OK/name/password/cell, and handlers for initialization, OK, field changes, and help.

Control flow/state: Private `CheckEnableOk` enforces required field state; mutable dialog fields are MFC `CString`s.

Dependencies/integration: Includes `resource.h`; implementation depends on MFC and OpenAFS auth libraries. Called from authentication UI flows.

Risks/tests: Header has no include guard. Test compilation in repeated include contexts and resource/control ID consistency.
