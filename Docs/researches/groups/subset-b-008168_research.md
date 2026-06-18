# subset-b-008168 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/admin_token_table.rs -->
# sources/object-store/garage/src/model/admin_token_table.rs

## Purpose
This file defines the replicated metadata table for Garage admin API bearer tokens. It stores token identifiers, argon2 password hashes of the full token, human-visible names, optional expiration, and endpoint scopes in CRDT-friendly structures so admin credentials can be created, updated, revoked, filtered, and replicated through the control-plane table system.

## Important APIs, types, and functions
`AdminApiToken` stores the public token prefix and a `crdt::Deletable<AdminApiTokenParams>`. `AdminApiTokenParams` contains `created`, `token_hash`, LWW `name`, LWW optional `ExpirationTime`, and LWW `AdminApiTokenScope`. `AdminApiTokenScope` wraps a vector of endpoint/scope strings. `AdminApiToken::new` generates `<prefix>.<secret>`, hashes the full bearer token with Argon2 and a random salt, and returns both the persisted record and plaintext token. `delete`, `is_deleted`, `params`, `params_mut`, `scope`, `is_expired`, and `has_scope` are the main accessors and policy checks. `AdminApiTokenTable` implements `TableSchema` under `admin_token` and reuses `KeyFilter` for deleted and name/prefix search.

## Control flow
Creation generates a random 12-byte hex prefix and a 32-byte URL-safe base64 secret, hashes the joined token, and initializes scope to `["*"]`. Normal admin authentication paths can look up by prefix, verify the plaintext token against `token_hash` elsewhere, then call `is_expired` and `has_scope`. Table filtering lowercases the search pattern and matches non-deleted token prefixes or exact lowercased names.

## State and persistence behavior
Only the token prefix and password hash are persisted; the plaintext bearer token is returned once from `new`. The table has an explicit migration marker `G2admtok`. Mutable fields are CRDTs: name, expiration, and scope are LWW values, while delete state uses `Deletable`. Scope merge is restrictive intersection, so concurrent divergent scope edits converge to the common allowed endpoints.

## Dependencies and integration points
The table depends on `garage_util::crdt`, `garage_table::{Entry, TableSchema}`, `garage_util::time::now_msec`, `base64`, `rand`, `hex`, and `argon2`. It is instantiated by `Garage::new` as a fully replicated control table and exposed to admin API logic. `ExpirationTime` comes from `permission.rs`; filters come from `key_table.rs`.

## Risks and edge cases
Plaintext tokens are only available at creation, so callers must surface them immediately. `AdminApiTokenScope::merge` computes intersection but preserves the left-side ordering and duplicates if present, so API-side validation should normalize scopes. Argon2 failures panic via `expect`, which is acceptable for normal randomness/hash configuration but not recoverable. Search matches names by exact lowercase equality, not substring. Expiration timestamps must use the same millisecond timebase as `now_msec`.

## Test signals
There are no direct tests in this file. The `arbitrary` feature can generate token scopes for fuzz/property tests. Meaningful coverage should exercise create/verify/revoke flows, scope intersection under concurrent edits, expiration boundary checks, and table filtering.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/admin_token_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/bucket_alias_table.rs -->
# sources/object-store/garage/src/model/bucket_alias_table.rs

## Purpose
This file defines the global bucket alias table and bucket-name validator. A global alias maps an S3 bucket name to a bucket UUID via an LWW canceling option, allowing aliases to be created, moved to deleted state, replicated, and filtered independently from the bucket records that keep reverse alias hints.

## Important APIs, types, and functions
`BucketAlias` has `name` and `state: Lww<CancelingOption<Uuid>>`. `BucketAlias::new`, `is_deleted`, and `name` construct and inspect alias entries. `Crdt` merge delegates to LWW state. `Entry<EmptyKey, String>` stores all aliases in one partition keyed by alias name. `BucketAliasTable` names the table `bucket_alias` and filters through `DeletedFilter`. `is_valid_bucket_name` enforces Garage's S3 bucket-name rules with optional punycode support, and `INVALID_BUCKET_NAME_MESSAGE` is the client-facing validation text.

## Control flow
Admin and S3 bucket paths use helper methods in `helper/locked.rs` to validate names, read/update `BucketAlias`, and coordinate alias timestamps with reverse maps in `Bucket`. Fast bucket resolution in `helper/bucket.rs` reads the local alias table, while admin paths do quorum reads. The validator checks length, allowed lowercase DNS characters, start/end characters, IP-address shape, `xn--` labels unless configured, and the `-s3alias` suffix.

## State and persistence behavior
The table's initial format is versioned by Garage's migration system. Alias deletion is represented by `CancelingOption(None)` rather than removing the row. LWW timestamps are chosen by locked helper code to be greater than both the alias-table and reverse-map timestamps, giving paired updates deterministic merge behavior.

## Dependencies and integration points
This module depends on `garage_table` CRDT/table traits and `garage_util::data::Uuid`. It integrates with `BucketHelper` resolution, `LockedHelper` alias mutation, bucket creation/deletion admin flows, and the user-facing S3 bucket name constraints.

## Risks and edge cases
The validator intentionally allows dots and rejects IP-looking names, but TLS virtual-host semantics around dotted bucket names still need handling elsewhere. Concurrent alias creation on different API nodes is only partially mitigated by local locking in `LockedHelper`; cross-node races can still create temporary inconsistencies. Punycode validation is controlled by configuration and is stricter for `.xn--` labels than the base AWS rule.

## Test signals
There are no local tests. Useful coverage would include every bucket-name rejection branch, punycode enabled/disabled behavior, LWW alias deletion/recreation, and paired alias/bucket reverse-map repair.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/bucket_alias_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/bucket_table.rs -->
# sources/object-store/garage/src/model/bucket_table.rs

## Purpose
This file defines Garage's replicated bucket metadata model. It stores bucket identity, deletion state, access-key permissions, global/local alias reverse indexes, website configuration, CORS rules, lifecycle rules, and quotas as CRDT state.

## Important APIs, types, and functions
`Bucket` contains an immutable UUID and `crdt::Deletable<BucketParams>`. `BucketParams` holds creation time, `authorized_keys`, alias reverse maps, website/CORS/lifecycle configs, and `BucketQuotas`. Public config types include `WebsiteConfig`, `RedirectAll`, `RoutingRule`, `RedirectCondition`, `Redirect`, `CorsRule`, `LifecycleRule`, `LifecycleFilter`, and `LifecycleExpiration`. `parse_lifecycle_date` accepts `YYYY-MM-DD` or midnight `YYYY-MM-DDTHH:MM:SSZ`. `Bucket::new`, `present`, `is_deleted`, `params`, `params_mut`, `authorized_keys`, `aliases`, and `local_aliases` are core accessors. `BucketTable` uses table name `bucket_v2`.

## Control flow
Bucket creation builds `BucketParams::new` with current millisecond creation time and empty CRDT maps. Mutations are generally performed through `LockedHelper`, which modifies both bucket reverse maps and the authoritative alias/key tables. `BucketParams::merge` keeps the earliest creation date, merges permissions and aliases, and LWW-merges configs/quotas.

## State and persistence behavior
The current format is `v2` with marker `G2bkt`; it migrates from `v08` by expanding website config with redirect/routing placeholders while preserving old permissions, aliases, CORS, lifecycle, and quota values. Deleted buckets retain their UUID and tombstone state. Reverse alias maps are advisory, used for listing and repair rather than as the authoritative source for global alias lookup.

## Dependencies and integration points
This table is fully replicated by `Garage::new`. It feeds S3 bucket authorization, admin bucket APIs, website/CORS/lifecycle handlers, lifecycle worker policy lookup, quota checks, object listing by bucket UUID, K2V bucket emptiness checks, and `LockedHelper::repair_aliases`.

## Risks and edge cases
Reverse alias state can diverge from `bucket_alias_table` or key-local aliases if paired writes partially fail or concurrent nodes mutate aliases; `repair_aliases` exists to correct this. Lifecycle date parsing rejects non-midnight datetimes, and invalid persisted lifecycle dates are only warned about by the lifecycle worker. Quota CRDTs use `AutoCrdt` with warning on differences, so concurrent conflicting quota edits require scrutiny.

## Test signals
No direct tests are present. Good signals should cover migration from v08, lifecycle date parsing, CRDT merge of permissions/configs, deletion tombstones, alias reverse-map repair, and lifecycle/quotas integration.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/bucket_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/garage.rs -->
# sources/object-store/garage/src/model/garage.rs

## Purpose
This file constructs the full Garage model layer: configuration, metadata database, membership system, block manager, metadata tables, counters, lifecycle persistence, optional K2V subsystem, and background workers. It is the dependency injection root for model, S3, K2V, block, and table replication components.

## Important APIs, types, and functions
`Garage` owns config, background variables, replication factor, DB, `System`, `BlockManager`, admin/bucket/key tables, bucket mutation mutex, S3 object/MPU/version/block-ref tables, object/MPU counters, lifecycle persister, and optional `GarageK2V`. `Garage::new` performs initialization. `spawn_workers` starts block/table/counter/lifecycle/K2V/snapshot workers. `bucket_helper`, `key_helper`, and `locked_helper` expose helper APIs, with `locked_helper` acquiring the bucket/key mutation mutex. `GarageK2V::new` creates K2V counter, subscription manager, item table, and RPC handler.

