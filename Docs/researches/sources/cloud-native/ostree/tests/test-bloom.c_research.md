# sources/cloud-native/ostree/tests/test-bloom.c

Purpose: GLib unit tests for OSTree's private bloom filter implementation.

Important APIs/types/functions: `OstreeBloom`, `ostree_bloom_new`, `ostree_bloom_new_from_bytes`, `ostree_bloom_get_size`, `ostree_bloom_get_k`, `ostree_bloom_get_hash_func`, `ostree_bloom_add_element`, `ostree_bloom_seal`, `ostree_bloom_maybe_contains`, and `ostree_str_bloom_hash`.

Control flow: registers tests for constructor initialization, building/sealing/reloading a filter, empty-filter negative membership, and membership checks while incrementally adding elements.

State/persistence: all state is in-memory `OstreeBloom` and `GBytes`; no filesystem persistence. Dependencies are GLib and private bloom headers.

Integration/risk/test signals: protects summary/repo-finder acceleration primitives that rely on stable hashes. Risks are false-positive theory versus tests that expect specific non-members to be false because the hash function is stable. GLib test paths report success.
