## sources/distributed-fs/openafs/src/kauth/user.c

Purpose: `user.c` is the Unix/non-Windows high-level user authentication interface for kauth. It converts passwords into keys, obtains TGT and AFS service tickets, optionally creates/uses PAGs, installs tokens, and exposes password-reading and password-verification wrappers.

Important APIs: `GetTickets` calls `ka_GetAuthToken`, clears the derived key, then calls `ka_GetAFSTicket`. `ka_GetAFSTicket` obtains an `afs` server token via `ka_GetServerToken`; on old pioctl interfaces it resolves the user's PTS Vice ID and installs a token with client name `AFS ID <id>`. `ka_UserAuthenticateGeneral` validates the interface version, initializes KA, derives the key with `ka_StringToKey`, handles alarm preservation on Unix, optionally verifies only with `ka_VerifyUserToken`, optionally calls `setpag`/`ktc_newpag`, applies default max lifetime, and retries with MIT DES `DES_string_to_key` if the Andrew string-to-key path yields `KABADREQUEST`. `ka_UserAuthenticate`, `ka_UserReadPassword`, and `ka_VerifyUserPassword` are compatibility wrappers.

State and persistence: updates process PAG and token cache state through `setpag`, `ktc_newpag`, and `ktc_SetToken` via lower helpers. It clears password-derived keys after use and restores Unix alarms/Rx state if it interrupted a pre-existing alarm.

Dependencies and integration points: depends on hcrypto DES/UI, Rx/rxkad, cellconfig, ptserver client APIs, KTC, KA token helpers, pioctl behavior, and error tables. The old-pioctl PTS path integrates authentication with filesystem identity by converting names to Vice IDs.

Risks: legacy DES fallback broadens compatibility but preserves weak cryptographic modes. Root with null instance is rejected as local-only. Some reason strings are generic or derived from error tables. PTS lookup failures in old-pioctl mode are logged but can return 0 in some error branches, intentionally tolerating inability to translate.

Test signals: exercised by `multiklog`, `test_interim_ktc.c`, `test_getticket.c`, and `test_rxkad_free.c` via `ka_UserAuthenticate*`, `ka_GetServerToken`, and token installation behaviors.
