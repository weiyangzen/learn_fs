# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/srq.c

## Purpose
Implements minimal Shared Receive Queue table support for Chelsio T6-class resources: allocation of driver SRQ bookkeeping and parsing of firmware SRQ table read replies.

## Important APIs, Types, and Functions
Exports `t4_init_srq` and `do_srq_table_rpl`. The relevant types are `struct srq_data` and `struct srq_entry` from `srq.h`; reply field extraction uses `struct cpl_srq_table_rpl` and `SRQT_*` macros from `t4_msg.h`.

## Control Flow
`t4_init_srq` allocates `struct srq_data`, records the firmware-reported table size, initializes the completion used by synchronous readers, and initializes the mutex. `do_srq_table_rpl` derives the table index from the reply TID, validates that the status is `CPL_CONTAINS_READ_RPL`, and on success copies decoded valid/index/PDID/queue-length/qbase/current-MSN/max-MSN values into `s->entryp`; it always completes the waiting operation before returning.

## State and Persistence Behavior
The persistent driver object is `adapter->srq`, with `srq_size`, a caller-provided `entryp` destination pointer, one completion, and one mutex. This file does not allocate the destination `srq_entry`; a reader must set `entryp` before issuing the firmware read. Hardware SRQ state remains in firmware; this module snapshots one reply into memory.

## Dependencies and Integration Points
Depends on `cxgb4.h`, `t4_msg.h`, and `srq.h`. `cxgb4_main.c` discovers SRQ resource ranges using firmware parameters, initializes `adapter->srq`, dispatches `CPL_SRQ_TABLE_RPL` to this file, and frees the SRQ data during adapter teardown. Upper-layer RDMA/offload diagnostics can use the completion and parsed entry to inspect SRQ table state.

## Risks
Risks include `adapter->srq` or `s->entryp` being unset when a reply arrives, only one outstanding SRQ table read being representable due to the single completion and entry pointer, truncation from narrow fields in `struct srq_entry`, and callers timing out if firmware replies are lost or dispatched incorrectly. Error replies complete without marking a valid entry, so readers must check `valid`.

## Test Signals
Signals include firmware parameter discovery of SRQ_START/SRQ_END, successful SRQ table read with completion before `SRQ_WAIT_TO`, invalid-status reply logging, concurrent-reader exclusion by the mutex, and teardown with no pending completion users.
