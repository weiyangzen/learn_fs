# Research Group subset-b-008165

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/bucket.rs -->
# sources/object-store/garage/src/api/s3/bucket.rs

## Purpose
Implements bucket-level S3 operations that are directly backed by Garage bucket/key metadata: bucket location, versioning stub, bucket ACL projection, list-buckets, create-bucket, and delete-bucket. It translates Garage's bucket alias and key permission model into AWS-shaped XML responses and mutates bucket/key alias tables through the locked helper layer.

## Important APIs, Types, And Functions
`handle_get_bucket_location` serializes the configured S3 region as `LocationConstraint`. `handle_get_bucket_versioning` returns an empty versioning configuration, signalling that full S3 versioning is not exposed here. `handle_get_bucket_acl` maps the current key's `BucketKeyPerm` into S3 grants using `create_grantee`. `handle_list_buckets` enumerates authorized bucket IDs from the key state, resolves active global aliases and key-local aliases, and returns `ListAllMyBucketsResult`. `handle_create_bucket` parses optional location XML, validates region and bucket name, then creates a `Bucket`, grants full permissions to the creator, and sets a local alias. `handle_delete_bucket` decides whether a delete removes only an alias or the bucket record itself. `parse_create_bucket_xml` is the XML helper covered by unit tests.

## Control Flow
Create bucket consumes the request body, rejects mismatched `LocationConstraint`, then takes `garage.locked_helper()` so alias and permission updates are serialized. It refetches the API key while locked, resolves any existing bucket name, returns AWS-compatible duplicate-bucket errors, validates creation permission and bucket naming, and writes bucket/key/alias state. Delete bucket also uses the locked helper. It detects whether the target name is a key-local alias, checks whether any other global or local aliases remain, and only performs true bucket deletion if this was the final alias and `is_bucket_empty` succeeds.

## State And Persistence
Persistent state lives in `bucket_table`, `bucket_alias_table`, and key-local alias/permission CRDT fields. Bucket creation inserts a new `Bucket`, writes key permissions with `BucketKeyPerm::ALL_PERMISSIONS`, and stores the bucket name as a local alias for the creator. Full deletion purges the alias, removes all authorized key permissions, and inserts a deleted bucket tombstone. Alias-only deletion updates either local or global alias state without deleting the underlying bucket.

## Dependencies And Integration Points
This module depends on `garage_model` bucket/key tables, `garage_table::util::EmptyKey`, CRDT `Deletable`, helper error mapping, and `crate::xml` S3 response types. It is called by the S3 request dispatcher after `ReqCtx` has resolved bucket, key, permissions, and bucket parameters.

## Risks And Test Signals
The main correctness risks are alias semantics, stale key permissions, and delete races around bucket emptiness. The locked helper lowers alias/permission race risk, but bucket emptiness is only as reliable as helper semantics. `parse_create_bucket_xml` has focused tests for empty, valid, region-bearing, and malformed XML. There are no direct tests here for alias deletion or list-bucket authorization filtering.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/bucket.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/copy.rs -->
# sources/object-store/garage/src/api/s3/copy.rs

## Purpose
Implements S3 `CopyObject` and `UploadPartCopy`. It reuses existing Garage object data whenever safe, or streams source object bytes through decrypt/checksum/encrypt/write paths when metadata, encryption, checksum, or range requirements demand a physical rewrite.

## Important APIs, Types, And Functions
`handle_copy` is the `CopyObject` entry point. It parses copy-source preconditions, checksum algorithm headers, source object metadata, source and destination encryption, metadata directive behavior, and then chooses `handle_copy_metaonly` or `handle_copy_reencrypt`. `handle_upload_part_copy` copies a byte range from a source object into an existing multipart upload part. `get_copy_source` resolves `x-amz-copy-source`, checks read permission on the source bucket, and fetches the source object. `extract_source_info` selects the latest complete non-delete source version metadata. `Defragmenter` coalesces block fragments during part-copy to avoid writing many tiny destination blocks.

