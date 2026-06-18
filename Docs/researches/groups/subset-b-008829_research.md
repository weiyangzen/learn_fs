# Group Research: subset-b-008829

This grouped report covers the requested TiKV encryption, `engine_panic`, and `engine_rocks` source files. Each section is delimited for reconciliation into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/errors.rs -->
# sources/storage-engines/tikv/components/encryption/src/errors.rs

Purpose: Defines the encryption crate's central `Error` enum, `Result<T>` alias, retry-code plumbing, and adapters for cloud KMS errors. It is the boundary type used by dictionary persistence, master-key backends, stream crypters, and RocksDB integration.

Important APIs and types: `Error` wraps boxed generic errors, recoverable tail-record parse failures, retry-coded KMS errors, RocksDB strings, IO, OpenSSL, protobuf, wrong-master-key, and both-master-key-failed cases. `RetryCodedError` composes `Debug`, `Display`, `ErrorCodeExt`, `RetryError`, `Send`, and `Sync`. `CloudConvertError` adapts `cloud::error::Error` plus context text into `Error::RetryCodedError`. `cloud_convert_error` returns a closure suitable for `map_err`.

Control flow and state: Error conversion is mostly one-way into `Error`; `From<Error> for IoError` preserves raw IO errors and stringifies all other variants. `ErrorCodeExt` maps variants to TiKV error-code domains, while `RetryError` marks wrong-master-key and both-master-key-failed as non-retryable and currently treats most other cases as retryable.

Dependencies and integration: Used by KMS retry paths, file dictionary recovery, encrypted file parsing, data-key manager load fallback, and external stream retry machinery. It depends on `cloud`, `error_code`, OpenSSL, protobuf, and `tikv_util::stream::RetryError`.

Risks: Retry classification is intentionally broad and may retry protobuf/crypter/corruption errors that are not transient. `Other` maps to generic unknown code, so callers lose detailed classification unless they use specialized variants. `CloudConvertError` stores context separately from the cloud error but preserves the cloud error code and retryability.

Test signals: No local unit tests in this file; behavior is exercised indirectly by master-key backend, KMS, dictionary recovery, and manager tests that match `WrongMasterKey`, `BothMasterKeyFail`, and tail corruption behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/file_dict_file.rs -->
# sources/storage-engines/tikv/components/encryption/src/file_dict_file.rs

Purpose: Persists the plaintext file dictionary mapping data-file paths to `FileInfo`. It supports legacy whole-file rewrite format and a v2 append-log format that can compact back to a base dictionary.

Important APIs and types: `FileDictionaryFile::new` creates and rewrites a dictionary file. `open` recovers existing contents, optionally rewrites, and returns both the persistence handle and recovered `FileDictionary`. `insert`, `remove`, and `sync` mutate the log. `recovery`, `rewrite`, `convert_record_to_bytes`, and `parse_next_record` implement the on-disk format. Internal `LogRecord` distinguishes insert and remove records.

Control flow: V2 files contain an encrypted-file header with raw protobuf `FileDictionary` content followed by log records. Each record has crc32, file-name length, `FileInfo` length, type byte, name bytes, and optional serialized `FileInfo`. Recovery parses the header, loads v1 via `PlaintextBackend` decrypt or v2 directly, then replays records. Incomplete tail records are warned and trimmed by later rewrite; non-tail checksum/type/remove-null failures are treated as unrecoverable and call `set_panic_mark`.

State and persistence: `file_dict`, `removed`, `file_size`, and `append_file` mirror persisted state. V2 `rewrite` writes a random temporary file, syncs it, renames atomically, syncs the base directory, then reopens append mode. Non-log mode rewrites the whole file through `EncryptedFile` with `PlaintextBackend`. Remove-count threshold drives compaction.

Dependencies and integration: Used by `DataKeyManager` to keep file metadata durable before/after filesystem operations. Relies on `EncryptedFile::Header`, protobuf `FileDictionary`/`FileInfo`, crc32, `file_system`, and encryption metrics.

Risks: Mutating comments warn callers to update the in-memory dictionary before persistence. Actual filesystem operations and dictionary updates are not atomic, so higher layers must handle stale dictionary entries. Recovery deliberately tolerates only tail corruption; middle corruption requires manual intervention. `OpenOptions::open(...).unwrap()` in rewrite can panic on unexpected open failure.

Test signals: Tests cover v1/v2 normal insert-remove recovery, missing files, opening existing dictionaries, v1-to-v2 update, v2-to-v1 downgrade, and v2 unreadability through the legacy `EncryptedFile` path.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/file_dict_file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/io.rs -->
# sources/storage-engines/tikv/components/encryption/src/io.rs

Purpose: Provides transparent encrypting/decrypting `Read`, `Write`, `Seek`, `AsyncRead`, and `AsyncWrite` adapters for TiKV file I/O. It implements AES/SM4 CTR stream encryption while preserving random-access semantics by resetting the counter from byte offsets.

Important APIs and types: Public wrappers are `EncrypterReader`, `DecrypterReader`, `EncrypterWriter`, and `DecrypterWriter`. `create_aes_ctr_crypter` maps `EncryptionMethod` to OpenSSL ciphers. Internal `CrypterReader`, `CrypterWriter`, `CrypterCore`, and `AsyncWriteState` hold stream offset, OpenSSL crypter, reusable buffer, and pending async-write state.

Control flow: Plaintext method bypasses cryptography. Reads fill caller buffers then encrypt/decrypt in place. Seeks reset the core offset and lazily rebuild OpenSSL state. Writes encrypt into an internal buffer, write to the inner writer, and roll back the crypto offset on partial or failed writes. Async writes first encrypt into a buffer, then consume that buffer across polls until the encrypted bytes are written.

