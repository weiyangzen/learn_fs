# subset-b-008313 research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/src/version_info.rs -->
# sources/security-integrity/cryfs/crates/cryfs-version/src/version_info.rs

## Purpose
Defines `VersionInfo`, the crate's combined semantic-version and git-metadata value. It is the display/serialization boundary used by `cryfs-version` macros to report package versions and to enforce Cargo.toml-versus-git-tag consistency.

## Important APIs, types, and functions
- `VersionInfo<'b, 'c, P>` stores a `Version<P>` plus optional `git2version::GitInfo`.
- `VersionInfo::new` is a `const fn` for `&str` prereleases that parses `gitinfo.tag_info.tag` and panics if it differs from the Cargo version.
- `assert_cargo_version_equals_git_version` returns `self` after constructor validation, supporting macro-generated const chains.
- `version`, `gitinfo`, `Display`, and `Debug` expose read-only state and render release/git suffixes.

## Control flow
Construction optionally inspects git tag metadata, parses the tag into `Version`, compares with `eq_const`, and panics on mismatch. Formatting always writes the semantic version first, then appends `+<commits>.g<commit>` for builds after a tag, `.modified` for dirty after-tag builds, or `+modified` for dirty on-tag builds.

## State and persistence behavior
The struct is immutable after construction and derives `Serialize`/`Deserialize`, so its persisted shape includes both nested `version` and nullable `gitinfo`. It does not fetch git state itself; it trusts `git2version` output passed by generated build-time code.

## Dependencies and integration points
Integrates with `Version`, `git2version::GitInfo`, `konst` const parsing/unwrap, Serde lifetime bounds, and the public version macros in the surrounding crate. Display output is likely user-facing CLI/log text.

## Risks and edge cases
Const panic message is intentionally generic until const formatting is stable. A git tag that is present but not parseable as this crate's `Version` format panics through `konst::result::unwrap!`. Display hides commit id when exactly on a clean tag, so diagnostics rely on `gitinfo()` for full metadata.

## Test signals
Unit tests cover Display/Debug combinations for prerelease, commits-since-tag, dirty tree, on-tag builds, accessors, and Serde round trips into owned `String` prerelease storage.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/src/version_info.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/tests/cryfs-version.rs -->
# sources/security-integrity/cryfs/crates/cryfs-version/tests/cryfs-version.rs

## Purpose
Integration tests for the `cryfs-version` procedural/macros surface by creating temporary downstream Cargo projects that depend on the local crate.

## Important APIs, types, and functions
- Computes `OUR_CRATE_PATH` and `OUR_GITVERSION` from `cryfs_version::GITINFO`.
- Uses `TempProjectBuilder` to generate temporary Cargo.toml/main.rs pairs.
- Exercises `package_version!`, `cargo_version!`, and `assert_cargo_version_equals_git_version!`.
- Helpers run projects and assert either successful JSON version output or expected build stderr.

## Control flow
Each module builds a small crate with a chosen version, then runs `cargo run` through `tempproject`. Tests that require git tag metadata are skipped when `OUR_GITVERSION` is absent. Success paths parse stdout as JSON `Version`; mismatch paths assert build failure contains the constructor panic text.

## State and persistence behavior
State is isolated to temporary Cargo projects and their build outputs. The tests persist no repository state but depend on the current checkout's git metadata when available.

## Dependencies and integration points
Depends on Cargo, `tempproject`, Serde JSON, the local `cryfs-version` path dependency, and macro expansion/build-script behavior. It validates downstream-user integration rather than only in-crate units.

## Risks and edge cases
The mismatch tests are conditional, so non-git source archives do not exercise tag enforcement. Assertions depend on exact panic text in compiler/build stderr. Temporary projects pin edition 2024 and declare their own workspace to avoid inheriting the parent workspace.

## Test signals
Signals are successful downstream builds, parsed version equality, and failed builds containing the version-mismatch diagnostic.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-version/tests/cryfs-version.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/Cargo.toml -->
# sources/security-integrity/cryfs/crates/crypto/Cargo.toml

## Purpose
Cargo manifest for the `cryfs-crypto` crate, declaring cryptographic primitives, backends, benchmark targets, and the optional `testutils` feature.

## Important APIs, types, and functions
- Package metadata is inherited from workspace settings.
- Runtime dependencies include OpenSSL vendored builds, sodiumoxide, RustCrypto AEAD/hash/KDF crates, `region`, `lockable`, `binrw`, and CryFS utility/version crates.
- Dev dependencies include `generic-tests`, `rstest`, and `criterion`.
- Bench targets are `hash`, `symmetric`, and `kdf` with Criterion harnesses.

## Control flow
Cargo selects the default empty feature set and always compiles all backend dependencies unless higher-level workspace features prune them elsewhere. Benchmarks are explicitly registered with `harness = false`.

## State and persistence behavior
The manifest controls dependency resolution and native OpenSSL vendoring. It stores no runtime state but affects reproducibility, binary size, and backend availability.

## Dependencies and integration points
This crate integrates with `cryfs-utils` for `Data`, `cryfs-version` for tag/version checks, OpenSSL/libsodium for native crypto, RustCrypto crates for portable backends, and Criterion for performance measurements.

## Risks and edge cases
OpenSSL is vendored, which improves build portability but increases build time and native build surface. All backend crates are hard dependencies; TODO comments in source indicate future feature-gating may be needed for production backend selection.

## Test signals
The manifest enables unit/generic tests and the three Criterion benches; no manifest-local tests exist.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/benches/hash.rs -->
# sources/security-integrity/cryfs/crates/crypto/benches/hash.rs

## Purpose
Criterion benchmark comparing SHA-512 hashing throughput across the default, pure Rust, OpenSSL, and libsodium backends over several input sizes.

## Important APIs, types, and functions
- `data(size, seed)` produces deterministic random `Data`.
- `bench_hash` benchmarks `Sha512`, `Sha2Sha512`, `OpensslSha512`, and `LibsodiumSha512`.
- Uses `Salt::generate_random`, `HashAlgorithm::hash`, `BenchmarkId`, and `black_box`.

## Control flow
For each size from one byte to one MiB, the benchmark creates a salt and deterministic data per backend registration, then repeatedly hashes in Criterion iterations.

## State and persistence behavior
No persistent state. Inputs are deterministic except salts are generated once per benchmark case, outside the measured loop.

## Dependencies and integration points
Integrates the public `cryfs_crypto::hash` API with Criterion and `cryfs_utils::Data`, providing comparative backend performance signals.

## Risks and edge cases
Salt generation is excluded from timing, which is appropriate for hashing backend throughput but not full operation cost. The one-MiB maximum avoids very long benches; larger commented sizes are not measured by default.

## Test signals
Criterion reports per-backend latency/throughput by input size; it is a performance signal, not a correctness test.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/benches/hash.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/benches/kdf.rs -->
# sources/security-integrity/cryfs/crates/crypto/benches/kdf.rs

## Purpose
Criterion benchmark for scrypt key derivation across the pure Rust `scrypt` backend and OpenSSL backend over a matrix of cost parameters.

## Important APIs, types, and functions
- Builds `ScryptSettings` for `log_n`, `r`, `p`, and `salt_len`.
- Uses `ScryptScrypt::generate_parameters` and both `ScryptScrypt::derive_key` and `ScryptOpenssl::derive_key`.
- Benchmarks 64-byte key derivation from the fixed password `"password"`.

