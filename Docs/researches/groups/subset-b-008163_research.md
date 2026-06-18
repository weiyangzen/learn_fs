# subset-b-008163 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_space.c -->
# sources/object-store/daos/src/vos/vos_space.c

Purpose: implements VOS pool space accounting, reservation, admission control, and telemetry updates for SCM, NVMe, and evictable-pool non-evictable memory buckets. It is the local guard used before updates allocate persistent VOS metadata or data extents.

Important APIs/functions: `vos_space_sys_init` computes built-in system reservations from GC, aggregation, NVMe availability, tiny/small pool status, and `frag_reserve_space`. `vos_space_sys_set` recomputes defaults, adds caller-provided reservations, validates against pool totals, and rolls back on error. `vos_space_query` fills `vos_pool_space` with total/free/system fields and optional VEA stats. `vos_space_hold` estimates update or remove cost, verifies available capacity after system, held, and rebuild reservations, and increments held counters. `vos_space_unhold` releases held accounting. `vos_space_update_metrics` periodically publishes SCM/NVMe total and used gauges.

Control flow and state: reservations live in `vos_pool::vp_space_sys`, `vp_space_held`, and `vp_space_rb`; durable totals are read from `vp_pool_df`. Space queries call PMDK/umem heap usage for SCM and VEA for NVMe. `estimate_space` conservatively assumes new object/dkey/akey/tree nodes and accounts single-value records, array extents, checksums, and SCM-vs-NVMe placement via `vos_io_scm`.

Dependencies/integration: depends on `vos_internal.h`, umem/PMDK heap APIs, VEA allocator stats, checksum helpers, VOS record sizing helpers, DAOS telemetry, and rebuild/update flags such as `VOS_OF_CRIT`, `VOS_OF_REMOVE`, and `VOS_OF_REBUILD`.

Risks: estimates are intentionally coarse and can reject updates early or underrepresent unusual metadata growth. Critical and remove operations bypass checks. NVMe held space is treated differently because VEA free space already excludes reservations. PMDK heap usage can return invalid values, handled by clamping SCM free to zero. Metrics are rate-limited to one second and tolerate query errors by logging.

Test signals: exercise tiny/small pools, pools without NVMe, evictable pools, rebuild reserve percentages, `VOS_OF_REMOVE` and `VOS_OF_CRIT`, failed VEA/umem queries, hold/unhold counter balance assertions, and telemetry refresh throttling.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_space.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_tls.h -->
# sources/object-store/daos/src/vos/vos_tls.h

Purpose: defines per-xstream/thread VOS TLS state and inline accessors for objects that many VOS paths need without threading parameters through every call.

Important APIs/types: `struct vos_tls` holds GC pool lists, PMDK transaction-stage data, the current DTX handle, timestamp table, standalone profile, object LRU cache, pool/container handle hash tables, a saved key hash, and telemetry nodes. Accessors include `vos_pool_hhash_get`, `vos_cont_hhash_get`, `vos_obj_cache_get`, `vos_txd_get`, `vos_ts_table_get`, `vos_ts_table_set`, `vos_dth_set/get`, `vos_kh_set/get/clear`, `vos_hash_get`, and `vos_sched_seq`.

Control flow and state: most functions call `vos_tls_get(standalone)` and return fields. `vos_dth_set` also drains `dth_share_tbd_list` when replacing a DTX handle with pending shared peers. `vos_hash_get` consumes a saved hash once and otherwise computes Murmur64 with `BTR_MUR_SEED`. `vos_sched_seq` returns zero in standalone builds and the scheduler sequence otherwise.

Dependencies/integration: integrates with GURT lists/hash tables, DAOS btree/hash helpers, LRU caches, BIO xstream context, DTX server state, telemetry, VOS timestamp tables, and VOS standalone tests. Tree code uses the saved hash path to avoid recomputing hashes for long keys.

Risks: the file documents the DTX handle TLS path as a hack: callers must avoid CPU yield while relying on `vtl_dth`, or another ULT on the same xstream could change it. Hash hints are one-shot and must be cleared or consumed in the right order. Accessors assume TLS exists except for `vos_dth_get`, which tolerates null.

Test signals: cover standalone and non-standalone TLS, DTX replacement with shared peers, hash set/get/clear behavior, `vos_hash_get` consuming saved hashes, and scheduler sequence fallback under `VOS_STANDALONE`.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_tree.c -->
# sources/object-store/daos/src/vos/vos_tree.c

