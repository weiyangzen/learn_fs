# subset-b-008170 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/table.rs -->
# sources/object-store/garage/src/table/table.rs

## Purpose
Generic distributed table facade for Garage metadata tables. `Table<F, R>` binds a schema, a replication policy, local table storage, Merkle maintenance, anti-entropy sync, garbage collection, insert queueing, and an RPC endpoint into the API used by higher-level model code.

## Important APIs, types, and functions
Key types are `Table<F, R>` and private `TableRpc<F>`. Public calls are `new`, `spawn_workers`, `insert`, `queue_insert`, `insert_many`, `get`, `get_range`, and `get_local`; internal helpers include `insert_internal`, `insert_many_internal`, `get_internal`, `get_range_internal`, and `repair_on_read`. The endpoint handler serves `ReadEntry`, `ReadRange`, and `Update` RPCs.

## Control flow
Construction creates `TableData`, `MerkleUpdater`, `TableSyncer`, `TableGc`, registers the table name in the layout manager, and installs itself as the Netapp endpoint handler. Writes compute partition hashes, ask replication for write sets, encode entries, then send update RPCs to enough nodes for write quorum. Batched writes deduplicate write sets, build per-node payloads, and track quorum with `QuorumSetResultTracker`. Reads query read nodes, merge divergent CRDT entries, and spawn repair-on-read updates when responses disagree.

## State and persistence behavior
Local persistence lives behind `TableData` and the underlying Garage DB transaction/tree APIs; this file coordinates when serialized entries are written locally or sent remotely. Merkle updater, syncer, GC, and insert queue workers maintain convergence and cleanup outside the request path. Read repair is asynchronous and best-effort after a successful client read.

## Dependencies and integration points
Integrates `garage_rpc` endpoints, `System`, `RequestStrategy`, OpenTelemetry tracing, table schema/replication traits, CRDT merging, table data encoding, Merkle/sync/GC workers, and Garage utility metrics/errors. Higher-level bucket/object/key tables rely on these generic semantics.

## Risks and test signals
Quorum accounting is the critical risk: wrong write-set deduplication, stale layout locks, or premature success can break read-after-write guarantees. Range reads must trim to the requested limit after merging node responses so later entries without read quorum are not returned. Useful tests are distributed write/read quorum failures, divergent replicas triggering repair, range limit/order behavior, and endpoint rejection of unexpected RPC variants.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/table.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/table/util.rs -->
# sources/object-store/garage/src/table/util.rs

## Purpose
Small table helper types shared by schemas and range reads. It supplies an empty partition/sort key, deletion filtering policy, and range enumeration direction.

## Important APIs, types, and functions
`EmptyKey` implements both `SortKey` and `PartitionKey`, returning an empty byte sort key and a zero hash. `DeletedFilter` has `Present`, `Deleted`, and `Any` variants with `apply`. `EnumerationOrder` has `Forward`, `Reverse`, and `from_reverse`.

## Control flow
The helpers are pure value conversions. Table data/range code applies `DeletedFilter` to per-entry deleted state and `EnumerationOrder` to choose forward or reverse traversal/trimming.

## State and persistence behavior
No persistent state is stored here. The enum values are serializable and become part of table RPC/range request state when clients enumerate metadata.

## Dependencies and integration points
Depends on table `PartitionKey`/`SortKey` traits and `garage_util::data::Hash`. `EmptyKey` is used for singleton/global table partitions such as bucket aliases.

## Risks and test signals
The zero hash for `EmptyKey` intentionally maps all singleton rows to one partition; accidental use for high-cardinality data would hot-spot a shard. Tests should cover filter truth tables and reverse flag conversion.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/table/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/Cargo.toml -->
# sources/object-store/garage/src/util/Cargo.toml

## Purpose
Cargo manifest for the `garage_util` crate, the shared utility layer used by Garage crates for configuration, CRDTs, serialization, errors, metrics, background workers, persistence, time, and version metadata.

## Important APIs, types, and functions
The manifest declares `lib.rs`, workspace dependencies on `garage_db` and `garage_net`, serialization/hash/time/async/HTTP/OpenTelemetry crates, build dependency `rustc_version`, and features `k2v` and optional `arbitrary` support.

## Control flow
Cargo uses the build script to inject `RUSTC_VERSION`; crate modules are exposed by `lib.rs`. Feature selection controls whether arbitrary generators for CRDT fuzzing are compiled.

## State and persistence behavior
No runtime state, but dependency and feature choices define which persistence, migration, and test/fuzz helpers are available to the compiled utility crate.

## Dependencies and integration points
This manifest is consumed by most Garage workspace crates. Version skew in `serde`, `rmp-serde`, `tokio`, `hyper`, and OpenTelemetry can affect public utility APIs across the repository.

## Risks and test signals
Optional `arbitrary` must stay synchronized with CRDT modules that gate `Arbitrary` impls. Build/test signals are workspace `cargo check`, feature builds with `--features arbitrary`, and utility crate unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/background/mod.rs -->
# sources/object-store/garage/src/util/background/mod.rs

## Purpose
Public entry point for Garage background work scheduling. It wires worker registration, status collection, and the worker processor loop.

## Important APIs, types, and functions
Exports `vars`, `worker`, `Worker`, and `WorkerState`. Defines `BackgroundRunner`, `WorkerInfo`, and `WorkerStatus`; important methods are `BackgroundRunner::new`, `get_worker_info`, and `spawn_worker`.

## Control flow
`new` creates an unbounded worker channel and shared status map, starts `WorkerProcessor::run` as a Tokio task, and returns both runner and join handle. `spawn_worker` boxes any `Worker` and sends it to the processor; status snapshots clone the mutex-protected map.

## State and persistence behavior
State is in-memory process state: queued workers, task ids, latest status, error counts, and last error timestamps. Persistent knobs may be exposed through `background/vars.rs`, but this module itself does not write disk state.

## Dependencies and integration points
Used by table Merkle/sync/GC workers, insert queues, and other long-running Garage services. Integrates Tokio channels/watch signals and worker traits from `worker.rs`.

## Risks and test signals
The unbounded channel assumes worker creation is controlled; abuse could grow memory. Status locking should remain short. Tests or runtime signals include worker info visibility, graceful shutdown through the watch signal, and no panic when workers exit.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/background/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/background/vars.rs -->
# sources/object-store/garage/src/util/background/vars.rs

## Purpose
Dynamic background variable registry for exposing and updating persisted runtime tuning values through a uniform string interface.

## Important APIs, types, and functions
`BgVars` stores named boxed `BgVarTrait` objects. `register_rw` registers a read/write variable from a `PersisterShared<V>` plus typed getter/setter closures; `register_ro` installs a read-only value; `get`, `get_all`, and `set` provide string access.

## Control flow
Registration clones the shared persister into closures. Reads call the typed getter and stringify the result. Writes parse the incoming string into `T`, call the setter, and propagate conversion or persistence errors.

## State and persistence behavior
The registry is in-memory, but registered setters can mutate and save `PersisterShared` values, so CLI/admin updates can become durable. Missing names and read-only writes are surfaced as `Error::Message`.

## Dependencies and integration points
Depends on Garage error helpers, migration-aware persisters, `FromStr`/`ToString`, and background/admin code that exposes worker tuning variables.

## Risks and test signals
String parsing is deliberately generic; ambiguous display/parse formats can make values non-round-trippable. Tests should cover unknown variable errors, read-only rejection, parse errors, and persistence side effects from setters.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/background/vars.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/background/worker.rs -->
# sources/object-store/garage/src/util/background/worker.rs

## Purpose
Core asynchronous worker scheduler for Garage background tasks, including lifecycle state transitions, backoff, status accounting, and graceful shutdown.

## Important APIs, types, and functions
Defines `WorkerState::{Busy, Throttled, Idle, Done}`, async trait `Worker` with `name`, `status`, `work`, and `wait_for_work`, `WorkerProcessor::run`, and private `WorkerHandler::step`. `EXIT_DEADLINE` bounds shutdown draining.

## Control flow
The processor accepts new boxed workers, assigns task ids, and drives each handler through a `FuturesUnordered` set. Busy workers call `work`; errors are logged, counted, timestamped, and converted to exponential `Throttled` sleeps. Idle workers wait for work or stop-signal changes; Done workers are removed. On shutdown, remaining workers are drained until deadline.

## State and persistence behavior
Worker state, error counters, consecutive error counts, and last errors are in memory and copied into the shared `WorkerInfo` map. There is no disk persistence, but errors influence runtime pacing through throttling.

## Dependencies and integration points
Uses Tokio select/watch/mpsc, `async_trait`, futures streams, Garage `Error`, `WorkerStatus`, and `now_msec`. All background subsystems implement this trait to participate in Garage process shutdown and status reporting.

## Risks and test signals
Risks include workers that never yield, unbounded repeated errors, and cancellation during long work after the exit deadline. The explicit `yield_now` for Busy loops is a fairness guard. Tests should simulate Busy/Idle/Done, error backoff, status map updates, and stop-signal deadline behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/background/worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/build.rs -->
# sources/object-store/garage/src/util/build.rs

## Purpose
Cargo build script for `garage_util`; records the Rust compiler version used for the build.

## Important APIs, types, and functions
`main` calls `rustc_version::version` and emits `cargo:rustc-env=RUSTC_VERSION=...`.

## Control flow
Cargo runs the script before compiling the crate. The emitted environment variable is later read by `version.rs` through `env!`.

## State and persistence behavior
No persistent application state. The build output embeds compiler version metadata into the binary.

## Dependencies and integration points
Integrates Cargo build-script protocol, `rustc_version`, and Garage build info metrics/version reporting.

## Risks and test signals
`unwrap` means build fails if rustc version cannot be queried. Build success and `garage_util::version::rust_version()` returning a non-empty string are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/config.rs -->
# sources/object-store/garage/src/util/config.rs

## Purpose
TOML configuration schema and deserialization helpers for a Garage node, covering storage paths, replication/consistency, RPC, discovery, metadata database, S3/K2V/web/admin APIs, compression, buffering, and feature toggles.

## Important APIs, types, and functions
Primary type is `Config`, with nested `DataDirEnum`, `DataDir`, `S3ApiConfig`, `K2VApiConfig`, `WebConfig`, `AdminConfig`, `ConsulDiscoveryAPI`, `ConsulDiscoveryConfig`, and `KubernetesDiscoveryConfig`. `read_config` parses a file. Helpers provide defaults and custom deserializers for compression and byte capacities.

## Control flow
Serde deserializes TOML into the typed schema, applying defaults and custom visitors. Compression accepts integer levels or string `none`; capacity fields accept integers or strings parsed by `bytesize`. The test writes a minimal config and verifies `rpc_secret` parsing.

## State and persistence behavior
This module reads configuration from disk but does not mutate it. Parsed values drive persistent storage locations, fsync behavior, data directory capacity/read-only semantics, metadata snapshots, RPC secrets, and admin tokens.

## Dependencies and integration points
Consumed by Garage startup, API servers, discovery code, DB initialization, block manager, and admin/metrics/tracing setup. Depends on serde, TOML, bytesize, socket address parsing, and Garage error handling.

