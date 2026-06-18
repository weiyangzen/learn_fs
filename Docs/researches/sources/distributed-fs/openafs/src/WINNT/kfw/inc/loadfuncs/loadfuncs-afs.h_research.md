## sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-afs.h

Purpose: Dynamic-load function typedef list for modern OpenAFS token/configuration DLLs used by KfW integration.

Important APIs/types/functions: Defines `AFSTOKENS_DLL` as `libafstokens.dll`, `AFSCONF_DLL` as `libafsconf.dll`, `cm_configProc_t`, and `TYPEDEF_FUNC` entries for `ktc_ListTokens`, `ktc_GetToken`, `ktc_SetToken`, `ktc_ForgetAllTokens`, `cm_SearchCellFile`, and `cm_GetRootCellName`.

Control flow: Included by the generic load-functions framework, which expands `TYPEDEF_FUNC` into function-pointer typedefs, globals, or loader entries. Runtime code loads the DLLs and calls resolved AFS token/cell functions.

State and persistence: This header has no state. Resolved function pointers and loaded module handles are held by the loadfuncs implementation. Token calls mutate AFS token state; cell functions read AFS cell configuration.

Dependencies and integration points: Depends on `loadfuncs.h`, `struct ktc_principal`, `struct ktc_token`, and `struct sockaddr_in` declarations from AFS/network headers. Used by OpenAFS Windows Kerberos-to-AFS token paths.

Risks: Function signatures must match the target DLL exactly. This modern variant has `ktc_SetToken(server, client, token, flags)` and `cm_SearchCellFile(cell, proc, rock)` signatures that differ from the AFS 3.6 header.

Test signals: Dynamic-load tests for DLL names and all exports; call-signature smoke tests for list/get/set/forget tokens; root-cell and cell-file search tests.