## Control flow
Startup ensures metadata and data directories exist, opens the configured DB engine with fsync/cache/map-size options, decodes the 32-byte RPC network secret, parses replication mode, creates membership `System`, builds full-replication parameters for control tables and sharded replication parameters for data metadata, initializes the block manager, then creates all tables in dependency order. S3 tables are wired so object updates feed counters, MPU deletion, version deletion, block-ref deletion, and block refcount changes. K2V is conditionally initialized behind the `k2v` feature.

## State and persistence behavior
All metadata is persisted in the selected Garage DB under `metadata_dir`. Lifecycle worker state is persisted separately through `PersisterShared` named `lifecycle_worker_state`. The model registers a block refcount recalculation closure that scans `block_ref_table`. Auto snapshots are optional and configured by `metadata_auto_snapshot_interval`.

## Dependencies and integration points
This module integrates `garage_db`, `garage_rpc::system`, replication mode parsing, `garage_block::BlockManager`, `garage_table`, `garage_util::background`, config parsing, all model table modules, S3 tables, lifecycle worker, snapshots, and optional K2V RPC. Upper layers use `Garage` as the shared application state.

## Risks and edge cases
Initialization order matters because table update hooks reference other tables. Missing/invalid `rpc_secret`, invalid DB engine, or directory creation failure abort startup. The local `bucket_lock` does not coordinate bucket/key mutations across nodes, which is explicitly documented as a partial mitigation. Auto snapshot interval rejects values under 600 seconds. Feature-gated K2V changes the shape of `Garage` and bucket emptiness behavior.

## Test signals
No direct tests are in this file. Integration tests that start Garage nodes exercise it heavily. Focused tests should cover config error paths, table dependency wiring, worker spawning, snapshot interval validation, and K2V feature-enabled initialization.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/garage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/helper/bucket.rs -->
# sources/object-store/garage/src/model/helper/bucket.rs

## Purpose
This file provides bucket lookup and cleanup helpers around `Garage`. It separates fast local reads used by request hot paths from quorum reads used by admin/control operations, and implements bucket emptiness checks plus incomplete upload cleanup.

## Important APIs, types, and functions
`BucketHelper` wraps `&Garage`. `resolve_global_bucket_fast` and `resolve_bucket_fast` use local table copies. `resolve_global_bucket` and `resolve_bucket` perform quorum table reads. `get_internal_bucket` retrieves a bucket even if deleted; `get_existing_bucket` requires a present bucket. `is_bucket_empty` scans S3 data objects and optional K2V counters. `cleanup_incomplete_uploads` aborts stale uploading object versions.

## Control flow
Bucket names can be a global alias, local key alias, or full hex UUID. Fast functions decode 64-character UUIDs or consult local alias/key state, then local bucket state. Quorum versions use table `get` calls, fetching the key table before interpreting local aliases. Cleanup pages through `object_table` ranges with `ObjectFilter::IsUploading`, creates `ObjectVersionState::Aborted` entries for versions older than the threshold, and inserts those object updates in batches.

## State and persistence behavior
Lookup helpers are read-only. `cleanup_incomplete_uploads` persists object updates that cause `ObjectTable::updated` to cascade version/MPU cleanup through table hooks. `is_bucket_empty` is read-only but uses counters for K2V when enabled, filtering to current non-gateway nodes from cluster layout.

## Dependencies and integration points
The helper depends on bucket, alias, key, object-table, K2V counter, table utility, layout, and time modules. S3 API handlers use fast lookup for normal requests; admin operations use quorum lookup. Lifecycle and bucket-delete paths rely on cleanup/emptiness checks.

## Risks and edge cases
Fast helpers intentionally do not provide read-after-write guarantees. A bucket name that decodes as a 32-byte UUID bypasses alias lookup. `cleanup_incomplete_uploads` computes `now_msec() - older_than`, so a duration larger than current epoch milliseconds would underflow. K2V emptiness depends on counter correctness, which can lag if counter update hooks failed.

## Test signals
No direct tests are present. Valuable coverage includes UUID-vs-alias resolution, stale local alias behavior, quorum read behavior after mutations, cleanup pagination, abort cascades, and K2V counter-based emptiness.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/helper/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/helper/error.rs -->
# sources/object-store/garage/src/model/helper/error.rs

## Purpose
This file defines model-helper errors used by admin and API helper operations. It wraps internal Garage errors, exposes bad-request and not-found conditions, and provides small conversion helpers for mapping `Option`/`Result` failures into client-meaningful errors.

## Important APIs, types, and functions
`Error` variants are `Internal(GarageError)`, `BadRequest`, `InvalidBucketName`, `NoSuchAccessKey`, and `NoSuchBucket`. `From<garage_net::error::Error>` maps network failures into `GarageError::Net`. `OkOrBadRequest` is implemented for `Result<T, E: Display>` and `Option<T>` to attach bad-request context.

## Control flow
Helper functions use `?` to convert low-level errors into `Internal`, and use explicit variants for access key or bucket lookup failures. Validation paths call `ok_or_bad_request` when parser/validation failure should be exposed as a bad client request rather than an internal error.

## State and persistence behavior
This module is stateless and serializable/deserializable. Its error enum is part of helper/RPC boundaries where model-layer errors may cross process boundaries.

## Dependencies and integration points
It depends on `thiserror`, `serde`, `garage_util::error::Error`, and `garage_net::error::Error`. It is imported by bucket, key, locked, K2V seen/rpc, and admin helper paths.

## Risks and edge cases
Overusing `Internal` for user input failures can leak operational messages or produce wrong HTTP status mapping in upper layers. The network conversion collapses all net errors into internal errors, which is appropriate for helper RPCs but may hide retriable/remote failure distinctions. `OkOrBadRequest` formats underlying errors directly into the response.

## Test signals
No local tests. Coverage should verify serialization stability, conversion mapping, and upper-layer HTTP/API error translation for each variant.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/helper/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/helper/key.rs -->
# sources/object-store/garage/src/model/helper/key.rs

## Purpose
This file provides small key-table lookup helpers around `Garage`, separating internal retrieval from user-facing existing-key retrieval.

## Important APIs, types, and functions
`KeyHelper` wraps `&Garage`. `get_internal_key` returns a `Key` table entry even if deleted and treats missing rows as internal errors. `get_existing_key` returns only non-deleted keys and maps missing/deleted rows to `Error::NoSuchAccessKey`.

## Control flow
Both methods perform quorum reads through `key_table.get(&EmptyKey, key_id).await`. The internal variant uses `ok_or_message`, while the existing variant filters `!state.is_deleted()`.

## State and persistence behavior
This module is read-only. It observes the fully replicated key table and does not mutate access-key state.

## Dependencies and integration points
It depends on `garage_table::util::EmptyKey`, `garage_util::error::OkOrMessage`, helper errors, `Garage`, and `Key`. `LockedHelper` uses it for alias/permission mutations and delete flows.

## Risks and edge cases
The distinction between missing internal key and deleted key is important: internal mutation/repair flows need tombstones, while user-facing operations should hide deleted keys. Callers pass `String` references rather than `str`, matching table key types but requiring ownership conversions elsewhere.

## Test signals
No direct tests. Useful tests should cover existing/deleted/missing keys and helper integration in permission and local-alias mutation paths.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/helper/key.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/helper/locked.rs -->
# sources/object-store/garage/src/model/helper/locked.rs

## Purpose
This file implements serialized helper operations for mutating bucket aliases, key-local aliases, key permissions, and key deletion. It is the coordination layer that updates both sides of denormalized relationships in bucket, key, and alias tables.

## Important APIs, types, and functions
`LockedHelper` holds `&Garage` and an optional `tokio::sync::MutexGuard`. It exposes `bucket()` and `key()` helper accessors; global alias methods `set_global_bucket_alias`, `unset_global_bucket_alias`, `purge_global_bucket_alias`; local alias methods `set_local_bucket_alias`, `unset_local_bucket_alias`, `purge_local_bucket_alias`; `set_bucket_key_permissions`; `delete_key`; and `repair_aliases`.

## Control flow
Alias setters validate bucket names, fetch relevant bucket/key/alias rows, reject collisions, compute an alias timestamp via `increment_logical_clock_2`, then write both authoritative and reverse-map records with the same timestamp. Unset operations refuse to leave a bucket with no aliases and remove both sides. Purge operations are tolerant cleanup paths for deletion/repair. Permission updates fetch both bucket and key, advance timestamps against both current permission maps, and write matching permission CRDT entries to both tables. `delete_key` purges local aliases, removes bucket permissions, then marks the key deleted. `repair_aliases` runs a DB transaction that scans buckets, alias table, and key table, removes aliases pointing to deleted buckets, reconstructs reverse maps, and queues table updates.

## State and persistence behavior
All public mutation methods write replicated metadata tables. The mutex is local to one Garage process and does not serialize concurrent API nodes. Timestamps are used as causality barriers so CRDT merges converge across paired table updates. `repair_aliases` writes directly through table queue-insert APIs inside a DB transaction and logs each repaired inconsistency.

## Dependencies and integration points
It depends on bucket alias validation/table, bucket/key helpers, bucket/key tables, permission CRDTs, Garage DB transactions, table utilities, and logical clocks. Admin bucket/key APIs should acquire `Garage::locked_helper` before calling these methods.