## Risks and test signals
Misparsed capacity/compression values can cause memory pressure or disabled compression unexpectedly. Optional secret-file fields require external permission checks elsewhere. Tests should cover both single/multiple data dirs, Unix/TCP API addresses, invalid capacities, compression `none`, and default consistency/database values.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/bool.rs -->
# sources/object-store/garage/src/util/crdt/bool.rs

## Purpose
A boolean CRDT where `true` is absorbing, useful for one-way flags that must converge across replicas.

## Important APIs, types, and functions
`Bool(bool)` exposes `new`, `set`, `get`, `From<bool>`, and `Crdt::merge`.

## Control flow
Merging ORs the local and remote value. Once any replica sets the flag, all later merges retain `true`.

## State and persistence behavior
The wrapped boolean is serializable/deserializable and can be stored in table entries. There is no timestamp or tombstone, so it cannot express a reset to false after true is observed.

## Dependencies and integration points
Depends on serde and the Garage `Crdt` trait. It can be nested in larger metadata CRDT structs.

## Risks and test signals
Use only for monotonic flags. Tests should verify false+false stays false and any merge involving true yields true.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/bool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/crdt.rs -->
# sources/object-store/garage/src/util/crdt/crdt.rs

## Purpose
Defines Garage's convergence contract for replicated metadata and a helper trait for simple automatically mergeable values.

## Important APIs, types, and functions
`Crdt` requires `merge(&mut self, other)`. `AutoCrdt` is implemented for ordered cloneable values where the maximum value wins; blanket `Crdt` implementation applies to any `AutoCrdt`. `String` and `bool` opt into this simple policy.

## Control flow
Generic CRDT containers call `merge` recursively. For `AutoCrdt`, merge compares values and replaces local state when the remote value is greater.

## State and persistence behavior
No state is stored here; the traits govern how serialized table values converge after reads, writes, sync, and repair.

## Dependencies and integration points
Used throughout Garage table schemas and CRDT modules (`Lww`, maps, options, deletable wrappers). It is central to safe multi-replica metadata reconciliation.

## Risks and test signals
The blanket max-wins policy is only valid for monotonic domains. Accidentally marking a non-monotonic type as `AutoCrdt` can lose information. Tests should check associativity/idempotence/commutativity for every CRDT type.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/crdt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/deletable.rs -->
# sources/object-store/garage/src/util/crdt/deletable.rs

## Purpose
CRDT wrapper representing either a present value or a deletion tombstone, allowing deletions to dominate stale present values during merge.

## Important APIs, types, and functions
`Deletable<T>` has `Present(T)` and `Deleted` variants. Helpers include `map`, `present`, `delete`, option conversion methods, `is_deleted`, `From<Option<T>>`, `From<Deletable<T>> for Option<T>`, and `Crdt::merge`.

## Control flow
A present value merged with another present value recursively merges the inner CRDT. Any merge involving `Deleted` results in `Deleted`, making deletion absorbing.

## State and persistence behavior
The tombstone must be persisted long enough for anti-entropy to suppress stale live values. It does not carry deletion time by itself; callers combine it with LWW wrappers when ordering matters.

## Dependencies and integration points
Used by metadata structures with delete semantics and table filters such as `DeletedFilter`. Depends on the base `Crdt` trait and serde derives.

## Risks and test signals
Because deletion is permanent inside this wrapper, recreating an entity generally needs a fresh outer timestamp/key generation strategy. Tests should verify tombstone dominance and recursive merge for present values.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/deletable.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/lww.rs -->
# sources/object-store/garage/src/util/crdt/lww.rs

## Purpose
Last-writer-wins CRDT wrapper around a value with a logical timestamp, used for mutable metadata fields where the newest update should dominate.

## Important APIs, types, and functions
`Lww<T>` stores `timestamp` and `value`. It exposes `new`, `raw`, `update`, `timestamp`, `get`, `take`, `get_mut`, `map`, `Default`, and `Crdt::merge`.

## Control flow
`new` and `update` choose timestamps using Garage logical clock helpers. `merge` replaces local state when the remote timestamp is newer; when timestamps tie, the greater value is kept to make convergence deterministic.

## State and persistence behavior
Timestamp and value are serialized with table entries. The logical clock ties wall time to monotonic increments, helping updates survive skew and repeated local writes.

## Dependencies and integration points
Depends on `time::increment_logical_clock`, serde, and `Crdt`. Frequently nested in bucket/key/user metadata CRDTs and maps.

## Risks and test signals
Clock skew and equal timestamp tie-breaking can surprise callers if values are not naturally ordered. `get_mut` can mutate without timestamp update, so it should be used carefully. Tests should cover newer timestamp dominance, tie ordering, update monotonicity, and default behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/lww.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/lww_map.rs -->
# sources/object-store/garage/src/util/crdt/lww_map.rs

## Purpose
Sorted map CRDT whose entries are individually last-writer-wins, enabling efficient per-key updates and convergence for metadata dictionaries.

## Important APIs, types, and functions
`LwwMap<K, V>` stores sorted `(K, timestamp, V)` items. Main methods are `new`, `raw_item`, `update_mutator`, `update_in_place`, `merge_raw`, `take_and_clear`, `clear`, `retain`, `get`, `get_timestamp`, `items`, `len`, `is_empty`, `Default`, `Crdt::merge`, and optional `Arbitrary`.

## Control flow
Updates compute a timestamp greater than the current entry timestamp, then `merge_raw` binary-searches by key. Existing entries are replaced only if the incoming timestamp is newer or if timestamp ties and incoming value orders greater. Merge iterates remote items through `merge_raw`.

## State and persistence behavior
The vector is kept sorted for deterministic serialization and binary search. Clearing drops local items but is not itself a replicated tombstone; deletions must be modeled in `V` if they need to propagate.

## Dependencies and integration points
Used in Garage CRDT metadata maps. Depends on ordering for keys and values, logical clock helpers, serde, and `Crdt`.

## Risks and test signals
A plain `clear` is local mutation, not a distributed delete. Value ordering participates in timestamp ties, so `V` ordering must be stable. Tests should check sorted insertion, timestamp tie behavior, retained item filtering, and merge idempotence.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/lww_map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/map.rs -->
# sources/object-store/garage/src/util/crdt/map.rs

## Purpose
Sorted map CRDT where values merge recursively instead of being overwritten by timestamps.

## Important APIs, types, and functions
`Map<K, V>` stores sorted `(K, V)` pairs. It provides `new`, `put_mutator`, `put`, `clear`, `get`, `items`, `len`, `is_empty`, `Default`, `FromIterator`, `Crdt::merge`, and optional `Arbitrary`.

## Control flow
`put` binary-searches by key and either replaces the local value or inserts at the sorted position. `merge` iterates remote items, recursively merging values for existing keys and inserting missing keys.

## State and persistence behavior
Deterministic sorted representation is serialized with metadata entries. Like `LwwMap`, `clear` is local and not a replicated deletion unless values encode tombstones.

## Dependencies and integration points
Used for nested metadata maps whose values are CRDTs. Depends on `Ord` keys, `Crdt` values, serde, and optional arbitrary fuzzing.

## Risks and test signals
Replacing a value with `put` can discard local nested CRDT state before merge; callers should use mutator patterns intentionally. Tests should cover sorted order, recursive merge, empty/default, and from-iterator behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/mod.rs -->
# sources/object-store/garage/src/util/crdt/mod.rs

## Purpose
Module aggregator for Garage CRDT primitives.

## Important APIs, types, and functions
Declares submodules `bool`, `crdt`, `deletable`, `lww`, `lww_map`, `map`, and `option`, then publicly re-exports their primary types and traits.

## Control flow
There is no runtime control flow; Rust module loading and re-exporting build a convenient public API surface.

## State and persistence behavior
No state. The module shapes import paths for all CRDT state stored elsewhere in Garage metadata.

## Dependencies and integration points
Consumed by `garage_util` clients and table schema code that imports `garage_util::crdt::*`.

## Risks and test signals
Adding or removing re-exports is a public API change for workspace crates. Compile tests catch missing exports; CRDT behavior is tested in the submodules.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/option.rs -->
# sources/object-store/garage/src/util/crdt/option.rs

## Purpose
Optional-value CRDT wrappers with two different merge policies: one that cancels on conflict and one that recursively merges present values.

## Important APIs, types, and functions
`CancelingOption<T>(Option<T>)` and `MergingOption<T>(Option<T>)` expose `inner`, `into_inner`, `map`, `From<Option<T>>`, and `Crdt::merge` implementations.

## Control flow
`CancelingOption` keeps a value only if both sides are equal or one side is `None`; conflicting `Some` values collapse to `None`. `MergingOption` treats `None` as absence and recursively merges when both sides are `Some`.

## State and persistence behavior
Both wrappers serialize the optional value as part of metadata. `None` can mean disabled, unset, or conflict depending on the wrapper, so callers must choose policy carefully.

## Dependencies and integration points
Used for optional fields in Garage CRDT metadata, often with nested `Lww` or map values. Depends on base `Crdt` and serde.

## Risks and test signals
The two option types have very different semantics; mixing them can silently change conflict resolution. Tests should cover `Some/None`, equal `Some`, conflicting `Some`, and recursive merge cases.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/option.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/data.rs -->
# sources/object-store/garage/src/util/data.rs

## Purpose
Common byte-array, UUID, hash, and hashing utilities for Garage.

## Important APIs, types, and functions
`FixedBytes32` wraps `[u8; 32]` with custom serde bytes representation, debug hex formatting, slice access, `try_from`, `to_vec`, and lexicographic `increment`. Type aliases `Uuid` and `Hash` use it. Functions include `sha256sum`, `blake2sum`, `fasthash`, and `gen_uuid`.

## Control flow
Hash helpers feed data through SHA-256, Blake2s, or xxhash. `gen_uuid` fills random bytes. `increment` walks bytes from the end, carrying over and returning `None` on all-0xff overflow.

## State and persistence behavior
Fixed 32-byte values are serialized compactly and used as persistent identifiers/hashes in tables, network node IDs, and data placement logic.

## Dependencies and integration points
Integrates serde visitors, hex formatting, `garage_net::NodeID` conversions, `rand`, `sha2`, `blake2`, and `xxhash-rust`.

## Risks and test signals
`fasthash` is not cryptographic and should not be used where collision resistance matters. Tests cover increment edge cases; additional signals are serde round-trips and NodeID conversions.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/data.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/encode.rs -->
# sources/object-store/garage/src/util/encode.rs

## Purpose
Serialization helpers for non-versioned MessagePack encoding and debug JSON rendering.

## Important APIs, types, and functions
`nonversioned_encode`, `nonversioned_decode`, and `debug_serialize` wrap `rmp-serde` and `serde_json`.

## Control flow
Encoding uses `rmp_serde::Serializer::with_struct_map` for stable struct-map representation. Decoding reads from a byte slice. Debug serialization pretty-prints JSON or returns the JSON serialization error as a string.

## State and persistence behavior
Used for data formats that do not need the migration marker chain in `migrate.rs`. Once persisted, struct-map field naming and serde compatibility become part of the on-disk/network contract.

## Dependencies and integration points
Depends on serde, rmp-serde, and serde_json. Complements the migration-aware `Migrate` trait.

## Risks and test signals
Non-versioned encoding is risky for long-lived disk state because schema changes have no migration marker. Tests should cover round-trips and field additions where defaults are expected.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/encode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/error.rs -->
# sources/object-store/garage/src/util/error.rs

