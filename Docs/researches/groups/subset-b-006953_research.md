# Research: subset-b-006953

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Filer.h -->
# sources/distributed-fs/ceph/src/osdc/Filer.h

## Purpose

`Filer.h` declares Ceph's file-to-object helper for clients that want logical inode byte-range I/O without hand-building object extents. The class wraps an `Objecter` and a `Finisher`, exposes asynchronous file operations, and hides the internal probe state used to discover logical file end and modification time across striped RADOS objects.

## Important APIs and Types

`class Filer` owns pointers to `CephContext`, `Objecter`, and `Finisher`. It is constructed from an existing `Objecter` and `Finisher`, and `is_active()` delegates liveness to the objecter.

The public async I/O API includes `read`, `read_trunc`, `write`, `write_trunc`, `zero`, `truncate`, and `purge_range`. Each takes an inode number and `file_layout_t`; read-like calls take a `snapid_t`, write-like calls take `SnapContext`, modification time, flags, and a completion `Context`. `read_trunc` and `write_trunc` include truncate size/sequence so callers can maintain ordered truncate semantics.

`probe` is overloaded for modern `ceph::real_time` and legacy `utime_t` mtime outputs. It searches forward or backward from `start_from` and writes the discovered logical end into the caller-provided `uint64_t *end`. The optional mtime output asks the implementation to continue scanning enough objects to report the maximum mtime observed in the searched region.

The private `Probe` struct is the main declared state. It has its own `std::mutex`, stores the immutable request fields, result pointers, current probing offset and length, extents being probed, per-object known sizes, max mtime, outstanding operations, accumulated error, and `found_size` flag. `C_Probe`, `_probe`, `_probed`, and `probe_impl` form the hidden asynchronous probe implementation.

`_do_purge_range` and `_do_truncate_range` are declared because their state structs are file-local implementation structs in `Filer.cc` while callbacks need to call back into `Filer`.

## Control Flow and Contracts

All public operations are asynchronous and complete a `Context`. The header's method signatures make the split clear: the caller supplies buffers and completion contexts, while the filer only maps logical ranges and delegates object execution. Callers retain responsibility for choosing snapshots, layout, flags, and truncate sequence values.

The probe contract is direction-sensitive. In forward mode it searches for the first short object relative to expected object extent size. In backward mode it searches earlier periods until it finds non-empty data or reaches the lower bound supplied through `end`. When an mtime pointer is provided, probe also reports the maximum object mtime observed while searching.

## State and Persistence Behavior

`Filer` itself does not own persistent metadata, caches, or journals. It relies on `file_layout_t` to derive object names and locators and on `Objecter` to submit durable RADOS mutations. The `Probe` state is heap allocated per request and freed after completion. Purge and truncate range state are declared as opaque implementation structs and similarly exist only for in-flight operations.

The persistent data affected by this API are file data objects, full-object removals, zeroed object ranges, object truncate metadata, and object mtimes. Snapshot persistence is entirely driven by `SnapContext` and read `snapid_t` values supplied by callers.

## Dependencies and Integration Points

The header depends on Ceph filesystem and OSD types: `file_layout_t`, `inodeno_t`, `ObjectExtent`, `SnapContext`, `object_t`, `snapid_t`, `ceph::buffer::list`, and Ceph time types. It forward-declares `Context`, `Messenger`, `Objecter`, and `Finisher` to keep compile dependencies lower.

`Journaler.h` includes `Filer.h` and embeds a `Filer` instance for journal storage. CephFS client/MDS-side code can use this API as the low-level object mapping layer, while `ObjectCacher` provides a separate cache/writeback path with similar file convenience wrappers.

## Risks and Edge Cases

The header exposes raw pointer completion and output parameters; callers must keep buffers and result pointers alive until completion. Copy constructor and assignment operator are declared private-ish without definitions in this header's public area, signaling copying should not be used even though the declarations are visible near public construction.

`probe` requires valid snapshots and sane `start_from`/`end` bounds. Multi-object purge/truncate completion assumes callback contexts are valid. Layout correctness is critical because every API trusts the supplied `file_layout_t`.

## Test Signals

Header-level users should be tested for callback lifetime, null/non-null completion behavior expected by each operation, real-time and `utime_t` probe overloads, truncating I/O propagation, and correct integration with layouts whose period is larger than one object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Filer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Journaler.cc -->
# sources/distributed-fs/ceph/src/osdc/Journaler.cc