## Risks and edge cases
The file explicitly documents unresolved cross-node races for bucket/alias mutations. Partial failures between paired inserts can leave reverse maps stale until repair. Unalias operations reject removing the last alias but races can invalidate that check. `delete_key` iterates existing aliases/permissions and performs nested async mutations, so failures can leave a partially cleaned key. `repair_aliases` trusts local DB state and should be run carefully on inconsistent clusters.

## Test signals
No direct tests in this subset. High-value tests should cover global/local alias collision, last-alias rejection, timestamp monotonicity, deleted bucket/key permission denial, partial repair scenarios, and concurrent same-alias operations.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/helper/locked.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/helper/mod.rs -->
# sources/object-store/garage/src/model/helper/mod.rs

## Purpose
This file is the module index for Garage model helpers.

## Important APIs, types, and functions
It declares `bucket`, `error`, `key`, and `locked` submodules. The actual APIs are `BucketHelper`, helper `Error`, `KeyHelper`, and `LockedHelper`.

## Control flow
There is no runtime control flow in this module. It only makes helper modules available to the crate.

## State and persistence behavior
No state is stored here. Persistence behavior is implemented in the submodules.

## Dependencies and integration points
`garage.rs` exposes helper constructors through `Garage::bucket_helper`, `Garage::key_helper`, and `Garage::locked_helper`, relying on this module tree.

## Risks and edge cases
The main risk is public module organization: renaming or removing exports breaks callers throughout admin/S3/K2V code. There are no behavioral edge cases in the file itself.

## Test signals
No direct tests are needed beyond compilation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/helper/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/index_counter.rs -->
# sources/object-store/garage/src/model/index_counter.rs

## Purpose
This file implements generic eventually replicated counters for indexed metadata tables. It lets tables such as objects, multipart uploads, and K2V items maintain bucket/partition-level counts and byte totals, while using per-node local counter state to avoid non-commutative increments in the global table.

## Important APIs, types, and functions
`CountedItem` defines counter table name, counter partition/sort keys, and `counts()`. `CounterEntry<T>` is the replicated global row mapping metric names to `CounterValue`. `CounterValue` stores per-node `(timestamp, value)` entries. `CounterTable<T>` is a sharded table schema. `IndexCounter<T>` owns the local DB tree and replicated counter table. `IndexCounter::count` updates local counters transactionally when an item changes. `offline_recount_all` zeros old local counters and recounts all entries from a source table. `filtered_values` collapses per-node values, optionally filtering to current layout nodes.

## Control flow
Table `updated` hooks call `IndexCounter::count(tx, old, new)`. The method computes metric deltas by subtracting old counts and adding new counts, loads or creates a local counter row, advances each metric timestamp using `max(previous + 1, now_msec())`, persists the local row, converts it into a global `CounterEntry`, and queues replication. Query-side filtering keeps one value per metric by taking the maximum value among selected nodes.

## State and persistence behavior
Local counters live in DB trees named `local_counter_v2:<COUNTER_TABLE_NAME>`. Global counters live in sharded replicated tables named by `CountedItem::COUNTER_TABLE_NAME`. Tombstones are entries whose selected values are all zero. `offline_recount_all` mutates local and global counter rows in batches of roughly 1000 entries, first zeroing all existing counters and then rebuilding from the counted table.

## Dependencies and integration points
It depends on Garage DB transactions, table replication, CRDT traits, migration codecs, cluster layout helpers, time, and background runners. `Object`, `MultipartUpload`, and `K2VItem` implement `CountedItem`; `Garage::new` creates corresponding counters and table hooks.

## Risks and edge cases
Counter correctness is best-effort: table hooks log and continue on counter failures, so displayed indexes can drift until offline recount. Taking the maximum per-node value assumes local node counters are independent replicated observations, but decommissioned or gateway nodes must be filtered by layout. Recount is an offline repair path and can be expensive. Timestamp monotonicity relies on local persisted timestamps and millisecond time.

## Test signals
No local tests. Useful tests should cover delta calculation, merge conflict resolution by timestamp, filtering by live nodes, tombstone filtering, hook failure behavior, and offline recount against object/MPU/K2V tables.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/index_counter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/causality.rs -->
# sources/object-store/garage/src/model/k2v/causality.rs

## Purpose
This file implements K2V causality tokens using vector clocks. The token records which per-node versions have been seen by a client so later writes/deletes can discard causally older values while preserving concurrent conflicts.

## Important APIs, types, and functions
`K2VNodeId` is a `u64` abbreviation of a Garage UUID. `VectorClock` is `BTreeMap<K2VNodeId, u64>`. `make_node_id` uses the first eight bytes of a node UUID. `vclock_gt` checks if one clock has any component greater than another; `vclock_max` merges clocks by max. `CausalContext` wraps a vector clock and exposes `new`, `serialize`, `parse`, and `is_newer_than`.

## Control flow
Serialization flattens sorted `(node,time)` pairs into u64s, prepends an XOR checksum, and encodes bytes using URL-safe base64 without padding. Parsing validates byte length, reconstructs the map, recomputes the checksum, and returns `None` on malformed tokens.

## State and persistence behavior
The structure is stored in K2V items and exposed as an API token string. It is deterministic because `BTreeMap` orders entries. The checksum is only corruption detection, not authentication.

## Dependencies and integration points
It depends on `base64`, `serde`, and `garage_util::data::Uuid`. `K2VItem::update`, polling APIs, range seen markers, and K2V clients use these tokens to express causal context.

## Risks and edge cases
`make_node_id` truncates 256-bit node IDs to 64 bits, so collisions are possible in theory. `vclock_gt` means "has some newer component," not a full partial-order domination check. The XOR checksum is weak against intentional tampering, so API authorization must not rely on it. Very large clocks inflate headers/tokens.

## Test signals
`test_causality_token_serialization` verifies round-trip for a nontrivial vector clock. Additional tests should cover invalid base64, bad lengths, checksum mismatch, empty clocks, and collision behavior assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/causality.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/item_table.rs -->
# sources/object-store/garage/src/model/k2v/item_table.rs

## Purpose
This file defines the K2V item CRDT table. Each item stores dotted version-vector state per storage node, supports concurrent values and deletes, notifies poll subscribers, and maintains K2V index counters.

## Important APIs, types, and functions
Constants `ENTRIES`, `CONFLICTS`, `VALUES`, and `BYTES` name metrics. `K2VItem` stores `K2VItemPartition`, sort key, and a map of `K2VNodeId` to `DvvsEntry`. `DvvsEntry` has `t_discard` and timestamped `DvvsValue` list. `DvvsValue` is `Value(Vec<u8>)` or `Deleted`. `K2VItem::update`, `causal_context`, `values`, `with_raw_items`, `DvvsEntry::from_raw`, and CRDT merge implementations are central. `K2VItemTable` hooks counters and subscriptions. `ItemFilter` supports tombstone exclusion and conflicts-only queries.

## Control flow
Writes apply an optional causal context by raising each node's discard timestamp, discard obsolete values, choose a new local timestamp above both previous local time and provided node timestamp, and append the new value/delete. Merge combines node entries, merges timestamp-ordered value lists without duplicates, takes max discard time, and discards obsolete values. Table updates first adjust the index counter, then notify subscribers of new entries.

## State and persistence behavior
The initial table format stores DVVS state in replicated sharded metadata table `k2v_item`. A tombstone is an item whose visible values are all `Deleted`. Counters aggregate live entries, conflicts, value count, and byte totals by bucket and partition key. Partition hashing uses Blake2b over bucket UUID and partition key.

## Dependencies and integration points
It depends on Garage DB, table CRDTs, index counters, K2V causality and subscriptions. `GarageK2V` creates this table and its counters; `K2VRpcHandler` performs writes and polls; API handlers use filters for listing conflicts/data.

## Risks and edge cases
Visible values are deduplicated by value equality, so identical concurrent values collapse for clients while clocks still retain provenance. The merge assumes `values` are timestamp-sorted; malformed persisted state could violate it. Counter failures are logged but ignored. A delete is just another value unless its causal context discards earlier values, so clients must supply correct tokens to overwrite.

## Test signals
`test_dvvsentry_merge_simple` covers a basic discard/merge case. More tests should cover concurrent values, deletes with/without causal context, tombstone filtering, counter counts, partition hash stability, and subscriber notifications.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/item_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/mod.rs -->
# sources/object-store/garage/src/model/k2v/mod.rs

## Purpose
This file declares the K2V model submodules.

## Important APIs, types, and functions
It exports `causality`, `seen`, `item_table`, `rpc`, and `sub`. These modules implement vector-clock tokens, range seen markers, the K2V item table, RPC insert/poll logic, and subscription management.

## Control flow
There is no runtime logic in this file.

## State and persistence behavior
No state is stored here. K2V state is in `item_table`, local timestamp DB trees in `rpc`, and transient subscriptions in `sub`.

## Dependencies and integration points
The module is feature-gated from `model/lib.rs` and `garage.rs` by the `k2v` feature.

## Risks and edge cases
Changing module visibility or names affects the K2V API, Garage initialization, and tests.

## Test signals
Compilation with and without the `k2v` feature is the primary signal for this file.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/rpc.rs -->
# sources/object-store/garage/src/model/k2v/rpc.rs

