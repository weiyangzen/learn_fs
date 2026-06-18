# File Research: sources/cow-pools/bcachefs-tools/include/linux/rhashtable.h

Kernel-style resizable hash table API for bcachefs-tools userspace compatibility. It defines `bucket_table`, bucket lock-bit encoding, nulls markers, hash helpers, traversal macros, lookup/insert/remove/replace inline paths, rhlist variants, and walker/destroy prototypes implemented elsewhere.

The core behavior mirrors Linux `rhashtable`: RCU-style lookup, per-bucket bit locks, deferred resize triggers via `schedule_work(&ht->run_work)`, load-factor grow/shrink thresholds, and fallback to `rhashtable_insert_slow()` during resize or overlong chains.

Risks are mostly semantic: this header assumes its userspace RCU/bitlock shims preserve enough kernel ordering. Misconfigured `rhashtable_params` can make key hashing/comparison inconsistent, and rhlist insertion/removal has subtle single-chain plus duplicate-list behavior.
