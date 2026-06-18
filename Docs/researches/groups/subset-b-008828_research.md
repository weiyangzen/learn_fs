# subset-b-008828 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/benches/skipmap.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/benches/skipmap.rs

Purpose: This nightly `test` benchmark suite measures basic `SkipMap` costs for insertion, forward iteration, reverse iteration, lookup, and insert-then-remove workloads. It uses a deterministic wrapping LCG-like key sequence so each benchmark exercises a fixed set of 1,000 pseudo-random `u64` keys.

Important APIs and functions: The file aliases `crossbeam_skiplist::SkipMap` as `Map`, imports `test::{black_box, Bencher}`, and defines `insert`, `iter`, `rev_iter`, `lookup`, and `insert_remove` with `#[bench]`. `black_box` prevents optimizer removal of entries returned by iterators, lookups, and removals.

Control flow: The insert benchmarks build a fresh map inside each `b.iter` invocation. Iteration and lookup benchmarks prepopulate one map before timing and then repeatedly traverse or query it. `insert_remove` populates a fresh map and then removes the same generated keys, unwrapping each removal to assert that benchmark setup remains coherent.

State and persistence behavior: All state is in-memory and per-benchmark. There is no filesystem persistence. The key generator's wrapping arithmetic is the only deterministic workload state.

Dependencies and integration points: It is tied to Rust nightly benchmark support through `#![feature(test)]` and exercises the public `SkipMap` wrapper rather than the lower-level `base::SkipList`.

Risks: Results cover only single-threaded operations on 1,000 keys, so they are not a concurrency scalability signal. The suite also omits comparison with `BTreeMap` or other concurrent maps.

Test signals: It provides performance signals only; `insert_remove` additionally catches unexpected missing keys through `unwrap`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/benches/skipmap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/examples/simple.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/examples/simple.rs

Purpose: This example is currently a commented scratch program for manual `SkipMap` timing. It shows how to instantiate a map, insert one million deterministic keys, iterate it, and print elapsed durations.

Important APIs and functions: The only active item is `fn main() {}`. The commented code references `std::time::Instant`, `crossbeam_skiplist::SkipMap::new`, `insert`, and `iter`.

Control flow: If uncommented, the example would create a map, generate keys with the same wrapping arithmetic as the benchmark, time inserts, then time a full traversal. As checked in, execution is a no-op.

State and persistence behavior: There is no persistent state. The commented example uses in-memory map state and wall-clock timing.

Dependencies and integration points: It belongs to the `crossbeam-skiplist` example target and documents ad hoc manual profiling more than library behavior.

Risks: Because it is entirely commented, it does not validate compilation of the showcased code. It may drift from current APIs without test coverage.

Test signals: None at runtime; the file only confirms an empty example target compiles.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/examples/simple.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/rustfmt.toml -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/rustfmt.toml

Purpose: This configuration deliberately leaves rustfmt at defaults to preserve the upstream `crossbeam-skiplist` style and reduce cherry-pick conflicts.

Important APIs and settings: There are no active rustfmt keys. The comments explain that the empty file is intentional.

Control flow: Not applicable; rustfmt reads the file and applies default formatting.

State and persistence behavior: The file is persistent repository formatting policy. It does not affect runtime state.

Dependencies and integration points: It integrates with developer formatting tools and CI formatting checks for this vendored component.

Risks: Future contributors may assume the file is accidentally empty and add local style settings, increasing divergence from upstream.

Test signals: Formatting stability is the only signal; no code tests depend on it.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/rustfmt.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/src/base.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/src/base.rs

Purpose: This is the lock-free skip-list core used by the public map and set wrappers. It implements ordered concurrent insertion, removal, search, range iteration, bidirectional traversal, and owned/reference-counted entry handles on top of `crossbeam_epoch`.

Important APIs and types: Public surface includes `SkipList<K,V>`, guarded `Entry<'a,'g,K,V>`, reference-counted `RefEntry<'a,K,V>`, `Iter`, `RefIter`, `Range`, `RefRange`, `IntoIter`, and `OwnedIter`. Internal types include dynamically sized `Node`, `Tower`, `Head`, `Position`, `HotData`, and `OwnedEntry`. Key methods are `new`, `len`, `front`, `back`, `get`, `lower_bound`, `upper_bound`, `get_or_insert`, `get_or_insert_with`, `insert`, `compare_insert`, `remove`, `pop_front`, `pop_back`, `clear`, and traversal helpers.

