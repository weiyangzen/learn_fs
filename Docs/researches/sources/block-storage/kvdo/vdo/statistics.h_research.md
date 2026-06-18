# File Research: sources/block-storage/kvdo/vdo/statistics.h

This header defines the versioned VDO statistics ABI, with `STATISTICS_VERSION = 35`. It is a struct-only aggregation header used by stats collection and sysfs/reporting paths.

Covered statistics groups include block allocator, commit pipeline, recovery journal, packer, slab journal, slab summary, reference counts, block map cache, hash locks, error counters, bio classes, memory usage, UDS index, and the top-level `struct vdo_statistics`.

`struct vdo_statistics` combines configuration/identity fields, logical/physical usage, recovery counters, mode string, recovery progress, nested component stats, bio in/out/meta/journal/page-cache counters, active VIO counts, dedupe timeout counts, flush counts, logical block size, memory usage, and index stats. Types come from `types.h`, so block counts remain consistent with on-disk VDO type definitions.
