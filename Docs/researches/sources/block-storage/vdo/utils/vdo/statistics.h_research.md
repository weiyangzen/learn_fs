# File Research: sources/block-storage/vdo/utils/vdo/statistics.h

Defines the VDO statistics ABI consumed by stats readers/writers.

Key details:
- `STATISTICS_VERSION = 36`.
- Defines nested statistic groups for allocator, commit pipeline, recovery journal, packer, slab journal, slab summary, ref counts, block map, hash locks, error counts, bio categories, memory usage, and UDS index.
- `struct vdo_statistics` combines capacity/use counters, mode/recovery fields, nested statistics, bios by stage, memory usage, and index stats.
- File header documents companion files that must be updated when adding statistics.

Research relevance:
- `messageStatsReader.c` mirrors this structure field by field; drift between text stats and this struct breaks parsing/reporting.
