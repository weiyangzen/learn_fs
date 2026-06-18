# sources/distributed-fs/coda/coda-src/auth2/auser.c

Purpose: Client-side auth library used by Coda user tools to initialize RPC2, discover auth servers, bind with a username/password, obtain tokens, and change passwords.

Important APIs/functions: `U_HostToNetClearToken`, `U_NetToHostClearToken`, `U_Authenticate`, `U_ChangePassword`, `U_InitRPC`, `U_AuthErrorMsg`, `U_GetAuthServers`, `U_BindToServer`, and `U_Error`. Internal helpers include `GetAuthServers` and `TryBinding`.

Control flow: `U_Authenticate` obtains a password from stdin or `getpass`, binds to one auth server with `AUTH_METHOD_CODAUSERNAME`, calls `AuthGetTokens`, then quits/unbinds. `U_ChangePassword` binds as the acting user, resolves target name to ID, and calls `AuthChangePasswd`. Server discovery uses realm SRV/config lookup unless a host override is supplied. `U_BindToServer` iterates server addresses until success or authentication rejection.

State and persistence: Maintains only transient RPC2 bindings and password buffers. Token persistence is handled by callers such as `clog` and `avenus`.

Dependencies and integration: Depends on RPC2/LWP, generated `auth2.h`, `prs.h`, `auth2.common.h`, Coda config, and realm parsing. Used by `clog`, `au`, and other client tools.

Risks and test signals: Password strings remain in stack buffers after use. Non-interactive password reading assumes `strlen(passwd) > 0` before trimming newline. Uses `RPC2_XOR` encryption type, which is legacy. Error reporting preserves RPC2 and auth return domains through `U_Error`.