## Control flow
Nested loops enumerate cost parameters, skip one invalid scrypt combination, generate parameters, and run derivation in Criterion iterations for each backend.

## State and persistence behavior
No persistent state. Random salt is generated once per bench case through `generate_parameters`; derivation work is the measured body.

## Dependencies and integration points
Exercises the `PasswordBasedKDF` trait and both scrypt backend modules. Benchmark IDs include debug-formatted settings for result grouping.

## Risks and edge cases
High-cost combinations can consume significant memory/time. The OpenSSL case uses parameters generated by the Rust backend, intentionally testing shared parameter compatibility but not backend-specific parameter generation.

## Test signals
Criterion timings reveal backend and parameter-scaling behavior; correctness is covered by unit tests elsewhere.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/benches/kdf.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/benches/symmetric.rs -->
# sources/security-integrity/cryfs/crates/crypto/benches/symmetric.rs

## Purpose
Criterion benchmark for symmetric encryption and decryption across AES-GCM and XChaCha20-Poly1305 backends.

## Important APIs, types, and functions
- `make_key`, `make_plaintext`, and `make_ciphertext` produce deterministic keys/data with required `Data` prefix/suffix capacity.
- Benchmarks default, OpenSSL, RustCrypto AEAD, and libsodium variants for AES-128-GCM, AES-256-GCM, and XChaCha20-Poly1305.
- Uses `LibsodiumAes256GcmNonce12::is_available` to skip unsupported hardware.

## Control flow
For each payload size, encryption cases construct a cipher and plaintext then measure `encrypt(plaintext.clone())`. Decryption cases pre-encrypt once then measure `decrypt(ciphertext.clone())`.

## State and persistence behavior
No persistent state. Randomness is deterministic for input/key generation, while encryption nonces are generated inside the measured operation.

## Dependencies and integration points
Stresses the public `Cipher`/`CipherDef` APIs, `EncryptionKey`, `Data` region growth, and backend interoperability choices exposed by type aliases.

## Risks and edge cases
Benchmarks include clone costs for `Data` and may include nonce generation overhead. Libsodium AES-GCM only runs when available, so result sets differ by CPU. The helper requires correctly preallocated `Data`; otherwise encryption implementations can panic on failed no-reallocation growth.

## Test signals
Criterion timings for encryption/decryption by size and backend; not a correctness oracle.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/benches/symmetric.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/backends/libsodium.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/backends/libsodium.rs

## Purpose
Implements the SHA-512 hash backend using libsodium through `sodiumoxide`.

## Important APIs, types, and functions
- `LibsodiumSha512` implements `HashAlgorithmDef` with 64-byte digest and 8-byte salt.
- Implements `HashAlgorithm<64, 8>::hash`.

## Control flow
Creates a libsodium SHA-512 state, updates it with salt bytes first, then data bytes, finalizes to a digest, and returns `Hash { digest, salt }`.

## State and persistence behavior
No persistent state. It consumes the provided salt by value and returns it unchanged for storage/verification.

## Dependencies and integration points
Uses `sodiumoxide::crypto::hash::sha512::State` and shared `Digest`, `Hash`, `Salt`, and traits from the hash module. Generic tests compare it with other backends.

## Risks and edge cases
Unlike the symmetric libsodium backend, this file does not call `sodiumoxide::init`; it relies on sodiumoxide hashing being usable without explicit local init or on earlier global initialization.

## Test signals
Generic hash tests verify determinism, salt/data sensitivity, exact compatibility vectors, and empty/long data behavior for this backend.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/backends/libsodium.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/backends/mod.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/backends/mod.rs

## Purpose
Backend aggregator for hash algorithms, exposing OpenSSL, RustCrypto `sha2`, and libsodium SHA-512 implementations.

## Important APIs, types, and functions
- Declares `openssl`, `sha2`, and `libsodium` submodules.
- Re-exports `OpensslSha512`, `Sha2Sha512`, and `LibsodiumSha512`.

## Control flow
This module has no runtime control flow; it is a compile-time namespace and public re-export layer.

## State and persistence behavior
No state.

## Dependencies and integration points
Feeds the parent `hash` module's public API and default type alias. Benchmarks and tests import concrete backend types through this module.

## Risks and edge cases
All backends are compiled as normal modules; backend dependency failures affect the whole crate until future feature-gating is introduced.

## Test signals
Coverage comes from backend-specific generic tests instantiated in `hash/tests.rs`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/backends/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/backends/openssl.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/backends/openssl.rs

## Purpose
Default SHA-512 hash backend using OpenSSL.

## Important APIs, types, and functions
- `OpensslSha512` implements `HashAlgorithmDef` and `HashAlgorithm<64, 8>`.
- Uses `openssl::sha::Sha512`.

## Control flow
Initializes an OpenSSL SHA-512 hasher, updates with salt then data, finishes, wraps bytes in `Digest`, and returns `Hash`.

## State and persistence behavior
Stateless except for local hasher state. Salt is preserved in the returned `Hash` for future verification.

## Dependencies and integration points
Integrated as `pub type Sha512 = backends::OpensslSha512` in the parent module and benchmarked against alternate backends.

## Risks and edge cases
OpenSSL output must remain byte-identical to other backends because compatibility tests assert exact vectors. Native OpenSSL build/runtime behavior can affect portability.

## Test signals
Generic hash tests instantiate both `Sha512` and `OpensslSha512`, checking exact digest vectors and backend parity.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/backends/openssl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/backends/sha2.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/backends/sha2.rs

## Purpose
Pure Rust SHA-512 backend using the RustCrypto `sha2` crate.

## Important APIs, types, and functions
- `Sha2Sha512` implements `HashAlgorithmDef` and `HashAlgorithm<64, 8>`.
- Imports `sha2::Digest` trait for `new`, `update`, and `finalize`.

## Control flow
Creates a `sha2::Sha512`, feeds salt then data, finalizes to a generic-array output, converts it into `[u8; 64]`, and returns the shared `Hash` shape.

## State and persistence behavior
No persistent state; returned salt and digest match the common hash format.

## Dependencies and integration points
Provides the portable backend for benchmarks and generic compatibility tests.

## Risks and edge cases
Any change to salt ordering or final byte conversion would break stored hash compatibility. This backend is useful when native OpenSSL/libsodium availability is constrained.

## Test signals
Generic hash tests assert deterministic behavior and exact compatibility vectors for this backend.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/backends/sha2.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/digest.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/digest.rs

## Purpose
Defines the fixed-size digest wrapper used as the output of hash algorithms.

## Important APIs, types, and functions
- `Digest<const DIGEST_LEN: usize>([u8; DIGEST_LEN])`.
- `new`, `to_hex`, and `from_hex`.
- Custom `Debug` prints the digest as hex inside a tuple.

## Control flow
`from_hex` decodes the full input with `hex::decode`, checks exact byte length, copies into a fixed array, and returns `InvalidStringLength` when the decoded byte count differs.

## State and persistence behavior
Digest is copyable immutable byte state. Hex encoding/decoding is the storage/display boundary and always uses lowercase output from `hex::encode`.

## Dependencies and integration points
Used by all hash backends and by `Hash`. Compatibility tests compare `to_hex()` values.

## Risks and edge cases
`from_hex` allocates a temporary `Vec` before length validation. It rejects wrong decoded byte length but reports the generic hex length error rather than a custom digest-size error.

