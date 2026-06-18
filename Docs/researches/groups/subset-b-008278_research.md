# Research: subset-b-008278

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/write.rs -->
# sources/object-store/rustfs/crates/protocols/src/sftp/write.rs

## Purpose
This file implements the write side of the RustFS SFTP gateway. It turns SFTP `OPEN`, `WRITE`, `CLOSE`, and large-copy behavior into S3-compatible `PutObject`, multipart upload, multipart completion, multipart abort, and multipart copy calls through the gateway `StorageBackend`. The core design is a sequential write state machine: small objects stay buffered until close and are committed with one `PutObject`; objects whose write buffer reaches `part_size` transition to multipart streaming and upload full parts as they arrive.

The module is also the cancellation-safety boundary for in-flight multipart uploads. Because request handlers temporarily remove write handles from the handle table while awaiting backend calls, this file builds "tombstone" `HandleState::Write` entries that carry the upload id and cached abort authorization. `driver.rs` consumes those tombstones from `Drop` to avoid orphaning multipart uploads when a session task is cancelled or disconnected mid-write.

## Important APIs, Types, And Functions
- `write_dispatch_byte_count`, `write_dispatch_append_bytes`, `write_dispatch_has_full_part`, and `fstat_reported_size` are small state-machine helpers over `WritePhase`. They implement offset accounting, append behavior, drain-loop decisions, and reported SFTP file size.
- `build_write_tombstone` constructs a failed write handle containing `upload_id` and `abort_authorized` for `Drop`.
- `rejects_excl_or_trunc_without_create` validates SFTP open-flag combinations.
- `should_abort_on_drop` returns an upload id only for `Streaming` or `Failed` phases whose cached abort probe allowed `AbortMultipartUpload`.
- `SftpDriver::open_write` validates paths, read-only mode, S3 `PutObject` authorization, and SFTP create/truncate semantics, then allocates a `HandleState::Write`.
- `SftpDriver::commit_write` performs the single-shot close-time `PutObject` path with metadata derived from SFTP attributes and retry on retryable S3 errors.
- `SftpDriver::start_multipart_upload`, `upload_multipart_bytes`, `finish_multipart_upload`, `abort_upload_with_auth`, and `close_abort_or_skip` wrap S3 multipart lifecycle operations with gateway authorization and error mapping.
- `SftpDriver::write_dispatch`, `write_dispatch_begin_streaming`, and `write_dispatch_flush_one_part` implement sequential writes, buffering-to-streaming transition, full-part upload, and failure poisoning.
- `SftpDriver::close_streaming` flushes a final partial part, completes multipart upload, or aborts/skips abort on failure according to the cached policy decision.
- `SftpDriver::multipart_copy` performs server-side copy for objects too large for single S3 copy by using multipart upload plus `UploadPartCopy` ranges.

## Control Flow
`open_write` first calls `enforce_server_readonly`, parses the SFTP path into bucket/key, rejects bucket-only opens, and authorizes `S3Action::PutObject`. It only accepts create-and-truncate semantics because the implementation replaces the whole object at close. `EXCLUDE` adds a best-effort `head_object` check: an existing object fails the open, a not-found result allows creation, and other S3 errors propagate. The handle starts in `WritePhase::Buffering` with empty `part_buffer`; selected open attributes are copied into the reported SFTP attributes and later converted to user metadata.

`write_dispatch` receives a write handle already removed from the table by the caller. It checks that the client offset exactly equals the current byte count, appends the incoming bytes, and loops while the buffer has at least `part_size` bytes. The first full part transitions from `Buffering` to `Streaming` by calling `start_multipart_upload`; after the upload id exists, a tombstone is inserted into the handle table before any later awaited part upload can be cancelled. Each full part is drained from the buffer and uploaded with `upload_multipart_bytes`, then its ETag is recorded as a `CompletedPart`. If upload fails, the phase becomes `Failed` with the upload id so close/drop can abort.

