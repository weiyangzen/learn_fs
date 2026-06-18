<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Filer.cc -->
# sources/distributed-fs/ceph/src/osdc/Filer.cc

## Purpose

`Filer.cc` implements the convenience layer that converts logical inode byte ranges into RADOS object operations. It is a thin but important bridge between `Striper` mapping and `Objecter` scatter/gather I/O: reads, writes, truncating writes, zero/removal operations, tail probing, object purging, and truncate-range maintenance all use file layout metadata to address the correct objects.

The file does not own durable state itself. Its state machines exist only to coordinate asynchronous object operations and then call the caller's `Context` when the requested logical file operation is complete.

## Important APIs and Functions

`Filer::read`, `read_trunc`, `write`, and `write_trunc` map the requested byte range with `Striper::file_to_extents` and immediately delegate to `Objecter::sg_read`, `sg_read_trunc`, `sg_write`, or `sg_write_trunc`. The truncating variants pass `truncate_size` and `truncate_seq` through to objecter so OSD-side truncate ordering is preserved.

`Filer::zero` maps the range and either issues a single object operation or builds a `C_GatherBuilder` for multi-object completion. Full-object zeroes become `Objecter::remove` unless `keep_first` is set for object number zero; partial extents become `Objecter::zero`.

`Filer::probe` and `probe_impl` allocate a `Probe` object, choose an initial probe window based on the layout period and direction, and then call `_probe`. `_probe` maps the current window into object extents and issues parallel `objecter->stat` calls using `C_Probe` callbacks on the configured `Finisher`. `_probed` collects object sizes and mtimes, detects the first non-full object in forward mode or first non-empty object in backward mode, computes the logical end offset through `ObjectExtent::buffer_extents`, and continues period-by-period when size or mtime discovery requires more data.

`purge_range` removes a sequence of file objects. A one-object purge is direct; larger purges use `PurgeRange` plus `_do_purge_range` to keep at most `filer_max_purge_ops` outstanding. `-ENOENT` is tolerated, other errors are saved and returned after all scheduled removals settle.

`truncate` and `_do_truncate_range` issue `CEPH_OSD_OP_TRIMTRUNC` over objects intersecting the truncate range. The one-object case calls `objecter->_modify` directly; larger ranges are rounded to layout periods and drained from the high end while respecting `filer_max_truncate_ops`.

## Control Flow

The simple read/write functions are synchronous setup for asynchronous objecter work: compute `vector<ObjectExtent>`, delegate, and rely on objecter to finish the caller context. Multi-object zero uses `C_GatherBuilder` so every remove/zero sub-operation completes before the original `oncommit`.

The probe path is a small asynchronous state machine. `_probe` is entered with the `Probe` mutex held, builds the next set of stats, unlocks, and submits objecter calls. Each `C_Probe::finish` normalizes `-ENOENT` to size zero, records errors, and calls `_probed` under the probe lock. `_probed` unlocks before returning and may recursively start the next probe window. This avoids holding the private probe lock while entering objecter or finishing user contexts.

Purge and truncate range control flow is bounded-concurrency drain. `_do_purge_range` and `_do_truncate_range` decrement outstanding counts when callbacks arrive, detect terminal completion when no work and no uncommitted operations remain, then schedule more operations up to the configured limit. Both explicitly issue objecter operations outside their state locks to avoid lock dependency loops.

## State and Persistence Behavior

`Filer.cc` persists data only indirectly through `Objecter` operations sent to OSDs. The transient states are `Probe`, `PurgeRange`, and `TruncRange`. `Probe` tracks the current byte window, extents under stat, outstanding object ids, known sizes, maximum mtime, result size pointer, error, and whether size was found. `PurgeRange` tracks first object, remaining count, outstanding removals, and accumulated error. `TruncRange` tracks byte offset/length still to trim, outstanding object modifications, and truncate sequence.

The persistent effects are RADOS object reads/writes, object removes, object zeroes, and `TRIMTRUNC` mutations. Snapshot semantics come from `snapid_t` for reads/probes and `SnapContext` for writes/removes/zero/truncate operations.

## Dependencies and Integration Points

The implementation depends on `Objecter`, `Striper`, `OSDMap::file_to_object_locator`, `ObjectExtent`, `SnapContext`, `C_GatherBuilder`, `C_OnFinisher`, and Ceph config keys `filer_max_purge_ops` and `filer_max_truncate_ops`. `Journaler` uses this file heavily for journal head/data I/O, tail probing, prezeroing, trimming, and erasing. Higher CephFS paths can use the same file abstraction directly or through caching layers.

## Risks and Edge Cases

Probe correctness is sensitive to layout period math, reverse probing, sparse/nonexistent objects, and object sizes that must not exceed expected extent ends. The backward path asserts `start_from > *end` and can underflow if callers pass bad bounds. Mtime probing intentionally continues after finding size when earlier periods may contain a newer mtime.

`zero` converts full-object zeroes into removes. That is efficient but semantically depends on higher layers accepting missing objects as zero data and on `keep_first` when callers must preserve the head object.

`purge_range` assumes `oncommit` is non-null in completion paths; callers should not pass null for multi-object operations. `truncate` ignores per-object callback errors in `C_TruncRange`, completing success after all operations finish, so tests should verify whether this is intended behavior or legacy tolerance.

## Test Signals

Useful coverage includes stripe layouts with multiple stripes and periods; reads/writes spanning object boundaries; zeroing full and partial objects with `keep_first` both ways; forward and backward probe across sparse tails; mtime probe across multiple periods; purge throttling and `-ENOENT` tolerance; truncate ranges that start/end mid-period; and objecter error propagation for probe and purge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Filer.cc -->
