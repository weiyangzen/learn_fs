# sources/distributed-fs/openafs/src/WINNT/client_creds/creds.cpp

Purpose: provides token-library loading, AFS service status helpers, current token enumeration, token destruction, token acquisition, and default-cell lookup for `afscreds.exe`.

Important APIs/functions: `Creds_OpenLibraries` dynamically loads `afsauthent.dll` and `libafsconf.dll`; `IsServiceRunning`, `IsServicePersistent`, `IsServiceConfigured`; `GetCurrentCredentials`; `DestroyCurrentCredentials`; `ObtainNewCredentials`; `GetDefaultCell`; `GetGatewayName`.

Control flow: token operations lazily load libraries and initialize RX/KA paths. `GetCurrentCredentials` clears `g.aCreds`, lists tokens via `ktc_ListTokens`, resolves each token via `ktc_GetToken`, converts cell/user/expiration into `CREDS`, restores reminder flags, and updates the tray icon. `ObtainNewCredentials` prefers KFW when available, otherwise parses login names and calls KA authentication.

State/persistence: mutates `g.aCreds`, `g.cCreds`, and `g.tickLastRetest` under `g.credsLock`. Reads service and cell registry keys. Reminder persistence is delegated to `LoadRemind`.

Dependencies/integration: integrates dynamic OpenAFS token/config DLLs, KFW, Windows SCM, registry constants, tray icon refresh, and dialog error reporting.

Risks: dynamic function pointer set must be complete or all token operations fail. Passwords are copied into fixed-size stack buffers and not scrubbed. `GetCurrentCredentials` updates UI/tray after releasing the lock but still depends on shared state. Service status branches differ between NT and gateway-mode non-NT.

Test signals: missing DLLs, stopped service, multiple-cell token enumeration, expired tokens, KFW and non-KFW authentication, root-cell registry override, and token destruction error paths.
