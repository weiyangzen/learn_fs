# subset-b-008243 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_remove.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_remove.rs

## Purpose
Implements S3 removal operations for the RustFS transition client: bucket delete, object delete, multi-object delete, and multipart-upload abort. It is the client-side HTTP/XML bridge between higher-level lifecycle/replication code and S3-compatible remote tiers.

## Important APIs, types, and functions
`RemoveBucketOptions`, `AdvancedRemoveOptions`, `RemoveObjectOptions`, `RemoveObjectsOptions`, `RemoveObjectResult`, and `RemoveObjectError` model deletion inputs and streamed outputs. `TransitionClient::remove_bucket`, `remove_bucket_with_options`, `remove_object`, `remove_object_inner`, `remove_objects`, `remove_objects_with_result`, `remove_objects_inner`, `remove_incomplete_upload`, and `abort_multipart_upload` are the main APIs. `generate_remove_multi_objects_request` serializes `<Delete>` XML and `process_remove_multi_objects_response` parses `<DeleteResult>` XML into per-object results.

## Control flow
Single bucket and object deletes construct `RequestMetadata` and call `execute_method` with HTTP DELETE, then clear bucket location cache for bucket deletes or extract delete marker headers for object deletes. Batch deletion consumes `ObjectInfo` values from a Tokio channel, groups up to 1000 entries, generates XML, computes MD5 and lowercase hex SHA-256 payload hashes, posts `?delete`, reads the response body, and sends one result per object. Invalid XML-name fallback is scaffolded but `has_invalid_xml_char` currently always returns false. Multipart abort maps a 404 into a typed `NoSuchUpload` response and otherwise propagates parsed HTTP errors.

## State and persistence behavior
This module does not persist local state. It mutates the in-memory bucket location cache after bucket deletion and emits deletion outcomes over channels. Remote S3/object-store state is changed by DELETE/POST requests. Batch deletion tracks a local pending set to detect missing response entries.

## Dependencies and integration points
It depends on `TransitionClient::execute_method`, `RequestMetadata`, S3 headers, `s3s::S3ErrorCode`, RustFS hash utilities, `ObjectInfo`, `DeleteMultiObjects`, and Tokio MPSC. It integrates with multipart upload discovery/abort APIs and with replication/lifecycle callers that consume result streams.

## Risks and edge cases
`remove_objects_with_result` creates a duplicate unused channel before creating the real one. `RemoveObjectResult::clone` drops the embedded error, so error forwarding can lose detail when a cloned result is sent. Batch response parsing requires one exact `(key, version)` match per input and reports synthetic errors for XML parse/read failures or unmatched entries. `remove_bucket_with_options` ignores its options, and response status validation for bucket/object delete relies mostly on `execute_method`.

## Test signals
The embedded Tokio test captures a raw HTTP request and asserts multi-delete uses a 64-character lowercase hex `X-Amz-Content-Sha256` instead of base64. Response parsing paths are covered indirectly by receiving at least one result from the local test server.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_remove.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_restore.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_restore.rs

## Purpose
Provides the transition client API for S3 restore-object requests, plus small serializable structures for restore output location/encryption metadata.

## Important APIs, types, and functions
`Encryption`, `MetadataEntry`, and `S3` model restore destination attributes. `TransitionClient::restore_object` is the only behavior-bearing function. It accepts bucket, object, optional version id, and an `s3s::dto::RestoreRequest`.

## Control flow
The method builds query values containing `restore` and optional `versionId`, prepares an empty request body, and calls `execute_method`. It then reads the full response body. HTTP `202 Accepted` and `200 OK` are considered success; any other status is converted through `http_resp_to_error_response`.

## State and persistence behavior
There is no local persistence. Successful calls instruct the remote tier to start or update object restore state. The supplied `RestoreRequest` is not currently serialized; the code has commented `quick_xml` serialization and sends an empty body/hash instead.

## Dependencies and integration points
This module integrates with `TransitionClient`, `RequestMetadata`, `ReaderImpl`, S3 restore DTOs, and shared error conversion. It is expected to be used by object lifecycle or tiering code that needs to restore archived objects from remote storage classes.