## Purpose

`Journaler.cc` implements a striped append-only journal stored through `Filer` and `Objecter`. It maintains durable journal head metadata, appends envelope-framed entries to the byte stream, flushes writes safely to RADOS, recovers the tail by probing object sizes, prezeroes/removes future objects to make tail probing reliable, reads entries with prefetch, trims expired objects, and erases a journal in two phases.

This implementation is used by higher Ceph components that need a serial durable log over the object store, historically including CephFS metadata logging.

## Important APIs and Functions

Construction wires the journal name, inode, pool, magic string, `Objecter`, `PerfCounters`, `Finisher`, embedded `Filer`, and initial pointer state. `set_readonly`/`set_writeable` guard mutating operations, while `create` initializes a blank active journal using the supplied layout and stream format.

Header handling is implemented by `_read_head`, `_finish_read_head`, `reread_head`, `_finish_reread_head`, `write_head`, `_write_head`, and `_finish_write_head`. The head is object zero (`file_object_t(ino, 0)`) and stores `trimmed_pos`, `expire_pos`, `unused_field`, `write_pos`, layout, magic, and stream format. `_finish_read_head` validates magic and pointer order, initializes layout/format, then probes from the header's `write_pos` to recover the true log end.

Recovery and probing use `_probe`, `_finish_probe_end`, `_reprobe`, and `_finish_reprobe`. These call `Filer::probe` forward from `write_pos`, then update `prezeroing_pos`, `prezero_pos`, `write_pos`, `flush_pos`, `safe_pos`, and `next_safe_pos` to the discovered end.

Appending and flushing are handled by `append_entry`, `_do_flush`, `_finish_flush`, `flush`, `wait_for_flush`, and `_write_head_needed`. `append_entry` frames the caller's buffer through `JournalStream::write`, advances `write_pos`, and flushes completed layout periods. `_do_flush` writes only bytes safely behind the prezero frontier, records `pending_safe`, splices flushed bytes out of `write_buf`, calls `filer.write`, advances `flush_pos`, releases throttle bytes, and may issue more prezero work.

Prezeroing uses `_issue_prezero`, `_finish_prezero`, and `wait_for_prezero`. It zeroes or removes full layout periods ahead of the writer based on `journaler_prezero_periods`, tracks out-of-order completions in `pending_zero`, and resumes deferred flushes once `prezero_pos` advances far enough.

Reading uses `_issue_read`, `_prefetch`, `_finish_read`, `_assimilate_prefetch`, `_have_next_entry`, `is_readable`, `wait_for_readable`, and `try_read_entry`. Reads are issued one layout period at a time so contiguous returned data can be assimilated before all objects finish. `JournalStream::readable` validates envelopes and computes bytes needed; `try_read_entry` consumes exactly one framed entry and advances `read_pos`.

Trimming and erasing use `_trim`, `_finish_trim`, `trim`, `erase`, and `_finish_erase`. Trimming only deletes whole periods up to the last committed `expire_pos` floor. Erase first deletes journal data objects from `trimmed_pos` through the current write region and deletes the head only after data purge succeeds.

`JournalStream::readable`, `read`, and `write` implement the actual entry envelope. Legacy format uses a leading `uint32_t` size. Resilient format adds a sentinel prefix and trailing start pointer so readers can detect damaged entry boundaries.

## Control Flow

Recovery starts in `STATE_UNDEF`. `recover` queues callbacks, moves to `STATE_READHEAD`, reads the head, decodes it, initializes pointers from the header, and moves to `STATE_PROBING`. Probe completion makes the journal `STATE_ACTIVE` and releases `waitfor_recover`. Repeated recover calls while recovery is already running only enqueue callbacks.

The write path is intentionally decoupled: `append_entry` only appends to memory and may trigger partial flushes; `_do_flush` starts RADOS writes; `_finish_flush` advances `safe_pos` when commits return; waiters in `waitfor_safe` complete once their requested journal boundary is safe. `flush` forces `_do_flush`, waits for safe, and opportunistically writes a fresh head if the configured head interval elapsed.

The read path lazily prefetches. `is_readable` returns the cached readability flag and calls `_prefetch`. If the reader reaches `safe_pos` while the writer has unflushed bytes, `_issue_read` waits on a safe-position callback and may trigger a flush. `try_read_entry` reads only when `_have_next_entry` has already confirmed a full entry envelope is available.