## Control Flow
`CopyObject` first checks `x-amz-copy-source-*` preconditions against the selected source version. It unwraps source metadata with copy-source SSE-C headers and derives destination encryption from normal SSE-C headers. It identifies multipart-ish source data by ETag shape or checksum type. If encryption is unchanged and no checksum recomputation is required, the metadata-only path creates a new object version pointing to the same inline bytes or version blocks. Otherwise it builds a source byte stream via `full_object_byte_stream` and calls `save_stream`.

`UploadPartCopy` decodes the destination upload ID, fetches source object and destination MPU concurrently, validates source preconditions and SSE-C keys, parses `x-amz-copy-source-range`, rejects inline source objects as too small, loads source version blocks, computes affected block subranges, creates a placeholder MPU part and empty version, then streams source blocks through optional decryption, defragmentation, encryption, checksum calculation, block writes, version writes, and block-ref writes.

## State And Persistence
Metadata-only copies insert a new destination object version. For block-backed data they also insert a new `Version`, duplicate block entries, and insert new `BlockRef` rows without reuploading block contents. The code intentionally writes the final object after version/block refs to avoid same-source-destination races that could drop reference counts too early. `UploadPartCopy` updates `mpu_table` twice: once with an unfinished part placeholder and once with final ETag/checksum/size. It writes part blocks under a new `Version` with a `MultipartUpload` backlink.

## Dependencies And Integration Points
The module integrates with `get.rs` for preconditions and source streaming, `put.rs` for `save_stream` and metadata extraction, `multipart.rs` for upload lookup and upload-id decoding, `encryption.rs` for SSE-C handling, block/version/object/mpu tables, and checksum helpers from `garage_api_common`.

## Risks And Test Signals
Risks include subtle checksum type migration behavior, source/destination encryption equivalence, range boundary handling, and consistency if a part-copy fails after placeholder state is written. The `Defragmenter` can change block grouping, so checksum and offset accounting are key. Tests cover XML serialization of copy responses, but not persistence, block reuse, encrypted copy, or part-copy range behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/copy.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/cors.rs -->
# sources/object-store/garage/src/api/s3/cors.rs

## Purpose
Provides S3 bucket CORS configuration endpoints: get, put, and delete. It converts between Garage's stored CORS representation and the shared S3 XML CORS schema.

## Important APIs, Types, And Functions
`handle_get_cors` reads `bucket_params.cors_config` and serializes a `CorsConfiguration` XML document. `handle_put_cors` deserializes request XML with `quick_xml::de::from_reader`, validates it, converts it into Garage's internal CORS config, and stores it. `handle_delete_cors` clears the config.

## Control Flow
GET returns `NoSuchCORSConfiguration` when no config is present; otherwise it maps every stored rule through `CorsRule::from_garage_cors_rule`. PUT collects the whole body, deserializes and validates before mutating state, then writes a fresh `Bucket::present(bucket_id, bucket_params)` to the bucket table. DELETE updates the config CRDT to `None` and writes the bucket back.

## State And Persistence
The only persistent state is `bucket_params.cors_config`, stored through `garage.bucket_table.insert`. Updates preserve the rest of the bucket parameters by mutating the received `bucket_params` clone and reinserting a present bucket record.

## Dependencies And Integration Points
Depends on `garage_api_common::xml::cors` for XML shapes and validation, `garage_model::bucket_table::Bucket` for persistence, and `ReqCtx` for resolved bucket identity and parameters. Runtime CORS request evaluation is outside this file but consumes the same stored config.

## Risks And Test Signals
Primary risks are schema compatibility and whether `validate()` fully enforces AWS constraints. The module does not include local tests; coverage likely comes from shared XML CORS tests or integration tests. Error behavior is straightforward: missing config is an S3-specific not-found error, malformed XML becomes `MalformedXML`.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/cors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/delete.rs -->
# sources/object-store/garage/src/api/s3/delete.rs

## Purpose
Implements object deletion and multi-object deletion. Garage does not remove object data synchronously here; it appends a delete-marker object version so readers see the key as absent while background/version/block cleanup can proceed separately.

