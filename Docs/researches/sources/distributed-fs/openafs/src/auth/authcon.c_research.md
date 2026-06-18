# sources/distributed-fs/openafs/src/auth/authcon.c

## Purpose
`authcon.c` builds RX security classes for OpenAFS client and server connections from local keys, current tokens, or rxgk key material. It centralizes fallback-to-null behavior and server security object construction.

## Important APIs, types, and functions
Public functions include `afsconf_ServerAuth`, `afsconf_ClientAuth`, `afsconf_ClientAuthSecure`, `afsconf_ClientAuthRXGKClear`, `afsconf_ClientAuthRXGKAuth`, `afsconf_ClientAuthRXGKCrypt`, `afsconf_ClientAuthToken`, `afsconf_SetSecurityFlags`, `afsconf_BuildServerSecurityObjects`, `afsconf_BuildServerSecurityObjects_int`, `afsconf_PickClientSecObj`, and `afsconf_PickClientLocalSecObj`. Internal helpers include `QuickAuth`, `_afsconf_GetRxkadKrb5Key`, `GenericAuth`, `_ClientAuthRXGK`, `LogDesWarning`, `LogNoKeysWarning`, and `PickClientSecObj`.

## Control flow
Server authentication uses `rxkad_NewKrb5ServerSecurityObject` with callbacks for rxkad DES and rxkad_krb5 typed keys. Client local-auth flow goes through `GenericAuth`, which prefers rxkad_krb5 typed keys by enctype list, falls back to latest DES rxkad key, generates a DES session key, makes a ticket for `afs` or an explicit rx identity, and returns an rxkad client security object. Token-auth flow reads current tokens with `ktc_GetTokenEx`, extracts rxkad material, and creates a client security object at clear or crypt level. rxgk local-auth flow prints a token/key from the latest rxgk cell key when compiled. `PickClientSecObj` selects among noauth, localauth, rxgk, current-token, and fallback-null modes.

## State and persistence
The file does not persist state itself. It reads keys from `struct afsconf_dir`, reads tokens from the cache manager, writes security flags into `dir->securityFlags`, and returns heap-allocated RX security objects owned by callers. It logs warnings when server key state is absent or only DES keys are present.

## Dependencies and integration points
It integrates `cellconfig`, `keys`, `ktc`, rx/rxkad, optional rxgk, hcrypto DES/random APIs, global pthread locking, and rx identity handling. `asetkey` produces the typed keys this file consumes; servers use `afsconf_BuildServerSecurityObjects_int` during RX service setup.

## Risks
Several failure paths intentionally fall back to rxnull through `QuickAuth`; callers must inspect `scIndex` or avoid `AFSCONF_SECOPTS_FALLBACK_NULL` when anonymous fallback is not acceptable. DES remains involved for rxkad session keys even when long-term keys are stronger. The code notes a leak when localauth requested but fallback null is rejected. Enctype preference is hardcoded. Local-auth identity support is limited to superuser and KRB4-style identities.

## Test signals
Cover server class arrays with no keys, DES keys, rxkad_krb5 keys, always-encrypt flags, and rxgk builds; client local-auth clear/crypt; current-token auth with and without tokens; fallback-null rejection; local identities; rxgk clear/auth/crypt; and key callback buffer-size failures.
