# subset-b-008281 RustFS Swift tests and protos generated module research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/tests/swift_listing_symlink_tests.rs -->
# sources/object-store/rustfs/crates/protocols/tests/swift_listing_symlink_tests.rs

## Purpose

This Swift-feature-gated Rust test module exercises the symlink helpers in `rustfs_protocols::swift::symlink`. The module-level comment also names container-listing coverage, but the actual source file is focused on symlink metadata detection, target parsing, empty/invalid target handling, special characters, loop-detection data structure expectations, maximum traversal depth, and the boundary between symlink targets and request query parameters.

## Important APIs, types, and functions

- Imports `rustfs_protocols::swift::symlink::*` and uses `HashMap<String, String>` as object metadata.
- `is_symlink(&HashMap<String, String>)` is expected to return true solely when metadata contains `x-object-symlink-target`.
- `get_symlink_target(&HashMap<String, String>)` returns `SwiftResult<Option<SymlinkTarget>>`, producing `None` when the header is absent and an error when the header exists but cannot be parsed.
- `SymlinkTarget::parse(&str)` accepts `container/object`, nested object paths after the first slash, and same-container object names without slash.
- `SymlinkTarget` exposes `container: Option<String>` and `object: String`.
- `validate_symlink_depth(depth: u8)` enforces a maximum depth of five hops, with depths `0..5` accepted and depth `5` rejected.

## Control flow

Each test constructs metadata or target strings, invokes a pure helper, and asserts either the parsed structure or the expected failure. Parsing is validated in two layers: direct `SymlinkTarget::parse` tests and metadata-driven `get_symlink_target` tests. Loop detection is represented by inserting link names into a `HashSet` and asserting that revisiting a prior link would be detectable. The depth test uses a local `MAX_SYMLINK_DEPTH` constant equal to the implementation limit and checks the boundary exactly.

## State and persistence behavior

There is no durable state. All state is local test data: metadata maps, parsed target values, and an in-memory `HashSet` representing visited symlink paths. The tests imply that production symlink traversal should maintain per-request visited state and depth counters rather than storing symlink resolution state in object metadata.

## Dependencies and integration points

The file depends on the `swift` Cargo feature and the Swift symlink module. It indirectly validates request-handler behavior because handlers write and read `x-object-symlink-target` metadata, while GET/HEAD code can later use `get_symlink_target`, `validate_symlink_depth`, and visited-path tracking to resolve links safely. The tests are also tied to Swift API header naming: the accepted header is `x-object-symlink-target`, not the shorter response header spelling.

## Risks and edge cases

- The module comment promises container listing tests, but no listing code appears in this file. That mismatch can mislead maintainers looking for prefix, delimiter, marker, or limit coverage.
- `is_symlink` is intentionally header-presence based. A metadata map with an empty or malformed target is still classified as a symlink and only fails when parsed.
- Query parameters are not stripped or parsed here; callers must ensure they pass only the target header value.
- The loop-detection test validates a generic `HashSet` pattern, not the implementation's `SymlinkPath` or `check_circular_reference` function.
- The tests use lower-case metadata keys, so they do not prove header normalization for mixed-case inputs.

## Test signals

This file provides focused unit test signals for valid and invalid target parsing, same-container targets, special-character preservation, empty target failure, metadata format expectations, and maximum symlink depth. Missing signals include real handler GET/HEAD symlink following, circular-reference errors through the production API, authorization checks, and container-listing behavior named in the header comment.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/tests/swift_listing_symlink_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/tests/swift_phase4_integration.rs -->
# sources/object-store/rustfs/crates/protocols/tests/swift_phase4_integration.rs

## Purpose

This Swift-feature-gated integration test module checks that Phase 4 Swift helper modules can be used together from the public `rustfs_protocols::swift::*` namespace. It is a lightweight cross-module smoke test rather than a storage-backed HTTP integration test.

## Important APIs, types, and functions