Write errors from flush, head writes, trim, or prezero call `handle_write_error`. That function invokes a one-shot configured handler, drops later errors after the handler has fired, or aborts if no handler is registered.

## State and Persistence Behavior

The persistent journal head is the serialized `Journaler::Header` in object zero. It is updated lazily and records lower bounds for trim/expire/write positions plus layout and stream format. Journal entries live after `layout.get_period()`; `create` initializes all positions to the layout period so data never overlaps the head object.

In-memory write state includes `prezeroing_pos`, `prezero_pos`, `write_pos`, `flush_pos`, `safe_pos`, `next_safe_pos`, `write_buf`, `write_buf_throttle`, `pending_safe`, `waitfor_safe`, `pending_zero`, and prezero waiters. Read state includes `read_pos`, `requested_pos`, `received_pos`, `read_buf`, `prefetch_buf`, `fetch_len`, `temp_fetch_len`, readability, and a single `on_readable` waiter.

Durable mutations are issued through `Filer`: data writes for flushed entries, zero/remove operations for prezeroing, purge operations for trim/erase, and objecter `read_full`/`write_full` for the head. The code preserves pointer invariants before writing the head: `write_pos >= expire_pos >= trimmed_pos`.

## Dependencies and Integration Points

`Journaler.cc` depends on `Journaler.h`, `Filer`, `Objecter`, Ceph `Context`/`C_OnFinisher`, `Finisher`, `Throttle`, `PerfCounters`, `bufferlist` encoding, and config keys `journaler_prefetch_periods`, `journaler_write_head_interval`, and `journaler_prezero_periods`. Its callbacks are all wrapped onto the finisher to avoid completing caller contexts directly from objecter paths.

Higher layers integrate by creating/recovering a journal, appending serialized log events, waiting for flush/safe, reading entries, advancing expire/trim positions, and registering a write error handler for blocklist or storage failures.

## Risks and Edge Cases

Tail recovery depends on future objects being absent or zeroed; bugs in prezeroing can make `Filer::probe` overestimate the journal tail. Partial entry detection in `_have_next_entry` resets write/flush/safe positions to `read_pos` when the reader reaches `write_pos` without a full envelope, but the code leaves an explicit FIXME for truncating disk state.

`write_buf_throttle` waits outside the journal lock and then reacquires it, so concurrent state changes must still preserve append ordering. `wait_for_readable` supports only one waiter (`ceph_assert(on_readable == 0)`). `handle_write_error` aborts if no handler is set, making error-handler registration a critical integration contract for production users.

Malformed resilient envelopes throw buffer errors from `JournalStream::readable` or `read`; callers see `-EINVAL` and readability stops. Mixed legacy/resilient compatibility depends on header stream format decode.

## Test Signals

Tests should cover create/recover/reread flows; corrupt head magic and invalid pointer order; legacy and resilient envelope read/write including bad sentinel; append across layout-period boundaries; safe-position waiters with out-of-order flush completions; prezero out-of-order completions; reading while writing at `safe_pos`; partial tail recovery; trim floor to period boundaries; erase data-before-head ordering; shutdown draining waiters; and one-shot write error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Journaler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Journaler.h -->
# sources/distributed-fs/ceph/src/osdc/Journaler.h

## Purpose

`Journaler.h` declares the public and internal shape of Ceph's striped object-backed journal. It documents the core pointer invariants, defines the durable header format, defines journal entry stream formats, and exposes asynchronous recovery, append, flush, read, trim, erase, and shutdown operations.

## Important APIs and Types

`stream_format_t` and `enum StreamFormat` define `JOURNAL_FORMAT_LEGACY` and `JOURNAL_FORMAT_RESILIENT`. Envelope constants describe legacy size-only framing and resilient sentinel/size/start-pointer framing. `JournalStream` encapsulates entry framing with `readable`, `read`, `write`, `get_envelope_size`, and a fixed sentinel value.

`Journaler::Header` is the serialized head stored at the start of the journal file. It includes `trimmed_pos`, `expire_pos`, `unused_field`, `write_pos`, `magic`, `file_layout_t layout`, and `stream_format`. Its versioned encode/decode supports older headers by defaulting missing stream format to legacy. It also provides dump/print helpers and generated test instances.

