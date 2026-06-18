# Research: subset-b-006985

Grouped research for Ceph RGW files under `sources/distributed-fs/ceph/src/rgw`. Each section is source-tree-aligned and intended to be split into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.h

Purpose: declares S3 authentication strategy composition plus SigV2/SigV4 canonicalization and streaming payload completion helpers for RGW. It is the public interface between REST S3 request handling, auth engines, and body readers that must verify SigV4 payload integrity.

Important APIs/types/functions: `STSAuthStrategy`, `ExternalAuthStrategy`, and templated `AWSAuthStrategy<AbstractorT, AllowAnonAccessT>` assemble auth engines and `IdentityApplier` factories. `AWSv4ComplMulti` and `AWSv4ComplSingle` implement `rgw::auth::Completer` and decorate `rgw::io::RestfulClient` body reads. Helpers include `rgw_create_s3_canonical_header()`, `parse_v4_credentials()`, `gen_v4_scope()`, URI encoding/recode helpers, payload-hash classifiers, canonical query/header builders, `get_v4_canon_req_hash()`, `get_v4_string_to_sign()`, `get_v4_signature()`, `get_v2_signature()`, and `get_aws_version_and_auth_type()`.

Control flow: `AWSAuthStrategy` optionally installs anonymous auth, parses `rgw_s3_auth_order`, filters configured STS/external/local engines, and adds the last engine as `FALLBACK` when multiple engines exist. `AWSv4ComplMulti` tracks chunk metadata, stream position, previous chunk signature, optional trailers, and SHA256 state as body bytes are received. `AWSv4ComplSingle` streams a body hash and compares it against the expected `x-amz-content-sha256` value in `complete()`.

State/persistence: no durable state is written here, but request state is modified by completers; `AWSv4ComplMulti::put_prop()` mutates the CGI/env map to surface validated trailer headers. The auth strategies retain pointers/references to `CephContext`, SAL driver, implicit tenant context, and auth engines.

Dependencies/integration: depends on `rgw_auth`, `rgw_auth_filters`, Keystone/LDAP auth, `rgw_rest_s3`, request env maps, Ceph crypto SHA256, and S3 canonicalization utilities. REST S3 operations call these declarations through auth engines and completers.

Risks: signature correctness is sensitive to URI recoding, plus-to-space behavior, missing `x-amz-content-sha256`, auth engine ordering, and chunk/trailer boundary parsing. `parse_auth_order()` silently falls back to default on unknown names. Streaming unsigned/trailer variants must stay aligned with AWS semantics.

Test signals: cover SigV2/SigV4 canonical strings, presigned URLs, reordered auth engine config, STS/external/local fallback, empty/unsigned/streaming/trailer payload modes, chunk signature mismatch, malformed chunk metadata, and trailer checksum propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_b64.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_b64.h

Purpose: header-only Base64 encode/decode helpers in namespace `rgw`, used by checksum and metadata code that needs compact textual binary representations.

Important APIs/types/functions: `to_base64<wrap_width>(std::string_view)` uses Boost archive iterator adaptors and optional MIME line wrapping; `from_base64(std::string_view)` removes whitespace and decodes Base64 input after stripping trailing padding.

Control flow: encoding pads the input length to a multiple of three for `=` suffix emission, runs `transform_width` plus `base64_from_binary`, then appends padding. Decoding returns an empty string for empty input, removes all trailing `=`, filters whitespace, then runs `binary_from_base64` and `transform_width`.

State/persistence: stateless, no persistence, no global mutable state.

Dependencies/integration: depends on Boost archive iterator adaptors and is used by `rgw_cksum.h` for checksum text rendering.

Risks: malformed Base64 input can throw through Boost iterators; callers do not get an error-code API. `to_base64()` comments say pad to multiple of three for output, but Base64 output length is conventionally multiple of four, so edge cases deserve regression tests. `from_base64()` assumes padding only appears at the end.

Test signals: round-trip empty, one-byte, two-byte, three-byte, long wrapped MIME strings, whitespace in input, invalid characters, and checksum-specific binary payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_b64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_basic_types.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_basic_types.cc

Purpose: implements JSON/XML conversion, bucket conversion/key formatting, shard encoding, principal formatting, account-id JSON handling, and owner variant parsing for fundamental RGW serialized types.

Important APIs/types/functions: `decode_json_obj(rgw_user&)`, `encode_json/encode_xml(rgw_user)`, `rgw_bucket::rgw_bucket(const rgw_user&, const cls_user_bucket&)`, `rgw_bucket::convert()`, `rgw_bucket::get_key()`, `rgw_bucket_shard::get_key()`, `encode/decode(rgw_bucket_shard)`, `encode_json_impl/decode_json_obj(rgw_zone_id)`, `rgw_data_placement_target::dump/decode_json()`, `rgw_bucket::dump/decode_json()`, `operator<<(Principal)`, `parse_owner()`, `to_string(rgw_owner)`, and JSON encode/decode for `rgw_owner`.

Control flow: bucket keys are assembled conditionally from tenant, bucket name, bucket id, and delimiters. Bucket JSON decode supports old placement fields by falling back to `pool`, `data_extra_pool`, and `index_pool` if `explicit_placement.data_pool` was absent. `parse_owner()` chooses account id when `rgw::account::validate_id()` succeeds, otherwise treats input as `rgw_user`.