`commit_write` is the close path for handles that never entered multipart streaming. It wraps the buffered bytes in `Bytes` and rebuilds a single-use `StreamingBlob` per attempt. Retry is bounded by `COMMIT_WRITE_MAX_RETRIES` and `COMMIT_WRITE_BACKOFF_MS`, and is limited to errors recognized as retryable by `rustfs_utils::retry::is_s3code_in_message_retryable`. Non-retryable failures are immediately mapped through `s3_error_to_sftp`.

`close_streaming` handles multipart close by optionally uploading a final non-empty trailing buffer, enforcing the S3 multipart part cap for that final part, and then calling `finish_multipart_upload`. Any failure in final part upload or completion routes through `close_abort_or_skip`; that helper either re-authorizes and calls `AbortMultipartUpload` or logs a policy-respecting skip if the initial abort probe was denied.

`multipart_copy` computes an effective range size large enough to keep the copy within `S3_MAX_MULTIPART_PARTS` and not exceed `S3_MAX_PART_SIZE`. It creates a destination multipart upload, iterates byte ranges with `UploadPartCopy`, collects ETags, then completes or aborts the destination upload. Source data remains server-side.

## State And Persistence Behavior
The persistent state mutated by this file is object data and multipart upload state in the backing S3-compatible store. Buffered writes become one completed object through `PutObject`. Streaming writes create a multipart upload, stage uploaded parts, and either complete into the destination object or abort the upload. Failed or cancelled multipart uploads can leave staged parts only when abort is unauthorized or abort itself fails; the code explicitly expects bucket lifecycle cleanup for that policy pattern.

In-memory state lives in `HandleState::Write` and `WritePhase`: `Buffering` owns bytes not yet sent to S3; `Streaming` owns `upload_id`, `abort_authorized`, `part_buffer`, uploaded part metadata, and `next_part_number`; `Failed` preserves `upload_id` and abort policy after a part failure or as a cancellation tombstone. `attrs.size` is updated after successful writes using saturating byte-count logic; `fstat_reported_size` returns cached size for failed handles so clients see the last known successful byte count.

Open-time SFTP attributes are persisted as S3 user metadata by `sftp_attrs_to_user_metadata` on both single `PutObject` and `CreateMultipartUpload`. Multipart copy intentionally starts with empty SFTP attributes.

## Dependencies And Integration Points
The module depends on SFTP-specific path parsing, attribute conversion, state definitions, and error mapping from sibling modules. It integrates with `SftpDriver` handle allocation and handle-table management, `StorageBackend` S3 operations, gateway `S3Action` authorization, russh-sftp protocol types, `s3s::dto` builders, byte streams from `bytes`/`futures_util`, retry classification from `rustfs_utils`, and structured tracing.

It is tightly coupled to `driver.rs` because cancellation safety relies on the driver's drop-time scan using `should_abort_on_drop`. It also relies on caller discipline: removed handles must be reinserted or tombstoned around awaits according to the documented pattern.

## Risks And Edge Cases
- The write path only supports sequential overwrite semantics. Non-sequential offsets, append-like writes, or create-without-truncate are rejected to avoid silent data corruption.
- `EXCLUDE` is not atomic against a racing close-time `PutObject`; the code documents this as an S3 limitation.
- The multipart tombstone design is robust but subtle. Any future await inserted between upload id creation and tombstone insertion, or any remove-await-reinsert site that forgets the tombstone, can reintroduce orphaned uploads.
- `write_dispatch_flush_one_part` drains bytes before `UploadPart`; on failure the bytes are intentionally lost and the handle is poisoned. This is correct for abort semantics but means recovery must happen by restarting the upload, not continuing the handle.
- Abort authorization is cached by probing IAM before upload creation completes. Conditional IAM policies are not represented because gateway authorization passes empty conditions, so only unconditional allow/deny is honored.
- If abort is denied, failed or cancelled multipart uploads rely on lifecycle cleanup. Operators using deny-abort policies must configure cleanup rules.
- `commit_write` retries retryable backend messages but not run-backend deadline failures; a stalled backend becomes an immediate SFTP failure.
- Multipart copy guards oversized effective part sizes, but the comments note that an out-of-spec backend content length can still surface as generic failure.

