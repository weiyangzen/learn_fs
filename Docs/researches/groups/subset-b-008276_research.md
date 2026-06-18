# subset-b-008276 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/dummy_storage.rs -->
# sources/object-store/rustfs/crates/protocols/src/common/dummy_storage.rs

Purpose: This test-only module provides `DummyBackend`, a queue-driven implementation of the protocol crate's S3 `StorageBackend` trait. It is built for SFTP and FTPS driver unit tests that need deterministic S3 responses, call observation, and cancellation/timeout fixtures without a real object store.

Important APIs and types: `DummyError` models backend miss, deny, upload, injected, and unconfigured failures. `AbortCall`, `UploadPartCall`, `PutObjectCall`, `CreateMultipartCall`, `CompleteCall`, and `HeadObjectCall` are observation records. `DummyBackend` exposes queue helpers such as `queue_head_object_ok`, `queue_put_object_err`, `queue_create_multipart_upload_ok`, `queue_upload_part_ok`, `queue_upload_part_copy_ok`, `queue_complete_multipart_upload_err`, `queue_get_object_range_bytes`, and `queue_list_objects_v2_ok_empty`; observer methods snapshot the recorded call logs. Stall helpers `stall_upload_part`, `stall_put_object`, and `stall_list_objects_v2` use `tokio::sync::Notify` plus `std::future::pending` to test cancellation and deadline behavior.

Control flow: Each `StorageBackend` method pops one response from its method-specific `VecDeque`. Defaults are intentionally strict: not-found for reads and deletes, empty success for benign listings, and `Unconfigured` for operations whose use should be explicitly scripted. Methods that can stall decide and pop while holding the mutex, then release it before awaiting so a stalled future does not poison the test backend.

State and persistence behavior: All state is in-memory behind one `Mutex<Inner>` and is normally shared through `Arc<DummyBackend>`. There is no filesystem or S3 persistence. Queues are FIFO and call logs append in invocation order; stall flags and notify handles are runtime-only cancellation-test state.

Dependencies and integration points: It depends on `s3s::dto` request/response types, `bytes`, `futures_util` streams, `async_trait`, and the crate-local `StorageBackend` abstraction. The generated streaming blobs let read/write tests drive the same body-consumption paths used by production drivers. Error strings intentionally contain S3-like substrings such as `NoSuchKey`, `NoSuchBucket`, `AccessDenied`, and `NoSuchUpload` so protocol error mappers classify them realistically.

Risks: Because all queues and logs share one mutex, highly concurrent tests can observe serialized rather than backend-realistic interleavings. Some default successes, especially `put_object` and `abort_multipart_upload`, can hide missing setup if tests forget to assert call logs. Stall mode must always release the lock before awaiting; this file does that explicitly.

Test signals: Local tests verify default `head_object` reports a mappable not-found, queued `head_object` responses are returned, multipart abort calls are logged, and unconfigured multipart creation fails loudly. Downstream driver tests use the call logs, queue lengths, stall notifications, and injected typed errors as stronger behavior signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/dummy_storage.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/gateway.rs -->
# sources/object-store/rustfs/crates/protocols/src/common/gateway.rs

Purpose: This module is the authorization and capability gateway shared by protocol drivers. It translates protocol-visible S3 operations into RustFS IAM policy actions, checks whether an operation is supported for a protocol, and runs IAM authorization for a `SessionContext`.

Important APIs and types: `AuthorizationError` separates permanent `AccessDenied` from transient `IamUnavailable`. `S3Action` enumerates bucket, object, multipart, ACL, and copy operations exposed by gateways. `From<S3Action> for PolicyS3Action` and `From<S3Action> for rustfs_policy::policy::action::Action` bridge to the policy engine. `S3Action::as_str`, `is_operation_supported`, `is_authorized`, and `authorize_operation` are the main callable APIs. Under `cfg(test)`, `with_test_auth_override` and `with_test_iam_unavailable` provide per-thread authorization fixtures.

