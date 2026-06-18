# subset-b-000533 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/config.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/config.rs

Purpose: defines the complete user-facing configuration surface for the BeeGFS Rust management daemon, covering initialization/import switches, database path, logging, BeeMsg/gRPC networking, TLS, authentication, registration policy, node/client timeout behavior, licensing, blocking thread limits, quota collection/enforcement, capacity-pool thresholds, and hidden daemonization options.

Important APIs/types/functions: the `generate_structs!` macro emits `Config`, its `Default`, private `OptionalConfig` for clap/TOML input, and merge logic. `Config::check_validity()` enforces UUID v4, quota dependency, and capacity-pool consistency. `load_and_parse()` implements default/config-file/CLI precedence and port shifting. `LogTarget` and `LogLevel` are clap/serde enums, with `LogLevel` mapped to `log::LevelFilter`.

Control flow: startup parses CLI first to discover the config file, loads TOML if present or explicitly requested, overlays CLI values, validates the merged result, then applies `port_shift` to BeeMsg and gRPC ports with overflow warnings. TOML uses `deny_unknown_fields`, while some options are CLI-only via `serde(skip)`.

State and persistence: this file does not persist state directly. It determines persistent file locations for SQLite, auth secret, TLS cert/key, license cert/library, quota ID files, and daemon PID. Its defaults shape on-disk deployment behavior.

Dependencies and integration points: used by `main.rs` for binary startup and by `lib.rs`, `grpc.rs`, `quota.rs`, `timer.rs`, and capacity-pool calculations at runtime. It depends on clap, serde/TOML, shared NIC filtering, duration/range parsers, UUID, and capacity-pool validation.

Risks: config precedence comments contain a misleading line saying config file settings overwrite command-line settings, while implementation overlays command line last. Hidden import/init/fs UUID options bypass TOML. `port_shift` intentionally allows overflow. Quota ID ranges can create large query sets if configured too broadly. TLS disable and auth disable are high-impact operational settings.

Test signals: no direct tests in this file. Useful coverage would exercise TOML/CLI precedence, unknown fields, duration/range parsing, invalid quota/enforcement combinations, dynamic capacity limits, UUID version checks, and port-shift overflow messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db.rs

Purpose: top-level SQLite database module for mgmtd. It owns migration discovery, initial database seeding, submodule exports, and test helpers for in-memory databases with fixture data.

Important APIs/types/functions: `MIGRATIONS` includes the generated migration list from `OUT_DIR`. `initial_entries()` seeds immutable config entries `FsUuid` and `FsInitDateSecs`. The module re-exports `import_v7()` and exposes submodules for entity, config, node, NIC, target, buddy group, storage pool, and miscellaneous operations.

Control flow: database creation callers migrate schema, call `initial_entries()`, optionally import v7 data, then commit. Runtime startup checks/migrates schema in `lib.rs`, then uses the submodules through transactional `App` helpers.

State and persistence: this module initializes the persistent SQLite config state containing filesystem UUID and initialization time. It relies on schema migrations and SQLite views/tables defined elsewhere under `db/schema`.

Dependencies and integration points: consumed by `main.rs` initialization, `lib.rs` migration/startup, gRPC handlers, timers, and quota update logic. It uses shared BeeGFS types, rusqlite, sqlite helper extensions, generated SQL-check macros, and UUID.

Risks: `initial_entries()` treats `FsUuid` and init time as immutable via `db/config.rs`; callers must only run it for new DBs. The migration include depends on build-script output being available and correct. Test helpers load `test_data.sql`, so schema/view drift can break broad test suites.

Test signals: built-in test helper functions are used by multiple submodule unit tests. Direct coverage should verify initial entries with and without caller-provided UUID and migration compatibility for fresh/in-memory databases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/buddy_group.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/buddy_group.rs

Purpose: implements database operations for metadata and storage buddy mirror groups, including validation, creation, storage-pool reassignment, automatic switchover, and storage group deletion.

Important APIs/types/functions: `validate_ids()` checks existence by numeric group IDs and server node type. `insert()` creates a `BuddyGroup` entity, validates primary/secondary targets, enforces same storage pool for storage groups, rejects secondary ownership of the meta root, and auto-generates aliases/IDs when needed. `update_storage_pools()`, `check_and_swap_buddies()`, `prepare_storage_deletion()`, and `delete_storage()` support pool moves, failover, and delete workflows.

Control flow: creation first chooses/validates numeric ID, checks target existence and group membership, applies storage/meta-specific constraints, creates a global entity, derives storage pool if applicable, and inserts the group. Switchover queries groups where the primary is offline, secondary is good, and secondary contact is recent, then swaps primary/secondary IDs in the DB.

State and persistence: writes `entities` and `buddy_groups`; switchover mutates group primary/secondary assignments; deletion removes storage groups. It reads `targets`, `storage_targets`, `root_inode`, and client-node state for safety checks.

Dependencies and integration points: used by gRPC create/delete/assign/mirror/root resync flows and by `timer.rs` switchover. Notifications are sent by callers after DB mutations.

Risks: `delete_buddy_group` is explicitly racy because it checks DB, calls nodes, then mutates DB. Switchover is DB-only until callers broadcast refresh notifications. Meta root and client-unmounted constraints are critical for data safety.

Test signals: unit tests cover insertion, pool updates, switchover positive and negative cases, deletion prechecks with mounted clients, returned node UIDs, and storage deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/buddy_group.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/config.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/config.rs

Purpose: typed access layer for key/value configuration rows stored in SQLite, especially filesystem identity and counters used by mgmtd.

Important APIs/types/functions: `Config` enum maps known keys (`FsUuid`, `FsInitDateSecs`, `FsName`, `CounterLastClientID`, `TrialSerial`) to stable DB strings. `set()` inserts/replaces mutable config rows and blocks updates to immutable keys. `get()` parses optional stored values into caller-requested types. `delete()` removes mutable rows.

Control flow: `set()` first reads the existing value for immutable keys and bails if already present, then writes with `REPLACE INTO config`. `get()` manually prepares and steps a query to avoid an extra allocation, then parses the stored string.

State and persistence: persists management configuration in the `config` table. `FsUuid`, `FsInitDateSecs`, and `TrialSerial` are treated immutable by this API, though direct SQL could still alter them. `CounterLastClientID` preserves sequential client ID allocation across restarts.

Dependencies and integration points: used by `db::initial_entries()`, `db::node::insert()` for client ID counters, `lib.rs` for trial serial persistence, `grpc/get_license.rs`, and `grpc/get_nodes.rs`.

Risks: all values are strings, so parse failures surface at read time. API-level immutability can be bypassed outside these helpers. `delete()` requires exactly one affected row, so deleting an already absent mutable key fails.

Test signals: `set_get_delete` covers immutable update/delete rejection, mutable replacement, read-missing behavior, and deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/entity.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/entity.rs

Purpose: manages globally unique entity records that back nodes, targets, pools, and buddy groups. The entity table centralizes UID and alias uniqueness across all object kinds.

Important APIs/types/functions: `get_uid()` resolves an alias to a UID; `get_alias()` resolves UID to alias; `insert()` verifies alias availability, inserts `(entity_type, alias)`, and returns the new SQLite rowid as `Uid`.

Control flow: creation checks the alias first to produce a typed value-exists error rather than relying only on a database constraint, then inserts into `entities`. Concrete object tables reference this entity row afterward.