## Risks and edge cases
The HTTP method is `HEAD`, while S3 RestoreObject is normally a POST request with a restore XML body. The current empty payload and empty checksum fields mean restore parameters such as days, tier, select type, or output location are ignored. This is likely incomplete or non-compliant unless the target tier has custom semantics.

## Test signals
No local tests are present. Useful tests would assert POST method selection, XML body serialization, version-id query encoding, checksum headers, and 200/202/error response handling against a local S3-compatible endpoint.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_restore.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_s3_datatypes.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_s3_datatypes.rs

## Purpose
Defines S3-compatible DTOs used by the transition client for listing buckets/objects/versions, multipart upload operations, copy results, checksum-bearing parts, and multi-delete XML payloads.

## Important APIs, types, and functions
Important structs include `ListBucketV2Result`, `ListBucketResult`, `ListMultipartUploadsResult`, `ObjectPart`, `ListObjectPartsResult`, `InitiateMultipartUploadResult`, `CompleteMultipartUploadResult`, `CompletePart`, `CompleteMultipartUpload`, `DeleteObject`, `DeleteMultiObjects`, and `DeleteMultiObjectsResult`. `ObjectPart::checksum_raw` decodes and validates base64 checksum bytes. `CompleteMultipartUpload::marshal_msg/unmarshal` and `DeleteMultiObjects::marshal_msg/unmarshal` translate Rust DTOs to and from quick-xml wire forms.

## Control flow
Most types are plain data carriers. Multipart completion and multi-delete requests serialize via `quick_xml::se::to_string`; fallback parsing creates internal wire structs with PascalCase field names and converts them into public structs. Checksum helpers select a checksum string by `ChecksumMode`, base64-decode it, and compare decoded length to the algorithm's expected raw byte length.

## State and persistence behavior
The file stores no mutable state. It preserves wire-visible metadata such as ETags, version IDs, part numbers, checksum fields, owner/initiation data, and delete marker metadata so callers can persist or forward it elsewhere.

## Dependencies and integration points
It depends on `s3s::dto::Owner`, serde, quick-xml, `time::OffsetDateTime`, `ChecksumMode`, and `transition_api::ObjectInfo/ObjectMultipartInfo`. It is consumed by list, multipart, checksum, and delete client modules.

## Risks and edge cases
Several result structs have private fields, limiting external construction/inspection. XML naming depends on serde defaults and local wire structs; serialization may not exactly match AWS S3 element names for all fields. Base64 uses RustFS URL-safe-no-pad helpers, which may differ from AWS's normal padded checksum encoding expectations.

## Test signals
No tests live in this file. Behavior is indirectly exercised by `api_remove` multi-delete tests and multipart/listing callers. Direct tests should round-trip XML examples for complete multipart upload and delete objects, including empty version IDs and checksum fields.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_s3_datatypes.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_stat.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/api_stat.rs

## Purpose
Implements metadata/stat APIs for buckets and objects: bucket existence probing, bucket versioning retrieval placeholder, and object HEAD/stat conversion.

## Important APIs, types, and functions
`TransitionClient::bucket_exists`, `get_bucket_versioning`, and `stat_object` are the exported methods. `stat_object` consumes `GetObjectOptions` and returns `transition_api::ObjectInfo` via `to_object_info`.

## Control flow
`bucket_exists` issues a HEAD bucket request and returns false on non-OK responses, otherwise true; it also reads and logs error response details when available. `get_bucket_versioning` sends `GET ?versioning`, reads the body, logs parsed error metadata, and currently returns `VersioningConfiguration::default()`. `stat_object` builds headers from options, adds internal replication/delete-marker headers, executes HEAD, interprets delete-marker and replication-ready headers, and returns either parsed object metadata or a minimal `ObjectInfo` for non-success/delete-marker cases.

## State and persistence behavior
There is no local persistence. The methods read remote bucket/object metadata and map HTTP headers into transient structs. Internal replication flags are transmitted as custom headers.

## Dependencies and integration points
The module uses `TransitionClient::execute_method`, `GetObjectOptions`, S3 headers `x-amz-delete-marker` and `x-amz-version-id`, UUID parsing, and common error conversion. It is part of read, replication, and delete-marker workflows.

## Risks and edge cases
`bucket_exists` returns true if `execute_method` itself returns an error, because only the `Ok(resp)` branch can return false. `get_bucket_versioning` ignores the returned XML and always returns default configuration. `stat_object` suppresses most non-OK statuses into default `ObjectInfo` instead of returning an error, which may hide authorization or missing-object failures from callers.