Purpose: registers and implements VOS object, dkey, akey, single-value, and extent-tree integration on top of DAOS btree/evtree primitives. It owns durable key records, single-value records, subtree creation/opening, DTX/ilog hooks, and punch/delete behavior.

Important APIs/functions: `obj_tree_register`, `obj_tree_init`, and `obj_tree_fini` register/open/close object dkey trees. Key btree callbacks include `ktr_rec_alloc/free/fetch/update`, hashed-key generation/comparison, lexical/default key comparison, and embedded anchor encode/decode. Single-value callbacks include `svt_rec_store/load/alloc/update/free`, `svt_check_availability`, payload free helpers, and overwrite handling. Public helpers include `key_tree_prepare`, `key_tree_release`, `key_tree_punch`, `key_tree_delete`, `vos_tree_mark_corruption`, `vos_evt_desc_cbs_init`, `evt_dop_log_add`, and `vos_irec_is_valid`.

Control flow and state: durable VOS state is stored in `vos_krec_df`, `vos_irec_df`, btree roots, evtree roots, ilogs, DTX record IDs, and BIO addresses. `key_tree_prepare` fetches or creates a key record, updates timestamp conflict tracking, then opens or creates the child btree/evtree based on `SUBTR_*` flags and existing `KREC_BF_BTR/KREC_BF_EVT` bits. `tree_open_create` prevents mixing array and single-value subtrees under one key. Punch paths insert missing keys for replay/propagation as needed, add ilog punch entries, invalidate known-key punch propagation state, and mark keys for aggregation.

Dependencies/integration: tightly coupled to DAOS btree, evtree, umem transactions, BIO allocation/free, DTX registration and availability, VOS ilog timestamp tracking, GC queues, checksums, object type feature selection, and VOS pool features such as dynamic roots and embedded-first trees.

Risks: this is a high-risk persistence module. Same-epoch single-value overwrite is rejected via minor epoch checks; overwrite frees require a DTX handle and cannot handle gang addresses. Free paths must deregister DTX records, release NVMe/SCM payloads, or enqueue GC correctly. Type mismatches between evtree and btree return `-DER_NONEXIST` or `-DER_NO_PERM` depending on create intent. Corruption marking creates missing keys if necessary and sets ilog corruption flags. Hash and timestamp interactions depend on TLS helpers.

Test signals: cover dkey/akey/single-value creation, array-vs-single conflicts, lexical/uint/default key comparisons, DTX availability filtering, same-epoch overwrite rejection, gang/NVMe payload free, punch of existing and missing keys, replay punch, corruption marking, dynamic-root/embedded-first features, and GC enqueue failures.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_ts.c -->
# sources/object-store/daos/src/vos/vos_ts.c

Purpose: implements allocation, eviction, upgrade, and conflict checks for the VOS in-memory timestamp cache used by transactional read/write conflict detection.

Important APIs/functions: `vos_ts_table_alloc/free` allocate per-type LRU arrays and negative miss caches. `vos_ts_evict_lru` allocates or evicts an LRU entry and initializes it from global or negative timestamps. `vos_ts_set_allocate` creates an operation-local timestamp set when conditional operations or a real DTX require tracking. `vos_ts_set_upgrade` promotes negative entries to positive LRU entries after creates. `vos_ts_check_read_conflict` checks whether a write timestamp conflicts with recorded low/high read timestamps.

Control flow and state: cache state is memory-only in `vos_ts_table` and `vos_ts_entry`. On eviction, `ts_update_on_evict` pushes read timestamps and write timestamp cache data into the entry's negative cache or table-global state, preserving conservative conflict knowledge after the positive entry is reused. Allocation initializes miss entries from global start timestamps and creates LRU arrays for container, object, dkey, and akey levels. Timestamp sets record the transaction ID so same-epoch writes from a different DTX still conflict.

Dependencies/integration: depends on `vos_internal.h`, `vos_ts.h`, `lru_array`, DTX IDs, TLS telemetry allocation gauges, and VOS operation flags. Tree code and ilog paths populate timestamp sets as they walk object/key hierarchy.

Risks: correctness depends on negative-cache hashing and LRU eviction preserving conservative bounds; false sharing in negative entries is accepted, but missed updates would be dangerous. The conflict comparison treats equal epochs with different DTX IDs as conflicts. Non-transactional operations and non-conditional operations may skip allocation, so callers must pass correct flags.