## Important APIs, Types, And Functions
`handle_delete_internal` performs the object-table mutation and returns the deleted version UUID and delete-marker UUID. `handle_delete` wraps it with S3 single-delete semantics, returning 204 even if the key did not exist. `handle_delete_objects` parses S3 delete XML, deletes each requested key independently, and returns `DeleteResult` entries unless quiet mode is enabled. `parse_delete_objects_xml` accepts formatted XML while rejecting non-whitespace stray text.

## Control Flow
Internal delete fetches the object from `object_table`, computes a monotonic timestamp with `next_timestamp`, generates a delete marker UUID, identifies the latest non-aborted version as the deleted version, and inserts a new object containing a complete `DeleteMarker` version. Multi-delete collects the body, parses XML using `roxmltree`, iterates objects, calls the same internal delete path, and accumulates per-key success or error XML.

## State And Persistence
Persistence is limited to `object_table.insert(Object::new(bucket_id, key, vec![delete_marker_version]))`. Existing version data, version table rows, block refs, and blocks are not modified here. Delete markers become part of object version history and are interpreted by GET/list filters elsewhere.

## Dependencies And Integration Points
Depends on the S3 object table types, `put::next_timestamp`, S3 XML response structs, and common helpers for body collection. It integrates with GET and LIST through `ObjectVersionState::Complete(ObjectVersionData::DeleteMarker)`, which those modules treat as missing data.

## Risks And Test Signals
Main risks are S3 compatibility for versioned deletion semantics and XML parsing strictness. `version_id` is accepted by the router but ignored by this implementation, so version-specific delete is not implemented here. Tests cover formatted XML, compact XML, quiet parsing, and rejection of non-whitespace text nodes.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/delete.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/encryption.rs -->
# sources/object-store/garage/src/api/s3/encryption.rs

## Purpose
Centralizes S3 SSE-C handling for object metadata, inline object bytes, streamed blocks, copy-source decryption, and response headers. It supports plaintext and customer-provided AES256 keys, with newer objects using an object-specific encryption key derived from bucket ID, version ID, object key, and the customer key.

## Important APIs, Types, And Functions
`EncryptionParams` is either `Plaintext` or `SseC { client_key, client_key_md5, object_key, compression_level }`. `new_from_headers` parses upload SSE-C headers. `check_decrypt` and `check_decrypt_for_copy_source` validate request keys against stored object encryption metadata and return decrypted metadata. `encrypt_meta`, `encrypt_blob`, `decrypt_blob`, `encrypt_block`, `decrypt_block_stream`, and `get_block` implement metadata/inline/block encryption and decryption. `has_encryption_header` helps PUT/MPU decide whether MD5 ETags can be computed from plaintext. `OekDerivationInfo::derive_oek` creates per-object keys.

## Control Flow
Header parsing requires algorithm `AES256`, a base64 32-byte key, and a matching base64 MD5. Missing companion headers or unknown algorithms become bad requests. For encrypted stored metadata, `check_decrypt_common` requires the matching SSE-C headers, constructs the right key form depending on `use_oek`, decrypts the serialized metadata blob, and decodes `ObjectVersionMetaInner`. Plaintext objects reject decryption headers.

Block encryption optionally zstd-compresses the plaintext block, prefixes a random stream nonce, and encrypts 4096-byte plaintext chunks with AES-GCM stream mode. Decryption reads the nonce, buffers enough bytes to distinguish final and non-final chunks, decrypts chunk-by-chunk, and optionally wraps the plaintext stream in a zstd decoder.

## State And Persistence
The module does not write tables directly, but it defines persisted metadata shape through `ObjectVersionEncryption::SseC { inner, compressed, use_oek }`. It also determines stored block bytes and block hashes because encrypted/compressed bytes are what get hashed and stored. ETags for encrypted objects are random 16-byte hex strings rather than MD5s.

## Dependencies And Integration Points
Used by PUT, GET, COPY, MULTIPART, LIST parts, and POST object. Depends on AES-GCM, HMAC-SHA256, base64, md5, zstd, `garage_block`, `garage_net::stream`, `block_manager`, and Garage object table metadata encoding.

