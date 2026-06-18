<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bloom.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bloom.c

## Purpose
Implements an internal Bloom filter with stable serialized bit-array output and a SipHash-based string hash helper.

## Important APIs and Types
`struct _OstreeBloom` stores `ref_count`, `n_bytes`, mutability, either owned mutable bytes or immutable `GBytes`, `k`, and `hash_func`. Public-internal functions create mutable filters, load immutable filters from `GBytes`, ref/unref, add elements, query possible membership, seal to `GBytes`, return configuration, and hash strings through `ostree_str_bloom_hash()`.

## Control Flow
Creation validates size, `k`, and hash function. `ostree_bloom_add_element()` runs the hash function for `i=0..k-1`, modulo-maps each hash into `n_bytes * 8`, and sets bits. `ostree_bloom_maybe_contains()` repeats the hashes and returns false on the first missing bit. `ostree_bloom_seal()` converts mutable bytes into immutable `GBytes` and can be called repeatedly. `ostree_str_bloom_hash()` fills a 16-byte SipHash key with the `k` value and hashes the input string.

## State and Persistence
Before sealing, the bit array is mutable and owned as `guint8*`. After sealing or loading, state is immutable `GBytes`. The serialized format is the raw bit array only, so metadata must travel alongside it.

## Dependencies and Integration Points
Depends on GLib boxed types, `GBytes`, assertions, endian helpers, and the embedded SipHash implementation. It is suitable for repository metadata acceleration where compact approximate membership matters.

## Risks
`ostree_bloom_ref()` contains a notable guard requiring `ref_count == G_MAXUINT - 1`; that appears inverted for normal reference increments and should be covered by tests. The implementation is not thread-safe around mutable state or manual ref_count. False-positive rates depend entirely on caller-chosen size and `k`.

## Test Signals
Signals include ref/unref lifecycle tests, add/seal/query tests, load-from-bytes parity, deterministic serialized bytes, string hash test vectors, NULL validation behavior, and regression coverage for the `ostree_bloom_ref()` guard.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bloom.c -->
