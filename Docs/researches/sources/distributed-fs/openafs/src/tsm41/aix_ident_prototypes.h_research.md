# sources/distributed-fs/openafs/src/tsm41/aix_ident_prototypes.h

## Purpose
Declares identity lookup callback stubs for the AIX 4 OpenAFS security method.

## Important APIs, Types, And Functions
The header declares `afs_getgrset`, `afs_getgrgid`, `afs_getgrnam`, `afs_getpwnam`, and `afs_getpwuid`, with return types involving `int`, `struct group *`, and `struct passwd *`.

## Control Flow
There is no executable flow. `aix41_auth.c` installs the declared callbacks into `secmethod_table`, and `aix41_ident.c` implements null-return stubs.

## State And Persistence
No state is owned. Runtime behavior is to decline identity data so AIX can fall back to local lookup behavior.

## Dependencies And Integration Points
The declarations depend on consumers having appropriate `struct group` and `struct passwd` declarations in scope. This header is specific to AIX 4.1 identity integration.

## Risks And Test Signals
This header contains conflicting declarations for `afs_getpwnam` with different argument/return types, and the implementation also differs. Strict C compilers or modern headers may reject it. Build coverage on the intended AIX compiler and security-method callback tests are the key signals.
