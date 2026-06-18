# sources/object-store/daos/src/pool/srv_pool.c lines 9039-9714

## Scope And Purpose

This chunk covers the tail of the pool service implementation in `srv_pool.c`, from the transactional body of `pool_attr_del_handler()` through the final `ds_pool_prop_recov_cont_reset()` helper. The code is server-side DAOS pool metadata service logic. It handles pool user attribute RPCs, pool service replica membership updates, pool map refresh and persistence helpers, server pool handle checks, target-status queries, container-service credential lookups, external pool-service maintenance entry points, and VOS/RDB upgrade plumbing.

The range is not a standalone subsystem; it is a set of exported and static helpers at the edge of the pool service. Most functions convert between public `struct ds_pool_svc *` or RPC handlers and internal `struct pool_svc *`, then operate under replicated database (`rdb`) transactions protected by Argobots read/write locks.

## Important APIs, Types, And Functions

- `pool_attr_del_handler()` and `ds_pool_attr_del_handler()` implement the pool attribute delete RPC. The handler looks up the current pool service leader, starts an RDB transaction, takes `svc->ps_lock` for writing, detects duplicate write RPCs via `pool_op_lookup()`, deletes attributes through `ds_rsvc_del_attr()`, records the operation result with `pool_op_save()`, commits, and replies with `po_rc` plus an updated service hint.
- `pool_attr_get_handler()` / `ds_pool_attr_get_handler()` and `pool_attr_list_handler()` / `ds_pool_attr_list_handler()` implement read-only attribute fetch/list RPCs. They still open RDB transactions and take `svc->ps_lock` for reading, but do not use duplicate-operation replay because `pool_op_lookup()` only tracks writes.
- `ds_pool_replicas_update_handler()` handles `POOL_REPLICAS_ADD` and `POOL_REPLICAS_REMOVE` RPC opcodes by duplicating the rank list, creating an RDB-service id from the pool UUID, and calling `ds_rsvc_add_replicas()` or `ds_rsvc_remove_replicas()`. The add path is intentionally guarded by `D_ASSERTF(false)` because required arguments are not yet correct.
- `ds_pool_child_map_refresh_sync()` and `ds_pool_child_map_refresh_async()` schedule `ds_pool_map_refresh_ult()` on `DSS_XS_SYS` to refresh the current xstream's cached pool map. The sync variant uses an `ABT_eventual`; the async variant allocates an argument object and lets the ULT own completion behavior.
- `ds_pool_prop_fetch()` reads selected pool properties from the service RDB through `pool_prop_read()`.
- `ds_pool_hdl_is_from_srv()` checks whether a pool handle UUID is the server pool handle. It prefers the cached `pool->sp_srv_pool_hdl`; otherwise it fetches the server handle through pool IV with `ds_pool_iv_srv_hdl_fetch()`.
- `is_pool_from_srv()` wraps pool lookup plus `ds_pool_hdl_is_from_srv()` and reports a boolean, logging lookup or IV-fetch failures.
- `ds_pool_target_status()` and `ds_pool_target_status_check()` query the cached `pool->sp_map` for a target id and return its `co_status`, or compare it with a requested status.
- `ds_pool_lookup_hdl_cred()` is a deliberate cross-service helper for container service code. It looks up a pool handle record in `svc->ps_handles` without taking `svc->ps_lock`, validates the pool global version supports stored handle credentials, copies `ph_cred` into caller-owned memory, and returns it in a `d_iov_t`.
- `ds_pool_mark_connectable()` calls `ds_pool_mark_connectable_internal()` inside a write transaction and commits only when the internal helper returns a positive "changed" status.
- `ds_pool_svc_load_map()` and `ds_pool_svc_flush_map()` are map persistence helpers. `load_map` reads the map from RDB. `flush_map` extracts a `pool_buf`, writes it to RDB, commits, refreshes the local `svc->ps_pool` cache, and triggers replicated-service map distribution.
- `ds_pool_svc_update_label()` writes `DAOS_PROP_PO_LABEL` to pool properties, using `DAOS_PROP_ENTRY_NOT_SET` when `label == NULL`.
- `ds_pool_svc_evict_all()` finds all handles to evict and disconnects them with `pool_disconnect_hdls()`, then increments `metrics->evict_total` and commits the metadata update if any handles were evicted.
- `ds_pool_svc2pool()` and `ds_pool_ps2cs()` expose the backing `struct ds_pool *` and associated container service pointer from an opaque `struct ds_pool_svc *`.
- `ds_pool_svc_upgrade_vos_pool()` maps a pool global version to a VOS data-format version, looks up a local pool service replica, and calls `rdb_upgrade_vos_pool()` on the service RDB if applicable.
- `ds_pool_prop_recov_cont_reset()` calls `pool_prop_recov_cont_check_and_update(tx, svc, false, true)` and normalizes positive "changed" returns to success. Container create/destroy paths use it to force in-flight pool recovery-container work to retry.