## Test signals
No local tests are present. Useful signals would cover HEAD 200 metadata conversion, delete-marker 405 handling with version IDs, replication-ready headers, missing bucket/object errors, and XML parsing for bucket versioning.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/api_stat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/bucket_cache.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/bucket_cache.rs

## Purpose
Maintains an in-memory bucket-to-region cache and implements bucket location discovery for the transition client.

## Important APIs, types, and functions
`BucketLocationCache::new/get/set/delete` wraps a `HashMap<String, String>`. `TransitionClient::get_bucket_location`, `get_bucket_location_inner`, and `get_bucket_location_request` perform cached region lookup. `process_bucket_location_response` maps S3 location XML and several error responses to region strings.

## Control flow
If the client has an explicit region, lookup returns it immediately. Otherwise it checks the cache, signs and sends `GET ?location`, reads the response, parses either `LocationConstraint` or Huawei-style `CreateBucketConfiguration`, normalizes empty location to `us-east-1` and `EU` to `eu-west-1`, then caches the result.

## State and persistence behavior
State is a process-local `HashMap` protected by the `TransitionClient` mutex. It is invalidated by bucket deletion code and updated on successful/derived location lookup. No disk persistence exists.

## Dependencies and integration points
It depends on transition-client credentials/signing, `UNSIGNED_PAYLOAD`, error parsing, `rustfs_signer`, quick-xml, and S3 error code semantics. Request construction reuses the client's path-vs-virtual-host decision and user-agent helper.

## Risks and edge cases
Region signing is hard-coded to `us-east-1` for location requests. Virtual-host URL construction omits explicit port in the virtual-style branch. Some error cases convert `AccessDenied` or authorization-region errors into location guesses, which is useful for AWS-compatible behavior but may mask policy failures. The cache has no TTL.

## Test signals
No local tests are present. Important tests would cover cache hit/miss, EU/empty normalization, Huawei XML shape, NotImplemented special cases, AccessDenied region extraction, and signed request headers for V2/V4/anonymous credentials.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/bucket_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/checksum.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/checksum.rs

## Purpose
Defines checksum modes and helpers for S3 checksum headers, multipart composite checksums, and automatic checksum metadata injection for PUT/multipart completion.

## Important APIs, types, and functions
`ChecksumMode` is an `EnumSetType` with CRC32, CRC32C, SHA1, SHA256, CRC64NVME, none, and full-object flags. Methods include `key`, `raw_byte_len`, `hasher`, `encode_to_string`, `composite_checksum`, and `full_object_checksum`. `Checksum` stores raw checksum bytes and encodes them. `add_auto_checksum_headers` and `apply_auto_checksum` mutate `PutObjectOptions` metadata.

## Control flow
Mode methods map enum variants to S3 header names, raw byte lengths, and concrete `rustfs_checksums` implementations. Composite checksum sorts parts by part number, decodes each part checksum through `ObjectPart::checksum_raw`, concatenates raw part digests, hashes the concatenation, and stores the resulting digest. Full-object checksum currently delegates to the same composite logic for merge-capable CRC modes.

## State and persistence behavior
No global mutable state is kept beyond lazy enum masks. The functions mutate caller-provided `PutObjectOptions.user_metadata` and part slices. Resulting headers become persisted object metadata when remote PUT/complete calls succeed.

## Dependencies and integration points
It depends on `rustfs_checksums`, S3 checksum header constants, URL-safe base64 helpers, `PutObjectOptions`, and `ObjectPart`. It integrates with multipart upload completion and object PUT paths.

## Risks and edge cases
`full_object_requested` checks the masked base algorithm and currently returns true for CRC64NVME rather than an explicit `ChecksumFullObject` flag combination. Full-object CRC merge is not a true range-length-aware CRC combine; it delegates to composite checksum. Metadata replacement in `apply_auto_checksum` overwrites existing user metadata.

## Test signals
No tests are in this file. Indirect coverage comes from multipart/PUT callers. Direct tests should validate header names, base64 length checks, composite sort order, invalid/missing part checksum errors, and preservation or intentional replacement of metadata.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/checksum.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/constants.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/constants.rs

