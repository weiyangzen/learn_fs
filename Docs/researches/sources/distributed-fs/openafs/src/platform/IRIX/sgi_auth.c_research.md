# sources/distributed-fs/openafs/src/platform/IRIX/sgi_auth.c

## Purpose
Provides IRIX-specific AFS password verification helpers for login/authentication integration.

## Important APIs, Types, And Functions
Exports `afs_verify` and `afs_gettktstring` when `AFS_SGI_ENV` is defined. `afs_verify` calls `ka_Init` and `ka_UserAuthenticateGeneral` with `KA_USERAUTH_DOSETPAG` to authenticate a user password and establish a PAG/token side effect. `afs_gettktstring` returns the cache/ticket path via `ktc_tkt_string`.

## Control Flow
`afs_verify` initializes kauth, calls the general user-authentication routine with username, password, default realm/cell, default lifetime, and an output expiration pointer. On failure it optionally prints the kauth reason and tells the caller to continue with local authentication by returning `1`; on success it returns `0`.

## State And Persistence
Successful authentication may establish process authentication group state and AFS tokens through the kauth/ktc layers. The file itself stores no static state.

## Dependencies And Integration Points
Depends on SGI platform macros, `kauth.h`, `kautils.h`, and the token-cache API. It is linked into IRIX authentication shared libraries by the sibling makefile.

## Risks And Test Signals
Risks include obsolete kauth password authentication, plaintext password handling, typoed `quite` parameter naming, and behavior that falls back to local auth after AFS failure. Test signals are correct return codes for valid/invalid AFS passwords, PAG/token creation, expiration output, and quiet/non-quiet diagnostic behavior.