## Purpose
Shared Garage utility error type and ergonomic conversion helpers for IO, serialization, TOML, HTTP, database, channel, and internal message errors.

## Important APIs, types, and functions
`Error` enum includes variants for DB, IO, RMP encode/decode, JSON, TOML, HTTP, hyper, invalid HTTP headers, and messages. Helpers include `unexpected_rpc_message`, `ErrorContext`, `OkOrMessage`, custom serde serialization/deserialization, and conversions from transaction and channel send errors.

## Control flow
Most functions propagate errors with `?` into this enum. Context helpers wrap lower-level errors in message text. Serialization of `Error` deliberately stores only string form, and deserialization reconstructs a message error.

## State and persistence behavior
Errors are not persistent domain state, but serializing them over RPC loses structured variant detail. This is acceptable for reporting but not for programmatic remote recovery logic.

## Dependencies and integration points
Used throughout Garage utility, table, web, and RPC code. Depends on `thiserror`, serde, HTTP/hyper, rmp-serde, TOML, and Garage DB.

## Risks and test signals
String-only error serialization can hide variant-specific behavior. Tests should exercise context helpers, transaction conversion, and RPC round-trips where callers expect a message-only remote error.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/forwarded_headers.rs -->
# sources/object-store/garage/src/util/forwarded_headers.rs

## Purpose
Extracts a client IP address from HTTP forwarding headers for request logging.

## Important APIs, types, and functions
`handle_forwarded_for_headers(headers)` reads `X-Forwarded-For`, parses the first comma-separated IP, and returns it as a string.

## Control flow
The function rejects missing headers, invalid UTF-8, empty first values, and invalid IP syntax through Garage `Error`. Tests cover IPv4, IPv6, invalid IPs, and missing headers.

## State and persistence behavior
No state or persistence. The result affects logs and metrics context, not authorization.

## Dependencies and integration points
Used by Garage web request logging and likely other HTTP endpoints behind proxies. Depends on `hyper::HeaderMap` and `std::net::IpAddr` parsing.

## Risks and test signals
`X-Forwarded-For` is client-controlled unless a trusted proxy strips/sets it; code should not use this for security decisions. Existing tests validate parsing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/forwarded_headers.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/lib.rs -->
# sources/object-store/garage/src/util/lib.rs

## Purpose
Crate root for `garage_util`, exporting shared utility modules.

## Important APIs, types, and functions
Enables tracing macros and declares public modules: `background`, `config`, `crdt`, `data`, `encode`, `error`, `forwarded_headers`, `metrics`, `migrate`, `persister`, `socket_address`, `time`, `tranquilizer`, and `version`.

## Control flow
No runtime control flow; this file defines module visibility and macro import.

## State and persistence behavior
No direct state. It makes persistence, migration, CRDT, and config modules available to the workspace.

## Dependencies and integration points
Every Garage crate importing `garage_util` depends on this public module layout.

## Risks and test signals
Changing module visibility is a workspace API break. Compile of dependent crates is the primary signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/metrics.rs -->
# sources/object-store/garage/src/util/metrics.rs

## Purpose
Metric utility helpers for timing futures and generating trace identifiers.

## Important APIs, types, and functions
`RecordDuration` extension trait offers `record_duration` and `bound_record_duration` for futures. `gen_trace_id` creates an OpenTelemetry `TraceId` from random bytes.

## Control flow
The wrapper records `Instant::now()` before awaiting a future, then records elapsed seconds into an OpenTelemetry value recorder with provided attributes after completion.

## State and persistence behavior
No persistent state. Runtime telemetry state is emitted through OpenTelemetry meters/traces.

## Dependencies and integration points
Used by table and web request paths to record latency. Depends on futures, OpenTelemetry metrics/trace types, and `rand`.

## Risks and test signals
Timing wrappers must preserve future output and lifetime behavior. Tests can wrap successful and failing futures and assert recorder invocation through a test meter provider.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/migrate.rs -->
# sources/object-store/garage/src/util/migrate.rs

## Purpose
Versioned MessagePack migration framework for persisted Garage data structures.

## Important APIs, types, and functions
`Migrate` defines `VERSION_MARKER`, associated `Previous`, `migrate`, `decode`, and `encode`. `InitialFormat` marks root formats. `NoPrevious` terminates migration chains. Unit tests define V1/V2 to verify direct decode and migration.

## Control flow
Decode first checks the current marker and attempts rmp-serde decode. If that fails or the marker does not match, it recursively tries the previous format and maps through `migrate`. Encode prefixes the current marker and serializes as struct map.

## State and persistence behavior
This is the central persistence compatibility mechanism for files stored through `Persister`. Version markers are part of the durable disk format.

## Dependencies and integration points
Used by `Persister` and `PersisterShared`. Depends on serde and rmp-serde.

## Risks and test signals
Migration chains must remain intact for all supported upgrade paths. Empty markers on initial formats can make overly permissive decodes if formats overlap. Tests should include old bytes, new bytes, corrupted bytes, and marker preservation.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/migrate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/persister.rs -->
# sources/object-store/garage/src/util/persister.rs

## Purpose
Synchronous/asynchronous file persistence helpers for migration-aware Garage values, plus an in-memory shared wrapper that saves changes.

## Important APIs, types, and functions
`Persister<T>` exposes `new`, `load`, `save`, `load_async`, and `save_async`; private `decode` logs a hexdump on migration failure. `PersisterShared<V>` wraps a `Persister` and `RwLock<V>` with `new`, `get_with`, and `set_with`.

## Control flow
Loads read the full file, decode via `T::decode`, and return structured errors on failure. Saves encode and truncate/create the file. `PersisterShared::new` loads existing state or defaults; `set_with` mutates under a write lock then saves.

## State and persistence behavior
This module writes durable local files but does not fsync or use atomic rename. Failed saves after in-memory mutation can leave memory and disk inconsistent for that call.

## Dependencies and integration points
Used for local node settings and background variables. Depends on `Migrate`, Garage errors, std and Tokio file IO, locks, and tracing macros.

## Risks and test signals
Truncate-in-place risks partial files on crash. Tests should cover missing file defaults, decode failure, save/load round-trip, async variants, and `PersisterShared` mutation persistence.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/persister.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/socket_address.rs -->
# sources/object-store/garage/src/util/socket_address.rs

## Purpose
Configuration type accepting either TCP socket addresses or Unix socket paths for Garage HTTP-style listeners.

## Important APIs, types, and functions
`UnixOrTCPSocketAddress::{TCPSocket, UnixSocket}` implements `Display` and custom serde `Deserialize`.

## Control flow
Deserialization treats strings starting with `/` as Unix socket paths and all others as `SocketAddr`. Display renders `http://addr` or `http+unix://path`.

## State and persistence behavior
No runtime state. Parsed values drive listener binding in API/web/admin servers.

## Dependencies and integration points
Used by `Config`, `WebServer`, and common server setup. Depends on serde, `SocketAddr`, `PathBuf`, and `FromStr`.

## Risks and test signals
Relative Unix socket paths are not accepted by the leading-slash heuristic. IPv6/TCP parse errors surface as config errors. Tests should cover IPv4, IPv6, Unix paths, and malformed strings.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/socket_address.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/time.rs -->
# sources/object-store/garage/src/util/time.rs

## Purpose
Timestamp and logical-clock helpers for Garage metadata.

## Important APIs, types, and functions
`now_msec`, `increment_logical_clock`, `increment_logical_clock_2`, and `msec_to_rfc3339`.

## Control flow
Current time is read from `SystemTime` in milliseconds. Logical clocks choose max of wall time and previous timestamp(s)+1. RFC3339 formatting splits milliseconds into seconds/nanoseconds and uses UTC.

## State and persistence behavior
Timestamps generated here are persisted in LWW metadata and logs. They bridge wall-clock time and monotonic update ordering.

## Dependencies and integration points
Used by CRDT LWW wrappers, worker error timestamps, and display/reporting code. Depends on chrono and system clock.

## Risks and test signals
`now_msec` panics if the system clock is before Unix epoch. Overflow on `prev + 1` is theoretically possible. Tests should cover formatting and logical increment behavior under older/newer wall time.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/time.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/tranquilizer.rs -->
# sources/object-store/garage/src/util/tranquilizer.rs

## Purpose
Adaptive throttling helper for background operations, sleeping or returning a throttled worker state based on recent work durations.

## Important APIs, types, and functions
`Tranquilizer` stores a bounded observation window and exposes `new`, `tranquilize`, `tranquilize_worker`, `reset`, and `clear`.

## Control flow
Each call observes time since the previous step, maintains a moving sum, computes delay as `tranquility * average_step_time`, and either sleeps or returns `WorkerState::Throttled`.

## State and persistence behavior
All state is in-memory timing data. It influences background workload pacing but is reset on process restart.

## Dependencies and integration points
Used by background workers that need to avoid consuming excessive resources. Integrates with Tokio sleep and `WorkerState`.

## Risks and test signals
Large first observations can over-throttle until the window rolls forward. `clear` does not reset `last_step_begin`; callers may need `reset`. Tests can use controlled durations or assert state transitions rather than exact sleep time.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/tranquilizer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/version.rs -->
# sources/object-store/garage/src/util/version.rs

## Purpose
Global runtime accessors for Garage version, optional feature list, and embedded Rust compiler version.

## Important APIs, types, and functions
Uses `ArcSwapOption` statics `VERSION` and `FEATURES`. Functions are `garage_version`, `garage_features`, `init_version`, `init_features`, and `rust_version`.

## Control flow
Startup calls init functions to store static references. Accessors load the swapped Arcs and return static data; `rust_version` reads the build-script environment variable.

## State and persistence behavior
State is process-global and in-memory. It feeds metrics/build info and diagnostics, not persistent application data.

## Dependencies and integration points
Depends on `arc-swap`, `lazy_static`, and the `RUSTC_VERSION` build env from `build.rs`.

## Risks and test signals
`garage_version` unwraps and will panic before initialization. Tests should initialize values before access and verify feature optionality.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/version.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/web/Cargo.toml -->
# sources/object-store/garage/src/web/Cargo.toml

## Purpose
Cargo manifest for `garage_web`, the crate implementing Garage's S3 website endpoint.

## Important APIs, types, and functions
Declares `lib.rs` and workspace dependencies on API common/S3/model/util/table crates plus HTML escaping, percent encoding, HTTP/hyper, Tokio, tracing, thiserror, and OpenTelemetry.

## Control flow
Cargo compiles the web crate against shared Garage crates and applies workspace lints.

## State and persistence behavior
No runtime state. Dependency choices determine web server request handling, S3 object reads, CORS, routing, and telemetry behavior.

## Dependencies and integration points
Integrates the web endpoint with Garage S3 API internals and model tables. Version changes in `hyper`/`http-body-util` can affect response body plumbing.

## Risks and test signals
Manifest drift can break compatibility with shared API error/body types. Build and `web_server.rs` unit tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/web/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/web/error.rs -->
# sources/object-store/garage/src/web/error.rs

## Purpose
Web endpoint error wrapper that maps Garage S3 API errors and website-specific lookup/bad-request failures to HTTP responses.

## Important APIs, types, and functions
`Error::{ApiError, NotFound, BadRequest}` implements `thiserror::Error`. Generic `From<T>` converts anything accepted by the S3 API error type. Methods are `http_status_code` and `add_headers`.