## Test signals
Unit tests cover round trip, invalid length, invalid characters, debug formatting, and a full exact hex pattern.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/digest.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/hash.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/hash.rs

## Purpose
Defines the common `Hash` result type that bundles a digest with the salt used to compute it.

## Important APIs, types, and functions
- `Hash<const DIGEST_LEN: usize, const SALT_LEN: usize>` with public `digest` and `salt` fields.
- Associated constants `DIGEST_LEN` and `SALT_LEN`.

## Control flow
No runtime control flow beyond type construction by backends.

## State and persistence behavior
Copyable value type holding digest and salt. The public fields make serialization/storage the caller's responsibility.

## Dependencies and integration points
Connects `Digest` and `Salt` and is the return value for `HashAlgorithm::hash` across all backends.

## Risks and edge cases
Public fields keep the API simple but allow callers to mix digest/salt values manually. Const generic dimensions enforce length consistency at compile time.

## Test signals
Behavior is indirectly tested by hash backend tests that compare digest and salt preservation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/hash.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/mod.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/mod.rs

## Purpose
Top-level hash module defining the hash traits, exporting hash value types, and selecting the default SHA-512 backend.

## Important APIs, types, and functions
- Traits `HashAlgorithmDef` and `HashAlgorithm<const DIGEST_LEN, const SALT_LEN>`.
- Re-exports `Digest`, `Hash`, `Salt`, and concrete backend types.
- `pub type Sha512 = backends::OpensslSha512`.

## Control flow
No runtime control flow. Implementations call `HashAlgorithm::hash` with explicit salt and input data.

## State and persistence behavior
The module defines no state. It establishes the persistent hash format contract: digest bytes plus salt bytes, with salt prepended before hashing.

## Dependencies and integration points
Used by benchmarks, tests, and downstream CryFS integrity code. It centralizes backend choice while still exposing alternatives.

## Risks and edge cases
TODO comments flag possible hardening by increasing salt size or switching to SHA3. The default backend selection is a type alias, so changing it must preserve exact digest compatibility or migrate stored data.

## Test signals
`hash/tests.rs` uses generic instantiations for default and concrete backends to enforce parity.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/salt.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/salt.rs

## Purpose
Defines the fixed-size salt wrapper for hash operations.

## Important APIs, types, and functions
- `Salt<const SALT_LEN: usize>([u8; SALT_LEN])`.
- `new`, `get`, `to_hex`, `from_hex`, and `generate_random`.
- Derives `derive_more::From` for raw array conversion.

## Control flow
`from_hex` decodes and length-checks, then copies into the fixed array. `generate_random` fills the array using `rand::rng().random()`.

## State and persistence behavior
Salt is copyable byte state, usually persisted alongside a digest. Hex output is lowercase; debug output reveals the salt in hex, which is acceptable because salts are non-secret.

## Dependencies and integration points
Consumed by all hash backends, tests, and benchmarks. It is part of the `Hash` return value.

## Risks and edge cases
Randomness source is `rand`'s default RNG interface. Tests assert two generated salts differ, which has an astronomically small false-failure probability for 8-byte salts.

## Test signals
Unit tests cover hex round trip, invalid length, random inequality, debug formatting, and an exact byte-to-hex mapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/salt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/tests.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/hash/tests.rs

## Purpose
Generic test suite verifying all SHA-512 backends share identical behavior and compatibility vectors.

## Important APIs, types, and functions
- `data(size, seed)` builds deterministic random `Data`.
- Generic tests over `Hasher: HashAlgorithm<64, 8>`.
- Instantiates for `Sha512`, `OpensslSha512`, `Sha2Sha512`, and `LibsodiumSha512`.

## Control flow
Each test calls the generic hasher with fixed salts and inputs, then compares digest/salt behavior. Compatibility tests assert exact SHA-512(salt || data) hex outputs.

## State and persistence behavior
No persistent state. The exact expected digest constants are compatibility fixtures for any stored or protocol-level hashes using this algorithm.

## Dependencies and integration points
Uses `generic-tests`, `rand`, `cryfs_utils::Data`, and the hash module's public traits/types. It validates backend interchangeability.

## Risks and edge cases
Exact-vector tests intentionally make salt order and algorithm changes breaking. The tests do not cover serialization of `Hash` as a whole because the wrapper has no serializer here.

## Test signals
Signals include deterministic same-salt outputs, different salt/data outputs, empty input support, and exact digest compatibility for short, empty, and 1024-byte inputs.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/hash/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/mod.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/kdf/mod.rs

## Purpose
Top-level key-derivation module defining traits for serializable KDF parameters and password-based KDF implementations.

## Important APIs, types, and functions
- `KDFParameters` requires deterministic `serialize` and fallible `deserialize`.
- `PasswordBasedKDF` associates `Settings` and `Parameters`, and provides `derive_key` plus `generate_parameters`.
- Exposes the `scrypt` module.

## Control flow
The traits define contracts only. Concrete implementations generate salt-bearing parameters, derive an `EncryptionKey` of requested size from password bytes and parameters, and allow serialized parameters to reproduce the same key.

## State and persistence behavior
KDF parameters are explicitly intended to be stored with encrypted data. Derived keys are returned as protected-memory `EncryptionKey` values.

## Dependencies and integration points
Connects KDF code to `symmetric::EncryptionKey` and `anyhow::Result`. Filesystem configuration and unlock paths can persist serialized `KDFParameters`.

## Risks and edge cases
Trait methods do not return errors from `derive_key`; current backends panic on invalid parameters or backend errors. That makes deserialize-time validation and compatibility tests important.

## Test signals
Concrete scrypt tests validate parameter serialization and derived key reproducibility across backends.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/mod.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/mod.rs

## Purpose
Namespace for scrypt KDF backend implementations.

## Important APIs, types, and functions
- Public submodules `openssl` and `scrypt`.
- Documents `ScryptScrypt` and `ScryptOpenssl` choices.

## Control flow
No runtime control flow; it exposes backend modules.

## State and persistence behavior
No state.

## Dependencies and integration points
Parent `scrypt` module aliases the pure Rust backend as default, while tests and benchmarks import both modules through this namespace.

## Risks and edge cases
TODO notes indicate backend feature selection is not yet configurable by Cargo features.

## Test signals
Backend correctness is tested via generic KDF tests instantiated for both concrete backend types.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/openssl.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/openssl.rs

## Purpose
OpenSSL-backed implementation of the scrypt password-based KDF.

## Important APIs, types, and functions
- `ScryptOpenssl` implements `PasswordBasedKDF`.
- Uses `openssl::pkcs5::scrypt` with `n = 1 << log_n`, `r`, `p`, and `MAXMEM = u64::MAX`.
- Delegates parameter generation to `ScryptParams::generate`.

## Control flow
`derive_key` asserts `log_n < 64`, computes OpenSSL parameters, allocates an `EncryptionKey`, and fills key bytes inside the key initializer closure. OpenSSL errors are converted to panics by `expect`.

## State and persistence behavior
Does not persist state. It consumes serialized/deserialized `ScryptParams` and produces protected-memory key material.

## Dependencies and integration points
Shares `ScryptParams` with the Rust backend, so stored parameter bytes are backend-independent. Used by benchmarks and generic compatibility tests.

## Risks and edge cases
`MAXMEM = u64::MAX` means OpenSSL is not constrained by an application-level memory limit. Invalid parameters or OpenSSL failures panic rather than returning `Result`.