## Purpose
Centralizes transition-client constants for S3 multipart limits, signing payload markers, retry worker count, date formatting, and GetObjectAttributes defaults.

## Important APIs, types, and functions
Exports multipart sizing constants (`ABS_MIN_PART_SIZE`, `MIN_PART_SIZE`, `MAX_PART_SIZE`, `MAX_PARTS_COUNT`, `MAX_SINGLE_PUT_OBJECT_SIZE`, `MAX_MULTIPART_PUT_OBJECT_SIZE`), signing constants (`UNSIGNED_PAYLOAD`, `UNSIGNED_PAYLOAD_TRAILER`, `SIGN_V4_ALGORITHM`, `ISO8601_DATEFORMAT`), `TOTAL_WORKERS`, and GetObjectAttributes constants.

## Control flow
There is no runtime control flow beyond compile-time constant initialization of a `time` format description.

## State and persistence behavior
No state or persistence. Values are shared across request construction, signing, multipart validation, and attribute APIs.

## Dependencies and integration points
The constants are consumed by transition request signing, put/multipart code, and object attributes. It depends on the `time` format-description macro.

## Risks and edge cases
The module imports `lazy_static`, `HashMap`, and `Arc` without using them and has broad allow attributes. Limits should be kept aligned with S3 compatibility rules and any RustFS-specific multipart policy.

## Test signals
No tests are present. Coverage is normally through validation in multipart upload, put-object, and signing tests that assert expected thresholds and header values.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/constants.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/credentials.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/credentials.rs

## Purpose
Provides credential value/provider abstractions for the transition client, including static credentials, signer type selection, anonymous fallback, and STS XML error decoding helpers.

## Important APIs, types, and functions
`SignatureType` enumerates default, V4, V2, V4 streaming, and anonymous signing. `Credentials<P>` caches a `Value` from a `Provider`. `Value` holds access key, secret key, session token, expiration, and signer type. `Static` implements `Provider`. `STSError`, `ErrorResponse`, `xml_decoder`, and `xml_decode_and_body` support STS-style XML errors.

## Control flow
`Credentials::new` forces an initial refresh. `get_with_context` retrieves new credentials only when `force_refresh` or provider expiration says so, then caches the value. `Static::retrieve` returns anonymous credentials if access key or secret is empty. XML helpers convert bytes to UTF-8 and parse with quick-xml.

## State and persistence behavior
Credential cache state lives in the `Credentials` struct and is protected by `TransitionClient`'s mutex when used by HTTP request construction. Nothing is persisted to disk.

## Dependencies and integration points
The module is used by `TransitionClient`, bucket-location signing, and tests that construct static V4 clients. It depends on `time::OffsetDateTime`, `quick_xml`, serde deserialization, and standard IO error mapping.

## Risks and edge cases
`Provider::retrieve_with_cred_context` returns `Value` directly, so provider retrieval cannot report errors. `Value.expiration` is not checked by `Credentials`; expiration is delegated completely to the provider. `Static` treats either missing key component as anonymous, which can silently disable signing for partially configured credentials.

## Test signals
No local tests are present. Indirect tests create static credentials for signed HTTP requests. Useful direct tests would cover anonymous fallback, forced refresh, provider expiration, context propagation, and XML error decoding.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/credentials.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/mod.rs

## Purpose
Declares the `client` module surface for ecstore's S3/transition-client implementation.

## Important APIs, types, and functions
It publicly exposes modules for admin helpers, bucket policy, error response mapping, get/list/put APIs, multipart/streaming, remove/restore/stat APIs, bucket cache, checksum, constants, credentials, object utilities, common object handlers, signer errors, transition core, and header/base64 utilities.

## Control flow
There is no executable control flow. Compilation and visibility are the only effects: sibling modules become addressable as `crate::client::<module>`.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
This is the integration point for all client submodules. Other crate areas import from this namespace to reach transition operations, object helpers, credentials, and error types.

## Risks and edge cases
Because every listed submodule is public, internal helper modules become part of the crate-visible API surface. Renaming or removing entries has broad compile impact.

## Test signals
No direct tests are meaningful beyond successful crate compilation and downstream module tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/object_api_utils.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/object_api_utils.rs

## Purpose
Contains object API helper utilities for PUT readers, GET range reader construction, compressed-offset scaffolding, and ETag normalization.

