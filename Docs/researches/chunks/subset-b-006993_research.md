# sources/distributed-fs/ceph/src/rgw/rgw_op.cc lines 8205-10503

## Scope

This chunk covers a dense set of RGW operation implementations in `rgw_op.cc`. It begins in the tail of multi-object delete operation logging, then implements object deletion, Swift bulk delete/upload, internal attribute get/set/remove, bucket metadata search settings, generic handler permission initialization, bucket policy management, object-lock and retention/legal-hold management, bucket policy status and public-access-block management, bucket encryption and ownership-control management, static large object JSON decoding, and server-side decryption filter construction for GET/COPY read pipelines.

The chunk is operation-dispatch code rather than protocol rendering code. Most classes here expose protocol-neutral `execute()`, `verify_permission()`, `pre_exec()`, or helper methods, while S3/Swift REST subclasses in `rgw_rest*.h` supply request parsing and response serialization.

## Purpose

The main purpose is to bind authenticated RGW requests to persistent SAL operations and metadata attributes:

- `RGWDeleteMultiObj` parses an S3 multi-delete request, authorizes each target object/version, applies object-lock constraints, deletes objects concurrently, emits per-object results, and commits notifications/logging.
- `RGWBulkDelete` and `RGWBulkUploadOp` implement Swift-compatible bulk middleware behavior for deleting account paths and uploading TAR archives into buckets/objects.
- `RGWGetAttrs`, `RGWSetAttrs`, and `RGWRMAttrs` provide NFS/internal attribute read/write/delete primitives against objects or buckets.
- Bucket policy, public access block, encryption, ownership controls, object lock, bucket metadata search, retention, and legal-hold operations persist S3 control-plane settings into bucket info or bucket/object attributes.
- `RGWHandler` and `RGWOp` helpers initialize ACL/IAM policy state and produce common logging/error-handler behavior.
- `get_decrypt_filter()` constructs a read filter for encrypted objects, including multipart and AEAD range-handling details.

## Important APIs, Types, and Functions

### Multi-object delete

- `RGWDeleteMultiObj::write_ops_log_entry()` finalizes `rgw_log_entry::delete_multi_obj_meta`, counting successes/failures from `ops_log_entries` and moving the entries into the log.
- `RGWDeleteMultiObj::handle_individual_object()` is the per-object deletion path. It builds an `rgw_obj_key`, loads a SAL object handle, checks `s3DeleteObject` or `s3DeleteObjectVersion`, optionally loads object state for size/etag/object-lock attributes, reserves notifications, calls `Object::DeleteOp::delete_obj()`, logs bucket access, commits notifications, and sends a partial XML/JSON response through the virtual `send_partial_response()`.
- `RGWDeleteMultiObj::handle_objects()` converts parsed `RGWMultiDelObject` entries into `rgw::multi_delete::Item` records and dispatches them through `rgw::multi_delete::dispatch()`, with `bucket->versioned()`, `rgw_multi_obj_del_max_aio`, and `skip_update_olh` controlling concurrency and OLH update behavior.
- `RGWDeleteMultiObj::execute()` parses the request body with `RGWMultiDelXMLParser`, validates required `Delete/Object` elements, enforces `rgw_delete_multi_obj_max_num`, handles quiet mode and MFA-delete rules, begins the streaming response, then runs the deletion loop either in a new Boost.Asio coroutine or the supplied yield context.

### Swift bulk delete and upload

- `RGWBulkDelete::Deleter::verify_permission()` reads bucket ACL/policy and authorizes `s3DeleteBucket`; bulk delete is account-scoped and uses the request's global user ACL.
- `RGWBulkDelete::Deleter::delete_single()` loads a bucket in the caller tenant, authorizes it, then either deletes one object using `Object::DeleteOp` or deletes the whole bucket, forwarding bucket deletion to the metadata master when needed.
- `RGWBulkDelete::execute()` repeatedly calls virtual `get_data()` for up to `MAX_CHUNK_ENTRIES` style chunks until `is_truncated` is false, and delegates each chunk to `Deleter::delete_chunk()`.
- `RGWBulkUploadOp::parse_path()` splits Swift bulk paths into bucket plus optional object key, after skipping leading slashes.
- `RGWBulkUploadOp::handle_upload_path()` derives a bucket path and file prefix from URL bucket/object state, matching Swift `$UPLOAD_PATH` behavior.
- `RGWBulkUploadOp::handle_dir()` creates missing buckets, after quota/max-bucket checks, default ACL creation, placement selection, and metadata-master forwarding.
- `RGWBulkUploadOp::handle_file()` uploads a TAR regular file into an object. It checks size, loads the bucket, verifies `s3PutObject`, checks quota before and after streaming, creates version ids when needed, sets up an atomic SAL writer, optionally wraps it in `RGWPutObj_Compress`, streams body blocks through MD5 and filters, stores ETAG/ACL/compression attrs, and completes with `FLAG_LOG_OP`.
- `RGWBulkUploadOp::execute()` reads TAR blocks from a virtual `StreamGetter`, uses `rgw::tar::StatusIndicator` and `HeaderView` to detect headers/end-of-archive, dispatches normal files and directories, ignores unsupported TAR entry types, records per-entry failures, and terminates early on authorization errors listed in `terminal_errors`.
- `RGWBulkUploadOp::AlignedStreamGetter` ensures file bodies are consumed up to TAR block alignment even when the caller stops at the declared file length.