## Control flow
Request handlers convert lower-level errors into this enum, then `error_to_res` in `web_server.rs` asks for status and headers.

## State and persistence behavior
No state. It shapes HTTP status/header output for web clients.

## Dependencies and integration points
Depends on `garage_api_s3::error::Error`, Hyper headers/status codes, and the common `ApiError` trait.

## Risks and test signals
The broad `From<T>` is convenient but can hide unintended conversions through the S3 API error type. Tests should verify NotFound=404, BadRequest=400, and S3 headers are preserved.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/web/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/web/lib.rs -->
# sources/object-store/garage/src/web/lib.rs

## Purpose
Crate root for Garage S3 website serving.

## Important APIs, types, and functions
Enables tracing macros, declares private `error` and `web_server` modules, and publicly re-exports `Error` and `WebServer`.

## Control flow
No runtime control flow; this defines the crate's public surface.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Consumers construct and run `WebServer` from this crate during Garage startup when `s3_web` is configured.

## Risks and test signals
Changing re-exports breaks dependent startup code. Workspace compile is the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/web/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/web/web_server.rs -->
# sources/object-store/garage/src/web/web_server.rs

## Purpose
Implements Garage's S3 static website endpoint: listener setup, request logging/metrics/tracing, bucket resolution from host, website routing rules, object GET/HEAD serving, redirects, error documents, and CORS.

## Important APIs, types, and functions
Important types are `WebMetrics`, `WebServer`, and private `RoutingResult`. Key functions are `WebServer::new`, `run`, `handle_request`, `check_key_exists`, `serve_file`, `handle_inner`, `error_to_res`, `RoutingResult::main_target`, `path_to_keys`, and `compute_redirect_target`.

## Control flow
`run` binds TCP or Unix sockets and delegates to the common server loop. Each request logs peer or forwarded IP, starts an OpenTelemetry span, records metrics, maps the body away, and calls `serve_file`. `serve_file` requires Host, maps host/root domain to bucket alias, loads bucket website config, applies path/routing rules, then either redirects or calls S3 GET/HEAD handlers. It also handles website redirect metadata, error documents, and CORS headers.

## State and persistence behavior
The server reads bucket alias, bucket configuration, and object tables through the `Garage` model. It does not write persistent state. Metrics counters/recorders track request and error counts/durations in memory/exported telemetry.

## Dependencies and integration points
Deeply integrates Hyper, Tokio listeners, Garage common server loop, S3 object handlers, bucket table routing rules, CORS helpers, forwarded header parsing, table lookups, and OpenTelemetry.

## Risks and test signals
Routing is subtle: percent-decoding, trailing-slash redirects, alternative error keys, and HTTP redirect code handling must match S3 website expectations. Host-derived bucket selection depends on trusted root-domain configuration. Existing tests cover `path_to_keys`; broader tests should cover routing rules, error document fallback, HEAD/OPTIONS behavior, CORS, Unix socket binding, and website redirect object metadata.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/web/web_server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/ISSUE_TEMPLATE/config.yml -->
# sources/object-store/minio-mc/.github/ISSUE_TEMPLATE/config.yml

## Purpose
GitHub issue-template configuration for the MinIO client repository. It disables blank issues and points users to community support for questions.

## Important APIs, types, and functions
YAML keys are `blank_issues_enabled: false` and a single `contact_links` entry named MinIO Community Support with Slack URL and explanatory text.

## Control flow
GitHub reads this metadata when a user opens an issue and offers the configured support link instead of allowing an unstructured blank issue.

## State and persistence behavior
No application state. It affects repository issue intake and triage workflow.

## Dependencies and integration points
Integrates with GitHub issue templates and MinIO community support operations.

## Risks and test signals
Disabling blank issues can reduce low-quality reports but may block valid reports if no issue forms are present. Test signal is GitHub rendering the issue chooser as intended.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/lock.yml -->
# sources/object-store/minio-mc/.github/lock.yml

## Purpose
Configuration for an issue-locking automation that locks inactive closed issues after a long quiet period.

## Important APIs, types, and functions
Important keys include `daysUntilLock: 365`, `skipCreatedBefore: false`, `exemptLabels: []`, `lockComment`, `setLockReason: true`, and `only: issues`.

## Control flow
The external lock app scans closed issues, skips exempt labels, posts the configured comment, sets the lock reason, and locks only issues after the inactivity threshold.

## State and persistence behavior
No code state. It mutates GitHub issue lock state and comments when the bot runs.

## Dependencies and integration points
Depends on the configured lock-threads GitHub app and repository labels.

## Risks and test signals
A broad empty exemption list means all closed issues are eligible. Bot dry-runs or observed locked old issues are the practical signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/lock.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/stale.yml -->
# sources/object-store/minio-mc/.github/stale.yml

## Purpose
Configuration for stale issue/PR automation in the MinIO client repository.

## Important APIs, types, and functions
Sets `daysUntilStale: 90`, `daysUntilClose: 30`, exempts `security` and `pending discussion`, uses label `stale`, posts a stale comment, and limits actions with `limitPerRun: 1`.

## Control flow
The probot stale app marks inactive items stale, then later closes stale items unless exempted or updated.

## State and persistence behavior
No application persistence. It changes GitHub labels/comments/closed state.

## Dependencies and integration points
Integrates GitHub issue lifecycle, repository labels, and security triage policy.

## Risks and test signals
The comment says closure after 21 days while `daysUntilClose` is 30, so user-facing text and automation differ. Signals are bot label/close activity and config validation by the stale app.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/stale.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/go-cross.yml -->
# sources/object-store/minio-mc/.github/workflows/go-cross.yml

## Purpose
GitHub Actions pull-request workflow that verifies MinIO client cross-compilation on Ubuntu with Go 1.25.x.

## Important APIs, types, and functions
Workflow `Crosscompile` runs on PRs to `master`, has concurrency cancellation per branch, read-only contents permission, checks out code, sets up Go, enables IPv6 sysctls, and runs `make crosscompile` with `CGO_ENABLED=0` and modules on.

## Control flow
For each matrix entry, checkout/setup precede the Ubuntu-only build step. The Make target delegates to `buildscripts/cross-compile.sh`.

## State and persistence behavior
No repo state is written except ephemeral CI workspace build cache/artifacts.

## Dependencies and integration points
Depends on GitHub Actions, Go toolchain, Makefile, and cross-compile script.

## Risks and test signals
The workflow only runs Ubuntu despite a matrix dimension. Build failures indicate target OS/ARCH compile regressions; IPv6 sysctl failures would break the job environment.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/go-cross.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/go.yml -->
# sources/object-store/minio-mc/.github/workflows/go.yml

## Purpose
Primary PR CI workflow for building and testing the MinIO client on Linux, macOS, and Windows, plus a separate 386 vet-style check.

## Important APIs, types, and functions
Uses Go 1.25.x for the build matrix, `go build`, `go test -race`, `make`, `make test-race`, `make verify`, and `functional-tests.sh`; Linux starts a local HTTPS MinIO server with bundled localhost certs. The `vetchecks` job runs Go 1.24.x and `GOOS=linux GOARCH=386 go test -short ./...`.

## Control flow
Matrix jobs set up Go, checkout, then branch by OS. Linux downloads MinIO server, installs a test CA, starts a 4-disk server, then runs full Make and functional test commands.

## State and persistence behavior
Only ephemeral CI files and local MinIO test data are created. No repository state is committed.

## Dependencies and integration points
Integrates GitHub Actions, MinIO server releases, local TLS certs, Makefile targets, Go race detector, and functional test suite.

## Risks and test signals
The Linux job depends on network download of the server binary and host certificate update permissions. Signals include race-test pass, functional test pass, and platform-specific build success.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/go.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/issues.yaml -->
# sources/object-store/minio-mc/.github/workflows/issues.yaml

## Purpose
GitHub Actions workflow that adds newly opened issues to a MinIO organization project.

## Important APIs, types, and functions
On `issues: opened`, it runs `actions/add-to-project@v0.5.0` with the configured project URL and `secrets.BOT_PAT`.

## Control flow
Each new issue triggers one Ubuntu job and one project-add step.

## State and persistence behavior
No code state. It mutates GitHub Projects membership for issues.

## Dependencies and integration points
Depends on a valid BOT_PAT secret and access to `https://github.com/orgs/miniohq/projects/2`.

## Risks and test signals
Expired or under-scoped tokens leave issues untracked. Test signal is successful workflow run and issue appearing in the project.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/issues.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/vulncheck.yml -->
# sources/object-store/minio-mc/.github/workflows/vulncheck.yml

## Purpose
Security analysis workflow that runs Go vulnerability analysis on PRs and master pushes.

## Important APIs, types, and functions
Checks out code, sets up Go 1.25.x, installs `golang.org/x/vuln/cmd/govulncheck@latest`, and runs `govulncheck ./...`.

## Control flow
Single Ubuntu job performs setup, install, and analysis sequentially.

## State and persistence behavior
No persistent state. It reads module dependencies and reports vulnerabilities in CI.

## Dependencies and integration points
Depends on Go module resolution, the latest govulncheck, and GitHub Actions.

## Risks and test signals
Using `@latest` can introduce nondeterministic failures when govulncheck changes. Signal is a clean vulnerability scan or actionable CI failure.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/workflows/vulncheck.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.golangci.yml -->
# sources/object-store/minio-mc/.golangci.yml

## Purpose
`golangci-lint` v2 configuration for MinIO client code quality checks and formatters.

## Important APIs, types, and functions
Enables `gomodguard`, `govet`, `ineffassign`, `misspell`, `revive`, `staticcheck`, and `unused`; enables `gofmt`, `gofumpt`, and `goimports`; excludes generated code and selected lint texts/paths.

## Control flow
Make targets call `golangci-lint run` with this config and optional `--fix`. Exclusions suppress known style rules across Go files and generated/vendor-like directories.

## State and persistence behavior
No runtime state. `lint-fix` can rewrite source formatting/imports.

## Dependencies and integration points
Integrates with `Makefile` targets `lint` and `lint-fix`, CI, and Go build tags `kqueue`.

## Risks and test signals
Broad exclusions may hide legitimate issues; formatter exclusions must match generated paths. Signal is deterministic lint pass in CI.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.goreleaser.yml -->
# sources/object-store/minio-mc/.goreleaser.yml

## Purpose
GoReleaser configuration for MinIO client release packaging, checksums, signing, packages, and Docker image templates, with GitHub release creation disabled.

## Important APIs, types, and functions
Configures `project_name: mc`, `CGO_ENABLED=0`, pre-hooks, multi-OS/ARCH builds with `kqueue` tag and ldflags, binary archives, deb/rpm nfpm packages, sha256 checksums, GPG detached signatures, changelog filtering, and Docker image templates.

## Control flow
A release run cleans, generates, tidies/downloads modules, builds supported targets, packages artifacts, signs/checksums them, and optionally builds Docker images per arch.

## State and persistence behavior
Writes release artifacts and package metadata, but does not create GitHub releases because `release.disable` is true.

## Dependencies and integration points
Depends on GoReleaser, Go modules, GPG, Docker, package metadata files, and ldflags matching `cmd` version variables.

## Risks and test signals
Ignored target combinations must reflect actual support. GPG/Docker credentials and file templates are operational risks. Test signal is a snapshot release run producing expected artifacts.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.goreleaser.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/Dockerfile -->
# sources/object-store/minio-mc/Dockerfile