`Journaler` owns persistent-position mirrors (`last_committed`, `last_written`), identity (`name`, `ino`, `pg_pool`, `magic`), execution support (`Objecter`, embedded `Filer`, `Finisher`, `PerfCounters`), state enum values, write pointers, read pointers, trim pointers, buffers, wait queues, throttle, prezero tracking, and callback class declarations.

The public async API includes `erase`, `create`, `recover`, `reread_head`, `reread_head_and_probe`, `write_head`, `wait_for_flush`, `flush`, `wait_for_readable`, `wait_for_prezero`, `trim`, and `shutdown`. Synchronous setters/getters include `set_layout`, `set_readonly`, `set_writeable`, `set_write_pos`, `set_read_pos`, `append_entry`, `set_expire_pos`, `set_trimmed_pos`, `set_write_error_handler`, `set_write_iohint`, and position/state getters.

## Control Flow and State Machine

The state constants are `STATE_UNDEF`, `STATE_READHEAD`, `STATE_PROBING`, `STATE_ACTIVE`, `STATE_REREADHEAD`, `STATE_REPROBING`, and `STATE_STOPPING`. Recovery moves through read-head and probe states before becoming active. Reread and reprobe are active-state refresh operations. Shutdown moves to stopping and forces waiters out.

The header comments define the journal's core order: `trimmed_pos <= expire_pos <= unused_field <= write_pos`; the implementation effectively treats `unused_field` as a committed expire/read field. The durable head may lag in-memory pointers, but `head.expire_pos >= trimmed_pos` is required so recovery can find a safe beginning before trimmed objects disappear.

Write-side flow is append to `write_buf`, flush to object data, advance `safe_pos` on commit, write the head lazily, then trim only after the head's expire position is committed. Read-side flow starts at `read_pos`, prefetches up to safe/write bounds, marks readable when a complete entry is available, then `try_read_entry` consumes one entry.

## State and Persistence Behavior

Persistent journal metadata is `Header`; persistent journal data is the byte stream laid out through `file_layout_t`. In-memory state tracks multiple positions because `write_pos`, `flush_pos`, and `safe_pos` can differ. `prezeroing_pos` and `prezero_pos` protect probe-based recovery by ensuring objects ahead of the tail are empty. `pending_safe` maps flush-start offsets to entry boundaries safe after completion; `waitfor_safe` maps requested safe positions to callbacks.

The read state separates requested, received, and consumed positions to support out-of-order object read completions. `prefetch_buf` holds non-contiguous returned chunks until `_assimilate_prefetch` can append them to `read_buf` in order.

`last_written` is the most recently submitted head; `last_committed` is the most recently committed head. Trimming is based on `last_committed.expire_pos`, not the volatile `expire_pos`, to avoid deleting objects before durable recovery metadata points past them.

## Dependencies and Integration Points

The header includes `Filer.h` and `Throttle`, and forward-declares `Objecter`, `Finisher`, `Context`, and `C_OnFinisher`. It uses Ceph buffer encoding macros and `WRITE_CLASS_ENCODER` for the header. Higher layers supply serialized entries, consume entries, control expire/trim positions, and handle write errors.

The file integrates with Ceph config through implementation paths for prefetch length, head-write interval, and prezero periods. It also integrates with perf counters for write latency and with objecter finisher wrapping for asynchronous callback dispatch.

## Risks and Edge Cases

The pointer model is subtle. Any caller that sets positions directly must preserve invariants and avoid doing so during in-flight reads unless the header explicitly permits it (`set_read_pos` asserts no in-progress read). `readonly` controls mutating operations by assertion rather than runtime error returns.

Only one readable waiter is supported. Write error handling is one-shot and must be reset if callers keep using the journal after recovery logic. Legacy headers without `stream_format` are accepted; malformed resilient entries are intentionally rejected.

## Test Signals

Header-focused tests should verify `Header` encode/decode compatibility, generated test instances, stream format envelope sizes, state getter behavior, direct setter invariants, `write_head_needed` timing, single-reader waiter assumptions, and trim safety based on committed head state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/Journaler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/ObjectCacher.cc -->
# sources/distributed-fs/ceph/src/osdc/ObjectCacher.cc

## Purpose

`ObjectCacher.cc` implements Ceph's in-memory object buffer cache with asynchronous read filling, dirty writeback, flush/release/purge/discard operations, dirty throttling, LRU trimming, and perf counters. It sits between higher file/object clients and a `WritebackHandler`, using `ObjectExtent` mappings from callers to cache and write back object byte ranges.

