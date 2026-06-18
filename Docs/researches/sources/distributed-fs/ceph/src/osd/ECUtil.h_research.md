# sources/distributed-fs/ceph/src/osd/ECUtil.h

Purpose: `ECUtil.h` declares optimized EC utility containers and algorithms for mapping RADOS object byte ranges onto erasure-coded shard extents, slicing shard buffers for plugin encode/decode, and representing EC read/write logs.

Important APIs and types: `extent_set`/`extent_map` are flat interval containers. `slice_iterator` walks common buffer slices across shards, exposing input and output `bufferptr`s for plugin operations and optional zero dedup. `ECUtil::shard_extent_set_t` is a shard-indexed interval set. `stripe_info_t` encapsulates k/m, stripe width, chunk size, raw/logical shard mapping, feature flags, and range conversion helpers. `shard_extent_map_t` stores per-shard extent maps and exposes encode/decode/pad/trim/read helpers. `log_entry_t` records EC read pipeline events.

Control flow: callers build `stripe_info_t` from the EC plugin and pool, translate RO ranges to shard sets/maps, populate or reconstruct `shard_extent_map_t`, then call encode/decode. `slice_iterator` advances through the smallest common contiguous slice boundary and invalidates CRCs for output buffers before plugin mutation.

State and persistence: all structures are in-memory, but they model durable EC layout. `stripe_info_t` reads pool/plugin capabilities such as overwrites, partial reads/writes, parity delta writes, CRC encode/decode, direct reads, and nonprimary shard status.

Dependencies and integration: depends on erasure-code plugin interfaces, `osd_types.h`, Ceph buffers, interval maps, `mini_flat_map`, `shard_id_t`, `raw_shard_id_t`, and logging.

Risks: the API exposes mutable maps with cached RO ranges, so modifications must call methods that keep offsets in sync. Alignment constants are fixed at 4096. `slice_iterator` assumes input maps are nonempty and buffers are structurally valid.

Test signals: tests should cover stripe constructors, custom chunk mappings, object-to-shard size conversion, shard range conversion, slice iteration with uneven extents, zero dedup, support flag behavior, and encode/decode API preconditions.
