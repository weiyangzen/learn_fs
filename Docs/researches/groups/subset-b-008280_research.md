# subset-b-008280 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/router.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/router.rs

## Purpose
Implements the Swift URL parser used to classify incoming HTTP requests into account, container, or object operations. It accepts canonical `/v1/AUTH_account/...` paths and an optional configured URL prefix such as `/swift/v1/...`.

## Important APIs, types, and functions
`SwiftRoute` carries the parsed account/container/object names plus the HTTP `Method`. `SwiftRoute::account()` and `project_id()` expose account identity and strip the `AUTH_` prefix using `ACCOUNT_PATTERN`. `SwiftRouter::new()` stores enablement and prefix configuration. `SwiftRouter::route()` is the main entry point. `decode_url_segment()` percent-decodes path components, and `is_valid_account()` enforces `AUTH_[a-zA-Z0-9_-]+`.

## Control flow
Routing exits early when disabled, strips the optional prefix with `strip_prefix`, splits on `/` while preserving empty object segments, verifies the first segment is `v1`, then matches exact segment shapes. Account and container trailing slash forms are normalized to account/container routes. Object routes join all remaining decoded segments, preserving consecutive slash semantics in object keys.

## State and persistence
The router is stateless except for its `enabled` flag and optional prefix. It performs no storage access.

## Dependencies and integration
Depends on `axum::http::{Method, Uri}`, `regex`, `LazyLock`, and `percent_encoding`. It integrates with the Swift request handler as the front-door path classifier.

## Risks
The prefix stripping requires `/{prefix}/`, so `/swift` without a slash will not match. Container names are only checked for non-empty segment shape here; deeper Swift naming constraints must live elsewhere. Percent decoding uses lossy UTF-8, which favors routing tolerance over strict rejection.

## Test signals
Unit tests cover valid/invalid account patterns, account/container/object routing, prefixed routing, disabled router behavior, and project id extraction.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/slo.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/slo.rs

## Purpose
Provides Swift Static Large Object support: JSON manifests describe segment objects, the module validates those segments, stores a manifest side object, creates a marker object, streams assembled downloads, returns manifests, and deletes manifests plus segments.

## Important APIs, types, and functions
`SLOSegment` models a segment path, size, etag, and optional range. `SLOManifest` owns ordered segments and optional creation time, with `from_json`, `total_size`, `calculate_etag`, and async `validate`. Handlers include `handle_slo_put`, `handle_slo_get`, `handle_slo_get_manifest`, and `handle_slo_delete`. Helpers parse segment paths, detect SLO marker metadata, parse Range headers, calculate segment slices, generate transaction ids, and build a chained segment stream.

## Control flow
PUT requires credentials, reads the full body, parses JSON, enforces a 2 MiB manifest limit after collection, validates each segment with `object::head_object`, stores `<object>.slo-manifest` with SLO metadata, then writes a zero-byte marker at the requested object path. GET loads the manifest side object, optionally parses a single Range header, computes segment ranges, builds an async stream that fetches each needed segment in order, and returns 200 or 206 with Swift SLO headers. Manifest GET returns raw JSON. DELETE loads the manifest, best-effort deletes every segment, then deletes manifest and marker.

## State and persistence
SLO state is persisted as two ordinary objects: a JSON manifest object named with `.slo-manifest` and a zero-byte marker object carrying `x-swift-slo`, `x-slo-etag`, and `x-slo-size` metadata. Segment data stays in normal Swift/S3 object storage.

## Dependencies and integration
Integrates with `super::object` for HEAD/GET/PUT/DELETE, `Credentials`, `s3s::Body`, `http_body_util`, `tokio_util::io::ReaderStream`, `futures`, `md5`, `uuid`, and `rustfs_ecstore::store_api::HTTPRangeSpec`. The Swift handler dispatches multipart-manifest query operations and SLO reads/deletes into this module.

## Risks
The manifest body is collected before the 2 MiB check, so oversized bodies still allocate first. The optional `SLOSegment.range` field is parsed but not enforced during validation or streaming. `parse_range_header` does not handle multi-range requests and can underflow if `total_size` is zero. DELETE ignores segment deletion errors, which improves idempotence but may leave orphan segments. The manifest key convention can collide with real object names ending in `.slo-manifest`.

## Test signals
Unit tests cover segment path parsing, manifest size/etag math, range parsing, segment-range calculations, JSON parsing, quote stripping, and edge cases. Storage-integrated PUT/GET/DELETE behavior is not directly exercised here.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/slo.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/staticweb.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/staticweb.rs