## Test Signals
The file has extensive unit coverage under `#[cfg(test)]`. Tests cover helper arithmetic and failure behavior, transition tombstones before awaits, abort authorization caching, metadata preservation for single and multipart uploads, missing ETags, parts-limit failures with allowed and denied abort, complete/final-part failure abort paths, open-flag validation including `EXCLUDE`, cancellation mid-upload drop abort, retry behavior for `commit_write`, timeout handling, and non-retryable access-denied behavior. These tests strongly exercise state-machine edges, policy-sensitive abort behavior, and recent cancellation-safety invariants.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/sftp/write.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/account.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/account.rs

## Purpose
This file implements Swift account-level validation and account metadata helpers for the Swift protocol layer. Its main job is tenant isolation: it checks that a Swift account path such as `AUTH_<project_id>` matches the Keystone project id embedded in authenticated credentials. It also stores account-level Swift metadata, especially TempURL keys, in a dedicated hidden S3 bucket represented by RustFS bucket metadata tags.

## Important APIs, Types, And Functions
- `validate_account_access(account, credentials) -> SwiftResult<String>` strips the `AUTH_` prefix, extracts `keystone_project_id` from credential claims, and returns the project id only when both match.
- `is_admin_user(credentials) -> bool` checks `keystone_roles` claims for `admin` or `reseller_admin`.
- `get_account_metadata_bucket_name(account) -> String` hashes the account with SHA256 and builds `swift-account-<first16hex>`.
- `get_account_metadata(account, credentials)` loads bucket metadata and returns tags whose keys start with `swift-account-meta-`.
- `update_account_metadata(account, metadata, credentials)` creates the metadata bucket if missing, replaces only `swift-account-meta-*` tags, preserves unrelated tags, serializes `Tagging` XML, and writes bucket metadata back through `metadata_sys`.
- `get_tempurl_key(account, credentials)` returns the `temp-url-key` account metadata value when present.

## Control Flow
Account access validation is synchronous and claim-driven. Missing `AUTH_` prefix returns `BadRequest`; missing Keystone project id returns `Unauthorized`; project mismatch returns `Forbidden`; success returns the project id string used by container mapping.

Metadata reads compute the hashed metadata bucket name and call `rustfs_ecstore::bucket::metadata_sys::get`. Any error is treated as absent metadata and returns an empty map. When metadata exists, only tags with the account metadata prefix are copied into the result with the prefix stripped.

Metadata writes resolve the global object store handle, create the metadata bucket if `metadata_sys::get` does not find it, reload bucket metadata, remove old Swift account metadata tags, append new tags, and persist the updated metadata. An empty resulting tag set clears both parsed and XML tagging fields; a non-empty set is serialized with `quick_xml`.

## State And Persistence Behavior
Persistent account state is stored in a synthetic bucket named by a deterministic hash of the account id. Account metadata is encoded as S3 bucket tags using the `swift-account-meta-` namespace. Updates are replace-all for Swift account metadata keys, not patch-by-key: every old prefixed tag is removed before the supplied map is written. Non-Swift bucket tags are deliberately preserved.

The metadata bucket may be created lazily. The `credentials` argument is currently unused in metadata functions, so authorization and tenant validation must happen before these helpers are called.

## Dependencies And Integration Points
The module depends on `rustfs_credentials::Credentials` for Keystone claims, `rustfs_ecstore::resolve_object_store_handle` and `metadata_sys` for storage access, `rustfs_storage_api::MakeBucketOptions` for lazy bucket creation, `s3s::dto::{Tag, Tagging}` for tag representation, SHA256/hex for deterministic bucket naming, `quick_xml` for tag serialization, and the local `SwiftError`/`SwiftResult` model.

