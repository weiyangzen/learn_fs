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