### Attribute and metadata-search operations

- `RGWGetAttrs::execute()` calls virtual `get_params()`, retrieves object attrs with `get_obj_attrs()`, and either returns requested keys or all attrs in a flat map.
- `RGWRMAttrs::execute()` deletes object attrs with `set_obj_attrs(nullptr, &attrs, FLAG_LOG_OP)`.
- `RGWSetAttrs::execute()` writes attrs to an object with `set_obj_attrs(&a, nullptr, FLAG_LOG_OP)` or merges bucket attrs with `Bucket::merge_and_store_attrs()`.
- `RGWConfigBucketMetaSearch::execute()` updates `RGWBucketInfo::mdsearch_config` and persists it with `Bucket::put_info()`.
- `RGWDelBucketMetaSearch::execute()` clears `mdsearch_config` and persists bucket info.

### Handler and response helpers

- `RGWHandler::do_init_permissions()` builds bucket policies with `rgw_build_bucket_policies()` and the IAM environment with `rgw_build_iam_environment()`.
- `RGWHandler::do_read_permissions()` loads object policies with `rgw_build_object_policies()` unless only bucket permission state is needed, translating `-ENODATA` to `-EACCES` and anonymous `-EACCES` to `-EPERM`.
- `RGWOp::error_handler()` delegates to the dialect handler; `RGWHandler::error_handler()` is the default pass-through.
- `RGWOp::gen_prefix()` appends dialect and operation name to request logging prefixes.
- `RGWDefaultResponseOp::send_response()` and bucket-policy/public-access delete response helpers map operation status into request-state errors and headers.

### Bucket policy and access-control settings

- `RGWPutBucketPolicy` reads the policy body, forwards to the metadata master, parses `rgw::IAM::Policy`, rejects public policies when `BlockPublicPolicy` is enabled, and persists `RGW_ATTR_IAM_POLICY` plus the optional remove-self-access marker through `retry_raced_bucket_write()`.
- `RGWGetBucketPolicy` reads `RGW_ATTR_IAM_POLICY` from bucket attrs and returns `-ERR_NO_SUCH_BUCKET_POLICY` for absent or empty policies.
- `RGWDeleteBucketPolicy` forwards to master and removes `RGW_ATTR_IAM_POLICY` and `RGW_ATTR_IAM_POLICY_REMOVE_SELF_ACCESS`.
- `RGWGetBucketPolicyStatus` reports whether the effective bucket policy or ACL is public.
- `RGWPutBucketPublicAccessBlock`, `RGWGetBucketPublicAccessBlock`, and `RGWDeleteBucketPublicAccessBlock` parse/decode `PublicAccessBlockConfiguration`, forward mutating calls to master, and persist or erase `RGW_ATTR_PUBLIC_ACCESS`.

### Object lock, retention, and legal hold