State/persistence: these functions define persisted textual and binary-visible identifiers. `rgw_bucket_shard` binary encoding stores bucket then shard id. JSON conversion is used in admin/config/reporting surfaces.

Dependencies/integration: integrates with cls user bucket structures, `rgw_account`, XML/JSON helpers, pool/placement types, and IAM principal display.

Risks: bucket key delimiter choices are protocol-sensitive; tenant/name/id ambiguity can break metadata lookup. Principal streaming prints Role and AssumedRole both as `role/` style except service/wildcard/account special cases. Owner parsing depends on account-id validation staying stricter than user ids.

Test signals: encode/decode round-trips, legacy bucket JSON placement decode, tenant and empty bucket-id key formatting, shard key formatting, owner parsing for account/user strings, and principal ARN rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_basic_types.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_basic_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_basic_types.h

Purpose: declares foundational RGW types shared across RGW, cls, and other Ceph components. The header warns against RGW-only dependencies because these serialized types cross subsystem boundaries.

Important APIs/types/functions: `RGWIntentEvent`, `rgw_err`, `rgw_zone_id`, `rgw::auth::Principal`, JSON/XML declarations for `rgw_user`, `rgw_zone_id`, pools, placement, and access keys, plus `RGWUploadPartInfo`. `Principal` has factory methods for wildcard, user, role, account, OIDC provider, assumed role, and service principals. `RGWUploadPartInfo` records multipart part number, size, accounted size, etag, modification time, manifest, compression info, optional checksum, and old prefixes for cleanup.

Control flow: most functions are inline serialization, comparison, and accessors. `RGWUploadPartInfo::decode()` handles legacy structure versions: manifest appears at v3, compression/accounted size at v4, old prefixes at v5, checksum at v6.

State/persistence: `rgw_zone_id` and `RGWUploadPartInfo` are buffer-encoded persisted data. `Principal` is in-memory identity matching data. Multipart uploads persist manifests, compression info, and checksums through this type.

Dependencies/integration: pulls in pool/user/bucket/object/checksum/compression types and the RADOS object manifest. Used by IAM/auth, bucket/object metadata, multipart upload completion, and JSON/admin surfaces.

Risks: adding dependencies here can break non-RGW build contexts. Changing encode versions or defaults can corrupt old multipart upload decode. `Principal::operator==` compares only type and `rgw_user`, so OIDC provider/service-specific fields are not part of equality.

Test signals: serialization compatibility for `rgw_zone_id` and all `RGWUploadPartInfo` versions, multipart checksum persistence, `Principal` comparisons/rendering, and `rgw_err` clear/error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_basic_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_blake3_digest.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_blake3_digest.h

Purpose: provides a small RGW digest wrapper around the C BLAKE3 implementation so checksum code can treat BLAKE3 like other digest algorithms.

Important APIs/types/functions: `rgw::digest::Blake3` exposes `digest_size`, `Restart()`, `Update(const unsigned char*, uint64_t)`, and `Final(unsigned char*)`.

Control flow: constructor calls `Restart()`, `Update()` forwards data to `blake3_hasher_update()`, and `Final()` writes `BLAKE3_OUT_LEN` bytes through `blake3_hasher_finalize()`.

State/persistence: holds only the mutable `blake3_hasher` context. The digest bytes are consumed by higher-level `rgw::cksum::Cksum` persistence.

Dependencies/integration: depends on `BLAKE3/c/blake3.h` and is wrapped by `rgw_cksum_digest.h` as `TDigest<rgw::digest::Blake3>`.

Risks: the API does not guard null output buffers or concurrent use. Digest size must stay synchronized with the descriptor table in `rgw_cksum.h`.

Test signals: BLAKE3 known-answer tests, restart reuse, multi-update equivalence with single update, and integration through `finalize_digest(Type::blake3)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_blake3_digest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket.cc

Purpose: implements bucket key parsing/formatting helpers and a utility to transfer bucket and object ownership through the SAL layer.

Important APIs/types/functions: `init_bucket()`, `rgw_bucket_parse_bucket_key()`, `rgw_make_bucket_entry_name()`, `rgw_parse_url_bucket()`, and `rgw_chown_bucket_and_objects()`.

Control flow: `rgw_bucket_parse_bucket_key()` parses `[tenant/]name:instance[:shard_id]`, with optional tenant and shard id. `rgw_parse_url_bucket()` parses S3 tenant-qualified `tenant:bucket`, allowing `:bucket` as explicit legacy tenant. `rgw_chown_bucket_and_objects()` first changes bucket ownership, skips object ACL rewrites when ObjectOwnership is `BucketOwnerEnforced`, then lists all object versions in batches of 1000 and calls `Object::chown()` for each.

State/persistence: parsing functions derive metadata keys. `rgw_chown_bucket_and_objects()` persists bucket owner metadata and object ACL/owner changes through SAL bucket/object operations.

Dependencies/integration: integrates with SAL `Driver`, `Bucket`, `Object`, `User`, object ownership helpers, Ceph errno/logging, and optional yields.

Risks: parsing uses delimiter assumptions; bucket names with unexpected delimiters can misparse. `strict_strtol(shard.data())` depends on null-terminated view data from the original string. Chown loops can be expensive, partially complete on error, and writes progress to `cerr`.

Test signals: parse/format round-trips for tenantless, tenant-qualified, idless, and sharded keys; S3 URL bucket parsing; chown behavior with BucketOwnerEnforced; partial-list continuation and failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket.h

Purpose: declares RGW bucket utility functions and object namespace constants used by bucket metadata, S3 URL parsing, and administrative ownership changes.

Important APIs/types/functions: `RGW_OBJ_NS_MULTIPART`, `RGW_OBJ_NS_SHADOW`, `init_bucket()`, `rgw_bucket_parse_bucket_key()`, `rgw_make_bucket_entry_name()`, `rgw_parse_url_bucket()`, and `rgw_chown_bucket_and_objects()`.

Control flow: this header is only declarations; behavior lives in `rgw_bucket.cc`.

State/persistence: constants define bucket-index namespaces for multipart and shadow objects. Declared functions operate on persisted bucket identifiers, metadata entry names, and SAL ownership state.

Dependencies/integration: includes `rgw_common.h` and `rgw_sal.h`, so it is RGW/SAL-specific unlike lower-level bucket types. Used by REST/admin code and bucket metadata utilities.

Risks: namespace constants and key parse contracts are compatibility surfaces; changing them breaks metadata lookup. The chown declaration exposes a broad operation whose callers must handle partial work and retries.

Test signals: compile users across RGW, namespace string expectations, and behavior tests in `rgw_bucket.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_encryption.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_encryption.cc