## Purpose
This file implements K2V-specific RPCs for routing writes and long-poll reads to the storage nodes responsible for each K2V partition. It keeps vector clocks small by generating write timestamps on a responsible storage node rather than at arbitrary API ingress nodes.

## Important APIs, types, and functions
`K2VRpc` includes insert, batch insert, poll item, poll range, and response variants. `InsertedItem` carries partition/sort/context/value. `K2VRpcHandler` owns `System`, item table, a mutex-protected local timestamp tree, endpoint, and subscription manager. Public methods are `new`, `insert`, `insert_batch`, `poll_item`, and `poll_range`. Internal methods handle insert/batch, `local_insert`, item/range polling, and range scans.

## Control flow
`insert` computes storage nodes for the partition hash and sends `InsertItem` to all candidates with quorum 1. `insert_batch` groups items by identical responsible node set and sends batch RPCs concurrently. Insert handling serializes local timestamp updates with a mutex, calls `update_entry_with`, advances the local timestamp stored under `b"timestamp"`, and propagates changed items through the item table. `poll_item` sends to all responsible nodes with read quorum and merges returned items until timeout. `poll_range` decodes/restricts the seen marker, sends individual calls to all nodes, waits for quorum plus a short extra delay or timeout, merges returned items, updates the seen marker, and returns `None` only when a previous marker existed and no new items were found.

## State and persistence behavior
The local timestamp tree `k2v_local_timestamp` persists each node's K2V logical time. Item updates persist through `k2v_item`. Poll subscriptions are transient in memory and wake local RPC handlers when table updates arrive. Range seen markers are client-provided/returned strings and not persisted server-side.

## Dependencies and integration points
This module depends on Garage RPC endpoints, request strategies, table replication, table local stores, DB transactions, K2V causality/seen/sub/item modules, and helper errors. It integrates with `GarageK2V` initialization and K2V API request handlers.

## Risks and edge cases
Insert quorum 1 means writes are accepted after one responsible node timestamps them, relying on table replication afterward. If the chosen node fails before propagation, availability/consistency depends on table durability. `poll_range_read_range` breaks on the first item outside `range.matches`; this is correct for end bounds but can prematurely stop for a prefix filter if the start point is not prefix-aligned. Long polls use local subscriptions and can miss events only if subscription timing and initial scan are wrong; the code subscribes before scanning when a seen marker exists. Invalid seen markers map to bad-request helper errors.

## Test signals
No direct tests here, but previous Garage K2V integration tests likely exercise batch, item, range, and poll flows. Focused tests should cover quorum error thresholds, range prefix scanning, timeout behavior, seen-marker shrinking, local timestamp monotonicity, and batch grouping.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/rpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/seen.rs -->
# sources/object-store/garage/src/model/k2v/seen.rs

## Purpose
This file implements `RangeSeenMarker`, the K2V poll-range continuation token. It compactly records globally seen per-node timestamps plus item-specific vector clocks so subsequent polls can return only new/unseen items.

## Important APIs, types, and functions
`RangeSeenMarker` stores a global `vector_clock` and per-sort-key item clocks. `new`, `restrict`, `mark_seen_node_items`, `canonicalize`, `encode`, `decode`, `decode_helper`, and `is_new_item` are the main methods.

## Control flow
Before a range poll, `restrict` narrows item-specific markers to the requested start/end/prefix. When node responses arrive, `mark_seen_node_items` raises the global clock for values produced by that node and records item-specific clocks for items still newer than the global clock. `canonicalize` drops per-item entries covered by the global clock. Encoding serializes with Garage's nonversioned msgpack helper, compresses with zstd, and base64-encodes. Decoding reverses that and returns `None` on malformed input.

## State and persistence behavior
Seen markers are client-visible continuation strings, not server-side state. They can grow with sparse per-item clocks but canonicalization keeps them smaller when full node ranges have been observed.

## Dependencies and integration points
It depends on K2V causality, item table, poll ranges, zstd, base64, Garage encode helpers, and helper bad-request conversion. `K2VRpcHandler::poll_range` uses it to filter responses and return new markers.

## Risks and edge cases
The marker is not authenticated; malicious clients can ask to skip data by supplying a broad marker. This is acceptable only if markers are treated as client-controlled cursors. Prefix restriction removes item-specific markers outside the prefix but keeps the global vector clock, which can still suppress old items from the same nodes. Large conflict sets can produce large tokens despite compression.

## Test signals
No local tests. Useful tests should cover encode/decode, range restriction for start/end/prefix, canonicalization, malicious/invalid strings, and `is_new_item` against global and per-item clocks.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/seen.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/sub.rs -->
# sources/object-store/garage/src/model/k2v/sub.rs

## Purpose
This file implements in-memory subscription tracking for K2V long polling. It lets local RPC handlers wait for changes to one item or to an entire partition.

## Important APIs, types, and functions
`PollKey` identifies one K2V item by partition and sort key. `PollRange` describes a partition range with optional prefix/start/end. `SubscriptionManager` wraps a mutex-protected `SubscriptionManagerInner` containing item and partition broadcast senders. Methods include `new`, `subscribe_item`, `subscribe_partition`, and `notify`. `PollRange::matches` checks whether an item belongs to a requested range.

## Control flow
Polling code subscribes before or during local reads. Table update hooks call `notify`, which sends a clone of the item to matching item and partition broadcast channels, removing channels that have no receivers. Range poll handlers wait on partition channels until a matching unseen item arrives.

## State and persistence behavior
Subscriptions are transient process-local memory. They are not replicated or persisted; each storage node manages waiters for its local RPC handlers.

## Dependencies and integration points
It depends on `tokio::sync::broadcast`, `std::sync::Mutex`, and K2V item types. `K2VItemTable::updated` calls `notify`, and `K2VRpcHandler` subscribes for poll item/range.

## Risks and edge cases
Broadcast channel capacity is 8, so slow consumers can lag and receive errors; polling code treats `recv` errors as RPC errors. `notify` holds a synchronous mutex while sending; broadcast send is nonblocking but clone cost grows with item size. `PollRange::matches` uses lexicographic string bounds and prefix checks; callers must build start/end consistently.

## Test signals
No direct tests. Coverage should include item and partition subscription delivery, channel cleanup after receivers drop, lag behavior, and range matching with prefix/start/end combinations.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/k2v/sub.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/key_table.rs -->
# sources/object-store/garage/src/model/key_table.rs

## Purpose
This file defines the replicated S3 access-key metadata table. It stores key IDs, secrets, names, optional expiration, create-bucket privileges, bucket permissions, and key-local bucket aliases.

## Important APIs, types, and functions
`Key` stores `key_id` and `crdt::Deletable<KeyParams>`. `KeyParams` includes creation time, immutable `secret_key`, LWW `name`, LWW optional `ExpirationTime`, LWW `allow_create_bucket`, CRDT map of authorized buckets, and LWW map of local aliases. `Key::new` generates Garage-style key IDs and random secrets. `Key::import` validates user-provided IDs/secrets. `delete`, `is_deleted`, `params`, `params_mut`, `bucket_permissions`, `allow_read`, `allow_write`, `allow_owner`, and `KeyParams::is_expired` are core operations. `KeyTable` uses `KeyFilter` for deleted and prefix/name matching.

## Control flow
New keys are created with ID prefix `GK`, 12 random bytes hex-encoded, and 32 random bytes hex-encoded as secret. Imported keys enforce minimum ID/secret lengths and ASCII character constraints. Permission checks read the CRDT map and default to no permissions. Search filters match non-deleted key prefixes or exact lowercased names.

## State and persistence behavior
Current format `G2key` migrates from v08 by adding optional creation timestamp and expiration. Deletes are tombstones via `Deletable`. Secret keys are stored in plaintext metadata, so metadata DB access is sensitive. Local aliases and authorized bucket maps are denormalized with bucket table state by `LockedHelper`.

## Dependencies and integration points
It depends on Garage CRDT/time/data/table modules and `BucketKeyPerm`. `Garage::new` creates a fully replicated `key_table`; S3 auth uses keys; admin APIs and `LockedHelper` mutate keys; bucket resolution checks local aliases.

## Risks and edge cases
Plaintext secret persistence requires protecting metadata snapshots/backups. `Key::import` accepts any graphic ASCII secret of length >=16, not necessarily high entropy. Concurrent permission/local-alias edits rely on timestamps in nested CRDTs. Deleted keys may retain historical state in tombstones until compaction/migration.

## Test signals
No direct tests in this file. Useful coverage includes generated/imported key validation, expiration checks, filter matching, permission defaults, v08 migration, and paired mutation with bucket table.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/key_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/lib.rs -->
# sources/object-store/garage/src/model/lib.rs

## Purpose
This file is the crate root for `garage_model`. It declares exported model modules and enables tracing macros.

## Important APIs, types, and functions
It exports `permission`, `index_counter`, admin/bucket/key tables, optional `k2v`, `s3`, `garage`, `helper`, and `snapshot`.

## Control flow
There is no runtime control flow. Conditional compilation exposes `k2v` only when the feature is enabled.

## State and persistence behavior
No state is stored here. State and persistence are implemented in the exported modules.

## Dependencies and integration points
Other Garage crates import table types, `Garage`, helpers, S3 metadata models, and optional K2V models through this crate root.