Control flow: Searches start at the highest non-empty head level, move right while bounds allow, and drop levels until level 0. Encountered marked pointers trigger `help_unlink`, which tries to splice deleted nodes out and decrement level references. Insertion searches a position, optionally marks an existing equal key for replacement, allocates a node with a random height, CAS-installs level 0, then opportunistically builds higher tower levels. Removal marks the node tower, decrements approximate length, and unlinks each level or falls back to a search that helps unlink.

State and persistence behavior: All state is volatile memory. `HotData` tracks a relaxed pseudo-random seed, approximate length, and max tower height. Node lifetime is controlled by a packed height/reference counter and deferred epoch reclamation; `RefEntry` and iterator cursor references must be released with an epoch guard, while public wrappers hide that detail.

Dependencies and integration points: It depends on `alloc`, `core`, `crossbeam_epoch::{Atomic, Collector, Guard, Shared}`, and `crossbeam_utils::CachePadded`. `map.rs` wraps it with default collector pinning; tests exercise both direct guarded APIs and public wrappers.

Risks: The implementation is unsafe-heavy: dynamic allocation layout, pointer tagging, relaxed/SeqCst ordering choices, guard-collector matching, and manual reference release are all correctness-critical. `RefEntry` leaks if `release` is never called, and delayed global epoch collection explains the `'static` bounds on mutating APIs. Length is approximate during concurrent mutation and can clamp underflow to zero.

Test signals: `tests/base.rs` covers creation, replacement, removal, bounds, ranges, iteration under deletion, panic safety in `get_or_insert_with`, concurrent closure races, owned iteration, clear, and destructor counts after epoch flushing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/src/base.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/src/lib.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/src/lib.rs

Purpose: This crate root defines the public shape and documentation for TiKV's vendored `crossbeam-skiplist` component. It presents `SkipMap` and `SkipSet` as ordered concurrent alternatives to `BTreeMap` and `BTreeSet`, and documents lock-free operation, race semantics, immutable value access, epoch reclamation, and performance tradeoffs.

Important APIs and types: It conditionally exposes `base` and reexports `SkipList` when `alloc` and pointer atomics are available. With `std`, it exposes `map`, `set`, and reexports `SkipMap` and `SkipSet`. The crate uses `#![no_std]`, enables `alloc`/`std` conditionally, and warns on missing docs and unsafe operations in unsafe functions.

Control flow: There is no runtime control flow beyond conditional module compilation. The documentation examples demonstrate concurrent insertion/removal and ordered iteration.

State and persistence behavior: No state is stored in this file. It controls compile-time module availability.

Dependencies and integration points: It depends on `crossbeam-epoch` and `crossbeam-utils` through submodules. The private `seal` module references `crossbeam_skiplist_offical::SkipList<(), ()>` only to keep cargo machete from flagging the dependency as unused.

Risks: Feature gating is central: `base` is available in no-std alloc builds, while `SkipMap`/`SkipSet` require `std`. The documentation explicitly warns that individual operations are atomic but multi-call workflows can race logically.

Test signals: Doctests in this root document public examples, while dedicated tests under `tests/` validate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/src/map.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/src/map.rs

Purpose: `map.rs` exposes the ergonomic, `std`-based `SkipMap<K,V>` API on top of `base::SkipList<K,V>`. It gives users a concurrent ordered map without requiring them to manage epoch guards or `RefEntry` release manually.

Important APIs and types: Public types are `SkipMap`, `Entry`, `IntoIter`, `Iter`, and `Range`. Main methods include `new`, `is_empty`, `len`, `front`, `back`, `contains_key`, `get`, `lower_bound`, `upper_bound`, `get_or_insert`, `get_or_insert_with`, `iter`, `range`, `insert`, `compare_insert`, `remove`, `pop_front`, `pop_back`, and `clear`. `Entry` exposes `key`, `value`, `is_removed`, navigation, cloning, and `remove`.

Control flow: Each operation pins the default epoch collector, calls the corresponding `base::SkipList` method, and converts `RefEntry` into a public `Entry`. `try_pin_loop` retries when a found guarded node cannot be reference-counted because concurrent removal won the race. Iterators and ranges hold `base::RefIter`/`RefRange` state and release cursor references in `Drop`.

State and persistence behavior: The map stores all key/value pairs in its inner skip list. `Entry` uses `ManuallyDrop` so its `Drop` implementation can consume the `RefEntry` and call `release_with_pin`. There is no disk persistence.

Dependencies and integration points: It integrates public Rust collection traits (`Default`, `IntoIterator`, `FromIterator`, `Debug`) with the unsafe base implementation and `crossbeam_epoch::default_collector`.

Risks: Returned entries keep removed nodes alive until dropped. Values are only shared immutably; callers needing mutation must use interior mutability. `get_or_insert_with` may evaluate and discard its closure result if another thread inserts first.