- `RGWPutBucketObjectLock` requires bucket versioning, parses `ObjectLockConfiguration`, validates retention periods, forwards to the metadata master, enables `BUCKET_OBJ_LOCK_ENABLED` if needed, and stores `RGWBucketInfo::obj_lock`.
- `RGWGetBucketObjectLock` returns `-ERR_NO_SUCH_OBJECT_LOCK_CONFIGURATION` when object lock is not enabled.
- `RGWPutObjRetention::verify_permission()` authorizes `s3PutObjectRetention`, reads params early, and separately checks `s3BypassGovernanceRetention` when bypass was requested.
- `RGWPutObjRetention::execute()` validates object-lock state, parses `Retention`, rejects past retain-until dates, compares against existing `RGW_ATTR_OBJECT_RETENTION`, enforces shortening/mode-change rules, journals bucket logging, and writes the encoded retention attr.
- `RGWGetObjRetention` loads and decodes `RGW_ATTR_OBJECT_RETENTION`, returning object-lock-style not-found errors for missing config.
- `RGWPutObjLegalHold` parses `LegalHold`, loads object attrs, journals logging, and writes `RGW_ATTR_OBJECT_LEGAL_HOLD`.
- `RGWGetObjLegalHold` loads and decodes `RGW_ATTR_OBJECT_LEGAL_HOLD`.

### Encryption and ownership controls

- `RGWPutBucketEncryption` parses `ServerSideEncryptionConfiguration`, forwards to master, encodes `RGWBucketEncryptionConfig`, and stores `RGW_ATTR_BUCKET_ENCRYPTION_POLICY`.
- `RGWGetBucketEncryption` decodes `RGW_ATTR_BUCKET_ENCRYPTION_POLICY`, returning `-ENOENT` and an S3-compatible message when absent.
- `RGWDeleteBucketEncryption` forwards to master and erases both `RGW_ATTR_BUCKET_ENCRYPTION_POLICY` and `RGW_ATTR_BUCKET_ENCRYPTION_KEY_ID`.
- `RGWPutBucketOwnershipControls` reads parsed ownership controls from its subclass, forwards to master, encodes them, and persists `RGW_ATTR_OWNERSHIP_CONTROLS`. For `BucketOwnerEnforced`, it decodes `RGW_ATTR_ACL` and rejects the update unless the bucket ACL matches the default private ACL.
- `RGWGetBucketOwnershipControls` decodes `RGW_ATTR_OWNERSHIP_CONTROLS`.
- `RGWDeleteBucketOwnershipControls` forwards to master and removes the ownership-controls attr.

### Decryption filter and SLO JSON

- `rgw_slo_entry::decode_json()` decodes static large object manifest entries: `path`, `etag`, and `size_bytes`.
- `get_decrypt_filter()` calls `rgw_s3_prepare_decrypt()` to construct a `BlockCrypt`. If encryption is not active it returns with a null filter. For encrypted objects it gathers multipart part numbers from `RGW_ATTR_CRYPT_PART_NUMS` or the requested `part_num`, gets encrypted part lengths from `RGW_ATTR_CRYPT_PARTS` or object manifest data, derives AEAD encrypted total size from part lengths or `CRYPT_ORIGINAL_SIZE`, detects compression, and returns an `RGWGetObj_BlockDecrypt` filter.

## Control Flow

Multi-object delete flows from whole-request validation into a streaming per-object loop. `execute()` rejects malformed XML, missing required elements, over-limit object counts, and MFA-delete failures before it emits any success response. After `begin_response()`, `handle_objects()` dispatches work through the multi-delete scheduler; each callback independently authorizes, checks object state, reserves notifications, deletes, logs, commits notifications, and emits a partial response. Final `op_ret` is set to zero because object-level errors have already been serialized into the response body.

Swift bulk upload is a TAR interpreter loop. `execute()` creates a protocol-specific stream, derives upload path prefixes, then repeatedly reads exact TAR blocks. Non-empty header blocks are interpreted; normal files create an `AlignedStreamGetter` over their body and call `handle_file()`, directories call `handle_dir()`, and other file types are skipped. Authorization terminal errors stop the entire bulk upload, matching Swift middleware behavior. The aligned getter destructor drains padding, so the next TAR header starts at the expected block boundary.

Control-plane bucket settings share a common shape: `verify_permission()` checks the IAM action, `get_params()` reads XML or subclass-parsed data, `execute()` decodes/validates, mutating requests forward to the metadata master, and persistence happens through `retry_raced_bucket_write()`, `merge_and_store_attrs()`, or `put_info()`. Read operations generally decode from `s->bucket_attrs` and set S3-compatible not-found errors when the attribute is absent.

Object-lock object operations are more stateful. Retention reads current object attrs, decodes existing retention if present, evaluates whether the request shortens retention or changes mode, and requires governance bypass both in the request and in authorization state. Retention and legal hold both load attrs for ETAG/size, write bucket-logging journal records, then mutate encoded object attrs.

