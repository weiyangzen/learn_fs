# sources/cloud-native/ostree/src/libostree/ostree-rollsum.c

Purpose: computes rolling-checksum chunk matches between two byte blobs for delta-style reuse analysis. It chunks both inputs with bupsplit bounded by `ROLLSUM_BLOB_MAX`, hashes chunks with CRC32, then confirms candidate matches by byte comparison.

Important APIs/types/functions: `ROLLSUM_BLOB_MAX` caps chunks at 32 KiB. `rollsum_chunks_crc32` returns a hash table keyed by CRC32, with values as arrays of `(crc,start,length)` `GVariant`s. `compare_matches` sorts final matches by destination offset. `_ostree_compute_rollsum_matches` produces `OstreeRollsumMatches`. `_ostree_rollsum_matches_free` releases hash tables, match array, and result struct.

Control flow: `rollsum_chunks_crc32` walks a `GBytes` buffer, asks `bupsplit_find_ofs` for boundaries until bupsplit returns 0, then switches to fixed-size chunks. It computes CRC32, stores triples under that CRC, and advances. `_ostree_compute_rollsum_matches` builds source and target chunk tables, finds shared CRCs, skips length mismatches, confirms by `memcmp`, appends `(crc,length,to_start,from_start)`, updates counters, sorts matches, and transfers ownership to the result.

State/persistence: all state is transient and in-memory: rollsum tables, counters, and match arrays. No filesystem, repository, or global state is changed. The caller owns the returned result.

Dependencies/integration: depends on `bupsplit.h`, zlib `crc32`, GLib `GBytes`, `GHashTable`, `GPtrArray`, and `GVariant`, plus libglnx cleanup helpers. Tests build this file directly with bupsplit/zlib.

Risks: CRC32 is only a prefilter and collisions are handled by `memcmp`, but repeated chunks can still create many candidate comparisons. The chunking loop computes `crc32(crc, buf, offset)` rather than `buf + start`, which deserves review because chunk validation later uses offsets. Tuple formats are implicit and easy to misuse.

Test signals: `tests/test-rollsum.c` exercises conflicting data, identical and shifted buffers, random buffers, and manual free paths; `tests/test-rollsum-cli.c` prints counters and match size for inspection.