The primary types are `struct pool_svc`, `struct ds_pool_svc`, `struct ds_rsvc`, `struct rdb_tx`, `struct pool_map`, `struct pool_buf`, `struct pool_hdl`, `struct pool_target`, `struct pool_map_refresh_ult_arg`, `daos_prop_t`, `d_iov_t`, `crt_rpc_t`, `crt_bulk_t`, and `d_rank_list_t`.

## Control Flow

Pool attribute delete follows the write-RPC pattern used earlier in the file. The handler extracts input and output structures from the CRT RPC, looks up the pool service leader with `pool_svc_lookup_leader()`, parses the bulk handle and count, opens an RDB transaction against `svc->ps_rsvc.s_db` and current term, and enters the service write lock. Duplicate detection is done before mutation; if the request is a duplicate or the `DAOS_MD_OP_FAIL_NOREPLY` fault is active, the handler skips the delete body and proceeds to operation-result saving. After `pool_op_save()`, the transaction commits and the handler reports the stored `op_val.ov_rc`. On exit it updates the reply hint via `ds_rsvc_set_hint()`, releases the leader reference, maps no-reply fault-injection paths to `-DER_TIMEDOUT`, and sends the CRT reply.

Pool attribute get/list are simpler read paths. They look up the leader, begin an RDB transaction, take the read lock, delegate actual attribute serialization and bulk transfer to `ds_rsvc_get_attr()` or `ds_rsvc_list_attr()`, release the lock, end the transaction, set the hint, and reply. There is no operation replay or RDB commit because these operations do not mutate the service database.

Replica update starts from the RPC opcode rather than the pool-service leader path. It duplicates the client-provided rank list into `ranks`, initializes an `id` iov over the pool UUID, and dispatches to RDB-service membership helpers. The remove path is the only usable path in this chunk. The output's `pmo_failed` field is assigned the rank list object so lower layers can mark failed ranks; the reply code is always sent through `pmo_rc`.

Map refresh control flow splits by sync/async call site. The sync helper builds a stack `pool_map_refresh_ult_arg`, creates an `ABT_eventual`, schedules `ds_pool_map_refresh_ult()` on the system xstream, waits for the ULT to publish an integer status, frees the eventual, and returns that status. The async helper heap-allocates the same argument shape and schedules the ULT without waiting.

The maintenance helpers follow a consistent transaction pattern:

- Read helpers such as `ds_pool_prop_fetch()` and `ds_pool_svc_load_map()` open a transaction, take `ps_lock` for reading, call a local RDB reader, release, end, and return.
- Write helpers such as `ds_pool_mark_connectable()`, `ds_pool_svc_update_label()`, and `ds_pool_svc_evict_all()` open a transaction, take `ps_lock` for writing, mutate RDB state, commit only when needed, release, and end.
- `ds_pool_svc_flush_map()` has extra post-commit control flow because RDB is authoritative after commit. If `ds_pool_tgt_map_update()` fails after commit, it resigns leadership with `rdb_resign()` to avoid serving future requests with stale local map state. If local update succeeds, it requests map distribution, drops `ps_lock`, and waits for distribution outside the lock.

## State And Persistence Behavior

Persistent state lives primarily in the pool service RDB:

