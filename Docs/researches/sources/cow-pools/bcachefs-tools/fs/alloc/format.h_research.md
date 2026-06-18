# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/format.h

On-disk allocation metadata format header.

Defines:
- Legacy `struct bch_alloc`, `bch_alloc_v2`, and `bch_alloc_v3` formats.
- Current `struct bch_alloc_v4`, the main per-bucket alloc-btree value.
- Field lists for v1/v2 variable fields.
- Compatibility flags for need-discard and need-inc-gen.
- `BCH_ALLOC_V4_U64s_V0` and `BCH_ALLOC_V4_U64s` size constants.
- Alloc-v4 bitfields for discard/inc-gen and backpointer packing metadata.
- Bucket generation key format: `struct bch_bucket_gens`, with 256 generation bytes per key.

Important alloc-v4 semantics:
- `data_type` stores current bucket state.
- Empty-state transitions are explicit:
  - nonempty to empty becomes `BCH_DATA_need_discard`.
  - need-discard to empty becomes `BCH_DATA_free`.
  - free with exhausted GC generation becomes `BCH_DATA_need_gc_gens`.
- `journal_seq_nonempty` and `journal_seq_empty` track bucket state transitions for noflush and discard safety.
- `NEED_DISCARD` is retained for forward/backward compatibility, though current `alloc_data_type()` no longer reads it.
- `stripe_refcount`, `stripe_sectors`, dirty/cached sector counts, IO times, generation fields, and external backpointer counters support allocator, GC, LRU, and EC logic.

Role:
- This header is the shared wire format consumed by alloc triggers, discard, freespace, LRU, backpointer, and foreground allocation code.