`validate_account_access` is called by container operations to derive the project id used for tenant bucket prefixes. `get_tempurl_key` is a likely integration point for Swift TempURL request authentication.

## Risks And Edge Cases
- `get_account_metadata` treats every metadata load error as "no metadata", which can hide storage failures from TempURL or account metadata callers.
- The account metadata bucket name uses only 16 hex characters of SHA256. Collision risk is low but nonzero by construction.
- Metadata writes do not validate tag count, key length, or value length against any S3 tag limits in this file.
- Credentials are ignored by metadata read/write helpers, so callers must validate account access and authorization externally.
- Lazy bucket creation uses default options and may expose account metadata buckets to normal bucket listings unless other layers hide the `swift-account-` naming convention.

## Test Signals
Unit tests cover successful account validation, mismatched account/project, invalid account format, missing project id, admin and reseller-admin role detection, non-admin defaults, and deterministic hashed account metadata bucket naming. There are no async storage tests for metadata read/write persistence, tag preservation, XML serialization, or error behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/account.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/acl.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/acl.rs

## Purpose
This file models and evaluates Swift container ACLs. It parses `X-Container-Read` and `X-Container-Write` header values into typed grants, serializes grants back to headers, and checks whether a request account/user/referrer is allowed. It intentionally allows public/referrer grants only for read ACLs and rejects public write ACLs.

## Important APIs, Types, And Functions
- `ContainerAcl { read, write }` stores parsed read and write grants.
- `AclGrant` represents `PublicRead`, `PublicReadReferrer(pattern)`, account-wide access, and user-specific access.
- `impl Display for AclGrant` serializes grants back to Swift header grammar.
- `ContainerAcl::parse_read` and `parse_write` split comma-separated headers, trim whitespace, and call `parse_grant`.
- `parse_grant(grant_str, allow_public)` recognizes `.r:*`, `.r:<pattern>`, `AUTH_account`, and `AUTH_account:user`.
- `check_read_access(request_account, request_user, referrer)` evaluates read grants and defaults empty read ACLs to authenticated access.
- `check_write_access(request_account, request_user)` evaluates write grants and defaults empty write ACLs to owner/caller write access.
- `matches_referrer_pattern` implements exact referrer matching plus leading-asterisk suffix matching.
- `read_to_header`, `write_to_header`, and `is_public_read` expose serialization and public-read inspection helpers.

## Control Flow
Parsing trims the whole header, returns an empty vector for empty values, then parses each non-empty comma-separated token. `.r:` grants are accepted only when parsing read ACLs; `.r:*` becomes public read and any other non-empty `.r:` suffix becomes a referrer pattern. `AUTH_` strings with a colon become user grants if the user part is non-empty; `AUTH_` strings without a colon become account grants. Any other string returns `BadRequest`.

Read access checks short-circuit on the first matching grant. Public read grants allow all callers. Referrer grants require a present `Referer` value matching exact or suffix pattern. Account and user grants require matching authenticated account and optionally user. Empty read ACLs allow any authenticated account and deny anonymous access.

Write access similarly scans write grants. Public grants are ignored defensively because parsing should prevent them. Account grants match the request account; user grants require both account and user. Empty write ACLs return true for the supplied request account, relying on callers to pass only the container owner or an otherwise authorized account.

## State And Persistence Behavior
This file is pure in-memory parsing and evaluation. It does not read or write storage itself. Persistence is handled by `container.rs`, which stores read/write ACL header strings in bucket tags named `swift-acl-read` and `swift-acl-write`, then reparses them through this module on retrieval.

## Dependencies And Integration Points
The module uses the local `SwiftError`/`SwiftResult` type and `tracing::debug` for structured ACL decision logs. It integrates with `container::set_container_acl` and `container::get_container_acl`, and likely with Swift object/container handlers that need to enforce public or cross-account access.

