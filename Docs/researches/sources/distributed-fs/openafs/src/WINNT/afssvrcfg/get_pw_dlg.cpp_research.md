<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.cpp

Purpose: Provides a small password prompt used when setting the AFS server principal requires the current AFS principal password.

Important APIs/functions: `GetAfsPrincipalPassword` displays `IDD_GET_PW` and returns a pointer to `g_CfgData.szServerPW` on OK. `GetPwDlgProc`, `CheckEnableButtons`, and `SaveDlgInfo` implement the dialog behavior.

Control flow: The final config page calls this from `CreatePrincipalAndKey` when cfg reports invalid/missing AFS password/key. The dialog enables OK only when the password field is non-empty and saves the value into global config data.

State and persistence: Mutates `g_CfgData.szServerPW`; no durable writes directly. The password is then passed to cfg APIs and remains in process memory.

Dependencies and integration points: Uses app-library help, modal dialog helpers, resource IDs, and fixed-size credential limits from `afscfg.h`.

Risks: `ShowPageInfo` is defined but not called, so existing password state is not prefilled. Returning a pointer to global password storage exposes mutable shared state. Password length is truncated by `lstrncpy` and not cleared after use.

Test signals: Test empty password disabling, OK/cancel return values, retry loop integration from `CreatePrincipalAndKey`, max-length password input, and help routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/get_pw_dlg.cpp -->