## Purpose
Multi-stage Dockerfile building and packaging the latest `mc` binary into a scratch image.

## Important APIs, types, and functions
Build stage uses `golang:1.22-alpine`, installs CA certificates and curl, fetches LICENSE/CREDITS, and runs `go install` with ldflags from `buildscripts/gen-ldflags.go`. Final stage copies `mc`, licenses, and CA bundle into scratch and sets entrypoint.

## Control flow
Docker builds the Go binary in Alpine, then copies only the executable and support files into a minimal runtime image.

## State and persistence behavior
No app persistence. The image contains a static binary and CA store.

## Dependencies and integration points
Depends on network access to GitHub/raw license files and Go module install of `github.com/minio/mc@latest`.

## Risks and test signals
Using `@latest` means builds are not tied to the local checkout. Test signal is successful `docker build` and `mc --help` in the image.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/Makefile -->
# sources/object-store/minio-mc/Makefile

## Purpose
Primary developer/CI automation for building, verifying, testing, cross-compiling, linting, installing, cleaning, and producing hotfix artifacts for MinIO client.

## Important APIs, types, and functions
Targets include `build`, `checks`, `getdeps`, `crosscompile`, `verifiers`, `vet`, `lint`, `lint-fix`, `test`, `test-race`, `verify`, `install`, `docker`, `hotfix`, `hotfix-push`, `docker-hotfix`, `docker-hotfix-push`, and `clean`. Variables derive GOPATH, LDFLAGS, GOOS/GOARCH, VERSION, TAG, and golangci path.

## Control flow
Default `all` builds. `build` checks dependencies then compiles with kqueue tag, trimpath, static CGO disabled, and generated ldflags. Test targets compose verifiers, builds, unit tests, race tests, and full functional tests. Hotfix targets rewrite version/ldflags, sign, checksum, and push artifacts.

## State and persistence behavior
Writes `mc`, GOPATH installs, release/hotfix artifacts, Docker images, and removes generated files on clean. It does not modify source except lint-fix via external tool.

## Dependencies and integration points
Calls build scripts, Go toolchain, golangci-lint, Docker, minisign, sha256sum, scp, and functional tests.

## Risks and test signals
Hotfix push embeds production host paths and credentials. `go install tool` depends on toolchain support. CI signals are `make`, `make test-race`, `make verify`, and `make crosscompile`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/_config.yml -->
# sources/object-store/minio-mc/_config.yml

## Purpose
Minimal Jekyll/GitHub Pages configuration selecting the `jekyll-theme-minimal` theme.

## Important APIs, types, and functions
Single YAML key `theme: jekyll-theme-minimal`.

## Control flow
GitHub Pages/Jekyll reads this config when rendering repository documentation pages.

## State and persistence behavior
No runtime state; it affects generated site appearance.

## Dependencies and integration points
Depends on Jekyll theme availability in GitHub Pages.

## Risks and test signals
Very low risk. Signal is successful Pages build with the expected theme.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/_config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/build.sh -->
# sources/object-store/minio-mc/buildscripts/build.sh

## Purpose
Interactive release-build script for producing versioned MinIO client binaries and checksum files for selected OS/ARCH targets.

## Important APIs, types, and functions
Functions are `_init`, `go_build`, and `main`. It derives LDFLAGS from `gen-ldflags.go`, validates `MC_RELEASE`, defines supported targets, uses `go build`, copies downloadable binaries, and writes SHA1/SHA256 checksum files.

## Control flow
Initialization extracts release tag/string and tool paths. `main` prompts for all or one supported target, validates input, and calls `go_build` for each. `go_build` computes names, compiles with `CGO_ENABLED=0`, copies platform-specific binary names, and generates checksum files.

## State and persistence behavior
Creates release directories, binaries, copied aliases, and checksum files. It may overwrite release output paths.

## Dependencies and integration points
Depends on bash, Go, git-derived ldflags, `shasum`, `sed`, and environment variable `MC_RELEASE`.

## Risks and test signals
Interactive prompt makes it unsuitable for noninteractive CI unless input is provided. Supported target list is narrower than cross-compile CI. Signal is all selected binaries and checksum files created.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/checkdeps.sh -->
# sources/object-store/minio-mc/buildscripts/checkdeps.sh

## Purpose
Build dependency and platform guard script used before compiling MinIO client.

## Important APIs, types, and functions
Sources `buildscripts/build.env`, defines `_init`, custom portable `readlink`, `assert_is_supported_arch`, `assert_is_supported_os`, `assert_check_golang_env`, `assert_check_deps`, and `main`.

## Control flow
Initializes minimum versions and host OS/arch, then checks architecture, OS, Go presence/minimum version, and Git minimum version. Errors print explanatory messages and exit nonzero.

## State and persistence behavior
No persistent state; only process environment and shell options are touched.

## Dependencies and integration points
Called by Makefile `checks` and `build`. Depends on shell utilities, Go, Git, Perl, sed, and `check_minimum_version` from sourced build env.

## Risks and test signals
Minimum `GO_VERSION=1.13` is much older than CI's Go 1.25, so it may not reflect real module requirements. Signals are successful `make checks` on supported platforms and clear failures on unsupported hosts.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/checkdeps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/cross-compile.sh -->
# sources/object-store/minio-mc/buildscripts/cross-compile.sh

## Purpose
Noninteractive cross-compilation smoke test for MinIO client across supported OS/ARCH targets.

## Important APIs, types, and functions
Functions `_init`, `_build`, and `main`. It sets `CGO_ENABLED=0`, enumerates target pairs, sets `GOOS`, `GOARCH`, `GO111MODULE`, and runs `go build -tags kqueue -o /dev/null`.

## Control flow
The script exits on first error. `main` loops all target pairs and invokes `_build`, which prints the target and package import path before compiling.

## State and persistence behavior
No persistent build artifacts are kept because output goes to `/dev/null`.

## Dependencies and integration points
Used by `make crosscompile` and the `go-cross` workflow. Depends on Go cross-compilation support for listed targets.

## Risks and test signals
The target list includes less common architectures; dependency build tags must remain portable. Signal is completion of every target without compile failure.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/cross-compile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/gen-ldflags.go -->
# sources/object-store/minio-mc/buildscripts/gen-ldflags.go

## Purpose
Go helper, run with `go run`, that generates linker flags embedding version, copyright year, release tag, commit hash, and short commit hash into MinIO client binaries.

## Important APIs, types, and functions
Functions are `genLDFlags`, `releaseTag`, `commitID`, `commitTime`, and `main`. It writes `-X github.com/minio/mc/cmd.*` flags for `Version`, `CopyrightYear`, `ReleaseTag`, `CommitID`, and `ShortCommitID`.

## Control flow
`main` uses an explicit version argument or formats the last commit time as RFC3339. `releaseTag` parses the version time, applies `MC_RELEASE` and optional `MC_HOTFIX`, and normalizes punctuation. Git commands retrieve commit hash/time.

## State and persistence behavior
No persistent state; output is consumed by builds and embedded into binaries.

## Dependencies and integration points
Called by Makefile, Dockerfile, and build scripts. Depends on git history, Go time parsing, and cmd package variable names.

## Risks and test signals
It panics if the version cannot be parsed as `2006-01-02T15-04-05Z` after replacement. `commitID()[:12]` assumes a full hash is available. Signal is valid ldflags output and successful binary build with version fields populated.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/buildscripts/gen-ldflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/access-perms.go -->
# sources/object-store/minio-mc/cmd/access-perms.go

## Purpose
Defines accepted bucket access-permission labels and validation for custom policy JSON files used by MinIO client policy/access commands.

## Important APIs, types, and functions
`accessPerms` is a string type with constants `none`, `download`, `upload`, `private`, `public`, and `custom`. Methods `isValidAccessPERM` and `isValidAccessFile` validate built-in labels or parse a policy file.

## Control flow
Built-in validation switches over known constants. File validation opens the named path, decodes JSON into `policy.BucketAccessPolicy`, enforces version `2012-10-17`, and ensures each statement effect is `Allow` or `Deny`.

## State and persistence behavior
Reads a local policy file but writes no state. Fatal messages are emitted through the shared CLI error path for invalid files.

## Dependencies and integration points
Depends on MinIO color JSON decoder and `minio-go` policy types. Integrated by commands that accept canned or custom bucket policies.

## Risks and test signals
The method returns false after `fatalIf`, so callers must not assume nonfatal validation. Tests should cover missing files, malformed JSON, bad version/effect, and every supported canned permission.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/access-perms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/accounting-reader.go -->
# sources/object-store/minio-mc/cmd/accounting-reader.go

## Purpose
Progress accounting helper implementing an `io.Reader`-like counter for transfer operations and formatted/JSON reporting of total, transferred bytes, duration, and speed.

## Important APIs, types, and functions
`accounter` stores atomically updated current/total counters, timing, refresh rate, and a finish channel. Functions/methods include `newAccounter`, `write`, `writer`, `Stat`, `Update`, `Set`, `Get`, `SetTotal`, `Add`, and `Read`. `accountStat` implements `String` and `JSON`.

## Control flow
Creation starts a goroutine that periodically calls `Update` until `Stat` closes `isFinished` once. `Read` increments by buffer length and caps current to total on deferred cleanup to handle upload retries.

## State and persistence behavior
State is in-memory and atomic; no disk persistence. `Stat` finalizes the goroutine and returns a snapshot.

## Dependencies and integration points
Uses colorized console tables, `cheggaaa/pb` formatting, MinIO probe errors, and colorjson. Used by transfer commands needing accounting without wrapping an underlying reader.

## Risks and test signals
`Read` counts the requested buffer length, not bytes from an underlying source, so it is a counter shim rather than a real reader wrapper. Tests should cover concurrent Add/Get, total cap behavior, JSON/String formatting, and goroutine shutdown through `Stat`.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/accounting-reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-create.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-create.go

## Purpose
Registers the MinIO admin access key create command. The file is a thin CLI surface for a shared access-key implementation and creates service/access key pairs with optional credentials, policy, name, description, and expiry flags.

## Important APIs, types, and functions
Defines command-specific flags/help where needed, a `cli.Command` value with `Before: setGlobalsFromContext`, `OnUsageError`, global flags, and a `mainAdmin...` handler.

## Control flow
After CLI parsing and global setup, the handler delegates to `commonAccesskeyCreate(ctx, false)`. Syntax validation, admin-client creation, server calls, and output formatting are centralized in the shared helper.

## State and persistence behavior
No local persistence. Successful execution mutates MinIO server IAM/access-key state through the admin API used by the delegate.

## Dependencies and integration points
Depends on `github.com/minio/cli`, global flag plumbing, shared access-key helpers, MinIO admin client construction, fatal error handling, and `accesskeyMessage` output from related files.

## Risks and test signals
Risks sit mostly in shared helpers and flag semantics: expiry parsing, policy-file handling, and target/user/access-key argument order. CLI tests should verify help text, flag registration, delegate path, and server API request shape.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-disable.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-disable.go

## Purpose
Registers the MinIO admin access key disable command. The file is a thin CLI surface for a shared access-key implementation and disables an access key without removing it.

## Important APIs, types, and functions
Defines command-specific flags/help where needed, a `cli.Command` value with `Before: setGlobalsFromContext`, `OnUsageError`, global flags, and a `mainAdmin...` handler.

