## sources/distributed-fs/openafs/src/WINNT/client_exp/unlog_dlg.h

Purpose: Declares `CUnlogDlg`, the token-discard dialog.

Important APIs/types: Public `SetCellName` sets the target cell. Dialog data binds OK and cell-name controls; handlers cover initialization, cell change, OK, and help.

Control flow/state: OK enablement depends on non-empty `m_strCellName`.

Dependencies/integration: Includes `resource.h`; implementation uses OpenAFS token APIs.

Risks/tests: Header has no include guard. Test caller-provided cell prepopulation and whether empty-cell all-token removal should be reachable from UI.