## Important APIs, types, and functions
`PutObjReader` wraps `rustfs_rio::HashReader` and can expose the current MD5 checksum or replace the reader after encryption. `ObjReaderFn` is a closure type for creating `GetObjectReader`. `new_getobjectreader` maps requested ranges or part numbers to object-reader closures plus offset/length. `to_s3s_etag` and `get_raw_etag` normalize metadata ETags.

## Control flow
Part-number requests are converted to byte ranges by walking object parts and summing `actual_size`. Explicit range requests are validated through `HTTPRangeSpec::get_offset_length`; success returns a closure wrapping the input buffer into `GetObjectReader`. ETag conversion classifies weak `W/"..."`, quoted strong, and plain values.

## State and persistence behavior
No persistent state. Functions consume object metadata and return transient readers/ranges. ETag helpers interpret metadata maps without mutation.

## Dependencies and integration points
The module integrates store API types (`ObjectInfo`, `ObjectOptions`, `HTTPRangeSpec`, `GetObjectReader`), S3 DTO `ETag`, file metadata part info, and RustFS hash readers. It is used by object GET/PUT paths.

## Risks and edge cases
`new_getobjectreader` returns `InvalidRange` when no range/part number is supplied, so callers must handle full-object reads elsewhere. Compression and encryption paths are mostly placeholders. `part_number_to_rangespec` uses `i < part_number`, which treats part numbers as one-based but may include one extra part depending on caller expectations.

## Test signals
Local tests cover strong, weak, quoted, malformed, and empty ETag conversion, plus raw ETag extraction with `etag`, fallback `md5Sum`, and missing metadata.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/object_api_utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/object_handlers_common.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/object_handlers_common.rs

## Purpose
Provides shared object-handler logic for lifecycle cleanup of noncurrent object versions, including delete replication scheduling.

## Important APIs, types, and functions
`delete_object_versions` is the main exported async function. `lifecycle_version_delete_replication_state` builds `ReplicationState` with purge-target status derived from replication pending status.

## Control flow
The function first reads bucket versioning state. It processes input deletes in chunks capped by `MAX_DELETE_LIST`. For each object, it fetches object info and asks replication policy whether the delete should be replicated. It then calls `ECStore::delete_objects`; successful deleted objects with replication candidates receive replication state and are scheduled through `schedule_replication_delete`. Per-object failures are logged with lifecycle context.

## State and persistence behavior
Persistent object/version state is modified through `ECStore::delete_objects`. Replication state is attached to deleted-object records and handed to the replication scheduler. The module itself stores no local state.

## Dependencies and integration points
It integrates lifecycle events, bucket versioning system, replication decision/scheduling, `ECStore`, object options, file metadata replication state, and lock limits. It is a bridge between lifecycle expiration and replication subsystems.

## Risks and edge cases
If bucket versioning config or object info lookup fails, cleanup for affected items is skipped and only debug logged. Replication decisions are made before deletion; object state can change between lookup and delete. Error indexing assumes returned `deleted_objs` and `errors` align with the current batch.

## Test signals
A unit test verifies replication state preserves pending purge target maps and the original replicate decision string. Broader behavior requires integration tests around lifecycle deletion, versioning suspended/enabled states, and replication scheduling.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/object_handlers_common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/signer_error.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/signer_error.rs

## Purpose
Normalizes signer failures into IO errors while preserving invalid UTF-8 header names for detection by higher layers/tests.

## Important APIs, types, and functions
`SIGNER_HEADER_ERROR_MARKER` is an internal marker string. `invalid_utf8_header_error`, `signer_error_to_io_error`, and `error_chain_contains_signer_header_marker` are crate-visible helpers. `SignerHeaderError` is a private error type carrying scope and header name.

## Control flow
Invalid signer header values are converted into `ErrorKind::InvalidInput` with a structured source error. Other signer errors become generic `Error::other` messages. Detection walks an error chain, checks for `SignerHeaderError` by downcast, and falls back to marker-string matching.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
The module is used by transition request signing and bucket-location signing. It depends on `rustfs_signer::SignV4Error` and standard error chaining.

## Risks and edge cases
Marker-string fallback is intentionally redundant but means unrelated errors containing the marker text can be classified as signer header errors. Non-header signing errors lose structured type information when converted to string IO errors.

