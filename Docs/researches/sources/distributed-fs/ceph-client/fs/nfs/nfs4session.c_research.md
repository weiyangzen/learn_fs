# sources/distributed-fs/ceph-client/fs/nfs/nfs4session.c

## Purpose
`nfs4session.c` implements NFSv4.1 session allocation, slot table management, slot sequencing, dynamic slot limit adjustment, and session initialization/destruction. It provides the runtime machinery used by SEQUENCE operations to serialize requests through session slots and by callback handling to wait for in-flight sequence IDs.

## Important APIs and Functions
- Slot lifecycle: `nfs4_setup_slot_table()`, `nfs4_shutdown_slot_table()`, `nfs4_alloc_slot()`, `nfs4_lookup_slot()`, `nfs4_free_slot()`, `nfs4_try_to_lock_slot()`.
- Draining/wakeups: `nfs4_slot_tbl_drain_complete()`, `nfs41_wake_and_assign_slot()`, `nfs41_wake_slot_table()`, `nfs4_slot_wait_on_seqid()`.
- Dynamic sizing: `nfs41_set_target_slotid()`, `nfs41_update_target_slotid()`.
- Session lifecycle: `nfs4_alloc_session()`, `nfs4_setup_session_slot_tables()`, `nfs4_destroy_session()`, `nfs4_init_session()`, `nfs4_init_ds_session()`.

## Control Flow
Slot tables are linked lists of `struct nfs4_slot` plus a bitmap of used slot IDs. `nfs4_realloc_slot_table()` grows the list as needed, resets sequence numbers, and constrains `max_slotid` to the negotiated table size. Request dispatch code allocates a free slot under `slot_tbl_lock`; waiters sleep on an RPC priority wait queue and are woken by `nfs41_wake_slot_table()` when slots become available.

`nfs41_assign_slot()` attaches a reserved slot to the RPC task's `nfs4_sequence_args` and `nfs4_sequence_res`. During drain, non-privileged tasks are not assigned slots. `nfs4_free_slot()` clears the used bitmap and recomputes `highest_used_slotid`; when the last slot drains it completes the table's drain completion so session reset and recovery can proceed.

The slot-target update path consumes server SEQUENCE results. `nfs41_update_target_slotid()` clamps server values to `NFS4_MAX_SLOTID`, filters sharp target changes as outliers using first and second derivative checks, updates server and target slot bounds, and wakes waiters if capacity increases.

Session setup initializes forechannel slots and, for `SESSION4_BACK_CHAN`, backchannel slots. Destruction sends `DESTROY_SESSION`, tears down the transport backchannel, destroys both wait queues, frees slots, and releases the session. Data-server session initialization mirrors the metadata server lease time and verifies the client is actually a DS client.

## State and Persistence
All state is in memory under `struct nfs4_session` and `struct nfs4_slot_table`: session ID, flags, channel attributes, slot sequence counters, capacity fields, generation counters, drain state, wait queues, and completions. There is no durable persistence; the server-visible state is reconstructed by EXCHANGE_ID/CREATE_SESSION after reset.

## Dependencies and Integration Points
This code depends on SUNRPC task scheduling and wait queues, transport backchannel support, NFSv4 protocol types, callback handling, and client state recovery in `nfs4state.c`. State recovery drains these tables before lease reclaim, session destroy/create, migration, and bind-connection operations. Tracepoints in `nfs4trace.h` observe setup and completion of SEQUENCE operations.

## Risks
The main risks are slot leaks, incorrect highest-used-slot tracking, assigning slots while draining, dynamic-slot outlier filtering suppressing legitimate server changes, and sequence ID waits timing out on callback paths. Error handling is memory-allocation sensitive because slot lookup can allocate with `GFP_NOWAIT` or `GFP_NOFS` depending on path.

## Test Signals
Exercise concurrent slot allocation/free, max-slot shrink and grow, callback waits via `nfs4_slot_wait_on_seqid()`, drain completion during session reset, and server-provided highest/target slot changes. Tracepoints `nfs4_setup_sequence` and `nfs4_sequence_done` should show slot IDs, sequence IDs, and target slot evolution. Fault injection around allocation and session destroy/create is important.