State and persistence behavior: No metadata is persisted here; state is per-stream. `CrypterCore::offset` advances only after successful cryptographic transformation. `reset_crypter` adjusts IV by block offset and consumes partial-block zeros so CTR keystream alignment matches random file offsets. `MAX_INPLACE_CRYPTION_SIZE` limits temporary buffer growth for in-place operations.

Dependencies and integration: Called by `DataKeyManager` when opening encrypted files and by other storage components that wrap file handles. It depends on OpenSSL, `file_system::File`, futures traits, `kvproto::EncryptionMethod`, and crate `Iv` validation.

Risks: Reader crypto errors panic because the underlying reader offset cannot be rolled back without wider API changes. Async write cancellation is guarded by a panic if another write tries to overwrite pending encrypted data. The implementation assumes CTR-mode update output length always equals input length; other modes would break invariants. SM4 support depends on the crate feature and linked OpenSSL support.

Test signals: Tests cover sync decrypt/read, encrypt-then-decrypt via readers and writers, random seeks and offsets, plaintext bypass, async read/write, injected async write failure, partial writes, and a should-panic case for aborted pending async writes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/lib.rs -->
# sources/storage-engines/tikv/components/encryption/src/lib.rs

Purpose: Crate root for TiKV encryption. It wires internal modules, re-exports the public API, and provides directory deletion helpers that keep encryption metadata consistent with filesystem cleanup.

Important APIs and types: Re-exports include config, `AesGcmCrypter`, `FileEncryptionInfo`, `Iv`, `EncryptedFile`, `Error`, `FileDictionaryFile`, stream wrappers, `DataKeyManager`, `DataKeyImporter`, and master-key backends. Public helpers are `trash_dir_all`, `clean_up_trash`, and `clean_up_dir`.

Control flow: `trash_dir_all` renames a directory to `TRASH-<name>`, asks the key manager to remove metadata using the original logical path and trash physical path, then removes the trash directory. `clean_up_trash` resumes deletions for leftover trash directories after restart. `clean_up_dir` deletes all direct child directories with a prefix and optionally removes metadata.

State and persistence behavior: State changes are delegated to `DataKeyManager::remove_dir`, so dictionary entries are removed before physical recursive delete completes. The trash prefix gives crash recovery a durable marker for deletion-in-progress.

Dependencies and integration: Used by storage cleanup paths that need directory removal while encryption is enabled. It integrates file-system operations with key manager metadata and exports test utilities for dependent crates.

Risks: Directory names are converted through `to_str().unwrap()` in cleanup paths, so non-UTF-8 names can panic. Existing trash-name collisions are left to filesystem rename behavior. Metadata removal and physical removal remain separate operations, but `clean_up_trash` is designed to repair restart leftovers.

Test signals: Root tests cover basic trash deletion, deletion with pre-existing trash path, cleanup of restart leftovers, and prefix cleanup without an encryption manager. Manager tests additionally cover encrypted trash-dir cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/manager/mod.rs -->
# sources/storage-engines/tikv/components/encryption/src/manager/mod.rs

Purpose: Implements TiKV data-key management for encrypted files. It loads and persists key/file dictionaries, rotates data keys, wraps file readers and writers, tracks metadata for create/link/rename/delete operations, and imports external data keys for restore.

Important APIs and types: `DataKeyManager::new`, `create_file_for_write`, `open_file_with_writer`, `open_file_for_read`, `get_file`, `new_file`, `delete_file`, `link_file`, `rename_file`, `remove_dir`, `dump_key_dict`, and `dump_file_dict` are the main APIs. `Dicts` owns the shared dictionaries and persistence handles. `DataKeyManagerArgs` maps config to runtime arguments. `DataKeyImporter` is an RAII importer with `add`, `commit`, and `rollback`. Internal `RotateTask` coordinates background saving and termination.

Control flow: Startup loads dictionaries with the current master key. If decryption fails with `WrongMasterKey`, it loads with the previous key and rewrites `key.dict` under the current key. If encryption is enabled for the first time, it creates empty dictionaries and immediately rotates a data key. A background thread periodically calls `maybe_rotate_data_key`; rotation also occurs when method changes, the current key exceeds the rotation period, or an exposed key can be replaced under a secure backend.

State and persistence behavior: `file.dict` is plaintext metadata persisted through `FileDictionaryFile`; `key.dict` is encrypted by the master-key backend via `EncryptedFile`. `current_key_id` is atomic so readers avoid partially updated `KeyDictionary.current_key_id`. File metadata operations update in-memory state and append/rewrite file dictionary records with sync on operation boundaries. Key dictionary writes mark keys exposed when saved with insecure master keys.

Dependencies and integration: Integrates with `EncryptionConfig`, stream wrappers from `io.rs`, `EncryptedFile`, master-key `Backend`, protobuf dictionaries, failpoints, metrics, `file_system`, and `walkdir`. RocksDB uses plaintext fallback from `get_file` when a file is not tracked.

Risks: Filesystem changes and dictionary changes are not atomic; code has explicit stale-entry cleanup for link targets and trash-directory workflows to mitigate this. Directory deletion/linking rejects symlinks. Background rotation uses `expect`, so persistent key-dictionary save errors panic the worker. Import rollback only removes imported keys within a time window to avoid deleting keys that may now be shared.

Test signals: Extensive tests cover enable/disable, insecure master rejection, master-key rotation fallback and failure, missing dictionaries, create/get/delete, link/rename, data-key rotation, persistence, exposed-key rotation, plaintext file wrappers, algorithm switches, directory rename/delete, key import rollback/commit, duplicate import races, and encrypted trash cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/manager/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/file.rs -->
# sources/storage-engines/tikv/components/encryption/src/master_key/file.rs