## Test signals
Unit tests verify direct invalid UTF-8 header errors and mapped signer header errors are detectable through the error chain, while unrelated IO errors are not.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/signer_error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/transition_api.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/transition_api.rs

## Purpose
Implements the core S3-compatible transition client: endpoint/TLS setup, credentials, request signing, retrying, URL construction, high-level object/list/multipart wrappers, and common object metadata DTOs.

## Important APIs, types, and functions
Core types are `TransitionClient`, `Options`, `BucketLookupType`, `ReaderImpl`, `RequestMetadata`, `TransitionCore`, `PutObjectPartOptions`, `ObjectInfo`, `RestoreInfo`, `ObjectMultipartInfo`, `UploadInfo`, `SendRequest`, `LocationConstraint`, and `CreateBucketConfiguration`. Key functions include `TransitionClient::new/private_new`, `build_tls_config`, `execute_method`, `new_request`, `doit`, `make_target_url`, `is_virtual_host_style_request`, `hash_materials`, `cred_context`, and `to_object_info`.

## Control flow
Client construction installs or reuses a rustls crypto provider, builds outbound TLS config from global RustFS TLS state, creates a Hyper client, initializes caches/flags/hash algorithms, and applies retry settings. `execute_method` checks offline state, builds signed requests in a retry loop, sends them through `doit`, accepts 200/204/206, parses error bodies, handles some region/cache updates, and retries retryable S3 codes or HTTP statuses. `new_request` resolves bucket location, builds path or virtual-host URL, obtains credentials, supports presigning, injects headers and payload hashes, signs V2/V4 requests, and attaches the body. `TransitionCore` exposes a smaller facade over list, put, multipart, bucket policy, abort, and get-object calls.

## State and persistence behavior
State is process-local: endpoint URL, credentials cache, bucket location cache, trace flags, accelerate/dual-stack flags, hash choices, health status atomics, retry count, and tier type. It does not persist locally; remote object-store state changes through delegated put/list/delete/multipart APIs.

## Dependencies and integration points
It integrates Hyper/Hyper-Rustls, rustls runtime state, RustFS retry utilities, signer crate, checksum modes, put/list/get/multipart modules, bucket location cache, S3 DTOs, UUID/time parsing, and error conversion.

## Risks and edge cases
`doit` converts non-success HTTP responses into generic IO errors, so `execute_method` may not receive structured non-2xx responses for its retry/error parsing. Auto virtual-host mode currently always returns false unless DNS mode is explicitly selected. URL path construction does not percent-encode object path segments. Several behaviors are placeholders or duplicated (`override_signer_type` assignment, tracing methods, health check). `to_object_info` uses simplified parsing for restore/expiration/tags/version IDs.

## Test signals
Unit tests cover rustls panic guarding, TLS config creation not panicking, idempotent provider install, invalid UTF-8 custom header reporting, and signer error mapping. Higher-level behavior is indirectly tested by delete request signing and other client modules.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/transition_api.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/utils.rs -->
# sources/object-store/rustfs/crates/ecstore/src/client/utils.rs

## Purpose
Supplies header/query classification helpers and base64 encoding/decoding utilities shared by the S3 client.

## Important APIs, types, and functions
Functions include `is_standard_query_value`, `is_storageclass_header`, `is_standard_header`, `is_sse_header`, `is_amz_header`, `is_rustfs_header`, `is_minio_header`, `base64_encode`, and `base64_decode`. Lazy maps define supported query keys, standard headers, and SSE headers.

## Control flow
Header checks lowercase keys and test membership/prefixes. `is_amz_header` accepts user metadata, grant headers, ACL, SSE headers, and checksum headers. Base64 helpers use `base64_simd::URL_SAFE_NO_PAD`.

## State and persistence behavior
The only state is lazy immutable lookup maps. No persistence.

## Dependencies and integration points
Used by checksum decoding, S3 datatype checksum handling, and likely request option/header filtering modules. Depends on `s3s` header constants and `base64_simd`.

## Risks and edge cases
`is_standard_query_value` indexes the map directly and will panic for unknown keys; other helpers use safe lookup. URL-safe no-pad base64 may be incompatible with standard AWS checksum/content-MD5 base64 expectations if used for wire headers.

