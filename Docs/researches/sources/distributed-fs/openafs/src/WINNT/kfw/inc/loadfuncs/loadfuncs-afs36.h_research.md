## sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-afs36.h

Purpose: Dynamic-load function typedef list for older AFS 3.6-style token/configuration DLLs.

Important APIs/types/functions: Defines `AFSTOKENS_DLL` as `afsauthent.dll`, `AFSCONF_DLL` as `libafsconf.dll`, the same `cm_configProc_t`, and `TYPEDEF_FUNC` entries for token and cell functions. Signatures differ from the modern header: `ktc_SetToken(struct ktc_principal *, struct ktc_token *, struct ktc_principal *, int)` and `cm_SearchCellFile(char *, char *, cm_configProc_t *, void *)`.

Control flow: The loadfuncs framework resolves old DLL exports and lets compatibility code call AFS 3.6 entrypoints through the generated pointers.

State and persistence: No state in the header. Runtime loader state is external; token APIs mutate AFS authentication state and cell search reads configuration.

Dependencies and integration points: Depends on `loadfuncs.h`, AFS token structs, and socket address declarations. It exists specifically to support older AFS client deployments.

Risks: The header guard closing comment names the modern guard, a minor maintenance hazard. Accidentally using modern call order with old function pointers can corrupt arguments. DLL name selection changes deployment requirements.

Test signals: Load `afsauthent.dll`, verify old export signatures, exercise token set/get/list/forget, and test old four-argument `cm_SearchCellFile` behavior separately from the modern path.
