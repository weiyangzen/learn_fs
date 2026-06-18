# sources/distributed-fs/openafs/src/tsm41/aix_auth_prototypes.h

## Purpose
Declares the AIX authentication callbacks and ticket-file helper used by the TSM/LAM dynamic auth modules.

## Important APIs, Types, And Functions
The header declares `afs_authenticate`, `afs_chpass`, `afs_passwdexpired`, `afs_passwdrestrictions`, `afs_getpasswd`, and `aix_ktc_setup_ticket_file`. Signatures match the AIX security method callback style with user names, password/message pointers, and reentry indicators.

## Control Flow
The header itself has no control flow. Initializer modules use these prototypes to assign callbacks into `secmethod_table`; implementation files provide kauth and no-op behavior.

## State And Persistence
No state is stored here. The declared functions may create authentication/PAG/token/ticket-file side effects at runtime.

## Dependencies And Integration Points
It is included by `aix41_auth.c`, `aix5_auth.c`, `aix_auth_common.c`, `aix_aklog.c`, and `aix_ktc.c`. It must remain consistent with AIX `usersec.h` callback expectations and the implementations.

## Risks And Test Signals
Risks are prototype drift against AIX headers and implementation mismatches. Compile warnings/errors in the AIX TSM module build are the primary signal, followed by module load and callback invocation tests.