## Test signals
Generic scrypt tests verify reproducibility, exact legacy vectors, empty/unicode/long password behavior, and parity with the default backend.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/openssl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/scrypt.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/scrypt.rs

## Purpose
Default pure Rust scrypt KDF backend using the RustCrypto `scrypt` crate.

## Important APIs, types, and functions
- `ScryptScrypt` implements `PasswordBasedKDF`.
- Builds `scrypt::Params::new(log_n, r, p)`.
- Calls `scrypt::scrypt` to fill an `EncryptionKey`.

## Control flow
`derive_key` converts stored parameters into RustCrypto parameters, panics with parameter debug text on invalid input, then derives into protected key memory. `generate_parameters` delegates to `ScryptParams::generate`.

## State and persistence behavior
No persistent state beyond using persisted `ScryptParams`. Output key is protected and zeroed by `EncryptionKey` semantics.

## Dependencies and integration points
This backend is aliased as `Scrypt` in the parent module and is used by default examples, tests, and benchmark parameter generation.

## Risks and edge cases
A TODO notes some CryFS 1.0 parameter settings may not load in CryFS 2.0 due to RustCrypto parameter constraints. Like OpenSSL, invalid derivation panics instead of returning an error.

## Test signals
Generic scrypt tests cover exact legacy serialized parameters and derived-key vectors, including default settings.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/backends/scrypt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/mod.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/mod.rs

## Purpose
Top-level scrypt module documenting cost parameters, exporting settings/parameter types, and selecting the default scrypt backend.

## Important APIs, types, and functions
- Re-exports `ScryptParams` and `ScryptSettings`.
- Public `backends` module.
- `pub type Scrypt = backends::scrypt::ScryptScrypt`.

## Control flow
No runtime control flow; it establishes type aliases and module visibility.

## State and persistence behavior
Defines the public path for serialized scrypt parameters used by encrypted data configuration.

## Dependencies and integration points
Used by KDF callers and tests as the default password KDF. Connects settings, serialized parameters, and backend implementations.

## Risks and edge cases
Default backend changes must preserve derived-key compatibility for existing serialized parameters. Documentation advertises high-memory presets that can be expensive in tests/benchmarks.

## Test signals
Includes `tests.rs`, which instantiates generic KDF tests for default and concrete backends.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/params.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/params.rs

## Purpose
Defines `ScryptParams`, the persisted binary parameters needed to reproduce scrypt-derived keys.

## Important APIs, types, and functions
- `ScryptParams { log_n, r, p, salt }` with `binrw` little-endian serialization.
- `generate`, accessors, `KDFParameters::serialize/deserialize`, and `Debug`.
- `write_log_n` serializes `log_n` as `n = 2^log_n`; `parse_log_n` validates power-of-two `n`.

## Control flow
Generation validates `log_n < 64`, creates a random salt of configured length, and stores compact `log_n`. Deserialization reads an on-disk `u64 n`, converts to `log_n`, checks exact power-of-two equivalence, then reads remaining bytes as salt.

## State and persistence behavior
This is a critical persistence format: serialized bytes are little-endian `n`, `r`, `p`, then arbitrary-length salt. Debug prints salt hex for diagnostics.

## Dependencies and integration points
Implements `KDFParameters` for the generic KDF trait. Both scrypt backends consume this type and compatibility tests pin exact serialized hex strings.

## Risks and edge cases
Salt has no minimum length validation on deserialize. `write_log_n` asserts and can panic if called with invalid internal state. Non-power-of-two stored `n` is rejected.

## Test signals
Unit tests verify generated fields and serialize/deserialize round trip. KDF tests add exact legacy serialized parameter vectors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/params.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/settings.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/settings.rs

## Purpose
Defines scrypt cost settings and named presets for production, low-memory, paranoid, and test derivations.

## Important APIs, types, and functions
- `ScryptSettings { log_n, r, p, salt_len }`.
- Presets `PARANOID`, `DEFAULT`, `LOW_MEMORY`, and `TEST`.
- Unit test `params_are_valid` validates presets against RustCrypto `scrypt::Params`.

## Control flow
No runtime control flow beyond callers choosing a preset and passing it to `ScryptParams::generate`.

## State and persistence behavior
Settings themselves are not persisted; generated `ScryptParams` persist the chosen numeric values and random salt.

## Dependencies and integration points
Used by KDF generation, examples, tests, and benchmarks. Comments document approximate memory usage for operational tuning.

## Risks and edge cases
Production presets can require large memory allocations, especially `PARANOID` and `DEFAULT`. `TEST` is public despite a TODO to restrict it, so callers could accidentally use weak settings outside tests.

## Test signals
`rstest` validates every preset can generate parameters accepted by `scrypt::Params::new`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/settings.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/tests.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/tests.rs

## Purpose
Generic test suite ensuring scrypt backends produce reproducible and backward-compatible keys.

## Important APIs, types, and functions
- Tests over `S: PasswordBasedKDF<Settings = ScryptSettings, Parameters = ScryptParams>`.
- Instantiates default `Scrypt`, `ScryptScrypt`, and `ScryptOpenssl`.
- Uses `KDFParameters::serialize/deserialize` and exact hex fixtures.

## Control flow
Tests generate parameters, derive keys of 56, 32, and 16 bytes, serialize/deserialize parameters, and re-derive. Compatibility tests deserialize fixed parameter hex and compare exact derived key hex.

## State and persistence behavior
Fixed serialized parameter vectors represent the durable on-disk KDF contract. Tests also verify password byte handling for empty, Unicode, and long passwords.

## Dependencies and integration points
Exercises both backend implementations through the shared trait and confirms `EncryptionKey::to_hex` values.

## Risks and edge cases
The default-settings compatibility test can be slower because it uses expensive production settings. Tests expect uppercase key hex from `EncryptionKey::to_hex`.

## Test signals
Signals include key reproducibility after parameter serialization, exact legacy key vectors for multiple key sizes, password sensitivity, empty/unicode/long password support, and backend parity.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/lib.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/lib.rs

## Purpose
Crate root for CryFS cryptographic primitives, exporting hash, KDF, and symmetric modules with strict documentation and unsafe-code policy.

## Important APIs, types, and functions
- `#![forbid(unsafe_code)]` and `#![deny(missing_docs)]`.
- Public modules `hash`, `kdf`, and `symmetric`.
- Calls `cryfs_version::assert_cargo_version_equals_git_version!()`.

## Control flow
No runtime control flow. The version assertion macro expands at compile time to enforce Cargo/git version consistency.

## State and persistence behavior
The crate root stores no state but governs public API and security posture.

## Dependencies and integration points
Integrates with `cryfs-version`; submodules connect to `cryfs-utils`, OpenSSL, sodiumoxide, and RustCrypto crates.

## Risks and edge cases
`forbid(unsafe_code)` only applies to this crate, not native/library dependencies. Missing-doc denial makes API additions require documentation.

## Test signals
Doctest examples and submodule tests/benches provide validation; the root itself has no unit tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/aesgcm.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/aesgcm.rs

## Purpose
Defines AES-GCM type aliases and the default nonce-size policy for symmetric encryption.

## Important APIs, types, and functions
- `DefaultNonceSize = U16`.
- `LibsodiumAes256GcmNonce12` for libsodium's fixed 12-byte AES-GCM nonce.
- `AeadAes256Gcm`, `OpensslAes256Gcm`, `Aes256Gcm`, and AES-128 equivalents.

