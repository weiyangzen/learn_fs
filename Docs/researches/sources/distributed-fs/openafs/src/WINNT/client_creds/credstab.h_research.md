# sources/distributed-fs/openafs/src/WINNT/client_creds/credstab.h

Purpose: declares credentials tab and obtain-credentials dialog entry points.

Important APIs: `ShowObtainCreds(BOOL fExpiring, LPTSTR pszCell)` launches the token acquisition UI, and `Creds_DlgProc` handles credentials tab dialog messages.

Control flow: no implementation; consumers call `ShowObtainCreds` from reminder, network-change, and user-click flows.

State/persistence: none directly, but both declared functions can interact with global credential state and reminder persistence.

Dependencies/integration: included by `afscreds.h`; relies on Win32 dialog types.

Risks: exported interface exposes mutable string pointer semantics without documenting ownership. `ShowObtainCreds` may spawn a thread and display modal UI.

Test signals: compile/link references from `window.cpp`, `ipaddrchg.c`, and `credstab.cpp` consumers.
