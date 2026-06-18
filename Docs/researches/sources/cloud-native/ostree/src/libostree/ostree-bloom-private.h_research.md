<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bloom-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bloom-private.h

## Purpose
Declares libostree's internal Bloom filter API for building, sealing, loading, and querying compact membership filters.

## Important APIs and Types
Defines opaque `OstreeBloom` and `OstreeBloomHashFunc(element, k)`. Declares constructors `ostree_bloom_new()` and `ostree_bloom_new_from_bytes()`, ref management, `ostree_bloom_add_element()`, `ostree_bloom_seal()`, `ostree_bloom_maybe_contains()`, getters for size/k/hash function, and `ostree_str_bloom_hash()`.

## Control Flow
No control flow exists in the header. The API shape enforces a mutable-build then immutable-query lifecycle.

## State and Persistence
The serialized persistent state is only the bit array returned by `ostree_bloom_seal()`. Callers must persist the hash function identity and `k` separately.

## Dependencies and Integration Points
Depends on GLib/GObject/GIO and libglnx. It declares a boxed type and autoptr cleanup, so internal users can store filters as boxed values or stack-managed pointers.

## Risks
This is marked internal and unstable. Loading bytes with the wrong `k` or hash function silently changes membership semantics. Bloom filters are probabilistic: false positives are expected, false negatives indicate bugs or parameter mismatch.

## Test Signals
Tests should verify add/query behavior, serialized byte stability, getter consistency, false-negative absence, and string hash determinism.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bloom-private.h -->