## Test signals
No local tests are present. Direct tests should cover unknown query key behavior, case-insensitive header checks, SSE/amz prefixes, and base64 compatibility expectations.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/client/utils.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/compress.rs -->
# sources/object-store/rustfs/crates/ecstore/src/compress.rs

## Purpose
Decides whether an object should be disk-compressed based on process environment, object name, content type, content encoding, include filters, and hard-coded exclusion lists.

## Important APIs, types, and functions
Exports environment variable names, default extension/MIME include lists, strict excluded extensions/content types, `MIN_DISK_COMPRESSIBLE_SIZE`, `parse_added_exclude_extensions`, and `is_disk_compressible`. Internal helpers parse booleans/CSV values, normalize extensions, detect configured patterns, detect existing content encodings, and cache `DiskCompressionConfig` in a `OnceLock`.

## Control flow
On first use, environment variables are parsed once. `is_disk_compressible` returns false if compression is disabled, if content encoding is already meaningful other than `identity` or `aws-chunked`, if extension/content type is excluded, or if an added exclusion matches. If include filters are empty it compresses everything except exclusions; otherwise it requires either extension or MIME include match.

## State and persistence behavior
The process-global compression config is immutable after first use because of `OnceLock`. There is no disk persistence. The decision controls later object storage behavior but this module only computes eligibility.

## Dependencies and integration points
It uses RustFS string matching helpers and HTTP headers. It is expected to be consulted by PUT/storage code before deciding on at-rest compression.

## Risks and edge cases
Environment changes after first call are ignored. MIME matching depends on simple pattern utilities. Default includes contain `.tar` and `.bin`, while exclusions include tar MIME types but not `.tar` extension, so behavior depends on content type accuracy. Invalid `Content-Encoding` is treated as already encoded and therefore not compressible.

## Test signals
Unit tests cover enabled parsing, include parsing/defaults, broad excluded extensions and content types, positive text/json/html cases, content-encoding skip logic, added exclusion parsing/application, and empty include filters compressing all non-excluded objects.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/compress.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/audit.rs -->
# sources/object-store/rustfs/crates/ecstore/src/config/audit.rs

## Purpose
Defines default key/value configuration sets for RustFS audit log targets: webhook, MQTT, AMQP, NATS, Pulsar, Redis, Postgres, Kafka, and MySQL.

## Important APIs, types, and functions
Public `LazyLock<KVS>` statics include `DEFAULT_AUDIT_WEBHOOK_KVS`, `DEFAULT_AUDIT_MQTT_KVS`, `DEFAULT_AUDIT_AMQP_KVS`, `DEFAULT_AUDIT_NATS_KVS`, `DEFAULT_AUDIT_PULSAR_KVS`, `DEFAULT_AUDIT_REDIS_KVS`, `DEFAULT_AUDIT_POSTGRES_KVS`, `DEFAULT_AUDIT_KAFKA_KVS`, and `DEFAULT_AUDIT_MYSQL_KVS`. Each contains `KV` entries with key, default value, and `hidden_if_empty`.

## Control flow
There is no dynamic control flow beyond lazy initialization. Each target starts disabled and supplies endpoint/broker/table/topic credentials, TLS settings, queue directory/limit, retry or timeout settings, format settings, and comments as appropriate.

## State and persistence behavior
The statics provide immutable defaults used by configuration loading/merging. Actual persisted server configuration lives in the broader `rustfs_config` subsystem, not here. Sensitive fields are marked hidden when empty for config display behavior.

## Dependencies and integration points
This file depends heavily on audit/server config constants from `rustfs_config`, `KV/KVS`, `EnableState`, default limits, event queue directory defaults, and Redis default channel. It is an integration source for admin/config APIs that enumerate available audit targets and defaults.

## Risks and edge cases
There are apparent duplicated struct fields in the source around AMQP client cert and Postgres TLS required entries, which should be checked at compile time. Defaults vary in units (`Redis keep alive` is `"15"` while others use duration strings). Incorrect `hidden_if_empty` flags could expose secrets or hide useful settings.

## Test signals
No local tests are present. Good coverage would assert every default KVS contains `enable` and `comment`, sensitive fields are hidden, queue defaults are consistent, and each target-specific required key is present exactly once.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/config/audit.rs -->