The implementation is a state machine around `BufferHead` regions. Each object has a sorted map of non-overlapping buffer heads, and every buffer head is in one of missing, clean, zero, dirty, RX, TX, or error state.

## Important APIs and Functions

`Object::split`, `merge_left`, `can_merge_bh`, `try_merge_bh`, and `maybe_rebuild_buffer` maintain the per-object interval map and buffer memory layout. Splitting preserves state, error, snap context, write/read tids, journal tid, flags, data, and read waiters. Merging requires adjacency, same state, compatible journal tid, and matching write tid for TX buffers.

`Object::map_read` maps an `ObjectExtent` into existing or newly allocated buffer heads, returning maps of hits, missing buffers, in-flight RX buffers, and error buffers. If the object is marked complete, gaps become clean zero hits. `Object::map_write` maps a write extent into one contiguous buffer head, splitting surrounding buffers and replacing journal tids when overwrites supersede earlier journal writeback expectations.

`bh_read` marks a buffer RX, assigns `last_read_tid`, submits `WritebackHandler::read`, and tracks outstanding reads through `C_ReadFinish`. `bh_read_finish` handles successful data, short reads padded with zeroes, trusted or distrusted `-ENOENT`, stale read tids, error state, waiter wakeups, merge attempts, retry of blocked reads, and outstanding-read accounting.

`readx` and `_readx` are the public and internal read paths. `_readx` maps every requested extent, submits missing reads, installs retry contexts on missing/RX buffers, handles optional `return_enoent`, constructs result data from cached buffer heads through `stripe_map`, records hole ranges for zero data, updates perf counters, trims clean cache, and returns either bytes read, error, `-ENOENT`, or zero for async-in-progress.

`writex` maps each write extent into cache, copies caller buffer fragments into dirty buffer heads, wakes read waiters invalidated by overwrite, updates dirty/nocache/dontneed flags, merges where legal, records perf counters, then calls `_wait_for_write` for dirty throttling or write-through behavior.

Writeback is implemented by `bh_write`, `bh_write_scattered`, `bh_write_adjacencies`, and `bh_write_commit`. Dirty buffers become TX, commit callbacks mark matching tids clean or dirty again on error, clear journal tids, update object commit tid, complete waiters in `waitfor_commit`, and notify `flush_set_callback` when an object set becomes fully clean.

Flush and lifecycle APIs include `flush`, `trim`, `flush_set`, range `flush_set`, `flush_all`, `purge_set`, `release_set`, `release_all`, `clear_nonexistence`, `discard_set`, and `discard_writeback`. `flusher_entry` is the background loop that flushes over-target dirty bytes, over-target dirty buffer-head counts, and aged dirty buffers, then waits for outstanding reads before thread exit.

Statistics maintenance is centralized in `bh_stat_add`, `bh_stat_sub`, `bh_set_state`, `bh_add`, `bh_remove`, and `verify_stats`. State changes update global byte counters, per-object-set dirty/tx byte counts, LRU membership, dirty-or-tx set membership, and dirty-waiter condition variables.

## Control Flow

Reads start with extent mapping. If every byte is represented by clean, zero, dirty, or TX buffers, `_readx` assembles the return buffer immediately. Missing buffers are marked RX and submitted to the writeback handler; the caller's completion is represented by a `C_RetryRead` attached to the last missing/RX buffer so the entire read is retried after enough data arrives. Cache pressure from RX bytes can push whole reads into the global `waitfor_read` queue until earlier reads complete.

Writes update the cache first and return according to the dirty throttling policy. Normal cached writes dirty memory and may complete after a throttle wait; FUA or zero dirty-limit paths force `flush_set` and optionally block until writeback commits. Overwriting TX data increments the overwritten-in-flush perf counter and preserves correctness by comparing write tids in commit callbacks.

Writeback moves dirty buffers to TX and submits handler writes. Commit callbacks may arrive after buffers were overwritten, split, discarded, or removed; the code therefore checks object existence, buffer state, and `last_write_tid` before marking clean. Commit waiters are keyed by object write tid, not individual buffer pointer.

Flush/release/discard paths all operate under the cache lock. Range flush walks intersecting buffers and schedules dirty ones. Release drops only clean/zero/error buffers and reports unclean bytes left. Discard removes in-memory extents, but if a buffer is TX and the caller used `discard_writeback`, it waits for commit before final completion.