Test signals: `tests/map.rs` covers duplicate insertion, compare-insert semantics, concurrent insert/remove regressions, iterator memory-leak regressions, ordered forward/backward iteration, range bounds, clear, into-iter ordering, panic safety, and concurrent same-key insert/get.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/src/map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/src/set.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/src/set.rs

Purpose: `set.rs` implements `SkipSet<T>` as a thin ordered set wrapper around `SkipMap<T, ()>`. It preserves the concurrent ordered behavior while exposing values as set entries rather than map keys.

Important APIs and types: Public types are `SkipSet`, set `Entry`, `IntoIter`, `Iter`, and `Range`. Methods mirror `SkipMap`: `new`, `is_empty`, `len`, `front`, `back`, `contains`, `get`, `lower_bound`, `upper_bound`, `get_or_insert`, `iter`, `range`, `insert`, `remove`, `pop_front`, `pop_back`, and `clear`. `Entry` dereferences to `T` and exposes `value`, navigation, `is_removed`, and `remove`.

Control flow: All operations delegate to `SkipMap<T, ()>`, converting map entries into set entries. `IntoIter` drops the unit value and yields only keys. Range and iterator behavior is inherited from the map layer.

State and persistence behavior: State is in-memory and stored in the underlying skip map. Entries hold map references, so removed values remain alive while entries exist.

Dependencies and integration points: It depends on `map.rs`, standard borrowing/range traits, `Deref`, and standard collection traits. It is reexported by `lib.rs` with the `std` feature.

Risks: Risks largely match `SkipMap`: approximate `len` under concurrency, immutable-only access, and logical races across multiple calls. Because the set is a map-to-unit adapter, correctness depends on key-only semantics being preserved by all map operations.

Test signals: `tests/set.rs` validates set insertion/removal, duplicate length behavior, entry navigation/reposition after removal and reinsertion, bounds, range combinations, iterator ordering, clear, into-iter output, and same-key concurrent insert/get.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/src/set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/tests/base.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/tests/base.rs

Purpose: This is the direct regression suite for the low-level guarded `base::SkipList` API. It validates behavior that public wrappers hide, especially guard usage, explicit `RefEntry` release, owned iteration, and destructor timing under epoch reclamation.

Important APIs and helpers: Tests use `SkipList`, `base::RefEntry`, `crossbeam_epoch::pin`, custom collectors, `Arc`, bounds, and a local `Entry` wrapper whose `Drop` calls `release_with_pin`. Test cases cover `new`, `is_empty`, `insert`, `remove`, `front`, `back`, entry navigation, `get`, `lower_bound`, `upper_bound`, `get_or_insert`, `get_or_insert_with`, `owned_iter`, `iter`, `range`, `into_iter`, `clear`, and drop behavior.

Control flow: Most tests build known integer maps, perform ordered mutations, and collect keys/values through entries or iterators. Panic and concurrency tests use `catch_unwind`, sleeping writer races, and spawned threads. The drop test uses a custom collector and explicit `flush` calls to observe deferred destruction.

State and persistence behavior: All state is in-memory. The suite tracks list length, removed-entry flags, explicit release behavior, and atomic counters for dropped keys and values.

Dependencies and integration points: It is the closest consumer of `base.rs`, so it catches lower-level API regressions before `SkipMap`/`SkipSet` wrappers are involved.

Risks: Some concurrency timing uses sleeps and therefore tests only selected interleavings. The direct API requires careful release discipline, and the local wrapper is part of the test safety model.

Test signals: Strong signals include sorted traversal after deletion, exact range outputs for inclusive/exclusive bounds, unchanged state after closure panic, closure execution despite discarded result, owned iterator validity across a spawned thread, clear-to-zero, and destructor counts after epoch flush.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/tests/base.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/tests/map.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/tests/map.rs

Purpose: This suite validates the public `SkipMap` API and its guard-hiding entry/iterator wrappers. It mirrors much of the base behavior while adding tests for `compare_insert` and wrapper-specific memory release regressions.

Important APIs and tests: It uses `SkipMap`, `Arc`, `Barrier`, `crossbeam_utils::thread`, `Bound`, and collection construction from iterators. Notable tests include `compare_and_insert`, `compare_insert_with_absent_key`, `concurrent_insert`, `concurrent_compare_and_insert`, `concurrent_remove`, `next_memory_leak`, `next_back_memory_leak`, `range_next_memory_leak`, `ordered_iter`, `ordered_range`, `iter_range2`, and `concurrent_insert_get_same_key`.

Control flow: Tests perform deterministic insert/remove sequences and collect ordered keys. Concurrency regressions run repeated two-thread same-key races or many compare-insert writers. Iterator tests interleave mutation with traversal and mix `next`/`next_back` calls to verify cursors terminate and release references correctly.

