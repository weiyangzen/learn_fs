# Research: sources/distributed-fs/ceph/src/rgw/rgw_op.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006992`: lines 1-8204, `Docs/researches/chunks/subset-b-006992_research.md`
- `subset-b-006993`: lines 8205-10503, `Docs/researches/chunks/subset-b-006993_research.md`

## Chunk Research

### subset-b-006992: lines 1-8204

# sources/distributed-fs/ceph/src/rgw/rgw_op.cc lines 1-8204

## Scope

This chunk covers the first 8,204 lines of `rgw_op.cc`, the core implementation file for many RADOS Gateway request operations. It begins with includes, shared helper functions, and policy/environment setup, then implements object GET/HEAD, object tag operations, bucket tag/replication/versioning/website/list/location/create/delete operations, object PUT/POST/copy/delete/restore, Swift metadata operations, ACL/lifecycle/CORS/request-payment operations, multipart upload init/complete/abort/list operations, health checks, and the start of multi-object delete.

The range ends immediately after `RGWDeleteMultiObj::write_ops_log_entry()` starts, so the multi-object delete execution and later object-lock, public-access-block, encryption, ownership-control, handler, and response helpers live outside this chunk.

## Purpose

The purpose of this chunk is to translate initialized RGW request state (`req_state`) into concrete authorization checks, storage abstraction layer calls, metadata mutations, data streaming pipelines, notifications, logging, quotas, and multisite forwarding. It is the large operation body behind many S3 and Swift API verbs: it checks bucket/object ACL and IAM policy, builds IAM condition context, loads bucket/object metadata, dispatches reads/writes through `rgw::sal::Driver`, and updates persistent bucket/object/user/account state.

This file is not only a thin dispatcher. Several operations encode core request semantics here: range parsing, DLO/SLO traversal, CORS rule selection, cloud-tier restore/read-through behavior, AEAD encrypted object size accounting, copy-source authorization, object lock checks during delete, multipart checksum composition, multipart completion locking, bucket creation placement validation, and metadata-forwarding rules for multisite master zones.

## Important APIs, Types, and Functions

### Shared helpers and request setup

- `parse_aws_s3_error()` parses XML `<Error>` responses from a forwarded master-zone request and fills `rgw_err`.
- `rgw_forward_request_to_master()` forwards metadata-changing requests to the metadata master zone through `RGWRESTConn`, maps HTTP status to errno, optionally parses JSON output, and preserves S3 error code/message text.
- `RGWGetObj::parse_range()` parses `Range` headers, supports suffix ranges, sets `partial_content`, `ofs`, `end`, and `range_parsed`, and optionally ignores invalid ranges according to `rgw_ignore_get_invalid_range`.
- ACL helpers decode `RGW_ATTR_ACL` from user, bucket, or object attrs: `decode_policy()`, `get_user_policy_from_attr()`, `rgw_op_get_bucket_policy_from_attr()`, `get_obj_policy_from_attr()`, and `rgw_policy_from_attrset()`.
- Public access block helpers decode bucket/account `RGW_ATTR_PUBLIC_ACCESS` and merge account-level and bucket-level config in `read_public_access_conf()`.
- `read_bucket_policy()` and `read_obj_policy()` enforce suspended-bucket behavior, load ACLs and bucket IAM policy, and hide missing-object existence from callers without `s3:ListBucket`.
- `rgw_build_bucket_policies()` is the main bucket-state initializer. It parses system bucket-instance params, loads source and destination buckets, sets `s->bucket`, `s->object` bucket binding, bucket attrs, ACLs, owner, zonegroup endpoint/name, redirect endpoint, destination placement, public-access-block config, object-ownership mode, Swift account ACLs, and bucket IAM policy.
- `rgw_build_object_policies()` marks objects atomic, optionally prefetches object data, and reads object ACL/policy state.
- IAM condition helpers populate `s->env` for policy evaluation: object/bucket tags (`s3:ExistingObjectTag/*`, `s3:ResourceTag/*`), requested tags, ACL grant headers, encryption headers, current time, source IP, transport security, user agent, username, subuser, and STS flag.
- `RGWOp::verify_op_mask()` enforces the user op mask and blocks non-system modification requests in read-only zones.
- `RGWOp::do_aws4_auth_completion()` completes streaming AWS v4 auth validation, returning content SHA mismatch on failure.
- `RGWOp::init_quota()` loads bucket-owner user/account quotas and combines them with zone/default quota settings for modifying operations.

