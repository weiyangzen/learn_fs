# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/srq.h

## Purpose
Declares the Chelsio SRQ table snapshot structures and firmware reply interface.

## Important APIs, Types, and Functions
Defines `SRQ_WAIT_TO` as a five-second timeout, `struct srq_entry` with valid/index/PDID/queue length/current MSN/max MSN/qbase fields, and `struct srq_data` with table size, destination entry pointer, completion, and mutex. Declares `t4_init_srq` and `do_srq_table_rpl`.

## Control Flow
No runtime control flow is present. The header encodes the synchronization model used by implementation and callers: serialize access with `srq_data.lock`, point `entryp` at caller storage, wait on `comp`, and check `entry.valid`.

## State and Persistence Behavior
The header's state is an in-memory snapshot of firmware SRQ table contents. It is not durable and does not own hardware resources; it mirrors values returned in `CPL_SRQ_TABLE_RPL`.

## Dependencies and Integration Points
Forward-declares `struct adapter` and `struct cpl_srq_table_rpl`. Included by `srq.c` and main adapter code that initializes/frees `adapter->srq` and dispatches replies.

## Risks
The structure fields are narrower than some extracted macro widths could imply, especially `idx`, `qlen`, and `pdid`; this should match expected firmware ranges. The single `entryp` pointer means callers must prevent overlapping reads.

## Test Signals
Build coverage with SRQ-enabled firmware paths, SRQ table read timeout handling, successful reply parsing, and lockdep coverage around the mutex/completion contract are the primary signals.
