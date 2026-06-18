# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/smt.c

## Purpose
Implements Source MAC Table allocation, reference counting, firmware programming, and reply handling for Chelsio switch/filter source-MAC entries.

## Important APIs, Types, and Functions
Exports `t4_init_smt`, `cxgb4_smt_alloc_switching`, `cxgb4_smt_release`, and `do_smt_write_rpl`. Internal helpers are `find_or_alloc_smte`, `t4_smte_free`, `write_smt_entry`, and `t4_smt_alloc_switching`. The runtime data model is `struct smt_data` plus per-entry `struct smt_entry` from `smt.h`.

## Control Flow
`t4_init_smt` allocates a flex-array SMT table with `SMT_SIZE` entries, initializes the table rwlock, per-entry spinlocks, indexes, states, source MACs, and refcounts. Allocation takes the table write lock, scans for an existing switching entry with the same source MAC or the first free entry, locks the selected entry, initializes it if the refcount was zero, copies the MAC, records `pfvf`, writes the entry to firmware, or increments the refcount for reuse. Release decrements the refcount under the entry lock and returns the entry to `SMT_STATE_UNUSED` when it reaches zero.

`write_smt_entry` builds a CPL SMT write request and sends it through `t4_mgmt_tx`. T4/T5 hardware programs pairs of source MACs per row, so the request carries both the target entry and its neighbor. T6 uses a distinct request shape and one entry per row. `do_smt_write_rpl` handles firmware replies and marks an entry `SMT_STATE_ERROR` on unexpected status.

## State and Persistence Behavior
State is in memory under `adapter->smt` and in the adapter firmware/hardware SMT after successful management Tx. The driver keeps refcounts and entry states locally; firmware reply errors only mark local state as error and log. Table memory is freed by the adapter teardown path, not in this file.

## Dependencies and Integration Points
Depends on `cxgb4.h` for adapter/netdev conversion and management Tx, `smt.h` for table types, `t4_msg.h` CPL formats, `t4fw_api.h`, `t4_regs.h`, and `t4_values.h`. `cxgb4_filter.c` allocates/releases SMT entries for filters with source-MAC rewriting, `cxgb4_main.c` initializes/frees `adapter->smt` and dispatches `CPL_SMT_WRITE_RPL` to `do_smt_write_rpl`, and `t4_hw.c` has related VI MAC/SMT index handling.

## Risks
Risks include table exhaustion returning `NULL`, failed `alloc_skb` leaving caller with no programmed entry, no immediate propagation of `write_smt_entry` failure to allocation state, refcount imbalance from filter error paths, pair-row programming on T4/T5 accidentally using stale neighbor MACs, and races if callers use entry fields without holding locks.

## Test Signals
Exercise filters requiring source-MAC rewrite, duplicate filters sharing the same SMAC, add/delete reference balance, table exhaustion, T4/T5 paired row behavior, T6 single-entry writes, firmware SMT write errors, and teardown with active filters.