Control flow: `authorize_operation` first consults the test-only override when compiled for tests, then rejects unsupported protocol/action pairs, then calls `is_authorized`. `is_authorized` fetches the global IAM system, builds policy args from the session principal, groups, owner status, bucket, object, and claims, then awaits `iam_sys.is_allowed`. IAM acquisition failures are logged and returned as `IamUnavailable`; policy denies become `AccessDenied`.

State and persistence behavior: Production code has no local persistent state. It reads global IAM and global owner credentials. Test overrides are thread-local `RefCell`/`Cell` state with drop guards that clear decisions after an async body, preventing leaked permissions across tests.

Dependencies and integration points: It integrates `rustfs_iam`, `rustfs_policy`, `rustfs_credentials`, `serde_json`, and `SessionContext`. FTPS and SFTP drivers call `authorize_operation` before storage operations. The protocol support table is important: FTPS permits basic bucket/object listing and transfer but not multipart/copy/ACL; SFTP permits bucket/object operations plus multipart write and copy-object for rename; Swift and WebDAV are represented for cross-protocol capability checks.

Risks: The support matrix is security-sensitive; adding a new action or protocol without updating the exhaustive matches can cause build failures or unintended denial. `HeadObject` maps to `GetObject`, and multipart create/upload/complete map to `PutObject`, which is deliberate but must stay aligned with IAM policy expectations. Test override code must remain behind `cfg(test)` so production cannot bypass IAM.

Test signals: Tests verify allow/deny overrides, cleanup after the override body, closure visibility of action/bucket/object, fallback to IAM-unavailable when no override is installed, and precedence of the IAM-unavailable injection over allow overrides.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/gateway.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/mod.rs -->
# sources/object-store/rustfs/crates/protocols/src/common/mod.rs

Purpose: This is the common module facade for protocol-independent pieces: storage client traits, authorization gateway, session identity, and the test-only dummy backend.

Important APIs and types: It declares `client`, `gateway`, and `session`, plus `dummy_storage` under `cfg(test)`. It re-exports `S3StorageBackend`, `AuthorizationError`, `S3Action`, `authorize_operation`, `is_operation_supported`, `ProtocolPrincipal`, and `SessionContext`.

Control flow: There is no runtime control flow beyond Rust module resolution and re-export selection. Test builds include `dummy_storage`; non-test builds exclude it.

State and persistence behavior: This file owns no state. It controls visibility of shared APIs and keeps the production module graph free of the dummy backend.

Dependencies and integration points: `lib.rs`, FTPS, SFTP, Swift, and WebDAV consumers use this facade to avoid depending on deeper module paths. The `S3StorageBackend` alias is especially important for protocol drivers that are generic over the object-store backend.

Risks: Re-export changes are public API changes for the protocols crate. Accidentally exposing test-only helpers outside `cfg(test)` would increase production surface area.

Test signals: The main signal is compilation of downstream modules and tests that import from `crate::common`. There are no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/session.rs -->
# sources/object-store/rustfs/crates/protocols/src/common/session.rs

Purpose: This module defines the authenticated session identity passed through protocol drivers and authorization checks.

Important APIs and types: `Protocol` enumerates `Ftps`, `Swift`, `WebDav`, and `Sftp`. `ProtocolPrincipal` wraps an `Arc<UserIdentity>` and exposes `access_key`. `SessionContext` stores the principal, protocol, and source IP, with constructors and access-key helper. `test_session` builds a minimal test context under `cfg(test)`.

Control flow: Construction is straightforward data wrapping. Consumers build a `SessionContext` after authentication and pass it to gateway authorization. The test helper supplies localhost and default credentials, relying on test authorization overrides rather than real IAM.

State and persistence behavior: There is no persistence. `Arc<UserIdentity>` shares immutable identity data across protocol components for one session. `source_ip` is retained but this file does not enforce IP policy.

Dependencies and integration points: It depends on `rustfs_policy::auth::UserIdentity` and standard IP types. FTPS user-detail construction populates `Protocol::Ftps`; SFTP server/session setup uses `Protocol::Sftp`; gateway support checks branch on `Protocol`.

Risks: Adding a new protocol requires updating exhaustive matches in this module's regression test and in gateway capability checks. `access_key` delegates directly into `UserIdentity.credentials`, so callers must ensure the identity was validated by IAM before use.