## Risks And Edge Cases
- Referrer matching is simple suffix matching for patterns starting with `*`; it does not parse URLs or normalize scheme/host. A full URL referrer may not match patterns as operators expect, or may match by suffix in surprising ways.
- Empty read ACLs allow any authenticated account according to this function, while comments say "owner can read". Correct ownership enforcement must happen before or around this check.
- Empty write ACLs return true for any supplied `request_account`, again relying on caller-side owner scoping.
- The parser accepts account names beginning `AUTH_` without validating project id shape.
- Duplicate grants are preserved and serialized; no normalization or deduplication is performed.
- Public write is rejected at parse time, but if a malformed `ContainerAcl` is constructed manually with public grants in `write`, they are silently ignored.

## Test Signals
The test module is broad. It covers parsing public, referrer, account, user, mixed, empty, and invalid ACLs; rejection of public write ACLs; read/write access decisions for public, referrer, account, and user grants; default empty ACL behavior; serialization; public-read detection; whitespace handling; multiple referrer patterns; user-specific requirements; ACL removal; and complex read/write scenarios. There are no persistence tests in this file because storage is delegated to `container.rs`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/acl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/bulk.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/bulk.rs

## Purpose
This file implements Swift bulk operations: bulk delete and bulk archive extract. Bulk delete processes a newline-separated list of `/container/object` paths and deletes each object through the Swift object layer. Bulk extract accepts a tar, tar.gz, or tar.bz2 archive, extracts regular file entries into memory, and uploads them into one container.

## Important APIs, Types, And Functions
- `DeleteResult` and `ExtractResult` model per-item outcomes, although only aggregate response structures are serialized by handlers.
- `BulkDeleteResponse` serializes Swift-style fields such as `Number Deleted`, `Number Not Found`, `Errors`, `Response Status`, and `Response Body`.
- `BulkExtractResponse` serializes `Number Files Created`, `Errors`, and response status/body fields.
- `parse_object_path(path)` trims a path, strips leading slashes, and splits it into container and object key.
- `handle_bulk_delete(account, body, credentials)` loops over request-body paths, calls `object::delete_object`, counts deleted/not-found/errors, and returns a JSON `200 OK` response.
- `ArchiveFormat::{Tar, TarGz, TarBz2}` and `ArchiveFormat::from_query` parse Swift `extract-archive` formats including aliases `tgz`, `tbz2`, and `tbz`.
- `handle_bulk_extract(account, container, format, body, credentials)` checks that the container exists, extracts archive entries, uploads each entry with `object::put_object`, and returns a JSON response.
- `extract_tar_entries(format, body)` builds an async tar reader, optionally wraps gzip/bzip2 decoders, skips directories, and returns `(path, bytes)` pairs for files.

## Control Flow
Bulk delete starts with structured debug logging, filters blank body lines, and rejects empty requests. Each path is parsed independently. A successful delete increments `number_deleted`; `SwiftError::NotFound` increments `number_not_found`; any other delete error is appended to `Errors` and represented as a per-item 500. Invalid path syntax is appended as a 400-style error. The overall Swift response body marks `"400 Bad Request"` if any errors occurred, but the HTTP status returned by the axum response is always `200 OK`, matching common Swift bulk response patterns where per-item status is in the JSON body.

Bulk extract validates the target container by calling `container::get_container_metadata`. It fully buffers the archive request body and then `extract_tar_entries` fully buffers every file entry before upload begins. It then uploads entries sequentially with an empty header map. Created files increment `number_files_created`; upload failures are collected in `Errors`. If zero files are created, response status and HTTP status become bad request; otherwise HTTP status is `201 Created`, even with per-file errors.

Archive extraction chooses a reader based on `ArchiveFormat`, iterates tar entries asynchronously, converts each tar path with `to_string_lossy`, skips directories, and reads regular entry contents to a `Vec<u8>`. Read failures for individual entries are logged and skipped rather than aborting the entire extraction.

