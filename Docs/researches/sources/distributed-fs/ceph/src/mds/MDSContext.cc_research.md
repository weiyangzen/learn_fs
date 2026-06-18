# sources/distributed-fs/ceph/src/mds/MDSContext.cc

## Purpose

`MDSContext.cc` implements MDS-specific `Context` completion wrappers. These wrappers ensure asynchronous callbacks run under the MDS rank lock when required, reset heartbeats, track outstanding I/O callbacks for slow-op diagnostics, respawn on severe I/O errors, and update the MDLog safe position after log completions.

## Important Functions And Control Flow

`MDSContext::complete` assumes `mds_lock` is already held, resets the rank heartbeat, and delegates to `Context::complete`. `MDSInternalContextWrapper::finish` forwards completion to a wrapped `Context`.

`MDSIOContextBase` constructs with a creation timestamp and optionally inserts itself into a global intrusive list protected by a spinlock. Its destructor removes the list item. `check_ios_in_flight` scans this list for contexts older than a cutoff, returning a bounded slow count and oldest timestamp. `MDSIOContextBase::complete` acquires `mds_lock`, drops callbacks while the daemon is stopping, respawns on `-EBLOCKLISTED` or `-ETIMEDOUT`, and otherwise calls `MDSContext::complete`.

`MDSLogContextBase::complete` captures the write position, calls `pre_finish`, runs normal I/O completion, and then calls `MDLog::set_safe_pos`. `MDSIOContextWrapper::finish` and `C_IO_Wrapper::finish` forward to wrapped contexts. `C_IO_Wrapper::complete` first queues itself on the finisher for async completion, then runs as a normal `MDSIOContext` when invoked synchronously by the finisher.

## State And Persistence Behavior

The only persistent-facing state is `MDSLogContextBase::write_pos`: it advances `MDLog::safe_pos` after the completion body has run, establishing the journal position that is both durable and callback-safe. The global I/O context list is transient diagnostic state.

## Dependencies And Integration Points

This file depends on `MDSRank`, `MDLog`, Ceph debug logging, and the `Context`/finisher model. `MDLog`, `MDCache`, objecter/filer callbacks, and gather builders use these contexts to cross from asynchronous storage/network completion back into MDS locked state.

## Risks And Test Signals

Risks include lock-order deadlocks, deleting wrapped contexts twice, failing to remove tracked I/O contexts, and advancing journal safe position before completion side effects are visible. Tests should cover slow I/O detection, stopping-daemon callback drops, blocklist/timeout respawn behavior, async `C_IO_Wrapper` queueing, and log safe-position monotonicity.