State and persistence: writes and reads the persistent `entities` table. Entity rows are prerequisites for nodes, targets, pools, and buddy groups, and aliases are intended to be globally unique user-facing names.

Dependencies and integration points: used by `node`, `target`, `storage_pool`, `buddy_group`, and alias update gRPC paths. It depends on `TypedError`, SQLite row-count helpers, and `EntityType` SQL variant mapping.

Risks: insertion is not by itself atomic with later concrete-table inserts unless callers keep it inside one transaction. Alias validation depends on the shared `Alias` type before this layer is called. Race resistance relies on SQLite transaction/constraints.

Test signals: unit test resolves the fixture `management` alias round-trip by UID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/entity.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7.rs

Purpose: imports a BeeGFS 7.2/7.4 management data directory into a fresh Rust mgmtd SQLite database.

Important APIs/types/functions: public `import_v7()` orchestrates the import. Helpers validate `format.conf`, target states, deserialize v7 node/NIC files, import meta/storage nodes and targets, parse buddy group maps, import storage pools, set root inode state, and import quota default/specific limits.

Control flow: import requires a new DB (`MAX(uid) <= 2`), `format.conf` version 5, and all meta/storage target states GOOD. It imports storage nodes/targets/groups/pools first, then meta nodes/groups/root, then quota if a quota directory exists. Storage-pool alias conflicts or invalid aliases prompt interactively for replacement aliases.

State and persistence: writes persistent nodes, targets, buddy groups, pools, root inode, NICs, and quota limit rows. It intentionally ignores ephemeral quota usage, clients, and refreshed runtime data. Large v7 quota values beyond signed 63-bit are treated as unlimited/skipped with notes.

Dependencies and integration points: called by `main.rs` database initialization when `--import-from-v7` is provided. It depends on shared BeeSerde decoders for legacy on-disk formats, DB helpers for inserts, and SQLite transactions for all-or-nothing behavior.

Risks: format support is intentionally narrow. Interactive alias repair can block automation. The code assumes old management is shut down and clients unmounted; those conditions are documented but not fully enforceable. SQL writes must stay aligned with schema views and v7 binary layouts.

Test signals: covered by `import_v7/test.rs`, which extracts a fixed v7.4 fixture and validates nodes, targets, groups, root, pools, and quota rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7/test.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7/test.rs

Purpose: end-to-end regression test for the v7 management data importer using a bundled v7.4 data archive.

Important APIs/types/functions: `import_v7()` test extracts `test_data.tar.gz` to a temporary directory, wraps execution in `catch_unwind()` for cleanup, then calls `import_v7_inner()`. The inner helper creates an in-memory DB, migrates schema, seeds initial entries, runs `super::import_v7()`, and checks imported rows.

Control flow: the test is skipped on Windows. It shells out to `tar`, imports from the extracted directory, then queries nodes, targets, buddy groups, root inode, storage pools, quota defaults, and quota limits in deterministic order.

State and persistence: uses only an in-memory SQLite database plus a temporary extracted fixture directory. It does not write production state.

Dependencies and integration points: verifies `db::MIGRATIONS`, `initial_entries()`, SQLite enum conversions, importer parsing, and schema compatibility together.

Risks: depends on the external `tar` command and fixture archive path. It validates one representative v7 layout, not all malformed files, missing files, alias-prompt paths, or non-GOOD target states.

Test signals: strong integration signal that the importer creates expected rows for a real v7.4-style dataset, including quota data and mirrored meta root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/import_v7/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/misc.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/misc.rs

Purpose: contains cross-cutting database helpers for numeric ID allocation and metadata-root state.

Important APIs/types/functions: `find_new_id()` finds an unused numeric ID in a table/field/node-type/range. `MetaRoot` represents unknown, normal node-hosted, or mirrored buddy-group-hosted root state. `get_meta_root()` reads `root_inode` joined to targets/nodes/groups. `enable_metadata_mirroring()` moves the root from a meta target to its buddy group and marks the secondary target `NeedsResync`.

Control flow: ID allocation uses SQL to find the smallest gap or the range minimum when unused. Metadata mirroring updates `root_inode` through a primary-target buddy-group join, then updates the secondary meta target consistency.

State and persistence: mutates `root_inode` and `targets.consistency` during metadata mirroring. Reads target/node/group topology and generates IDs for multiple object tables.

Dependencies and integration points: called by node/target/pool/buddy insert paths, gRPC root-mirroring handler, node insertion, and import code. It depends on trusted static table/field arguments.

Risks: `find_new_id()` builds SQL from `table` and `field`; its warning is correct that user-supplied names would be SQL injection. Metadata mirroring assumes a valid primary buddy group exists and one root row is affected.

Test signals: unit tests cover gap/min/all-taken ID allocation and normal-to-mirrored root transition, including a second mirroring attempt failing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/node.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/node.rs

Purpose: database access layer for BeeGFS nodes, including registration/update, lookup, stale client cleanup, license machine counting, and deletion.

Important APIs/types/functions: `Node` models `uid`, numeric ID, node type, alias, and port. `get_with_type()` and `get_by_alias()` read nodes. `insert()` allocates/generates IDs and aliases, inserts an entity and node row. `update()` refreshes port, last contact, and machine UUID. `count_machines()` counts distinct recently active meta/storage machines for licensing. `delete_stale_clients()` and `delete()` remove nodes.

Control flow: client auto-ID allocation uses persistent `CounterLastClientID` to avoid immediate reuse and scans upward, wrapping only at `u32::MAX`. Non-client nodes allocate from `1..=0xFFFF`. Explicit IDs are checked through entity resolution before insertion.

State and persistence: writes `entities`, `nodes`, and the client-ID counter. Updates `last_contact` on heartbeat/registration and deletes stale client rows based on configured timeout.

Dependencies and integration points: used by BeeMsg registration/heartbeat paths, gRPC delete/set-alias/list paths, timers, import, and license checks.

Risks: ID reuse semantics for clients are subtle and depend on the counter being durable. `update()` replaces machine UUID with the passed optional value. License counting ignores inactive/stale nodes older than five minutes.

Test signals: tests cover insert/get/delete, duplicate ID/alias failures, alias lookup, and stale client deletion after artificially aging rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/node_nic.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/node_nic.rs

Purpose: handles persistent network interface records associated with nodes and maps them into BeeMsg-compatible NIC structures.

Important APIs/types/functions: `NodeNic` represents node UID, IP address, port, NIC type, and name. `get_all_addrs()` returns socket addresses grouped by UID for connection-pool seeding. `get_with_node()` and `get_with_type()` read NICs. `ReplaceNic` and `replace()` delete and recreate a node's NIC list. `map_bee_msg_nics()` converts DB NICs into `shared::bee_msg::node::Nic`.

Control flow: reads join `node_nics` with `nodes` to combine stored addresses with current node port. `replace()` removes all old rows for a node before inserting the provided list.

State and persistence: persists `node_nics` rows; these are refreshed at startup for management and from node registration/heartbeat paths for other nodes.

Dependencies and integration points: used by `lib.rs` startup, connection-pool initialization, gRPC `get_nodes`, gRPC `set_alias` heartbeat notification, and v7 import.

Risks: address strings are parsed at read time; malformed DB data causes errors. `replace()` is destructive for a node's NICs and should run inside transactions with validated input. Ordering is by node UID, not NIC priority.

Test signals: tests cover grouped address retrieval, per-node reads, type-filtered reads, clearing NICs, and inserting a replacement NIC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/node_nic.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/storage_pool.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/storage_pool.rs