## State And Persistence Behavior
Bulk delete mutates object storage by calling the Swift object delete path for each requested object. Bulk extract mutates object storage by creating or overwriting objects in the target container through `object::put_object`. This file does not directly access S3 buckets; all object persistence goes through the Swift `container` and `object` modules.

Response state is accumulated in local structs and serialized to JSON. No durable operation log or transaction state is maintained. Bulk operations are partial-success workflows: earlier successful deletes/uploads are not rolled back if later items fail.

## Dependencies And Integration Points
The module depends on `object::delete_object`, `object::put_object`, `container::get_container_metadata`, Swift error/result types, axum response builders, `s3s::Body`, serde JSON serialization, `futures::StreamExt`, `tokio_tar`, `async_compression`, Tokio async I/O, and transaction id generation from `super::handler`.

It is an HTTP handler support module for Swift routes such as `DELETE /?bulk-delete` and `PUT /{container}?extract-archive=<format>`.

## Risks And Edge Cases
- Bulk extract buffers the entire archive and all file contents in memory. Large archives can cause high memory usage; there are no local entry count, total size, or per-file limits.
- Tar entry paths are accepted as lossy strings and passed directly to `put_object`. This file does not reject absolute paths, `..`, duplicate entries, special file types other than directories, or path names that may be surprising as object keys.
- Entry read failures are logged and skipped without adding an error to the response, which can make archives appear more successful than they were.
- Bulk delete keeps processing after errors and returns HTTP 200 even when JSON `Response Status` is `"400 Bad Request"`; clients must inspect the body.
- `DeleteResult` and `ExtractResult` are accumulated partly or defined but not serialized in the final response, so detailed status is limited to `Errors`.
- Uploads in bulk extract use an empty header map, so content type and metadata from archive entries are not preserved.

## Test Signals
Unit tests cover object-path parsing, invalid paths, archive format parsing and aliases, default response values, body line filtering, and, behind the `swift` feature, tar extraction for plain tar, gzip, bzip2, directory skipping, invalid tar errors, and empty archives. There are no storage-backed handler tests for partial delete/upload behavior, response status/body coupling, or transaction id headers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/bulk.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/container.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/container.rs

## Purpose
This file implements Swift container operations on top of RustFS/S3 bucket primitives. It maps account-scoped Swift container names to tenant-prefixed S3 bucket names, performs container CRUD, lists objects, stores Swift container metadata as bucket tags, manages Swift object versioning configuration, and persists container ACLs through the ACL parser.

## Important APIs, Types, And Functions
- `sanitize_storage_error` logs detailed storage failures while returning a generic `InternalServerError`.
- `swift_metadata_to_s3_tags` and `s3_tags_to_swift_metadata` convert between `X-Container-Meta-*` metadata and `swift-meta-*` S3 bucket tags.
- `ContainerMapperConfig` and `ContainerMapper` implement tenant prefixing. `hash_project_id` uses the first eight bytes of SHA256 as a 16-character hex prefix; `swift_to_s3_bucket`, `s3_to_swift_container`, and `bucket_belongs_to_project` apply or reverse that mapping.
- `bucket_info_to_container` converts `BucketInfo` to the Swift `Container` DTO.
- `list_containers`, `create_container`, `get_container_metadata`, `update_container_metadata`, and `delete_container` implement Swift container CRUD.
- `list_objects` implements Swift container object listing by calling `list_objects_v2`.
- `enable_versioning`, `disable_versioning`, and `get_versions_location` manage the `swift-versions-location` bucket tag.
- `set_container_acl`, `get_container_acl`, and `delete_container_acl` store and retrieve ACL header values in `swift-acl-read` and `swift-acl-write` bucket tags.

## Control Flow
Most public operations first call `validate_account_access` to extract the Keystone project id, validate the Swift container name, instantiate the default tenant-prefix mapper, and resolve the global object store handle. The mapped bucket name is then used for storage API calls.

