# sources/distributed-fs/openafs/src/tsm41/aix_auth_common.c

## Purpose
Provides common kauth-based authentication callbacks shared by the AIX dynamic auth modules. It prompts for an AFS password when needed, authenticates through `ka_UserAuthenticateGeneral`, sets a PAG, and arranges Kerberos ticket-file ownership when built in Kerberos mode.

## Important APIs, Types, And Functions
The main function is `afs_authenticate`. Supporting no-op callbacks are `afs_chpass`, `afs_passwdexpired`, `afs_passwdrestrictions`, and `afs_getpasswd`. It uses `ka_UserAuthenticateGeneral`, `getpass`, `getpwnam`, `aix_ktc_setup_ticket_file`, and AIX auth return constants such as `AUTH_SUCCESS`, `AUTH_FAILURE`, and `AUTH_NOTFOUND`.

## Control Flow
`afs_authenticate` clears reentry/message outputs, uses the provided response or prompts interactively, rejects empty passwords, verifies the user exists locally, then calls kauth with `KA_USERAUTH_VERSION + KA_USERAUTH_DOSETPAG`. `KANOENT` maps to not-found; other kauth failures allocate a message. On success it calls `aix_ktc_setup_ticket_file` and returns success. The other callbacks are success/no-op except `afs_getpasswd`, which returns `NULL` and sets `ENOSYS`.

## State And Persistence
Authentication can create/set AFS authentication state and a PAG through kauth. It may also affect Kerberos ticket-file ownership through the helper. Allocated error messages are returned to AIX for display/cleanup.

## Dependencies And Integration Points
This file is compiled for `AFS_AIX41_ENV` and used by both AIX 4 and AIX 5 kauth dynamic modules. It depends on AIX user security, passwd lookup, OpenAFS kauth/kautils, and prototypes from `aix_auth_prototypes.h`.

## Risks And Test Signals
Risks include use of `getpass`, fixed-size `sprintf` buffers, typoed error text, local passwd requirement before AFS auth, and message allocation ownership assumptions. Tests should cover response-supplied and prompt-based auth, empty password rejection, nonexistent user, `KANOENT`, general kauth failures, successful PAG creation, and ticket-file setup in Kerberos builds.