Test signals: Compile-time-style regression tests match every `Protocol` variant with no wildcard and assert that `test_session` preserves the supplied protocol.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/common/session.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/constants.rs -->
# sources/object-store/rustfs/crates/protocols/src/constants.rs

Purpose: This module centralizes small cross-protocol constants for path semantics, network defaults, authentication suffixes, feature-gated protocol defaults, and default bind addresses.

Important APIs and types: `paths` defines root/current/parent/separator strings plus POSIX directory/file type bits and permission triples. `network` defines default bind/source addresses, auth suffixes, and auth failure delay. Feature-gated `ftps`, `webdav`, and `defaults` modules define passive-port parsing constants, WebDAV body/timeout limits, and default FTPS/WebDAV/SFTP listener addresses.

Control flow: There is no executable control flow. Constants are selected at compile time with feature flags such as `ftps`, `webdav`, and `sftp`.

State and persistence behavior: No state or persistence. Values are compile-time constants used by config validation and protocol attribute generation.

Dependencies and integration points: FTPS config uses the passive port separator/count and default address/range. SFTP constants derive POSIX modes from `paths`. Servers use network defaults for source IPs and listener defaults. WebDAV code can use the feature-gated body and request timeout limits.

Risks: Constants encode public behavior and defaults; changing default bind addresses, file modes, or permission triples can affect clients and security posture. Feature gating means missing features remove modules from the public API, so imports must stay gated consistently.

Test signals: Indirect tests in SFTP attributes assert POSIX mode composition. FTPS config tests or startup paths exercise passive port parsing defaults. No direct tests live in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/ftps/config.rs -->
# sources/object-store/rustfs/crates/protocols/src/ftps/config.rs

Purpose: This file defines FTPS startup configuration and initialization errors, including listener binding, passive ports, external passive address, TLS requirement, certificate directory, and optional CA file.

Important APIs and types: `FtpsInitError` wraps bind I/O errors, `libunftp::ServerError`, and human-readable invalid config messages. `FtpsConfig` stores `bind_addr`, `passive_ports`, `external_ip`, `ftps_required`, `tls_enabled`, `cert_dir`, and `ca_file`. `validate` and `parse_passive_ports` are the key methods; `Default` supplies `0.0.0.0:8021`, `40000-50000`, TLS enabled, and no certificate directory.

Control flow: `validate` rejects required FTPS without a certificate directory, checks certificate and CA paths with `tokio::fs::try_exists`, and validates passive-port syntax when configured. `parse_passive_ports` splits `start-end`, parses both as `u16`, and rejects reversed ranges.

State and persistence behavior: This file does not persist anything. It only reads filesystem metadata for certificate-related paths during validation.

Dependencies and integration points: `FtpsServer::new` calls `validate` before building the libunftp server. `FtpsServer::start` later consumes the passive range and certificate fields. Defaults come from crate constants.

Risks: `try_exists(...).unwrap_or(false)` intentionally treats lookup errors as missing, which simplifies startup errors but can hide permission-vs-absence distinctions. When `tls_enabled` is true but `ftps_required` is false and no cert dir is set, validation allows plain FTP fallback through server logic; operators must set both fields correctly for mandatory TLS.

Test signals: No local tests are present. Useful tests would cover missing cert dir when required, missing CA file, malformed passive ranges, start greater than end, and default parse success.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/ftps/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/ftps/driver.rs -->
# sources/object-store/rustfs/crates/protocols/src/ftps/driver.rs

Purpose: This module adapts libunftp's storage interface to the S3-compatible `StorageBackend`, presenting buckets and objects as an FTP filesystem.

Important APIs and types: `FtpsMetadata` implements unftp `Metadata` with size, optional modified time, directory flag, uid/gid zero, and no symlink support. `FtpsDriver<S>` wraps a generic S3 backend. Helper methods include `new`, `list_buckets`, `parse_s3_path`, and `delete_bucket_recursively`. The `StorageBackend<FtpsUser>` implementation supplies `metadata`, `list`, `get`, `put`, `del`, `mkd`, `rmd`, `cwd`, and `rename`.

