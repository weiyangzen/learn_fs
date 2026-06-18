# sources/distributed-fs/openafs/src/tsm41/aix_aklog.c

## Purpose
Implements the AIX 5 Kerberos 5 `aklog_dynamic_auth` module. During AIX login/session authentication it obtains Kerberos 5 AFS service credentials, imports them as rxkad tokens, optionally resolves a PTS vice id, configures PAG behavior, and stores tokens via `ktc_SetTokenEx`.

## Important APIs, Types, And Functions
The exported entry point is `aklog_initialize`. Security callbacks include `aklog_authenticate`, `aklog_open`, `aklog_chpass`, `aklog_passwdexpired`, `aklog_passwdrestrictions`, and `aklog_getpasswd`. Core helpers are `afs_realm_of_cell`, `get_credv5`, `get_user_realm`, `get_cellconfig`, and `auth_to_cell`. Key globals are `uidpag`, `localuid`, `ak_cellconfig`, `linkedcell`, and `_krb425_ccache`.

## Control Flow
`aklog_initialize` clears the AIX method table and registers auth/open callbacks. `aklog_open` parses NUL-delimited options such as `uidpag` and `localuid`. `aklog_authenticate` initializes a Kerberos context and calls `auth_to_cell`. `auth_to_cell` reads client cell config, selects a Kerberos realm, tries `afs/<cell>` and optionally `afs` principals, builds a token jar, imports the V5 ticket as rxkad token data, derives the username and realm suffix, optionally queries PTS for the vice id or uses the local uid, sets token PAG policy, and either sets tokens directly or forks/setuids for root with UID-based PAGs.

## State And Persistence
The module stores process-global option flags, cached Kerberos ccache/principal state, and cell config. Its lasting effect is kernel/cache-manager token state and PAG assignment. It reads Kerberos credential caches, AFS client config, passwd data, and possibly PTS data.

## Dependencies And Integration Points
It integrates AIX LAM/TSM security methods, Kerberos 5 APIs with portability macros for principal and keyblock access, OpenAFS cell config, token import APIs, ktc, rxkad token formats, PTS client calls, syslog, passwd lookup, PAG APIs, and AIX process/session behavior.

## Risks And Test Signals
Risks are high because this is security-sensitive and platform-specific: fixed-size string copies, cached Kerberos objects without cleanup, comments noting `pr_Initialize` can crash long-running daemons, DES enctype request assumptions, UID/PAG ambiguity, fork/setuid error handling, and token vice-id mapping fallbacks. Tests should cover module load, options parsing, local and linked cells, `afs/<cell>` and `afs` service principal fallback, foreign-realm username suffixes, PTS unavailable, `localuid`, root `uidpag` fork path, missing Kerberos cache, expired tickets, and token visibility after login.