## Purpose
Implements Swift container static website behavior: container metadata configures index documents, error documents, optional directory listings, and listing CSS.

## Important APIs, types, and functions
`StaticWebConfig` holds `index`, `error`, `listings`, and `listings_css`, with small accessor methods. `load_config()` reads container metadata and maps `web-index`, `web-error`, `web-listings`, and `web-listings-css`. `is_enabled()` checks whether an index document is configured. Pure helpers include `detect_content_type`, `normalize_path`, `is_directory_path`, `resolve_path`, breadcrumb generation, and `generate_directory_listing`. `handle_static_web_get()` is the request handler.

## Control flow
The handler loads config, rejects disabled containers, resolves the incoming path, and either generates a listing or attempts to serve an object. Listing mode uses `container::list_objects` with an optional prefix and returns generated HTML. Object mode streams `object::get_object` through `ReaderStream`; a not-found object triggers the configured error document if present, otherwise a plain 404 response.

## State and persistence
Configuration is persisted in container metadata. Served content, index documents, CSS, and error documents are normal objects. The module does not mutate state.

## Dependencies and integration
Depends on Swift `container` and `object` modules, `Credentials`, `s3s::Body`, `axum::http::Response`, and tracing. The Swift handler calls `staticweb::is_enabled` and `handle_static_web_get` before ordinary object GET behavior.

## Risks
Generated HTML directly interpolates object names, paths, and CSS hrefs without HTML escaping, so object names containing markup could create listing XSS. Directory-without-trailing-slash redirect behavior is documented but not implemented in this file. `is_enabled()` requires an index even if listings alone are configured, making listings-only hosting unreachable through the public check. Listing links are root-relative and may not preserve Swift account/container prefixes.

## Test signals
Tests cover config accessors, MIME detection, path normalization, directory detection, path resolution, breadcrumbs, listing structure, size formatting, parent links, priority of index over listings, and case-insensitive extensions. Storage-backed handler paths are not covered.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/staticweb.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/symlink.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/symlink.rs

## Purpose
Provides metadata-level Swift object symlink support. It parses symlink target headers, identifies symlink metadata, formats target headers, and supplies depth/cycle validation helpers used by the main Swift object handlers.

## Important APIs, types, and functions
`SymlinkPath` is a hashable account/container/object tuple for visited-set loop detection. `SymlinkTarget` models a same-container or cross-container target and implements `parse`, `to_header_value`, and `resolve_container`. `extract_symlink_target()` reads `x-object-symlink-target` from request headers. `is_symlink()` and `get_symlink_target()` inspect object metadata. `validate_symlink_depth`, `check_circular_reference`, and `validate_symlink_access` enforce a maximum depth of five and reject repeated paths.

## Control flow
Creation-time code calls `extract_symlink_target`; if present, the target is normalized into metadata. Read/head flows in the Swift handler call `get_symlink_target`, add current path to a visited set, resolve the target container, and recursively continue until a non-symlink object or validation error is reached.

## State and persistence
Symlinks are persisted only as user metadata under `x-object-symlink-target`. This module itself performs no I/O and owns no persistent state.

## Dependencies and integration
Uses `http::HeaderMap`, `HashSet`, tracing, and Swift error/result types. `object.rs` records symlink metadata during PUT, while `handler.rs` resolves chains and adds response `x-symlink-target` headers.

## Risks
The parser splits on the first slash, so a same-container object name containing `/` is interpreted as `container/object`. That matches the documented format but can surprise users expecting relative object paths. Header value formatting always returns a container-qualified form, even for same-container targets. Validation prevents cycles only when callers maintain and pass the visited set correctly.

## Test signals
Tests cover target parsing, invalid empty forms, formatting, container resolution, header extraction, metadata detection, depth checks, path equality, circular reference detection, and combined validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/symlink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/sync.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/sync.rs

## Purpose
Defines configuration and helper logic for Swift container synchronization. The file models sync metadata, sync status, retry queue entries, conflict-resolution rules, target URL parsing, and HMAC signatures, but does not implement a background replication worker.

## Important APIs, types, and functions
`SyncConfig::from_metadata`, `to_metadata`, and `validate` manage `x-container-sync-to` and `x-container-sync-key`. `SyncStatus` records last success, synced count, failures, last error, and queue size. `SyncQueueEntry` tracks object, etag, last modified, retry count, and next retry, with exponential backoff helpers. `ConflictResolution` and `resolve_conflict()` encode local/remote precedence. `extract_target_container()` parses target URLs. `generate_sync_signature()` and `verify_sync_signature()` use HMAC-SHA1 over the request path.

