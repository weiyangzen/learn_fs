# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extent_update.c

Implements trimming of large extent updates so atomic btree transactions do not require too many alloc/EC iterators.

Key entry point:
- `bch2_extent_trim_atomic()` scans overlapping keys and cuts back an insert if the estimated iterator count would exceed `EXTENT_ITERS_MAX`.

Important details:
- Counts alloc and EC btree iterator needs from extent pointer entries, cached-pointer LRU updates, and reflink indirections.
- Handles whiteouts with type-aware filtering while still supplying max keys needed by snapshot ancestry assertions.
- For reflink pointers, walks the reflink btree to account for referenced extents and their alloc pointer updates.
- Emits an `extent_trim_atomic` trace event when trimming occurs.

Dependencies and interactions:
- Uses extent pointer decoding helpers from `extents.h`, btree iter/update APIs, and interior btree logic.