Purpose: inserts storage-pool entities and rows, including automatic numeric ID allocation.

Important APIs/types/functions: `insert()` accepts an optional numeric `PoolId` (`0` means auto), validates uniqueness, creates a global pool entity with the supplied alias, inserts into `pools`, and returns `(Uid, PoolId)`.

Control flow: auto-ID uses `misc::find_new_id()` against the `pools` table for storage node type. Explicit IDs are checked via `try_resolve_num_id()`. After entity insertion, the concrete pool row is inserted with storage node type.

State and persistence: writes `entities` and `pools`; assignment of targets or buddy groups to the pool is handled by gRPC `assign_pool`/`create_pool` logic, not here.

Dependencies and integration points: used by `grpc/create_pool.rs` and v7 storage-pool import. It depends on entity uniqueness, SQLite enum mapping, and typed value-exists errors.

Risks: entity insertion and pool insertion must be in one transaction to avoid orphaned entities on failure. Pool ID range is fixed to 16-bit-like `1..=0xFFFF`.

Test signals: no local tests in this file; create/list pool gRPC tests and v7 importer tests exercise the path indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/storage_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/target.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/db/target.rs

Purpose: database operations for metadata and storage targets, including creation, validation, state updates, pool assignment, storage-node mapping, capacity refresh, and deletion.

Important APIs/types/functions: `validate_ids()` verifies target numeric IDs by server node type. `insert_storage()` allocates/creates storage targets. `insert()` creates a target entity and row. `update_consistency_states()`, `update_storage_pools()`, `update_storage_node_mappings()`, `get_and_update_capacities()`, and `delete_storage()` mutate target runtime/assignment state.

Control flow: storage targets can be inserted unmapped; metadata targets are inserted with a node ID. New storage targets default to pool `1`. Capacity refresh reads old capacity values before updating rows and returns the previous values to callers.

State and persistence: writes `entities` and `targets`, including `node_id`, `pool_id`, registration token, consistency, and capacity fields. Deletes storage targets only.

Dependencies and integration points: used by BeeMsg target registration/heartbeat/capacity handlers, gRPC set-state/delete/list/assign, buddy group creation, v7 import, quota target discovery, and timers.

Risks: `insert()` relies on entity alias uniqueness to reject duplicate target aliases; explicit numeric duplicates can still surface as DB constraint errors if not checked by caller. `update_storage_node_mappings()` returns affected count and silently leaves unknown IDs unchanged. Capacity update assumes target rows already exist.

Test signals: unit test covers auto and explicit storage target insertion, duplicate explicit ID failure, mapping updates, and resulting row counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/db/target.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/error.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/error.rs

Purpose: defines a small typed error enum for recurring database/business validation failures with stable wording.

Important APIs/types/functions: `TypedError` has `ValueNotFound { name, value }` and `ValueExists { name, value }` variants with `thiserror` display implementations. Constructors `value_exists()` and `value_not_found()` accept `ToString` inputs.

Control flow: no control flow beyond constructor formatting. Callers wrap variants in `anyhow` or `bail!` so errors can be propagated through gRPC and service layers.

State and persistence: stateless.

Dependencies and integration points: used by entity, target, buddy group, and storage pool validation to produce consistent "not found" and "already exists" errors.

Risks: only two error categories exist; most logic still uses free-form `anyhow` messages, so callers should not assume all validation failures are typed.

Test signals: no direct tests. Existing DB tests indirectly check these paths by asserting operations fail, but not exact messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc.rs

Purpose: declares and serves the mgmtd management gRPC API, wiring protobuf RPC methods to handler modules and applying TLS/authentication/shutdown/license guard helpers.

Important APIs/types/functions: `ManagementService { app }` implements `pm::management_server::Management` via `shared::impl_grpc_handler!`. `serve()` builds the tonic server, configures TLS unless disabled, attaches an `auth-secret` metadata interceptor, binds on IPv4/IPv6 unspecified address, and spawns graceful serving. `fail_on_pre_shutdown()` and `fail_on_missing_license()` centralize handler preconditions.

Control flow: each RPC is macro-generated to call a same-named async handler module, log context, and map errors. `serve()` reads certificate/key files if TLS is enabled, rejects missing/mismatched auth metadata when auth is configured, and shuts down via `RunStateHandle`.

State and persistence: no direct DB writes here; handlers perform state changes. Server state is the cloned `RuntimeApp`, TLS identity, and auth secret.

Dependencies and integration points: bridges `protobuf::management`, tonic, shared gRPC utilities, `RuntimeApp`, license verification, DB modules, and all `grpc/*` handlers.

Risks: disabling TLS logs a warning but still serves. Authentication compares a hashed `AuthSecret` from request metadata; clients must send exact metadata bytes. Handler availability during pre-shutdown depends on each handler calling the helper.

Test signals: handler modules contain focused tests. Additional integration tests should cover TLS file failures, auth metadata rejection, and generated handler error-code mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/assign_pool.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/assign_pool.rs

Purpose: implements the RPC that assigns a storage pool to selected storage targets and buddy groups.

Important APIs/types/functions: `assign_pool()` performs gRPC-level guards and response shaping. `do_assign()` contains reusable transactional assignment logic shared by `create_pool()`.

Control flow: handler verifies storage-pool license and pre-shutdown state, resolves the pool entity, calls `do_assign()`, logs, and sends `RefreshStoragePools` to meta and storage nodes. `do_assign()` rejects direct target assignment when a target belongs to a storage buddy group, updates standalone target pool IDs, updates buddy group pool IDs, and updates both grouped targets to the same pool.

State and persistence: mutates `targets.pool_id` and `buddy_groups.pool_id` inside the caller's transaction. Sends cluster refresh notifications after commit in the RPC path.

Dependencies and integration points: used by `assign_pool` RPC and `create_pool` RPC. Relies on `ResolveEntityId`, storage pool licensing, SQLite joins over storage buddy groups, and BeeMsg refresh messages.

Risks: partial assignment inside a transaction is safe if the outer transaction rolls back on any error. The function assumes all groups are storage groups via resolved entity semantics and SQL shape; invalid node-type combinations should be tested.

Test signals: no direct tests here. Pool creation/list tests and manual assignment paths should validate grouped target auto-assignment and standalone target rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/assign_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/common.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/common.rs

Purpose: shared constants for quota-related gRPC handlers.

Important APIs/types/functions: `QUOTA_NOT_ENABLED_STR` standardizes the user-facing error when quota RPCs are called while quota support is disabled. `QUOTA_STREAM_PAGE_LIMIT` sets DB page size to 1,000,000 rows. `QUOTA_STREAM_BUF_SIZE` sets response channel buffer size to 100,000.

Control flow: none.

State and persistence: stateless; affects runtime memory/latency tradeoffs for quota streaming.

Dependencies and integration points: used by `get_quota_limits`, `get_quota_usage`, `set_quota_limits`, and `set_default_quota_limits`.

Risks: large page/buffer settings can use significant memory during large quota queries but reduce DB overhead. The values are tuned from local performance comments and may need reassessment on production-scale deployments.

Test signals: no direct tests. Streaming quota tests should cover empty, small, and multi-page result sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_buddy_group.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_buddy_group.rs

Purpose: handles creation of metadata or storage buddy mirror groups through gRPC.

Important APIs/types/functions: `create_buddy_group()` parses request node type, alias, optional numeric group ID, and primary/secondary target entities; calls `db::buddy_group::insert()`; returns the created `EntityIdSet`.