Control flow: Paths are cleaned and split into bucket/object with `rustfs_utils::path`. Root listing calls `ListBuckets`; bucket paths call `HeadBucket`; object paths call `HeadObject`, `GetObject`, `PutObject`, or `DeleteObject`. Directory listing uses `ListObjectsV2` with delimiter `/`, converts `contents` into files, and `common_prefixes` into directories. `get` fully drains the S3 body into a `Vec<u8>` and returns a cursor. `put` rejects append (`start_pos > 0`), copies the whole reader into memory, and performs one `PutObject`. Bucket removal pages through all objects, deletes them one by one, then deletes the bucket. `rename` is explicitly unsupported.

State and persistence behavior: The driver is stateless aside from the backend handle. Persistent effects are S3 bucket creation/deletion, object uploads/deletes, and recursive object deletion during bucket removal. It does not store local handles or cache metadata. PUT and GET buffer whole object bodies in memory.

Dependencies and integration points: It integrates unftp storage traits, `s3s::dto` builders, `authorize_operation`, `S3Action`, `FtpsUser.session_context`, `MaskedAccessKey` logging, and RustFS path helpers. It relies on the session's IAM-derived access and secret keys for every backend call.

Risks: `mkd` creates buckets without an explicit `authorize_operation` call in this file, unlike most other mutating operations. Whole-object buffering in `get` and `put` can be unsafe for large files. Recursive bucket deletion ignores individual object delete errors and can leave partial cleanup before bucket delete. `del` only treats a path ending in `/` as bucket deletion, while `rmd` always treats the parsed bucket as the target. S3 pseudo-directories below a bucket are not first-class for FTPS creation/removal.

Test signals: There are no local tests in this file. Expected signals are authorization denial mapping to unftp errors, root and bucket listings, metadata conversion from S3 timestamps/content lengths, append rejection, put size return, recursive deletion pagination, idempotent no-such-bucket handling, and rename returning `CommandNotImplemented`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/ftps/driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/ftps/mod.rs -->
# sources/object-store/rustfs/crates/protocols/src/ftps/mod.rs

Purpose: This is the FTPS module declaration file.

Important APIs and types: It exposes `config`, `driver`, and `server` submodules. Public crate-level re-exports are handled in `lib.rs`, not here.

Control flow: There is no runtime control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: The module enables feature-gated `crate::ftps::*` imports when the `ftps` feature is compiled. `server` depends on both `config` and `driver`; consumers typically reach `FtpsConfig` and `FtpsServer` through `lib.rs`.

Risks: Removing or renaming a module here breaks feature builds and crate re-exports. There is no logic-specific risk.

Test signals: Compilation of the FTPS feature is the relevant signal.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/ftps/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/ftps/server.rs -->
# sources/object-store/rustfs/crates/protocols/src/ftps/server.rs

Purpose: This module builds and runs the FTPS server around libunftp, including TLS setup, passive/active mode configuration, IAM-backed authentication, and user-detail construction for storage operations.

Important APIs and types: `FtpsUser` implements `UserDetail` and carries username, display name, and `SessionContext`. `FtpsServer<S>` owns `FtpsConfig` and a generic S3 storage backend. `FtpsUserDetailProvider` builds `FtpsUser` from IAM identity lookup. `FtpsAuthenticator` verifies access key and secret key against IAM. `FtpsServer::new`, `start`, `config`, and `storage` are the main server APIs.

Control flow: `new` validates configuration. `start` logs startup, creates a TLS reload shutdown channel, builds a `libunftp::ServerBuilder` with `FtpsDriver` factories and IAM auth, configures passive ports, optional external passive host, active/passive mode, optional TLS certificate resolver and reload loop, optional mandatory FTPS, then spawns `server.listen`. A `tokio::select!` waits for server completion/failure or broadcast shutdown, and asks the reload loop to stop either way. Authentication fetches IAM, constructs RustFS credentials from FTP username/password, checks key validity, verifies identity presence, compares stored secret key, and returns a libunftp principal.

State and persistence behavior: Runtime state includes the server task, TLS reload task, and cloned storage backend. It reads certificate material from `cert_dir` through the reloadable resolver but does not write files. IAM user identity is read during auth and user-detail phases. Session contexts use `0.0.0.0` as source IP here.

