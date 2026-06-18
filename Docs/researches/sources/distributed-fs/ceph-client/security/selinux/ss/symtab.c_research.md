# sources/distributed-fs/ceph-client/security/selinux/ss/symtab.c

## Purpose
`symtab.c` implements the simple string-keyed symbol table used throughout SELinux policy parsing for classes, permissions, roles, types, users, booleans, sensitivities, and categories.

## Important APIs, Types, and Functions
The file exports `symtab_init()`, `symtab_insert()`, and `symtab_search()`. It defines private key operations `symhash()` and `symcmp()` and packages them into `symtab_key_params`. The hash function is djb2a over unsigned bytes; comparison is `strcmp()`.

## Control Flow
`symtab_init()` resets `nprim` and initializes the underlying `hashtab`. Insert/search forward the supplied string key and datum to `hashtab_insert()` and `hashtab_search()` with the symbol key parameters. Ownership of inserted keys/data is handled by policydb-specific destructors, not by this file.

## State and Persistence
The symtab holds in-memory policy symbols during and after policy load. `nprim` is a caller-maintained count of primary symbols and is later used by `policydb_index()` to allocate value-to-name/value-to-struct arrays.

## Dependencies and Integration Points
It depends on Linux string/kernel/errno headers and the local `hashtab` abstraction. `policydb.c` is the primary consumer and uses one `struct symtab` per SELinux symbol kind.

## Risks
Duplicate-key behavior is delegated to `hashtab_insert()`. Since keys are raw `char *`, callers must ensure stable allocated storage and matching destruction. Hash collision behavior affects policy load/search performance.

## Test Signals
Policy load tests with many symbols and collision-heavy names provide coverage. Unit-level signals would include insert/search success, duplicate rejection from the underlying hash table, and `nprim` preservation across initialization and policy parsing.
