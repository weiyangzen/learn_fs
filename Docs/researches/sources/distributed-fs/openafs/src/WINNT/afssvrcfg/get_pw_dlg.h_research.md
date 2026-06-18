<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.h

Purpose: Declares the AFS principal password prompt.

Important APIs/functions: `GetAfsPrincipalPassword(HWND hParent, TCHAR *&pszServerPW)` returns true and points the output reference at the stored server password on success.

Control flow: No implementation logic; intended for password retry paths in final configuration.

State and persistence: Implementation writes `g_CfgData.szServerPW`.

Dependencies and integration points: Requires Win32/TCHAR types and is included by `config_server_page.cpp`.

Risks: API exposes pointer lifetime tied to global config state instead of returning a copied secure string.

Test signals: Verify callers handle false by cancelling the operation and do not retain the pointer after global state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.h -->
