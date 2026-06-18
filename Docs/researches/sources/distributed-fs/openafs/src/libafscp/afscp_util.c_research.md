## sources/distributed-fs/openafs/src/libafscp/afscp_util.c

Purpose: Builds client security objects and VLDB ubik clients for `libafscp` cells. It supports rxnull anonymous mode, Kerberos credential cache authentication, and server-local KeyFile authentication as an arbitrary AFS user.

Important APIs and functions: Public controls are `afscp_Insecure`, `afscp_AnonymousAuth`, `afscp_LocalAuthAs`, and `afscp_SetConfDir`. Private helpers are `_GetCellInfo`, `_GetNullSecurityObject`, `_GetLocalSecurityObject` when Kerberos is available, `_GetSecurityObject`, and `_GetVLservers`.

Control flow: `_GetSecurityObject` obtains cell config, optionally tries local auth if `authas_name` is set, otherwise derives a Kerberos realm, opens the default credential cache, tries `afs/cell@realm` then `afs@realm`, derives a DES key, and creates an rxkad client security object at clear or crypt level. If Kerberos is disabled or auth fails and `try_anonymous` is set, it returns rxnull security. `_GetVLservers` creates RX connections to configured VLDB servers and initializes a ubik client.

State and persistence: Maintains global `insecure`, `try_anonymous`, `authas_name`, and `confdir`. These influence all later cell creation. It reads local OpenAFS and Kerberos configuration but does not persist changes.

Dependencies and integration: Uses OpenAFS auth config, rxnull, rxkad, rx identity, Kerberos 5 APIs, hcrypto DES derivation, and ubik client initialization. Called during `afscp_CellByName`.

Risks: Security behavior is process-global and order-dependent. Anonymous fallback only occurs when explicitly enabled. `afscp_SetConfDir` ignores open failure except by leaving `confdir` null for later calls. The nested `if (realm) if (realm == NULL)` branch is unreachable and suggests stale logic. Kerberos DES derivation limits interoperability to rxkad-compatible tickets.

Test signals: Test Kerberos credential success, service principal fallback, local auth, anonymous fallback, insecure clear mode, invalid impersonation names, alternate conf directories, missing CellServDB, and cleanup after repeated confdir changes.