## Control flow
No runtime control flow; aliases select backend implementations and key/nonce/tag sizes through type parameters.

## State and persistence behavior
The alias selection affects ciphertext layout because nonce size is the ciphertext prefix length. Default AES-GCM uses a 16-byte nonce for random-nonce collision resistance.

## Dependencies and integration points
Feeds public exports in `symmetric/mod.rs`, compatibility tests, and benchmarks. Depends on `generic_array::typenum::U16`, `aes-gcm`, and OpenSSL backend types.

## Risks and edge cases
Changing `DefaultNonceSize` or default backend impacts ciphertext compatibility. AES-128 is documented as not recommended but still exported and tested.

## Test signals
Cipher generic tests instantiate default, 12-byte, and 16-byte nonce variants across OpenSSL/RustCrypto/libsodium where applicable.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/aesgcm.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/aead.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/aead.rs

## Purpose
Generic RustCrypto AEAD backend adapter implementing CryFS `Cipher`/`CipherDef` for `aead`-ecosystem ciphers.

## Important APIs, types, and functions
- `AeadCipher<C: KeyInit + AeadInPlace>` stores an `EncryptionKey`.
- `CipherDef` maps key size, nonce prefix, and tag suffix from AEAD type-level sizes.
- `encrypt`, `decrypt`, and `random_nonce`.

## Control flow
`new` validates key length. Encryption creates a cipher from key bytes, generates a random nonce, encrypts in place, grows `Data` into nonce-prefix/tag-suffix layout, and writes overhead bytes. Decryption checks minimum size, splits nonce/cipherdata/tag, verifies/decrypts in place, then shrinks to plaintext.

## State and persistence behavior
Cipher instances hold protected key material. Ciphertext format is `nonce || encrypted_payload || tag`, with no associated data.

## Dependencies and integration points
Used by AES-GCM and XChaCha20-Poly1305 RustCrypto aliases. Relies on `Data` having preallocated prefix/suffix capacity for no-reallocation growth.

## Risks and edge cases
Encryption panics if `Data` lacks sufficient reserved prefix/suffix capacity. Cipher construction is repeated per operation. No associated data is authenticated, so all metadata integrity must be handled elsewhere.

## Test signals
Shared cipher tests cover round trips, tamper failure, too-small ciphertext failure, nonce nondeterminism, backend interoperability, and compatibility ciphertext vectors.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/aead.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/cipher.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/cipher.rs

## Purpose
Placeholder module for future ciphers using the RustCrypto `cipher` trait ecosystem.

## Important APIs, types, and functions
No APIs are defined; the file contains only a module-level documentation comment.

## Control flow
No runtime control flow.

## State and persistence behavior
No state.

## Dependencies and integration points
Declared by `symmetric/backends/mod.rs` but currently unused.

## Risks and edge cases
Its presence may imply future backend expansion, but it contributes no behavior today.

## Test signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/cipher.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/libsodium.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/libsodium.rs

## Purpose
libsodium-backed AEAD implementations for AES-256-GCM and XChaCha20-Poly1305.

## Important APIs, types, and functions
- `init_libsodium` guarded by `Once`.
- `Aes256Gcm` with `is_available`, `CipherDef`, and `Cipher`.
- `XChaCha20Poly1305` with `CipherDef` and `Cipher`.
- Shared `_encrypt`, `_decrypt`, and key conversion helpers.

## Control flow
Constructors validate key length and initialize libsodium; AES-GCM also creates an `Aes256Gcm` object that may require hardware support. Encryption generates a nonce, seals plaintext in place, grows `Data` to store nonce prefix and tag suffix, then returns ciphertext. Decryption validates length, splits overhead, reconstructs libsodium nonce/tag types, verifies/decrypts in place, and shrinks to plaintext.

## State and persistence behavior
Global libsodium initialization is process-wide and one-time. Cipher instances hold protected `EncryptionKey`. Ciphertext format is shared with other backends: nonce prefix, encrypted payload, tag suffix.

## Dependencies and integration points
Provides public aliases for libsodium AES-GCM and default XChaCha20-Poly1305. Interoperability tests cross-decrypt with RustCrypto and OpenSSL where formats match.

## Risks and edge cases
AES-GCM constructor panics if called without checking hardware availability. Encryption panics when `Data` lacks reserved overhead capacity. Associated data is `None`, so metadata binding is not provided here.

## Test signals
Generic cipher tests validate libsodium round trips, tamper/short-ciphertext failures, random nonce behavior, compatibility vectors, and cross-backend interoperability for XChaCha20 and 12-byte AES-GCM on supported architectures.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/libsodium.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/mod.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/mod.rs

## Purpose
Aggregator module for symmetric cipher backend implementations.

## Important APIs, types, and functions
- Public submodules `aead`, `cipher`, `libsodium`, and `openssl`.

## Control flow
No runtime control flow.

## State and persistence behavior
No state.

## Dependencies and integration points
Concrete cipher aliases in `aesgcm.rs` and `xchacha20poly1305.rs` refer to these backend modules.

## Risks and edge cases
All backend modules are compiled together; TODO notes indicate future feature-gating and production backend choice work.

## Test signals
Covered indirectly by the shared cipher tests instantiated for aliases using each backend.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/openssl.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/openssl.rs

## Purpose
OpenSSL AEAD backend adapter for AES-128-GCM and AES-256-GCM.

## Important APIs, types, and functions
- `CipherType` trait defines key size, nonce size, auth tag size, and OpenSSL cipher instantiation.
- `Aes256Gcm<NonceSize>` and `Aes128Gcm<NonceSize>` implement `CipherType`.
- `AeadCipher<C: CipherType>` implements `CipherDef` and `Cipher`.

## Control flow
Constructor validates key length and stores an OpenSSL cipher handle. Encryption generates a random nonce and tag, calls `encrypt_aead`, copies output back into the original `Data`, grows prefix/suffix overhead, and writes nonce/tag. Decryption validates size, splits nonce/cipherdata/tag, calls `decrypt_aead`, shrinks the `Data`, and copies plaintext back.

## State and persistence behavior
Cipher instances hold protected key bytes and an OpenSSL cipher descriptor. Ciphertexts use the common `nonce || ciphertext || tag` format with configurable nonce length and 16-byte tag.

## Dependencies and integration points
Default AES-GCM aliases point here. Interoperability tests compare OpenSSL outputs with RustCrypto and libsodium formats.

## Risks and edge cases
OpenSSL operations allocate separate output buffers, so performance includes copy-back costs. Encryption still requires preallocated `Data` overhead or panics on growth. No associated data is supplied.

## Test signals
Generic cipher tests cover OpenSSL AES-128/256 with default, 12-byte, and 16-byte nonces, cross-backend decryption, tamper failures, and fixed compatibility ciphertexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/backends/openssl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/cipher_tests.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/cipher_tests.rs

## Purpose
Comprehensive generic test suite for symmetric cipher correctness, interoperability, size accounting, nondeterminism, and backwards-compatible ciphertext formats.

## Important APIs, types, and functions
- Helper `key(num_bytes, seed)` creates deterministic `EncryptionKey`.
- `allocate_space_for_ciphertext<C>` creates `Data` with required overhead.
- Generic `enc_dec` tests cover encrypt/decrypt pairs, tamper, short ciphertext, and wrong key.
- Generic `basics` tests cover overhead size math and nonce nondeterminism.
- `backward_compatibility_test!` decrypts fixed ciphertext hex fixtures.