Control flow: after license/pre-shutdown checks, the handler resolves both targets in a write transaction, creates the group, logs success, sends `SetMirrorBuddyGroup` to meta, storage, and client nodes, and sends `RefreshStoragePools` for storage groups.

State and persistence: writes a buddy group entity and row. For storage groups, group creation also implies storage-pool membership relationships used by pool refresh consumers.

Dependencies and integration points: depends on mirroring license, entity resolution, DB group constraints, BeeMsg `SetMirrorBuddyGroup`, and storage-pool refresh notifications.

Risks: notification happens after DB commit; failures to deliver are not rolled back. Target/node-type mismatches and root-inode secondary restrictions are enforced in DB helper. Storage-pool refresh is needed for grouped targets to be interpreted correctly by other nodes.

Test signals: no direct test in this file; DB buddy group tests cover constraints. RPC tests should verify notifications and proto response fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_buddy_group.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_pool.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_pool.rs

Purpose: implements storage pool creation and optional initial assignment of targets and buddy groups.

Important APIs/types/functions: `create_pool()` validates the request is for storage node type, parses alias and optional numeric pool ID, calls `db::storage_pool::insert()`, then reuses `assign_pool::do_assign()`.

Control flow: license and pre-shutdown guards run first. The DB transaction inserts the pool and applies requested assignments atomically. The handler builds a `EntityIdSet`, logs, sends `RefreshStoragePools` to meta/storage nodes, and returns the pool.

State and persistence: writes `entities` and `pools`, and may update `targets.pool_id` and `buddy_groups.pool_id`.

Dependencies and integration points: storage-pool license, pool DB helpers, assignment logic, and BeeMsg storage-pool refresh.

Risks: node type must be storage; any future non-storage pool type would require API changes. Assignment validation can fail after pool insertion but before commit, which is safe because the transaction rolls back.

Test signals: `get_pools` tests validate fixture pools; create-pool-specific tests would be useful for auto IDs, assignment rollback, and notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/create_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_buddy_group.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_buddy_group.rs

Purpose: deletes storage buddy groups through a multi-step check/notify/commit flow.

Important APIs/types/functions: `delete_buddy_group()` resolves the group, verifies storage type, calls `db::buddy_group::prepare_storage_deletion()`, sends BeeMsg `RemoveBuddyGroup` to both owning storage nodes, and then calls `db::buddy_group::delete_storage()`.

Control flow: the `execute` flag controls dry-run versus committed deletion. The first transaction validates deletion and obtains primary/secondary node UIDs. The handler sends check-only or execute removal messages to both nodes and requires both `OpsErr::SUCCESS`. A second transaction deletes the DB row if execution is requested; refresh notification follows successful execution.

State and persistence: removes a storage buddy group from SQLite only after both storage nodes accept removal. Sends `RefreshStoragePools` because group membership affects pool state.

Dependencies and integration points: mirroring license, DB deletion checks, BeeMsg request/response types, and storage-pool refresh.

Risks: the source notes this is racy: database state can change between validation, node RPCs, and final deletion. Dry-run mode performs validations and node check requests but does not commit.

Test signals: no direct tests in this file. DB helper tests cover mounted-client rejection and deletion. RPC tests should simulate primary/secondary node response failures and execute=false behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_buddy_group.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_node.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_node.rs

Purpose: implements node deletion, including special handling for meta nodes and their implicit targets.

Important APIs/types/functions: `delete_node()` resolves a node, rejects management node deletion, checks meta target buddy/root constraints, checks non-meta assigned targets, deletes the node, and optionally sends `RemoveNode`.

Control flow: an immediate transaction performs all validation and deletion, committing only when `execute` is true. Meta nodes first delete their one associated meta target if not in a buddy group and not hosting root inode. Storage/client paths require no assigned targets. After commit, notifications go to meta/client for meta deletion or meta/storage/client for storage deletion.

State and persistence: deletes from `nodes` and, for meta nodes, deletes the corresponding target row. Cascading entity cleanup depends on schema constraints/triggers.

Dependencies and integration points: entity resolution, DB node deletion, root/buddy checks, BeeMsg `RemoveNode`, and pre-shutdown guard.

Risks: execute=false still runs deletion SQL inside an uncommitted transaction to validate effects. Meta target assumptions require exactly one target per meta node. Notification delivery failure does not undo deletion.

Test signals: async test covers management deletion rejection, meta buddy member rejection, successful empty meta-node deletion, and database absence afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_node.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_pool.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_pool.rs

Purpose: deletes an empty storage pool.

Important APIs/types/functions: `delete_pool()` resolves the pool entity, counts assigned storage targets and buddy groups, deletes the pool row when empty, and returns the deleted pool entity.

Control flow: after license/pre-shutdown checks, an immediate transaction enforces emptiness. The `execute` flag controls commit. Successful execution logs and sends `RefreshStoragePools` to meta and storage nodes.

State and persistence: removes from `pools`; entity cleanup depends on schema behavior. It does not reassign targets or groups.

Dependencies and integration points: storage-pool license, entity resolution, SQLite pool/target/group tables, and storage-pool refresh.

Risks: default pool deletion behavior is governed only by DB constraints and assigned rows; this file does not special-case pool ID 1. Dry-run mode executes deletion inside a rolled-back transaction.

Test signals: no direct tests. Useful coverage would include non-empty pool rejection, execute=false no-op, default pool handling, and notification emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_target.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_target.rs

Purpose: deletes standalone storage targets.

Important APIs/types/functions: `delete_target()` resolves a target, ensures it is a storage target and not a buddy-group member, calls `db::target::delete_storage()`, and returns the deleted target entity.

Control flow: the handler uses an immediate transaction and honors `execute` for commit/dry-run. After committed deletion it logs, sends `RefreshCapacityPools` to meta nodes, and sends `RefreshStoragePools` to meta/storage nodes.

State and persistence: removes a storage target row from SQLite. It does not contact the owning storage node; this is a management DB operation plus refresh notifications.

Dependencies and integration points: pre-shutdown guard, entity resolution, target DB helper, capacity-pool and storage-pool BeeMsg refresh messages.

Risks: only storage targets can be deleted directly; meta target deletion is tied to node deletion. Deleting a target with stale external node state may require operators to coordinate daemon state.

Test signals: no direct tests here. Needed tests include buddy-member rejection, execute=false, non-storage rejection, and notification types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/delete_target.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_buddy_groups.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_buddy_groups.rs

Purpose: implements the read-only RPC returning all buddy groups with member targets, storage pool, and consistency state.

Important APIs/types/functions: `get_buddy_groups()` queries `buddy_groups_ext`, joins primary/secondary `targets_ext`, optional `pools_ext`, and maps rows to `pm::get_buddy_groups_response::BuddyGroup`.

Control flow: one read transaction builds the full response. Node type and target consistency enums are converted through SQLite enum helpers into protobuf integer variants.

State and persistence: read-only; exposes persisted buddy group topology and target consistency states.

Dependencies and integration points: used by management clients/ctl tooling. Depends on DB views, protobuf `EntityIdSet`, and enum conversion helpers.

Risks: inner joins require primary and secondary targets to exist; inconsistent DB rows would disappear or error. There is no filtering or pagination, so very large clusters return one response containing all groups.

Test signals: no direct tests. Useful tests would verify meta versus storage groups, optional pool population, and consistency state mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_buddy_groups.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_license.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_license.rs

Purpose: returns license certificate data and trial-serial persistence state over gRPC.