`list_containers` lists all buckets, filters by the project hash prefix, and converts matching buckets to Swift containers. `create_container` checks existence and returns `Ok(false)` for an existing bucket so the handler can return Swift `202 Accepted`; otherwise it creates the bucket and returns `Ok(true)`. `delete_container` verifies existence and then deletes with `force: false`, mapping non-empty bucket errors to Swift conflict.

`get_container_metadata` verifies the bucket, then loads bucket metadata tags and extracts only `swift-meta-*` tags into `custom_metadata`; object count and bytes used are currently placeholders. `update_container_metadata` verifies existence, loads current bucket metadata, removes old `swift-meta-*` tags while preserving other tags, appends converted Swift metadata tags, serializes tags to XML when non-empty, and writes the bucket metadata back.

`list_objects` checks bucket existence, prepares max keys, prefix, marker, and delimiter arguments, calls `list_objects_v2`, and maps returned object metadata into Swift object DTOs with name, ETag, size, content type, and RFC3339 modification time.

Versioning and ACL operations follow the same tag-editing pattern. Versioning requires the archive container to exist and differ from the source container before writing `swift-versions-location`. ACL setting validates header strings through `ContainerAcl` before replacing the ACL tag pair. ACL retrieval loads tags and reparses values into a `ContainerAcl`.

## State And Persistence Behavior
Container existence maps directly to S3 bucket existence. Tenant isolation is encoded in bucket names by a deterministic project hash prefix. Swift custom metadata, versioning configuration, and ACLs are persisted as bucket tags in RustFS bucket metadata; tag XML and parsed tag config are updated together with a new `tagging_config_updated_at` timestamp.

Tag updates are namespace-specific replacements. Metadata updates remove only `swift-meta-*` tags. Versioning updates remove only `swift-versions-location`. ACL updates remove only `swift-acl-read` and `swift-acl-write`. Other tags are preserved across all of these operations.

Object listing is read-only. Object counts and byte totals in container metadata/listing are currently not persisted or computed in this module and are returned as zero.

## Dependencies And Integration Points
This module depends on `account::validate_account_access`, Swift DTOs from `types`, `rustfs_ecstore::resolve_object_store_handle`, bucket/list storage traits, `rustfs_storage_api` bucket option types, `s3s::dto::{Tag, Tagging}`, SHA256, `quick_xml`, `time`, and `tracing`.

It is the central Swift container service used by higher-level HTTP handlers, CORS loading (`cors.rs`), bulk extract validation (`bulk.rs`), object-versioning logic in `object.rs`, and ACL enforcement/retrieval via `acl.rs`.

## Risks And Edge Cases
- The default mapper always enables tenant prefixing, but disabling prefixing makes `bucket_belongs_to_project` return true for all buckets, weakening tenant isolation.
- Container names are validated only for non-empty, length <= 256, and no slash. S3 bucket naming restrictions are stricter, so some Swift-valid names may fail storage creation later.
- Error mapping often checks substrings such as `"not found"` or `"NoSuchBucket"`, which can be brittle across storage error formatting.
- Metadata, versioning, and ACL updates use read-modify-write on bucket metadata with no explicit concurrency control in this file; concurrent updates to different tag namespaces can race and lose changes.
- `get_versions_location` returns `Ok(None)` for any metadata load error, potentially hiding storage failures as "versioning disabled".
- Object count and byte usage are placeholders, so Swift clients that depend on accurate container stats receive zeros.
- ACL default semantics rely on `acl.rs` and caller context; this module stores/retrieves ACLs but does not enforce them in container operations.

## Test Signals
The test module covers tenant hash mapping, reverse mapping, project ownership checks, bucket-to-container conversion, container-name validation, collision prevention for ambiguous tenant/container separator cases, hash determinism and S3-compatible characters, metadata-to-tag conversion, tag-to-metadata extraction, case normalization, round trips, tag preservation/removal behavior, and versioning tag format/update/removal helpers. There are no async integration tests for real bucket creation/deletion, metadata persistence through `metadata_sys`, object listing, ACL persistence, or concurrent tag updates.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/container.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/cors.rs -->
# sources/object-store/rustfs/crates/protocols/src/swift/cors.rs

