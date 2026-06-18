# File Research: sources/cow-pools/openzfs/module/zfs/dmu_tx.c

Implements DMU transaction creation, hold declaration, space/memory reservation, txg assignment, throttling, callbacks, commit, and abort.

Key points:
- `dmu_tx_create_dd()`, `dmu_tx_create()`, and `dmu_tx_create_assigned()` initialize transactions, hold lists, callback lists, pool references, and start timestamps.
- Holds describe intended modifications before txg assignment: writes, appends, frees, clones, ZAP updates, bonus buffers, generic space, spill blocks, and SA attribute updates.
- `dmu_tx_hold_dnode_impl()` and `dmu_tx_hold_object_impl()` attach dnode references and create `dmu_tx_hold_t` records with refcounted space and memory estimates.
- `dmu_tx_check_ioerr()` proactively reads existing blocks needed by a future modification, surfacing I/O errors before DMU state is dirtied.
- Write/append/free accounting reads partial edge blocks and needed indirects, respecting block alignment and avoiding full-free level-0 dbuf instantiation assumptions.
- Clone accounting reserves BRT-entry memory and relevant indirect-block write space.
- ZAP accounting uses worst-case microzap/fatzap space and performs lookup-based leaf error checks where a name is known.
- SA helpers reserve layout registry ZAP updates, bonus space, and spill space depending on attribute registration, growth, and spill state.
- Debug-only `dmu_tx_dirty_buf()` verifies that dirty buffers match declared holds.

Assignment and throttling:
- `dmu_tx_try_assign()` rejects transactions with prior I/O errors, suspended pools, dirty-data pressure, or write-log pressure before taking an open txg.
- Uses `txg_hold_open()` and dnode `dn_assigned_txg` / `dn_tx_holds` to prevent conflicting assignment across adjacent txgs.
- Computes worst-case allocation size with `spa_get_worst_case_asize()` and reserves memory/asize through `dsl_dir_tempreserve_space()`.
- `dmu_tx_delay()` imposes a nonlinear delay based on dirty-data and TX_WRITE log pressure, capped by `zfs_delay_max_ns`.
- `dmu_tx_assign()` implements blocking/nonblocking retry semantics for `DMU_TX_WAIT`, `DMU_TX_NOTHROTTLE`, and `DMU_TX_SUSPEND`.
- `dmu_tx_wait()` waits for dirty space, pool resume, specific dnode assignment release, or next synced txg.

Lifecycle:
- `dmu_tx_commit()` releases dnode tx holds, clears temporary reservations, registers txg callbacks, releases txg sync holds, and destroys the transaction.
- `dmu_tx_abort()` is for unassigned transactions, clears any temporary reservation, runs callbacks with `ECANCELED`, and destroys the transaction.
- `dmu_tx_callback_register()` and `dmu_tx_do_callbacks()` provide end-of-txg callback support.
- `dmu_tx_init()` / `dmu_tx_fini()` install/remove `dmu_tx` kstats.

Dependencies and interactions:
- Coordinates with dbuf/dnode locking, txg machinery, DSL directory quotas/reservations, dirty-data throttling, ZAP/SA code, and spa suspension/failmode policy.
- Exports the public kernel DMU transaction API when built in-kernel.

Research relevance:
- This is the write-side admission-control layer for DMU mutations. It encodes the contract that callers must declare what they may dirty before assignment, enabling safe txg grouping, quota checks, error preflight, and backpressure.