## Control flow
The suite instantiates test modules for default aliases, concrete OpenSSL/RustCrypto/libsodium backends, nonce-size variants, and selected cross-backend encrypt/decrypt pairs. Compatibility tests decrypt preencrypted `"Hello World"` ciphertexts with deterministic keys.

## State and persistence behavior
Fixed ciphertext hex strings encode the durable ciphertext layout contract for nonce prefix, ciphertext body, and tag suffix. Tests also model required `Data` reserved regions.

## Dependencies and integration points
Uses `generic-tests`, typenum `U12`/`U16`, `cryfs_utils::Data`, and all public cipher aliases. It is the main guard against backend format drift.

## Risks and edge cases
Libsodium AES-GCM tests are architecture-gated by x86/x86_64 but still may require runtime hardware support. Tests deliberately do not assert exact encryption output for fresh operations because nonces are random.

## Test signals
Signals include successful round trips, failed tamper/wrong-key/too-small decryptions, expected ciphertext length overheads, fresh encryption inequality, cross-backend interoperability, and exact legacy decryptability.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/cipher_tests.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/key.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/key.rs

## Purpose
Defines `EncryptionKey`, the protected-memory key container used by symmetric ciphers and KDF outputs.

## Important APIs, types, and functions
- `EncryptionKey { key_data, _lock_guard }`.
- `new`, `from_hex`, `to_hex`, `as_bytes`, `num_bytes`, `take_bytes`, `skip_bytes`, and `generate_random`.
- `Drop` zeroes key bytes with `sodiumoxide::utils::memzero`.

## Control flow
`new` allocates zeroed boxed bytes, attempts to lock memory pages with `region::lock`, warns on failure, calls the initializer closure, then stores optional lock guard. Split helpers copy portions into new protected keys. Random generation fills key bytes from `rand`.

## State and persistence behavior
Key bytes live in heap memory with best-effort mlock and are zeroed on drop. `to_hex`/`from_hex` intentionally expose/copy key material and are marked by TODO as test-only candidates but are currently public.

## Dependencies and integration points
Used by ciphers and KDFs. Logging reports lock failures without failing functionality. `lockable::InfallibleUnwrap` is used by infallible constructors.

## Risks and edge cases
Memory locking is best-effort and may fail silently except for a warning. Public `to_hex` and `from_hex` bypass secret-protection goals. `take_bytes` and `skip_bytes` panic on out-of-bounds slicing.

## Test signals
Key behavior is indirectly tested through KDF and cipher tests that compare hex output, key sizes, deterministic seeded keys, and wrong-key decrypt failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/key.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/mod.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/mod.rs

## Purpose
Top-level symmetric encryption module defining cipher traits, public aliases, error types, and max key-size guarantees.

## Important APIs, types, and functions
- `Cipher` trait with `encrypt`, `decrypt`, and overhead accessors.
- `CipherDef` trait with `new`, `KEY_SIZE`, and overhead constants.
- `InvalidKeySizeError`.
- Re-exports `EncryptionKey`, AES-GCM aliases, XChaCha20-Poly1305 aliases, and `DefaultNonceSize`.
- `MAX_KEY_SIZE = 56` with `const_assert!` checks.

## Control flow
Traits define the runtime encryption/decryption contract. Concrete aliases select backends. Compile-time assertions verify supported ciphers do not exceed the maximum KDF-derived key size.

## State and persistence behavior
The module defines ciphertext shape expectations: prefix overhead stores nonce/IV and suffix overhead stores authentication tag. `MAX_KEY_SIZE` affects KDF strategy and backwards compatibility when switching ciphers.

## Dependencies and integration points
Used by CryFS encryption layers, KDFs, benchmarks, and tests. Integrates `Data`, `derive_more`, `static_assertions`, and backend modules.

## Risks and edge cases
The `Cipher::encrypt` API requires callers to provide `Data` with adequate reserved overhead; misuse can panic in backends. No associated data is part of the trait, so authenticated metadata must be handled by surrounding layers.

## Test signals
`cipher_tests.rs` validates the trait contract across all exported ciphers and backend combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/xchacha20poly1305.rs -->
# sources/security-integrity/cryfs/crates/crypto/src/symmetric/xchacha20poly1305.rs

## Purpose
Defines XChaCha20-Poly1305 type aliases for RustCrypto and libsodium backends, selecting libsodium as default.

## Important APIs, types, and functions
- `AeadXChaCha20Poly1305` maps to the generic RustCrypto AEAD adapter.
- `LibsodiumXChaCha20Poly1305` maps to the libsodium backend.
- `XChaCha20Poly1305` aliases libsodium as default.

## Control flow
No runtime control flow; backend behavior is in the referenced adapters.

## State and persistence behavior
XChaCha20 ciphertexts use 24-byte nonce prefix and 16-byte tag suffix. Default backend changes must keep this format interoperable.

## Dependencies and integration points
Publicly re-exported by `symmetric/mod.rs` and instantiated in tests/benchmarks.

## Risks and edge cases
Defaulting to libsodium introduces native dependency/runtime initialization needs, but interoperability tests ensure the RustCrypto format matches.

## Test signals
Cipher tests verify libsodium and RustCrypto XChaCha20 cross-decrypt each other's ciphertexts and can decrypt legacy fixed ciphertexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/crypto/src/symmetric/xchacha20poly1305.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/Cargo.toml -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/Cargo.toml

## Purpose
Cargo manifest for the CryFS end-to-end performance test and benchmark crate.

## Important APIs, types, and functions
- Depends on CryFS blobstore, blockstore, config, filesystem, runner, rustfs, utils, and version crates.
- Uses Criterion with `async_tokio` for benchmarks.
- `benchmark` feature switches code paths from operation-count tests to mounted filesystem benchmarks.
- Registers `all_operations` bench with `harness = false`.

## Control flow
Normal `cargo test` builds the in-process operation-count harness. `cargo bench --features benchmark` enables mounted benchmark code and the Criterion main in `benches/all_operations.rs`.

## State and persistence behavior
The manifest itself stores no runtime state but selects whether temporary in-memory/tracked stores or real mounted benchmark paths are compiled.

## Dependencies and integration points
This crate is highly integrated with internal CryFS stack layers and FUSE/rustfs backends. It also depends on `nix`, `fuser`, `tokio`, `tempfile`, and logging utilities.

## Risks and edge cases
The crate depends on `cryfs-runner` despite a TODO saying it should not. Benchmark feature changes the compiled module set, so test and bench paths can diverge.

## Test signals
Cargo targets expose operation-count tests and Criterion benchmark execution; correctness expectations live in operation modules.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/benches/all_operations.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/benches/all_operations.rs

## Purpose
Criterion benchmark entry point aggregating all filesystem operation benchmarks when the `benchmark` feature is enabled.

## Important APIs, types, and functions
- Non-benchmark `main` panics with an instruction to enable the feature.
- Feature-gated `criterion_main!` lists benchmark groups from `cryfs_e2e_perf_tests::operations::*`.

## Control flow
Without `benchmark`, running the bench binary fails immediately. With the feature, Criterion dispatches every listed operation benchmark group, including both fuser/fuse-mt variants where defined.

## State and persistence behavior
No persistent state in this file; each benchmark group manages its own fixtures and temp stores.