## Risks And Test Signals
Risks are high because chunk sizing and nonce layout are durable formats. Constants explicitly warn not to change encrypted stream chunk size. Decryption returns IO errors on malformed streams, and copy logic only reuses blocks when both sides are plaintext because Garage v2 object keys differ per version. Tests cover block encryption/decryption round trips with and without compression; header parsing, metadata migration, and malformed encrypted stream cases are not locally tested.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/encryption.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/error.rs -->
# sources/object-store/garage/src/api/s3/error.rs

## Purpose
Defines the S3 API error type, conversions from lower-level errors, AWS error-code mapping, HTTP status mapping, response headers, and XML error body rendering.

## Important APIs, Types, And Functions
`Error` is the crate error enum. It wraps `CommonError` and adds S3-specific cases such as `NoSuchKey`, `NoSuchUpload`, CORS/lifecycle missing config, precondition failures, multipart part errors, malformed XML, invalid ranges, invalid encryption algorithms, and invalid checksums. `aws_code` maps variants to S3 error strings. The `ApiError` implementation provides `http_status_code`, `add_http_headers`, and `http_body`.

## Control Flow
Most handlers return `Result<Response<ResBody>, Error>`. Conversions normalize helper errors to internal errors by default, while `pass_helper_error` is re-exported for callers that want specific helper errors exposed. Signature errors are mapped into S3 errors without losing authorization-header detail. Invalid range errors carry the object length so `add_http_headers` can emit `Content-Range: bytes */len`.

## State And Persistence
No persistence. This file controls externally visible protocol state: status codes, XML body fields, CORS wildcard on error responses, and selected headers.

## Dependencies And Integration Points
Depends on `garage_api_common` common errors, generic server `ApiError`, signature errors, helper error mapping, Hyper status/header types, and S3 XML serialization. Every S3 handler relies on this type for `?` propagation.

## Risks And Test Signals
Risk is protocol compatibility: wrong AWS code/status pairs affect clients and SDK retries. XML serialization failure in an error path falls back to a static internal-error XML body. There are no local tests here; confidence depends on common-error tests and integration behavior. The duplicate comment for lifecycle/CORS missing config is harmless but signals copy-paste maintenance risk.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/get.rs -->
# sources/object-store/garage/src/api/s3/get.rs

## Purpose
Implements S3 GET and HEAD object reads, including metadata headers, conditional requests, range reads, partNumber reads, checksum response headers, SSE-C decryption, and streamed block responses.

## Important APIs, Types, And Functions
`handle_head` and `handle_get` are context-aware entry points; `handle_head_without_ctx` and `handle_get_without_ctx` are also used by website serving. `object_headers` builds S3 response headers from object version metadata and decrypted metadata. `GetObjectOverrides` represents response header overrides. `full_object_byte_stream` streams inline or block-backed data. `handle_get_range`, `handle_get_part`, `body_from_blocks_range`, and `calculate_part_bounds` implement partial reads. `PreconditionHeaders` parses and evaluates HTTP and copy-source preconditions.

## Control Flow
GET/HEAD fetch the object from `object_table`, choose the latest complete/data version, reject delete markers, extract `ObjectVersionMeta`, and call `EncryptionParams::check_decrypt` to validate SSE-C headers and get plaintext metadata. Conditional headers are evaluated before content handling. GET rejects simultaneous `partNumber` and `Range`. Full GET streams the whole object and applies response overrides. Range and part reads return 206 and intentionally skip override headers.

For block-backed full reads, the first block is fetched immediately while a task loads the version table and streams remaining blocks in order. Range reads load the version table, select intersecting blocks by true object offset, then slices chunks from decrypted block streams as they pass through.

## State And Persistence
This module is read-only. It reads `object_table`, `version_table`, and block data through `block_manager` via `EncryptionParams::get_block`. It treats `Version.deleted` as a transient internal consistency error rather than a missing key.

## Dependencies And Integration Points
Integrates with `copy.rs` by exporting `full_object_byte_stream`, `PreconditionHeaders`, and `check_version_not_deleted`. It depends on encryption, checksum helpers, Hyper headers, `http_range`, Garage object/version tables, and ordered block RPC tags.

