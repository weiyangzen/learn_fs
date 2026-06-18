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