Purpose: implements XML and JSON formatting for S3 bucket default encryption configuration.

Important APIs/types/functions: `ApplyServerSideEncryptionByDefault::decode_xml/dump_xml()`, `ServerSideEncryptionConfiguration::decode_xml/dump_xml()`, and `RGWBucketEncryptionConfig::decode_xml/dump_xml/dump()`.

Control flow: XML decode reads `KMSMasterKeyID`, `SSEAlgorithm`, `ApplyServerSideEncryptionByDefault`, `BucketKeyEnabled`, and optional `Rule`. XML dump emits only configured fields: KMS key only when non-empty, bucket key only when true, and rule only when present. JSON dump writes `rule_exist` and rule fields when present.

State/persistence: no storage I/O; it transforms XML/JSON around buffer-encoded structures declared in the header. Bucket encryption policies are persisted as bucket attrs elsewhere.

Dependencies/integration: uses `rgw_xml.h` decoders and Ceph JSON encoding. REST bucket encryption handlers use these methods to parse and return S3-compatible configuration.

Risks: this layer does not validate algorithm names or KMS key semantics. Optional XML elements are accepted without policy checks. Empty KMS key is omitted on output, which must match API behavior.

Test signals: XML decode/dump for SSE-S3 and SSE-KMS, bucket key enabled/disabled, absent `Rule`, malformed XML, JSON dump of configured/unconfigured cases, and buffer round-trip from the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_encryption.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_encryption.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_encryption.h

Purpose: declares serialized S3 bucket default encryption configuration types.

Important APIs/types/functions: `ApplyServerSideEncryptionByDefault` stores `kmsMasterKeyID` and `sseAlgorithm`; `ServerSideEncryptionConfiguration` wraps default encryption and `bucketKeyEnabled`; `RGWBucketEncryptionConfig` wraps optional rule existence. Each exposes accessors, `encode()`, `decode()`, XML methods, and class encoders.

Control flow: `RGWBucketEncryptionConfig::encode()` persists `rule_exist` and conditionally persists `rule`; decode mirrors this. Nested classes encode/decode fields in fixed version-1 structures.

State/persistence: these are bucket-attribute payload types, serialized with Ceph buffer encoding and surfaced through XML/JSON.

Dependencies/integration: depends only on `include/types.h`, `include/encoding.h`, XML forward declaration, and formatter forward declaration. The low dependency surface makes it suitable as a metadata type.

Risks: no semantic validation in constructors or decode; invalid algorithm strings can be represented. `bucketKeyEnabled` defaults false, so omitted XML and explicit false are equivalent.

Test signals: buffer encode/decode of rule-present and no-rule cases, XML parsing for optional fields, API output for omitted KMS key and bucket key, and backward compatibility if future fields are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_encryption.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_layout.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_layout.cc

Purpose: implements string parsing, JSON conversion, and buffer encoding for bucket index/log layout and resharding state metadata.

Important APIs/types/functions: `to_string()/parse()` for `BucketIndexType`, `BucketHashType`, `BucketLogType`, and `BucketReshardState`; encode/decode/JSON functions for `bucket_index_normal_layout`, `bucket_index_layout`, `bucket_index_layout_generation`, `bucket_index_log_layout`, `bucket_log_layout`, `bucket_log_layout_generation`, and `BucketLayout`.

Control flow: each tagged layout encodes its type then conditionally encodes variant payload fields. Decode mirrors switch cases. `BucketLayout::decode()` has legacy behavior: for struct versions before logs existed, it synthesizes a log layout from current index when the index type is normal; version 3 adds `judge_reshard_lock_time`.

State/persistence: these functions define persisted bucket layout metadata, including current index generation, target reshard layout, log generations, and reshard status/time.

Dependencies/integration: used by bucket metadata, resharding code, and JSON/admin output. Depends on Ceph encoding, JSON decoder, `utime`, and Boost case-insensitive parsing.