## Risks And Test Signals
Important risks include partial stream error handling: a comment notes that sending an error stream item after bytes may still look successful in some client cases. Range handling assumes `all_blocks` is non-empty for block objects. Conditional request logic truncates timestamps to seconds to match HTTP date precision. There are no local tests in this file; precondition, range, and SSE-C behavior require integration coverage.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/get.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/lib.rs -->
# sources/object-store/garage/src/api/s3/lib.rs

## Purpose
Declares the S3 API crate/module surface. It wires tracing macros and exposes the modules that make up Garage's S3 server implementation.

## Important APIs, Types, And Functions
The file uses `#[macro_use] extern crate tracing;` and declares modules: public `api_server`, `error`, `cors`, `get`, `website`, and `xml`; private `bucket`, `copy`, `delete`, `lifecycle`, `list`, `multipart`, `post_object`, `put`, `encryption`, and `router`.

## Control Flow
No runtime control flow is defined here. Visibility controls which modules are reachable from outside the crate and which are intended only for internal dispatch.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
This is the integration root for the S3 API. Public exports indicate external consumers can use the server, error type, GET helpers, CORS/website handlers, and XML types. Private modules are still integrated internally by the API server and router.

## Risks And Test Signals
Risks are compile-time visibility and module coupling. Making modules private enforces routing through the crate's server path. There are no direct tests because behavior is entirely determined by submodules.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/lifecycle.rs -->
# sources/object-store/garage/src/api/s3/lifecycle.rs

## Purpose
Implements S3 bucket lifecycle configuration get, put, and delete endpoints. It persists lifecycle rules in bucket parameters and converts between Garage and S3 XML representations.

## Important APIs, Types, And Functions
`handle_get_lifecycle` reads stored lifecycle config and serializes `LifecycleConfiguration`. `handle_put_lifecycle` deserializes request XML, validates and converts it into Garage's lifecycle config, then stores it. `handle_delete_lifecycle` clears the config.

## Control Flow
GET returns `NoSuchLifecycleConfiguration` when no lifecycle config exists. PUT collects the request body, deserializes with `quick_xml`, calls `validate_into_garage_lifecycle_config`, rejects invalid rules as bad request, updates `bucket_params.lifecycle_config`, and writes the bucket. DELETE updates the same CRDT field to `None`.

## State And Persistence
State is `bucket_params.lifecycle_config` persisted by reinserting `Bucket::present(bucket_id, bucket_params)` into `bucket_table`. This file only manages configuration; lifecycle execution/expiration is elsewhere.

## Dependencies And Integration Points
Depends on shared XML lifecycle types in `garage_api_common::xml::lifecycle`, Garage bucket table persistence, and `ReqCtx`. It is dispatched by the S3 router and requires owner authorization according to router policy.

## Risks And Test Signals
Risks are validation completeness and compatibility with AWS lifecycle XML. No local tests exist in this file. Because lifecycle rules can delete or transition data elsewhere, accepting a malformed config would have broad downstream effects, so shared validation is the key dependency.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/lifecycle.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/list.rs -->
# sources/object-store/garage/src/api/s3/list.rs

## Purpose
Implements S3 listing APIs for objects, multipart uploads, and multipart upload parts. It handles V1/V2 object pagination, delimiter/common-prefix semantics, upload markers, URL encoding, and checksum visibility for encrypted multipart parts.

## Important APIs, Types, And Functions
Query structs are `ListQueryCommon`, `ListObjectsQuery`, `ListMultipartUploadsQuery`, and `ListPartsQuery`. Entry points are `handle_list`, `handle_list_multipart_upload`, and `handle_list_parts`. `fetch_list_entries` is the generic pagination loop over object-table ranges. `ObjectAccumulator` and `UploadAccumulator` implement `ExtractAccumulator`. `fetch_part_info` filters completed MPU parts and computes pagination. `RangeBegin` represents inclusive/exclusive cursor modes and upload-id cursor modes.

## Control Flow
Object and upload listing create a table range IO closure with different `ObjectFilter` values, build an accumulator, compute the starting cursor from query markers/tokens, and repeatedly call `get_range` with `page_size + 1`. The accumulator either extracts object entries, common prefixes, or uploads until full. Pagination returns the next marker/token depending on list version and whether the next cursor is inclusive or exclusive.