Purpose: Implements a secure master-key backend backed by a local key file. It reads a hex-encoded AES-256-GCM key and delegates encryption/decryption to the in-memory GCM backend.

Important APIs and types: `FileBackend::new` validates and loads the key file. `Backend` implementation provides sync `encrypt`, `decrypt`, and `is_secure`. `AsyncBackend` implementation forwards to the sync methods.

Control flow: `new` opens the file, checks its exact size as 64 hex bytes plus newline, reads it completely, verifies newline termination, decodes hex, then constructs `MemAesGcmBackend`. `encrypt` generates a fresh GCM IV and encrypts content; `decrypt` validates and authenticates through the memory backend.

State and persistence behavior: The backend keeps the decoded master key in memory. It does not persist new state; encrypted metadata stores IV, method, ciphertext, and GCM tag in `EncryptedContent`.

Dependencies and integration: Used by data-key dictionary encryption and by multi-master-key restore. It depends on `file_system::File`, crate `AesGcmCrypter`/`Iv`, and master-key metadata handled in `mem.rs`.

Risks: Strict file sizing prevents accidental large reads but rejects files without trailing newline or with extra whitespace. The decoded key remains in process memory for backend lifetime. Authentication failures surface as `WrongMasterKey`, which triggers previous-key fallback in the manager.

Test signals: Tests verify known AES-256-GCM vectors, successful encrypt/decrypt round trips, GCM tag mismatch as `WrongMasterKey`, and missing tag as metadata corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/file.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/kms.rs -->
# sources/storage-engines/tikv/components/encryption/src/master_key/kms.rs

Purpose: Implements a master-key backend that obtains and decrypts data keys through a cloud KMS provider, caches the current plaintext data key, and encrypts metadata with AES-256-GCM.

Important APIs and types: `KmsBackend::new`, `encrypt_content`, `decrypt_content`, async counterparts, and test-only `clear_state` are main APIs. Internal `State` stores `MemAesGcmBackend` plus cached KMS ciphertext key. Test module `fake` provides `FakeKms` and vector fixtures.

Control flow: Sync APIs lock a single-thread Tokio runtime and block on async work. Encryption lazily calls `KmsProvider::generate_data_key` with timeout and retry, builds a memory GCM backend, encrypts plaintext, and adds KMS vendor and ciphertext-key metadata. Decryption validates vendor, parses ciphertext key, reuses cached state if the ciphertext key matches, otherwise calls KMS `decrypt_data_key`, builds state, decrypts, and caches it.

State and persistence behavior: Cached state is held in an async mutex and avoids repeated KMS decrypts for the same encrypted data key. Durable state lives only in `EncryptedContent` metadata: method/IV/tag from GCM plus KMS vendor and ciphertext key.

Dependencies and integration: Depends on `cloud::kms`, `tikv_util::stream::{retry, with_timeout}`, Tokio runtime, thread hooks, and `MemAesGcmBackend`. It satisfies both sync `Backend` and async `AsyncBackend`, so it works for key dictionaries and multi-master-key restore.

Risks: A runtime mutex serializes sync API calls. Missing KMS vendor returns `WrongMasterKey` to allow fallback to non-KMS backends; vendor mismatch returns `Other`. KMS decrypt failures are wrapped as `WrongMasterKey`, which may hide transient/cloud detail except through the nested message. Timeout is fixed at 10 seconds.

Test signals: Tests cover state caching identity, known-vector encryption/decryption through fake KMS, missing/invalid vendor, missing ciphertext key, and wrong KMS data-key behavior after clearing cache.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/kms.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/mem.rs -->
# sources/storage-engines/tikv/components/encryption/src/master_key/mem.rs

Purpose: Provides the in-memory AES-256-GCM backend shared by file and KMS master-key backends. It encrypts/decrypts `EncryptedContent` using a plaintext master key held in memory.

Important APIs and types: `MemAesGcmBackend::new`, `encrypt_content`, and `decrypt_content`. The backend stores a `cloud::kms::PlainKey` typed as AES-GCM-256.

Control flow: Construction validates the raw key through `PlainKey::new`. Encryption writes metadata `method=aes256-gcm`, IV bytes, and GCM tag, and stores ciphertext content. Decryption checks method, IV, and tag metadata before authenticating and decrypting the content.

State and persistence behavior: The only runtime state is the plaintext key. Serialized state appears in `EncryptedContent` metadata and content fields. Authentication failures are classified as `WrongMasterKey`; malformed or unsupported metadata is `Other`.

Dependencies and integration: Used directly by `FileBackend` and internally by `KmsBackend::State`. It depends on crate `AesGcmCrypter`, `AesGcmTag`, `Iv`, master-key metadata keys, and cloud key wrappers.

Risks: The method mismatch path intentionally does not fallback as wrong master key, because unsupported future formats should fail clearly. Tag mismatch is ambiguous between corruption, attack, and wrong key, so it returns `WrongMasterKey` for manager fallback compatibility.

Test signals: Tests verify an external AES-GCM test vector, successful authentication, missing method, invalid method, missing tag, and mismatched tag classification.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/mem.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/metadata.rs -->
# sources/storage-engines/tikv/components/encryption/src/master_key/metadata.rs

Purpose: Centralizes string keys and byte markers used in `EncryptedContent.metadata` for master-key encryption formats.