`get_decrypt_filter()` is a constructor path in a larger read/copy pipeline. Its early exit is no encryption, while the non-trivial path gathers enough multipart, compression, and AEAD size metadata to instantiate a block decrypt filter that can transform subsequent object data correctly.

## State and Persistence Behavior

Persistent state touched in this chunk includes:

- Object data/index state through `Object::DeleteOp::delete_obj()` and bulk-upload `Writer::complete()`.
- Object attrs such as `RGW_ATTR_ETAG`, `RGW_ATTR_ACL`, `RGW_ATTR_COMPRESSION`, `RGW_ATTR_OBJECT_RETENTION`, and `RGW_ATTR_OBJECT_LEGAL_HOLD`.
- Bucket info fields such as `mdsearch_config`, object-lock flags, and `obj_lock`.
- Bucket attrs such as `RGW_ATTR_IAM_POLICY`, `RGW_ATTR_IAM_POLICY_REMOVE_SELF_ACCESS`, `RGW_ATTR_PUBLIC_ACCESS`, `RGW_ATTR_BUCKET_ENCRYPTION_POLICY`, `RGW_ATTR_BUCKET_ENCRYPTION_KEY_ID`, and `RGW_ATTR_OWNERSHIP_CONTROLS`.
- Bucket existence and bucket metadata from Swift bulk upload directory creation and bulk delete bucket removal.
- Notification reservations/commits for object deletion events.
- Bucket logging records for deletes, retention updates, legal hold updates, and bulk upload object writes.

Several operations are intentionally master-zone coordinated. Bucket creation, bucket deletion, bucket policy mutation, object-lock config mutation, public-access-block mutation, bucket encryption mutation, and ownership-controls mutation call `rgw_forward_request_to_master()` when required before local persistence. Metadata writes use `retry_raced_bucket_write()` where bucket attributes may race with other writers.

Read-only state paths include attr fetches, object-lock config existence checks, bucket policy status computation, bucket encryption/ownership/public-access decode operations, and decryption-filter setup from object attrs/manifests. Even read paths may load object state atomically to evaluate IAM tag conditions or object-lock checks.

## Dependencies and Integration Points

This chunk depends heavily on the RGW SAL interfaces:

- `rgw::sal::Driver` for bucket loading, notification creation, atomic writers, compression type, cluster stats, and master-zone checks.
- `rgw::sal::Bucket` for object handles, bucket info/attrs, quota checks, creation/removal, placement, versioning, and metadata persistence.
- `rgw::sal::Object` for state loading, attrs, delete ops, attr mutation, object identity, and version-instance handling.
- `rgw::sal::Writer` and `rgw::sal::DataProcessor` for bulk upload streaming and completion.

Authorization integrates with ACL and IAM helpers: `verify_bucket_permission()`, `verify_object_permission()`, `verify_*_no_policy()`, tag-condition helpers, `read_bucket_policy()`, `get_iam_policy_from_attr()`, root-owner exceptions, public-access-block policy evaluation, and object-lock governance bypass permissions.

Protocol integrations are provided by subclasses:

- S3 subclasses parse XML request bodies and serialize multi-delete, bucket policy, object-lock, public-access, encryption, ownership, retention, legal-hold, and attr responses.
- Swift subclasses provide bulk upload streams, bulk delete `get_data()`, and bulk result formatting.
- NFS/internal callers use the attr operations without S3/Swift equivalents.

Other dependencies include Boost.Asio coroutine spawning, `rgw::multi_delete::dispatch`, TAR parsing helpers under `rgw::tar`, compression plugins, MD5/ETAG helpers, XML and JSON decoders, `bufferlist` encoding/decoding, `retry_raced_bucket_write`, bucket logging, notification manager reservations, crypt helpers such as `rgw_s3_prepare_decrypt()`, and `RGWGetObj_BlockDecrypt`.

## Risks and Edge Cases