- Imports `rustfs_protocols::swift::*`, so the tests depend on the Swift module re-export surface.
- `symlink::is_symlink` and `symlink::get_symlink_target` are checked against metadata containing `x-object-symlink-target`.
- `expiration::parse_delete_at` parses a Unix timestamp string from `x-delete-at`.
- `ratelimit::RateLimiter::new`, `RateLimit { limit, window_seconds }`, and `check_rate_limit` are used to verify independent counters by key.
- `ratelimit::extract_rate_limit` parses account metadata from `x-account-meta-rate-limit` in `limit/window` format.

## Control flow

The first test is compile-only and exists to ensure the Phase 4 modules remain accessible. The symlink-expiration test builds one metadata map containing both a symlink target and an expiration timestamp, then verifies both modules can read their own headers without conflict. The rate-limit key test creates one limiter and applies the same policy to two keys in lockstep, verifying each key allows three requests and then rejects the fourth. The metadata extraction test parses `1000/60` into the expected limit and window.

## State and persistence behavior

There is no persisted state. The only mutable state is inside `RateLimiter`, which maintains in-memory per-key counters or token-bucket state for the life of the limiter instance. Metadata maps are local and demonstrate that Phase 4 features share object/account metadata by convention rather than through a central schema.

## Dependencies and integration points

The file depends on public Swift modules for symlink, expiration, and rate limiting. It integrates at the crate API level, confirming `rustfs_protocols::swift::*` exposes these helpers together under the `swift` feature. It does not instantiate the Swift HTTP handler or storage backend.

## Risks and edge cases

- The compile-only test has no assertions, so it only guards import viability.
- The rate-limit test assumes deterministic exhaustion after exactly `limit` successful calls with no refill during the test window.
- Expiration parsing uses a fixed future-like timestamp but does not validate expiration rejection, deletion scheduling, or clock behavior.
- Metadata coexistence is tested only for header key independence, not for handler serialization, persistence, or case normalization.

## Test signals

The module signals that Phase 4 metadata features can coexist and that rate limiting is isolated by key. It should catch public API breakage in module names or basic function signatures. It does not provide end-to-end HTTP/storage confidence.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/tests/swift_phase4_integration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/tests/swift_simple_integration.rs -->
# sources/object-store/rustfs/crates/protocols/tests/swift_simple_integration.rs

## Purpose

This Swift-feature-gated test module is a broad, simple integration smoke suite for Swift helper modules. It validates that encryption, sync, static large objects, TempURL, versioning, symlink detection, rate-limit parsing, quota structs, conflict resolution, and retry scheduling can all be used from one test crate.

## Important APIs, types, and functions

- `encryption::EncryptionConfig::new`, `encrypt_data`, and `EncryptionMetadata::to_headers` are checked for metadata generation and coexistence with user metadata.
- `sync::SyncConfig::from_metadata`, `generate_sync_signature`, `verify_sync_signature`, `resolve_conflict`, and `SyncQueueEntry` retry methods are exercised.
- `slo::SLOManifest`, `SLOSegment`, `calculate_etag`, and `total_size` are validated structurally.
- `tempurl::TempURL::new` and `generate_signature` must produce a 40-character HMAC-SHA1 hex signature.
- `versioning::generate_version_name` must include the original object names and vary across object inputs.
- `symlink::is_symlink` is called against metadata using `x-symlink-target`, which is not the canonical request metadata key used by `symlink.rs`.
- `ratelimit::RateLimit::parse` and `quota::QuotaConfig` are checked.

## Control flow

The tests are independent. They construct small domain values, call one or two helpers, and assert stable properties such as header values, deterministic signatures, signature length, SLO size, version-name inclusion, rate-limit numeric fields, quota fields, conflict decisions, and retry timestamps. No async runtime, HTTP server, or object storage is involved.

## State and persistence behavior

All state is local to the tests. Encryption produces ciphertext and metadata but does not persist keys. Sync retry state is held in a `SyncQueueEntry`, where `schedule_retry(2000)` increments `retry_count` and sets `next_retry` to `2060`. User metadata coexistence is represented by merging encryption headers with an object metadata key.