- User pool attributes are stored below `svc->ps_user` through generic replicated-service attribute helpers. Delete operations persist through a committed RDB transaction; get/list only read and bulk-transfer values.
- Write RPC replay state is stored in `svc->ps_ops` and the `ds_pool_prop_svc_ops_num` root property by `pool_op_save()`. Attribute delete participates in this idempotency state, including fault-injection cases that simulate lost replies.
- Pool service replica membership changes are applied through `ds_rsvc_add_replicas()` / `ds_rsvc_remove_replicas()` to the RDB-service layer, not directly through this file's pool KVS paths.
- Pool map state is persisted as a `pool_buf` and version under `svc->ps_root`. `ds_pool_svc_flush_map()` writes the buffer, commits it, updates the in-memory `svc->ps_pool` target map, and triggers IV/map distribution so children and shards observe the new version.
- Pool labels are persisted as normal pool properties with `pool_prop_write()`. Passing `NULL` explicitly marks the label property unset.
- Pool handles and their credentials live in `svc->ps_handles`. `ds_pool_lookup_hdl_cred()` reads a `struct pool_hdl` value and copies the variable-length credential area for container-service authorization checks.
- Evict-all mutates pool handle state by finding eligible handle UUIDs and disconnecting them through `pool_disconnect_hdls()`. The metric counter is updated in memory, while disconnection state is committed to RDB.
- VOS/RDB upgrade state is persisted below the service replica's RDB/VOS pool by `rdb_upgrade_vos_pool()`, keyed by the data-format version derived from `pool->sp_global_version`.

Several helpers also touch cached state. `ds_pool_hdl_is_from_srv()` uses `pool->sp_srv_pool_hdl` if populated, `ds_pool_target_status*()` reads the cached `pool->sp_map`, and `ds_pool_svc_flush_map()` refreshes `svc->ps_pool` after the authoritative map write.

## Dependencies And Integration Points

This chunk depends heavily on the DAOS replicated service and RDB layers: `pool_svc_lookup_leader()`, `pool_svc_put_leader()`, `ds_rsvc_set_hint()`, `ds_rsvc_*_attr()`, `ds_rsvc_add_replicas()`, `ds_rsvc_remove_replicas()`, `ds_rsvc_lookup()`, `ds_rsvc_query_map_dist()`, `ds_rsvc_request_map_dist()`, `ds_rsvc_wait_map_dist()`, `rdb_tx_begin()`, `rdb_tx_lookup()`, `rdb_tx_commit()`, `rdb_tx_end()`, `rdb_resign()`, and `rdb_upgrade_vos_pool()`.

It also integrates with DAOS pool infrastructure:

- Pool IV and map-refresh code in `srv_iv.c` consumes `struct pool_map_refresh_ult_arg` and implements `ds_pool_map_refresh_ult()`.
- Target-side pool code uses `ds_pool_svc_upgrade_vos_pool()` during pool property/VOS update and `ds_pool_hdl_is_from_srv()` when serving non-client pool target map queries.
- Container service code uses `ds_pool_lookup_hdl_cred()` when it needs to compare a container handle's pool handle owner and the pool handle is not cached in memory. It also calls `ds_pool_prop_recov_cont_reset()` around container metadata changes so pool recovery-container state is retried.
- Pool map and target code provide `pool_map_find_target()`, `pool_buf_extract()`, `pool_buf_free()`, `read_map()`, `write_map_buf()`, and `ds_pool_tgt_map_update()`.
- Security and authorization paths are indirectly involved through stored pool handle credentials (`ph_cred`, `ph_cred_len`) and later comparison in container service.
- Metrics integration uses `svc->ps_pool->sp_metrics[DAOS_POOL_MODULE]`, especially `evict_total`; map-version metrics are handled in nearby map-distribution callbacks.
- Fault injection uses `DAOS_FAIL_CHECK(DAOS_MD_OP_PASS_NOREPLY)` and `DAOS_FAIL_CHECK(DAOS_MD_OP_FAIL_NOREPLY)` to exercise retry/idempotency behavior in attribute write handlers.

The public surface exposed by this range is declared in pool internal headers for use elsewhere in the DAOS server, while many handlers are registered through the DAOS pool RPC dispatch table in adjacent code.

## Risks And Edge Cases