### Cloud tier, restore, and replication-status handling

- `handle_replication_status_header()` upgrades object replication status from `PENDING` to `COMPLETED` when `is_sync_completed()` says the object has synced, persisting `RGW_ATTR_OBJ_REPLICATION_STATUS`.
- `wait_for_restore_completion()` waits on a restore waiter and polls object attrs for cross-instance restore completion, failure, or timeout. It returns restore-state enum values or S3-style timeout/failure errors.
- `handle_cloudtier_obj()` decodes `RGW_ATTR_MANIFEST`, verifies cloud-S3 tier manifests, sets cloud-tier attrs for sync, starts restore jobs through `driver->get_rgwrestore()`, updates restore expiry, handles read-through restore waiting, and returns different status values for restore API vs read-through GET.

### Object GET, HEAD, DLO, SLO, and attributes

- `RGWGetObj::verify_permission()` handles ordinary GET, GET torrent, versioned GET, and replication GET. Replication requests require ACL/retention/legal-hold permissions and may require `s3:GetObjectVersionForReplication`, especially for SSE-KMS.
- `RGWGetObj::execute()` is the central GET/HEAD flow. It parses params, prepares a SAL read op, handles stat-only and auth-only requests, serves torrent metadata, chains optional Lua/Arrow Flight/decompression/decryption filters, repairs replication status, blocks duplicate replication trace destinations, invokes cloud-tier read-through, handles DLO/SLO manifests, computes AEAD plaintext sizes for ranges/content length, checks expiration, decodes tags, iterates object data through filters, and sends response/error data.
- `RGWGetObj::prefetch_data()` avoids prefetch for HEAD, auth-only requests, and range requests.
- `RGWGetObj::init_common()` parses range and conditional time headers.
- DLO support uses `iterate_user_manifest_parts()`, `RGWGetObj::handle_user_manifest()`, and `RGWGetObj::read_user_manifest_part()` to list segment objects by prefix, calculate total length and aggregate etag, re-check permissions for segment objects, optionally decompress/decrypt parts, and stream selected ranges.
- SLO support uses `RGWSLOInfo`, `rgw_slo_part`, `iterate_slo_parts()`, and `RGWGetObj::handle_slo_manifest()` to decode static manifest entries, load per-bucket ACL/policy, build an offset map, calculate aggregate etag, and read each selected part.
- `RGWGetObjAttrs` reuses `RGWGetObj::execute()` after requiring both `s3:GetObject` and `s3:GetObjectAttributes`-style permissions.

### Object tags, bucket tags, replication config

- `RGWGetObjTags`, `RGWPutObjTags`, and `RGWDeleteObjTags` read, set, or remove `RGW_ATTR_TAGS` on existing objects. Put/delete log journal records before mutating attrs. Tag-conflict `-ECANCELED` is translated to `-ERR_TAG_CONFLICT`.
- `RGWGetBucketTags`, `RGWPutBucketTags`, and `RGWDeleteBucketTags` read, set, or erase bucket `RGW_ATTR_TAGS`. Mutating paths forward to the master zone and use `retry_raced_bucket_write()`.
- `RGWGetBucketReplication`, `RGWPutBucketReplication`, and `RGWDeleteBucketReplication` expose and update bucket sync policy groups in `RGWBucketInfo::sync_policy`, also forwarding mutations to the master zone.

### Account and bucket operations

