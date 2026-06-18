# sources/distributed-fs/openafs/src/tsm41/aix5_auth.c

## Purpose
Defines the AIX 5+ security method initialization entry point for OpenAFS kauth-based dynamic authentication. Compared with the AIX 4 module, it registers authentication/password callbacks and `getpasswd`, but not group/passwd identity lookup stubs.

## Important APIs, Types, And Functions
The active function is `afs_initialize(struct secmethod_table *meths)`, compiled for `AFS_AIX51_ENV`. It installs `afs_chpass`, `afs_authenticate`, `afs_passwdexpired`, `afs_passwdrestrictions`, and `afs_getpasswd`.

## Control Flow
At module load, `afs_initialize` calls `ka_Init`, clears the security method table, registers the AFS callbacks, and returns success.

## State And Persistence
It initializes kauth process state and fills the method table. Persistent authentication effects occur later in `afs_authenticate`, not in this file.

## Dependencies And Integration Points
The file depends on AIX `usersec.h`, OpenAFS kauth/kautils, and `aix_auth_prototypes.h`. `tsm41/Makefile.in` compiles it as `aix_auth.o` for AIX 5/6/7 system names.

## Risks And Test Signals
Risks are method-table ABI differences across AIX releases and missing callback slots for newer AIX expectations. Useful signals are AIX 5+ dynamic module load, callback table inspection, and login authentication through the shared `aix_auth_common.c` implementation.