Important APIs and types: `MetadataKey` variants are `Method`, `Iv`, `AesGcmTag`, `KmsVendor`, and `KmsCiphertextKey`; `as_str` maps them to stable metadata names. `MetadataMethod` variants are `Plaintext` and `Aes256Gcm`; `as_slice` maps them to stable byte values.

Control flow and state: This is a pure constant/enum mapping module with no mutable state. Other backends use it to write and validate metadata.

Dependencies and integration: Imported by plaintext, memory, file, and KMS backends. The string names are part of the persisted encrypted metadata contract, so changing them would break dictionary/key compatibility.

Risks: There is no version negotiation here; unsupported methods are handled by callers. Typos or changes in constants would make existing metadata unreadable.

Test signals: No local tests, but all master-key backend tests exercise these metadata names through successful and failing decrypt paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/metadata.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/mod.rs -->
# sources/storage-engines/tikv/components/encryption/src/master_key/mod.rs

Purpose: Defines the master-key abstraction layer and combines plaintext, file, KMS, and multi-master-key restore behavior.

Important APIs and types: `Backend` is the sync encrypt/decrypt/security trait. `AsyncBackend` is the async variant. `PlaintextBackend` stores content without encryption but validates plaintext metadata. `MultiMasterKeyBackend` asynchronously maintains an optional ordered backend list and configs, with update, encrypt, decrypt, `generate_data_key`, and `is_initialized` APIs.

Control flow: Plaintext encryption writes `method=plaintext`; decrypt refuses non-plaintext metadata as `WrongMasterKey`. `MultiMasterKeyBackend::update_from_proto_if_needed` converts protobuf master keys to configs, and `update_from_config_if_needed` rebuilds backend objects only when configs change. Encryption/decryption clones the current backend vector under a read lock, tries backends in order, returns the first success, and combines error messages if all fail.

State and persistence behavior: Plaintext backend has no state. Multi-master-key state is an async `RwLock` containing optional configs and backend vector; configs and backends are updated together. It does not persist state itself, but decrypts persisted `EncryptedContent` produced by one of the configured backends.

Dependencies and integration: Used by backup/restore and by `DataKeyManager` master-key operations. Depends on `MasterKeyConfig`, protobuf `MasterKey`, generated data-key helper, and concrete file/KMS modules.

Risks: Multi-backend errors are string-combined into `Other`, so structured error codes are lost after all attempts fail. Backend creation is synchronous inside the write lock. Plaintext backend is deliberately insecure; manager rejects enabling encryption with insecure current master key.

Test signals: Tests provide `MockBackend` for manager fallback tests and async mock backends for multi-master-key failure aggregation and first-success behavior with multiple backends.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/master_key/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/metrics.rs -->
# sources/storage-engines/tikv/components/encryption/src/metrics.rs

Purpose: Registers Prometheus metrics for encryption metadata and file I/O duration.

Important APIs and types: Lazy static metrics are `ENCRYPTION_DATA_KEY_GAUGE`, `ENCRYPTION_FILE_NUM_GAUGE`, `ENCRYPTION_INITIALIZED_GAUGE`, `ENCRYPT_DECRPTION_FILE_HISTOGRAM`, and `ENCRYPTION_FILE_SIZE_GAUGE`.

Control flow and state: Metrics are globally registered on first access. Gauges are updated by dictionary load/save, file dictionary insert/remove/rewrite, and manager initialization. The histogram is defined for read/write duration labels but this file only registers it.

Dependencies and integration: Depends on `prometheus` macros. Integration points are `file_dict_file.rs`, `manager/mod.rs`, and likely encrypted-file I/O modules outside this work item.

Risks: Metric names and label cardinality are persistent observability contracts. Two descriptions contain spelling errors, but changing names/descriptions may affect dashboards. Registration uses `unwrap`, so duplicate registration would panic if crate initialization were duplicated unexpectedly.

Test signals: No local tests; manager tests check gauge values after initialization and metadata load.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/test_utils.rs -->
# sources/storage-engines/tikv/components/encryption/src/test_utils.rs

Purpose: Provides small test helpers for creating master-key files and random master keys.

Important APIs and types: `create_master_key_file_test_only` writes a provided hex string plus newline into a temporary `master_key` file and returns its path plus `TempDir`. `generate_random_master_key` returns a hex-encoded random 32-byte key.

Control flow and state: The helper creates temporary filesystem state and relies on the returned `TempDir` to keep it alive. Random generation uses `rand::thread_rng().gen()` and `hex::encode`.

Dependencies and integration: Used by master-key and manager tests that need a `FileBackend`-compatible key file.

Risks: All errors unwrap because this is test-only support. Callers must retain the returned `TempDir`; dropping it removes the key file.

Test signals: No direct tests; heavily used in `file.rs` and `manager/mod.rs` tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/encryption/src/test_utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/Cargo.toml -->
# sources/storage-engines/tikv/components/engine_panic/Cargo.toml

Purpose: Declares the `engine_panic` crate, an example/skeleton TiKV engine implementation whose methods panic. It exists to satisfy and document the broad `engine_traits` surface for alternative engines.

Important APIs and types: Package metadata sets edition 2021, unpublished Apache-2.0 crate, and feature `testexport`. Dependencies include `engine_traits`, `encryption`, `kvproto`, `raft`, `tikv_util`, `tracker`, and `txn_types`.

Control flow and state: Cargo metadata only; no runtime behavior. The dependency list mirrors trait areas implemented by the panic modules, including raft log APIs, SST encryption hooks, perf tracking, and transaction timestamp types.

Integration points: Builds as a workspace component and provides a compile-time template for engine implementors.

Risks: Because implementations panic, accidental production use would fail immediately. The manifest keeps dependencies broad enough that trait drift is caught at compile time.

