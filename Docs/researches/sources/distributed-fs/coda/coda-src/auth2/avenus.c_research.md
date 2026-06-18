# sources/distributed-fs/coda/coda-src/auth2/avenus.c

Purpose: Client helper library for sending, retrieving, and deleting auth tokens in Venus through Coda pioctls.

Important APIs/functions: `U_SetLocalTokens`, `U_GetLocalTokens`, and `U_DeleteLocalTokens`. Internal `venusbuff` packages clear/secret token sizes, token data, and realm.

Control flow: `U_SetLocalTokens` fills a `venusbuff` and sends `_VICEIOCTL(3)`. `U_GetLocalTokens` passes the realm to `_VICEIOCTL(8)`, validates returned token sizes, and copies tokens out. `U_DeleteLocalTokens` sends the realm to `_VICEIOCTL(9)`.

State and persistence: No local persistence; Venus stores or removes token state. Token file persistence is handled elsewhere (`tokenfile.c`, not in this subset).

Dependencies and integration: Used by `clog` and related client utilities. Depends on Coda kernel/Venus pioctl ABI, `auth2.h`, and config constants.

Risks and test signals: `strncpy(inbuff.realm, realm, MAXHOSTNAMELEN)` may omit NUL on long realm names. Raw numeric ioctl constants are less self-documenting than named constants. Return semantics differ on Cygwin vs Unix for get-token failures.