Risks: unknown enum strings leave fields unchanged because parse return values are ignored in JSON decoders. `Indexless` layouts skip normal fields but some JSON output always includes `normal`, so consumers must tolerate unused data. Layout version changes affect existing buckets.

Test signals: binary compatibility for all struct versions, JSON parse case-insensitivity, legacy decode log synthesis, indexless decode/output, reshard state parse, and num-shard defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_layout.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_layout.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_layout.h

Purpose: declares the persisted description of bucket index layouts, bucket log layouts, and resharding status.

Important APIs/types/functions: enums `BucketIndexType`, `BucketHashType`, `BucketLogType`, `BucketReshardState`; structs `bucket_index_normal_layout`, `bucket_index_layout`, `bucket_index_layout_generation`, `bucket_index_log_layout`, `bucket_log_layout`, `bucket_log_layout_generation`, and `BucketLayout`; helpers `log_layout_from_index()`, `matches_gen()`, `log_to_index_layout()`, `num_shards()`, `current_num_shards()`, `current_min_layout_shards()`, `is_layout_indexless()`, `is_layout_reshardable()`, and `current_layout_desc()`.

Control flow: the header defines equality, stream operators, and helper conversions. `num_shards()` treats historical `num_shards=0` as one shard. Reshardability is limited to `Normal` index layouts.

State/persistence: `BucketLayout` carries current and target index generations, untrimmed log generations, resharding state, and `judge_reshard_lock_time`, all persisted by implementations in the `.cc`.

Dependencies/integration: low-level Ceph encoding and JSON; consumed by bucket metadata, resharding, bilog/datalog, and bucket index selection paths.

Risks: equality for `bucket_index_normal_layout` ignores `min_num_shards`, so comparisons may miss minimum-shard changes. Helpers assert normal layout in some paths. Current log/index conversion assumes `InIndex` log layout.

Test signals: helper semantics for zero shards, indexless buckets, reshardable checks, equality expectations including `min_num_shards`, log/index conversion, and generation matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_layout.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_logging.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_logging.cc

Purpose: implements S3 server access logging configuration parsing/output, pending log object naming/rollover, record generation, quota checks, target policy validation, source bookkeeping, and deletion cleanup.

Important APIs/types/functions: `configuration::decode_xml/dump_xml/dump/to_json_str()`, `new_logging_object()`, `commit_logging_object()`, `rollover_logging_object()`, both `log_record()` overloads, `object_name_oid()`, `get_bucket_id()`, `update_bucket_logging_sources()`, `bucket_deletion_cleanup()`, `source_bucket_cleanup()`, `verify_target_bucket_policy()`, `verify_target_bucket_attributes()`, and `get_target_and_conf_from_source()`.

Control flow: XML decode enables config only when `LoggingEnabled` exists, parses target bucket/prefix, Ceph extensions, journal filters, and key format. Logging loads the target bucket, validates policy/attributes, refreshes the source list, gets or creates the pending object name, rolls over by time or full-object error, formats either standard or journal records, checks user/bucket quota, and appends. Cleanup removes source attrs, source list entries, pending-object name objects, and either commits or removes pending log objects depending on whether source or target is deleted.

State/persistence: bucket logging config is stored in `RGW_ATTR_BUCKET_LOGGING`; target source tracking in `RGW_ATTR_BUCKET_LOGGING_SOURCES`; pending object names and pending/committed log objects are manipulated through SAL bucket methods with object version trackers for races.

Dependencies/integration: SAL driver/bucket/object, `req_state`, IAM policy evaluator, ARN, S3 auth helpers, quotas, XML/JSON, filters, Ceph time, and retry-raced bucket writes.

Risks: rollover is race-prone and relies on `-ECANCELED` handling. Cleanup intentionally swallows many post-attr-removal errors to preserve idempotence, which can leak objects. Target policy verification mutates request environment with `aws:SourceArn` and `aws:SourceAccount`. `EventTime` partition format is not fully implemented. Logging target cannot itself have logging, requester pays, or encryption.

Test signals: XML round-trips, standard/journal record formats, journal filters, target policy allow/deny, requester-pays/encryption/logging rejection, quota failures, object rollover by time and `-EFBIG`, source/target bucket deletion cleanup, races on pending object name, and tenant-qualified target bucket parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_logging.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_logging.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_logging.h

Purpose: declares RGW bucket logging configuration, enums, record buffers, constants, and operational helpers for S3 server access logging.

Important APIs/types/functions: enums `KeyFormat`, `LoggingType`, `PartitionDateSource`; struct `configuration`; `service_principal`; `source_buckets`; `MAX_BUCKET_LOGGING_BUFFER`; `bucket_logging_records`; template `to_string(records)`; and declarations for logging, rollover, source bookkeeping, cleanup, verification, and target loading helpers.

Control flow: `configuration::encode()` serializes target bucket, key format, prefix, roll time, logging type, batch size, date source, and only encodes `key_filter` for journal logging. Decode mirrors this conditional layout.

State/persistence: `configuration` is the buffer-encoded bucket logging attr. `source_buckets` is the encoded set on target buckets. Record buffers are in-memory batching primitives.

Dependencies/integration: SAL forward declarations, bucket types, buffer encoding, async yield, S3 key filters, and ARN. Used by REST bucket logging handlers and operation completion logging.

Risks: conditional encoding of `key_filter` depends on `logging_type` being decoded correctly. `records_batch_size` is documented for batching, while actual write behavior is in SAL/logging implementation. `LoggingType::Any` is a selector, not valid user config.