## Purpose
This file implements Swift CORS support for containers. It loads CORS configuration from Swift container metadata, injects CORS headers into normal responses, handles browser preflight `OPTIONS` requests, and exposes a convenience check for whether CORS is configured.

## Important APIs, Types, And Functions
- `CorsConfig` stores `allow_origin`, `max_age`, `expose_headers`, and `allow_credentials`.
- `CorsConfig::load(account, container_name, credentials)` calls `container::get_container_metadata` and parses `x-container-meta-access-control-*` custom metadata keys.
- `CorsConfig::is_enabled` returns true when an allowed origin is configured.
- `CorsConfig::inject_headers(response, request_origin)` adds `access-control-allow-origin`, `access-control-expose-headers`, and `access-control-allow-credentials` when applicable.
- `handle_preflight(account, container_name, credentials, request_headers)` builds the `OPTIONS` response, adds allowed methods, max age, echoed request headers, and Swift transaction id headers.
- `is_enabled(account, container_name, credentials)` loads configuration and converts load errors to `Ok(false)`.

## Control Flow
Loading is metadata-driven. `allow_origin` is copied directly from `x-container-meta-access-control-allow-origin`; `max_age` is parsed as `u64` and ignored on parse failure; `expose_headers` is split on commas and trimmed; `allow_credentials` is true only when the metadata value lowercases to `"true"`.

Header injection is a no-op unless CORS is enabled. A configured wildcard origin always emits `access-control-allow-origin: *`. A specific configured origin is emitted only when the request `Origin` header is present and exactly equals the configured value. Expose headers are joined with comma-space. Credentials are emitted whenever enabled, independent of whether an allow-origin header was actually inserted.

Preflight handling loads config, rejects unconfigured containers with `Forbidden`, extracts `Origin`, creates an empty `200 OK` response, injects CORS headers, adds a fixed Swift method list, adds max age if configured, echoes `Access-Control-Request-Headers` as `Access-Control-Allow-Headers`, and appends `x-trans-id` plus `x-openstack-request-id`.

## State And Persistence Behavior
This file is read-only with respect to persistent state. CORS configuration is persisted elsewhere as Swift container custom metadata, which `container.rs` stores as `swift-meta-*` bucket tags. `cors.rs` only loads and interprets those metadata values and mutates outgoing HTTP response headers.

## Dependencies And Integration Points
The module depends on `container::get_container_metadata`, `SwiftError`/`SwiftResult`, axum/http header and response types, `s3s::Body`, `rustfs_credentials::Credentials`, `tracing`, and transaction id generation from `super::handler`.

It integrates with Swift object/container handlers that need to answer preflight requests or add CORS headers to normal responses.

## Risks And Edge Cases
- Specific origins require exact string equality; there is no list parsing, wildcard subdomain matching, normalization, or case folding.
- `allow_credentials` can be emitted with wildcard origin, a combination browsers reject for credentialed requests.
- If a specific origin is configured but the request origin does not match, `allow_credentials` and expose headers may still be added without `allow-origin`.
- `is_enabled` maps all load errors, including storage errors, to `false`, which can hide backend failures.
- Invalid `max_age` values are silently ignored.
- Echoing requested headers trusts the request header value as long as it is syntactically accepted by the HTTP library; no configured allow-list is enforced here.

## Test Signals
Unit tests cover default disabled config, enabled config, wildcard origin injection, exact-origin match and mismatch, expose-header joining, credentials header injection, disabled no-op behavior, and simple expose-header parsing. There are no async tests for `CorsConfig::load`, preflight response construction, transaction id headers, forbidden behavior when CORS is absent, or storage-error masking in `is_enabled`.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/protocols/src/swift/cors.rs -->