Test signals: No tests in the manifest; compile success is the main signal that the skeleton still satisfies required traits.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/cf_names.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/cf_names.rs

Purpose: Implements `CfNamesExt` for `PanicEngine`.

Important APIs and types: `PanicEngine::cf_names` returns `Vec<&str>` by trait contract but unconditionally panics.

Control flow and state: No state or persistence; every call is a sentinel failure.

Dependencies and integration: Depends on `engine_traits::CfNamesExt` and the local `PanicEngine`. It documents that real engines must expose column-family names.

Risks: Any call in tests or runtime will panic, as intended for this skeleton.

Test signals: No local tests; compile-time trait conformance is the signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/cf_names.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/cf_options.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/cf_options.rs

Purpose: Provides panic stubs for column-family option access and mutation.

Important APIs and types: `PanicEngine` implements `CfOptionsExt` with associated `PanicCfOptions`. `PanicCfOptions` implements `CfOptions`, exposing write buffer, L0 trigger, pending compaction limit, block cache, Titan options, auto-compaction, SST partitioner, and compaction-thread controls.

Control flow and state: All methods panic and store no options. The file is a trait-surface checklist for real engines.

Dependencies and integration: References `engine_traits::{CfOptions, CfOptionsExt, SstPartitionerFactory}` and `PanicTitanDbOptions`.

Risks: It compiles only as long as the skeleton tracks the trait exactly; runtime use is invalid.

Test signals: No tests; trait compilation is coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/cf_options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/checkpoint.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/checkpoint.rs

Purpose: Panic skeleton for checkpoint creation and database merge support.

Important APIs and types: `PanicEngine` implements `Checkpointable` with associated `PanicCheckpointer`. `PanicCheckpointer` implements `Checkpointer::create_at`.

Control flow and state: `new_checkpointer`, `merge`, and `create_at` panic. There is no persisted checkpoint state.

Dependencies and integration: Uses `engine_traits::{Checkpointable, Checkpointer}` and `std::path::Path`. Documents that real engines must create checkpoint directories and optionally Titan outputs.

Risks: Accidental invocation panics. The imported `core::panic` is redundant but harmless.

Test signals: No local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/checkpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/compact.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/compact.rs

Purpose: Panic stubs for compaction control and compaction-event reporting.

Important APIs and types: `PanicEngine` implements `CompactExt`; `PanicCompactedEvent` implements `CompactedEvent` with key-range, declined-byte, output-level, region decline calculation, and CF accessors.

Control flow and state: All compaction operations and event accessors panic. No compaction state exists.

Dependencies and integration: Mirrors real engine APIs for manual compaction, file compaction, range validation, and split-check event consumption.

Risks: Runtime invocation panics. Trait drift here would reveal missing methods during compile.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/compact.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/db_options.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/db_options.rs

Purpose: Panic skeleton for database-wide options and Titan DB options.

Important APIs and types: `PanicEngine` implements `DbOptionsExt` with `PanicDbOptions`. `PanicDbOptions` implements rate limiter, flush size, background jobs, WAL manifest verification, and Titan option hooks. `PanicTitanDbOptions` implements `TitanCfOptions`.

Control flow and state: Every getter/setter panics; no option state is stored.

Dependencies and integration: Tracks `engine_traits::{DbOptions, DbOptionsExt, TitanCfOptions}`.

Risks: Runtime use panics; compile success keeps the engine skeleton synchronized with option trait evolution.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/db_options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/db_vector.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/db_vector.rs

Purpose: Panic implementation of the database value vector trait.

Important APIs and types: `PanicDbVector` implements `DbVector`, `Deref<Target=[u8]>`, and `PartialEq<&[u8]>`.

Control flow and state: `deref` panics, so `PartialEq` also panics when it dereferences `self`. No buffer is stored.

Dependencies and integration: Serves as associated `DbVector` for `PanicEngine` and `PanicSnapshot` peek operations.

Risks: Any attempted value inspection panics. The equality impl is syntactically useful but not operational.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/db_vector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/engine.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/engine.rs

Purpose: Defines `PanicEngine`, the central panic-based implementation of core key-value engine traits and iterator traits.

Important APIs and types: `PanicEngine` implements `KvEngine`, `Peekable`, `SyncMutable`, and `Iterable`; `PanicEngineIterator` implements `Iterator`; `PanicEngineIterMetricsCollector` implements `IterMetricsCollector`; iterator metrics are exposed through `MetricsExt`.

Control flow and state: Snapshot creation, sync, downcast, point reads, writes, deletes, range deletes, iterator creation, seeking, movement, key/value access, and metrics all panic. There is no storage state.

Dependencies and integration: Imports broad `engine_traits` APIs and uses `PanicSnapshot`, `PanicDbVector`, and `PanicWriteBatch` as associated types in other modules.

Risks: This is a compile-time template only. It intentionally does not provide a safe no-op implementation, so accidental use fails loudly.

Test signals: No local tests; compile-time trait coverage is the intended validation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/flow_control_factors.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/flow_control_factors.rs

Purpose: Panic skeleton for engine flow-control metrics.

Important APIs and types: `PanicEngine` implements `FlowControlFactorsExt` methods for number of files at level, immutable memtable count, and pending compaction bytes.

Control flow and state: All methods panic and return no values.

Dependencies and integration: Real engines use these metrics for write-flow control decisions; this file keeps the skeleton API-complete.

Risks: Runtime calls panic.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/flow_control_factors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/import.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/import.rs

Purpose: Panic skeleton for external SST ingestion.

Important APIs and types: `PanicEngine` implements `ImportExt` with associated `PanicIngestExternalFileOptions`. Options implement `new`, `move_files`, and `allow_write`.