## Dependencies and integration points
Connects the operation modules to Criterion's bench harness and enforces the feature-gated compilation model described by the crate root.

## Risks and edge cases
Adding a new operation module requires adding it here to be benchmarked. The panic path prevents accidental meaningless bench runs without the feature.

## Test signals
Criterion benchmark output across all listed filesystem operations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/benches/all_operations.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/env_logger.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/env_logger.rs

## Purpose
One-time logger initialization helper for non-benchmark performance tests.

## Important APIs, types, and functions
- Static `INITED: Once`.
- `init()` builds an `env_logger::Builder`, defaults filter level to `Off`, parses environment overrides, and initializes logging once.

## Control flow
`init` uses `Once::call_once` to prevent duplicate logger initialization panics across many tests.

## State and persistence behavior
Process-global logger state is initialized once. No files are written by this helper.

## Dependencies and integration points
Used by test harness code under `#[cfg(not(feature = "benchmark"))]` to keep logs quiet unless environment variables opt in.

## Risks and edge cases
Global logger initialization cannot be undone; tests that need different logger setup must coordinate with this helper.

## Test signals
No direct tests; absence of duplicate-init panics and quiet default logs are the operational signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/env_logger.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/common.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/common.rs

## Purpose
Common non-benchmark helper for constructing deterministic `RequestInfo` used by in-process rustfs drivers.

## Important APIs, types, and functions
- `request_info()` returns `RequestInfo` with zeroed `unique`, uid, gid, and pid.

## Control flow
No branching; creates a value on demand.

## State and persistence behavior
No state. The fixed uid/gid/pid influence permission metadata in operation-count tests.

## Dependencies and integration points
Used by `fuse_mt.rs` and `fuser.rs` to invoke rustfs high-level/low-level APIs without a real kernel FUSE request.

## Risks and edge cases
All tests run as uid/gid zero from the filesystem API's perspective, so permission behavior may differ from mounted benchmark/syscall paths.

## Test signals
Indirectly covered by all in-process filesystem driver tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/fuse_mt.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/fuse_mt.rs

## Purpose
Implements `FilesystemDriver` using rustfs's object/high-level API, modeling fuse-mt-style path-based operations without a real mount.

## Important APIs, types, and functions
- `FusemtFilesystemDriver` wraps `ObjectBasedFsAdapter<Device>`.
- `NodeHandle = AbsolutePathBuf`; `FileHandle = cryfs_rustfs::FileHandle`.
- Implements all common filesystem operations: create, mkdir, symlink, attrs, chmod/chown/truncate/time updates, open/release, readdir, read/write, rename, fsync.
- `ReadCallbackImpl` captures async callback data in `Arc<Mutex<Option<FsResult<Vec<u8>>>>>`.

## Control flow
Most operations convert parent/name handles into absolute paths and call corresponding high-level rustfs methods with fixed `request_info()`. `release` simulates FUSE flush before release. `readdir` opens a directory, reads entries, releases the handle, then normalizes self/parent references. Reads use callback capture because the rustfs API returns data through a callback.

## State and persistence behavior
Driver owns an async-drop guard around the adapter/device. Reset after setup flushes adapter cache; reset after test does nothing because this object adapter has no separate cache to clear. Filesystem data persists in the fixture's tracked block/blob stores.

## Dependencies and integration points
Bridges the generic test fixture to `cryfs_rustfs::object_based_api::ObjectBasedFsAdapter`, high-level async API traits, CryFS `CryDevice`, and path types.

## Risks and edge cases
Path-based handles avoid inode cache modeling, so operation counts differ from fuser driver variants. Read callbacks unwrap captured results and will panic if the callback is not invoked.

## Test signals
All operation modules instantiated with the Fusemt fixture compare expected blobstore/high-level/low-level counts and functional success.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/fuse_mt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/fuser.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/fuser.rs

## Purpose
Implements `FilesystemDriver` over rustfs's low-level FUSE-like API with configurable inode-cache modeling.

## Important APIs, types, and functions
- `FuserCacheBehavior` abstracts cached and uncached node handle behavior.
- `WithInodeCache` uses `InodeGuard`; `WithoutInodeCache` uses `AbsolutePathBuf` and explicit lookup/forget traversal.
- `_split_common` optimizes two-path lookup for rename.
- `InodeGuard` calls `forget` on drop.
- `FuserFilesystemDriver<C>` implements the full driver trait using `ObjectBasedFsAdapterLL`.
- `ReplyDirectoryImpl` and `ReadCallbackImpl` adapt callback-based APIs.

## Control flow
Driver methods load required inode(s) through the cache behavior, invoke low-level rustfs operations, and then either preserve inode guards or forget temporary inodes. Mutating metadata operations use `setattr` with only relevant fields set. Rename loads old/new parents together so common ancestors are not duplicated and same-directory moves use correct inode identity.

## State and persistence behavior
The driver owns an `AsyncDropArc<ObjectBasedFsAdapterLL<Device>>`. `WithInodeCache` holds inode references until handles drop; `WithoutInodeCache` forgets looked-up inodes after each operation to simulate cold kernel cache. Reset methods flush/reset filesystem caches. Underlying filesystem content persists in fixture stores.

## Dependencies and integration points
Bridges CryFS fixture devices to low-level rustfs APIs, FUSE root inode semantics, callback traits, and async drop. Operation modules use it to distinguish cached and uncached fuser performance.

## Risks and edge cases
Drop for `InodeGuardInner` blocks inside Tokio to call async forget/drop, which can deadlock if runtime assumptions change. Missing forget calls would skew operation counts and leak filesystem references. Callback capture unwraps assume APIs always call callbacks.

## Test signals
Operation-count tests instantiate fuser-with-cache and fuser-without-cache variants; expected counts in operation modules validate lookup/cache behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/fuser.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/interface.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/interface.rs

## Purpose
Defines the common async filesystem driver abstraction used by both in-process performance tests and mounted benchmarks.

## Important APIs, types, and functions
- `FilesystemDriver: AsyncDrop + Debug`.
- Associated `NodeHandle` and `FileHandle` types.
- `new` accepts a fully constructed `CryDevice` stack.
- Async methods cover initialization, cache reset, namespace operations, metadata operations, open file operations, read/write, statfs, rename, and fsync.
- Default `mkdir_recursive` builds nested directories using repeated `mkdir`.

## Control flow
Test operation modules call this trait uniformly. Implementations translate abstract node handles into high-level paths, low-level inodes, or real mounted paths.

## State and persistence behavior
The trait owns no state but defines lifecycle hooks: `init`, `destroy`, `reset_cache_after_setup`, and `reset_cache_after_test`. These hooks determine what remains cached when operation counts are measured.

## Dependencies and integration points
Central contract between `FilesystemFixture`, test drivers, operation modules, and concrete fuser/fuse-mt/mounting drivers.

## Risks and edge cases
`Option<NodeHandle>` represents root; this is repeatedly TODO-noted as less explicit than a root handle. Implementations must keep operation semantics equivalent despite different handle models.

## Test signals
All operation perf tests compile against this trait and compare behavior/counts across implementations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/interface.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/mod.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/mod.rs

## Purpose
Filesystem driver module aggregator and feature-gated export point.

## Important APIs, types, and functions
- Re-exports `FilesystemDriver`.
- Non-benchmark exports: `FuserFilesystemDriver`, `WithInodeCache`, `WithoutInodeCache`, and `FusemtFilesystemDriver`.
- Benchmark exports: `FusemtMountingFilesystemDriver` and `FuserMountingFilesystemDriver`.

