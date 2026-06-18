# File Research: sources/cow-pools/openzfs/module/zfs/dmu_send.c

Implements `zfs send` stream construction for full, incremental, raw, compressed, resumable, saved, and redacted sends.

Key points:
- Defines send tunables for corrupt-data substitution, queue sizing/fill fractions, estimate record size override, free-record emission, and unmodified spill block handling.
- Builds DMU replay records through `dump_record()`, maintaining the send stream Fletcher checksum and stream offset.
- Aggregates adjacent `DRR_FREE`, `DRR_FREEOBJECTS`, and `DRR_REDACT` records via `dsc_pending_op` to reduce stream record count.
- Emits `DRR_OBJECT`, `DRR_WRITE`, `DRR_WRITE_EMBEDDED`, `DRR_SPILL`, `DRR_OBJECT_RANGE`, `DRR_FREE`, `DRR_FREEOBJECTS`, `DRR_REDACT`, `DRR_BEGIN`, and `DRR_END`.
- Handles stream feature negotiation in `setup_featureflags()`: SA spill, large blocks, embedded data, compression, raw encrypted streams, LZ4, ZSTD, resuming, redaction, large dnodes, long names, and large microzap constraints.
- `send_do_embed()` gates embedded block emission on stream feature compatibility and compression support.
- Raw send paths preserve encrypted block parameters: byteswap state, salt, IV, MAC, compression type, compressed size, dnode raw bonus data, object range encryption metadata, and crypt keydata in the BEGIN nvlist.
- Non-raw encrypted sends authenticate the objset physical buffer before sending if needed.
- Large blocks are split to `SPA_OLD_MAXBLOCKSIZE` when the stream lacks large-block support.
- Corrupt blocks can either abort with `EIO` or be replaced by a recognizable bad-block fill pattern when `zfs_send_corrupt_data` is enabled.

Pipeline and threading:
- Represents work as `struct send_range`, covering data, holes, objects, object ranges, redaction ranges, previously redacted ranges, and EOS markers.
- `send_traverse_thread()` runs `traverse_dataset_resume()` with `send_cb()` to turn changed blocks/dnodes into ordered ranges.
- `redact_list_thread()` traverses redaction lists and emits either `REDACT` or `PREVIOUSLY_REDACTED` ranges.
- `send_merge_thread()` merges ranges from the target traversal, ancestor redaction list, and optional redact-book list, using priority rules so redaction metadata overrides lower-priority data where appropriate.
- `find_next_range()` slices overlapping ranges at change points, preserving sorted object/block order and selecting the highest-priority metadata for each interval.
- `send_reader_thread()` issues ARC/zio reads after redaction decisions are known, resolves `PREVIOUSLY_REDACTED` ranges against the target dnode, skips deleted objects, expands large holes efficiently via `dnode_next_offset()`, and piggybacks unmodified spill blocks on object records.
- The main thread dequeues prefetched ranges and calls `do_dump()` to serialize replay records.

Entry points:
- `dmu_send_obj()` sends by dataset object IDs and validates from-snapshot ancestry.
- `dmu_send()` sends by dataset/bookmark names, supports live filesystem or volume ownership, saved `%recv` streams, redaction bookmarks, resume object/offset, and clone detection.
- `dmu_send_impl()` is the central implementation: holds objsets/redaction lists, creates BEGIN payload nvlist fields, starts worker threads, drains the reader queue, emits END when appropriate, and cleans up holds/queues/status.
- `dmu_send_estimate_fast()` estimates stream size from dataset space accounting or bookmark deltas, with adjustment for indirect blocks and replay-record overhead.

Dependencies and interactions:
- Uses `dmu_traverse.c` via `traverse_dataset_resume()` for txg-filtered tree walking.
- Uses DSL dataset/bookmark/redaction-list APIs for ancestry, redacted dataset metadata, saved stream state, and redaction bookkeeping.
- Uses ARC/zio read paths for cached and direct data reads, including raw/compressed reads.
- Cooperates with receive-side stream compatibility through feature flags, record layout, payload padding, and checksum sequencing.

Research relevance:
- This is the main source for OpenZFS replication stream semantics. It ties together COW block birth times, dataset ancestry, encryption metadata, redaction, resumability, record ordering, and bounded prefetching into the on-wire `zfs send` format.