Dependencies and integration points: It depends on libunftp, unftp_core auth/detail traits, rustls with aws-lc provider, RustFS TLS reload utilities, RustFS config env keys, IAM, credential types, `MaskedAccessKey`, and shared `SessionContext`. `FtpsDriver` receives the storage clone per session.

Risks: The code stores the spawned reload task in `_reload_task` but relies on the shutdown channel rather than joining it. The comment says dropping `server_handle` closes the listener on shutdown, but in the current branch the handle is not explicitly aborted after shutdown wins the select, so graceful cancellation behavior depends on Tokio and libunftp task lifetime details. Source IP is not taken from the client connection. Secret-key comparison is direct string equality. CA file is validated in config but this server path uses `with_no_client_auth`, so client-certificate verification is not actually wired here.

Test signals: No local tests exist. Useful signals include startup validation errors, passive range application, TLS-required behavior with and without certs, reload shutdown, authentication rejection for bad key or secret, masked logging, and user-detail failure when IAM is unavailable or identity is missing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/ftps/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/lib.rs -->
# sources/object-store/rustfs/crates/protocols/src/lib.rs

Purpose: This is the protocols crate root. It denies unsafe code, declares shared and feature-gated protocol modules, and defines the crate's public re-export surface.

Important APIs and types: Always-present modules are `common` and `constants`. Feature-gated modules are `ftps`, `swift`, `webdav`, and `sftp`. Re-exports include `Protocol`, `AuthorizationError`, `ProtocolPrincipal`, `S3Action`, `SessionContext`, `authorize_operation`, plus `FtpsConfig`/`FtpsServer`, `SwiftService`, `WebDavConfig`/`WebDavServer`, and `SftpConfig`/`SftpInitError`/`SftpServer` when their features are enabled.

Control flow: There is no runtime control flow. Compile-time feature flags determine which protocol modules and re-exports are included.

State and persistence behavior: No state or persistence.

Dependencies and integration points: This file is the external API boundary for the protocols crate. Downstream crates can import protocol servers and config types from here instead of navigating internal module paths.

Risks: Re-export changes are semver-relevant for consumers. Feature-gate mismatches between modules and re-exports can break builds. `#![deny(unsafe_code)]` means new unsafe dependencies or blocks in this crate require architectural review rather than local allowance.

Test signals: Full feature-matrix compilation is the main signal. There are no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/attrs.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/attrs.rs

Purpose: This module converts S3 bucket/object metadata into SFTPv3 `FileAttributes`, preserves selected SFTP attributes as S3 user metadata on writes, generates safe longname strings, and implements the shared `STAT`/`LSTAT`/`FSTAT` stat dispatcher for `SftpDriver`.

Important APIs and types: `s3_attrs_to_sftp` builds directory or regular-file attributes with POSIX type bits. `sftp_attrs_to_user_metadata` maps present `mtime`, `permissions`, `uid`, and `gid` into user metadata keys. `apply_user_metadata_to_sftp_attrs` overlays those keys on stat results. `timestamp_to_mtime` clamps S3 timestamps into SFTPv3 `u32` seconds. `generate_longname` sanitizes filenames and delegates formatting to `russh_sftp::protocol::File::new`. `SftpDriver::do_stat` is the async stat implementation.

Control flow: `do_stat` parses the raw path into bucket/key. Root returns default directory attributes without storage calls. Bucket paths authorize `HeadBucket`, call `head_bucket`, and return default directory attrs. Object paths authorize `HeadObject`, call `head_object`, and return file attrs using non-negative content length, clamped mtime, and optional user metadata overrides. If `head_object` reports not-found, it authorizes `ListBucket`, lists `key/` with delimiter and `max_keys=1`, and returns directory attrs if any contents or prefixes exist; otherwise it returns `NoSuchFile`.

State and persistence behavior: Attribute conversion is pure. Persistent state enters only through S3 object metadata read from `HeadObject` and metadata written elsewhere using `sftp_attrs_to_user_metadata`. There is no local cache.