State and persistence behavior: All state is in-memory. Tests inspect public length, emptiness, entry removal flags, values after replacement, and iterator output.

Dependencies and integration points: The suite is a contract for users of `SkipMap` and indirectly exercises `base::SkipList`, `Entry::Drop`, `Iter::Drop`, and `Range::Drop`.

Risks: It cannot prove all lock-free interleavings, but it captures prior Crossbeam issues around duplicate same-key insertion/removal, range counting, and same-key insert/get visibility.

Test signals: Exact expected values and sorted sequences are the main signals; concurrency tests signal panic-free execution, max-value compare-insert convergence, and persistent `get` success while another thread repeatedly inserts the same key.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/tests/map.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/tests/set.rs -->
# sources/storage-engines/tikv/components/crossbeam-skiplist/tests/set.rs

Purpose: This suite validates the public `SkipSet` API as a set-oriented adapter over `SkipMap<T, ()>`. It ensures key-only behavior, ordering, range semantics, entry navigation, and same-key concurrency remain correct.

Important APIs and tests: It uses `SkipSet`, `crossbeam_utils::thread`, `Barrier`, `Bound`, and iterator collection. Test names cover smoke construction, emptiness, insertion, removal, concurrent insert/remove, entry navigation/removal/reposition, length, get, lower/upper bounds, `get_or_insert`, front/back, iterators, ranges, `iter_range2`, `into_iter`, `clear`, and `concurrent_insert_get_same_key`.

Control flow: Tests create fixed integer sets, mutate them, and collect ordered values through `Entry` deref. Range tests exhaust combinations of included/excluded/unbounded bounds. Concurrency tests use repeated two-thread races and a longer same-key insert/get loop.

State and persistence behavior: All state is in-memory. Since entries wrap map entries, removed elements are observable through `is_removed` and remain valid while referenced.

Dependencies and integration points: It tests the set wrapper and indirectly the map/base layers. It is especially useful for checking that map key/value behavior did not leak into the set API.

Risks: The same-key insert/get test uses a fixed loop count and does not explore arbitrary schedules. Like the map suite, it validates behavior but not full lock-free progress guarantees.

Test signals: Sorted value outputs, duplicate insertion preserving length, removed-entry flags, empty/non-empty transitions, exact range vectors, and panic-free concurrent same-key operations provide the primary signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crossbeam-skiplist/tests/set.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/Cargo.toml -->
# sources/storage-engines/tikv/components/crypto/Cargo.toml

Purpose: This manifest defines TiKV's small `crypto` shim crate, used for cryptographic utilities with FIPS-aware OpenSSL setup.

Important APIs and settings: Package metadata sets name `crypto`, version `0.0.1`, edition 2021, Apache-2.0 license, and `publish = false`. Dependencies are `openssl`, `openssl-sys`, `slog`, and `slog-global` from the workspace. The lint configuration whitelists custom cfgs `ossl1`, `ossl3`, and `disable_fips`.

Control flow: Cargo uses this file to compile `build.rs`, expose OpenSSL version information, and allow code guarded by the custom cfgs.

State and persistence behavior: It is build metadata only. No runtime state is defined here.

Dependencies and integration points: `openssl-sys` is intentionally kept as a direct dependency so the build script can read `DEP_OPENSSL_VERSION_NUMBER`. The encryption component depends on this crate for random-number generation.

Risks: Removing `openssl-sys` or the custom-cfg lint allowance breaks FIPS build detection or produces unexpected-cfg warnings.

Test signals: Build success under FIPS and non-FIPS configurations is the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/build.rs -->
# sources/storage-engines/tikv/components/crypto/build.rs

Purpose: The build script configures whether the `crypto` crate compiles with FIPS support and which OpenSSL major-family cfg to enable.

Important APIs and functions: `main` checks the compile-time `ENABLE_FIPS` environment variable. If it is not exactly `1`, it emits `cargo:rustc-cfg=disable_fips`. Otherwise it reads `DEP_OPENSSL_VERSION_NUMBER`, parses it as hex, and emits either `ossl3` for OpenSSL 3.x-or-newer or `ossl1` for older OpenSSL.

Control flow: Non-FIPS builds return early. FIPS builds require the OpenSSL version environment variable from `openssl-sys`; absence causes a panic with a dependency hint.

State and persistence behavior: State is compile-time cfg output consumed by `fips.rs`. No runtime state is stored.

Dependencies and integration points: It depends on Cargo build-script environment propagation from `openssl-sys`.