- `RGWListBuckets::execute()` lists buckets for an owner, optionally with stats, aggregates global and placement-policy stats, supports pagination/limits, skips anonymous listing, and streams response chunks.
- `RGWGetUsage::execute()` reads usage entries by date range, syncs user stats, loads bucket stats, and loads aggregate user stats.
- `RGWStatAccount::execute()` lists all buckets with stats and aggregates placement-policy/global totals.
- Bucket versioning, website, CORS, lifecycle, request-payment, and requester-pays operations mostly follow the pattern: add IAM condition context, verify bucket permission, parse request params, forward metadata changes to master, mutate bucket info/attrs under `retry_raced_bucket_write()` or service-specific helpers, and return read state in response members.
- `RGWListBucket::execute()` rejects indexless buckets, rejects unordered listing with delimiters, optionally reads stats, constructs `rgw::sal::Bucket::ListParams`, calls `bucket->list()`, and captures objects/common prefixes/truncation markers.
- `select_bucket_placement()` chooses requested, user-default, or zonegroup-default placement, validates zonegroup placement targets, and enforces user placement tags.
- `check_owner_max_buckets()` enforces account/user max-bucket limits by listing existing buckets.
- `RGWCreateBucket::execute()` validates location constraints and system `rgwx-zonegroup`, selects placement, prevents incompatible changes to existing buckets, handles Swift metadata update for existing Swift buckets, encodes ACL/CORS/object-ownership attrs, parses Swift quota/website metadata, forwards creation to the master if this zone is not the metadata master, adopts master-assigned bucket ids/markers, and calls `Bucket::create()`.
- `RGWDeleteBucket::execute()` checks ownership zonegroup, syncs owner stats, verifies emptiness for locally owned buckets, forwards delete to master, removes SSE-S3 bucket keys, removes the bucket, and tolerates `-ECANCELED` races as success.

### Object write, POST, copy, restore, metadata, and delete

- `RGWPutObj::init_processing()` parses copy-source bucket/object/version/range, loads copy-source bucket info/attrs, rejects malformed copy-source ranges, rejects blocked public canned ACLs, and parses PUT params.
- `RGWPutObj::verify_permission()` authorizes copy-source reads separately from destination writes, temporarily adds source object tags for source IAM policy evaluation, adds requested ACL/tag/encryption context, adds bucket tags, and verifies `s3:PutObject`.
- `RGWPutObj::execute()` handles ordinary PUT, multipart part PUT, append writes, and copy-source-range PUT. It performs MD5/checksum validation, quota checks before and after streaming, Swift versioning copy, notification reservation, writer selection, multipart upload info loading, append/versioned object handling, compression/encryption/torrent/Lua/checksum filter construction, streaming from request body or copy-source reads, AWS v4 completion, attr construction (`ETag`, ACL, DLO/SLO, replication status, checksum, user metadata, delete-at, tags, object lock attrs, AEAD original size), bucket logging, writer completion, standard logging, and notification commit.
- `RGWPutObj::get_data(fst,lst,bl)` reads copy-source ranges through decompress/decrypt filters and uses AEAD size correction before range validation.
- `RGWPostObj::execute()` processes browser/form POST uploads and Swift multi-file form post style loops. It reserves notifications, enforces min/max/quota, streams each file through encryption/compression/checksum filters, computes MD5 etag, fixes AEAD original size to file payload size rather than whole multipart form size, writes ACL/content-type/compression/checksum attrs, completes an atomic writer, and commits notification.
- Swift metadata operations include `RGWPutMetadataAccount`, `RGWPutMetadataBucket`, and `RGWPutMetadataObject`. They parse request metadata, preserve/remove custom attrs, filter temp URL keys, quota, website config, Swift versioning location, DLO manifest/delete-at attrs, and persist through user store, bucket metadata update, or object attr update.
- `RGWRestoreObj::execute()` reads object attrs and calls `handle_cloudtier_obj()` in restore mode, storing the restore-specific result for the response layer.
- `RGWDeleteObj::execute()` loads object state, enforces object lock and MFA delete where needed, supports Swift SLO multipart delete by bulk-deleting manifest entries, reserves notifications, performs Swift versioning restore if applicable, constructs and executes a SAL `DeleteOp` with versioning/precondition parameters, maps selected races/precondition errors to success, logs journal records, updates counters, and commits notifications.
- `RGWCopyObjDPF` is a copy data-processor factory that builds source decrypt/decompress filters and destination encrypt/compress filters when copy must stream data, computes final plaintext size for compressed/encrypted sources, strips stale compression attrs, and repairs AEAD original-size/parts attrs.
- `RGWCopyObj::execute()` loads source state, rejects cloud-tier transitioned sources, checks max PUT size and quota, handles Swift versioning, logs journal records, invokes `src_object->copy_object()` with `RGWCopyObjDPF`, optionally sends progress responses, logs standard GET side of copy, commits notifications, and updates counters.

