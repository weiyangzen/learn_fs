# File Research: sources/block-storage/kvdo/vdo/pool-sysfs-stats.c

Read completely: 2065 lines.

This file exposes VDO runtime statistics under the pool `statistics` sysfs directory. It defines `struct pool_stats_attribute`, a read-only sysfs show path, `vdo_pool_stats_sysfs_ops`, and the exported `vdo_pool_stats_attrs[]` table consumed by the pool sysfs setup.

Every attribute read takes `vdo->stats_mutex`, refreshes `vdo->stats_buffer` with `vdo_fetch_statistics()`, calls the attribute-specific printer, and unlocks. The file is mostly a generated-style projection from `struct vdo_statistics` fields to one sysfs file per counter, using `sprintf()` with numeric or string formatting.

Statistics covered include capacity and block usage, recovery counters and mode, packer counters, allocator counters, recovery journal events, slab journal events, slab summary and refcount writes, block map cache/page counters, hash/dedupe lock counters, error counters, instance/VIO counts, dedupe timeout and flush counters, logical block size, memory usage, UDS index counters, and many bio counters split by operation class and stage. Bio groups include incoming, partial incoming, outgoing, metadata, journal, page cache, completed variants, acknowledged variants, partial acknowledged, and in-progress.

Dependencies: Linux kobject/sysfs conventions, `vdo_fetch_statistics()`, `struct vdo_statistics`, `vdo->stats_directory`, `vdo->stats_mutex`, `logger.h`, `dedupe.h`, `statistics.h`, and `pool-sysfs.h`.

Security/reliability notes: attributes are read-only and serialized around a single stats buffer. The implementation assumes all printed values fit sysfs buffers and uses legacy `sprintf()` rather than bounded helpers. The file has no mutation path; correctness depends on `vdo_fetch_statistics()` producing a coherent snapshot while protected by `stats_mutex`.