Risks: `ENABLE_FIPS` is checked with `option_env!`, so it reflects compile-time environment. A malformed version string panics. The threshold treats all pre-3 OpenSSL as `ossl1`, even though API support can vary.

Test signals: Successful cfg emission and build behavior under `ENABLE_FIPS=1` are the useful signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/build.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/src/fips.rs -->
# sources/storage-engines/tikv/components/crypto/src/fips.rs

Purpose: This module centralizes OpenSSL FIPS-mode activation and status logging for TiKV cryptographic code.

Important APIs and state: Public functions are `maybe_enable`, `can_enable`, and `log_status`. `FIPS_VERSION: AtomicUsize` records 0 for disabled, 1 for OpenSSL 1.x FIPS, and 3 for OpenSSL 3 provider mode. `_OPENSSL_VERSION` references `openssl_sys::SSL_version` to keep the dependency visible.

Control flow: `maybe_enable` returns immediately if `can_enable` is false. Under `ossl1`, it calls `openssl::fips::enable(true).unwrap()` and stores 1. Under `ossl3`, it loads the `fips` provider, intentionally leaks it with `mem::forget`, and stores 3. If no expected cfg is active, it logs a warning.

State and persistence behavior: Runtime state is only the atomic status flag and the loaded OpenSSL provider. There is no disk persistence.

Dependencies and integration points: It relies on cfgs emitted by `build.rs`, `openssl`, `openssl-sys`, and `slog-global`. It should be called very early in process startup.

Risks: Provider loading and FIPS enable use `unwrap`, so misconfigured FIPS environments can panic. Calling it late may leave earlier crypto operations outside FIPS mode.

Test signals: Status logs and successful startup under each cfg are the primary signals; no local unit tests are present.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/src/fips.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/src/lib.rs -->
# sources/storage-engines/tikv/components/crypto/src/lib.rs

Purpose: This crate root describes `crypto` as a FIPS-conscious shim for cryptographic operations and exports the concrete modules currently implemented.

Important APIs and modules: It publicly exposes `fips` and `rand`. The documentation calls out random-number generation and leaves message-digest support as a TODO.

Control flow: There is no runtime control flow in this file.

State and persistence behavior: No state is defined here.

Dependencies and integration points: Downstream crates import `crypto::fips` for process setup and `crypto::rand` for OpenSSL-backed randomness, avoiding direct use of non-FIPS RNGs in encryption paths.

Risks: The crate is intentionally small; adding cryptographic helpers here should preserve FIPS semantics and avoid accidental use of non-approved providers.

Test signals: Module-level tests, if any, live in submodules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/src/rand.rs -->
# sources/storage-engines/tikv/components/crypto/src/rand.rs

Purpose: This module exposes cryptographically strong random bytes and `u64` generation through OpenSSL, keeping encryption-related randomness inside the FIPS-aware crypto shim.

Important APIs and functions: `rand_bytes(buf: &mut [u8]) -> Result<(), ErrorStack>` delegates to `openssl::rand::rand_bytes`. `rand_u64() -> Result<u64, ErrorStack>` fills an 8-byte buffer and returns `u64::from_ne_bytes`.

Control flow: `rand_u64` is a simple wrapper: allocate array, fill using `rand_bytes`, convert to native-endian integer, propagate OpenSSL errors.

State and persistence behavior: No persistent state. Randomness comes from OpenSSL's RNG state.

Dependencies and integration points: `encryption/src/encrypted_file/mod.rs` uses `rand_u64` to create temporary file extensions. Other cryptographic code should prefer this module over the general `rand` crate.

Risks: `from_ne_bytes` is fine for random IDs but produces architecture-endian textual values if later serialized directly. Callers must handle OpenSSL `ErrorStack`.

Test signals: No direct tests in this file; consumers validate random IV/temp-name behavior indirectly.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/crypto/src/rand.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/Cargo.toml -->
# sources/storage-engines/tikv/components/encryption/Cargo.toml

Purpose: This manifest defines the core TiKV encryption crate containing data-key management, master-key backends, file encryption, cloud KMS integration types, metrics, and backup helpers.

Important APIs and settings: Package metadata sets edition 2024 and `publish = false`. Features include `failpoints`, `sm4` via vendored OpenSSL, and `testexport`. Dependencies include `cloud`, `crypto`, `file_system`, `kvproto`, `openssl`, `protobuf`, `prometheus`, `serde`, `tokio`, and TiKV utility crates. A comment explicitly discourages using the general `rand` crate for encryption-related code despite the dependency being present.

Control flow: Cargo uses features to include failpoints and conditional SM4 support. The dependency graph wires the crate to protobuf encryption metadata, cloud KMS providers, OpenSSL ciphers, filesystem abstractions, and metrics.