Important APIs/types/functions: `get_license()` calls `app.license().get_license_cert_data()`, reads `Config::TrialSerial` from SQLite, and builds `GetLicenseResponse` including a derived `trial_used` flag.

Control flow: if certificate data is available and is a trial certificate, the handler marks `trial_used` true when the stored trial serial exists and differs from the current serial. For non-trial or missing data it reports false.

State and persistence: read-only. It reads the license library's cached cert data and the DB config row storing a previously used trial serial.

Dependencies and integration points: used by management clients to inspect licensing. Integrates `license.rs`, protobuf license types, and DB config.

Risks: if the license library is unavailable or no cert is loaded, the helper returns an error. Trial-used semantics depend on serial persistence during startup in `lib.rs`.

Test signals: no direct tests. Coverage should include no library, invalid/no data, trial same serial, trial different serial, and non-trial certs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_license.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_nodes.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_nodes.rs

Purpose: implements node listing, optional NIC expansion, filesystem UUID reporting, and meta-root identification.

Important APIs/types/functions: `get_nodes()` reads nodes from `nodes_ext`, optionally reads NICs, resolves root inode owner to `meta_root_node` and optional `meta_root_buddy_group`, and reads `Config::FsUuid`.

Control flow: one read transaction fetches raw nodes/NICs/root/UUID. After the transaction, if NICs were requested, it groups NIC rows by node UID and formats addresses with the node port. Invalid stored IP strings fall back to IPv6 unspecified during formatting.

State and persistence: read-only; exposes `nodes`, `node_nics`, `root_inode`, and config state.

Dependencies and integration points: used by management clients and tests. Depends on DB views, `EntityIdSet`, SQLite enum conversion, and IP/socket formatting.

Risks: optional NIC inclusion can add load. The post-query NIC grouping is O(nodes * nics). Root-query joins assume one root row. IP parse fallback may hide malformed stored NIC addresses in responses.

Test signals: async test verifies node counts with/without NICs, selected NIC counts, and meta-root node UID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_nodes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_pools.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_pools.rs

Purpose: returns storage pools with assigned storage targets, buddy groups, and optionally default quota limits.

Important APIs/types/functions: `get_pools()` builds pool records from storage pool tables, joins default quota limits when requested, separately gathers target and buddy-group assignments, then merges them into each pool response.

Control flow: read transaction returns three lists: pools, `(pool_uid, target)` pairs, and `(pool_uid, buddy_group)` pairs. The handler then appends matching targets/groups to each pool by UID. Missing quota defaults are represented as `-1`.

State and persistence: read-only over pools, entities, targets, buddy groups, and quota default limits.

Dependencies and integration points: used after create/delete/assign pool operations and by management clients. Depends on quota enum SQL values and protobuf response structures.

Risks: merge is quadratic over pool assignments, acceptable for small lists but potentially inefficient at very large scale. Quota limit inclusion uses left joins and sentinel values, so consumers must interpret `-1` as unlimited/unset.

Test signals: async test verifies pool count, assigned target/group counts, and default quota values including `-1` for missing limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_pools.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_limits.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_limits.rs

Purpose: streams configured per-user/per-group quota limits with optional ID and pool filters.

Important APIs/types/functions: `get_quota_limits()` returns `RespStream<GetQuotaLimitsResponse>`. It resolves an optional pool, builds SQL filters for user/group min/max/list, and pages through grouped quota-limit rows using `QUOTA_STREAM_PAGE_LIMIT`.

Control flow: license and quota-enable guards run first. The SQL `WHERE` string starts as `FALSE` and appends OR clauses only for requested filters. Streaming repeatedly fetches a page at increasing offset, sends each row as `QuotaInfo`, and stops when the page is short.

State and persistence: read-only over `quota_limits` and `pools_ext`.

Dependencies and integration points: used by management clients; depends on quota license, runtime config, response streaming helper, DB enum conversions, and pool entity resolution.

Risks: dynamic SQL is built from numeric request values and resolved pool ID, not raw strings, but the approach is still fragile. If no filters are provided, `WHERE FALSE` returns no rows. Offset pagination can be expensive on huge tables and can observe changes between pages.

Test signals: no direct tests. Needed coverage includes empty filters, user/group range/list combinations, pool filter, multi-page streaming, and quota disabled/unlicensed paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_limits.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_usage.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_usage.rs

Purpose: streams aggregated quota usage joined with effective limits and optional exceeded/pool filters.

Important APIs/types/functions: `get_quota_usage()` returns `RespStream<GetQuotaUsageResponse>`. It builds user/group ID filters, optional pool UID `HAVING`, optional exceeded/not-exceeded filtering, and streams grouped `QuotaInfo` rows.

Control flow: after license/quota-enable checks, the handler builds dynamic `WHERE` and `HAVING` clauses, queries `quota_usage` joined to targets/pools/default/specific limits, aggregates usage by quota ID/type/pool, and sends paged responses. The first streamed response includes `refresh_period_s`; later messages omit it.

State and persistence: read-only over quota usage collected by `quota.rs` timers and quota limit tables.

Dependencies and integration points: management clients use this to inspect quota state. It depends on quota update interval config, pool resolution, streaming helpers, and SQLite aggregation.

Risks: no ID filters means no results. Offset pagination may be slow and inconsistent under concurrent updates. Effective limit logic uses `COALESCE(l.value, d.value, -1)` and exceeded checks require positive limits.

Test signals: no direct tests in this file; quota update tests populate usage. Streaming/filter tests would improve confidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_quota_usage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_targets.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_targets.rs

Purpose: returns all targets with owning node, storage pool, reachability, consistency, capacities, and computed capacity-pool classification.

Important APIs/types/functions: `get_targets()` reads target rows and implements `CapacityInfo` for target response references so `CapPoolCalculator` can classify capacity pools.

Control flow: the DB query joins targets to nodes, pools, and buddy group membership. Reachability uses `node_offline_timeout`, last update age, pre-shutdown state, and primary/secondary status. After reading, the handler computes meta capacity pools globally for meta targets and storage capacity pools separately per storage pool.

State and persistence: read-only over targets, nodes, pools, and buddy groups. Capacity values are persisted by target update paths elsewhere.

Dependencies and integration points: used by management clients and affected by `timer.rs` pre-shutdown/switchover behavior. Depends on cap-pool config and calculators.

Risks: capacity-pool calculation unwraps optional capacity through the `CapacityInfo` trait but only calls it after checking `Some`; future changes must preserve that guard. Reachability logic changes during pre-shutdown to protect primary targets. Large pool/target sets trigger repeated filtering per pool.

Test signals: no direct test in this file. Useful coverage would verify reachability thresholds, pre-shutdown behavior, meta/storage cap-pool calculations, and unmapped storage targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/get_targets.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/mirror_root_inode.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/mirror_root_inode.rs

Purpose: enables metadata mirroring for the root inode after strict cluster-safety checks.

Important APIs/types/functions: `mirror_root_inode()` reads `db::misc::get_meta_root()`, validates prerequisites, sends `SetMetadataMirroring` to the root meta node, and commits `db::misc::enable_metadata_mirroring()` if the node returns success.

Control flow: handler requires mirroring license and no pre-shutdown. It rejects already mirrored/unknown roots, requires the root target to be primary in a meta buddy group, requires no mounted clients, and requires all other meta/storage nodes to have been quiet beyond `node_offline_timeout`. Only then does it contact the root meta node.