List parts decodes upload ID, loads the upload through `multipart::get_upload`, checks whether request headers can decrypt the upload metadata, filters completed parts, and emits checksum fields only when encryption is absent or decryption headers are valid.

## State And Persistence
Read-only. Reads `object_table` ranges and `mpu_table` state through `get_upload`. It relies on object version states to distinguish data objects from multipart upload markers and on MPU part CRDT ordering to select the latest completed part per part number.

## Dependencies And Integration Points
Depends on Garage object and MPU tables, `EnumerationOrder::Forward`, S3 XML list result types, URI encoding helpers, multipart upload decoding, encryption metadata validation, and checksum value representations.

## Risks And Test Signals
Listing compatibility is delicate. Risks include off-by-one pagination, inclusive token encoding, delimiter skipping via `key_after_prefix`, and lexicographic upload-id ordering. The code has substantial unit tests for common prefixes, upload extraction, pagination over synthetic ranges, and list-part pagination/filtering. It does not directly test object V2 continuation token round trips or encrypted checksum hiding.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/multipart.rs -->
# sources/object-store/garage/src/api/s3/multipart.rs

## Purpose
Implements multipart upload lifecycle: initiate, upload part, complete, abort, upload lookup, upload-id decoding, complete-body XML parsing, and multipart checksum aggregation.

## Important APIs, Types, And Functions
`handle_create_multipart_upload` creates an uploading object version and an `mpu_table` row. `handle_put_part` streams one part through the PUT block pipeline and records ETag/checksum/size in the MPU. `handle_complete_multipart_upload` validates requested parts, joins part versions into a final object version, calculates multipart ETag and optional checksums, enforces quotas, and finalizes object state. `handle_abort_multipart_upload` marks the uploading object version aborted. Helpers include `get_upload`, `decode_upload_id`, `parse_complete_multipart_upload_body`, `request_checksum_algorithm_and_type`, and `MultipartChecksummer`.

## Control Flow
Initiation generates an upload UUID, chooses a timestamp, extracts metadata, stores encryption metadata and checksum algorithm in an uploading `ObjectVersion`, inserts it into `object_table`, then creates a `MultipartUpload`. Upload-part decodes the upload ID, configures streaming checksums, gets the upload and first block concurrently, validates encryption headers, writes a placeholder part in `mpu_table`, creates a part `Version`, calls `read_and_put_blocks`, verifies stream checksums, and updates the MPU part with final metadata. Completion parses XML, verifies checksum type consistency, requires strictly increasing part numbers, matches requested ETags/checksums against stored completed parts, loads part versions, creates a final `Version` under the upload ID, inserts block refs, calculates final checksum/ETag, checks quotas, optionally rewrites encrypted metadata with final checksum info, and inserts the complete object version.

## State And Persistence
Uses `object_table` for upload markers, aborted markers, and final complete object versions; `mpu_table` for mutable part metadata; `version_table` for uploaded part block lists and final version block lists; `block_ref_table` for final object block references. `InterruptedCleanup` marks a part version deleted if upload-part fails after version creation.

## Dependencies And Integration Points
Depends on `put.rs` for metadata extraction, quotas, chunking, and block writes; `encryption.rs` for SSE-C validation; object/mpu/version/block-ref tables; checksum utilities; and XML response types. COPY part upload also depends on `get_upload` and `decode_upload_id`.

## Risks And Test Signals
Risks include partial failure cleanup, checksum algorithm/type compatibility, final part ordering and block part-number remapping, and quota rollback behavior. The complete path writes final `Version` and block refs before quota check; on quota failure it aborts the object marker but the final version/ref artifacts may remain for cleanup logic. Tests are absent for the full async persistence flow, but XML/checksum helpers have indirect coverage through list and shared checksum logic.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/multipart.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/post_object.rs -->
# sources/object-store/garage/src/api/s3/post_object.rs

## Purpose
Implements browser-based S3 POST object upload using multipart/form-data policies. It verifies the signed policy, validates form fields and content length constraints, then delegates object writing to the normal `save_stream` PUT path.