## Control flow
After CLI parsing and global setup, the handler delegates to `enableDisableAccesskey(ctx, false)`. Syntax validation, admin-client creation, server calls, and output formatting are centralized in the shared helper.

## State and persistence behavior
No local persistence. Successful execution mutates MinIO server IAM/access-key state through the admin API used by the delegate.

## Dependencies and integration points
Depends on `github.com/minio/cli`, global flag plumbing, shared access-key helpers, MinIO admin client construction, fatal error handling, and `accesskeyMessage` output from related files.

## Risks and test signals
Risks sit mostly in shared helpers and flag semantics: expiry parsing, policy-file handling, and target/user/access-key argument order. CLI tests should verify help text, flag registration, delegate path, and server API request shape.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-disable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-edit.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-edit.go

## Purpose
Registers the MinIO admin access key edit command. The file is a thin CLI surface for a shared access-key implementation and updates service/access key secret, policy, metadata, or expiry.

## Important APIs, types, and functions
Defines command-specific flags/help where needed, a `cli.Command` value with `Before: setGlobalsFromContext`, `OnUsageError`, global flags, and a `mainAdmin...` handler.

## Control flow
After CLI parsing and global setup, the handler delegates to `commonAccesskeyEdit(ctx)`. Syntax validation, admin-client creation, server calls, and output formatting are centralized in the shared helper.

## State and persistence behavior
No local persistence. Successful execution mutates MinIO server IAM/access-key state through the admin API used by the delegate.

## Dependencies and integration points
Depends on `github.com/minio/cli`, global flag plumbing, shared access-key helpers, MinIO admin client construction, fatal error handling, and `accesskeyMessage` output from related files.

## Risks and test signals
Risks sit mostly in shared helpers and flag semantics: expiry parsing, policy-file handling, and target/user/access-key argument order. CLI tests should verify help text, flag registration, delegate path, and server API request shape.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-edit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-enable.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-enable.go

## Purpose
Registers the MinIO admin access key enable command. The file is a thin CLI surface for a shared access-key implementation and reenables a disabled access key.

## Important APIs, types, and functions
Defines command-specific flags/help where needed, a `cli.Command` value with `Before: setGlobalsFromContext`, `OnUsageError`, global flags, and a `mainAdmin...` handler.

## Control flow
After CLI parsing and global setup, the handler delegates to `enableDisableAccesskey(ctx, true)`. Syntax validation, admin-client creation, server calls, and output formatting are centralized in the shared helper.

## State and persistence behavior
No local persistence. Successful execution mutates MinIO server IAM/access-key state through the admin API used by the delegate.

## Dependencies and integration points
Depends on `github.com/minio/cli`, global flag plumbing, shared access-key helpers, MinIO admin client construction, fatal error handling, and `accesskeyMessage` output from related files.

## Risks and test signals
Risks sit mostly in shared helpers and flag semantics: expiry parsing, policy-file handling, and target/user/access-key argument order. CLI tests should verify help text, flag registration, delegate path, and server API request shape.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-info.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-info.go

## Purpose
Implements `mc admin accesskey info`, retrieving and formatting metadata for one or more access keys including parent user, policy source, status, expiration, STS flag, and identity-provider details.

## Important APIs, types, and functions
Defines `adminAccesskeyInfoCmd`, `accesskeyMessage` with `String`/`JSON`, `providerInfo`, `mainAdminAccesskeyInfo`, `commonAccesskeyInfo`, and `nilExpiry`.

## Control flow
The command requires target plus at least one access key, creates an admin client, calls `InfoAccessKey` for each key, maps LDAP/OpenID provider-specific fields into display structs, and prints each message.

## State and persistence behavior
No local persistence. It reads server IAM/access-key state and emits text or JSON.

## Dependencies and integration points
Uses madmin access-key APIs, colorjson, lipgloss styling, humanized expiration times, shared CLI/probe/error helpers, and provider-specific message types defined elsewhere.

## Risks and test signals
Provider-specific nil fields and sentinel expiration handling are edge cases. Tests should cover multiple keys, LDAP/OpenID/builtin providers, JSON redaction/omitempty behavior, and disabled status rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-list.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-list.go

## Purpose
Implements `mc admin accesskey list/ls`, listing users and their STS/service-account access keys with filters for self, all, temporary-only, service-account-only, and users-only views.

## Important APIs, types, and functions
Defines list flags, `adminAccesskeyListCmd`, `userAccesskeyList` with `String`/`JSON`, and `mainAdminAccesskeyList`.

## Control flow
Shared `commonAccesskeyList` parses alias/users/options. The command calls `ListAccessKeysBulk`; if an unauthenticated all-users probe gets Access Denied under tentative-all mode, it retries without `All`. Results are printed per user.

## State and persistence behavior
Read-only against server IAM state. No local files are written.

## Dependencies and integration points
Depends on madmin `ServiceAccountInfo`, shared access-key listing parser, colorjson, lipgloss, humanized expiration, and global output mode.

## Risks and test signals
String comparison on `Access Denied.` is brittle. Tests should cover self/all fallback, LDAP label mode, empty users, filter combinations, and JSON output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-remove.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-remove.go

## Purpose
Registers the MinIO admin access key remove command. The file is a thin CLI surface for a shared access-key implementation and deletes an access key.

## Important APIs, types, and functions
Defines command-specific flags/help where needed, a `cli.Command` value with `Before: setGlobalsFromContext`, `OnUsageError`, global flags, and a `mainAdmin...` handler.

## Control flow
After CLI parsing and global setup, the handler delegates to `commonAccesskeyRemove(ctx)`. Syntax validation, admin-client creation, server calls, and output formatting are centralized in the shared helper.

## State and persistence behavior
No local persistence. Successful execution mutates MinIO server IAM/access-key state through the admin API used by the delegate.

## Dependencies and integration points
Depends on `github.com/minio/cli`, global flag plumbing, shared access-key helpers, MinIO admin client construction, fatal error handling, and `accesskeyMessage` output from related files.

## Risks and test signals
Risks sit mostly in shared helpers and flag semantics: expiry parsing, policy-file handling, and target/user/access-key argument order. CLI tests should verify help text, flag registration, delegate path, and server API request shape.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-sts-revoke.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey-sts-revoke.go

## Purpose
Implements `mc admin accesskey sts-revoke`, revoking all STS tokens or a specific token type for a named user or the authenticated user.

## Important APIs, types, and functions
Defines flags `--all`, `--self`, and `--token-type`, `adminAccesskeySTSRevokeCmd`, `stsRevokeMessage`, `checkSTSRevokeSyntax`, and `mainAdminAccesskeySTSRevoke`.

## Control flow
Syntax validation enforces target presence, user-vs-self exclusivity, and exactly one revoke mode. The handler creates an admin client, calls `RevokeTokens` with `madmin.RevokeTokensReq`, and prints a success message.

## State and persistence behavior
No local persistence. It mutates server-side STS/token state through the admin API.

## Dependencies and integration points
Depends on madmin token revoke API, shared CLI/probe/fatal handling, and MinIO output formatting.

## Risks and test signals
Argument exclusivity is critical to avoid revoking wrong tokens. Tests should cover all invalid flag combinations, self mode, named user mode, token-type mode, and API error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey-sts-revoke.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey.go -->
# sources/object-store/minio-mc/cmd/admin-accesskey.go

## Purpose
Command group registration for `mc admin accesskey`, collecting all access-key management subcommands.

## Important APIs, types, and functions
`adminAccesskeySubcommands` lists list, remove, info, create, edit, enable, disable, and STS revoke commands. `adminAccesskeyCmd` registers the group and `mainAdminAccesskey` handles missing subcommands.

## Control flow
CLI dispatch enters the group; if no valid subcommand is provided, `commandNotFound` reports usage. Real behavior lives in subcommand files.

## State and persistence behavior
No state directly. Subcommands mutate or read server IAM state.

## Dependencies and integration points
Depends on `github.com/minio/cli`, global flags, and all access-key subcommand variables.

## Risks and test signals
Subcommand ordering affects help output. Compile catches missing command variables; CLI tests should verify unknown subcommand handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-accesskey.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-info.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-info.go

## Purpose
Compatibility command wrapper for deprecated `mc admin bucket info`. It keeps the old CLI entry point registered while directing users to `mc stat`.

## Important APIs, types, and functions
Defines a `cli.Command` with name/usage/action/global flags and a `main...` handler that calls `deprecatedError`.

## Control flow
CLI dispatch reaches the handler, which immediately reports the replacement command `mc stat` and returns without contacting a MinIO server.

## State and persistence behavior
No state is read or written. The command exists for user migration only.

## Dependencies and integration points
Depends on the shared `github.com/minio/cli` command framework, global flags, usage-error handling, and `deprecatedError` messaging.

## Risks and test signals
The main risk is stale replacement guidance. Tests should assert the command remains hidden or deprecated as intended and emits the expected replacement text.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-quota.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-quota.go

## Purpose
Compatibility command wrapper for deprecated `mc admin bucket quota`. It keeps the old CLI entry point registered while directing users to `mc quota`.

## Important APIs, types, and functions
Defines a `cli.Command` with name/usage/action/global flags and a `main...` handler that calls `deprecatedError`.

## Control flow
CLI dispatch reaches the handler, which immediately reports the replacement command `mc quota` and returns without contacting a MinIO server.

## State and persistence behavior
No state is read or written. The command exists for user migration only.

## Dependencies and integration points
Depends on the shared `github.com/minio/cli` command framework, global flags, usage-error handling, and `deprecatedError` messaging.

## Risks and test signals
The main risk is stale replacement guidance. Tests should assert the command remains hidden or deprecated as intended and emits the expected replacement text.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-quota.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-add.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-remote-add.go

## Purpose
Compatibility command wrapper for deprecated `mc admin bucket remote add`. It keeps the old CLI entry point registered while directing users to `mc replicate add`.

## Important APIs, types, and functions
Defines a `cli.Command` with name/usage/action/global flags and a `main...` handler that calls `deprecatedError`.

## Control flow
CLI dispatch reaches the handler, which immediately reports the replacement command `mc replicate add` and returns without contacting a MinIO server.

## State and persistence behavior
No state is read or written. The command exists for user migration only.

## Dependencies and integration points
Depends on the shared `github.com/minio/cli` command framework, global flags, usage-error handling, and `deprecatedError` messaging.

## Risks and test signals
The main risk is stale replacement guidance. Tests should assert the command remains hidden or deprecated as intended and emits the expected replacement text.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-add.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-add_test.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-remote-add_test.go

## Purpose
Unit test coverage for bandwidth string parsing used by replication/remote bucket configuration helpers.

## Important APIs, types, and functions
`TestGetBandwidthInBytes` table-tests `getBandwidthInBytes` with decimal SI units (`M`, `G`), binary IEC units (`Mi`, `Gi`, `Ki`), fractional values, very large values, and small values.

## Control flow
The test runs in parallel and iterates cases, failing if parsing returns an error or a byte count different from the expected integer.

## State and persistence behavior
No state or persistence. It validates pure parsing behavior.

## Dependencies and integration points
Targets helper logic used by bucket remote/replication configuration even though surrounding admin remote commands are deprecated wrappers.