Test signals: configuration encode/decode for Standard and Journal, XML/JSON output, source-bucket set encoding, `Any` selector behavior, partitioned/simple key-format serialization, and batch limit boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_logging.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync.cc

Purpose: implements bucket sync policy flow resolution for multisite RGW, converting zonegroup and bucket policies into source/destination pipe sets used by data sync.

Important APIs/types/functions: stream operators for sync entities/pipes, `filter_relevant_pipes()`, `rgw_sync_group_pipe_map` methods, `RGWBucketSyncFlowManager::pipe_rules`, `pipe_set`, `allowed_data_flow()`, `init()`, `reflect()`, `RGWSyncPolicyCompat::convert_old_sync_config()`, and `RGWBucketSyncPolicyHandler` constructors, `init()`, `reflect()`, pipe getters, and export/import checks.

Control flow: group map initialization filters policy pipes touching the local zone/bucket, chooses explicit group data flow or a parent-derived default flow, and populates source/dest multimaps for symmetrical and directional flows. `reflect()` recursively applies parent policy, then local group policy, with `FORBIDDEN` disabling matching pipes and enabled/allowed groups inserting pipes. `pipe_rules` select highest-priority matching prefix/tag filters and can detect when tag fetch is required before choosing params.

State/persistence: no direct storage writes. It reads zonegroup sync policy, optional bucket sync policy, bucket sync hints from `RGWSI_Bucket_Sync`, and builds in-memory pipe maps, handler sets, zone sets, hints, and resolved pipe sets.

Dependencies/integration: `rgw_sync_policy`, zone services, bucket sync service, object tags, `RGWBucketInfo`, buffer attrs, logging, and Ceph context. Data sync and REST/admin policy code use handler results to decide import/export routes.

Risks: policy precedence is subtle: forbidden beats enabled, and bucket-level allowed without zonegroup enabled can disable sync. Prefix selection uses sorted `multimap` and comments note a trie would be better. `find_basic_info_without_tags()` can return false/need-more-info on conflicting same-priority params. Disabled pipe matching must stay consistent with `match()` semantics.

Test signals: legacy zone sync conversion, symmetrical/directional flows, parent plus bucket policy precedence matrix, forbidden overrides, wildcard bucket fallback, prefix/tag priority selection, source/target zone maps, resolved hints, `bucket_exports_object()`, and sync-module disabled behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync.h

Purpose: declares bucket sync policy mapping and query types for RGW multisite bucket-level synchronization.

Important APIs/types/functions: `rgw_sync_group_pipe_map`, `RGWSyncPolicyCompat`, `RGWBucketSyncFlowManager` with nested `endpoints_pair`, `pipe_rules`, `pipe_handler`, and `pipe_set`, `RGWBucketSyncPolicyHandler`, `rgw_bucket_sync_pair_info`, and `rgw_bucket_sync_pipe`.

Control flow: declarations model two levels: flow manager resolves raw policy flow groups into pipe sets, and policy handler owns zone/bucket context and exposes source/target pipe queries. `pipe_handler` delegates object parameter lookup to shared `pipe_rules`.

State/persistence: in-memory policy resolution state includes group maps, source/target pipes by zone, zone sets, source/target bucket hints, and resolved hints. `rgw_bucket_sync_pipe` bundles resolved source/destination bucket info and attrs for downstream sync.

Dependencies/integration: includes `rgw_common`, sync policy definitions, zone metadata, service forward declarations, `RGWBucketInfo`, object tags, bucket shard types, and buffer attrs.

Risks: many getters return mutable or raw pointers/references to internal containers, so lifetime is tied to the handler. Child handlers point at parent handlers and parent flow managers. `bucket_exports_data()` assumes `bucket_info` is present when needed.

Test signals: construction of root and child handlers, lifetime of shared rule refs, pipe-set insert/disable, source/dest query aggregation including resolved hints, and object filter matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync_cache.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync_cache.h

Purpose: provides a per-datalog-shard LRU cache for bucket-shard sync state used by data sync coroutines.

Important APIs/types/functions: `rgw::bucket_sync::State`, `Entry`, `EntryToKey`, `Cache`, and `Handle`. `State` tracks key `(rgw_bucket_shard, optional generation)`, current `rgw_data_sync_obligation`, a counter, and progress timestamp.

Control flow: `Cache::create()` returns an intrusive pointer with configured target size. `Cache::get()` calls intrusive LRU `get_or_create()` and returns a `Handle` that retains both cache and entry. `Handle` implements copy/move assignment in an order that keeps the cache alive while replacing entries.

State/persistence: in-memory only; no disk/RADOS writes. The cached state represents live data-sync progress and obligations for bucket shards.

Dependencies/integration: depends on Ceph intrusive LRU, Boost intrusive ref counters, `rgw_data_sync.h`, `rgw_bucket_shard`, and `rgw_data_sync_obligation`.

Risks: explicitly uses thread-unsafe reference counting because intended scope is single-threaded; cross-thread sharing would be unsafe. LRU eviction must not invalidate active `Handle`s. Progress state is volatile and must be reconstructable.

Test signals: cache hit/create behavior by shard/generation key, LRU eviction with active handles, copy/move handle lifetime, counter updates, and no cross-thread use assumptions in data sync tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_sync_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_bucket_types.h