## Control flow
Compile-time `cfg(feature = "benchmark")` selects mounted drivers for benchmarks or in-process drivers for operation-count tests.

## State and persistence behavior
No state.

## Dependencies and integration points
Connects crate features to the fixture/test-driver code that chooses concrete driver types.

## Risks and edge cases
Feature-gated module sets mean code can compile in test mode but fail in benchmark mode, or vice versa.

## Test signals
Compilation under both default test and benchmark features is the direct signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/mounting.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/mounting.rs

## Purpose
Benchmark-only `FilesystemDriver` implementation that mounts CryFS into a temp directory through fuser or fuse-mt backends and performs real OS syscalls.

## Important APIs, types, and functions
- `MountingBackend` with `spawn_mount`.
- `FuserBackend` and `FusemtBackend`.
- `MountingFilesystemDriver<B>` with `MaybeMounted` state.
- Helpers `real_path_for_node`, `metadata_to_node_attrs`, `asyncify`, and `to_timespec`.

## Control flow
`new` stores an unmounted device and temp mount directory. `init` swaps state from `NotMounted` to `Mounted` by spawning the selected backend. `destroy` swaps back through `Invalid` and unmounts in a blocking task. Filesystem operations translate abstract absolute paths to paths under the mount directory and call Tokio fs APIs, libc/nix functions, or file-handle methods.

## State and persistence behavior
State is a mutex-protected mount lifecycle enum. Filesystem contents persist in the underlying fixture stores while mounted. Temp mount directory is removed when `TempDir` drops. Reset-cache hooks are no-ops because real kernel/OS caches are outside the in-process harness.

## Dependencies and integration points
Integrates `cryfs_rustfs` mounted backends, `fuser`, `tokio::fs`, Unix metadata and permission APIs, `nix`, and the generic fixture. It is used only with the `benchmark` feature.

## Risks and edge cases
The file uses small `unsafe` libc calls for chmod despite the crypto crate forbidding unsafe elsewhere. OS/kernel behavior can add extra filesystem activity, so this driver is unsuitable for deterministic operation counts. Mutex state panics on invalid lifecycle calls.

## Test signals
Criterion benchmark behavior under mounted fuser/fuse-mt drivers; functional failures surface as `FsError::InternalError` or assertions in read/write sizing.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/mounting.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_fixture.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_fixture.rs

## Purpose
Builds the full CryFS blockstore/blobstore/filesystem stack for operation-count tests and benchmarks, inserting tracking wrappers at every relevant layer.

## Important APIs, types, and functions
- Constants `NUM_CHILDREN_PER_INNER_NODE`, `BLOCKSIZE_BYTES`, `NUM_BYTES_FOR_THREE_LEVEL_TREE`, and `MY_CLIENT_ID`.
- `ActionCounts` aggregates blobstore, high-level blockstore, and low-level blockstore counts.
- `FilesystemFixture<B, FS>` owns filesystem, tracked stores, blobstore, and temp local state.
- `create_filesystem`, `create_uninitialized_filesystem`, store/device construction helpers, `reset_counts`, `totals`, cache reset hooks, and `config`.

## Control flow
Fixture creation wraps a supplied low-level blockstore in tracking/shared/locking layers, computes overhead and config blocksize, creates a tracked blobstore, creates a CryFS device through `make_device`, then constructs the selected `FilesystemDriver`. `create_filesystem` additionally calls `init` and clears blobstore cache. Drop destroys the filesystem inside the current Tokio runtime.

## State and persistence behavior
Filesystem data lives in the supplied blockstore; local state lives in a temp directory. Tracking wrappers accumulate counts until reset. Config uses fixed root blob, encryption key, cipher, filesystem id, format version, and client id for reproducibility.

## Dependencies and integration points
Integrates blobstore, low/high-level blockstores, blockstore stack setup, config/local state, runner device creation, rustfs atime behavior, async drop wrappers, and concrete filesystem drivers.

## Risks and edge cases
Manual overhead calculation must match actual blockstore overhead; an assertion guards drift. Drop assumes a Tokio runtime is active. Cache reset behavior is carefully tuned and can deadlock if open files prevent cache unloading.

## Test signals
Operation modules call `totals` and compare `ActionCounts`; fixture assertions catch overhead mismatch and unexpected integrity violations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_fixture.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/lib.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/lib.rs

## Purpose
Crate root documenting and wiring the CryFS end-to-end performance test/benchmark harness.

## Important APIs, types, and functions
- `#![cfg(any(test, feature = "benchmark"))]` prevents normal library use.
- Modules: `env_logger` in non-benchmark mode, `filesystem_driver`, `filesystem_fixture`, public `operations`, `perf_test_macro`, `test_driver`, and `utils`.
- Compile-time version assertion through `cryfs_version`.

## Control flow
Compilation is mode-dependent: tests use in-memory/tracked APIs and operation-count assertions, while benchmark feature compiles mounted syscall drivers and Criterion benches.

## State and persistence behavior
No root state; submodules own temporary stores and counters.

## Dependencies and integration points
This is the public surface consumed by `benches/all_operations.rs` and by cargo tests generated from operation modules.

## Risks and edge cases
The crate is unavailable outside tests/benchmark feature by design. Feature-dependent module inclusion can hide compile failures in the other mode.

## Test signals
Successful `cargo test` and `cargo bench --features benchmark` compilation/execution validate the root wiring.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/main.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/main.rs

## Purpose
Placeholder binary entry point telling users to run tests instead of `cargo run`.

## Important APIs, types, and functions
- `main` prints a short instruction.

## Control flow
Single synchronous print statement.

## State and persistence behavior
No state.

## Dependencies and integration points
Exists because the crate has a binary target; real behavior lives in tests and benches.

## Risks and edge cases
Running the crate binary does not execute performance tests, which could confuse users unless they read the message.

## Test signals
No tests; the signal is the printed message.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/chmod.rs -->
# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/chmod.rs

## Purpose
Defines performance tests/benchmarks for `chmod` on files and directories at several path depths.

## Important APIs, types, and functions
- Invokes `perf_test!(chmod, [file_in_rootdir, dir_in_rootdir, file_in_nesteddir, file_in_deeplynesteddir])`.
- Scenario functions build fixtures, set up target nodes, execute `filesystem.chmod`, and declare expected `ActionCounts`.
- Uses `FixtureType` to vary expected counts for fuser cached, fuser uncached, and fuse-mt drivers.

## Control flow
Each scenario creates a filesystem, creates the relevant target in setup, resets caches through the test driver, performs chmod with a file or directory mode flag, and checks blobstore/high-level/low-level operation counters.

## State and persistence behavior
The operation mutates mode metadata on the target node and writes affected blobs/blocks. Expected counts reflect whether parent/path nodes are cached and how deep the target is.

## Dependencies and integration points
Uses the generic `FilesystemDriver`, `TestDriver`, path helpers, `Mode`, and count structs from blobstore/blockstore layers. It is included in both tests and the all-operations benchmark entry.

## Risks and edge cases
Many expected counts carry TODOs, meaning they encode observed behavior that may not yet be fully justified. Path-depth and cache-model changes will require careful count updates.

## Test signals
Signals are successful chmod execution and exact `ActionCounts` matches for root file, root directory, nested file, and deeply nested file scenarios across fixture types.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/chmod.rs -->