State and persistence behavior: This file is build metadata only; persistence behavior is implemented in submodules.

Dependencies and integration points: It is consumed by `encryption_export` and TiKV server components that need at-rest encryption and backup encryption support.

Risks: Feature and dependency changes can affect cryptographic compliance, especially SM4/OpenSSL vendoring and RNG selection.

Test signals: Build and crate tests under relevant feature combinations are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/export/Cargo.toml -->
# sources/storage-engines/tikv/components/encryption/export/Cargo.toml

Purpose: This manifest defines `encryption_export`, a crate that reexports selected encryption APIs and wires concrete cloud provider backends for applications and examples outside the core encryption crate.

Important APIs and settings: It uses edition 2021, Apache-2.0, and has an `sm4` feature forwarding to `encryption/sm4`. Dependencies include provider crates `aws`, `azure`, `gcp`, `gcp_v2`, `cloud`, core `encryption`, `file_system`, `kvproto`, `protobuf`, logging, and `tikv_util`. Dev dependencies support the example CLI with `rust-ini` and `structopt`.

Control flow: Cargo resolves provider implementations here, keeping core backend factory code separate from provider-specific crates.

State and persistence behavior: Build metadata only.

Dependencies and integration points: `export/src/lib.rs` uses these dependencies to construct `KmsBackend` instances for AWS, Azure, GCP v1, and GCP v2.

Risks: Provider crate API changes or feature mismatch can break the public factory layer. The forwarded `sm4` feature must stay aligned with core encryption.

Test signals: Provider factory tests and example compilation are the relevant signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/export/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/export/examples/ecli.rs -->
# sources/storage-engines/tikv/components/encryption/export/examples/ecli.rs

Purpose: `ecli` is an example command-line program demonstrating encryption and decryption of files through KMS-backed `encryption_export` backends.

Important APIs and types: It defines `Operation::{Encrypt,Decrypt}`, `Opt`, `Command::{Aws,Azure,Gcp}`, and provider-specific subcommand structs with `structopt`. Helper functions `create_aws_backend`, `create_azure_backend`, `create_gcp_backend`, `process`, and `main` build backends and transform file content.

Control flow: `process` parses CLI args, reads the input file, builds the selected backend, encrypts plaintext into serialized `EncryptedContent` or decrypts serialized `EncryptedContent` into plaintext, then writes the output file. `main` prints `done` or an error string.

State and persistence behavior: It reads one input path and writes one output path. Credential files are optionally parsed as INI mainly for presence/shape validation. Encryption metadata is persisted as protobuf bytes.

Dependencies and integration points: It uses provider constants, `KmsConfig`, `KmsBackend`, `create_cloud_backend`, `file_system` abstractions, `kvproto::EncryptedContent`, `protobuf::Message`, and `structopt`.

Risks: The Azure helper populates a local `azure_cfg` but never assigns it into `config.azure`, so Azure backend creation appears likely to fail the sanity check in `create_cloud_backend`. The AWS credential parser does not apply credentials to config. Output files are opened with create/write but not truncate, which can leave trailing bytes when overwriting longer files.

Test signals: No unit tests; compilation and manual CLI runs are the signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/export/examples/ecli.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/export/src/lib.rs -->
# sources/storage-engines/tikv/components/encryption/export/src/lib.rs

Purpose: This crate-level library reexports core encryption APIs and provides factory functions that turn TiKV encryption configuration into concrete local, plaintext, or cloud KMS master-key backends.

Important APIs and functions: Public functions are `data_key_manager_from_config`, `create_async_backend`, `create_backend`, and `create_cloud_backend`. Internal helpers `create_backend_inner` and `create_async_backend_inner` dispatch on `MasterKeyConfig`. The crate reexports `AsyncBackend`, `Backend`, `DataKeyManager`, `DataKeyManagerArgs`, config types, cleanup helpers, `Iv`, `KmsBackend`, and error/result types.

Control flow: Backend creation logs failures and propagates errors. `create_cloud_backend` converts `KmsConfig` into `cloud::Config`, logs region/endpoint/key/vendor, then dispatches AWS/default, Azure, GCP, or GCP v2 providers with provider-specific sanity checks. `data_key_manager_from_config` builds current and lazy previous master-key backends for `DataKeyManager::new`.

State and persistence behavior: The library itself stores no state, but returned backends may read key files or call external KMS services. `DataKeyManager` persists/uses the file dictionary at the supplied dictionary path.

Dependencies and integration points: It connects core encryption to `aws`, `azure`, `gcp`, `gcp_v2`, `cloud`, and TiKV logging/error utilities.