Purpose: declares fundamental serialized bucket identity, placement, and shard types that must remain independent of RGW-only contexts.

Important APIs/types/functions: `rgw_bucket_key`, `rgw_bucket`, `std::hash<rgw_bucket>`, stream operator for `rgw_bucket`, `rgw_bucket_placement`, `rgw_bucket_shard`, `std::hash<rgw_bucket_shard>`, and encode/decode declarations for shards.

Control flow: `rgw_bucket::match()` treats an empty bucket id on either side as wildcard. `encode()` writes version 10 fields with optional explicit placement; `decode()` supports legacy versions with old pool fields, numeric ids through v3, tenant from v8, and explicit-placement flag from v10. `get_namespaced_name()` uses `tenant/name` when tenant exists.

State/persistence: `rgw_bucket` is a core persisted identifier with tenant, name, marker, bucket id, and explicit placement. `rgw_bucket_shard` combines bucket id and shard id for index/log/sync/cache keys.

Dependencies/integration: pool/user/placement types, formatter, hashing, and cls user bucket conversion implemented elsewhere. Used broadly by bucket metadata, sync, logging, cache, and REST.

Risks: legacy decode defaults are compatibility-critical. `operator<<` appears to include an extra closing parenthesis in display. Equality requires exact bucket id while `match()` allows empty-id wildcard, so callers must choose correctly.

Test signals: all legacy decode versions, explicit-placement absence/presence, wildcard matching, hashing stability, ordered comparisons, shard key formatting, and stream output expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_bucket_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cache.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_cache.cc

Purpose: implements RGW in-memory object cache lookup, update, expiry, LRU eviction, chained-cache invalidation, and JSON/test-instance support for cache notification types.

Important APIs/types/functions: `ObjectCache::get()`, `put()`, `invalidate_remove()`, `chain_cache_entry()`, `touch_lru()`, `remove_lru()`, `invalidate_lru()`, `set_enabled()`, `invalidate_all()`, `do_invalidate_all()`, `chain_cache()`, `unchain_cache()`, destructor, and dump/test-instance methods for `ObjectMetaInfo`, `ObjectCacheInfo`, `RGWCacheNotifyInfo`.

Control flow: `get()` takes a shared lock, misses disabled/absent/expired/type-mismatched entries, upgrades to write lock for expiry or LRU promotion, and fills `rgw_cache_entry_info` with locator/generation. `put()` invalidates chained dependents, increments generation, promotes LRU, merges flags/data/xattrs/meta/version, and supports negative entries. `chain_cache_entry()` verifies all referenced cache generations before registering dependent cache callbacks.

State/persistence: cache state is process memory only. Notification structs are serializable for cache invalidation messages. Entries carry `time_added`, generation counters, xattrs/data/meta/version, and dependent chained entries.

Dependencies/integration: Ceph shared mutex, RGW perf counters, configuration `rgw_cache_lru_size` and `rgw_cache_expiry_interval`, `rgw_cache_entry_info`, formatter, bufferlist, and chained caches.

Risks: lock upgrade is manual unlock/lock and must re-check map state. `for_each()` in the header appears to call the callback only for entries younger than expiry when expiry is set, but skips all entries if expiry is zero. Negative entries return `-ENODATA`. LRU size condition uses `>` so one extra entry can exist until touch.

Test signals: concurrent get/put/invalidate races, expiry removal and chained invalidation, type-mask miss, negative cache hit, xattr modification merge, generation mismatch in `chain_cache_entry()`, LRU eviction, and disable clears cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cache.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cache.h

Purpose: declares object cache data structures, flags, cache notification payloads, chained-cache interface, and `ObjectCache`.

Important APIs/types/functions: operation enum values `UPDATE_OBJ` and `INVALIDATE_OBJ`; flags `CACHE_FLAG_DATA`, `XATTRS`, `META`, `MODIFY_XATTRS`, `OBJV`; `ObjectMetaInfo`; `ObjectCacheInfo`; `RGWCacheNotifyInfo`; `RGWChainedCache`; `ObjectCacheEntry`; and `ObjectCache`.

Control flow: declarations expose `get()`, optional-return `get()`, `for_each()`, `put()`, invalidation, context setup, chained-cache registration, and enable/disable. Inline `for_each()` reads under shared lock and filters by enabled/expiry.

State/persistence: structs are buffer-encoded for notifications and test instances. `ObjectCache` live state is an unordered map plus LRU list, counters, expiry, and chained cache registry.

Dependencies/integration: Ceph mutex/time/assert, cls version types, `rgw_common`, bufferlist, and RGW cache entry info. Used by RADOS/object metadata layers to cache object data/xattrs/meta.

Risks: `ObjectCacheInfo::time_added` is not encoded; restored notifications do not carry cache age. `for_each()` expiry condition may be inverted or too restrictive for zero-expiry cases. Chained entries store raw cache pointers and string keys, so unregister ordering matters.

Test signals: encode/decode for cache notification structs, flag merge semantics, `for_each()` with expiry zero/nonzero, chain registration/unregistration, and cache_info generation lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cache_driver.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cache_driver.h

Purpose: declares an abstract external cache driver interface and cache object attribute names for RGW cache backends.