Control flow and state: Ingest, latch acquisition, and option mutation all panic. No latch or ingest state exists.

Dependencies and integration: References `RangeLatchGuard`, `Range`, and `IngestExternalFileOptions`, documenting the contract real engines must satisfy for import/restore paths.

Risks: Runtime use panics.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/import.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/io_limiter.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/io_limiter.rs

Purpose: Panic skeleton for engine I/O limiter support.

Important APIs and types: `PanicEngine` implements `IOLimiterExt` with associated `PanicIOLimiter`; `PanicIOLimiter` implements constructor, rate setter, request accounting, and metric getters.

Control flow and state: Every method panics. There is no limiter state.

Dependencies and integration: Tracks `engine_traits::{IOLimiter, IOLimiterExt}`.

Risks: Runtime use panics.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/io_limiter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/lib.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/lib.rs

Purpose: Crate root for the panic engine skeleton. It exports modules that mirror the full TiKV engine trait layout.

Important APIs and types: Re-exports include CF names/options, compaction, DB options, DB vectors, engine, import, misc, snapshot, SST, write batch, range/MVCC/TTL properties, perf context, flow control, table properties, and checkpoint modules. `raft_engine` is private but provides trait impls for `PanicEngine`.

Control flow and state: No runtime logic beyond module wiring. The crate has `#![allow(unused)]` because it is a template.

Dependencies and integration: Intended for new engine implementors to copy and replace `Panic*` types with real implementations. It keeps module organization aligned with other TiKV engines.

Risks: Publicly exported panic types can be instantiated and then panic on use. The skeleton should not be used as a functional engine.

Test signals: Compile-time conformance across the crate is the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/misc.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/misc.rs

Purpose: Panic skeleton for miscellaneous engine operations and statistics reporting.

Important APIs and types: `PanicReporter` implements `StatisticsReporter<PanicEngine>`. `PanicEngine` implements `MiscExt` with flush, delete ranges, memtable stats, ingest slowdown, used size, path, WAL sync, manual compaction toggles, background work pause/continue, existence/lock checks, stats dumps, sequence numbers, SST size, key count, range stats, stall status, active memtable stats, accumulated flush count, and disk-engine access.

Control flow and state: Every operation panics; no reporting state exists.

Dependencies and integration: This mirrors operational APIs consumed throughout TiKV for maintenance, metrics, and safety checks.

Risks: Runtime use panics. Since this surface is large, trait changes are likely to show up here during compilation.

Test signals: No local tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/misc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/mvcc_properties.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/mvcc_properties.rs

Purpose: Panic skeleton for MVCC table/range property access.

Important APIs and types: `PanicEngine` implements `MvccPropertiesExt::get_mvcc_properties_cf`, taking CF, safe point, and key range.

Control flow and state: The method panics and returns no properties.

Dependencies and integration: Uses `txn_types::TimeStamp` and `engine_traits::MvccProperties`. Real engines use this for split/check and GC-related range statistics.

Risks: Runtime use panics.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/mvcc_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/perf_context.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/perf_context.rs

Purpose: Panic skeleton for engine performance context collection.

Important APIs and types: `PanicEngine` implements `PerfContextExt` with associated `PanicPerfContext`. `PanicPerfContext` implements `start_observe` and `report_metrics`.

Control flow and state: All methods panic. There is no performance counter state.

Dependencies and integration: Uses `PerfLevel`, `PerfContextKind`, and `tracker::TrackerToken`. Real engines use this for RocksDB perf-context reporting.

Risks: Runtime use panics.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/perf_context.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/raft_engine.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/raft_engine.rs

Purpose: Panic skeleton for raft log engine traits using `PanicEngine` and `PanicWriteBatch`.

Important APIs and types: `PanicEngine` implements `RaftEngineReadOnly`, `RaftEngineDebug`, and `RaftEngine`. `PanicWriteBatch` implements `RaftLogBatch`. Methods cover raft state, entries, store ident, bootstrap region, region/apply state, flushed index, dirty mark, recover state, scans, batch creation/consume, log cleanup, GC, purge, metrics, size/path, raft-group iteration, and batch mutations.

Control flow and state: All methods panic. No raft log state, batches, or persistence exists.

Dependencies and integration: Depends on `kvproto` raft/server metadata, `raft::eraftpb::Entry`, and `engine_traits` raft traits. It documents the full raft-engine surface expected by TiKV.

Risks: Runtime use panics; this module is private from crate root but its trait implementations attach to exported types.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/raft_engine.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/range_properties.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/range_properties.rs

Purpose: Panic skeleton for approximate range-size/key APIs.

Important APIs and types: `PanicEngine` implements `RangePropertiesExt` for approximate keys, approximate size, and split-key calculation on default and named CFs.

Control flow and state: All methods panic and hold no property state.

Dependencies and integration: Real engines use these APIs for region split checks and scheduling decisions.

Risks: Runtime use panics.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/range_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/snapshot.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/snapshot.rs

Purpose: Panic skeleton for read snapshots and snapshot iterators.

Important APIs and types: `PanicSnapshot` implements `Snapshot`, `Peekable`, `Iterable`, `CfNamesExt`, and `SnapshotMiscExt`. `PanicSnapshotIterator` implements `Iterator`; `PanicSnapshotIterMetricsCollector` implements iterator metrics.

Control flow and state: Point reads, iterator creation, CF names, sequence number, iterator movement/access, and metrics all panic. No read view state exists.

Dependencies and integration: Associated snapshot type for `PanicEngine`; mirrors real snapshot APIs consumed by TiKV read paths.