## State and Persistence Behavior

The cache's persistent effects are through `WritebackHandler` reads and writes. In-memory state includes `objects` indexed by pool id and `sobject_t`, object LRU, clean/rest and dirty LRUs, `dirty_or_tx_bh`, wait queues, stats counters, and a private finisher for async wait callbacks.

`ObjectSet` groups objects for a higher-level inode/pool and tracks truncate size/seq, dirty/tx bytes, and whether single-extent reads should return `-ENOENT`. `Object` tracks existence and completeness: `complete=false` means gaps are not known zero; `complete=true` with `exists=false` means trusted `-ENOENT` told the cache the object is all zero/missing.

`BufferHead` state is the core persistence-adjacent state. Dirty and TX buffers represent data not yet safely written or currently committing. Clean/zero/error buffers are cacheable read state. RX buffers represent in-flight reads and pin themselves through reference counting. Journal tid tracks external journal writeback coordination; replacing it calls `WritebackHandler::overwrite_extent`.

## Dependencies and Integration Points

The implementation depends on `WritebackHandler` for storage I/O, `ObjectExtent`/`Striper` for caller mappings, Ceph `Context` and `Finisher`, `LRUObject`/`LRU`, `xlist`, `SnapContext`, perf counters, `ZTracer`, config `osdc_blkin_trace_all`, and the caller-provided shared cache lock.

Higher layers use `prepare_read`, `prepare_write`, `readx`, `writex`, and file convenience wrappers in the header. The writeback handler abstracts whether writes can be scattered and whether copy-on-write hazards exist. `flush_set_callback` lets the owner release journal or capability resources when dirty data has fully committed.

## Risks and Edge Cases

Correctness depends on non-overlapping buffer maps and exact stat symmetry. Splits, merges, state transitions, and removals must keep `data`, LRUs, `dirty_or_tx_bh`, object refs, and byte counters consistent. `verify_stats` exists because drift here can break dirty throttling, trimming, and shutdown.

`-ENOENT` handling is deliberately conservative. A trusted missing-object result can mark an object complete and nonexistent, wake all waiters, and remove all-zero buffers; `clear_nonexistence` must distrust in-flight reads when later writes/copy-up can invalidate that assumption.

TX commit races are common: a newer write tid can supersede an older commit, discarded TX buffers can delay completion through gathers, and overwritten journal tids must notify the writeback handler. Tests should target stale tid callbacks and object removal during in-flight I/O.

The cache lock is held across much of the control flow, with careful use of condition variables and finishers. The flusher intentionally unlocks when it has flushed too many aged buffers under lock to avoid starving other threads.

## Test Signals

Strong tests include interval splitting/merging invariants; read hits, misses, RX retries, error retries, holes, short read zero padding, trusted and distrusted `-ENOENT`; write overwrites of missing/clean/dirty/TX buffers; dirty limit blocking and async freespace callbacks; scattered and non-scattered writeback; commit error redirtying; flush_set/flush_all gather completion; discard_writeback waiting on TX commits; release/purge behavior; flusher threshold and age behavior; shutdown waiting for outstanding reads; and `verify_stats` after randomized operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/ObjectCacher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/ObjectCacher.h -->
# sources/distributed-fs/ceph/src/osdc/ObjectCacher.h

## Purpose

`ObjectCacher.h` declares the cache and writeback interface for object byte ranges used by Ceph filesystem clients. It defines the buffer-head state model, object grouping, read/write request containers, public cache operations, file-layout convenience wrappers, and performance counter ids used by `ObjectCacher.cc`.

## Important APIs and Types

The perf counter enum declares cache hit/miss operation counters, hit/miss byte counters, data read/written/flushed counters, overwritten-during-flush bytes, and dirty-limit blocking counters.

`ObjectCacher::OSDRead` carries a vector of `ObjectExtent`s, a read snap id, output buffer pointer, and fadvise flags. `prepare_read` allocates it. `ObjectCacher::OSDWrite` carries extents, `SnapContext`, data buffer, mtime, fadvise flags, and optional journal tid. `prepare_write` allocates it.