## Dependencies and integration points

This file depends on the public Swift helper modules exported by `rustfs_protocols`. The modules themselves integrate with cryptographic crates, HMAC signing conventions, Swift container-sync metadata headers, SLO manifest formats, and quota/rate-limit metadata contracts. The test suite verifies helper interoperability at the API level.

## Risks and edge cases

- The symlink detection test uses `x-symlink-target`, while the symlink implementation checks `x-object-symlink-target`; the test intentionally ignores the result, so it does not assert the canonical behavior.
- Encryption is not round-tripped with `decrypt_data`.
- SLO ETag coverage checks only a one-segment manifest and non-empty digest, not multi-segment ordering semantics.
- TempURL and sync signatures check length and determinism but not known test vectors.
- Versioning checks inclusion and inequality but not sort order or timestamp format; the dedicated versioning test file covers those.

## Test signals

This module is useful as a compilation and basic behavior canary across many Swift Phase 4 helpers. It can catch public API removals, major metadata-format changes, and simple regression in deterministic signing or retry math. It is not a substitute for storage-backed Swift API tests.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/tests/swift_simple_integration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/tests/swift_versioning_integration.rs -->
# sources/object-store/rustfs/crates/protocols/tests/swift_versioning_integration.rs

## Purpose

This Swift-feature-gated module comprehensively tests Swift object-version name generation. It focuses on the string contract used to archive object versions: an inverted timestamp prefix followed by container and object path segments. The tests cover format, ordering, path preservation, special characters, timestamp precision, uniqueness under sequential and concurrent generation, and cleanup/listing assumptions.

## Important APIs, types, and functions

- Imports `rustfs_protocols::swift::versioning::*`; the primary exercised API is `generate_version_name(container, object) -> String`.
- Version strings are expected to split as `{inverted_timestamp}/{container}/{object}` with `splitn(3, '/')` for ordinary containers.
- The timestamp component is expected to contain a decimal point, have a 10-digit whole part in stability tests, and have exactly nine fractional digits.
- Inverted timestamps are expected to make newer versions lexicographically smaller, so simple sorting can list newest versions first.
- Standard library concurrency primitives `Arc`, `Mutex`, and `thread` are used to stress concurrent generation.

## Control flow

The module creates version names under different timing and input scenarios. Format tests split the string and inspect timestamp and path components. Ordering tests generate versions with sleeps and compare adjacent strings. Precision and stress tests generate many names, count unique values with a `HashSet`, and enforce acceptable collision-rate thresholds rather than perfect uniqueness. Path tests assert version names preserve nested object paths and even container strings containing slashes. Metadata and cleanup tests verify surrounding structures that versioning workflows rely on.

## State and persistence behavior

There is no direct persistence. The version name itself encodes ordering state through current system time. The concurrent stress test stores generated strings in a mutex-protected vector. The metadata preservation test uses a local `HashMap` to model metadata that archive/restore workflows should preserve, but no archival storage is invoked.

## Dependencies and integration points

The tests depend on the Swift versioning helper and the system clock. In production, these version names integrate with object-copy or archive workflows where current objects are moved to a versions container/prefix and later restored on delete. The format is also an integration contract for listing, cleanup, and parsing because callers infer timestamp, container, and object from slash-delimited strings.

## Risks and edge cases

- Tests that depend on sleep duration and system clock precision can be flaky on very slow, very fast, or low-resolution platforms.
- Collision thresholds acknowledge that timestamp-only names are not a complete uniqueness mechanism under concurrent writes. The comments say production should use additional mechanisms such as UUIDs if strict uniqueness is required.
- Containers containing slashes make naive `splitn(3, '/')` parsing ambiguous. One test checks preservation for `"photos/2024"`, while another parser-style test assumes ordinary no-slash container names.
- Performance test includes 1000 sleeps of 10 microseconds but asserts total runtime below 200 ms, which may be tight under loaded CI.
- Empty container and object names are accepted by the generator tests even though they may not be valid Swift object names in production.