## Risks and edge cases
Changing module names or feature gates is a public crate API change. The `#[macro_use] extern crate tracing;` pattern makes logging macros available throughout the crate.

## Test signals
Compilation under normal and `k2v` feature configurations is the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/permission.rs -->
# sources/object-store/garage/src/model/permission.rs

## Purpose
This file defines CRDT-compatible permission and expiration primitives shared by access keys, buckets, and admin tokens.

## Important APIs, types, and functions
`BucketKeyPerm` stores a timestamp and read/write/owner booleans. Constants `NO_PERMISSIONS` and `ALL_PERMISSIONS` seed common permission states. `is_any` checks whether any permission is granted. Its `Crdt` merge chooses the greater timestamp; if timestamps tie but values differ, it logs a warning and merges to the most restrictive permission set. `ExpirationTime(pub u64)` merges to the earliest timestamp.

## Control flow
Permission mutation code in `LockedHelper` advances timestamps before writing paired bucket/key maps. CRDT merges resolve concurrent permission states using the timestamp. Expiration checks in key/token params compare current time to `ExpirationTime.0`.

## State and persistence behavior
These types are serialized into bucket, key, and admin token table records. Permission timestamps are logical clocks, not just wall-clock timestamps. Expiration times use millisecond timestamps.

## Dependencies and integration points
It depends on `serde` and `garage_util::crdt`. `BucketKeyPerm` is embedded in `BucketParams.authorized_keys` and `KeyParams.authorized_buckets`; `ExpirationTime` is embedded in key and admin token params.

## Risks and edge cases
Equal timestamp conflicts intentionally reduce permissions, which is safe but may surprise admins after concurrent writes. Callers must use logical-clock helpers to avoid equal timestamps for intended updates. Expiration merge chooses the minimum, so concurrent changes converge toward earlier expiration.

## Test signals
No direct tests. Useful tests should cover permission timestamp ordering, equal-timestamp conflict restriction, expiration minimum merge, and paired bucket/key permission updates.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/permission.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/s3/block_ref_table.rs -->
# sources/object-store/garage/src/model/s3/block_ref_table.rs

## Purpose
This file defines the block-reference metadata table connecting stored data blocks to object versions. It drives block manager refcounts when references are created or deleted.

## Important APIs, types, and functions
`BlockRef` stores block hash, version UUID, and CRDT bool deletion state. It implements `Entry<Hash, Uuid>`, `is_tombstone`, and CRDT merge. `BlockRefTable` holds a `BlockManager` and implements `updated` to call `block_incref` or `block_decref`. `block_ref_recount_fn` returns a `CalculateRefcount` closure. `calculate_refcount` scans table rows for a block and counts non-deleted refs.

## Control flow
When a block ref transitions from deleted/absent to live, `updated` increments the block manager refcount in the same DB transaction. When it transitions from live to deleted/absent, it decrements. Version deletion cascades enqueue deleted `BlockRef` records from `version_table.rs`.

## State and persistence behavior
Rows are sharded by block hash and sorted by version UUID. Deletion is a CRDT bool tombstone. Refcount changes affect block manager persistent/local state via transaction hooks. Recount can recompute expected refcount from table contents for repair.

## Dependencies and integration points
It depends on Garage DB, table replication/schema traits, `BlockManager`, `CalculateRefcount`, and version table deletion cascades. `Garage::new` registers recount closure with the block manager.

## Risks and edge cases
If table hook errors are ignored upstream or a repair is needed, block refcounts can diverge from metadata. `calculate_refcount` assumes table keys for one hash are contiguous and decodable. Deleting a version with duplicate block hashes still creates per-version refs, so refcount semantics are per live version reference.

## Test signals
No direct tests. Good tests should cover incref/decref transitions, CRDT deletion merges, recount scanning, and version-delete cascade integration.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/s3/block_ref_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/s3/lifecycle_worker.rs -->
# sources/object-store/garage/src/model/s3/lifecycle_worker.rs

## Purpose
This file implements the background worker that applies S3 lifecycle rules: expiring current objects by inserting delete markers and aborting stale incomplete multipart uploads.

## Important APIs, types, and functions
`LifecycleWorkerPersisted` stores `last_completed`. `LifecycleWorker` owns `Garage`, current `State`, and persister. `State` is `Completed(date)` or `Running` with scan position, counters, and cached last bucket. `register_bg_vars` exposes last completed date. Worker methods implement `name`, `status`, `work`, and `wait_for_work`. `process_object`, `check_size_filter`, `midnight_ts`, `next_date`, and `today` implement lifecycle decisions.

## Control flow
On startup, the worker compares persisted completion date to today and either idles or starts a scan. `work` processes up to 100 object-table rows per run using raw DB cursor position. It skips buckets without enabled lifecycle rules, reusing `last_bucket` for consecutive objects. For expiration rules, it finds the latest data version, checks prefix, size, and date filters, then queues an object update containing a new delete marker. For abort rules, it queues aborted states for old uploading versions. When the scan ends, it persists `last_completed` and becomes idle until the next local/UTC midnight.

## State and persistence behavior
Worker progress is in memory during a day; only the completed date is persisted. Object expirations and MPU aborts persist as object-table updates, which trigger normal object/version/MPU cascades. The worker uses either local timezone or UTC based on config.

## Dependencies and integration points
It depends on background worker traits, chrono, persister, bucket lifecycle config, object table, Garage DB transactions, and object-table update hooks. `Garage::spawn_workers` starts it and registers bg variables.

## Risks and edge cases
If Garage restarts mid-scan, the day restarts from the beginning because only completed date is persisted. Lifecycle `AtDate` strings are validated at processing time; invalid persisted dates log warnings. The worker inserts delete markers rather than deleting all versions, matching versioning semantics but requiring upper layers to interpret latest delete marker. `status` has a formatting typo in `"Multipart uploads aborted: { }"`. Timezone midnights can be ambiguous for local DST and use `.single().expect`.

## Test signals
No direct tests here. Useful tests should cover date math, prefix/size filters, expiration delete-marker insertion, MPU abort insertion, restart behavior, invalid lifecycle dates, local timezone behavior, and skip-bucket cursor advancement.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/s3/lifecycle_worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/s3/mod.rs -->
# sources/object-store/garage/src/model/s3/mod.rs

## Purpose
This file declares S3 metadata submodules for the Garage model crate.

## Important APIs, types, and functions
It exports `block_ref_table`, `mpu_table`, `object_table`, `version_table`, and `lifecycle_worker`.

## Control flow
There is no runtime logic here.

## State and persistence behavior
No direct state. The exported modules define S3 object, multipart, version, block-ref, and lifecycle persistence.

## Dependencies and integration points
`garage.rs` imports these modules to construct S3 metadata tables and workers. S3 API crates import the data models through this module tree.

## Risks and edge cases
Module organization changes affect many S3 code paths.

## Test signals
Compilation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/s3/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/s3/mpu_table.rs -->
# sources/object-store/garage/src/model/s3/mpu_table.rs

## Purpose
This file defines metadata for active and deleted multipart uploads. It tracks uploaded part versions, propagates cleanup to version metadata, and contributes per-bucket MPU counters.

## Important APIs, types, and functions
`MultipartUpload` stores upload UUID, creation timestamp, CRDT deleted flag, CRDT map of `MpuPartKey` to `MpuPart`, and backlink bucket/key. `MpuPartKey` orders by part number then timestamp. `MpuPart` stores version UUID, optional ETag, optional checksum, and optional size. `MultipartUpload::new` and `next_timestamp` are constructors/helpers. `MultipartUploadTable::updated` updates counters and propagates deletions to `VersionTable`. `CountedItem` metrics are `UPLOADS`, `PARTS`, and `BYTES`.

## Control flow
Retries for the same part get unique timestamps and all versions remain until upload deletion. CRDT merge marks deletion dominant: once deleted, parts are cleared. Part merge chooses present/max ETag, size, and checksum values. When an MPU transitions from live to deleted, table update code queues deletion `Version` entries for all previously known part versions.

## State and persistence behavior
The current initial format marker is `G09s3mpu`. Rows are keyed by upload UUID. Deleted rows are tombstones. Counters aggregate active upload count, distinct part numbers, and known part sizes by bucket. Version cleanup is queued transactionally but hook failures are logged and require repair.

## Dependencies and integration points
It depends on object-table checksum types, version table, index counters, Garage DB, and sharded table replication. S3 multipart API paths create/update/delete these rows; object-table completion/abortion also deletes MPU rows.

## Risks and edge cases
`counts` deduplicates part numbers by calling `dedup` without sorting the collected numbers; because `parts.items()` is ordered by `MpuPartKey`, equal part numbers should be adjacent, but that invariant matters. Deletion clears parts after merge, so late part updates lose to deletion. Hook failures can leave orphaned versions. Optional size/checksum fields mean counters may undercount bytes for in-progress parts.

## Test signals
No direct tests in this file. Multipart integration tests should exercise it. Focused tests should cover part ordering, retry timestamps, deletion cascades, counter metrics, and merge dominance of deletion.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/s3/mpu_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/s3/object_table.rs -->
# sources/object-store/garage/src/model/s3/object_table.rs

## Purpose
This file defines the primary S3 object metadata table. It stores object keys, version history, upload state, delete markers, inline/first-block data pointers, object metadata, encryption metadata, checksums, and hooks that cascade cleanup to version and multipart tables.