Important APIs/types/functions: constants like `RGW_CACHE_ATTR_MTIME`, `EPOCH`, `OBJECT_SIZE`, `ACCOUNTED_SIZE`, `MULTIPART`, `OBJECT_NS`, `BUCKET_NAME`, `VERSION_ID`, `SOURCE_ZONE`, `LOCAL_WEIGHT`, `DELETE_MARKER`, `INVALID`, `DIRTY`, delimiter `CACHE_DELIM`, callback aliases `ObjectDataCallback` and `BlockDataCallback`, `Partition`, and abstract `CacheDriver`.

Control flow: `CacheDriver` implementations must support initialization, sync and async put/get, append/delete/rename, attr get/set/update/delete, single-attr get/set, partition info/free space, and data recovery via callbacks.

State/persistence: concrete implementations persist cached object/block data and attrs outside this header. Attribute names define on-disk or backend metadata contracts.

Dependencies/integration: `rgw_common`, `rgw_aio`, SAL attrs, `DoutPrefixProvider`, `rgw_user`, `rgw_obj_key`, optional yield, and AIO result lists.

Risks: interface has many operations with no default semantics; backend implementations must align attr names and async cost/id behavior. `const::std::string` spelling appears in several pure virtual declarations but is accepted as `const std::string`; style may confuse maintainers.

Test signals: backend conformance for all virtual methods, attr naming compatibility, async get/put completion ordering, recovery callback coverage, partition free-space reporting, and rename/delete edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cache_driver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_cksum.cc

Purpose: implements checksum combination for multipart objects, including AWS-compatible CRC full-object synthesis and digest-style composite checksums.

Important APIs/types/functions: `combine_crc_cksum()`, private `DigestCombiner`, private `CRCCombiner`, and `CombinerFactory()`.

Control flow: `combine_crc_cksum()` rejects mismatched or non-CRC types, byteswaps stored CRC values into algorithm order, calls type-specific madler combiner functions for CRC64NVME/CRC32/CRC32C, byteswaps back to at-rest order, and returns a raw `Cksum`. `DigestCombiner` hashes concatenated part checksum bytes and marks `COMPOSITE_MASK`. `CRCCombiner` stores the first part checksum and combines each following part by length, marking `FULL_OBJECT_MASK`.

State/persistence: no direct storage writes; produced `Cksum` objects are persisted by object metadata/parts elsewhere. Flags distinguish legacy/composite/full-object multipart semantics.

Dependencies/integration: `rgw_cksum.h`, `rgw_cksum_digest.h`, CRC digest byte swapping, madler CRC combine routines, SPDK CRC64 include, and checksum callers in REST multipart completion.

Risks: parameter name says `len1` while header says `len2`; correctness depends on passing the second segment length expected by combine functions. `CRCCombiner::append()` dereferences optional combine result without guard. CRC byte order is subtle and AWS-visible.

Test signals: known multipart CRC32/CRC32C/CRC64NVME combinations, digest composite checksums with part count behavior at response layer, mismatched type rejection, one-part CRC combine, and byte-order regression vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cksum.h

Purpose: defines RGW checksum algorithms, descriptors, serialized checksum value type, AWS/RGW header naming, checksum parsing, type compatibility rules, and combiner interface.

Important APIs/types/functions: enum `Type`; flags `FLAG_AWS_CKSUM`, `FLAG_CRC`; `Desc`; class `Cksum`; `no_cksum`; `to_string()`, `to_uc_string()`, `parse_cksum_type()`, `cksum_flags_of()`, `parse_cksum_type_hdr()`, `is_checksum_hdr()`, `permitted_cksum_algo_and_type()`, `combine_crc_cksum()`, abstract `Combiner`, `CombinerFactory()`, `get_checksum_type()`, and `get_part_checksum_type()`.

Control flow: `Cksum` constructors accept raw or armored input. Encoding stores type id, digest size, raw digest bytes, and flags. Header/element names are derived from algorithm descriptors. Compatibility allows composite for all but CRC64NVME and full-object only for CRC family. `get_checksum_type()` treats legacy v1 multipart checksums as composite.

State/persistence: `Cksum` is persisted in object/multipart metadata. Flags are a format and semantics contract; v2 marks newer stored checksums and full-object/composite masks identify combined checksum mode.

Dependencies/integration: Boost string helpers, `fmt`, Ceph armor, hex/base64 helpers, buffer encoding. Used by REST S3, put-object pipeline, multipart completion, and response checksum headers.

Risks: decode trusts stored type/digest size enough to copy into fixed array; malformed values can overrun if not protected by encoded data discipline. `to_base64()` encodes the hex string rather than raw digest, which is a display helper rather than AWS armor. Composite/full-object flag semantics are intentionally nuanced for 2023 and 2025 compatibility.

Test signals: descriptor table indexes match enum values, armor/raw constructors, header parsing case-insensitivity, v1/v2 decode semantics, compatibility matrix, checksum type response values, and malformed decode handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum_digest.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cksum_digest.h

Purpose: adapts multiple concrete digest implementations behind a small polymorphic interface for RGW checksum calculation.

Important APIs/types/functions: abstract `Digest`; templated `TDigest<T>`; type aliases `Blake3`, `Crc32`, `Crc32c`, `XXH3`, `SHA1`, `SHA256`, `SHA512`, `Crc64Nvme`; `DigestVariant`; visitor `get_digest_ptr`; `get_digest()`, `digest_factory()`, and `finalize_digest()`.