## Control flow
Metadata parsing returns `Ok(None)` when no sync target exists, errors when a target lacks a key, and constructs an enabled config otherwise. Retry scheduling increments the retry count and caps backoff at one hour. Conflict resolution returns whether the local object should win. Signature verification regenerates and compares hex signatures.

## State and persistence
The file only defines in-memory structs. Persistent sync configuration is represented as container metadata headers. Queue and status persistence are not implemented here.

## Dependencies and integration
Depends on Swift errors, `HashMap`, tracing, `hmac`, `sha1`, and `hex`. It is intended to integrate with container metadata and a future sync worker.

## Risks
The documentation describes bidirectional background sync, retries, and timestamp convergence, but this file only supplies helper primitives. HMAC comparison is ordinary string equality, not constant-time. URL validation checks only `http://` or `https://` prefix and path shape. Short sync keys only warn. Retry backoff uses `1 << (retry_count - 1)` and remains safe under the max-retry policy, but callers should avoid scheduling unbounded retries.

## Test signals
Unit tests cover metadata parsing, validation, status counters, retry backoff/readiness/max retries, conflict strategies, target container extraction, signature generation, and verification.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/sync.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/tempurl.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/tempurl.rs

## Purpose
Implements OpenStack Swift TempURL signing and validation. TempURLs allow unauthenticated, time-limited object access using account-level HMAC-SHA1 keys.

## Important APIs, types, and functions
`TempURLParams` stores `temp_url_sig`, `temp_url_expires`, and optional `temp_url_ip_range`; `from_query()` parses them from a raw query string. `TempURL` holds the signing key and implements `generate_signature()` and `validate_request()`. `constant_time_compare()` compares signatures byte by byte. `generate_tempurl()` creates a signed URL for a path and TTL.

## Control flow
Validation checks current UNIX time against expiration, regenerates the expected signature from uppercased method, expiration, and path, compares signatures, and returns unauthorized errors for expired or invalid requests. Generation computes `now + ttl_seconds`, signs the path, and appends query parameters.

## State and persistence
No local state is persisted. The key is passed into `TempURL`; in the broader Swift stack it comes from account metadata. Generated URLs embed expiration and signature in query parameters.

## Dependencies and integration
Uses Swift errors, `hmac`, `sha1`, `hex`, and `SystemTime`. The Swift handler parses TempURL query parameters, loads the account TempURL key, validates the request, and then dispatches object operations without normal credentials.

## Risks
`from_query()` splits on every `=`, does not percent-decode values, and rejects parameters containing encoded or literal `=` characters. IP range restriction is parsed but not enforced. The length mismatch path in `constant_time_compare` returns immediately, so it is not fully constant-time for different-length strings. Only SHA1 TempURL signatures are supported.

## Test signals
Tests cover deterministic signatures, method/path/expiration sensitivity, valid/expired/wrong-signature/method-mismatch validation, comparison behavior, query parsing, URL generation, and format checks for a documented-style test vector.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/tempurl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/types.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/types.rs

## Purpose
Defines shared Swift data structures used by listing and metadata flows.

## Important APIs, types, and functions
`Container` serializes a container listing item with name, object count, total bytes, and optional last modified timestamp. `Object` serializes an object listing item with name, MD5/ETag hash, size, content type, and last modified timestamp. `SwiftMetadata` holds extracted custom metadata plus optional container read/write ACLs.

## Control flow
There is no behavior beyond serde serialization/deserialization and default construction for `SwiftMetadata`.

## State and persistence
These are in-memory DTOs. They mirror persisted Swift/S3 container/object metadata but do not perform reads or writes.

## Dependencies and integration
Depends on `serde` and `HashMap`. `Object` is used by static website directory listings. Container and object listing handlers can serialize these structures as Swift-compatible JSON responses.

## Risks
Timestamp fields are plain strings, so format consistency is enforced by producers rather than types. `SwiftMetadata` ACL fields are only containers for parsed values; authorization semantics must be implemented elsewhere. Dead-code allowances indicate some types are forward-facing API surface even when not locally referenced.

## Test signals
No tests in this file. Coverage is indirect through modules that construct or consume these DTOs, such as staticweb listing tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/versioning.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/versioning.rs

## Purpose
Implements Swift object version archival and restore logic. Version-enabled containers archive overwritten or deleted current objects into a separate archive container using inverted timestamp keys, and deletes can restore the newest archived version.

## Important APIs, types, and functions
`generate_version_name()` creates `{inverted_timestamp}/{container}/{object}` names. `archive_current_version()` checks whether the current object exists and copies it to the archive container. `restore_previous_version()` lists versions, copies the newest back, and deletes the restored archive entry. `list_object_versions()` lists archive objects and filters by `/{container}/{object}` suffix.