### ACL, lifecycle, CORS, and request payment

- `RGWGetACLs` returns bucket or object ACL XML after checking `Get*Acl` permission.
- `RGWPutACLs` rejects ACL writes under bucket-owner-enforced ownership, parses canned/header/XML ACLs, prevents owner changes except equivalent requester identities, caps grant count, forwards bucket ACL writes to master, rejects public ACLs under public-access-block, logs object ACL changes, and persists `RGW_ATTR_ACL` to object or bucket attrs.
- `RGWPutLC` rejects indexless buckets, optionally verifies Content-MD5, parses and rebuilds S3 lifecycle XML, forwards to master, and persists via `driver->get_rgwlc()->set_bucket_config()`. `RGWDeleteLC` forwards and removes lifecycle config/list membership.
- CORS read/write/delete/options functions decode bucket CORS attrs, build global CORS from config, select matching origin/method/header rules, emit response parameters, forward mutations, and update or erase `RGW_ATTR_CORS`.
- `RGWSetRequestPayment` forwards requester-pays changes to master and updates `RGWBucketInfo::requester_pays`.

### Multipart upload

- `RGWInitMultipart::execute()` starts an RGW tracing span, parses params, encodes trace/ACL/generic metadata, prepares encryption attrs, stores request metadata and object tags, stores object retention/legal-hold/checksum settings on the upload object, initializes the multipart upload, and returns the upload id.
- `try_sum_part_cksums()` lists uploaded parts, validates every part has the expected checksum type, combines part checksums with `rgw::cksum::CombinerFactory()`, and returns both encoded and armored multipart checksum values, adding a part-count suffix for composite checksums.
- `RGWCompleteMultipart::execute()` parses the complete XML, validates part count, loads upload info, locks the multipart meta object with a serializer, handles idempotent retry by comparing recalculated etag against an existing object when the meta object is gone, loads meta attrs/trace context, computes and validates checksums, prepares target attrs, reserves notifications, logs journal records, verifies lock renewal, calls `upload->complete()` to assemble the final object, logs standard records, deletes the meta object with cls version checks, retries cleanup for parts racing with completion, commits notifications, and leaves lock release to `complete()`.
- `RGWCompleteMultipart::check_previously_completed()` recalculates multipart etag from the requested parts and compares it with the existing object; if checksum attrs exist, it decodes and reconstructs the armored checksum response value.
- `RGWAbortMultipart::execute()` locks the meta object with the same serializer namespace, extracts trace context, aborts the upload, and unlocks.
- `RGWListMultipart::execute()` loads upload info, decodes upload ACL/checksum attrs, and lists parts.
- `RGWListBucketMultiparts::execute()` supports Swift `path` handling and lists active multipart uploads with common prefixes and next markers.

## Control Flow

Most operations follow a common RGW lifecycle:

1. `init_processing()` parses request-specific params and sometimes performs early state loads.
2. `verify_permission()` populates IAM condition keys, loads tag context when a policy needs it, and calls bucket/object/user permission helpers.
3. `pre_exec()` emits `100-continue` and dumps bucket state through `rgw_bucket_object_pre_exec()`.
4. `execute()` mutates or reads SAL state, sets `op_ret`, response fields, attrs, version ids, etags, and counters.
5. Response methods outside this chunk serialize the fields populated here.

The chunk has several deeper pipelines:

- GET prepares a read op, builds response filters in reverse execution order, reconciles cloud-tier/manifest/range/AEAD state, then iterates data through SAL and filters.
- PUT/POST build writer/data-processor filters in reverse execution order, stream request/copy-source data into the writer, flush filters, validate auth/checksums/quota, build attrs, then call writer `complete()`.
- COPY delegates the copy itself to SAL but supplies `RGWCopyObjDPF` so the backend can either do server-side copy or stream through transform filters when encryption/compression requires it.
- Multipart complete serializes on the upload meta object, computes final metadata, commits parts to the destination object, then cleans upload metadata and late racing parts.
- Bucket metadata mutations usually forward first to the metadata master zone, then update local bucket info/attrs with raced-write retry.

## State and Persistence Behavior

This chunk reads and writes persistent RGW state extensively:

- Bucket metadata attrs: ACL, tags, CORS, lifecycle, website config, quota, Swift versioning, requester-pays, public-access-block-derived behavior, ownership controls at create time, and replication sync policy.
- Bucket info fields: versioning flags, MFA flag, website flags/config, sync policy, requester-pays, placement/layout, quota, owner, object lock setting, zonegroup, creation metadata, and Swift versioning location.
- Object attrs: ACL, etag, content type, user metadata, object tags, compression metadata, torrent metadata, checksums, DLO/SLO manifests, delete-at, object retention/legal hold, encryption metadata including AEAD original size, replication status, restore status, trace context, and cloud-tier metadata.
- Object data/head state: PUT/POST/COPY complete writers create or overwrite objects; DELETE creates delete markers or deletes versions according to bucket versioning; Swift versioning may copy or restore prior object versions.
- Multipart state: init creates upload metadata; part PUT writes part objects; complete writes final object, removes upload meta object, and cleans orphaned late parts; abort deletes upload state.
- User/account metadata: Swift account metadata/temp URL/quota updates store user attrs/info.
- Logs and side effects: bucket logging journal/standard records, notification reserve/commit calls, op counters, trace spans, restore waiter registrations, and replication-status attr repair.
- Multisite state: many bucket metadata mutations are forwarded to the master zone before local persistence, and object replication status/trace attrs influence sync behavior.

Some nominal reads can mutate state. GET may update replication status or start/wait for cloud restore. COPY may log and write destination attrs. DELETE may restore a Swift previous version instead of deleting. ACL/tag writes log journal records before attr mutation.

## Dependencies and Integration Points

- SAL interfaces are the primary backend contract: `rgw::sal::Driver`, `Bucket`, `Object`, `Object::ReadOp`, `Object::DeleteOp`, `Writer`, `MultipartUpload`, `Notification`, `DataProcessor`, `PlacementTier`, and services such as lifecycle and restore.
- Request/context types include `req_state`, `req_info`, `DoutPrefixProvider`, `optional_yield`, `RGWAccessControlPolicy`, `rgw_owner`, `ACLOwner`, `RGWBucketInfo`, `rgw_bucket`, `rgw_obj_key`, and `RGWObjVersionTracker`.
- IAM and ACL integration uses `rgw::IAM::Policy`, `ARN`, action enums, session and identity policies, bucket/object ACLs, public access block, object ownership, canned ACLs, and S3 condition keys.
- Multisite integration uses `rgw::SiteConfig`, periods, zonegroups, zone params, master-zone forwarding through `RGWRESTConn`, bucket sync policy, object replication status, and redirect endpoints.
- Encryption/compression/checksum pipelines integrate `rgw_crypt`, `BlockCrypt`, `RGWPutObj_BlockEncrypt`, `get_decrypt_filter()`, `Compressor`, `RGWPutObj_Compress`, `RGWGetObj_Decompress`, `RGWCompressionInfo`, and `rgw::cksum` helpers.
- Optional feature integration appears behind build/runtime gates: D4N cache filters, Arrow Flight GET filter, Lua get/put data filters, torrent generation, and LTTNG tracepoints.
- Swift compatibility surfaces are DLO/SLO manifests, account ACLs, temp URL keys, Swift object/bucket/account metadata, form POST multi-file behavior, Swift versioning copy/restore, and multipart/SLO delete behavior.
- Logging/notification integration uses `rgw::bucketlogging::log_record()`, `driver->get_notification()`, notification event types, `rgw::op_counters`, and OpenTelemetry-style RGW trace spans.

## Risks