`BufferHead` is the per-object interval cache entry. Its states are `STATE_MISSING`, `STATE_CLEAN`, `STATE_ZERO`, `STATE_DIRTY`, `STATE_RX`, `STATE_TX`, and `STATE_ERROR`. It stores extent start/length, flags (`dontneed`, `nocache`), owning `Object`, data `bufferlist`, read/write tids, write time, snap context, journal tid, read error, and waiters by offset. Its refcount pins LRU entries during RX/TX states.

`Object` represents one cached `sobject_t` and owns a sorted `map<loff_t, BufferHead*> data`. It tracks object number, object set, locator, truncate size/seq, `complete`, `exists`, last write/commit tids, dirty-or-tx bytes, commit waiters, and in-flight read callbacks. It exposes interval manipulation (`split`, `merge_left`, `map_read`, `map_write`, `truncate`, `discard`) and reference/LRU helpers.

`ObjectSet` groups cached objects for a higher-level inode and pool. It stores owner pointer, inode, truncate metadata, pool id, object list, aggregate dirty/tx bytes, and `return_enoent` policy.

`ObjectCacher` owns the writeback handler, shared lock, dirty/cache sizing limits, trace endpoint, object indexes, wait queues, LRUs, dirty-or-tx set, flusher thread, finisher, stats, and public operations. Important public APIs are `start`, `stop`, `readx`, `writex`, `is_cached`, `flush_set`, `flush_all`, `purge_set`, `release_set`, `release_all`, `discard_set`, `discard_writeback`, `clear_nonexistence`, and tuning setters.

The file convenience methods `file_is_cached`, `file_read`, `file_read_ex`, `file_write`, and `file_flush` call `Striper::file_to_extents` and then use the object-level cache operations.

## Control Flow and Contracts

Most methods require the caller-provided cache lock to be held; the implementation asserts this extensively. Public non-blocking read and write calls return immediately with a byte count/error or zero for async in progress. Completion contexts are used for deferred reads, dirty-limit freespace notifications, flush completion, and discard-writeback completion.

The header separates allocation of request containers from execution. Callers build `OSDRead`/`OSDWrite` through helpers, populate extents through either direct object mappings or file convenience wrappers, and transfer ownership to `readx`/`writex`.

`ObjectCacher::start` and `stop` control the background flusher thread. Destruction expects all cache objects and LRUs to be empty, so owners must flush/release/purge before destroying the cacher.

## State and Persistence Behavior

The header declares only in-memory cache state. Durable writes are delegated through `WritebackHandler`; durable read state is reflected as clean/zero/error buffer heads. Dirty and TX bytes are tracked globally and per object set, and flushing transitions them toward clean. Snap context and truncate sequence fields are preserved in write requests and cached objects so writeback can be ordered correctly relative to snapshots and truncates.

LRU state is split between dirty buffers, non-dirty buffers, and objects. RX/TX buffers pin themselves with the `BufferHead` refcount so they cannot be evicted while I/O is active. `Object::can_close` requires no buffers and no commit waiters.

## Dependencies and Integration Points

`ObjectCacher.h` depends on Ceph core types, `LRUObject`, `Context`, `object.h`, `xlist`, `Cond`, `Finisher`, `SnapContext`, `Thread`, `zipkin_trace`, and `Striper`. It forward-declares `WritebackHandler`, which is the main persistence integration.

The API integrates with higher file clients through `ObjectSet` and file-layout wrappers. `flush_set_callback_t` lets owners be notified when an object set has no more dirty/TX data, which is important for journal/capability accounting outside the cache.

## Risks and Edge Cases

Because this is a lock-coupled API, callers must respect locking and lifetime rules. Passing request objects or completion contexts with insufficient lifetime will fail asynchronously. `return_enoent` is only meaningful for single-extent reads, and the implementation asserts that constraint.

The state enum allows many transitions, but only some are valid in context. Dirty/TX counters, journal tid replacement, and LRU membership must remain synchronized. The destructor's assertions make leaked dirty, RX, TX, or object refs visible at shutdown.

File convenience wrappers depend on correct `ObjectSet::truncate_size` and layout metadata. Incorrect truncate metadata can cause the cache to map or flush ranges inconsistent with OSD truncate ordering.

## Test Signals

Header/API tests should cover state predicate behavior, refcount pin/unpin, object close eligibility, object-set aggregation, request ownership transfer, public lock assertions in debug builds, file wrapper extent mapping, dirty limit setters, flusher start/stop lifecycle, and `return_enoent` single-extent enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/ObjectCacher.h -->
