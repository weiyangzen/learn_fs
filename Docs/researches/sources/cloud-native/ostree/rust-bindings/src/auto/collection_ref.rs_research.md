# sources/cloud-native/ostree/rust-bindings/src/auto/collection_ref.rs

Purpose: Generated boxed wrapper for `OstreeCollectionRef`, representing a collection ID plus ref name for peer-to-peer and collection-aware repository operations.

Important APIs: `CollectionRef::new(collection_id, ref_name)`, private wrapper methods for equality and hash, plus Rust `PartialEq`, `Eq`, and `Hash` implementations that delegate to libostree.

Control flow and state: Construction allocates a boxed C struct; cloning/freeing use GLib boxed copy/free with the OSTree type. Equality and hash are computed by libostree, preserving C semantics.

Dependencies and integration points: Feature-gated by `v2018_6` in `mod.rs`. Integrates with collection-ID refs, repo finders, summary metadata, and any Rust APIs that use collection-aware references.

Risks: Hash implementation hashes the C-provided `u32` hash value into Rust's hasher, so it mirrors libostree equality but compresses identity through a 32-bit value. `collection_id` is optional, so callers must understand local refs versus collection refs.

Test signals: Equality/hash property tests for same/different collection IDs and ref names, compile under `v2018_6`, and integration with collection-aware repo lookups.
