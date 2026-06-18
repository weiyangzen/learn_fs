# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/segment.h

## Purpose
Declares the generic pcache segment metadata and in-memory segment view. It provides flag/type helpers, segment-position arithmetic, copy APIs, and initialization options shared by the cache segment and request code.

## Important APIs, Types, And Functions
`struct pcache_segment_info` is the persistent segment header containing `pcache_meta_header`, flags, and `next_seg`. `PCACHE_SEG_INFO_FLAGS_HAS_NEXT` records segment chaining, and `PCACHE_SEG_INFO_FLAGS_TYPE_MASK` stores the segment type, currently `PCACHE_SEGMENT_TYPE_CACHE_DATA`. `struct pcache_segment` holds the cache device, data pointer, data size, segment id, and pointer to the associated segment info.

Inline helpers include `segment_info_has_next()`, `segment_info_set_type()`, `segment_info_get_type()`, and `segment_pos_advance()`. The header declares `segment_copy_to_bio()`, `segment_copy_from_bio()`, and `pcache_segment_init()`.

## Control Flow
Cache code creates a `pcache_segment_init_options` object with a physical segment id, type, data offset, and segment-info pointer, then calls `pcache_segment_init()` to derive the usable data window. Segment positions advance monotonically within `segment->data_size` and fail fast via `BUG_ON()` if callers overrun.

## State And Persistence
`pcache_segment_info` is persistent when written by cache-segment code; `pcache_segment` and `pcache_segment_pos` are volatile views. The `next_seg` field links cache segments in on-media order, which is used during replay/writeback/GC to walk the cache log.

## Dependencies And Integration Points
The header depends on block bio types, bitfield helpers, and `pcache_internal.h`. It is included by segment copy code, cache segment metadata code, and cache key/data paths that need to move positions or inspect segment types.

## Risks
Segment type and `has_next` share the same flags word, so future flags must avoid overlapping `PCACHE_SEG_INFO_FLAGS_TYPE_MASK`. `segment_pos_advance()` uses `BUG_ON()` instead of returning an error, making metadata corruption or caller arithmetic bugs fatal. There is no bounds checking in the copy API declarations; callers must enforce it.

## Test Signals
Build tests should catch type/flag helper changes. Runtime tests should cover segment chaining, end-of-segment advancement, replay of `next_seg`, and copy operations at exact segment-data boundaries.
