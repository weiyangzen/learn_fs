# sources/distributed-fs/ceph/src/osd/ECUtil.cc

Purpose: `ECUtil.cc` implements optimized EC extent translation, shard extent map mutation, encoding, decoding, padding, trimming, buffer extraction, debug output, and small helper functions.

Important APIs and functions: `stripe_info_t::ro_range_to_shards` maps RADOS object ranges to per-shard extents and optional shard buffers. `shard_extent_map_t` implements `intersect`, `insert`, `insert_ro_extent_map`, `insert_parity_buffers`, `encode`, `encode_parity_delta`, `decode`, `_decode`, `pad_and_rebuild_to_ec_align`, `get_ro_buffer`, `zero_pad`, `pad_with_other`, `trim`, and containment helpers. `shard_extent_set_t` implements subtract/intersection/insert. The file also defines `log_entry_t` streaming and hinfo-key compatibility helpers.

Control flow: range translation minimizes divisions, computes starting/ending raw shards, applies partial chunk offsets, and inserts shard ranges or sliced buffers. Encode/decode iterate common aligned slices; if any buffer is not page-aligned, maps are rebuilt/padded and retried. Decode first reconstructs missing data shards, then encodes requested parity shards when needed, and finally trims invented buffers back to requested extents.

State and persistence: state is in-memory extent maps over shard offsets. It directly determines what bytes are written to ObjectStore transactions by higher layers. `get_hinfo_key` remains for upgraded pools with legacy metadata.

Dependencies and integration: uses `ECUtil.h`, erasure-code plugin chunk APIs, Ceph buffer alignment/CRC behavior, interval maps, and `DoutPrefixProvider`. `ECTransaction` depends on these transformations for write generation.

Risks: off-by-one or alignment mistakes corrupt EC layout. `slice_map` appears to use `min` where `max` may be expected for some range fields, so slice-related changes need scrutiny. Rebuild retries must terminate. Parity delta writes assume plugin support and aligned old/new buffers.

Test signals: key tests include RO-to-shard mapping across stripe boundaries, partial chunks, custom chunk mappings, encode/decode with missing shards, parity reconstruction, zero dedup, unaligned buffers forcing rebuild, PDW parity updates, and round-trip `get_ro_buffer`.