Risks: Runtime use panics.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/sst.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/sst.rs

Purpose: Panic skeleton for SST reading, writing, builder configuration, external SST metadata, and streaming readers.

Important APIs and types: `PanicEngine` implements `SstExt` with `PanicSstReader`, `PanicSstWriter`, and `PanicSstWriterBuilder`. Reader implements checksum and kv-count APIs plus `RefIterable`; writer implements put/delete/size/finish; builder configures DB, CF, memory mode, compression, and path. `PanicExternalSstFileInfo` and `PanicExternalSstFileReader` implement external-file traits and `Read`.

Control flow and state: Every operational method panics. The iterator contains only phantom lifetime state.

Dependencies and integration: Imports `encryption::DataKeyManager`, showing real SST readers may be encryption-aware. Also tracks compression and CF-name APIs from `engine_traits`.

Risks: Runtime use panics. The broad surface is important for compile-time detection of SST trait changes.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/sst.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/table_properties.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/table_properties.rs

Purpose: Minimal panic/empty skeleton for table properties.

Important APIs and types: `UserCollectedProperties` returns `None` for property lookups, approximate size/keys, and MVCC properties. `TableProperties` panics for user-collected properties and number of entries. `TablePropertiesCollection::iter_table_properties` is a no-op. `PanicEngine` implements `TablePropertiesExt`.

Control flow and state: Collection iteration silently does nothing, while engine lookup and table accessors panic. No table-property state is stored.

Dependencies and integration: Mirrors the property APIs used for range statistics, MVCC statistics, and table inspection.

Risks: The no-op collection may hide invocation compared with other panic stubs, but `table_properties_collection` itself panics before a collection can be obtained.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/table_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/ttl_properties.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/ttl_properties.rs

Purpose: Panic skeleton for TTL range property access.

Important APIs and types: `PanicEngine` implements `TtlPropertiesExt::get_range_ttl_properties_cf`.

Control flow and state: The method panics and stores no TTL metadata.

Dependencies and integration: Real engines use this for TTL-aware range scans or compaction decisions.

Risks: Runtime use panics.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/ttl_properties.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/write_batch.rs -->
# sources/storage-engines/tikv/components/engine_panic/src/write_batch.rs

Purpose: Panic skeleton for write-batch creation, mutation, savepoints, merging, and write execution.

Important APIs and types: `PanicEngine` implements `WriteBatchExt` with associated `PanicWriteBatch` and `WRITE_BATCH_MAX_KEYS = 1`. `PanicWriteBatch` implements `WriteBatch` and `Mutable`.

Control flow and state: All methods panic, including write, size/count inspection, clear, savepoint operations, merge, put/delete, and range delete. There is no batch state.

Dependencies and integration: Used as the associated write batch for both KV and raft panic-engine traits.

Risks: Runtime use panics; `WRITE_BATCH_MAX_KEYS` is a placeholder and not a functional capacity limit.

Test signals: No tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_panic/src/write_batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/Cargo.toml -->
# sources/storage-engines/tikv/components/engine_rocks/Cargo.toml

Purpose: Declares the real RocksDB-backed TiKV engine crate. It exposes feature flags and dependencies for RocksDB integration, encryption, properties, raft, metrics, and test support.

Important APIs and types: Features include `trace-lifetime`, `jemalloc`, `portable`, `sse`, `failpoints`, `testexport`, and `nortcheck`. The RocksDB dependency is `tikv/rust-rocksdb` with the `encryption` feature. Edition is 2024.

Control flow and state: Cargo metadata only. Feature flags alter allocator/SIMD/runtime-check/failpoint behavior and dependency features.

Dependencies and integration: Pulls in `engine_traits`, `encryption`, `file_system`, `keys`, `kvproto`, `rocksdb`, `prometheus`, `raft`, `tikv_util`, `txn_types`, and many support crates. This crate is the concrete engine implementation behind most TiKV storage operations.

Risks: `nortcheck` disables Rust-side invariant checks and can break tests. Git-sourced RocksDB ties behavior to the external rust-rocksdb repository and its enabled `encryption` feature.

Test signals: Manifest dev-dependencies include `proptest`, `rand`, and `toml`; actual tests live in source modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/cf_names.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/cf_names.rs

Purpose: Implements column-family name discovery for `RocksEngine`.

Important APIs and types: `RocksEngine` implements `CfNamesExt::cf_names` by delegating to the inner RocksDB handle.

Control flow and state: Stateless delegation; returned names reflect the currently opened RocksDB column families.

Dependencies and integration: Used by compaction, maintenance, metrics, and callers that need to iterate all CFs. It depends on the local `RocksEngine::as_inner` API and RocksDB's CF-name access.

Risks: Lifetime and validity of returned `&str` values depend on the inner RocksDB wrapper contract. No filtering is applied.

Test signals: Indirectly exercised by compaction tests that iterate all CF names.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/cf_names.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/cf_options.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/cf_options.rs

Purpose: Bridges `engine_traits::CfOptions` to rust-rocksdb `ColumnFamilyOptions`.

Important APIs and types: `RocksEngine` implements `CfOptionsExt::get_options_cf` and `set_options_cf`. `RocksCfOptions` wraps `RawCfOptions`, supports `from_raw`, `into_raw`, deref/deref-mut, write-buffer-manager flush size helpers, and all `CfOptions` trait methods.

Control flow: CF option reads first resolve a CF handle with `util::get_cf_handle`, then obtain raw options from the DB. Dynamic option setting calls RocksDB `set_options_cf`. Trait methods forward to raw RocksDB getters/setters and adapt errors with `r2e` or boxed errors.