State and persistence: after successful node-side mirroring, updates `root_inode` to point to the buddy group and marks the secondary meta target `NeedsResync`.

Dependencies and integration points: integrates DB root helpers, BeeMsg root-mirroring message, node last-contact tracking, and client-node state.

Risks: there remains a documented race where clients may mount after the check but before node-side operation; operators must coordinate. If node-side success occurs but DB update fails, reconciliation may be required.

Test signals: no direct tests. Needed tests should cover each precondition, node failure response, and DB transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/mirror_root_inode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_alias.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_alias.rs

Purpose: updates the alias of a non-client entity and broadcasts node alias changes.

Important APIs/types/functions: `set_alias()` parses entity type, entity ID, and new alias. Its local `update_alias_fn` resolves the entity, rejects clients, checks alias uniqueness, updates `entities.alias`, and returns the previous entity identity.

Control flow: for node aliases, the handler updates the alias in a write transaction, re-reads the node and NIC list, then sends a BeeMsg `Heartbeat` to meta/storage/client nodes so they learn the new alias. For targets/pools/buddy groups it only updates the DB.

State and persistence: mutates `entities.alias`. For node aliases, cluster-visible state is refreshed by notification rather than direct writes to other nodes.

Dependencies and integration points: uses entity resolution, node/NIC DB helpers, `map_bee_msg_nics()`, BeeMsg heartbeat shape, and pre-shutdown guard.

Risks: returned response is empty, so clients must rely on subsequent list calls. The notification sends a heartbeat-like message with zero version fields; consumers must tolerate that. Client alias updates are explicitly unsupported.

Test signals: async test covers missing entity, wrong entity type, duplicate alias, client rejection, successful node alias update, notification emission, and DB value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_alias.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_default_quota_limits.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_default_quota_limits.rs

Purpose: updates or clears default quota limits for a storage pool.

Important APIs/types/functions: `set_default_quota_limits()` resolves the pool and applies optional user/group space/inode limit fields. The nested `update()` helper treats `-1` as delete/unlimited, values greater than `-1` as upsert, and values below `-1` as invalid.

Control flow: quota license, pre-shutdown, and `quota_enable` checks run before mutation. The write transaction resolves the pool once, then applies only fields present in the request.

State and persistence: writes or deletes rows in `quota_default_limits` keyed by pool, ID type, and quota type.

Dependencies and integration points: used by management clients and read by `get_pools`, `get_quota_usage`, and quota enforcement calculations.

Risks: the handler does not proactively notify nodes; enforcement changes take effect through the next quota distribution cycle. Sentinel `-1` semantics must remain consistent with readers.

Test signals: no direct tests. Useful tests would cover each field, invalid negative values, deletion, pool resolution, quota disabled, and enforcement interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_default_quota_limits.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_quota_limits.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_quota_limits.rs

Purpose: updates or clears specific quota limits for user/group IDs across pools.

Important APIs/types/functions: `set_quota_limits()` iterates request `limits`, resolves each pool, converts ID type, and applies optional space/inode limits using prepared `REPLACE` and `DELETE` statements.

Control flow: quota license, pre-shutdown, and `quota_enable` checks gate the write transaction. For each quota entry, values greater than `-1` are persisted; `-1` or lower deletes the row for that quota type. Missing fields are left unchanged.

State and persistence: mutates `quota_limits` rows keyed by quota ID, ID type, quota type, and pool ID.

Dependencies and integration points: read by quota usage RPC and quota enforcement. Relies on pool entity resolution and quota enum SQL variants.

Risks: unlike default limits, values below `-1` are treated as delete rather than invalid, which may be inconsistent. Per-entry pool resolution can be repetitive for large batches. Enforcement waits for periodic distribution.

Test signals: no direct tests. Needed coverage includes mixed insert/delete, invalid/missing quota IDs, repeated pools, quota disabled, and value semantics below `-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_quota_limits.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_target_state.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_target_state.rs

Purpose: manually updates a target consistency state and pushes that state to the owning node.

Important APIs/types/functions: `set_target_state()` parses target entity and desired `TargetConsistencyState`, updates the DB through `db::target::update_consistency_states()`, sends `SetTargetConsistencyStates` to the target owner, and broadcasts `RefreshTargetStates`.

Control flow: DB state is updated first and returns the target plus node UID. Then the handler sends the node request and bails if the response is not `OpsErr::SUCCESS`. Finally, all meta/storage/client nodes are notified to refresh target states.

State and persistence: mutates `targets.consistency`. The node-side state update and cluster refresh are separate network side effects.

Dependencies and integration points: pre-shutdown guard, target entity resolution, target DB helper, BeeMsg target-state messages, and refresh notifications.

Risks: if the DB update succeeds but the node request fails, the handler returns an error while DB state remains changed. This asymmetry is explicitly called out in the error message and may need operator attention.

Test signals: no direct tests. Useful tests would simulate node success/failure, unknown target, meta/storage state mapping, and notification emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/set_target_state.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/start_resync.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/start_resync.rs

Purpose: starts or restarts buddy target resync for metadata or storage buddy groups.

Important APIs/types/functions: `start_resync()` resolves a buddy group, identifies source primary and destination secondary target plus source node UID, checks current resync status via meta/storage BeeMsg requests, optionally calls nested `override_last_buddy_comm()`, marks destination target `NeedsResync`, and broadcasts `RefreshTargetStates`.

Control flow: metadata resync only supports full non-restart resync and rejects timestamps. Storage resync can override last buddy communication timestamp; restart requires a timestamp and waits up to 180 seconds for the existing resync to stop, polling every two seconds. The actual resync begins when nodes fetch refreshed target state.

State and persistence: mutates destination target consistency in SQLite. It sends BeeMsg stats/override requests to the source node and refresh notifications to the cluster.

Dependencies and integration points: mirroring license, buddy group/target DB views, storage/meta resync BeeMsg types, `tokio::time`, and target-state refresh mechanics.

Risks: the code documents a race where storage nodes may overwrite the communication timestamp before resync starts. Polling is described as simple but imperfect. DB state change and source-node override are separate effects.

Test signals: no direct tests. Coverage should include meta rejection cases, storage running/not-running states, restart timeout, override failure, and final DB state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/grpc/start_resync.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/lib.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/lib.rs

Purpose: library entry point for the BeeGFS management service. It wires static startup info, SQLite, BeeMsg networking, connection pool, timers, gRPC, license loading, and graceful shutdown control.

Important APIs/types/functions: `StaticInfo` holds immutable runtime config, auth secret, local NICs, and IPv6 choice. `start()` initializes the daemon and returns `RunControl`. `migrate_db_schema()` backs up and migrates SQLite. `RunControl::wait_for_shutdown()` drives pre-shutdown, client state-drain waiting, and final shutdown. `version_str()` exposes compile-time `VERSION`.

Control flow: startup leaks `StaticInfo` for `'static` sharing, binds UDP, builds outgoing connection pool, opens/migrates DB, refreshes management node/NIC rows, loads/verifies license and persists first trial serial, seeds connection-pool addresses from DB, starts TCP/UDP BeeMsg listeners, timers, and gRPC.

State and persistence: opens and migrates the SQLite DB, updates management node last contact/NICs, persists first trial serial, and reads node addresses into memory. Shutdown enters pre-shutdown before notifying clients to pull target state when buddy groups and clients exist.

Dependencies and integration points: central integration point for `app`, `db`, `license`, shared BeeMsg incoming/outgoing networking, run-state, timers, gRPC, and config.

