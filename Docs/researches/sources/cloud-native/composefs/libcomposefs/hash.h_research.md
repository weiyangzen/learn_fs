# sources/cloud-native/composefs/libcomposefs/hash.h

## Purpose
`hash.h` declares the gnulib hash-table API embedded in libcomposefs. It exposes the opaque `Hash_table`, tuning parameters, callback types, lookup/traversal APIs, allocation/free APIs, and insertion/removal functions consumed by internal composefs code.

## Important APIs, Types, And Functions
`Hash_tuning` controls shrink/growth thresholds, factors, and whether the initialization candidate is an entry count or bucket count. `Hash_hasher`, `Hash_comparator`, and `Hash_data_freer` define caller-provided behavior. Important functions are `hash_initialize`, `hash_free`, `hash_clear`, `hash_lookup`, `hash_get_entries`, `hash_do_for_each`, `hash_insert`, `hash_insert_if_absent`, `hash_remove`, `hash_rehash`, and `hash_string`.

## Control Flow
The header documents the caller contract: create a table with callbacks, insert non-NULL entries, look up by comparable key objects, optionally walk all entries, and release with `hash_free`. It also warns that mutation during traversal is restricted.

## State And Persistence
The header defines no persistent storage. It establishes that user entries are stored by pointer and that `data_freer` is invoked only during `hash_free`/`hash_clear`.

## Dependencies And Integration Points
It includes `config.h`, `stdio.h`, and `stdbool.h`, and uses GNU-style attributes. Composefs integrates it in `lcfs-writer-erofs.c` for xattr and inode maps.

## Risks
The declared `hash_xinitialize` and `hash_xinsert` are not implemented in `hash.c` in this subset; composefs does not use them. Callers must not pass NULL entries and must ensure hash/comparator consistency.

## Test Signals
No direct header tests exist. API compatibility is validated indirectly by successful libcomposefs build and tests that exercise writer/loader hash usage.