Test signals: cover table allocation cleanup on partial failure, global-vs-negative eviction updates, conflict detection for lower/higher/equal epochs and same/different DTX IDs, negative entry upgrade after create, and memory gauge accounting.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_ts.h -->
# sources/object-store/daos/src/vos/vos_ts.h

Purpose: declares timestamp-cache structures and inlines for VOS transactional conflict tracking across container, object, dkey, and akey hierarchy levels.

Important APIs/types: defines `vos_ts_info`, `vos_ts_pair`, `vos_wts_cache`, `vos_ts_entry`, `vos_ts_set_entry`, `vos_ts_set`, `vos_ts_table`, read/write flag bits, and timestamp type counts. Inline helpers include `vos_ts_in_tx`, lookup/allocation helpers, `vos_ts_get_negative`, `vos_ts_wcheck`, `vos_ts_set_add`, `vos_ts_set_mark_entry`, `vos_ts_evict`, `vos_ts_peek_entry`, `vos_ts_set_check_conflict`, `vos_ts_set_update`, `vos_ts_set_wupdate`, and state save/restore.

Control flow and state: callers allocate a `vos_ts_set`, add entries as VOS descends through object/dkey/akey records, optionally use negative entries for missing subtrees, then update read or write timestamps after operation success. The table keeps high/low read timestamps and the two highest write timestamps needed for uncertainty-bound checks. `vos_ts_set_add` advances expected hierarchy type automatically, hashes object IDs specially, and uses TLS saved hashes for keys.

Dependencies/integration: includes DAOS DTX types, VOS TLS, and `lru_array`. It is designed for hot-path inlining and is used by tree and ilog code to coordinate conditional fetch/update semantics with DTX conflict checks.

Risks: many functions are no-ops when not in a real transaction, so caller flag correctness is essential. `ts_set_size` must account for all akeys or `-DER_BUSY` can occur. `vos_ts_set_get_entry_type` computes indexes from type/akey index and relies on ordering assumptions. `vos_ts_wcheck` is conservative when the write cache lacks enough history, which can reject operations under uncertainty.

Test signals: cover hierarchy insertion order, duplicate or repeated akey handling, negative lookup paths, hash-index derivation from parent entries, write uncertainty cases documented in `vos_ts_wcheck`, read/write level selection, and save/restore around speculative tree probes.
<!-- END_FILE_RESEARCH: sources/object-store/daos/src/vos/vos_ts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/fuzz/src/lib.rs -->
# sources/object-store/garage/fuzz/src/lib.rs

Purpose: provides a generic fuzz/test helper for validating CRDT merge laws used by Garage table state.

Important API: `check_crdt_laws<T>(a, b, c)` accepts any `T: Crdt + PartialEq + Clone + Debug` and asserts idempotency, commutativity, a corollary idempotency after merge, and associativity.

Control flow and state: the helper clones inputs, mutates the clones through `merge`, and compares resulting values with `assert_eq!`. It has no persistence and no external side effects beyond panics on law violations.

Dependencies/integration: depends on `garage_table::crdt::Crdt` and Rust `Debug`. Fuzz targets can instantiate arbitrary CRDT values and call this helper to catch merge implementations that would make distributed table reconciliation non-convergent.

Risks: it validates algebraic laws for three provided values only; fuzz quality depends on generators. It does not test serialization, tombstone compaction, timestamp monotonicity, or partial-order semantics unless encoded in generated values.

Test signals: useful failures are assertion messages showing non-idempotent, non-commutative, or non-associative merges. Add fuzz corpora for CRDT values with deletes, concurrent updates, equal timestamps, and empty/default states.
<!-- END_FILE_RESEARCH: sources/object-store/garage/fuzz/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/Cargo.toml -->
# sources/object-store/garage/src/api/admin/Cargo.toml

Purpose: declares the `garage_api_admin` Rust crate, which builds the Garage Admin API server library from `lib.rs`.

Important configuration: package metadata identifies version `2.3.0`, edition 2018, AGPL-3.0 license, repository, and README. The `[lib]` section points at `lib.rs`. Dependencies include Garage workspace crates (`garage_model`, `garage_block`, `garage_table`, `garage_util`, `garage_rpc`, `garage_api_common`) and external API/runtime crates such as `hyper`, `http`, `tokio`, `serde`, `utoipa`, `argon2`, `chrono`, `thiserror`, `paste`, `format_table`, `opentelemetry`, and optional Prometheus support.