## Important APIs, Types, And Functions
`handle_post_object` is the entry point. `Policy`, `PolicyCondition`, `Conditions`, and `Operation` model the base64 JSON policy document. `StreamLimiter` enforces `content-length-range` while streaming the file. The function also handles `${filename}` substitution, CORS response headers, success redirects, and `success_action_status`.

## Control Flow
The handler extracts the multipart boundary, applies size constraints, reads form fields until the `file` part, and stores prior fields in a `HeaderMap` while rejecting duplicate names. It validates required `key` and `policy`, parses form authorization, substitutes filename if requested, verifies SigV4 over the policy, resolves the bucket, checks write permission, and computes matching CORS rule before upload. It decodes and validates policy expiration and conditions, consumes each provided form field against the allowed condition set, rejects missing required policy fields, extracts metadata/checksum/encryption settings, and streams the file through `save_stream` with checksum verification and length limiting.

## State And Persistence
Persistent object state is created entirely by `save_stream`: object table, version table, block refs, block storage, and quota checks. This file stores no policy state. It influences metadata headers, checksum metadata, object encryption, and response behavior.

## Dependencies And Integration Points
Depends on `multer` for multipart parsing, SigV4 form verification from `garage_api_common::signature::payload`, CORS helpers, shared checksum parsing, `put::save_stream`, and encryption derivation. It constructs a `ReqCtx` after policy authorization and bucket resolution.

## Risks And Test Signals
Risks include policy-condition parity with AWS, form field normalization, rejecting or accepting `x-ignore-*`, and streaming length enforcement only becoming final at EOF for undersized files. Success location construction assumes HTTPS when a host is present. Unit tests cover policy condition deserialization and normalization; they do not cover authorization, multipart parsing, CORS, upload persistence, or success responses.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/post_object.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/put.rs -->
# sources/object-store/garage/src/api/s3/put.rs

## Purpose
Implements S3 PutObject and the reusable object write pipeline used by normal PUT, POST object, multipart upload parts, and copy-rewrite paths. It chunks streams, computes/verifies checksums, encrypts data, writes blocks, records version/block references, enforces quotas, and finalizes object metadata.

## Important APIs, Types, And Functions
`handle_put` parses request metadata, checksums, trailer checksum algorithms, and SSE-C headers before calling `save_stream`. `save_stream` handles inline versus block-backed storage and returns `SaveStreamResult`. `check_quotas` enforces bucket object/byte limits. `read_and_put_blocks` is the streaming pipeline. `put_block_and_meta` writes one block plus version and block-ref metadata. `StreamChunker` creates block-sized chunks. `extract_metadata_headers` preserves standard headers, `x-amz-meta-*`, and validates `x-amz-website-redirect-location`. `next_timestamp` maintains monotonic object-version timestamps.

## Control Flow
`save_stream` reads the first block while fetching any existing object. If the first block is below `INLINE_THRESHOLD`, it finalizes checksums, checks quotas, encrypts inline bytes and metadata, and writes a complete inline object. Larger uploads write an uploading marker to `object_table`, create an empty `Version`, then call `read_and_put_blocks`. After streaming, checksums are verified or stored, quotas are checked, and the object marker is replaced with a complete `FirstBlock` version. `InterruptedCleanup` marks the object version aborted if a failure occurs before finalization.

`read_and_put_blocks` runs a four-stage pipeline: read chunks from client, hash plaintext for MD5/extra checksums, encrypt and BLAKE2-hash stored bytes, then write blocks with bounded concurrent storage-node RPCs while inserting `version_table` and `block_ref_table` records.

## State And Persistence
Small objects live fully in `object_table` inline data. Large objects use `object_table` for uploading/complete version state, `version_table` for block layout, `block_ref_table` for GC/reference tracking, and `block_manager` for actual block bytes. Bucket quota checks read `object_counter_table` and account for replacement diffs from previous object counts.

## Dependencies And Integration Points
Used by `multipart.rs`, `copy.rs`, and `post_object.rs`. Depends on Garage block manager, object/version/block-ref/counter tables, checksum receiver types, OpenTelemetry tracing, encryption, website redirect header constants, and API body helpers.

