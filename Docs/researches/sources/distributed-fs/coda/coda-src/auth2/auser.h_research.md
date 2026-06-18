# sources/distributed-fs/coda/coda-src/auth2/auser.h

Purpose: Public header for the auth2 client helper library.

Important APIs/types: Declares token byte-order helpers, `U_Authenticate`, `U_ChangePassword`, `U_InitRPC`, `U_AuthErrorMsg`, `U_GetAuthServers`, `U_BindToServer`, and `U_Error`.

Control flow and state model: The API separates server discovery, binding, token retrieval, and error formatting so command-line tools can compose these operations.

Persistence and integration: No persistence. Integrates auth tools with RPC2-generated auth stubs and token storage helpers.

Risks and test signals: Function signatures expose raw password pointers and lengths; callers are responsible for clearing sensitive data and freeing `RPC2_addrinfo` lists returned by `U_GetAuthServers`.