Control flow and state: no runtime control flow. Feature flags gate optional integrations: `metrics` enables Prometheus exporter dependencies, and `k2v` forwards to `garage_model/k2v`. Lints are inherited from the workspace.

Dependencies/integration: this manifest is the integration surface between the admin API implementation and the workspace dependency graph. It also controls whether metrics endpoints can expose Prometheus data and whether K2V tables appear in node statistics.

Risks: `hyper` is built without default features and with `server`/`http1`, so HTTP behavior depends on common server abstractions for missing capabilities. Optional metrics code must stay cfg-gated with the feature. Workspace version drift can break schema, RPC, or helper assumptions across Garage crates.

Test signals: run crate checks with default features, with `--features metrics`, and with `--features k2v`. API schema generation and admin server tests should confirm optional fields compile under all feature combinations.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/admin_token.rs -->
# sources/object-store/garage/src/api/admin/admin_token.rs

Purpose: implements Admin API token management endpoints: list, lookup, create, update, delete, and describe the current bearer token.

Important handlers: `ListAdminTokensRequest` returns non-deleted table tokens plus configured daemon `metrics_token` and `admin_token` pseudo-records. `GetAdminTokenInfoRequest` finds exactly one token by ID or search. `CreateAdminTokenRequest` creates a new `AdminApiToken`, applies requested fields, persists it, and returns the secret once. `UpdateAdminTokenRequest` edits mutable parameters. `DeleteAdminTokenRequest` writes a delete tombstone. `GetCurrentAdminTokenInfoRequest` maps the presented bearer token to config pseudo-token or table token metadata.

Control flow and state: persistent state is in `garage.admin_token_table` as CRDT/deletable token records. `apply_token_updates` enforces mutual exclusion between explicit expiration and `never_expires`, then updates name, expiration, and scope CRDT fields. `admin_token_info_results` converts stored milliseconds to `DateTime<Utc>` and computes `expired` using `now_msec`.

Dependencies/integration: uses Garage table range/get/insert APIs, `AdminApiToken` model helpers, `ExpirationTime`, chrono timestamps, and shared admin `RequestHandler` contracts. Authentication enforcement lives in `api_server.rs`; this file manages persisted token metadata and scopes used by that enforcement.

Risks: `GetCurrentAdminTokenInfoRequest` assumes non-config tokens contain a `.` and unwraps `split_once`, relying on prior auth parsing. Granting `CreateAdminToken` or `UpdateAdminToken` scope is privilege escalation by design and warned in schema. Search must match exactly one candidate. Timestamp conversion uses `expect` for invalid stored values.

Test signals: cover config pseudo-token listing/current-info, ID vs search exclusivity, create returning secret once, expiration/never-expire conflict, scope updates, delete tombstones, expired filtering through server auth, and malformed current-token inputs.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/admin_token.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/api.rs -->
# sources/object-store/garage/src/api/admin/api.rs

Purpose: defines the public and RPC-serializable Admin API request/response schema for cluster, token, layout, key, bucket, node, worker, and block operations.

Important APIs/types: `admin_endpoints!` generates `AdminApiRequest`, `AdminApiResponse`, and tagged RPC responses for all public endpoints. `local_admin_endpoints!` creates multi-node wrappers for local operations and `LocalAdminApiRequest/Response`. Data contracts include `MultiRequest/MultiResponse`, cluster status/health/statistics structures, admin token and access key structures, layout role and history structures, bucket info/update/inspection structures, node statistics, worker state, block errors, block backlinks, and purge responses.

Control flow and state: this file mostly has schema declarations; generated `RequestHandler` impls delegate actual work to per-domain modules. Multi-node request handlers use `find_matching_nodes`, Garage RPC `call_many`, and tagged local responses to aggregate successes and errors by node ID.

Dependencies/integration: integrates serde serialization, utoipa schema generation, `garage_rpc` RPC helpers, `garage_api_common` XML/common-error types, admin macros, and all domain handler modules. Compatibility is visible through many `FIXME for v3` optional/default fields kept for v2 clients.

Risks: schema changes are public API changes. Untagged enums such as preview results, bucket alias changes, retry block requests, and admin responses can be ambiguous if fields overlap. Multi-node response conversion must match the local response variant or reports "returned invalid value". The endpoint list must stay synchronized with routers, OpenAPI generation, auth scopes, and handler impls.

Test signals: schema serialization/deserialization round trips, OpenAPI generation, router-to-request parsing, tagged RPC conversions, multi-node aggregation with success/error/mismatched variants, backward compatibility for defaulted fields, and scope names matching `AdminApiRequest::name`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/api.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/api_server.rs -->
# sources/object-store/garage/src/api/admin/api_server.rs