## Important APIs, types, and functions
`Object` is keyed by bucket UUID and object key and contains sorted `ObjectVersion` entries. `ObjectVersion` has UUID, timestamp, and `ObjectVersionState`: `Uploading`, `Complete`, or `Aborted`. `ObjectVersionData` is `DeleteMarker`, `Inline(meta, bytes)`, or `FirstBlock(meta, hash)`. `ObjectVersionMeta`, `ObjectVersionEncryption`, `ObjectVersionMetaInner`, `ChecksumAlgorithm`, `ChecksumValue`, and `ChecksumType` model headers, SSE-C encrypted metadata, compression flags, ETags, sizes, and checksum semantics. `Object::new`, `add_version`, `versions`, `ObjectVersion::is_uploading`, `is_complete`, `is_data`, `ChecksumValue::algorithm`, CRDT merges, `ObjectTable::updated`, filters, and `CountedItem` are central.

## Control flow
Constructing an object inserts versions sorted by `(timestamp, uuid)`. Merging adds or merges same-key versions, then discards obsolete earlier versions before the latest complete version. State merge makes `Aborted` dominant over local state, `Complete` replace `Uploading`, and complete data merge via `AutoCrdt`. Table updates first update object counters. Then, for old versions absent from the new object or newly aborted, they queue deleted `Version` rows. For old multipart uploading versions that disappear or stop uploading, they queue deleted `MultipartUpload` rows.

## State and persistence behavior
The file contains migrations from v08 to v09, v010, and v2. v09 adds multipart upload flags; v010 introduces encryption metadata and checksum values; v2 adds checksum type. Current object table name is `object`. Tombstone status is only a single delete-marker version. Counters aggregate live object count, unfinished upload count, and bytes by bucket.

## Dependencies and integration points
It depends on Garage DB, table CRDTs, sharded replication, index counters, MPU table, and version table. S3 PUT/GET/DELETE/list/multipart/lifecycle code consumes and mutates this model; version table and block ref table handle data block cleanup.

## Risks and edge cases
Obsolete-version pruning after merge means historical versions before the latest complete state are intentionally removed, so versioning semantics are simplified compared with full S3 version history. Hook failures log and continue, leaving cleanup for repair. Encryption metadata may be encrypted, so callers must handle plaintext vs SSE-C branches. Inline encrypted data is never compressed while block data may be compressed/encrypted depending on flags. The tombstone definition only matches one delete marker; multiple versions with a latest delete marker are not table tombstones.

## Test signals
No direct unit tests in this file, but S3 integration tests cover many paths. Focused tests should cover migrations, version ordering/pruning, state merge precedence, counter metrics, delete cascades to version/MPU tables, checksum type migration, and encrypted metadata handling.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/s3/object_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/s3/version_table.rs -->
# sources/object-store/garage/src/model/s3/version_table.rs

## Purpose
This file defines metadata for the data blocks belonging to a single object or multipart part version. It provides the bridge from object/MPU metadata to block references and block refcount cleanup.

## Important APIs, types, and functions
`Version` stores UUID, CRDT deleted flag, CRDT map of `VersionBlockKey` to `VersionBlock`, and a `VersionBacklink` to either an object bucket/key or multipart upload ID. `VersionBlockKey` orders by part number then offset. `VersionBlock` stores block hash and uncompressed/plain size. `Version::new`, `has_part_number`, and `n_parts` are helpers. `VersionTable::updated` propagates deletion of block refs. v09 migrates from v08 by replacing bucket/key fields with `VersionBacklink::Object`.

## Control flow
When a version is marked deleted after previously being live, the update hook queues deleted `BlockRef` entries for every old block. Version merge makes deletion dominant and clears blocks if deleted; otherwise it merges block maps. `n_parts` reads the last block key's part number and errors if no blocks exist.

## State and persistence behavior
Current format marker is `G09s3v`; table name is `version`; rows are keyed by version UUID. Deleted rows are tombstones. Block maps are cleared after deletion, but the update hook uses the old live row to propagate block-ref tombstones.

## Dependencies and integration points
It depends on block-ref table, table replication, Garage DB, and error helpers. Object table and MPU table enqueue deleted versions; upload paths create live versions with blocks; block manager cleanup follows from block-ref table hooks.

## Risks and edge cases
If a delete update arrives without local old block data, block-ref deletion propagation may not happen from that node; repair/recount paths are needed. `has_part_number` uses binary search over ordered CRDT map items, relying on `VersionBlockKey` ordering. `n_parts` returns the highest part number, not necessarily a count of contiguous parts.

## Test signals
No direct tests. Useful coverage includes v08 migration, block ordering, delete cascade to block refs, `n_parts` empty/error behavior, and deletion merge dominance.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/s3/version_table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/model/snapshot.rs -->
# sources/object-store/garage/src/model/snapshot.rs

## Purpose
This file implements manual and automatic metadata DB snapshots. It creates snapshot directories/files through the DB engine, keeps only the newest snapshots, and exposes a background worker for periodic snapshots.

## Important APIs, types, and functions
`async_snapshot_metadata` runs blocking snapshot work on a Tokio blocking thread. `snapshot_metadata` acquires a global `SNAPSHOT_MUTEX`, chooses the configured/default snapshot directory, calls `garage.db.snapshot`, and invokes `cleanup_snapshots`. `AutoSnapshotWorker` schedules periodic snapshots with randomized interval. `KEEP_SNAPSHOTS` is 2.

## Control flow
Manual snapshots fail fast if another snapshot is running. Snapshot names are current UTC RFC3339 timestamps. Cleanup reads entries, filters short names, sorts by filename, and deletes all but the two newest. Auto worker first schedules half an interval after startup, then after each successful snapshot schedules `interval * (1.0..1.2)`.

## State and persistence behavior
Snapshots are filesystem artifacts under `metadata_snapshots_dir` or `<metadata_dir>/snapshots`. No metadata table rows are changed. The auto worker keeps scheduling state only in memory.

## Dependencies and integration points
It depends on Garage DB snapshot support, filesystem APIs, background worker traits, rand, chrono, and Garage config. `Garage::spawn_workers` starts it when configured.

## Risks and edge cases
`cleanup_snapshots` constructs deletion paths with `snapshots_dir.join(to_delete.path())`; because `DirEntry::path()` is already a path, this deserves review for path correctness. Cleanup handles only files directly inside snapshot directories before removing the directory, so nested directories could fail. Auto snapshots stop on snapshot errors and reschedule only after success because `work` returns the error.

## Test signals
No local tests. Useful tests should cover lock contention, default/configured directories, retention ordering, directory cleanup, auto scheduling, and the `join(to_delete.path())` path behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/model/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/Cargo.toml -->
# sources/object-store/garage/src/net/Cargo.toml

## Purpose
This manifest defines the `garage_net` crate, Garage's RPC networking library forked from Netapp. It configures package metadata, the library root, optional telemetry, dependencies, dev dependencies, and workspace lints.

## Important APIs, types, and functions
The crate is named `garage_net` version `2.3.0`, with library path `lib.rs`. Feature `telemetry` enables `opentelemetry` and `opentelemetry-contrib`; default features are empty. Dependencies cover async runtime/streams (`tokio`, `tokio-util`, `tokio-stream`, `futures`), serialization (`serde`, `rmp-serde`), crypto/authenticated transport (`sodiumoxide`, `kuska-handshake`), byte buffers, sockets, logging, `arc-swap`, `thiserror`, `rand`, and config helpers.

## Control flow
Cargo uses this manifest to compile the network crate. Feature selection controls whether request telemetry propagation code in `client.rs` is compiled.

## State and persistence behavior
No runtime state. Dependency versions are inherited from the workspace, making the root workspace lock/configuration authoritative.

## Dependencies and integration points
Other Garage crates depend on `garage_net` for `NetApp`, endpoints, messages, priorities, peering, and errors. The manifest integrates with workspace lints and shared dependency versions.

## Risks and edge cases
Because dependencies are workspace-pinned, changes outside this crate can alter network behavior. The optional telemetry feature changes request encoding by adding telemetry IDs but should remain wire-compatible because request headers include a telemetry ID length. Edition is 2018, so syntax choices must remain compatible.

## Test signals
`net/test.rs` is compiled as the crate test module. Manifest-level signals include building with default features and with `--features telemetry`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/bytes_buf.rs -->
# sources/object-store/garage/src/net/bytes_buf.rs

## Purpose
This file implements `BytesBuf`, a chunk-preserving byte buffer used by the network stream utilities to accumulate and split byte streams efficiently without always concatenating chunks.

## Important APIs, types, and functions
`BytesBuf` stores `VecDeque<Bytes>` plus total length. Methods include `new`, `len`, `is_empty`, `extend`, `take_all`, `take_max`, `take_exact`, internal `take_exact_ok`, `into_slices`, `into_bytes`, and `into_stream`. It implements `Default`, `From<BytesBuf> for Bytes`, and `From<Bytes> for BytesBuf`.

## Control flow
`extend` appends non-empty chunks. `take_all` returns empty, the sole chunk, or concatenates multiple chunks into `BytesMut`. `take_max` either drains all data or delegates to exact slicing. `take_exact_ok` pops from the front, slices a larger front chunk, returns an equal chunk directly, or concatenates across multiple chunks.

