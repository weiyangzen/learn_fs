## sources/distributed-fs/orangefs/src/io/trove/trove-types.h

Purpose: Provides Trove's type facade over PVFS2 storage types and maps PVFS error constants into the Trove error namespace.

Important APIs and definitions: Type aliases map handles, extents, sizes, offsets, operation IDs, collection IDs, dataspace types, vtags, flags, keyvals, attributes, states, contexts, statfs, getinfo options, and object refs from `PVFS_*` to `TROVE_*`. `TROVE_method_id` enumerates DBPF, alt-aio, null-aio, and direct-io variants. `TROVE_method_callback` selects a method per collection. Macros define null handles/collection IDs, attribute conversion aliases, and many `TROVE_E*` constants as `PVFS_E* | PVFS_ERROR_TROVE`.

Control flow: Header-only definitions; it influences all Trove compile units by preserving a separate Trove naming layer while using PVFS binary representations.

State and persistence: None. The aliases are part of the source-level and ABI contract between Trove and PVFS components.

Dependencies and integration points: Includes `pvfs2-internal.h`, `pvfs2-types.h`, and `pvfs2-storage.h`. Included by public Trove APIs, internal method tables, handle management, and DBPF code.

Risks: Because most types are aliases, Trove is not actually insulated from PVFS representation changes. Error constants are bitwise combinations and must stay consistent with PVFS error handling. Adding a new method requires updating this enum and every method table in `trove-mgmt.c`. The comment notes the abstraction may be historical rather than strict.

Test signals: Compile against current PVFS headers, assert sizes/layouts for aliased structs used on disk or across process boundaries, verify error translation and formatting for `TROVE_E*`, and test every `TROVE_method_id` table entry.