Risks: Empty vendor defaults to AWS. Azure/GCP require provider-specific nested config; missing config returns explicit errors. Factory functions log key IDs and endpoints, which is operationally useful but should avoid secrets.

Test signals: The local test checks Azure missing-config failure and successful secure backend creation with a populated Azure config.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/export/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/backup/backup_encryption.rs -->
# sources/storage-engines/tikv/components/encryption/src/backup/backup_encryption.rs

Purpose: `BackupEncryptionManager` groups encryption dependencies and helper operations used by backup/log-backup flows.

Important APIs and types: The struct stores an optional user-supplied plaintext `CipherInfo`, a `master_key_based_file_encryption_method`, a `MultiMasterKeyBackend`, and an optional TiKV `DataKeyManager`. Public methods are `new`, inherent `default`, `opt_data_key_manager`, async `encrypt_data_key`, async `decrypt_data_key`, async `is_master_key_backend_initialized`, and `generate_data_key`.

Control flow: Data-key encryption/decryption delegates to the multi-master-key backend. Initialization readiness requires a non-`Unknown`, non-`Plaintext` method and an initialized backend. Data-key generation delegates to the backend using the configured encryption method.

State and persistence behavior: The manager is cloneable and holds backend/key-manager handles, but does not itself persist data. The optional plaintext data key is specifically documented as intended for stream backup uploads and not recommended in production.

Dependencies and integration points: It integrates backup protobuf `CipherInfo`, encryption protobuf `EncryptedContent`/`EncryptionMethod`, `DataKeyManager`, and `MultiMasterKeyBackend`.

Risks: The inherent `default` is not a `Default` trait implementation, which may surprise generic callers. Readiness depends on async backend state and encryption method consistency. Plaintext data-key support is operationally sensitive.

Test signals: No direct tests in this file; coverage likely comes from backup workflows that exercise key encryption and readiness checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/backup/backup_encryption.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/backup/mod.rs -->
# sources/storage-engines/tikv/components/encryption/src/backup/mod.rs

Purpose: This module file exposes backup encryption support from the encryption crate.

Important APIs and modules: It contains `pub mod backup_encryption;`.

Control flow: No runtime control flow.

State and persistence behavior: No state is defined here.

Dependencies and integration points: It is the namespace entry point for `BackupEncryptionManager`.

Risks: Minimal; adding backup encryption modules requires explicit export here.

Test signals: Compilation verifies the module path.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/backup/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/config.rs -->
# sources/storage-engines/tikv/components/encryption/src/config.rs

Purpose: This module defines user-facing and protobuf-facing encryption configuration types, including data encryption method selection, data-key rotation, file/KMS master-key configuration, and vendor-specific KMS subconfig conversion.

Important APIs and types: Key types are `EncryptionConfig`, `FileConfig`, `AzureConfig`, `GcpConfig`, `AwsConfig`, `KmsConfig`, and `MasterKeyConfig`. Important methods are `KmsConfig::from_proto`, `KmsConfig::to_cloud_config`, `MasterKeyConfig::from_proto`, and custom serde helpers for `EncryptionMethod`.

Control flow: Defaults choose plaintext data encryption, seven-day rotation, enabled file dictionary log, threshold one million, and plaintext current/previous master keys. KMS config conversion copies common key/location/vendor fields and optional Azure/GCP/AWS nested fields, translating empty proto strings to `None`. `to_cloud_config` validates non-empty key IDs through `cloud::kms::KeyId::new`.

State and persistence behavior: These structs are serialized/deserialized from TOML and protobuf, and `OnlineConfig` marks most encryption settings as skipped for online changes. Secret-bearing Azure fields are intentionally omitted from `Debug`.

Dependencies and integration points: It depends on `cloud::kms` subconfigs, `kvproto::encryptionpb`, serde, `online_config`, `ReadableDuration`, and crate `Error`.

Risks: Configuration shape is security-sensitive. Empty strings become `None` only in proto conversion, while TOML parsing follows serde defaults. Most fields are not online-configurable. `MasterKeyConfig::from_proto` returns `None` if the oneof is absent, leaving callers to decide defaults.

Test signals: Unit tests cover TOML parsing for AWS/Azure/GCP KMS, proto-to-config conversion with vendor-specific fields, cloud-config conversion, and empty key-id rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/crypter.rs -->
# sources/storage-engines/tikv/components/encryption/src/crypter.rs

Purpose: This module contains encryption primitive helpers: key length mapping, file encryption metadata, IV handling for CTR/GCM modes, AES-GCM tag handling, an AES-256-GCM crypter, and config validation.

