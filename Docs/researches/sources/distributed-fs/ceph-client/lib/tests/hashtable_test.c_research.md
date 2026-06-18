
# sources/distributed-fs/ceph-client/lib/tests/hashtable_test.c

## Purpose
`hashtable_test.c` validates Linux kernel hashtable macros for initialization, emptiness, hashed-node detection, insertion, deletion, full iteration, safe deletion during iteration, and key-bucket iteration.

## Important APIs, types, and functions
The local `struct hashtable_test_entry` embeds an `hlist_node` plus `key`, `data`, and `visited`. Tests use `DEFINE_HASHTABLE`, `DECLARE_HASHTABLE`, `hash_init()`, `hash_empty()`, `hash_add()`, `hash_hashed()`, `hash_del()`, `hash_for_each()`, `hash_for_each_safe()`, `hash_for_each_possible()`, and `hash_for_each_possible_safe()`.

## Control flow
Each KUnit case builds a small stack hashtable, inserts one or more entries, then validates macro behavior. The possible-iteration tests intentionally add three entries with key 0 and one entry with key 1, then inspect bucket placement to allow either three or four visits depending on whether both keys hash to the same bucket. Safe tests delete entries during traversal and verify each original entry was visited once.

## State and persistence
All hashtables and entries are stack-local. `visited` fields provide per-test state for traversal coverage.

## Dependencies and integration points
The file depends on `<linux/hashtable.h>` and KUnit and is built by `CONFIG_HASHTABLE_KUNIT_TEST`.

## Risks and edge cases
Because `hash_for_each_possible()` iterates a bucket rather than filtering by key, the test correctly accepts same-bucket non-key entries. Future readers must not tighten that expectation incorrectly. The tests do not cover concurrent RCU hashtable variants.

## Test signals
Failures indicate unexpected emptiness, missing hashed state, unexpected keys/data during traversal, incorrect visit counts, or failed deletion semantics.