- `RGWDeleteMultiObj::execute()` begins streaming responses before all object deletes finish. After that point request-level failures cannot be represented as a normal top-level error; the code intentionally forces `op_ret = 0` and depends on per-object partial responses.
- Per-object multi-delete treats `-ENOENT` as success after `delete_obj()`, but object-lock checks may be skipped only when object state load returns `-ENOENT`. Versioned delete-marker behavior and OLH update skipping are therefore sensitive to SAL delete semantics.
- Notification reserve happens before deletion and commit happens only on successful deletion. Commit failure is logged but cannot roll back the delete.
- Bulk delete authorizes with `s3DeleteBucket` even when deleting an object path. This may be intentional for Swift bulk-delete account semantics, but it is broader than ordinary S3 object delete permission.
- `RGWBulkDelete::execute()` does not assign `op_ret` from `delete_chunk()` and loops while `!op_ret`; correctness depends on `get_data()` and response rendering using the `Deleter` failure counters rather than operation-level status.
- Bulk upload path parsing assumes callers only pass paths for which `parse_path()` succeeds; `handle_dir()` and `handle_file()` dereference the optional result directly.
- `handle_file()` logs `data.c_str()` at debug level 20 for body chunks, which can expose object content in high-verbosity logs and can be costly.
- Bulk upload uses MD5 as ETAG and notes that checksums are not supported. Checksum-related clients may observe weaker behavior than newer S3 PUT paths.
- Several bucket-attribute delete operations call `put_info()` on mutable `s->bucket->get_attrs()` while put operations often use copied attrs with `merge_and_store_attrs()`. Raced attr writes need coverage through `retry_raced_bucket_write()`.
- Object retention compares retain-until dates by `time_t`, which can lose sub-second precision. Retention mode strings are compared as literals such as `GOVERNANCE`.
- Retention and legal-hold mutations log journal records before modifying attrs. A later attr-write failure can leave a log record for an update that did not persist.
- Public-access-block delete verifies `s3PutBucketPublicAccessBlock` rather than a distinct delete action. This mirrors S3 IAM naming in some implementations but should be watched when IAM action coverage changes.
- `RGWPutBucketOwnershipControls` only validates the ACL when `RGW_ATTR_ACL` is present. Missing or undecodable ACL handling can affect BucketOwnerEnforced compatibility.
- Decryption filter setup continues after failure to decode `RGW_ATTR_CRYPT_PART_NUMS`, but fails on `RGW_ATTR_CRYPT_PARTS` decode errors. Multipart encrypted reads depend on these attrs and manifest data being internally consistent.
- AEAD encrypted size derivation intentionally skips compressed objects because compression changes encryption input. Range behavior for compressed encrypted objects relies on downstream decompression/filter size handling.

## Test and Validation Signals

Useful coverage for this chunk should include:

- S3 multi-delete tests for malformed XML, missing `Delete`/`Object`, object-count limits, quiet mode, MFA delete, empty keys, per-object permission denial, version-specific delete, object-lock denial, delete-marker creation, notification failures, and concurrent deletes with `rgw_multi_obj_del_max_aio`.
- Bucket logging and notification tests that distinguish delete success, delete `ENOENT`, logging failure, notification reserve failure, and notification commit failure.
- Swift bulk delete tests for bucket/object paths, missing buckets/objects, permission failures, master-zone forwarding for bucket delete, failure counters, and paginated `get_data()` chunks.
- Swift bulk upload tests for leading slashes, URL bucket/object prefixes, directory bucket creation, existing bucket handling, quota failure before and after streaming, max PUT size, versioned upload instance naming, compression attrs, TAR padding drain, unsupported TAR entry skip, and terminal auth error behavior.
- Attribute operation tests for requested-key filtering, all-attrs fetch, object vs bucket attr writes, delete attrs, permission failures, and `FLAG_LOG_OP` behavior.
- Bucket metadata search tests for owner-only access, config persistence, clear behavior, and attr refresh after `put_info()`.
- Bucket policy tests for root-owner shortcuts, remove-self-access marker handling, invalid principals, malformed policies, public-policy rejection under public-access-block, absent/empty policy reads, master forwarding, and raced writes.
- Object-lock tests for versioning-required bucket config, invalid retention periods, missing object-lock config, governance bypass permission/request combinations, retention shortening, compliance-to-governance rejection, legal-hold encode/decode, and corrupt attr decode errors.
- Public-access-block, encryption, and ownership-control tests for XML decode failures, absent attrs, corrupt attr decode, master forwarding, attr erasure, and BucketOwnerEnforced ACL validation.
- Decryption filter tests for unencrypted objects, single-part encrypted objects, multipart encrypted objects with `RGW_ATTR_CRYPT_PART_NUMS`, `GET ?partNumber=N` fallback, replicated-object `RGW_ATTR_CRYPT_PARTS`, manifest-derived part lengths, AEAD encrypted-size derivation, compressed encrypted objects, and decode-error handling.
- Multisite tests should verify that all mutating bucket-control operations either run on the metadata master or correctly forward request data and then persist returned master state locally.