Purpose: implements the Admin API HTTP/RPC server, endpoint parsing, request dispatch, bearer-token authorization, and node matching for proxied local requests.

Important APIs/types: `AdminRpc` carries proxied public or local admin requests. `AdminRpcResponse` carries tagged success or serialized API errors. `AdminApiServer::new` initializes hashed configured tokens and registers the RPC endpoint. `run` starts the generic API server. `handle_http_api` parses old/new routes, determines authorization type, verifies bearer tokens, and dispatches special or JSON endpoints. `verify_authorization` validates config tokens or persisted admin-token-table entries using Argon2. `find_matching_nodes` resolves `self`, `*`, or node ID prefixes.

Control flow and state: configured admin/metrics tokens are hashed at startup and kept in memory. Persisted token lookup is local table state keyed by token prefix and filtered for non-expired scope-bearing records. HTTP paths under `/v0/` and `/v1/` use legacy routers; other paths use new request parsing. RPC handling converts handler errors into transportable HTTP code/error/message triples.

Dependencies/integration: uses `garage_api_common::generic_server`, Hyper requests/responses, Garage RPC endpoint machinery, admin routers, argon2 password hashing, Garage system node state, background runner, optional Prometheus exporter, and admin schema/handlers.

Risks: startup hashes configured tokens with random salts, so equality uses Argon2 verification rather than stable hashes. `parse_authorization` requires exact `Bearer ` prefix. Global config tokens have no prefix; table tokens must be `prefix.secret`. `GetCurrentAdminTokenInfo` is deliberately exempted from scope checks after token validity. Node-prefix matching errors on zero or multiple matches.

Test signals: legacy and new route parsing, CORS headers on success/error, missing/malformed bearer headers, config token and table token verification, expired/scope-denied tokens, metrics token requirement modes, RPC error marshalling, and node selector behavior for `self`, `*`, unique and ambiguous prefixes.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/api_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/block.rs -->
# sources/object-store/garage/src/api/admin/block.rs

Purpose: implements local block administration endpoints for inspecting resync errors, block references/backlinks, retrying resync, and purging blocks plus associated metadata references.

Important handlers/functions: `LocalListBlockErrorsRequest` maps block manager resync errors into API rows. `LocalGetBlockInfoRequest` resolves a block hash prefix, reads refcount and block reference table entries, and joins version/MPU/object backlinks. `LocalRetryBlockResyncRequest` clears backoff for all errored blocks or a provided list. `LocalPurgeBlocksRequest` marks versions and block refs deleted and may add object delete markers or delete MPU records. Helpers are `find_block_hash_by_prefix` and `handle_block_purge_version_backlink`.

Control flow and state: local persistent state spans block manager reference counts/resync queue, `block_ref_table`, `version_table`, `mpu_table`, and `object_table`. Purge walks requested hashes, marks block refs deleted, marks versions deleted, clears MPU parts when needed, and inserts a delete marker if the purged version is the latest complete object version.

Dependencies/integration: depends on Garage block manager, S3 object/version/MPU models, table range/get/insert APIs, hash parsing, common error helpers, and local admin RPC wrappers generated in `api.rs`.

Risks: purge is destructive metadata surgery and must preserve table convergence through tombstones rather than raw deletion. Prefix lookup requires at least four characters and scans the underlying block-ref store; ambiguous prefixes fail. `LocalGetBlockInfo` limits range reads to 10000 refs. Object delete-marker insertion uses `timestamp + 1`, which assumes monotonic ordering is sufficient for hiding purged latest versions.

Test signals: cover prefix validation/ambiguity, blocks with object backlinks, MPU backlinks present and garbage-collected, retry all vs selected blocks, purge idempotency, deleted refs/versions, latest-version delete marker insertion, and large ref fanout behavior near the 10000 limit.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/block.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/bucket.rs -->
# sources/object-store/garage/src/api/admin/bucket.rs

Purpose: implements bucket administration: list, lookup, create, update, delete, cleanup incomplete uploads, inspect object versions, grant/revoke key permissions, and manage global/local aliases.

Important handlers/functions: `ListBucketsRequest`, `GetBucketInfoRequest`, `CreateBucketRequest`, `DeleteBucketRequest`, `UpdateBucketRequest`, `CleanupIncompleteUploadsRequest`, `InspectObjectRequest`, `AllowBucketKeyRequest`, `DenyBucketKeyRequest`, `AddBucketAliasRequest`, `RemoveBucketAliasRequest`, `handle_bucket_change_key_perm`, `bucket_info_results`, and `parse_bucket_id`.