Control flow: `TDigest` forwards restart/update/final calls and iterates over bufferlist buffers for buffer updates. `digest_factory()` switches on checksum type to construct the right variant. `finalize_digest()` creates a `Cksum` of the requested type and calls `Final()` when a digest implementation exists.

State/persistence: digest state is in-memory; output becomes a `Cksum` persisted elsewhere.

Dependencies/integration: Ceph SHA crypto classes, RGW Blake3/CRC/XXH wrappers, `rgw_cksum.h`, and bufferlist. Used by checksum pipe and multipart combiner.

Risks: `Type::none` produces `std::monostate` and `get_digest()` returns null; callers must not call `Update()` on null digest. `TDigest::Update(const bufferlist&)` lacks `override` annotation. Adding algorithms requires updating both enum descriptor and variant/factory.

Test signals: factory coverage for each `Type`, null behavior for none, known-answer digest tests, bufferlist vs contiguous update equivalence, and algorithm additions failing compile/tests unless all tables are updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum_digest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum_pipe.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_cksum_pipe.cc

Purpose: implements the put-object checksum pipe that streams incoming object data through a digest while forwarding data to the next SAL data processor.

Important APIs/types/functions: `RGWPutObj_Cksum` constructor, `RGWPutObj_Cksum::Factory()`, and `RGWPutObj_Cksum::process()`.

Control flow: factory first finds checksum headers in the request environment; known algorithms create a pipe, unknown or malformed headers throw `rgw::io::Exception(EINVAL)`. If no header exists but an override type is supplied, it creates a pipe using the synthetic SDK checksum-algorithm header mapping. `process()` updates the digest over every buffer segment, then forwards the moved bufferlist to the next pipe.

State/persistence: the pipe maintains digest variant, digest pointer, selected type, flags, current finalized `Cksum`, and selected header. Final checksum is stored by higher layers after upload processing.

Dependencies/integration: `rgw_cksum_pipe.h`, `rgw_cksum`, `RGWEnv`, SAL `DataProcessor`, put-object pipe chain, and `rgw_client_io` exceptions.

Risks: `_digest` is null for `Type::none`, but factory avoids constructing that except malformed paths. Override path may not fix the request environment, as noted by comment. Exceptions must be translated by REST upload paths.

Test signals: factory behavior for each checksum header source, unknown algorithm errors, override type, streaming multi-buffer digest, forwarding logical offsets, and final verification against request headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum_pipe.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum_pipe.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_cksum_pipe.h

Purpose: declares checksum-header discovery helpers and the put-object checksum data-processing pipe.

Important APIs/types/functions: `cksum_hdr_t`, `cksum_algorithm_hdr(Type)`, `cksum_algorithm_hdr(const RGWEnv&)`, `multipart_cksum_algo()`, `get_hdr_cksum()`, `find_hdr_cksum()`, `parse_cksum_flags()`, and class `RGWPutObj_Cksum`.

Control flow: header discovery honors AWS precedence: individual checksum algorithm header before SDK algorithm header, trailers, then concrete checksum value headers. `get_hdr_cksum()` uses the selected algorithm to read `HTTP_X_AMZ_CHECKSUM_<ALG>`. `find_hdr_cksum()` scans value headers for CompleteMultipartUpload-style requests without algorithm header. `parse_cksum_flags()` maps `x-amz-checksum-type` to full-object or composite, otherwise defaults by algorithm family.

State/persistence: helpers inspect request env only. `RGWPutObj_Cksum` state includes digest variant and finalized `Cksum`; persistence happens in object metadata outside this class.

Dependencies/integration: `rgw_putobj` pipe, `RGWEnv`, `rgw_cksum`, digest factory, Ceph split, and AWS checksum request semantics.

Risks: `get_hdr_cksum()` and `find_hdr_cksum()` declare `cksum_type` without initializing before no-header return paths. Trailer parsing returns the first recognized checksum type. The `xxh3` SDK header string is `"XX3"`, likely suspicious. Verify requires both header key and expected value.

Test signals: AWS precedence cases, trailer checksum algorithm detection, uninitialized no-header paths under sanitizers, CompleteMultipartUpload checksum scan including crc64nvme coverage, checksum-type defaults, and malformed header rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_cksum_pipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_client_io.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_client_io.cc

Purpose: implements basic RGW client I/O initialization and debug logging of request environment variables.

Important APIs/types/functions: `rgw::io::BasicClient::init(CephContext*)`.

Control flow: `init()` calls virtual/overridden `init_env(cct)` and returns immediately on error. At RGW debug level 20, it iterates through `get_env().get_map()`, wraps each key/value in `rgw::crypt_sanitize::env`, and logs sanitized environment values.

State/persistence: initializes per-client request environment state via `init_env()`. No durable state.

Dependencies/integration: `rgw_client_io.h`, crypt sanitization, RGW dout subsystem, `CephContext` debug configuration, and `RGWEnv` map access. Used by frontends before request processing/auth.

Risks: debug logging must remain sanitized because env contains credentials and signatures. `init_env()` failure skips logging and propagates the raw error. Logging every env variable at level 20 can be noisy but useful for auth/debug tests.

Test signals: successful and failing `init_env()` propagation, sanitized logging for authorization/security headers, no unsanitized secret leakage, and debug-level gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_client_io.cc -->
