## sources/distributed-fs/moosefs/mfsmaster/patterns.c

Purpose: manages automatic file creation patterns that match names and user/group selectors to apply storage class, trash retention, and extended attribute masks. It stores patterns in metadata, exposes admin add/delete/list operations, and provides the runtime matcher used by filesystem creation paths.

Important APIs and types: `pattern` stores compiled `glob`, validity/modified flags, glob name, effective uid/gid filters, priority, operation mask, storage class id, trash retention, and set/clear eattr masks. `patterntab` is a fixed 1024-entry array sorted by validity, descending priority, storage class id, and name; `validpatterns` marks active prefix length. Key functions are `patterns_find_matching`, `patterns_add`, `patterns_delete`, `patterns_mr_add`, `patterns_mr_delete`, `patterns_sclass_delete`, `patterns_list`, `patterns_store`, `patterns_load`, `patterns_cleanup`, and `patterns_init`.

Control flow: add validates nonempty glob and eattr mask consistency, resolves storage class name if requested, rejects duplicates, fills the first free slot, recompiles modified glob entries, sorts, and either changelogs `PATADD` or increments metadata version for replay. Delete marks matching entries invalid, recompiles/sorts, and changelogs or increments metadata version. Matching scans the sorted active prefix and returns the first pattern whose uid/gid filter and glob match. Loading clears existing patterns, reads records until a sentinel, supports old version `0x10` without `clreattr`, and optionally skips excess entries under `ignoreflag`.

State and persistence behavior: patterns are persisted in metadata section `PATT`, version `0x11`. Runtime compiled glob objects are rebuilt after load/add/delete and freed on invalidation. Admin operations are changelogged; replay operations update metadata version.

Dependencies and integration points: depends on `globengine`, `storageclass`, `metadata`, `changelog`, `main`, `bio`, `datapack`, `mfslog`, and MooseFS status/error constants. `metadata.c` loads storage classes before patterns, and filesystem creation code can query `patterns_find_matching`.

Risks: fixed capacity returns `MFS_ERROR_PATLIMITREACHED`. Sorting means table index is not stable across changes. Glob compilation happens for every modified valid pattern during `patterns_have_changed`; invalid patterns free their glob. `patterns_sclass_delete` silently removes patterns referencing a deleted storage class, which can change create behavior.

Test signals: test duplicate detection, capacity limit, eattr validation, storage class lookup, priority ordering, uid/gid filtering, glob matching, changelog vs replay paths, section version load compatibility, too-many-pattern handling with and without ignore, list buffer sizing, and storage-class deletion side effects.