- The file concentrates many independent S3/Swift semantics in long methods. `RGWGetObj::execute()`, `RGWPutObj::execute()`, `RGWCopyObj::execute()`, and `RGWCompleteMultipart::execute()` are especially high risk because range handling, attrs, filters, logging, notification, quota, versioning, and error paths share one control flow.
- Filter order is subtle. GET wants decrypt/decompress/Lua/response ordering, PUT wants checksum/Lua/torrent/compress/encrypt/writer ordering, and COPY builds both read and write chains. Reordering can corrupt data, break checksum validation, or expose encrypted/compressed bytes.
- AEAD size handling is duplicated across GET, PUT, POST, copy-source range reads, and copy object. Missing `RGW_ATTR_CRYPT_ORIGINAL_SIZE` or stale crypt part attrs can produce wrong content length, bucket index size, or range validation.
- IAM tag condition handling mutates `s->env` and sometimes removes source tags after temporary source authorization. Missing removal or wrong object/bucket tag source can leak condition keys between source and destination permission checks.
- Master-zone forwarding must happen before local metadata mutation for multisite consistency. Any unforwarded bucket metadata update can diverge zones; any forwarding with wrong owner/effective identity can fail or apply under the wrong authority.
- Missing-object error mapping in `read_obj_policy()` intentionally hides object existence unless the caller has list permission. Callers must preserve this behavior to avoid information leaks.
- Bucket-owner-enforced ACLs, public-access-block rejection, object lock, governance bypass, MFA delete, requester-pays, and versioning flags are policy-sensitive; regressions here can violate S3 compatibility or retention guarantees.
- Multipart completion is race-prone: lock acquisition, idempotent retry, late part uploads, checksum list truncation, meta object deletion with version checks, and orphan cleanup all need to stay coordinated.
- Cloud-tier GET/restore reads can start asynchronous restore and wait with timeout/polling. Incorrect status mapping can turn restore-in-progress into the wrong S3 error or block request threads too long.
- DLO/SLO handling revalidates segment permissions and computes aggregate lengths/etags. Off-by-one range errors or segment size mismatches can corrupt partial responses.
- Several error paths happen after durable writes or notification reservations. Later notification/logging failure is often intentionally not rolled back; tests need to assert the chosen durability semantics.

## Test and Validation Signals

Useful validation should cover:

- GET/HEAD ranges, invalid range ignore mode, conditional headers, zero-size objects, expired objects, DLO/SLO full and ranged reads, torrent rejection for SSE-C, cloud-tier read-through success/timeout/failure, replication trace `NotModified`, and AEAD encrypted/compressed content lengths.
- PUT/POST object writes with content MD5, flexible checksums, chunked upload, copy-source and copy-source-range, append writes, object tags, user metadata, DLO/SLO manifests, delete-at, object lock attrs, SSE-C/SSE-S3/SSE-KMS, compression, Lua filters, torrent attrs, quota failure before and after streaming, and notification/logging side effects.
- COPY across metadata-directive cases, encrypted/compressed source and destination combinations, cloud-tier transitioned source rejection, source permission denial vs destination permission denial, progress callback behavior, versioned destination ids, and AEAD attr repair.
- DELETE for ordinary object, versioned object, delete marker creation, null version, MFA delete, object lock governance/compliance, bypass governance permission, Swift version restore, SLO multipart delete, precondition success/failure/no-precondition-error, and notification/logging behavior.
- Bucket operations for create existing-bucket compatibility, location constraint enforcement with and without periods, remote/system zonegroup creation, placement target/tag denial, max-bucket limits, versioning/MFA transitions, object-lock versioning constraints, indexless list/lifecycle rejection, website/CORS/request-payment/tag/replication mutations, bucket delete empty checks, and SSE-S3 bucket-key cleanup.
- ACL and public-access-block tests for canned/header/XML ACL parsing, grant-count limits, bucket-owner-enforced rejection, owner-change rejection, public ACL denial, bucket ACL master forwarding, object ACL journal logging, and race `-ECANCELED` handling.
- Lifecycle and CORS tests for malformed XML, optional Content-MD5 validation, global CORS fallback, method/header/origin mismatch, and delete of missing CORS.
- Multipart tests for init metadata/encryption/tags/checksum settings, part upload through `RGWPutObj`, complete XML variants, too many parts, checksum type mismatch/missing part checksum, supplied multipart checksum with and without suffix, idempotent complete after meta deletion, concurrent complete lock contention, abort lock behavior, late part cleanup retries, and list parts/uploads pagination.
- Multisite tests for all forwarded metadata mutations, non-master zone behavior, forwarded S3 error parsing, JSON parsing for create bucket master info, and redirect behavior for bucket zonegroup mismatch.
- Build/runtime matrix checks for D4N, Arrow Flight, Lua data filters, torrent enabled/disabled, RADOS restore services, and tracing enabled/disabled paths.

### subset-b-006993: lines 8205-10503

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