## Test signals

The suite strongly signals the expected version-name string contract: inverted timestamp, nine fractional digits, lexicographic newest-first sorting, and path preservation. It also documents tolerated collision rates and parser assumptions. It does not test actual PUT archive, DELETE restore, cross-account isolation in storage, or metadata persistence through real object operations.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/tests/swift_versioning_integration.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/Cargo.toml -->
# sources/object-store/rustfs/crates/protos/Cargo.toml

## Purpose

This manifest defines the `rustfs-protos` crate, whose description says it provides gRPC and FlatBuffers protocol interfaces for communication between RustFS components. It also declares a `gproto` binary at `src/main.rs`, likely used for protocol generation or inspection.

## Important APIs, types, and functions

- Package metadata uses workspace-managed `version`, `edition`, `license`, `repository`, `rust-version`, and `homepage`.
- `documentation` points to the docs.rs page for `rustfs-protos`.
- The crate opts into workspace lints with `[lints] workspace = true`.
- `[[bin]] name = "gproto"` maps to `src/main.rs`.
- `[lib] doctest = false` disables doctests for the library, which is common for generated protocol crates.
- Dependencies include internal crates `rustfs-common`, `rustfs-io-metrics`, `rustfs-config`, `rustfs-tls-runtime`, and `rustfs-utils`.
- Protocol/generation dependencies include `flatbuffers`, `prost`, `tonic`, `tonic-prost`, and `tonic-prost-build`.
- `tonic` enables `transport`, `tls-native-roots`, and `tls-aws-lc`; `tokio` enables only `sync`.

## Control flow

The manifest does not contain runtime control flow. Build-time behavior is determined by Cargo: it compiles the library, includes the `gproto` binary, links generated FlatBuffers and Prost/Tonic modules, and applies workspace dependency versions and lint settings.

## State and persistence behavior

There is no runtime state in the manifest. Persistent build behavior comes from Cargo metadata and workspace dependency resolution. The choice to include code-generation/build crates as normal dependencies means downstream builds may compile generation support even when only consuming generated modules.

## Dependencies and integration points

This crate sits between protocol schema files (`models.fbs`, `node.proto`), generated Rust modules under `src/generated`, and RustFS components needing typed gRPC or FlatBuffers messages. TLS-enabled `tonic` settings indicate that generated gRPC clients/servers can use secure transport with native roots and AWS-LC TLS support. Internal RustFS dependencies suggest protocol messages are not isolated DTOs only; the crate may also provide service wiring, metrics, config, TLS runtime integration, or utility support.

## Risks and edge cases

- Generated modules often produce clippy warnings; the source modules suppress those locally, but workspace lints can still affect hand-written code.
- Disabling doctests prevents generated examples from breaking builds but also reduces documentation verification.
- `tonic-prost-build` as a regular dependency can increase compile surface if it is only needed by the binary or build tooling.
- TLS feature selection couples protocol transport behavior to native roots and AWS-LC availability.
- Consumers must be aware that generated sources should not be manually edited.

## Test signals

The manifest itself has no tests. Useful validation signals are `cargo check -p rustfs-protos`, `cargo test -p rustfs-protos`, and any regeneration command through `gproto` that confirms generated gRPC and FlatBuffers outputs remain compatible with `prost`, `tonic`, and `flatbuffers`.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/generated/flatbuffers_generated/mod.rs -->
# sources/object-store/rustfs/crates/protos/src/generated/flatbuffers_generated/mod.rs

## Purpose

This generated-module wrapper exposes the FlatBuffers-generated Rust code below `flatbuffers_generated`. Its only item is `pub mod models;`, which makes the generated `models.rs` module available to the parent generated module.

## Important APIs, types, and functions

- `pub mod models;` declares and publicly exposes `flatbuffers_generated::models`.
- There are no functions, structs, constants, or state in this file.

## Control flow

The file has no runtime control flow. Cargo/Rust module resolution loads `models.rs` when this module is referenced.

## State and persistence behavior

