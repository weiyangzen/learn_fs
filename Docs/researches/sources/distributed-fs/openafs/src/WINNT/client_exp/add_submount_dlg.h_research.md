# sources/distributed-fs/openafs/src/WINNT/client_exp/add_submount_dlg.h

Purpose: declares the add/edit submount dialog.

Important APIs/types: `CAddSubmtDlg` exposes `SetAddMode`, `SetSubmtInfo`, and `GetSubmtInfo`; tracks share and path strings through DDX.

Control flow: callers configure add/edit mode and optional existing info, run the dialog, then retrieve a new `CSubmountInfo` if saved.

State/persistence: pending share/path and save/add flags; no direct registry or filesystem writes.

Dependencies/integration: forward-declares `CSubmountInfo`, uses MFC controls and resource IDs.

Risks: no include guard in this header. Ownership of `GetSubmtInfo` result is manual and must be documented by callers.

Test signals: inclusion in submount management UI and object ownership handling.