State and persistence behavior: `RocksCfOptions` is an in-memory wrapper around raw options. Some setters mutate the option object before engine open; `set_options_cf` changes live RocksDB options. Block cache capacity and compaction limiter setters mutate shared RocksDB objects.

Dependencies and integration: Used by config application, flow-control tuning, compaction setup, block cache management, Titan options, and SST partitioning. Depends on `RocksTitanDbOptions`, `RocksSstPartitionerFactory`, and RocksDB raw APIs.

Risks: `set_flush_size` and `get_flush_size` fail if no write-buffer manager is attached. `set_max_compactions` fails if no compaction-thread limiter exists. Integer casts from RocksDB values to `i32` assume values fit. Dynamic option strings are passed through to RocksDB for validation.

Test signals: No local tests in this file, but compaction tests create and mutate `RocksCfOptions`, and broader engine configuration tests likely cover option bridging.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/cf_options.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/checkpoint.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/checkpoint.rs

Purpose: Implements RocksDB checkpoint creation and instance merge for `RocksEngine`.

Important APIs and types: `RocksEngine` implements `Checkpointable` with associated `RocksEngineCheckpointer`. `RocksEngineCheckpointer` wraps `rocksdb::Checkpointer` and implements `create_at`.

Control flow: `new_checkpointer` delegates to RocksDB and maps errors. `merge` creates `MergeInstanceOptions` with `merge_memtable=false` and `allow_source_write=true`, collects raw inner DB references, and calls RocksDB `merge_instances`. `create_at` optionally deletes the output directory in test builds, then delegates to RocksDB with optional Titan output and log-size flush threshold.

State and persistence behavior: Checkpoints materialize RocksDB state at output directories. Merge mutates the target DB by merging source instances while allowing source writes.

Dependencies and integration: Used by backup/snapshot/admin flows that need consistent engine checkpoints. Integrates `file_system` cleanup in tests and RocksDB checkpoint APIs.

Risks: Creating a checkpoint while background work is paused can fail, as the test expects. Test-only deletion of output directories must remain behind cfg. Merge options intentionally do not merge memtables, so callers must understand durability/flush requirements.

Test signals: `test_checkpoint` writes a key, verifies checkpoint failure while background work is paused, resumes background work, creates a checkpoint, opens it, and reads the key.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/checkpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/compact.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/compact.rs

Purpose: Implements manual compaction operations for `RocksEngine`.

Important APIs and types: `RocksEngine` implements `CompactExt`, with `RocksCompactedEvent` as event type. Methods include `auto_compactions_is_disabled`, `compact_range_cf`, `compact_files_in_range_cf`, `compact_files_cf`, and `check_in_range`.

Control flow: Auto-compaction status iterates CFs and returns true if any CF disables auto compactions. Range compaction builds `CompactOptions` from `ManualCompactionOptions` and calls RocksDB. File-in-range compaction scans CF metadata levels below the output level, selects files overlapping the requested key range, and delegates to `compact_files_cf`. File compaction determines output level, output compression, target file size, optionally filters out L0 files, builds `CompactionOptions`, and calls RocksDB.

State and persistence behavior: Operations mutate RocksDB SST layout but not logical key-value content. Output compression and file sizing are derived from live CF options.

Dependencies and integration: Uses CF name discovery, CF-handle lookup, RocksDB metadata/options, CPU count for subcompactions, and error mapping. Called by administrative compaction and split/check maintenance.

Risks: Range overlap tests use byte comparisons against file smallest/largest keys; boundary semantics must match RocksDB metadata. `exclude_l0` filters by filename suffix, which depends on RocksDB naming conventions. Large compactions can be expensive and run concurrently depending on options.

Test signals: `test_compact_files_in_range` creates multiple L0 files per CF with auto compaction disabled, compacts selected ranges to L1 and then the last level, and asserts file distribution and key ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/compact.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/compact_listener.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/compact_listener.rs

Purpose: Converts RocksDB compaction completion callbacks into TiKV `RocksCompactedEvent` values with key ranges and per-region declined-byte estimates.

Important APIs and types: `RocksCompactionJobInfo` wraps raw RocksDB job info and implements `engine_traits::CompactionJobInfo`. `RocksCompactedEvent` implements `CompactedEvent`. `CompactedEventSender` abstracts event delivery. `CompactionListener` implements `rocksdb::EventListener`.

Control flow: On compaction completion, the listener ignores failed jobs and jobs rejected by an optional filter. It collects input/output filenames, decodes range properties from table properties, separates input and output properties, derives smallest/largest input keys, and sends a `RocksCompactedEvent`. Event methods expose key range, declined bytes, trivial-decline classification, output level label, CF, and `calc_ranges_declined_bytes`, which maps compaction range overlap to region IDs and computes old-new size deltas above a threshold.

State and persistence behavior: Listener state is an event sender plus optional filter. Events are in-memory observations; they do not persist state. Declined-byte calculations use decoded SST range properties captured from the compaction job.

Dependencies and integration: Integrates RocksDB event callbacks with TiKV range property decoding and split-check or scheduling logic that consumes compaction events. Uses `collections::hash_set_with_capacity`, `RangeProperties`, and `UserCollectedPropertiesDecoder`.

Risks: If any SST property decode fails, the entire event is dropped after a warning. If both input and output properties are empty, or key bounds are missing, no event is sent. File matching depends on string paths from RocksDB. Declined-byte estimates are approximate and threshold-filtered.

Test signals: No local unit tests in this file; behavior is indirectly exercised by compaction/event integration tests elsewhere. Compile-time trait implementation protects the wrapper surface.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/compact_listener.rs -->