Control flow and state: persistent state is spread across bucket table, bucket alias table, key table, object/version tables, object and MPU counter tables, and helper-managed alias/permission links. Create validates requested aliases, inserts a new bucket, then sets aliases and optional key permissions under the locked helper. Delete requires bucket emptiness, revokes key permissions, purges local/global aliases, then writes a bucket delete tombstone. Update mutates website, quota, CORS, and lifecycle CRDT fields. Inspect object reads object versions and joins version blocks to produce version/block metadata.

Dependencies/integration: uses Garage model helpers for locked multi-table changes, bucket/key permission types, S3 object and MPU tables, XML conversion/validation for website/CORS/lifecycle configs, CRDT wrappers, time utilities, and common bucket-name validation.

Risks: alias and permission operations span multiple CRDT tables, so using `locked_helper` is critical. Search by bucket ID prefix can be ambiguous. Delete depends on `is_bucket_empty` correctness. Website disabling rejects stray index/error fields but routing rules behavior follows request shape. Object inspection omits plaintext headers for encrypted variants and reports block metadata only when version rows exist.

Test signals: cover alias validation and conflicts, local alias with key lookup, bucket delete with non-empty buckets, full alias/permission cleanup on delete, website/CORS/lifecycle validation, quota updates, incomplete upload cleanup thresholds, inspect variants for uploading/complete/delete-marker/aborted/inline/first-block versions, and allow/deny partial permission bits.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/cluster.rs -->
# sources/object-store/garage/src/api/admin/cluster.rs

Purpose: implements cluster-wide status, health, statistics, and peer connection endpoints.

Important handlers: `GetClusterStatusRequest` merges known-node liveness with current and older layout roles to report nodes, roles, disk free space, and draining state. `GetClusterHealthRequest` maps system health into stable strings and counters. `GetClusterStatisticsRequest` computes bucket/object totals and cluster-wide available data/metadata estimates, returning both free-form text and structured fields. `ConnectClusterNodesRequest` asks the system layer to connect to provided node addresses.

Control flow and state: reads current cluster layout history, known node statuses, bucket table, object counter table, and ring assignment data. Availability estimates count partitions per node and use the minimum per-partition available bytes multiplied by partition count, marking results incomplete when any storage node lacks disk information. It avoids gathering per-bucket counters when there are 1000 or more buckets.

Dependencies/integration: uses `garage_rpc::layout`, partition constants, Garage system health and connect APIs, table enumeration, object counters, `bytesize`, and `format_table` for compatibility free-form output.

Risks: statistics are estimates and can be lower in practice; missing node disk info makes them imprecise. Large bucket counts skip object totals. Layout reads can fail or be unavailable, in which case parts of status/statistics degrade. Free-form output is maintained for compatibility and should not be treated as parseable.

Test signals: cover connected and disconnected nodes, nodes only in older layouts as draining, gateway vs storage roles, health status mapping, statistics with complete and missing disk info, bucket count above and below 1000, empty layouts, and connect success/failure aggregation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/cluster.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/error.rs -->
# sources/object-store/garage/src/api/admin/error.rs

Purpose: defines the Admin API error type and maps admin/domain failures to HTTP status codes, API error codes, headers, and JSON bodies.

Important APIs/types: `enum Error` wraps `CommonError` and adds `NoSuchAdminToken`, `NoSuchAccessKey`, `NoSuchBlock`, `NoSuchWorker`, `NoSuchKey`, and `KeyAlreadyExists`. `commonErrorDerivative!` supplies shared constructors/conversions. `From<HelperError>` maps helper errors into common or admin-specific variants. `Error::code` returns stable API code strings. `ApiError` impl provides HTTP status, CORS/content-type headers, and serialized body.

Control flow and state: no persistence. Error conversion is synchronous and used by handlers and the generic API server. Most not-found variants map to 404; duplicate imported keys map to 409; common errors delegate to shared status logic.

Dependencies/integration: depends on Hyper status/header types, `thiserror`, Garage common error helpers, generic server `ApiError`, and helper-layer errors from `garage_model`.

Risks: the `From<HelperError>` impl has an `unreachable!()` for helper errors not convertible to `CommonError` or `NoSuchAccessKey`; new helper variants could panic if not handled. Error body JSON serialization fallback hides serialization failures behind an InternalError-shaped payload. Code strings are client-visible and should remain stable.