## Control flow
Archive flow logs start, `head_object`s the current object, skips not-found, maps Swift account/container/object names to S3 bucket/key names, resolves the global object store, gets source object info, and performs storage `copy_object`. Restore flow lists matching versions, selects the first sorted entry, maps buckets/keys, copies archive to current, then deletes the archive object. Listing validates account, lists up to 1000 archive objects without prefix, converts S3 names back to Swift names, filters suffixes, and sorts ascending so inverted timestamps put newest first.

## State and persistence
Versions are persisted as ordinary objects in an archive container. Current-object data remains in the primary container. Container versioning configuration itself is managed in `container.rs`, not here.

## Dependencies and integration
Depends on Swift account validation, container/object mappers, object HEAD, `resolve_object_store_handle`, storage `ObjectOperations`/`ListOperations`, credentials, and tracing. The Swift handler calls archive before overwrites/deletes and restore after versioned deletes.

## Risks
`generate_version_name()` uses `as_secs_f64`; formatting to nanosecond precision may imply more precision than the float preserves. Listing scans only the first 1000 archive objects and filters client-side, so older or numerous versions can be missed. Restore reports cleanup failure as an error after the current object was already restored, creating ambiguous client semantics. Copy/restore are not transactional across objects.

## Test signals
Unit tests cover version name shape, ordering, special characters, filtering logic, and timestamp uniqueness. Storage-integrated archive/restore/list operations are not fully mocked in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/versioning.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/webdav/config.rs -->
# sources/object-store/rustfs/crates/protocols/src/webdav/config.rs

## Purpose
Defines WebDAV server configuration and initialization errors.

## Important APIs, types, and functions
`WebDavInitError` distinguishes bind, server, invalid config, and TLS failures. `WebDavConfig` contains bind address, TLS enablement, certificate directory, optional CA file, maximum request body size, and request timeout. `validate()` checks TLS file requirements and nonzero limits. `Default` binds `0.0.0.0:8080`, enables TLS, and sets 5 GiB body / 300 second timeout defaults.

## Control flow
Validation rejects TLS-enabled configs without `cert_dir`, rejects missing certificate directories and CA files using async `tokio::fs::try_exists`, and rejects zero body size or timeout.

## State and persistence
No persistence; this is runtime configuration consumed by `server.rs`.

## Dependencies and integration
Uses `SocketAddr`, `thiserror`, and Tokio filesystem checks. `WebDavServer::new()` calls `config.validate()` before accepting a config.

## Risks
The default enables TLS but leaves `cert_dir` unset, so `WebDavConfig::default()` is intentionally incomplete until the caller supplies certificates or disables TLS. `ca_file` is validated but server TLS currently configures `with_no_client_auth`, so CA validation is not yet enforced by the server path. `request_timeout_secs` is validated but not visibly applied in `server.rs`.

## Test signals
No tests here. Behavioral coverage should come from server initialization tests that exercise default, TLS, and invalid limit cases.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/webdav/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/webdav/driver.rs -->
# sources/object-store/rustfs/crates/protocols/src/webdav/driver.rs

## Purpose
Adapts the `dav-server` filesystem traits to RustFS/S3 storage. WebDAV paths map to buckets and object keys, while file, directory, rename, delete, metadata, and listing operations are translated into authorized S3 backend calls.

## Important APIs, types, and functions
`WebDavMetaData` implements `DavMetaData`; `WebDavDirEntry` implements `DavDirEntry`; `WebDavFile<S>` implements `DavFile` for reads, writes, seeks, metadata, and flush; `WebDavDriver<S>` implements `DavFileSystem`. Helper enums `ResolvedPath` and `HeadObjectProbe` disambiguate files, directory markers, prefix directories, missing objects, and forbidden probes. Important helpers include `parse_path`, `list_buckets`, `list_objects`, `resolve_path`, `prefix_has_entries`, `copy_object_streaming`, `execute_directory_rename_pairs`, and `delete_bucket_recursively`.

## Control flow
`open` parses a DAV path, authorizes GET or PUT, and returns a `WebDavFile`. Reads issue ranged GETs from the current position and advance the position. Writes append into an in-memory buffer and `flush` uploads a single object. `read_dir` lists buckets at root or uses delimiter-based object listing inside buckets. `metadata` resolves files, directory markers, prefix directories, bucket roots, and root. `create_dir` creates either a bucket or zero-byte `application/x-directory` marker. `remove_dir` deletes all objects under a prefix or recursively clears a bucket. `rename` resolves source as file or directory, authorizes each S3 action, copies to destination, then deletes sources.

