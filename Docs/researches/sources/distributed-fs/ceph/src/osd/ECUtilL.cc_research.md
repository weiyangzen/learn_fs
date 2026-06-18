# sources/distributed-fs/ceph/src/osd/ECUtilL.cc

Purpose: `ECUtilL.cc` implements legacy EC utility functions for stripe/chunk conversion, deprecated plugin encode/decode wrappers, and legacy `HashInfo` persistence helpers.

Important APIs and functions: `stripe_info_t::chunk_aligned_offset_len_to_chunk` converts logical chunk-aligned ranges to chunk offsets. Two `decode` overloads reconstruct either a concatenated logical output or requested shard outputs using deprecated erasure-code APIs and subchunk repair hints. `encode` splits logical full stripes and appends encoded shard buffers. `HashInfo::append`, `encode`, `decode`, `dump`, stream output, and generated test instances manage legacy hinfo metadata. `is_hinfo_key_string`/`get_hinfo_key` expose the legacy attr key.

Control flow: encode walks the input one full stripe at a time and appends each encoded chunk to shard bufferlists. Decode validates equal shard buffer lengths, slices per chunk or repair-data window, calls plugin decode, and appends outputs. `HashInfo::append` updates cumulative CRCs when hashes are present and advances total chunk size.

State and persistence: `HashInfo` persists total chunk size and cumulative shard hashes in the `hinfo_key` object attr for legacy EC objects. It also carries an ephemeral projected chunk size for in-flight planning.

Dependencies and integration: uses `ECUtilL.h`, Ceph encoding macros, `bufferlist`, `Formatter`, and deprecated erasure-code plugin methods hidden behind ignore-deprecated macros. Consumed by `ECTransactionL`, legacy backend recovery/scrub, and hinfo registry code.

Risks: deprecated plugin APIs and manual subchunk calculations are compatibility-sensitive. Assertions assume aligned and nonempty buffers. Clearing hashes on truncation removes hash validation data, which is intentional but affects scrub signals.

Test signals: generated `HashInfo` test instances support encoding tests. Additional coverage should check encode/decode round trips, subchunk repair decode, hinfo append CRC updates, decode of persisted hinfo, and legacy attr-key filtering.