There is no state or persistence. It is a compile-time namespace bridge.

## Dependencies and integration points

The module is consumed by `sources/object-store/rustfs/crates/protos/src/generated/mod.rs`, which declares `mod flatbuffers_generated;` and re-exports `flatbuffers_generated::models::*`. This means changing visibility or module names here directly affects the public generated API of `rustfs-protos`.

## Risks and edge cases

- Because this is generated-wrapper code, manual edits may be overwritten by the FlatBuffers generation pipeline.
- Removing `pub` would break the parent module's re-export path.
- Adding additional generated schemas here requires keeping parent re-exports and file generation in sync.

## Test signals

Compilation of `rustfs-protos` is the primary signal. Any consumer importing `rustfs_protos::generated::PingBody` through the parent re-export indirectly depends on this module declaration.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/generated/flatbuffers_generated/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/generated/flatbuffers_generated/models.rs -->
# sources/object-store/rustfs/crates/protos/src/generated/flatbuffers_generated/models.rs

## Purpose

This FlatBuffers-generated Rust file defines the `models` schema namespace for the protos crate. In the current source it contains one table, `PingBody`, with an optional byte-vector payload. The header marks it as compiler-generated and not intended for manual edits.

## Important APIs, types, and functions

- `extern crate alloc;` enables generated code to use allocation-compatible types in `alloc`.
- `pub mod models` contains all generated schema items.
- `PingBodyOffset` is an empty enum used as a generated offset marker.
- `PingBody<'a>` wraps `::flatbuffers::Table<'a>` in field `_tab`.
- `impl Follow for PingBody<'a>` lets FlatBuffers traverse a buffer into a `PingBody`.
- `PingBody::VT_PAYLOAD` is the vtable offset for the payload field.
- `PingBody::get_fully_qualified_name()` returns `"models.PingBody"`.
- `unsafe fn init_from_table` constructs a wrapper from a raw FlatBuffers table.
- `PingBody::create` builds a table using `PingBodyArgs`.
- `PingBody::payload()` returns `Option<::flatbuffers::Vector<'a, u8>>`.
- `impl Verifiable for PingBody` validates the optional byte-vector field.
- `PingBodyArgs<'a>` holds an optional FlatBuffers vector offset and implements `Default` with `payload: None`.
- `PingBodyBuilder` wraps a mutable `FlatBufferBuilder`, provides `add_payload`, `new`, and `finish`.
- `impl Debug for PingBody` prints the payload field.

## Control flow

Read-side control flow uses FlatBuffers traits: a caller follows a table location to `PingBody`, optionally verifies it, and reads `payload()` through the generated vtable lookup. Write-side control flow starts a table, optionally pushes the payload slot if `PingBodyArgs.payload` is present, and finishes the table to produce a `WIPOffset<PingBody>`. Verification visits the table, checks the optional payload vector field, and finishes successfully if the buffer shape is valid.

## State and persistence behavior

The file has no mutable global state. `PingBody` is a zero-copy view into a serialized byte buffer with lifetime `'a`; it does not own payload bytes. `PingBodyBuilder` mutates the caller-provided `FlatBufferBuilder` until `finish`. Persistence is the serialized FlatBuffer produced by callers, not any state stored in this module.

## Dependencies and integration points

This code depends heavily on the `flatbuffers` crate traits and types: `Table`, `Follow`, `FlatBufferBuilder`, `Allocator`, `WIPOffset`, `Vector`, `Verifier`, and `InvalidFlatbuffer`. It is exposed through `flatbuffers_generated::mod.rs` and re-exported by `generated/mod.rs`, making `PingBody` part of the public generated protocol surface. The source schema is likely `src/models.fbs`, and regeneration must preserve compatibility for any component exchanging PingBody FlatBuffers.

## Risks and edge cases