Test signals: cover status/code/body for every variant, CORS headers on errors, helper-error conversion including new helper variants, JSON serialization fallback, and common error delegation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/key.rs -->
# sources/object-store/garage/src/api/admin/key.rs

Purpose: implements S3 access-key administration: list, lookup, create, import, update, delete, and detailed key info with related bucket permissions and aliases.

Important handlers/functions: `ListKeysRequest`, `GetKeyInfoRequest`, `CreateKeyRequest`, `ImportKeyRequest`, `UpdateKeyRequest`, `DeleteKeyRequest`, `key_info_results`, and `apply_key_updates`.

Control flow and state: key records are persisted in `garage.key_table`. Creation generates a new key and returns secret material in the detail response. Import rejects any existing record for the supplied access key ID, even deleted ones, validates key format through `Key::import`, and stores the imported key. Update mutates CRDT fields for name, expiration, and create-bucket permission. Delete uses `locked_helper` so associated bucket permissions/aliases can be cleaned consistently. `key_info_results` joins authorized bucket IDs and local aliases to bucket table state and optionally includes the secret key.

Dependencies/integration: uses Garage key model, bucket table, locked helper, permission expiration type, table range/get/insert APIs, chrono conversion, and admin schema types.

Risks: secret key exposure depends on `show_secret` and creation/import choices; callers must avoid logging responses. Search must resolve exactly one key. Import cannot reuse deleted key IDs, which avoids resurrection ambiguity but may surprise users. Timestamp conversion panics on invalid stored milliseconds. Update `allow`/`deny` only affects `create_bucket`; bucket-specific permissions are managed in `bucket.rs`.

Test signals: cover list filtering of deleted keys, lookup by ID/search/no match/multiple matches, create with secret returned, import invalid/existing/deleted key IDs, expiration vs never-expire conflict, allow/deny create-bucket transitions, delete cleanup via helper, and `show_secret_key` response behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/key.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/layout.rs -->
# sources/object-store/garage/src/api/admin/layout.rs

Purpose: implements cluster layout read/update/apply/revert/history operations and skip-dead-node tracker manipulation.

Important handlers/functions: `GetClusterLayoutRequest`, `format_cluster_layout`, `GetClusterLayoutHistoryRequest`, `UpdateClusterLayoutRequest`, `PreviewClusterLayoutChangesRequest`, `ApplyClusterLayoutRequest`, `RevertClusterLayoutRequest`, `ClusterLayoutSkipDeadNodesRequest`, and conversions between API and internal `layout::ZoneRedundancy/LayoutParameters`.

Control flow and state: layout state lives in Garage system `LayoutHistory`, including current versions, old versions, staging CRDTs, role maps, parameters, and update trackers. Update merges current roles with staging, validates node IDs and capacities, writes staged role/parameter changes through the layout manager, and returns formatted layout. Preview computes but does not persist staged changes. Apply computes a requested new version and persists it. Revert clears staging. Skip-dead-nodes advances ACK and optionally SYNC trackers for dead or all nodes to unblock old-layout retirement.

Dependencies/integration: depends on Garage RPC layout types, CRDT merge/update mutators, Garage system layout manager, node status, and admin schema role/parameter types.

Risks: layout changes affect placement and data movement. Capacity below 1024 is rejected, and zone redundancy must be between 1 and replication factor. Apply requires the caller-specified version as a safety check but still depends on current staging. `allow_missing_data` in skip-dead-nodes can mark sync progress despite missing data quorum, so it is operationally dangerous. Preview returns structured error for layout computation messages but propagates other errors.

Test signals: cover format output for current/staged roles and parameters, invalid node IDs/capacity/redundancy, update then preview/apply/revert, version mismatch on apply, history statuses current/draining/historical, tracker maps when multiple versions exist, and skip-dead-nodes with and without `allow_missing_data`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/layout.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/lib.rs -->
# sources/object-store/garage/src/api/admin/lib.rs

Purpose: crate root for the Garage Admin API server. It declares module boundaries, exports the server type, and defines the common authorization and request-handler abstractions used throughout admin modules.

Important APIs/types: exports `api_server::AdminApiServer` as `Admin`; defines `Authorization::{None, MetricsToken, AdminToken}`; defines trait `RequestHandler` with associated `Response` and an async-returning `handle(self, &Arc<Garage>, &Admin)` method. It publicly exposes `api`, `api_server`, and `openapi`, and keeps routers/domain modules private.

