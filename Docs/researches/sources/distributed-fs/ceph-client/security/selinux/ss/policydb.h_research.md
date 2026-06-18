# sources/distributed-fs/ceph-client/security/selinux/ss/policydb.h

## Purpose
`policydb.h` defines the in-kernel shape of an SELinux policy database and the serialized policy buffer helpers. It is the contract between the parser/writer in `policydb.c`, the security server in `services.c`, MLS code, conditional policy code, and SID conversion code.

## Important APIs, Types, and Functions
Key datum types include `perm_datum`, `common_datum`, `class_datum`, `role_datum`, `type_datum`, `user_datum`, `level_datum`, `cat_datum`, `cond_bool_datum`, `type_set`, `ocontext`, and `genfs`. Lookup keys include `role_trans_key`, `filename_trans_key`, and `range_trans`. `struct policydb` owns symbol tables, value-to-name arrays, value-to-struct arrays, TE/conditional AV tables, role/filename/range transition hash tables, role allows, object contexts, genfs contexts, type-attribute maps, policycaps, permissive and neveraudit maps, policy version, unknown handling flags, and process transition permission masks. `struct policy_file` is a moving buffer cursor for binary policy data.

## Control Flow
The header establishes numeric indices for symbol classes (`SYM_*`) and object contexts (`OCON_*`) that drive loop-based parser/destructor code. Inline `next_entry()` and `put_entry()` are the central policy stream operations: they bound-copy from/to the buffer and advance the cursor.

## State and Persistence
The declarations encode both persistent policy concepts and transient indexes. Arrays such as `sym_val_to_name` and `class_val_to_struct` are derived from symbol tables after parsing. `policydb.len` records the binary policy length for later readback.

## Dependencies and Integration Points
It includes `symtab`, `avtab`, `sidtab`, `ebitmap`, `mls_types`, `context`, and `constraint`, making it a central SELinux SS header. External callers use the validity, lookup, read, write, and destroy prototypes rather than reaching into parser internals.

## Risks
Any layout change must be synchronized with parser version compatibility and all destroy paths. The symbol and object-context enum counts are baked into compatibility checks. `put_entry()` relies on multiplication overflow detection; callers must pass correct element sizes and counts.

## Test Signals
Compilation across SELinux MLS, NetLabel, Infiniband, and conditional policy configurations is a baseline. Policy load/readback tests should cover every `OCON_*` and `SYM_*` kind and confirm unknown-class flags and policycaps survive a round trip.
