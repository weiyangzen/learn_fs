# sources/distributed-fs/openafs/src/tsm41/aix_ktc.c

## Purpose
Provides a small helper for AIX kauth modules to adjust Kerberos ticket-file ownership after successful authentication.

## Important APIs, Types, And Functions
The only function is `aix_ktc_setup_ticket_file(char *userName)`, compiled for `AFS_AIX41_ENV`. When `AFS_KERBEROS_ENV` is defined, it uses `getpwnam`, `ktc_tkt_string_uid`, and `chown`.

## Control Flow
The helper opens the passwd database, resolves the authenticated user, and if found changes ownership of the user's ktc ticket-file path to the user's uid/gid. It prints `perror` diagnostics on `chown` or `getpwnam` failures and closes the passwd database.

## State And Persistence
In Kerberos builds it persists filesystem metadata changes on the ticket file path. Non-Kerberos builds compile the function as a no-op. It reads passwd database state.

## Dependencies And Integration Points
It is called after `ka_UserAuthenticateGeneral` succeeds in `aix_auth_common.c`. It depends on OpenAFS ktc APIs and AIX/POSIX passwd and ownership APIs.

## Risks And Test Signals
Risks include changing ownership of an unexpected path from `ktc_tkt_string_uid`, weak error reporting through stderr/perror in an auth module context, and no action in non-Kerberos builds. Tests should cover Kerberos and non-Kerberos builds, existing and missing passwd entries, chown failure, and resulting ticket-file ownership.
