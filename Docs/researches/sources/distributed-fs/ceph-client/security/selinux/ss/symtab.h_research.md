# sources/distributed-fs/ceph-client/security/selinux/ss/symtab.h

## Purpose
`symtab.h` declares the SELinux symbol table wrapper around the generic `hashtab` implementation. It gives policy code a concise type for string-to-datum mappings plus a primary-symbol count.

## Important APIs, Types, and Functions
`struct symtab` contains `struct hashtab table` and `u32 nprim`. Public prototypes are `symtab_init()`, `symtab_insert()`, and `symtab_search()`.

## Control Flow
The header is intentionally minimal: policy readers allocate/populate datums, call `symtab_insert()`, then later call `symtab_search()` for references and mapping. `nprim` is filled by parser code according to policy metadata.

## State and Persistence
The symbol table persists inside `struct policydb` for the lifetime of the loaded policy. It is also used to construct derived indexes for fast value-to-name and value-to-struct access.

## Dependencies and Integration Points
It includes `hashtab.h` and is included by `policydb.h`. Every SELinux policy symbol kind is represented by this type.

## Risks
Because the API does not encode ownership, callers must pair inserted keys/data with the right destructors. Changes to `struct symtab` affect `policydb` layout and initialization/destruction loops.

## Test Signals
Compiler coverage plus policy load/search tests are enough for this small wrapper. Debug hash evaluation in `policydb.c` can expose pathological table sizing.