- Several constructors and traversal methods are unsafe because they assume a valid FlatBuffer table and location. Callers should verify untrusted buffers before access.
- `payload` is optional. Callers must handle `None`, which can represent an empty PingBody distinct from a present zero-length vector.
- The payload is an untyped byte vector, so higher-level interpretation and size limits must be enforced outside this generated layer.
- Manual edits will be overwritten by the FlatBuffers compiler.
- Because the parent module re-exports generated models with glob export, adding new generated names can affect downstream namespace collisions.

## Test signals

There are no local tests. Good signals are generated-code compilation, round-trip FlatBuffer construction and readback for `PingBody` with absent, empty, and non-empty payloads, and verifier rejection tests for malformed buffers.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/generated/flatbuffers_generated/models.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/generated/mod.rs -->
# sources/object-store/rustfs/crates/protos/src/generated/mod.rs

## Purpose

This generated top-level module wires together the prost/tonic generated gRPC modules and the FlatBuffers generated modules for the `rustfs-protos` crate. It centralizes generated-code lint suppression and re-exports FlatBuffers model types.

## Important APIs, types, and functions

- `#![allow(unused_imports)]` and `#![allow(clippy::all)]` suppress warnings commonly emitted by generated code.
- `pub mod proto_gen;` exposes generated protobuf/gRPC modules.
- `mod flatbuffers_generated;` keeps the FlatBuffers wrapper module private at this level.
- `pub use flatbuffers_generated::models::*;` re-exports generated FlatBuffers model items such as `PingBody`.

## Control flow

There is no runtime control flow. Rust module loading and public re-export resolution determine which generated types are available to users of the crate.

## State and persistence behavior

There is no state or persistence. The file establishes namespace and visibility for generated protocol definitions.

## Dependencies and integration points

This module integrates `proto_gen/mod.rs`, which currently exposes `node_service`, with the FlatBuffers `models` namespace. Consumers can import protobuf service modules through `generated::proto_gen::...` and FlatBuffers model types directly through `generated::*`. The lint allowances protect generated files from breaking workspace-wide clippy checks.

## Risks and edge cases

- Glob re-export of FlatBuffers models can create name collisions as schemas grow.
- Keeping `flatbuffers_generated` private while re-exporting its contents is convenient, but downstream users cannot address the original generated namespace path through this module.
- `allow(clippy::all)` is appropriate for generated code but can mask issues if hand-written code is later added to this module.
- Changes to this module are public API changes for consumers of `rustfs-protos`.

## Test signals

Compilation is the main signal. Public API tests or downstream compile tests should verify both `generated::proto_gen::node_service` access and direct import of re-exported FlatBuffers models.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/generated/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/generated/proto_gen/mod.rs -->
# sources/object-store/rustfs/crates/protos/src/generated/proto_gen/mod.rs

## Purpose

This generated protobuf namespace wrapper exposes the generated `node_service` module. It is the protobuf/gRPC counterpart to the FlatBuffers wrapper under `flatbuffers_generated`.

## Important APIs, types, and functions

- `pub mod node_service;` declares and publicly exposes generated code from `node_service.rs`.
- The file itself defines no functions, structs, constants, or state.

## Control flow

There is no runtime control flow. Rust module resolution includes `node_service.rs` when `proto_gen::node_service` is referenced.

## State and persistence behavior

There is no state or persistence in this wrapper. State and wire-format behavior live in the generated protobuf service/client/message code in `node_service.rs`.

## Dependencies and integration points

The module is exposed by `generated/mod.rs` as `pub mod proto_gen`, so consumers use paths such as `rustfs_protos::generated::proto_gen::node_service`. The underlying generated service code depends on `prost`, `tonic`, and `tonic-prost` according to the crate manifest.

## Risks and edge cases

- Adding or renaming protobuf files requires updating this generated wrapper or regenerating it.
- Since this is a namespace bridge, a missing `node_service.rs` or stale generated file breaks the entire protobuf public surface.
- Manual edits may be overwritten by the protobuf generation pipeline.

## Test signals

The key signal is `cargo check -p rustfs-protos`, plus any integration test that imports generated node service clients, servers, and messages through `generated::proto_gen::node_service`.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protos/src/generated/proto_gen/mod.rs -->
