# sources/distributed-fs/ceph/src/osd/ECUtilL.h

## Purpose

`ECUtilL.h` declares the legacy erasure-coded object utility layer under `ECLegacy::ECUtilL`. It concentrates stripe geometry conversions, erasure-code encode/decode entry points, and legacy per-shard hash metadata used by `ECBackendL`, `ECCommonL`, `ECTransactionL`, and scrub code. The file is a header contract: most algorithms are implemented in `ECUtilL.cc`, but this file defines the invariants callers rely on when translating logical object offsets to per-shard chunk ranges and when persisting hash information in object xattrs.

## Important APIs, Types, and Functions

`stripe_info_t` stores immutable EC layout facts: `stripe_width`, per-data-shard `chunk_size`, data chunk count `k`, coding chunk count `m`, forward `chunk_mapping`, and reverse mapping. Constructors derive these from `ErasureCodeInterfaceRef` or explicit unit-test values and assert that stripe width is divisible by `k`. `complete_chunk_mapping()` fills absent mapping entries with identity positions; `reverse_chunk_mapping()` asserts the mapping is a bijective permutation.

The offset helpers form the main public API: `logical_to_prev_chunk_offset()`, `logical_to_next_chunk_offset()`, `logical_to_prev_stripe_offset()`, `logical_to_next_stripe_offset()`, `aligned_logical_offset_to_chunk_offset()`, `chunk_aligned_logical_offset_to_chunk_offset()`, `chunk_aligned_logical_size_to_chunk_size()`, `aligned_chunk_offset_to_logical_offset()`, `chunk_aligned_offset_len_to_chunk()`, `offset_len_to_stripe_bounds()`, `offset_len_to_chunk_bounds()`, `offset_length_to_data_chunk_indices()`, and `offset_length_is_same_stripe()`.

The free functions `encode()` and two overloads of `decode()` are the legacy adapters to `ErasureCodeInterface`. `HashInfo` tracks `total_chunk_size`, `cumulative_shard_hashes`, and ephemeral `projected_total_chunk_size`. It exposes append, clear, encode/decode, dump, test-instance generation, logical-size conversions, xattr key helpers `is_hinfo_key_string()` and `get_hinfo_key()`, and `update_to()` for refreshing committed hash state while preserving projection.

## Control Flow and Data Flow

The header's inline control flow is mostly arithmetic normalization. Logical offsets round down or up to stripe boundaries, then convert to chunk offsets by dividing by the data stripe fanout. Chunk-size conversions assert chunk alignment rather than silently repairing caller mistakes. `offset_len_to_stripe_bounds()` converts an arbitrary logical extent to a stripe-aligned logical span; `chunk_aligned_offset_len_to_chunk()` is declared here and implemented by applying that span to per-chunk coordinates.

Data flows from pool EC profile and `ErasureCodeInterface` into `stripe_info_t`, then into read, write, repair, and scrub paths. Encode callers pass a stripe-aligned logical buffer and desired shard set; decode callers pass available shard buffers and either a concatenated output list or per-shard output pointers. `HashInfo` data flows through the hidden xattr named by `get_hinfo_key()`, with projected size allowing transaction code to reason about in-flight object size before metadata commits.

## State and Persistence Behavior

`stripe_info_t` is immutable after construction and persists no disk state. `HashInfo` is the persistent piece: `total_chunk_size` and `cumulative_shard_hashes` are encoded with Ceph's `ENCODE_START` framework and stored in an internal EC xattr. `projected_total_chunk_size` is explicitly ephemeral; decode resets it to the committed `total_chunk_size`, and `update_to()` preserves the caller's projection while replacing committed hash fields. `set_total_chunk_size_clear_hash()` intentionally discards shard hash coverage while retaining size.

## Dependencies and Integration Points

This header depends on `ErasureCodeInterface`, Ceph bufferlists, encoding helpers, `Formatter`, `ceph_assert`, `shard_id_t`, and standard containers. It integrates with `ECUtilL.cc` for implementation, `ECBackendL` for xattr sanitation and object IO, `ECCommonL` for recovery reads and `UnstableHashInfoRegistry`, `ECTransactionL` for write transformations and rollback xattrs, and scrub code that compares legacy hash info against authoritative object state.

## Risks and Edge Cases

Most validation uses `ceph_assert`, so production behavior assumes callers have already satisfied alignment, mapping, and buffer-size preconditions. `reverse_chunk_mapping()` indexes `used.at(index)` after converting signed mapping values, so invalid negative or out-of-range mappings abort. Zero-size encode/decode paths are valid but must not be confused with missing data. Hash state may be absent after `set_total_chunk_size_clear_hash()`, so consumers must check `has_chunk_hash()` before trusting per-shard hashes. Logical-to-chunk conversion can overflow if very large offsets are added without caller bounds.

## Test Signals

Useful tests should cover identity and non-identity chunk mappings, mapping bijection assertions, aligned and unaligned offset/length conversions, zero-length encode/decode, partial repair decode through `minimum_to_decode()`, and round-trip `HashInfo` encoding. EC integration tests should verify `hinfo_key` is stripped from user-visible attributes, preserved for internal legacy EC objects, updated across appends, reset on decode, and compared by scrub. Unit-test constructors and `HashInfo::generate_test_instances()` are explicit hooks for encoding and formatter regression tests.
