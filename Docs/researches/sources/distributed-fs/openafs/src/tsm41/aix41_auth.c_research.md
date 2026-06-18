# sources/distributed-fs/openafs/src/tsm41/aix41_auth.c

## Purpose
Defines the AIX 4.1 security method initialization entry point for the OpenAFS dynamic authentication module. It registers AFS authentication and identity hooks with AIX's `secmethod_table`.

## Important APIs, Types, And Functions
The single active function is `afs_initialize(struct secmethod_table *meths)`, compiled only for `AFS_AIX41_ENV` and not `AFS_AIX51_ENV`. It calls `ka_Init`, zeros the method table, and assigns `afs_chpass`, `afs_authenticate`, `afs_passwdexpired`, `afs_passwdrestrictions`, plus group/passwd lookup stubs from `aix41_ident.c`.

## Control Flow
When AIX loads the module, `afs_initialize` initializes kauth once, clears all method slots, installs password/authentication callbacks, and installs identity callbacks so non-local registries can fall through to local functions when the OpenAFS stubs return null.

## State And Persistence
The function initializes kauth package state in-process and mutates the caller-provided method table. It does not write persistent data, but the registered authenticate callback may later obtain tokens and set PAG/ticket state.

## Dependencies And Integration Points
It depends on AIX `usersec.h`, OpenAFS kauth/kautils, and prototypes in `aix_auth_prototypes.h`. It is compiled to `aix_auth.o` for AIX 4 by `tsm41/Makefile.in`.

## Risks And Test Signals
Risks include strict compile gating for old AIX, method-table ABI drift, and identity prototype mismatches. Tests are AIX 4 module load, `afs_initialize` callback table inspection, successful authentication through `afs_authenticate`, and fallback behavior for getpwnam/getgrnam hooks.