## Risks And Test Signals
Risks include partial writes leaving aborted markers or orphaned version/block metadata for repair, checksum interactions with encrypted ETags, trailer checksum timing, and quota checks after block upload for large objects. The concurrent pipeline depends on channel ordering and `FuturesOrdered`. No local unit tests are present; coverage must come from integration uploads, multipart, copy, and checksum tests.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/put.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/router.rs -->
# sources/object-store/garage/src/api/s3/router.rs

## Purpose
Maps HTTP method, bucket/key addressing, query parameters, and selected headers to typed S3 `Endpoint` variants, and assigns each endpoint an authorization class.

## Important APIs, Types, And Functions
`Endpoint` enumerates supported and stubbed S3 operations. `Endpoint::from_request` parses a request into `(Endpoint, Option<bucket>)`. Method-specific parsers `from_get`, `from_head`, `from_post`, `from_put`, and `from_delete` are generated with `router_match!`. `get_key` extracts object keys for key-based endpoints. `authorization_type` maps endpoints to `Authorization::{None, Read, Owner, Write}`. `generateQueryParameters!` declares recognized operation keywords and query fields.

## Control Flow
`from_request` handles root requests as `ListBuckets` or `Options`, derives bucket/key from either host-style bucket input or path-style URI, percent-decodes the key, parses query parameters, dispatches by HTTP method, warns when `x-id` does not match the parsed endpoint name, and logs unused query parameters. PUT routing gives copy operations precedence when `x-amz-copy-source` is present, distinguishing `CopyObject` from `UploadPartCopy` by `partNumber`.

## State And Persistence
No persistence. It creates the request classification that controls downstream authorization and handler selection.

## Dependencies And Integration Points
Depends on router macros from `garage_api_common`, Hyper request/header types, and the common `Authorization` enum. The API server consumes `Endpoint` to build `ReqCtx`, enforce permissions, and call the appropriate handler module.

## Risks And Test Signals
Risks are endpoint ambiguity, unsupported operations being parsed as typed variants but not implemented elsewhere, query parameter parsing mismatches, and authorization classification drift. The module has extensive tests based on AWS documentation examples, bucket/key extraction, percent decoding, invalid endpoints, copy header routing, upload-part-copy routing, and authorization type expectations. A commented failing plus-to-space case records an unresolved URL encoding question.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/router.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/api/s3/website.rs -->
# sources/object-store/garage/src/api/s3/website.rs

## Purpose
Implements S3 bucket website configuration get, put, and delete endpoints, and defines the `x-amz-website-redirect-location` object metadata header constant used by PUT/COPY.

## Important APIs, Types, And Functions
`X_AMZ_WEBSITE_REDIRECT_LOCATION` is the shared header name. `handle_get_website` serializes the stored Garage website config into `WebsiteConfiguration` XML. `handle_put_website` deserializes and validates XML then stores Garage website config. `handle_delete_website` clears it.

## Control Flow
GET returns an XML configuration when present. Unlike CORS/lifecycle, absence returns 204 No Content rather than an S3 missing-configuration error. PUT collects the body, deserializes with `quick_xml`, validates website config, converts it into Garage's internal representation, and writes the bucket. DELETE sets the config to `None` and writes the bucket.

## State And Persistence
State is `bucket_params.website_config`, persisted by inserting `Bucket::present(bucket_id, bucket_params)` into `bucket_table`. Object-level redirect metadata is not stored here, but the exported header constant is used by `put.rs` metadata extraction and `copy.rs` metadata-copy filtering.

## Dependencies And Integration Points
Depends on shared website XML types, Garage bucket table persistence, and `ReqCtx`. The website serving path uses this stored config together with GET/HEAD helpers to serve index/error behavior elsewhere.

## Risks And Test Signals
Risks are AWS compatibility for no-config GET behavior, validation completeness for routing rules, and consistency of redirect header semantics across PUT and COPY. No local tests are present in this file; validation is delegated to shared XML website code.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/api/s3/website.rs -->