## State and persistence
All durable state is S3 bucket/object state. Directory state is represented by explicit trailing-slash marker objects and/or object prefixes. `WebDavFile` keeps transient position and write buffer in `RwLock`s.

## Dependencies and integration
Depends on `dav-server`, RustFS S3 storage backend abstraction, gateway authorization, session context, `s3s::dto`, percent decoding, RustFS path helpers, bytes/futures, Tokio locks, and tracing. `server.rs` creates this driver after Basic authentication.

## Risks
Writes buffer entire files until flush, bounded by `max_body_size` in `WebDavFile` but constructed through `WebDavFile::new()` in `open`, so server-provided limits are not passed into the driver there. Copy/rename/delete directory operations are multi-object and non-transactional; partial copies can remain after delete failures. `remove_dir` and recursive bucket delete ignore per-object delete errors in some paths. `copy` is not implemented even though `rename` performs copy/delete manually. Path cleaning may normalize client-supplied paths before authorization, which is desired but security-sensitive.

## Test signals
Tests cover URL-decoded path parsing, invalid UTF-8 rejection, trailing slash behavior, nested and non-ASCII paths, bucket-root parsing, and a regression showing directory rename surfaces delete failures after successful copies. Most live S3 authorization/list/read/write behavior relies on integration coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/webdav/driver.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/webdav/mod.rs -->
# sources/object-store/rustfs/crates/protocols/src/webdav/mod.rs

## Purpose
Declares the WebDAV protocol module boundary.

## Important APIs, types, and functions
Exports `config`, `driver`, and `server` submodules. It has no local functions or types.

## Control flow
None locally. Compile-time module inclusion is controlled by the parent crate feature gate for WebDAV.

## State and persistence
None.

## Dependencies and integration
Integrated by `lib.rs`, which exposes WebDAV modules and re-exports server/config types when the `webdav` feature is enabled.

## Risks
The module is intentionally thin; risks are limited to feature/module wiring. Missing re-exports here may require callers to import nested paths.

## Test signals
No direct tests. Compilation with the `webdav` feature verifies module wiring.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/webdav/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/webdav/server.rs -->
# sources/object-store/rustfs/crates/protocols/src/webdav/server.rs

## Purpose
Runs the WebDAV network server. It binds a TCP listener, optionally wraps connections in TLS, authenticates Basic credentials against IAM, constructs a WebDAV driver, and delegates requests to `dav-server`.

## Important APIs, types, and functions
`WebDavServer<S>` stores `WebDavConfig` and storage backend. `new()` validates config. `start()` owns listener setup, TLS resolver/reload setup, accept loop, per-connection spawning, and shutdown handling. `handle_connection_impl()` runs Hyper HTTP/1 over a Tokio IO. `handle_request()` validates body size, parses Basic auth, authenticates, builds `DavHandler`, converts request/response bodies, and returns Hyper responses. `authenticate()` checks IAM access key and secret key and builds a `SessionContext`. Small helpers create unauthorized/error responses and decode base64.

## Control flow
Startup logs, binds, configures a reloadable certificate resolver when TLS is enabled, then loops on accepts and shutdown. Each connection is handled in a spawned task. Each request checks `Content-Length`, decodes Basic credentials, calls IAM, constructs `WebDavDriver`, collects the whole request body into bytes, delegates to `dav-server`, collects the response body, and returns it.

## State and persistence
Server state is runtime-only. TLS certificates are loaded from `cert_dir` and may be reloaded by a background task. Authentication state comes from IAM. Object persistence is delegated through `WebDavDriver` and the storage backend.

## Dependencies and integration
Depends on Hyper, Hyper-util, `dav-server`, Tokio TCP/broadcast/watch, rustls/tokio-rustls, RustFS TLS runtime/config utilities, IAM, credentials, session context, and tracing. It is re-exported from the protocols crate under the WebDAV feature.

## Risks
Requests and responses are fully collected in memory around `dav-server`; the request side has a `Content-Length` check but chunked bodies without a length can still be collected before driver write limits apply. `request_timeout_secs` is not visibly enforced. TLS uses `with_no_client_auth`, so `ca_file` from config is not applied. A new DAV handler is built per request, which is simple but may add overhead.

## Test signals
No local tests. Useful coverage would include auth success/failure, payload-too-large, chunked upload behavior, TLS config validation, graceful shutdown, and end-to-end DAV methods through a mock storage backend.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/webdav/server.rs -->