## State and persistence behavior
State is in-memory only. It preserves chunk ownership with `Bytes` reference-counted slices where possible.

## Dependencies and integration points
It depends on `bytes` and `crate::stream::ByteStream`. Message decode and stream readers use this buffering pattern for framing.

## Risks and edge cases
`take_exact_ok` asserts sufficient length and unwraps front chunks, so callers must check length first. Converting many small chunks to one `Bytes` copies data. `into_stream` emits original slices and consumes the buffer.

## Test signals
`test_bytes_buf` covers append, take-all, take-max, failed exact take, successful exact take, and empty state. Additional tests could cover slicing a larger single front chunk and multi-chunk exact boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/bytes_buf.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/client.rs -->
# sources/object-store/garage/src/net/client.rs

## Purpose
This file implements outgoing client-side NetApp connections. It authenticates to peers, checks protocol/app version tags, starts send/receive loops, tracks in-flight requests, and cancels remote streams when callers drop responses early.

## Important APIs, types, and functions
`ClientConn` stores remote address, peer ID, optional send channel, atomic next request ID, and `inflight` response waiters. `ClientConn::init` performs handshake and loop setup. `close` drops the send channel. `call` encodes a request, registers a oneshot response channel, sends a stream item, waits for and decodes the response. `CancelOnDrop` and `CancelOnDropStream` send cancel frames unless response streams reach EOS.

## Control flow
Initialization performs `kuska_handshake` client auth using network and node keys, wraps the socket in encrypted `BoxStream`, reads the remote version tag, and rejects mismatches. It then registers the connection, spawns send and recv loops, clears in-flight requests on shutdown, and deregisters from `NetApp`. `call` allocates a u32 request ID, optionally starts telemetry, encodes the request path/message/stream, inserts the inflight waiter, sends `SendItem::Stream`, wraps the response stream with cancellation-on-drop, decodes `RespEnc`, and deserializes the typed response.

## State and persistence behavior
All state is transient per TCP connection. In-flight request IDs wrap at u32 and collisions are detected by replacing and erroring the old request. Dropping `query_send` closes the connection.

## Dependencies and integration points
It depends on `NetApp`, endpoint/message encoding, send/recv loops, byte streams, tokio channels, futures, `kuska_handshake`, sodium keys through `NetApp`, and optional OpenTelemetry. `Endpoint::call_streaming` delegates remote calls to `ClientConn::call`.

## Risks and edge cases
The comment notes send-loop shutdown should wait for in-flight responses; currently send loop completion stops recv loop and clears inflight. Request ID collision is possible after wraparound under very long-lived high-volume connections. Cancellation is suppressed only when the response stream returns `None`; callers that do not drain attached streams will cancel server work. Version mismatch aborts connection before request handling.

## Test signals
No direct unit tests in this file; crate-level network tests exercise calls. Useful tests should cover version mismatch, request cancellation, stream-drop cancellation, in-flight clearing on disconnect, telemetry feature builds, and request ID collision behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/endpoint.rs -->
# sources/object-store/garage/src/net/endpoint.rs

## Purpose
This file defines typed RPC endpoints over `NetApp`. It maps application message types and handler objects to path-addressed local handlers and remote calls, with support for attached request/response streams.

## Important APIs, types, and functions
`StreamingEndpointHandler<M>` handles full `Req<M>` and returns `Resp<M>`. `EndpointHandler<M>` is the simpler message-only trait, with a blanket implementation into streaming handling. `Endpoint<M,H>` stores path, owning `NetApp`, and optional handler in `ArcSwapOption`. Public methods are `path`, `set_handler`, `call_streaming`, and `call`. Internal `GenericEndpoint`, `DynEndpoint`, and `EndpointArc` erase endpoint types for dispatch from server connections.

## Control flow
Local calls bypass serialization and invoke the handler directly when target equals local node ID. Remote calls find a `ClientConn` by target node ID, serialize the request, and call over the connection. Incoming encoded requests are decoded by `EndpointArc::handle`, passed to the registered handler, encoded as `RespEnc`, or fail with `NoHandler`.

## State and persistence behavior
Endpoint state is in-memory handler registration. `drop_handler` clears references during shutdown to break cycles. No persistence.

## Dependencies and integration points
It depends on `arc-swap`, futures boxed futures, message encoding, netapp connection maps, and network errors. `NetApp::endpoint` registers endpoints in a path map; server connections use `GenericEndpoint` dispatch.

## Risks and edge cases
The unit handler `()` panics if it receives a request, so client-only endpoints must not be exposed to incoming traffic. `NetApp::endpoint` panics on duplicate paths. Local calls skip serialization, which is efficient but means serialization errors are only observed on remote paths. Handler absence maps to `NoHandler`.

## Test signals
Network tests should cover local and remote endpoint calls, no-handler errors, streaming handlers, and duplicate endpoint path panics.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/error.rs -->
# sources/object-store/garage/src/net/error.rs

## Purpose
This file defines the error type and logging helpers for `garage_net`, plus compact serialization helpers for I/O error kinds in stream error frames.

## Important APIs, types, and functions
`Error` includes I/O, messagepack encode/decode, Tokio join, oneshot receive, handshake, UTF-8, framing, remote I/O error, request ID collision, message, no-handler/shutdown, connection closed, and version mismatch variants. `From` implementations map watch/mpsc send errors into messages. `LogError` logs and discards nested result errors. `u8_to_io_errorkind` and `io_errorkind_to_u8` map selected `io::ErrorKind` values to stable small integers.

## Control flow
Send/recv loops and connection setup use `?` to propagate `Error`. Error frames encode `io::ErrorKind` with `io_errorkind_to_u8`; receivers reconstruct remote errors using `u8_to_io_errorkind`.

## State and persistence behavior
No persistent state. Error kind numeric codes are part of the wire protocol for stream error frames.

## Dependencies and integration points
It depends on `thiserror`, `log`, `rmp-serde`, `tokio`, and `kuska-handshake`. All net modules import this error type.

## Risks and edge cases
Unknown error kinds collapse to `Other`. MPSC/watch send errors lose detail. `Remote` carries kind and string but not structured application error types. Changing numeric mappings would affect compatibility with older peers.

## Test signals
No direct tests. Useful tests should cover error kind round-trips, remote error frame decoding, `LogError` behavior, and version/no-handler mapping in endpoint calls.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/lib.rs -->
# sources/object-store/garage/src/net/lib.rs

## Purpose
This file is the crate root for `garage_net`, a networking library for Garage RPC communication.

## Important APIs, types, and functions
It exports public modules `bytes_buf`, `error`, `stream`, `util`, `endpoint`, `message`, `netapp`, and `peering`, keeps `client`, `recv`, `send`, and `server` private, and re-exports `crate::netapp::*`. Tests are in `test`.

## Control flow
There is no runtime logic in the crate root.

## State and persistence behavior
No state is stored here.

## Dependencies and integration points
Garage RPC and model crates import `NetApp`, node key types, endpoints, messages, priorities, peering manager, and errors through this crate.

## Risks and edge cases
Public/private module boundaries define the crate API. Making send/recv/client internals public or moving re-exports would affect downstream crates.

## Test signals
Crate tests in `net/test.rs` compile through this root. Feature builds with telemetry are also important.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/message.rs -->
# sources/object-store/garage/src/net/message.rs

## Purpose
This file defines the typed request/response model and wire encoding for endpoint messages, including priorities, optional attached byte streams, order tags, and request/response framing inside logical streams.

## Important APIs, types, and functions
`RequestPriority` plus constants `PRIO_HIGH`, `PRIO_NORMAL`, `PRIO_BACKGROUND`, `PRIO_PRIMARY`, and `PRIO_SECONDARY` drive send queue scheduling. `OrderTag`/`OrderTagStream` order related messages. `Message` defines associated response type. `Req<M>` and `Resp<M>` wrap serialized messages and optional `ByteStream`s with builder/accessor methods. `IntoReq` converts messages or existing requests. `AttachedStream` converts fixed bytes or streams into `ByteStream`. `ReqEnc` and `RespEnc` encode/decode path, telemetry ID, message bytes, and attached streams.

## Control flow
Requests serialize messages using named rmp-serde. `ReqEnc::encode` writes priority, path length/path, telemetry length/ID, message length/message, then chains any attached stream. `ReqEnc::decode` reads those fields and exposes the remaining stream. Responses encode a u32 message length/message and optional stream; response errors become a stream yielding an I/O error. `RespEnc::decode` reads the response message and calls `fill_buffer` to detect EOS early, avoiding unnecessary cancellation when the caller ignores an empty stream.

## State and persistence behavior
No persistent state. The byte layout is the internal `garage_net` wire contract between compatible peers. `OrderTag` carries random stream IDs and order numbers only in memory/wire frames.

## Dependencies and integration points
It depends on `bytes`, `rand`, `serde`, `rmp-serde`, futures streams, byte stream utilities, and network errors. Endpoints, client/server connections, and send loops use these structures.

## Risks and edge cases
Path and telemetry lengths are encoded as `u8`, so paths/telemetry IDs above 255 bytes truncate by cast during encode; endpoint paths should remain short. `Req::clone` panics for non-buffer streams. Error responses are encoded as stream errors rather than structured typed response errors. Local endpoint calls may skip serialization and miss encode failures.

