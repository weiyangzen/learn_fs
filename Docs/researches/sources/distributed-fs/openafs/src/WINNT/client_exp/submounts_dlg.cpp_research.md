## sources/distributed-fs/openafs/src/WINNT/client_exp/submounts_dlg.cpp

Purpose: Implements the submount management dialog backed by the OpenAFS client registry `Submounts` key.

Important APIs/functions: `FillSubmtList` enumerates registry values; `ReadSubmtInfo` reads one value; `OnAdd`, `OnChange`, and `OnDelete` stage work items; `FixSubmts` applies staged add/change/delete operations through `RegSetValueEx` and `RegDeleteValue`; `SetAddOnlyMode` supports a direct create-and-save flow from a selected path.

Control flow/state: The UI list shows current and staged submounts, while `m_ToDo` owns pending `CSubmountInfo*` changes. `AddWork` coalesces operations by share name before `OnOk` persists them.

Dependencies/integration: Uses MFC, `CAddSubmtDlg`, `CSubmountInfo`, registry constants from `afsreg.h`, `WNetGetConnection`, `HOURGLASS`, and `msgs`.

Risks/tests: Registry string byte counts use character counts instead of byte counts in Unicode builds. `RegCreateKeyEx` return status is mostly ignored. Add-only mode immediately calls `OnAdd` and `OnOk`, so cancellation semantics need scrutiny. Test HKLM permission failures, Wow64 registry view, Unicode submount names, staged add-delete coalescing, and network-drive path expansion.
