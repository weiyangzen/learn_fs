# sources/distributed-fs/openafs/src/WINNT/client_exp/add_submount_dlg.cpp

Purpose: implements a modal add/edit dialog for AFS submount entries.

Important APIs/functions: `CAddSubmtDlg` constructor, `OnInitDialog`, `CheckEnableOk`, edit-change handlers, `OnOK`, `SetSubmtInfo`, `GetSubmtInfo`, and `OnHelp`.

Control flow: the dialog initializes localized resources, optionally switches to edit mode by disabling share-name editing, enables OK only when both share and path are non-empty, records save intent on OK, and returns a new `CSubmountInfo` with `SIS_ADDED` or `SIS_CHANGED`.

State/persistence: local MFC fields `m_strShareName`, `m_strPathName`, `m_bAdd`, and `m_bSave`; no direct persistence. Caller owns returned `CSubmountInfo` and performs actual submount update.

Dependencies/integration: depends on `CSubmountInfo`, help IDs, messages, MFC DDX, and localized dialog templates.

Risks: `GetSubmtInfo` allocates with `new`, so callers must delete. Validation only checks non-empty fields here; path/share semantic validation must happen elsewhere.

Test signals: add mode, edit mode title/disabled share, OK enable behavior, cancel returning null, returned status, and help ID selection.