## Test signals
No direct tests in this file. Network tests should cover request/response round trips, attached streams, error streams, priority propagation, order tags, clone behavior, path length limits, and empty-stream cancellation defusing.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/message.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/netapp.rs -->
# sources/object-store/garage/src/net/netapp.rs

## Purpose
This file implements `NetApp`, the main authenticated peer-to-peer RPC connection manager. It owns node identity, network key, version tag, connection maps, endpoint registry, listener lifecycle, outgoing connection setup, and connection/disconnection callbacks.

## Important APIs, types, and functions
Type aliases `NodeID`, `NodeKey`, and `NetworkKey` wrap sodiumoxide public/secret/auth keys. `VersionTag` combines `NETAPP_VERSION_TAG` and application version. `HelloMessage` advertises server address/port. `NetApp::new`, `on_connected`, `on_disconnected`, `endpoint`, `listen`, `drop_all_handlers`, `try_connect`, `disconnect`, connection registration callbacks, and `EndpointHandler<HelloMessage>` are key APIs. `set_keepalive` configures TCP keepalive.

## Control flow
`new` derives local node ID from the private key, builds the version tag, creates the Hello endpoint, and registers itself as handler. `listen` binds TCP, accepts connections until `must_exit`, sets keepalive, and spawns `ServerConn::run` tasks collected by a `FuturesUnordered` collector. `try_connect` avoids self/already-connected peers, optionally binds outgoing sockets, applies a 10-second connect timeout, sets keepalive, and initializes `ClientConn`. Client connection registration replaces old outgoing connections, calls callbacks, and sends Hello if listening. Server-side registration waits for Hello before exposing a usable incoming peer address.

## State and persistence behavior
All connection/endpoint state is in memory under `RwLock` or `ArcSwapOption`. There is no persistence; peering reconstructs connections from bootstrap/gossip. Version tags are exchanged per connection.

## Dependencies and integration points
It depends on tokio TCP, socket2 keepalive, sodiumoxide keys, kuska handshake via client/server modules, endpoints/messages, and peering callbacks. `garage_rpc::System` builds on `NetApp`; model K2V and table RPCs create endpoints through it.

## Risks and edge cases
Duplicate endpoint paths panic. `listen` unwraps bind failure, so caller must ensure config validity before spawning. `drop_all_handlers` is needed to break reference cycles on shutdown. Incoming connections are not treated as full peers until Hello provides address/port. Outgoing connection replacement closes the old connection asynchronously. Version tag mismatch prevents mixed incompatible nodes from connecting.

## Test signals
Network integration tests should cover handshake, listener shutdown, local/remote endpoint calls, Hello behavior, duplicate endpoint panic, connection replacement, keepalive failures as warnings, and version mismatch.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/netapp.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/peering.rs -->
# sources/object-store/garage/src/net/peering.rs

## Purpose
This file implements the full-mesh peering strategy for `NetApp`. It tracks known peer addresses, manages outgoing reconnection attempts, sends pings, detects dead links, exchanges peer lists, prunes stale addresses, and publishes peer health information.

## Important APIs, types, and functions
Protocol messages are `PingMessage` and `PeerListMessage`. `KnownAddr` tracks address success/failure. `PeerInfoInternal` stores known addresses, connection state, last ping/seen times, recent ping durations, and failed ping count. Public `PeerInfo` reports state and ping stats. `PeerConnState` is `Ourself`, `Connected`, `Waiting`, `Trying`, or `Abandoned`. `PeeringManager::new`, `run`, `get_peer_list`, `set_ping_timeout_millis`, `ping`, `exchange_peers`, `handle_peer_list`, `try_connect`, `on_connected`, and `on_disconnected` drive the strategy. `pruning_sort_key` ranks addresses for removal.

## Control flow
Construction seeds known hosts with bootstrap peers and our own address, registers ping/peer-list endpoints, and installs NetApp connection callbacks. The run loop every second schedules pings for connected peers and retries for waiting peers. Pings use high priority and a configurable timeout; repeated failures beyond threshold disconnect the peer. Ping hash mismatch triggers peer-list exchange. Retry attempts sort addresses by recent success, shuffle never-successful addresses, try each address with NetApp, update success/failure counters, then prune to at most five addresses.

## State and persistence behavior
Peering state is in-memory only. `public_peer_list` is an `ArcSwap` snapshot for readers. Known-host hash is a sodiumoxide digest of the set of currently up node IDs, not addresses.

## Dependencies and integration points
It depends on `NetApp`, endpoints, message priorities, tokio, sodiumoxide hash, `arc-swap`, and random address shuffling. Garage system membership can query `get_peer_list` for status and use callbacks to keep full mesh connectivity.

## Risks and edge cases
Peer discovery is address gossip, not authenticated membership by itself; the NetApp handshake authenticates node IDs. Address pruning relies on consecutive failures and last success; NAT or changing public addresses can produce churn. Incoming disconnections do not change outgoing state. Failed pings disconnect after `FAILED_PING_THRESHOLD` but actual reconnect timing depends on callback state transitions. `run` sleeps with `tokio::time::sleep` and checks `must_exit.borrow()` only at loop top, so shutdown can wait up to loop delay.

## Test signals
`test_pruning_sort_key` covers stale address pruning priority. Additional tests should cover bootstrap initialization, hash changes, peer exchange, retry state transitions, ping failure disconnects, incoming/outgoing callback behavior, and public peer list stats.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/peering.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/recv.rs -->
# sources/object-store/garage/src/net/recv.rs

## Purpose
This file implements the receiving half of the custom multiplexed stream protocol. It reads chunk frames from a connection, reconstructs per-request byte streams, dispatches new streams to connection-specific handlers, and handles cancellation/error frames.

## Important APIs, types, and functions
`Sender` wraps an unbounded packet sender and sends a broken-pipe error on drop if the stream ended unexpectedly. `RecvLoop` defines `recv_handler`, optional `cancel_handler`, and async `recv_loop`.

## Control flow
`recv_loop` repeatedly reads request ID and chunk size/flags. A `CANCEL_REQUEST` frame removes any active stream, sends a cancel error into it, calls `cancel_handler`, and continues. Normal frames parse continuation/error flags, read the payload, create a new channel and call `recv_handler` for first chunks, forward data/error packets to the stream sender, and either keep the sender in the active map for continuations or close it at EOS.

## State and persistence behavior
State is transient per connection: a `HashMap<RequestID, Sender>` for streams in progress. No persistence.

## Dependencies and integration points
It depends on `send.rs` constants, `ByteStream`, error helpers for remote I/O errors, futures/Tokio async read, and mpsc streams. `ClientConn` and server connections implement `RecvLoop`.

## Risks and edge cases
The code indexes `next_slice[0]` for error frames, so malformed zero-length error frames would panic. It asserts no continuation on error frames. If the receiver side drops before EOS, `Sender` still consumes frames but signals broken pipe. Unexpected EOF cleanly exits the loop; other read errors abort connection.

## Test signals
No direct tests. Useful tests should cover multi-chunk stream reconstruction, cancellation, remote error frames, malformed frame handling, dropped receiver behavior, and concurrent stream IDs.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/recv.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/net/send.rs -->
# sources/object-store/garage/src/net/send.rs

## Purpose
This file implements the sending half of the custom multiplexed stream protocol. It queues request/response streams by priority, chunks them into frames, honors optional order tags, sends cancellation frames, and writes encrypted transport bytes.

## Important APIs, types, and functions
Protocol constants define `RequestID`, `ChunkLength`, `MAX_CHUNK_LENGTH`, continuation/error flags, length mask, and `CANCEL_REQUEST`. `SendItem` is either a stream or cancellation. `SendQueue`, `SendQueuePriority`, and `SendQueueItem` implement scheduling. `DataFrame` encodes data or error chunks. `SendLoop::send_loop` drives channel receive and frame writes.

## Control flow
New streams are inserted into a priority-sorted queue, with lower priority values sent first. Within a priority, `poll_next_ready` first polls streams that have sent zero bytes so small requests can go out quickly, then all streams round-robin. Streams with `OrderTag`s wait until their order number is at the front for that tag stream. Each ready packet becomes a data frame with continuation flag based on stream EOS, or an error frame with encoded I/O kind/message. Cancellation removes queued work and writes a special cancel header. The loop exits after the input channel closes and queued streams drain, then sends transport goodbye.

## State and persistence behavior
All state is per connection and in memory. No persistence. The chunk format is the internal wire protocol consumed by `recv.rs`.

## Dependencies and integration points
It depends on `ByteStreamReader`, message priorities/order tags, error kind encoding, bytes buffers, futures polling, `kuska_handshake::BoxStreamWrite`, and tokio mpsc. `ClientConn` and server connections implement `SendLoop`.

## Risks and edge cases
Unbounded mpsc channels can grow if producers outpace the transport. Order-tag bookkeeping uses unwrap/assert paths and assumes remove/send completion paths remain consistent. Error messages are truncated to fit one chunk. Frequent `flush` after every frame favors latency over throughput. Cancellation only removes queued outgoing data; already transmitted data may still be processed remotely.

## Test signals
No direct unit tests. Useful tests should cover priority ordering, round-robin chunking, order tags, cancellation frames, error-frame truncation, queue removal, and interoperation with `recv_loop`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/net/send.rs -->