Risks: `Box::leak` intentionally makes static info process-lifetime. License failures leave features unavailable but do not abort startup. Shutdown state-drain depends on clients reporting both meta and storage pulls before timeout or second signal.

Test signals: no direct tests here in this subset. Integration tests should cover migration, startup with/without license, auth secret propagation, connection-pool seeding, and shutdown client wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/license.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/license.rs

Purpose: wraps the external BeeGFS license verification shared library and exposes Rust APIs for certificate loading, feature checks, machine limits, and certificate data retrieval.

Important APIs/types/functions: `LicensedFeature` maps feature enum variants to C-string DNS names. `ExternalBuf` owns C buffers returned by the library and frees them on drop. `LoadedLibrary` dynamically loads expected symbols and provides safe-ish wrappers. `LicenseVerifier` exposes `with_lib()`, `with_no_lib()`, `load_and_verify_license_cert()`, `get_license_cert_data()`, `get_licensed_machines()`, and `verify_licensed_feature()`.

Control flow: startup loads function pointers from the configured library path, initializes the cert store, reads PEM asynchronously, verifies it via FFI, decodes prost protobuf results, rejects reusing a different trial serial, and logs success. Feature verification calls the library per requested feature and maps result enums to `anyhow` errors.

State and persistence: no local persistence; the external library caches the last verified cert. Trial serial persistence is handled by `lib.rs` through DB config.

Dependencies and integration points: used by startup and gRPC/license/feature gates. Depends on `libloading`, prost-generated license protobufs, C ABI function signatures, and configured certificate/library files.

Risks: loading arbitrary dynamic libraries and calling assumed signatures is unsafe; comments document the contract. Missing library makes all licensed features unavailable. External buffer pointers must be valid NUL-terminated strings and freed by the matching function.

Test signals: no direct tests. Useful coverage would use a fake dynamic library or abstraction to validate valid/invalid/error results, trial serial mismatch, machine-limit DNS parsing, and no-library behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/license.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/main.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/main.rs

Purpose: binary entry point for the management daemon. It handles process setup, configuration, logging, initialization/import mode, auth/NIC discovery, Tokio runtime construction, license library loading, startup, systemd readiness, shutdown signals, and panic logging.

Important APIs/types/functions: `main()` maps errors to exit code 1. `inner_main()` performs runtime setup. `init_db()` creates a new DB in memory, migrates/seeds/imports, then atomically backs it up to a new on-disk file. `panic_handler()` logs backtraces. `wait_for_shutdown_signal()` waits for SIGINT/SIGTERM.

Control flow: config is parsed first, optional daemonization happens before logger init, then init/import/upgrade modes can exit early. Normal startup requires existing DB, reads auth secret unless disabled, queries NICs, creates Tokio runtime with configured blocking threads, loads license library, starts `mgmtd::start()`, notifies systemd, and waits for shutdown.

State and persistence: creates DB files only in init/import mode, using `File::create_new()` and cleanup on backup failure. Reads auth file and license library/cert paths. Writes daemon PID file through `daemonize`.

Dependencies and integration points: consumes `config`, `db`, `license`, shared NIC/journald/auth helpers, Tokio Unix signals, systemd notification, and library `start()`.

Risks: daemonization before logging can obscure failures except daemonization itself. License library loading is unsafe by design. Init/import writes to disk only after in-memory success, reducing partial DB risk. Unix signal code is platform-specific.

Test signals: no direct tests. Integration tests should cover init DB with/without v7 import, existing-file failure, auth file errors, logger modes, and upgrade early exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/quota.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/quota.rs

Purpose: periodically collects quota usage from storage nodes, stores it in SQLite, calculates exceeded quota IDs, and pushes enforcement state to meta/storage nodes.

Important APIs/types/functions: `fetch_and_update()` gathers configured user/group IDs, requests `GetQuotaInfo` from each storage target owner, and replaces `quota_usage` per successfully fetched target. `distribute_exceeded()` builds `SetExceededQuota` messages for every pool/id-type/quota-type combination and fills exceeded IDs when licensed. `try_read_quota_ids()` parses whitespace-separated numeric IDs from files.

Control flow: collection skips if quota feature is not licensed. It discovers mapped storage targets, builds ID sets from system users/groups, files, and configured ranges, concurrently requests user and group quota per target, and only updates a target when both requests succeed. Enforcement sends empty messages too, so stale exceeded IDs are cleared on nodes.

State and persistence: mutates `quota_usage` rows; reads pools, targets, quota limits, default limits, and user config. Sends enforcement state to all meta/storage nodes.

Dependencies and integration points: called by `timer.rs` when quota is enabled. Integrates license checks, system ID iteration, BeeMsg quota messages, and SQLite aggregation.

Risks: large configured ID ranges can create heavy network and DB load. Partial target fetch failure intentionally preserves old usage for that target. Enforcement can be very message-heavy because it sends pool x id-type x quota-type messages to every node.

Test signals: async tests cover quota collection, failed-fetch preservation/removal behavior, and exceeded quota message content across pools/types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/quota.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/quota/system_id.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/quota/system_id.rs

Purpose: provides iterators over local system user and group IDs for quota collection.

Important APIs/types/functions: `user_ids()` returns `UserIDIter`, wrapping libc `setpwent/getpwent/endpwent`. `group_ids()` returns `GroupIDIter`, wrapping `setgrent/getgrent/endgrent`. A global `OnceLock<tokio::sync::Mutex<()>>` serializes all iteration.

Control flow: each async constructor acquires the global mutex, resets libc enumeration, and returns an iterator holding the guard. The iterator calls libc on each `next()` and drops by ending enumeration.

State and persistence: no persistence. It reads process-local libc/NSS user and group databases and holds a global async mutex during iteration.

Dependencies and integration points: used by `quota::fetch_and_update()` when configured minimum system user/group IDs are set.

Risks: libc enumeration APIs use global state; the mutex protects this module but cannot protect unrelated code calling `setpwent/getpwent` or group equivalents. Iteration can block other tasks waiting for system IDs until the iterator drops.

Test signals: multi-thread Tokio tests spawn 16 concurrent readers for users and groups and assert all collected lists are equal, guarding the mutex serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/quota/system_id.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/timer.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/timer.rs

Purpose: starts and runs periodic background tasks for stale-client deletion, quota updates, quota enforcement, and buddy-group switchover.

Important APIs/types/functions: `start_tasks()` spawns task futures. `delete_stale_clients()` periodically deletes old client nodes. `update_quota()` runs quota collection and exceeded distribution. `switchover()` periodically calls `db::buddy_group::check_and_swap_buddies()` and broadcasts target refreshes after swaps.

Control flow: stale-client loop sleeps for configured timeout or exits on pre-shutdown. Quota loop runs immediately, then sleeps for the configured interval. Switchover uses `node_offline_timeout / 6`, skips missed ticks, delays the initial real check by one interval, and exits on pre-shutdown.

State and persistence: stale-client and switchover tasks mutate SQLite; quota task mutates quota usage and sends enforcement messages. Switchover sends `RefreshTargetStates` after DB swaps.

Dependencies and integration points: started by `lib.rs`; relies on run-state pre-shutdown signaling, DB helpers, quota module, and BeeMsg refresh messages.

Risks: no task is joined here; lifecycle is controlled by cloned run-state handles. Switchover timing must align with node target-offline behavior to avoid unsafe failover around management shutdown. Errors are logged and loops continue.