Dependencies and integration points: It depends on SFTP constants, path parsing/sanitizing, SFTP error mapping, `SftpDriver` backend runners, `russh_sftp` protocol types, and `s3s::dto::ListObjectsV2Input`. SFTP handlers for stat-like operations call this shared body.

Risks: S3 user metadata values are parsed as `u32` and invalid values are silently ignored. Directory detection adds a backend listing after object miss, which is correct for pseudo-directories but can add latency. Authorization for the fallback list uses `prefix` as object context; policy semantics must agree with that. Longname safety depends on `sanitise_control_bytes` handling all control bytes clients might interpret.

Test signals: Tests cover POSIX type bits and permission triples, metadata mapping and overrides, directory/file longname prefixes, LF sanitization, timestamp clamping for pre-epoch and overflow values, and mode constant values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/attrs.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/config.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/config.rs

Purpose: This module defines SFTP listener configuration, validation, operational env override resolution, host-key loading, and initialization errors.

Important APIs and types: `SftpInitError` covers missing/unreadable host-key directories, insecure Unix key permissions, no valid keys, invalid config, russh server errors, and unsupported platforms. `SftpConfig` includes bind address, host-key directory, idle timeout, multipart part size, handle limits, backend operation timeout, read-cache window/total memory, read-only mode, and SSH banner. Methods include `validate`, `resolve_handles_per_session`, `resolve_backend_op_timeout_secs`, `resolve_read_cache_window_bytes`, `resolve_read_cache_total_mem_bytes`, and `load_host_keys`.

Control flow: `validate` enforces `SSH-2.0-` banner prefix, positive idle timeout, S3 multipart min/max part size, and target `usize` compatibility. The resolve helpers accept `None`, return in-range overrides, and log warnings while falling back for out-of-range values; read-cache window specially accepts `0` as disabled. `load_host_keys` scans the configured directory, skips non-files, empty files, and huge files, checks Unix mode bits, reads candidate PEM strings, decodes unencrypted private keys, logs decode failures differently for key-looking vs non-key files, errors if no keys load, and sorts keys by algorithm preference then public key bytes.

State and persistence behavior: The module reads host-key files and directory metadata but writes nothing. Loaded private keys are returned in memory; comments note the private key type zeroizes on drop, while intermediate PEM strings are ordinary `String`s. Configuration values are runtime data, usually derived from environment by caller code.

Dependencies and integration points: It uses SFTP limits constants, `russh::keys`, Tokio filesystem APIs, Unix permission extensions when available, and tracing. The SFTP server startup path validates config and loads host keys before accepting clients. The operational values feed driver resource limits, timeouts, read cache behavior, and multipart flushing.

Risks: Passphrase-protected host keys are skipped rather than prompting, so an all-encrypted directory fails startup. On Windows, ACL security is trusted rather than verified in code. `HostKeyDirNotSet` exists for callers that require env presence, but this file does not read env directly. The PEM string is not zeroized. Sorting by algorithm changes offered key order, so tests pin the intended preference.

Test signals: Tests cover typical validation, bad banner, zero timeout, part-size bounds, error display, missing and empty directories, Windows key loading, Unix insecure permissions, valid Ed25519 loading, non-key/empty/passphrase-like skips, Ed25519-before-ECDSA ordering, and all resolver boundary cases for handles, backend timeout, read-cache window, disabled cache sentinel, and total memory.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/constants.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/constants.rs

Purpose: This file groups the SFTP implementation's named constants: backend error substrings, POSIX modes, protocol identifiers, S3 API limits, SSH transport tuning, watchdog timing, read-directory caps, backend deadlines, write retry settings, and read-cache memory bounds.

Important APIs and types: `s3_error_codes` names S3-code fragments such as `NoSuchKey`, `NoSuchBucket`, `AccessDenied`, and `NoSuchUpload`. `http_error_codes` names numeric fragments. `posix` provides `POSIX_DIR_MODE`, `POSIX_FILE_MODE`, and test-only `POSIX_TYPE_MASK`. `protocol` defines SFTP version 3 and subsystem name `sftp`. `limits` defines constants such as `MAX_READ_LEN`, handle bounds, keepalive values, handshake and wedge watchdog timers, SSH channel/event buffer sizes, S3 multipart/copy limits, shutdown drain timeout, root listing and READDIR page caps, backend operation timeout bounds, commit-write retries/backoff, and read-cache window/total-memory bounds.

