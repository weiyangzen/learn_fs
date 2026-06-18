# sources/distributed-fs/openafs/src/kauth/katoken.c

## Purpose
Provides client-side token-cache helpers that obtain kauth tickets from the AuthServer and store them in the kernel token cache.

## Important APIs, Types, And Functions
Exports `ka_GetAuthToken`, `ka_GetServerToken`, `ka_GetAdminToken`, and `ka_VerifyUserToken`. It uses `ktc_token`, `ktc_principal`, `ubik_client`, KA service IDs, cell/realm helpers, `ka_Authenticate`, `ka_GetToken`, and `ktc_SetToken`/`ktc_GetToken`.

## Control Flow
`ka_GetAuthToken` expands a cell, connects unauthenticated to the authentication service, authenticates with the supplied key to get a TGS token, and stores it under the `krbtgt` server principal. `ka_GetServerToken` first checks for a cached service token, obtains or imports the correct TGS token, supports inter-cell token acquisition through the local cell when needed, contacts the target cell's ticket-granting service, gets a service token, and stores it, optionally with `AFS_SETTOK_SETPAG`. `ka_GetAdminToken` similarly obtains or caches an admin-service token. `ka_VerifyUserToken` authenticates without storing a token.

## State And Persistence
State changes are writes to the kernel token cache through ktc APIs. Function-local connections are destroyed after use. The global pthread lock serializes these flows.

## Dependencies And Integration Points
It bridges high-level tools such as `klog`/`kpasswd` to low-level client RPC helpers in `authclient.c` and token-cache APIs in `afs/auth.h`. It depends on kauth cell config and Ubik client connections.

## Risks And Test Signals
Risks include holding the global mutex across network calls, token-cache principal naming subtleties for local versus foreign cells, inter-cell fallback behavior, and cleanup leaks on early returns after connection creation. Test signals include fresh and cached auth/admin/service tokens, `-setpag` token placement, foreign-cell token acquisition, unavailable server errors, and token verification without cache writes.
