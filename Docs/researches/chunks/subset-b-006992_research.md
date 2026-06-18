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