## Risks and test signals
Float truncation/rounding is the main risk for fractional units. The table is the direct signal for expected decimal-vs-binary semantics.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-add_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-edit.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-remote-edit.go

## Purpose
Compatibility command wrapper for deprecated `mc admin bucket remote edit`. It keeps the old CLI entry point registered while directing users to `mc replicate update`.

## Important APIs, types, and functions
Defines a `cli.Command` with name/usage/action/global flags and a `main...` handler that calls `deprecatedError`.

## Control flow
CLI dispatch reaches the handler, which immediately reports the replacement command `mc replicate update` and returns without contacting a MinIO server.

## State and persistence behavior
No state is read or written. The command exists for user migration only.

## Dependencies and integration points
Depends on the shared `github.com/minio/cli` command framework, global flags, usage-error handling, and `deprecatedError` messaging.

## Risks and test signals
The main risk is stale replacement guidance. Tests should assert the command remains hidden or deprecated as intended and emits the expected replacement text.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-edit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-main.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-remote-main.go

## Purpose
CLI command group registration for `mc admin bucket remote`, collecting related subcommands and providing common missing-subcommand behavior.

## Important APIs, types, and functions
Defines a `[]cli.Command` subcommand slice, a parent `cli.Command` with global setup/flags/subcommands, and a `main...` handler that calls `commandNotFound`.

## Control flow
The parent command does not perform server operations itself. CLI dispatch either routes to a registered subcommand or invokes the handler for usage/error reporting.

## State and persistence behavior
No direct state. Child commands may read or mutate server configuration, IAM, bucket metadata, or deprecated command state.

## Dependencies and integration points
Depends on MinIO's CLI package, global flag setup, and the subcommand variables declared in sibling files.

## Risks and test signals
A missing subcommand in the slice makes an implemented command unreachable. Compile and CLI help/dispatch tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-remove.go -->
# sources/object-store/minio-mc/cmd/admin-bucket-remote-remove.go

## Purpose
Compatibility command wrapper for deprecated `mc admin bucket remote remove`. It keeps the old CLI entry point registered while directing users to `mc replicate rm`.

## Important APIs, types, and functions
Defines a `cli.Command` with name/usage/action/global flags and a `main...` handler that calls `deprecatedError`.

## Control flow
CLI dispatch reaches the handler, which immediately reports the replacement command `mc replicate rm` and returns without contacting a MinIO server.

## State and persistence behavior
No state is read or written. The command exists for user migration only.

## Dependencies and integration points
Depends on the shared `github.com/minio/cli` command framework, global flags, usage-error handling, and `deprecatedError` messaging.

## Risks and test signals
The main risk is stale replacement guidance. Tests should assert the command remains hidden or deprecated as intended and emits the expected replacement text.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket-remote-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket.go -->
# sources/object-store/minio-mc/cmd/admin-bucket.go

## Purpose
CLI command group registration for `mc admin bucket`, collecting related subcommands and providing common missing-subcommand behavior.

## Important APIs, types, and functions
Defines a `[]cli.Command` subcommand slice, a parent `cli.Command` with global setup/flags/subcommands, and a `main...` handler that calls `commandNotFound`.

## Control flow
The parent command does not perform server operations itself. CLI dispatch either routes to a registered subcommand or invokes the handler for usage/error reporting.

## State and persistence behavior
No direct state. Child commands may read or mutate server configuration, IAM, bucket metadata, or deprecated command state.

## Dependencies and integration points
Depends on MinIO's CLI package, global flag setup, and the subcommand variables declared in sibling files.

## Risks and test signals
A missing subcommand in the slice makes an implemented command unreachable. Compile and CLI help/dispatch tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-bucket-export.go -->
# sources/object-store/minio-mc/cmd/admin-cluster-bucket-export.go

## Purpose
Implements cluster bucket export, downloading bucket metadata from a MinIO server into a local zip file for backup or migration.

## Important APIs, types, and functions
Defines a `cli.Command`, syntax checker for `target/[bucket]`, and main handler. The handler creates an admin client, calls `ExportBucketMetadata`, writes a temp file, backs up any existing destination, renames into place, chmods to `0600`, and prints text or JSON.

## Control flow
After syntax validation and alias normalization, the command streams server response to a temp file. Existing destination files are moved aside with a timestamp before the temp file is atomically moved into the final path.

## State and persistence behavior
Writes local backup zip files and backup copies of prior outputs. Server state is read-only. Output permissions are tightened to avoid world-readable metadata.

## Dependencies and integration points
Depends on madmin export APIs, filesystem helpers such as `moveFile`, global JSON mode, console coloring, and MinIO probe errors.

## Risks and test signals
Path construction from aliases can create surprising local paths; export contains sensitive metadata. Tests should cover existing destination backup, custom output where supported, permission mode, JSON output, and stream copy failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-bucket-export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-bucket-import.go -->
# sources/object-store/minio-mc/cmd/admin-cluster-bucket-import.go

## Purpose
Implements cluster bucket import, restoring bucket metadata from a local zip file into a MinIO cluster.

## Important APIs, types, and functions
Defines a `cli.Command`, zip validation/syntax logic, main handler, and `importMetaMsg` output formatter. It uses madmin import result types to render successes, skips, removals, additions, and errors.

## Control flow
The command validates argument count, opens the zip file, creates a `zip.NewReader` to reject invalid archives, reopens the file for streaming, creates an admin client, calls `ImportBucketMetadata`, and prints structured results.

## State and persistence behavior
Reads a local zip backup and mutates server-side metadata/IAM state. No local output is persisted beyond terminal/JSON output.

## Dependencies and integration points
Depends on `klauspost/compress/zip`, madmin import APIs, console coloring, shared probe/fatal handling, and global output mode.

## Risks and test signals
Import is high impact: wrong target or stale backup can overwrite server metadata. Tests should cover invalid zip rejection, partial import error rendering, JSON output, and fallback behavior where present.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-bucket-import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-bucket.go -->
# sources/object-store/minio-mc/cmd/admin-cluster-bucket.go

## Purpose
CLI command group registration for `mc admin cluster bucket`, collecting related subcommands and providing common missing-subcommand behavior.

## Important APIs, types, and functions
Defines a `[]cli.Command` subcommand slice, a parent `cli.Command` with global setup/flags/subcommands, and a `main...` handler that calls `commandNotFound`.

## Control flow
The parent command does not perform server operations itself. CLI dispatch either routes to a registered subcommand or invokes the handler for usage/error reporting.

## State and persistence behavior
No direct state. Child commands may read or mutate server configuration, IAM, bucket metadata, or deprecated command state.

## Dependencies and integration points
Depends on MinIO's CLI package, global flag setup, and the subcommand variables declared in sibling files.

## Risks and test signals
A missing subcommand in the slice makes an implemented command unreachable. Compile and CLI help/dispatch tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-iam-export.go -->
# sources/object-store/minio-mc/cmd/admin-cluster-iam-export.go

## Purpose
Implements cluster iam export, downloading IAM info from a MinIO server into a local zip file for backup or migration.

## Important APIs, types, and functions
Defines a `cli.Command`, syntax checker for `target`, and main handler. The handler creates an admin client, calls `ExportIAM`, writes a temp file, backs up any existing destination, renames into place, chmods to `0600`, and prints text or JSON.

## Control flow
After syntax validation and alias normalization, the command streams server response to a temp file. Existing destination files are moved aside with a timestamp before the temp file is atomically moved into the final path.

## State and persistence behavior
Writes local backup zip files and backup copies of prior outputs. Server state is read-only. Output permissions are tightened to avoid world-readable metadata.

## Dependencies and integration points
Depends on madmin export APIs, filesystem helpers such as `moveFile`, global JSON mode, console coloring, and MinIO probe errors.

## Risks and test signals
Path construction from aliases can create surprising local paths; export contains sensitive metadata. Tests should cover existing destination backup, custom output where supported, permission mode, JSON output, and stream copy failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-iam-export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-iam-import.go -->
# sources/object-store/minio-mc/cmd/admin-cluster-iam-import.go

## Purpose
Implements cluster IAM import, restoring IAM info from a local zip file into a MinIO cluster.

## Important APIs, types, and functions
Defines a `cli.Command`, zip validation/syntax logic, main handler, and `iamImportInfo` output formatter. It uses madmin import result types to render successes, skips, removals, additions, and errors.

## Control flow
The command validates argument count, opens the zip file, creates a `zip.NewReader` to reject invalid archives, reopens the file for streaming, creates an admin client, calls `ImportIAMV2 with fallback to ImportIAM`, and prints structured results.

## State and persistence behavior
Reads a local zip backup and mutates server-side metadata/IAM state. No local output is persisted beyond terminal/JSON output.

## Dependencies and integration points
Depends on `klauspost/compress/zip`, madmin import APIs, console coloring, shared probe/fatal handling, and global output mode.

## Risks and test signals
Import is high impact: wrong target or stale backup can overwrite server metadata. Tests should cover invalid zip rejection, partial import error rendering, JSON output, and fallback behavior where present.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-iam-import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-iam.go -->
# sources/object-store/minio-mc/cmd/admin-cluster-iam.go

## Purpose
CLI command group registration for `mc admin cluster iam`, collecting related subcommands and providing common missing-subcommand behavior.

## Important APIs, types, and functions
Defines a `[]cli.Command` subcommand slice, a parent `cli.Command` with global setup/flags/subcommands, and a `main...` handler that calls `commandNotFound`.

## Control flow
The parent command does not perform server operations itself. CLI dispatch either routes to a registered subcommand or invokes the handler for usage/error reporting.

## State and persistence behavior
No direct state. Child commands may read or mutate server configuration, IAM, bucket metadata, or deprecated command state.

## Dependencies and integration points
Depends on MinIO's CLI package, global flag setup, and the subcommand variables declared in sibling files.

## Risks and test signals
A missing subcommand in the slice makes an implemented command unreachable. Compile and CLI help/dispatch tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster-iam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster.go -->
# sources/object-store/minio-mc/cmd/admin-cluster.go

## Purpose
CLI command group registration for `mc admin cluster`, collecting related subcommands and providing common missing-subcommand behavior.

## Important APIs, types, and functions
Defines a `[]cli.Command` subcommand slice, a parent `cli.Command` with global setup/flags/subcommands, and a `main...` handler that calls `commandNotFound`.

## Control flow
The parent command does not perform server operations itself. CLI dispatch either routes to a registered subcommand or invokes the handler for usage/error reporting.

## State and persistence behavior
No direct state. Child commands may read or mutate server configuration, IAM, bucket metadata, or deprecated command state.

## Dependencies and integration points
Depends on MinIO's CLI package, global flag setup, and the subcommand variables declared in sibling files.

## Risks and test signals
A missing subcommand in the slice makes an implemented command unreachable. Compile and CLI help/dispatch tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-export.go -->
# sources/object-store/minio-mc/cmd/admin-config-export.go

## Purpose
Implements `mc admin config export`, which exports all server config keys to STDOUT.

## Important APIs, types, and functions
Defines command flags/help, syntax checker, output message type `configExportMessage`, and main handler. Server interaction is through madmin `GetConfig`.

## Control flow
The handler validates arguments, initializes an admin client from the target alias, branches for help/list/clear modes where applicable, calls the relevant server API, and prints a text or JSON message.

