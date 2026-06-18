# sources/cloud-native/composefs/libcomposefs/hash.c

## Purpose
`hash.c` is the bundled gnulib generic hash-table implementation used inside libcomposefs for small internal indexes, notably shared xattr deduplication and image-load inode tracking. It provides separate-chaining buckets, optional custom hash/comparator/free callbacks, load-factor-based growth, optional shrink behavior, and traversal helpers.

## Important APIs, Types, And Functions
The private `struct hash_entry` stores user data plus overflow links. `struct hash_table` owns bucket storage, counts, tuning, callbacks, and a recycled overflow-entry list. Public implementations include `hash_initialize`, `hash_free`, `hash_clear`, `hash_lookup`, `hash_insert`, `hash_insert_if_absent`, `hash_remove`, `hash_rehash`, `hash_get_entries`, and statistics helpers. `safe_hasher` aborts if a caller-provided hasher returns an out-of-range bucket. `hash_string` supplies the string hash used by composefs filters and xattr keys.

## Control Flow
Initialization validates tuning, chooses a prime bucket count, and allocates zeroed bucket heads. Lookup hashes to a bucket then compares the head and overflow chain. Insert checks for an existing equal entry, grows when used buckets exceed the threshold, and either fills an empty head or allocates/reuses an overflow entry. Remove unlinks matching data, recycles overflow nodes, and may shrink. Rehash transfers entries to a stack-local table and carefully rolls back on allocation failure.

## State And Persistence
All state is in-memory only. The table does not copy user data; ownership of stored data is defined by the caller and optional `data_freer`.

## Dependencies And Integration Points
It depends on `hash.h`, `bitrotate.h`, `xalloc-oversized.h`, libc allocation, and `config.h` compile flags. Meson forces `USE_OBSTACK=0`, `TESTING=0`, and `USE_DIFF_HASH=0`, so composefs uses malloc-backed buckets and the recode-style string hash.

## Risks
Hashers that return values outside the bucket range abort. NULL entries are unsupported and abort in insert-if-absent. Traversal is invalid across table mutation as documented in the header. Rehash rollback is complex and should be treated as high-risk for allocation-failure changes.

## Test Signals
There is no direct hash-table test in this subset. Coverage is indirect through EROFS writer shared-xattr tables, loader inode hash tables, and filtered toplevel entry hashing in `test-checksums.sh`, `test-random-fuse.sh`, and `test-lcfs.c`.