Important APIs and types: Functions include `get_method_key_length` and `verify_encryption_config`. Types include `FileEncryptionInfo`, `Iv::{Gcm,Ctr,Empty}`, `AesGcmTag`, and `AesGcmCrypter<'k>`. `AesGcmCrypter::KEY_LEN` is 32 bytes and it exposes `new`, `encrypt`, and `decrypt`.

Control flow: IV constructors use OpenSSL random bytes. `Iv::from_slice` interprets 16 bytes as CTR and 12 bytes as GCM. CTR `add_offset` treats the IV as a big-endian `u128` and wraps addition; GCM and empty IVs reject offset changes. AES-GCM uses OpenSSL AEAD functions with empty AAD, returning ciphertext plus a 16-byte tag.

State and persistence behavior: `FileEncryptionInfo` carries method/key/iv metadata and hides key material in `Debug`. No persistent state is stored here; callers persist encrypted metadata elsewhere.

Dependencies and integration points: It uses `kvproto::EncryptionMethod`, `cloud::kms::PlainKey`, OpenSSL random and symmetric APIs, byteorder, and crate errors.

Risks: `get_method_key_length` panics on unknown methods. `AesGcmTag::from` asserts the source is at least 16 bytes but then attempts to copy the whole source into 16 bytes, so longer slices would panic. GCM uses no AAD, so all authenticated context must be inside ciphertext or external protocol checks.

Test signals: Tests check random IV uniqueness/roundtrip, NIST AES-256-GCM vector encryption/decryption, tag equality, and decryption failure with a wrong tag.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/crypter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/encrypted_file/header.rs -->
# sources/storage-engines/tikv/components/encryption/src/encrypted_file/header.rs

Purpose: This module defines the binary header format for encrypted files and validates header/content integrity through version, length, and CRC32 checks.

Important APIs and types: `Version::{V1,V2}` distinguishes files containing only encrypted content from files with unencrypted trailing log records. `Header` stores `version`, `crc32`, and `size`. Public methods are `Header::new`, `Header::parse`, `Header::to_bytes`, and `Header::version`.

Control flow: `Header::new` computes CRC32 over serialized encrypted content and records its length. `parse` requires a 16-byte header, decodes version, CRC32, and big-endian size, then enforces exact remaining size for V1 or at-least size for V2. It slices content and remaining bytes, recomputes CRC32, and returns an error on mismatch.

State and persistence behavior: The header is persisted at the beginning of encrypted files as 1 version byte, 3 reserved bytes, 4 CRC bytes, and 8 content-size bytes. V2 permits additional trailing data after the encrypted content.

Dependencies and integration points: It is used by `encrypted_file/mod.rs` before protobuf parsing/decryption. It depends on `byteorder`, `crc32fast`, `Write`, and TiKV boxed errors.

Risks: CRC32 is corruption detection, not authentication; cryptographic integrity must come from the encrypted content/backend. Large encoded sizes are cast to `usize` after length checks and should be reviewed for 32-bit targets.

Test signals: Tests cover empty header roundtrip, successful parse with content, missing content error, and CRC mismatch error.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/encrypted_file/header.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/encrypted_file/mod.rs -->
# sources/storage-engines/tikv/components/encryption/src/encrypted_file/mod.rs

Purpose: This module provides `EncryptedFile`, a helper for atomically reading and writing files whose payload is encrypted by a master-key backend and wrapped with the header format from `header.rs`.

Important APIs and types: It reexports `header::*`, defines `TMP_FILE_SUFFIX`, and exposes `EncryptedFile::new`, `read`, and `write`. The struct stores a base path and file name rather than an open handle.

Control flow: `read` opens the target file, reads all bytes, parses the header, deserializes `EncryptedContent` protobuf from the protected content slice, decrypts through `Backend`, records a histogram, and returns plaintext. `write` creates a random-suffixed temp file, encrypts plaintext, serializes protobuf bytes, writes a V1 header and content, syncs the temp file, atomically renames it over the original, syncs the base directory, and records metrics.

State and persistence behavior: Persistent state is the encrypted file on disk. Writes use temp-file-plus-rename for atomic replacement and directory fsync for durability. Broken temp files are acknowledged by a TODO and not garbage-collected here.

Dependencies and integration points: It uses `crypto::rand::rand_u64`, TiKV `file_system` wrappers, `kvproto::EncryptedContent`, protobuf serialization, `master_key::Backend`, metrics, logging, and `tikv_util::time::Instant`.

Risks: The temp file is opened with create/write but without `create_new`, so an extremely unlikely random-name collision could overwrite an existing temp file. Stale temp cleanup is missing. Reads load the whole file into memory.

Test signals: Unit tests verify missing-file error propagation and plaintext backend write/read roundtrip in a temporary directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/encrypted_file/mod.rs -->