## State and persistence behavior
No local persistence except reading STDIN for import. Commands read or mutate server-side MinIO configuration and may require a service restart, which is reported in output messages.

## Dependencies and integration points
Depends on MinIO CLI globals, madmin config APIs, colorjson/template rendering for output, console coloring, and probe/fatal error handling.

## Risks and test signals
Configuration commands are operationally sensitive: malformed key strings, env-only help, restart-required flags, and history restore ids need strict tests. Signals include API request correctness, JSON output, help rendering, and restart guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-get.go -->
# sources/object-store/minio-mc/cmd/admin-config-get.go

## Purpose
Implements `mc admin config get`, which retrieves a subsystem config key or shows help when no subsystem is provided.

## Important APIs, types, and functions
Defines command flags/help, syntax checker, output message type `configGetMessage/configHelpMessage`, and main handler. Server interaction is through madmin `GetConfigKV/HelpConfigKV`.

## Control flow
The handler validates arguments, initializes an admin client from the target alias, branches for help/list/clear modes where applicable, calls the relevant server API, and prints a text or JSON message.

## State and persistence behavior
No local persistence except reading STDIN for import. Commands read or mutate server-side MinIO configuration and may require a service restart, which is reported in output messages.

## Dependencies and integration points
Depends on MinIO CLI globals, madmin config APIs, colorjson/template rendering for output, console coloring, and probe/fatal error handling.

## Risks and test signals
Configuration commands are operationally sensitive: malformed key strings, env-only help, restart-required flags, and history restore ids need strict tests. Signals include API request correctness, JSON output, help rendering, and restart guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-help.go -->
# sources/object-store/minio-mc/cmd/admin-config-help.go

## Purpose
Shared rendering helpers for MinIO admin config help output in text and JSON forms.

## Important APIs, types, and functions
Defines `HelpTmpl`, `funcMap`, parsed `HelpTemplate` and `HelpEnvTemplate`, and `configHelpMessage` with `String` and `JSON`.

## Control flow
Commands construct `configHelpMessage` from madmin help responses. `String` chooses normal or env-only template and executes it into a buffer; `JSON` marshals the raw help response.

## State and persistence behavior
No state. It formats server-provided config help metadata.

## Dependencies and integration points
Used by config get/set/reset paths. Depends on Go templates, color functions, colorjson, console/probe helpers, and madmin help response shape.

## Risks and test signals
Template field drift in madmin help structs can break output at runtime. Tests should cover env-only and normal templates, JSON output, and empty subsystem help.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-help.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-history.go -->
# sources/object-store/minio-mc/cmd/admin-config-history.go

## Purpose
Implements `mc admin config history`, which lists or clears historic configuration changes.

## Important APIs, types, and functions
Defines command flags/help, syntax checker, output message type `configHistoryMessage`, and main handler. Server interaction is through madmin `ListConfigHistoryKV/ClearConfigHistoryKV`.

## Control flow
The handler validates arguments, initializes an admin client from the target alias, branches for help/list/clear modes where applicable, calls the relevant server API, and prints a text or JSON message.

## State and persistence behavior
No local persistence except reading STDIN for import. Commands read or mutate server-side MinIO configuration and may require a service restart, which is reported in output messages.

## Dependencies and integration points
Depends on MinIO CLI globals, madmin config APIs, colorjson/template rendering for output, console coloring, and probe/fatal error handling.

## Risks and test signals
Configuration commands are operationally sensitive: malformed key strings, env-only help, restart-required flags, and history restore ids need strict tests. Signals include API request correctness, JSON output, help rendering, and restart guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-history.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-import.go -->
# sources/object-store/minio-mc/cmd/admin-config-import.go

## Purpose
Implements `mc admin config import`, which imports multiple config keys from STDIN.

## Important APIs, types, and functions
Defines command flags/help, syntax checker, output message type `configImportMessage`, and main handler. Server interaction is through madmin `SetConfig`.

## Control flow
The handler validates arguments, initializes an admin client from the target alias, branches for help/list/clear modes where applicable, calls the relevant server API, and prints a text or JSON message.

## State and persistence behavior
No local persistence except reading STDIN for import. Commands read or mutate server-side MinIO configuration and may require a service restart, which is reported in output messages.

## Dependencies and integration points
Depends on MinIO CLI globals, madmin config APIs, colorjson/template rendering for output, console coloring, and probe/fatal error handling.

## Risks and test signals
Configuration commands are operationally sensitive: malformed key strings, env-only help, restart-required flags, and history restore ids need strict tests. Signals include API request correctness, JSON output, help rendering, and restart guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-import.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-reset.go -->
# sources/object-store/minio-mc/cmd/admin-config-reset.go

## Purpose
Implements `mc admin config reset`, which resets subsystem config keys or lists reset help.

## Important APIs, types, and functions
Defines command flags/help, syntax checker, output message type `configResetMessage`, and main handler. Server interaction is through madmin `DelConfigKV/HelpConfigKV`.

## Control flow
The handler validates arguments, initializes an admin client from the target alias, branches for help/list/clear modes where applicable, calls the relevant server API, and prints a text or JSON message.

## State and persistence behavior
No local persistence except reading STDIN for import. Commands read or mutate server-side MinIO configuration and may require a service restart, which is reported in output messages.

## Dependencies and integration points
Depends on MinIO CLI globals, madmin config APIs, colorjson/template rendering for output, console coloring, and probe/fatal error handling.

## Risks and test signals
Configuration commands are operationally sensitive: malformed key strings, env-only help, restart-required flags, and history restore ids need strict tests. Signals include API request correctness, JSON output, help rendering, and restart guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-reset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-restore.go -->
# sources/object-store/minio-mc/cmd/admin-config-restore.go

## Purpose
Implements `mc admin config restore`, which restores server config from a history restore id.

## Important APIs, types, and functions
Defines command flags/help, syntax checker, output message type `configRestoreMessage`, and main handler. Server interaction is through madmin `RestoreConfigHistoryKV`.

## Control flow
The handler validates arguments, initializes an admin client from the target alias, branches for help/list/clear modes where applicable, calls the relevant server API, and prints a text or JSON message.

## State and persistence behavior
No local persistence except reading STDIN for import. Commands read or mutate server-side MinIO configuration and may require a service restart, which is reported in output messages.

## Dependencies and integration points
Depends on MinIO CLI globals, madmin config APIs, colorjson/template rendering for output, console coloring, and probe/fatal error handling.

## Risks and test signals
Configuration commands are operationally sensitive: malformed key strings, env-only help, restart-required flags, and history restore ids need strict tests. Signals include API request correctness, JSON output, help rendering, and restart guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-set.go -->
# sources/object-store/minio-mc/cmd/admin-config-set.go

## Purpose
Implements `mc admin config set`, which sets subsystem config key/value strings or shows help when no key/value separator is present.

## Important APIs, types, and functions
Defines command flags/help, syntax checker, output message type `configSetMessage`, and main handler. Server interaction is through madmin `SetConfigKV/HelpConfigKV`.

## Control flow
The handler validates arguments, initializes an admin client from the target alias, branches for help/list/clear modes where applicable, calls the relevant server API, and prints a text or JSON message.

## State and persistence behavior
No local persistence except reading STDIN for import. Commands read or mutate server-side MinIO configuration and may require a service restart, which is reported in output messages.

## Dependencies and integration points
Depends on MinIO CLI globals, madmin config APIs, colorjson/template rendering for output, console coloring, and probe/fatal error handling.

## Risks and test signals
Configuration commands are operationally sensitive: malformed key strings, env-only help, restart-required flags, and history restore ids need strict tests. Signals include API request correctness, JSON output, help rendering, and restart guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config.go -->
# sources/object-store/minio-mc/cmd/admin-config.go

## Purpose
CLI command group registration for `mc admin config`, collecting related subcommands and providing common missing-subcommand behavior.

## Important APIs, types, and functions
Defines a `[]cli.Command` subcommand slice, a parent `cli.Command` with global setup/flags/subcommands, and a `main...` handler that calls `commandNotFound`.

## Control flow
The parent command does not perform server operations itself. CLI dispatch either routes to a registered subcommand or invokes the handler for usage/error reporting.

## State and persistence behavior
No direct state. Child commands may read or mutate server configuration, IAM, bucket metadata, or deprecated command state.

## Dependencies and integration points
Depends on MinIO's CLI package, global flag setup, and the subcommand variables declared in sibling files.

## Risks and test signals
A missing subcommand in the slice makes an implemented command unreachable. Compile and CLI help/dispatch tests are the main signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-console.go -->
# sources/object-store/minio-mc/cmd/admin-console.go

## Purpose
Deprecated compatibility wrapper for `mc admin console`, redirecting users to `mc admin logs` while preserving old flags.

## Important APIs, types, and functions
Defines flags `--limit/-l` and `--type/-t`, hidden `adminConsoleCmd`, and `mainAdminConsole`.

## Control flow
The handler builds a replacement command string starting with `mc admin logs`, maps `limit` to `--last`, lowercases `type`, appends positional args, and calls `deprecatedError`.

## State and persistence behavior
No state and no server calls.

## Dependencies and integration points
Depends on MinIO CLI flag parsing and shared deprecation messaging.

## Risks and test signals
Replacement command synthesis must match the current logs command flags. Tests should cover no flags, limit, type case normalization, and passthrough args.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-console.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-cancel.go -->
# sources/object-store/minio-mc/cmd/admin-decom-cancel.go

## Purpose
Implements `mc admin decommission cancel`, cancelling a specific pool decommission or listing cancellable in-progress decommissions when no pool is supplied.

## Important APIs, types, and functions
Defines `adminDecommissionCancelCmd`, `checkAdminDecommissionCancelSyntax`, and `mainAdminDecommissionCancel`.

## Control flow
The command accepts target plus optional pool. With a pool, it calls `CancelDecommissionPool`. Without a pool, it calls `ListPoolsStatus`, filters started and incomplete decommissions, formats capacity/status rows, and displays a table.

## State and persistence behavior
Specific-pool mode mutates server decommission state. Listing mode is read-only. No local state is persisted.

## Dependencies and integration points
Depends on madmin pool status/decommission APIs, humanize formatting, console tables, color setup, and shared CLI/probe helpers.

## Risks and test signals
The table allocation uses filtered length but iterates original statuses with incremented indexes, which can be fragile if skipped rows create gaps. Tests should cover no active pools, mixed complete/incomplete pools, specific cancellation, and JSON expectations if added later.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-cancel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-start.go -->
# sources/object-store/minio-mc/cmd/admin-decom-start.go

## Purpose
Implements `mc admin decommission start`, starting decommissioning for a specified server pool.

## Important APIs, types, and functions
Defines `adminDecommissionStartCmd`, `checkAdminDecommissionStartSyntax`, `startDecomMessage` with `String`/`JSON`, and `mainAdminDecommissionStart`.

## Control flow
Requires exactly target and pool arguments, cleans the target alias, creates an admin client, calls `DecommissionPool`, and prints success for the pool.

## State and persistence behavior
No local persistence. It mutates server-side pool decommission state.

## Dependencies and integration points
Depends on madmin decommission API through the admin client, console coloring, colorjson, global context, and probe/fatal handling.

## Risks and test signals
Wrong pool argument can initiate disruptive data movement. Tests should cover syntax validation, API errors, JSON/text output, and alias cleaning.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-decom-start.go -->
