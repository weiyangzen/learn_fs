# sources/distributed-fs/openafs/src/tsm41/aix41_ident.c

## Purpose
Provides AIX 4.1 identity lookup stubs for the OpenAFS security method. These are intentionally null implementations so AIX can fall back to local passwd/group mechanisms while treating AFS users as non-local registry users.

## Important APIs, Types, And Functions
Compiled only for `AFS_AIX41_ENV` and not `AFS_AIX51_ENV`, it defines `afs_getgrset`, `afs_getgrgid`, `afs_getgrnam`, `afs_getpwnam`, and `afs_getpwuid`. Each function returns `NULL` despite some declarations using integer return types.

## Control Flow
The functions have no internal flow beyond returning null. They are installed into `secmethod_table` by `aix41_auth.c`.

## State And Persistence
No state is read or written. The behavior affects AIX login lookup control flow by declining to provide AFS-specific identity records.

## Dependencies And Integration Points
It includes AIX security and OpenAFS kauth headers and `aix_ident_prototypes.h`. It exists for compatibility with AIX 4's security method behavior and is built as `aix_ident.o`.

## Risks And Test Signals
There are visible prototype/signature inconsistencies between this implementation and `aix_ident_prototypes.h`, including swapped argument/return expectations for passwd lookups. Build warnings or errors on stricter compilers are likely signals. Runtime tests should confirm AIX falls back to local identity lookup when these callbacks return null.