Control flow: There is no executable control flow. Constants are imported by SFTP config, server, driver, directory, errors, and attribute code to keep numeric policy in one place.

State and persistence behavior: No state or persistence. Constants determine runtime resource ceilings and wire-visible behavior.

Dependencies and integration points: `posix` composes modes from crate-wide path constants. `SftpConfig` uses handle, timeout, part-size, and cache bounds. Directory listing uses `ROOT_LISTING_MAX_ENTRIES` and `READDIR_PAGE_MAX_KEYS`. Error mapping uses the S3/HTTP fragments. Server code uses SSH buffer, keepalive, handshake, shutdown, and watchdog constants.

Risks: Many constants are protocol or AWS contract values and should not drift without compatibility review. Operational bounds affect memory pressure: the upper handle count combined with part-size can imply very high worst-case session memory. Error classification by substring is pragmatic but can misclassify unusual backend error text. SFTP protocol version is fixed at 3, so later draft semantics require separate implementation work.

Test signals: Indirect tests assert POSIX mode values, config resolver bounds, read-cache sentinels, and driver behavior around errors/timeouts/listing. No direct tests live in this constants file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/dir.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/dir.rs

Purpose: This module implements SFTP directory operations over S3: dot entries, paged listings, emptiness checks, bucket and subdirectory creation/removal, OPENDIR cursor setup, and READDIR cursor advancement.

Important APIs and types: `dot_entries` creates `.` and `..` directory `File` entries. `SftpDriver` methods include `next_listing_page`, `validate_directory_empty`, `fetch_bucket_list`, `mkdir_bucket`, `mkdir_subdir_marker`, `rmdir_bucket`, `rmdir_subdir_marker`, `readdir_cursor`, `opendir_inner`, and `readdir_inner`. It uses `DirCursor`, `ListingContinuation`, and `HandleState` from SFTP state.

Control flow: `opendir_inner` parses the path. Root opens a root cursor without backend calls. Non-root paths authorize `ListBucket`, check `HeadBucket`, normalize object prefixes with a trailing slash, and allocate a directory handle. `readdir_inner` temporarily removes the handle, inserts a pre-advance cursor copy before awaiting, calls `readdir_cursor`, reinserts updated state after success, and converts empty output to SFTP `Eof`. `readdir_cursor` emits dot entries once, then either fetches all buckets once for root or calls `next_listing_page` for object listings. `next_listing_page` reauthorizes each page, builds `ListObjectsV2` with delimiter and continuation token, converts `common_prefixes` to directory entries and `contents` to file entries, skips `__XLDIR__` markers, and advances continuation to `Next` or `Done`. `validate_directory_empty` lists at most one or two entries and rejects removal if any real child content or common prefixes exist.

State and persistence behavior: Directory iteration state is held in per-session handles. Persistent effects occur through S3 `CreateBucket`, zero-byte directory marker `PutObject`, `DeleteBucket`, and marker `DeleteObject`. Subdirectories are represented with RustFS's encoded `__XLDIR__` marker convention. Root bucket listing is not paginated by S3, so the module truncates converted entries at a fixed cap.

Dependencies and integration points: It depends on attribute conversion, path helpers, SFTP error mapping, S3 DTO builders, RustFS path marker encoding, storage backend runners, authorization, and russh_sftp protocol types. Handler trait wrappers delegate their OPENDIR, READDIR, MKDIR, and RMDIR bodies here.

Risks: The pre-advance cursor tombstone is subtle but critical for cancellation safety; changing insertion order can lose or skip entries on cancelled READDIR. Emptiness checks must propagate list failures to avoid destructive fall-through. Root `ListBuckets` can still allocate the backend's whole bucket vector before truncation. Subdirectory emptiness relies on filtering the decoded marker key equal to the prefix.

Test signals: Tests verify list errors block directory deletion, empty listings pass, cancelled READDIR leaves the cursor unadvanced for reissue, EOF after exhaustion emits no error-level event, and real backend failures do emit an error-level READDIR log.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/dir.rs -->
