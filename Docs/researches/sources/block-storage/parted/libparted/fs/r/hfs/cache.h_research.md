# File Research: sources/block-storage/parted/libparted/fs/r/hfs/cache.h

Defines the HFS common extent-cache structures and reference tags.

Key definitions:
- `CR_*` constants identify where an extent reference comes from, such as primary catalog/extents/allocation records, B-tree records, journal info block, or journal.
- Cache tuning constants control hash/index granularity and allocation table growth.
- `HfsCPrivateExtent` records extent start/length plus the metadata location that references it.
- `HfsCPrivateCacheTable` stores allocated extent records.
- `HfsCPrivateCache` owns the table list, linked-reference index, and required buffer size.

Exports:
- Cache create/delete.
- Add/search/move extent.
- Inline needed-buffer query.

Role:
- Support layer for HFS/HFS+ relocation modules outside this file group.