- `pool_attr_del_handler()` begins at this chunk's first line after earlier setup; the important risk is idempotency. Any change that skips `pool_op_save()` or returns the live `rc` rather than saved `op_val.ov_rc` can break retry semantics for write RPCs after dropped replies.
- Fault-injection paths intentionally turn successful or stored `-DER_MISC` outcomes into `-DER_TIMEDOUT` replies. This is test-only behavior but is easy to misread as ordinary error handling.
- Attribute get/list read from the current leader. If leadership changes between lookup and transaction start, `rdb_tx_begin()` or later RDB operations may fail; callers rely on the returned service hint for retry routing.
- The `POOL_REPLICAS_ADD` branch is deliberately unusable and asserts false. Accidentally enabling that RPC without fixing metadata capacity and VOS format arguments could create malformed service replicas.
- `ds_pool_child_map_refresh_async()` does not free `arg` on `dss_ult_create()` failure in this snippet. The ownership contract may rely on caller expectations or ULT behavior, so this is a candidate leak path to inspect if async scheduling fails under resource pressure.
- `ds_pool_hdl_is_from_srv()` uses a cached server handle with an inline comment questioning staleness. If the cached value is stale, internal map-query authorization could reject a valid server handle or accept an old one.
- `ds_pool_target_status_check()` optionally returns a `struct pool_target *` after releasing `pool->sp_lock`. Callers must not assume the returned pointer is stable across concurrent map replacement unless they hold or otherwise serialize map lifetime.
- `ds_pool_lookup_hdl_cred()` intentionally avoids `svc->ps_lock` to prevent lock-order problems with container service locks. The caller's transaction and service leadership must provide enough consistency; this bypass should be treated carefully in any refactor.
- `ds_pool_svc_flush_map()` commits RDB state before updating the local cache. If local update fails, the code resigns leadership, but the new map may already be distributed or later distributed by another leader. Consumers need to tolerate transient leadership churn.
- `ds_pool_svc_evict_all()` commits only when `n_hdl_uuids > 0`. A no-handle result ends the transaction without commit, which is correct for no mutation but important for metrics and audit expectations.
- `ds_pool_svc_upgrade_vos_pool()` returns success when no local pool service replica exists. That is intentional for ranks without a service replica, but callers must not interpret it as proof that every replica has been upgraded.
- `ds_pool_prop_recov_cont_reset()` normalizes positive returns to zero. Positive values from `pool_prop_recov_cont_check_and_update()` mean state changed, not an error.

## Test Signals

Useful verification for this chunk is mostly DAOS server integration testing plus targeted unit/fault-injection coverage:

- Pool attribute tests should cover set/delete/get/list through client RPCs, including deletion of multiple keys via bulk transfer, listing size reporting, and read-after-delete from a new leader.
- Retry/idempotency tests should exercise duplicate pool attribute delete RPCs with the same client UUID/time and verify the second execution returns the saved result without applying the mutation twice.
- Fault-injection tests using `DAOS_MD_OP_PASS_NOREPLY` and `DAOS_MD_OP_FAIL_NOREPLY` should verify client-observed timeouts and server-side saved operation results are compatible with retry.
- Pool service replica membership tests should validate `POOL_REPLICAS_REMOVE`; `POOL_REPLICAS_ADD` should remain unreachable or explicitly fail until the guarded TODO is implemented.
- Pool map tests should cover `ds_pool_child_map_refresh_sync()` and async refresh behavior on non-leader xstreams, including stale local map versions and `DAOS_FORCE_REFRESH_POOL_MAP`.
- Map flush tests should verify RDB map version persistence, local `ds_pool_tgt_map_update()` refresh, map distribution wait behavior, and leadership resignation when local refresh fails after commit.
- Property tests should cover `ds_pool_prop_fetch()` and `ds_pool_svc_update_label()` for set, update, and unset label cases.
- Target-status tests should query existing and nonexistent target ids and verify `-DER_NONEXIST`, status return values, and matched-status boolean behavior.
- Container-service authorization tests should exercise the cache-miss path through `ds_pool_lookup_hdl_cred()` and verify the returned credential buffer is freed by the caller.
- Eviction tests should cover no-handle and many-handle cases for `ds_pool_svc_evict_all()`, checking handle disconnection, RDB commit behavior, and `evict_total` metric increments.
- Upgrade tests should cover supported and unsupported pool global versions, ranks with and without local service replicas, and errors from `rdb_upgrade_vos_pool()`.