Test signals: no direct tests. DB buddy-group tests cover swap logic; integration tests should validate task exit on pre-shutdown and quota scheduling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/timer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/types.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/types.rs

Purpose: local type utilities for mgmtd database/protobuf integration, primarily SQLite enum conversion.

Important APIs/types/functions: `SqliteEnumExt` defines `sql_variant()`, `from_sql_variant()`, and `from_row()`. The `impl_enum_sqlite!` macro implements it for `EntityType`, `NodeType`, `NodeTypeServer`, `NicType`, `TargetConsistencyState`, `QuotaIdType`, and `QuotaType`. The module re-exports entity resolution helpers from `types/entity.rs`.

Control flow: enum conversions are fixed integer mappings used by schema rows. Unknown integer values become rusqlite invalid-type errors.

State and persistence: establishes the numeric representation persisted in SQLite for core enums.

Dependencies and integration points: used throughout DB modules, gRPC handlers, import code, quota logic, and tests.

Risks: changing mappings would break existing databases unless migrations translate values. `from_sql_variant()` reports invalid type rather than a richer unknown-value error.

Test signals: no dedicated tests. Broad DB and gRPC tests exercise conversions via fixture rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/types/entity.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/types/entity.rs

Purpose: resolves user/API entity identifiers (`uid`, alias, or legacy numeric ID) into complete `EntityIdSet` values by querying the appropriate SQLite view.

Important APIs/types/functions: `ResolveEntityId` provides `try_resolve()` and `resolve()`. Implementations exist for `EntityId`, `Uid`, `LegacyId`, and `Alias`. `try_resolve_num_id()` and `resolve_num_id()` are convenience helpers. `resolve_sql_from()` selects view-specific base SQL for nodes, targets, buddy groups, and pools.

Control flow: resolution dispatches by identifier kind, appends a `WHERE` clause, queries one row, and returns `None` or a typed `EntityIdSet`. Pool resolution hard-codes storage node type in the base select.

State and persistence: read-only over `nodes_ext`, `targets_ext`, `buddy_groups_ext`, and `pools_ext`.

Dependencies and integration points: used by nearly every gRPC mutation and DB validation path to normalize protobuf/entity references before changing state.

Risks: dynamic SQL appends controlled fragments only, but it still depends on exact view column aliases. Legacy ID resolution requires both node type and numeric ID; wrong entity-type/ID combinations return not found.

Test signals: no direct tests. `set_alias`, delete handlers, and DB creation tests indirectly exercise successful and failing resolutions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/types/entity.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/rust-toolchain.toml -->
# sources/distributed-fs/beegfs-rust/rust-toolchain.toml

Purpose: pins the Rust toolchain for the BeeGFS Rust workspace.

Important APIs/types/functions: TOML `[toolchain]` declares `channel = "1.94"` and `profile = "default"`.

Control flow: rustup uses this file when commands are run inside the workspace to select/download the specified compiler toolchain.

State and persistence: no application state. It affects developer/CI toolchain selection and reproducibility.

Dependencies and integration points: applies to all Rust crates in `beegfs-rust`, including mgmtd, shared, sqlite, protobuf, and derive crates.

Risks: channel `1.94` is a future or specific stable version relative to many environments; builds fail if rustup cannot resolve/install it. Pin updates should be coordinated with edition/style settings and dependency MSRVs.

Test signals: validated by successful `cargo` commands under rustup. No unit tests apply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/rust-toolchain.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/rustfmt.toml -->
# sources/distributed-fs/beegfs-rust/rustfmt.toml

Purpose: configures formatting style for the BeeGFS Rust workspace.

Important APIs/types/functions: sets `style_edition = "2024"`, groups imports as one block, uses module-level import granularity, wraps comments, and sets comment width to 100.

Control flow: rustfmt reads this file during formatting and applies these choices across crates.

State and persistence: no runtime state; it affects source formatting and review diffs.

Dependencies and integration points: used by developer/CI formatting workflows and must be supported by the pinned Rust/rustfmt version.

Risks: `style_edition = "2024"` and import grouping options require sufficiently new rustfmt support. If contributors use older toolchains, formatting can fail or produce inconsistent output.

Test signals: `cargo fmt --check` or equivalent is the relevant validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/rustfmt.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/Cargo.toml -->
# sources/distributed-fs/beegfs-rust/shared/Cargo.toml

Purpose: manifest for the `shared` crate, which contains reusable BeeGFS protocol, networking, parsing, logging, type, and optional gRPC support used by mgmtd and other crates.

Important APIs/types/functions: declares package metadata inherited from the workspace, dependency on local `bee_serde_derive`, workspace dependencies such as `anyhow`, `libc`, `log`, `regex`, `ring`, `serde`, `thiserror`, and `tokio`, plus optional `protobuf`, `tonic`, and `tokio-stream`. Feature `grpc` enables those optional gRPC dependencies. Clippy lint `undocumented_unsafe_blocks = "deny"` is set.

Control flow: Cargo resolves optional gRPC dependencies only when the `grpc` feature is enabled.

State and persistence: no runtime state; it defines build graph and lint policy.

Dependencies and integration points: mgmtd uses shared BeeMsg, connection, NIC, parser, run-state, and type modules. Optional protobuf/tonic integration supports management API code paths.

Risks: `ring` is pulled for hashing with a comment noting licensing/indirect dependency concerns. Feature-gated code must compile both with and without `grpc`. Workspace dependency versions control compatibility.

Test signals: crate-level `cargo check/test` across feature combinations, especially default and `--features grpc`, validate this manifest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg.rs -->
# sources/distributed-fs/beegfs-rust/shared/src/bee_msg.rs

Purpose: defines core BeeGFS wire-message traits, common operation error codes, message header layout, and serialization/deserialization helpers shared by mgmtd and other Rust components.

Important APIs/types/functions: `MsgId` is a `u16`. `BaseMsg` and `Msg` mark BeeGFS messages and require an associated message ID. `OpsErr` wraps BeeGFS operation error integers with constants such as `SUCCESS`, `INTERNAL`, `UNKNOWN_NODE`, `EXISTS`, `NOTEMPTY`, `UNKNOWN_TARGET`, `INVAL`, `AGAIN`, and `UNKNOWN_POOL`. `Header` is a BeeSerde-serializable 40-byte header with feature flags, prefix, ID, target/user fields, and sequence fields. Helpers include `serialize_body()`, `serialize_header()`, `serialize()`, `deserialize_header()`, `deserialize_body()`, and `deserialize()`.

Control flow: serialization writes the body after a reserved header slot, sets total message length and message ID, then serializes the header. Deserialization validates the fixed header length and prefix before decoding the body slice indicated by `msg_len`.

State and persistence: stateless; it encodes/decodes network byte buffers used in BeeMsg TCP/UDP communication.

Dependencies and integration points: re-exports message submodules for buddy groups, misc, node, quota, storage pool, and target. Used by shared connection code, mgmtd handlers, timers, quota, and gRPC side-effect messages.

Risks: buffer sizes must be correct; `serialize()` indexes `buf[Header::LEN..]` and callers must provide enough space. `deserialize_body()` trusts `header.msg_len()` for slicing and will panic or error if inconsistent with buffer length depending on slice bounds. Header prefix compatibility is strict.

Test signals: no direct tests here. Protocol tests should cover header round trips, invalid prefixes, short buffers, body length mismatches, and all message submodule serialization compatibility with C++ BeeGFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/src/bee_msg.rs -->