Control flow and state: no runtime state is stored here. The trait is the dispatch contract consumed by macros in `macros.rs` and by `api_server.rs`. Module declarations cause handler impls to be linked for tokens, buckets, cluster, layout, block, node, repair, worker, and special endpoints.

Dependencies/integration: depends on `tracing` macros via `#[macro_use] extern crate tracing`, `Arc`, and `garage_model::garage::Garage`. It is the top-level integration point for generated routers/OpenAPI and all endpoint modules.

Risks: adding a new endpoint requires coordinated changes across this module list, `api.rs` endpoint macros, routers/OpenAPI, and a `RequestHandler` impl. The trait uses `impl Future + Send`, so handler futures must remain sendable; non-Send captured state would fail compilation.

Test signals: compile tests are primary. Add endpoint smoke tests when introducing modules to ensure the macro-generated dispatch sees the handler impl and the endpoint is exported through router/OpenAPI as expected.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/macros.rs -->
# sources/object-store/garage/src/api/admin/macros.rs

Purpose: provides code-generation macros that connect endpoint type declarations in `api.rs` to request/response enums, tagged RPC conversion, dispatch, and local multi-node RPC fanout.

Important macros: `admin_endpoints!` generates `AdminApiRequest`, `AdminApiResponse`, `TaggedAdminApiResponse`, endpoint names, response tagging, `From<Request>` conversions, `TryFrom<TaggedAdminApiResponse>` conversions, and `RequestHandler` dispatch. `local_admin_endpoints!` generates `LocalAdminApiRequest/Response`, public multi-node request/response aliases, conversions, fanout `RequestHandler` impls, local endpoint names, and local dispatch.

Control flow and state: generated public dispatch rejects special endpoints outside HTTP, delegates regular endpoints to their request handlers, and wraps responses. Generated local fanout resolves nodes, sends `AdminRpc::Internal` via `call_many`, then fills `MultiResponse.success` or `.error` maps keyed by hex node ID.

Dependencies/integration: relies on `paste`, serde derives available in the expansion context, `find_matching_nodes`, `AdminRpc`, `AdminRpcResponse`, `RequestStrategy::with_priority(PRIO_NORMAL)`, `HashMap`, `hex`, and the `RequestHandler` trait.

Risks: macro expansions hide a large amount of API surface; endpoint ordering and names become auth scope strings and RPC variant names. Untagged public responses need tagged wrappers for RPC to avoid ambiguity. Local fanout treats unexpected response variants as per-node errors, not hard failures. Special endpoints must remain HTTP-only.

Test signals: compile expansion for new endpoints, conversion tests for tagged responses, special endpoint rejection through generic dispatch, local fanout with success/API error/RPC error/wrong variant, and endpoint name stability for authorization scopes.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/macros.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/admin/node.rs -->
# sources/object-store/garage/src/api/admin/node.rs

Purpose: implements local node information, metadata snapshot, and node statistics endpoints.

Important handlers/functions: `LocalGetNodeInfoRequest` returns local node ID, hostname, version/build info, DB engine, address, role, draining state, and disk partitions. `LocalCreateMetadataSnapshotRequest` triggers asynchronous metadata snapshot creation. `LocalGetNodeStatisticsRequest` builds compatibility free-form text plus structured table and block-manager statistics. `gather_table_stats` reads per-table approximate item counts, Merkle tree size, Merkle queue, insert queue, and GC queue.

Control flow and state: reads local system status, current/old layout versions, known nodes, database engine metadata, many Garage metadata tables, and block manager queues. Snapshot endpoint delegates to `garage_model::snapshot::async_snapshot_metadata`, which persists snapshot artifacts outside this file.

Dependencies/integration: depends on Garage system/local status, layout history, version helpers, DB engine, table replication/schema traits, block manager stats, optional `k2v` feature tables, `format_table`, and local admin RPC wrappers.

Risks: statistics are approximate and some fields are retained as free-form compatibility text. `garage_features().unwrap()` in statistics assumes build feature metadata exists. Draining detection compares current role absence with older layout presence. Adding new metadata tables requires updating statistics coverage.

Test signals: cover node info for storage/gateway/draining states, disk info presence/absence, snapshot success/failure propagation, table stats for all included tables, k2v feature builds, block manager queue counts, and behavior when feature metadata is unavailable.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/admin/node.rs -->
