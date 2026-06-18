# sources/distributed-fs/ceph-client/include/linux/journal-head.h

## Purpose
Defines `struct journal_head`, the JBD/JBD2 metadata wrapper attached to a `buffer_head`. It stores journaling list membership, transaction ownership, checkpoint links, frozen data, committed data, and trigger callbacks for journaled buffers.

## Important APIs, Types, And Functions
The header declares `tid_t`, forward-declares `transaction_t`, and defines `struct journal_head`. Key fields include `b_bh`, `b_state_lock`, `b_jcount`, `b_jlist`, `b_modified`, `b_frozen_data`, `b_committed_data`, `b_transaction`, `b_next_transaction`, transaction list links, checkpoint transaction/list links, `b_triggers`, and `b_frozen_triggers`.

## Control Flow
JBD2 attaches a journal head to a buffer, files it onto transaction lists while protected by journal and buffer locks, freezes data before log IO when necessary, and later moves buffers through commit and checkpoint lists. Trigger pointers allow filesystem-specific work when frozen data is stable or aborted.

## State And Persistence
All state is in-memory metadata associated with a buffer head. `b_frozen_data` and `b_committed_data` are snapshots used during commit and allocation safety, not durable journal records themselves. Transaction pointers describe current ownership until commit/checkpoint cleanup releases them.

## Dependencies And Integration Points
Depends on `linux/spinlock.h` and `struct buffer_head`. It is included by `jbd2.h` and consumed by the journaling implementation and filesystem metadata paths.

## Risks
The comments document lock ownership per field; violating those rules risks list corruption, stale transaction ownership, or frozen data races. The separate `b_jlist` and `b_modified` fields deliberately avoid bitfield races that could clobber `b_jcount`.

## Test Signals
Useful signals are journal stress tests with concurrent metadata updates, checkpoint cleanup, data journaling with frozen copies, trigger invocation tests, lockdep, and buffer_head lifetime/refcount assertions.
