# Research: subset-b-008185

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-handlers_test.go -->
## sources/object-store/minio/cmd/bucket-handlers_test.go

Purpose: exercises bucket-level S3 HTTP handlers through MinIO's `ExecObjectLayerAPITest` harness across the configured object layer implementations. It focuses on remove bucket, bucket location, head bucket, multipart upload listing, list buckets, and multi-object delete behavior rather than implementation internals.

Important APIs and helpers: `TestRemoveBucketHandler`, `TestGetBucketLocationHandler`, `TestHeadBucketHandler`, `TestListMultipartUploadsHandler`, `TestListBucketsHandler`, and `TestAPIDeleteMultipleObjectsHandler` delegate to helper functions that build signed V4/V2 requests with `newTestSignedRequestV4` and `newTestSignedRequestV2`, unsigned requests with `newTestRequest`, and endpoint URLs such as `getBucketLocationURL`, `getHEADBucketURL`, `getListMultipartUploadsURLWithParams`, `getListBucketURL`, and `getDeleteMultipleObjectsURL`. The tests also use response helpers such as `generateMultiDeleteResponse`, `encodeResponse`, and anonymous policy builders from the policy test file.

Control flow: each test initializes state in the object layer, sends requests through `apiRouter.ServeHTTP`, and compares HTTP status, XML error bodies, or encoded response bodies. Remove bucket first writes an object and then verifies bucket deletion fails for both V4 and V2 signatures. Location and head tests cover valid, invalid credential, anonymous, and nil object-layer paths. Multipart upload listing runs a matrix of invalid bucket, missing bucket, delimiter, prefix/key-marker, upload-id marker, negative max-uploads, valid requests, invalid credentials, anonymous policy access, and nil object-layer requests. Multi-delete uploads objects, installs a policy allowing anonymous delete only under `public/*`, then validates quiet/non-quiet responses and mixed authorization results.

State and persistence behavior: the file mutates test object-layer state by creating objects, creating bucket policies, and deleting objects. It does not persist metadata directly, but it verifies handler-visible state transitions such as non-empty buckets refusing removal, policy-assisted anonymous access, and multi-delete idempotency for previously deleted objects.

Dependencies and integration points: integrates the HTTP router, authentication signing utilities, object-layer API, bucket policy subsystem, S3 XML encoding, and test harnesses for anonymous and nil object-layer scenarios. It indirectly exercises authorization through bucket policies and handler error conversion.

Risks: the location test currently skips the successful signed case with `if i != 1 { continue }`, so it only executes the invalid-credential case in that loop. Several assertions depend on exact XML serialization and response body ordering, which can be brittle if encoding changes. Multi-delete expected responses are manually constructed and could drift from handler behavior if response generation changes.

Test signals: coverage is broad for HTTP status handling, auth variants, anonymous access, nil object-layer fallback, and multi-delete response shape. It does not deeply validate bucket metadata persistence, multipart upload contents, or all list multipart edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle-audit.go -->
## sources/object-store/minio/cmd/bucket-lifecycle-audit.go

Purpose: defines lifecycle audit event metadata for ILM operations. It wraps `lifecycle.Event` with a local source enum so audit and trace output can distinguish whether lifecycle work originated from healing, scanning, decom, rebalance, or an S3 request path.

Important APIs and types: `lcEventSrc` is a `uint8` enum with generated `String()` support from `stringer`; values include `lcEventSrc_Heal`, `lcEventSrc_Scanner`, `lcEventSrc_Decom`, `lcEventSrc_Rebal`, and S3 operation sources such as `lcEventSrc_s3PutObject`. `lcAuditEvent` embeds `lifecycle.Event` and stores `source lcEventSrc`. `Tags()` converts event fields into audit tag strings. `newLifecycleAuditEvent` is the constructor used by transition and expiry code.

Control flow: `Tags()` starts with a five-entry map, conditionally adds `ilm-src` when source is not `None`, always adds `ilm-action` and `ilm-rule-id`, and conditionally adds due time, transition tier, newer noncurrent versions, and noncurrent days. Time values use `iso8601Format`; integer values use `strconv.Itoa`.

State and persistence behavior: no persistent state is stored. The struct captures a snapshot of a lifecycle event and source for downstream audit logging.

Dependencies and integration points: depends on `internal/bucket/lifecycle` for event/action semantics and on generated stringer code for source names. It is consumed by `transitionObject`, `expireTransitionedObject`, and audit logging paths in lifecycle processing.

Risks: adding new `lcEventSrc` values requires regenerating stringer output or audit tags may degrade. Because tags are stringly typed, downstream dashboards depend on stable key names such as `ilm-action` and `ilm-tier`.

Test signals: no direct tests in this subset cover tag generation. Indirect coverage comes from lifecycle transition and expiry tests elsewhere if they assert audit output, but the local files mainly test lifecycle parsing and handlers.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle-audit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle-handlers.go -->
## sources/object-store/minio/cmd/bucket-lifecycle-handlers.go

Purpose: implements S3 bucket lifecycle configuration handlers for PUT, GET, and DELETE. It validates request authentication, parses lifecycle XML, checks object-lock constraints, validates transition tiers, updates bucket metadata, and returns S3-compatible XML or empty success responses.

Important APIs and functions: `bucketLifecycleConfig` names the persisted config as `lifecycle.xml`. `PutBucketLifecycleHandler` requires Content-MD5, authorizes `policy.PutBucketLifecycleAction`, reads object-lock config via `globalBucketObjectLockSys.Get`, parses with `lifecycle.ParseLifecycleConfigWithID`, validates rules with `Validate`, validates tiers with `validateTransitionTier`, tracks expiry-rule changes, marshals XML, and persists through `globalBucketMetadataSys.Update`. `GetBucketLifecycleHandler` authorizes `policy.GetBucketLifecycleAction`, optionally parses `withUpdatedAt`, fetches metadata with `GetLifecycleConfig`, clears internal `ExpiryUpdatedAt`, and writes XML plus optional `x-minio-lifecycle-cfg-updated-at` header. `DeleteBucketLifecycleHandler` authorizes with put-lifecycle action and calls `globalBucketMetadataSys.Delete`.

Control flow: all handlers create request context, audit log on return, verify object API initialization, extract `bucket` via mux vars, authenticate, validate bucket existence, then interact with metadata. PUT compares prior lifecycle rules from disk against new rules to detect removal of expiration behavior; if new config has expiry or an expiry rule was removed, it updates `ExpiryUpdatedAt` before saving.

State and persistence behavior: lifecycle XML is stored inside bucket metadata under the lifecycle slot, with updated timestamps managed by `BucketMetadataSys`. DELETE has special behavior in the metadata layer: removing lifecycle config may persist an empty lifecycle document containing only `ExpiryUpdatedAt` to signal scanner behavior after expiry rules are removed.

Dependencies and integration points: integrates S3 auth policy, mux routing, lifecycle parser/validator, object lock retention config, tier config validation, global bucket metadata, audit logging, and MinIO lifecycle updated-at response headers.

Risks: PUT depends on reading the prior config from disk, so metadata read failures block updates even if in-memory config exists. Expiry-rule removal detection matches by rule ID and could miss semantic changes if IDs are reused incorrectly. GET exposes updated-at only for a MinIO-specific query parameter and returns errors for invalid boolean parsing.

Test signals: `bucket-lifecycle-handlers_test.go` validates wrong credentials, malformed filters/dates, successful PUT/GET/DELETE order, and no-config GET after delete. Tests do not cover `withUpdatedAt`, Content-MD5 failure, transition tier success, or expiry-rule removal timestamp behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle-handlers_test.go -->
## sources/object-store/minio/cmd/bucket-lifecycle-handlers_test.go

Purpose: tests S3 bucket lifecycle HTTP endpoints for authentication failures and the core PUT/GET/DELETE lifecycle.

Important APIs and helpers: `TestBucketLifecycleWrongCredentials` and `TestBucketLifecycle` invoke `ExecObjectLayerAPITest` with lifecycle endpoints. Helpers `testBucketLifecycleHandlersWrongCredentials`, `testBucketLifecycleHandlers`, and `testBucketLifecycle` build signed V4 requests with `newTestSignedRequestV4`, route through `apiRouter`, and compare status, XML response bodies, and unmarshaled `APIErrorResponse` fields.

Control flow: the wrong-credential test matrix sends GET, PUT, and DELETE using empty credentials and invalid credentials, expecting `AccessDenied` or `InvalidAccessKeyId`. The happy-path matrix first sends invalid lifecycle XML cases to assert `InvalidArgument`, then successfully PUTs a lifecycle rule, GETs the canonical XML, DELETEs it, and finally confirms subsequent GET returns `NoSuchLifecycleConfiguration`.

State and persistence behavior: the ordered test intentionally relies on lifecycle config persisted by the PUT being visible to GET and removed by DELETE. It validates the handler path through `globalBucketMetadataSys.Update` and `Delete` at a behavioral level.

Dependencies and integration points: depends on the shared object-layer test harness, HTTP router, request signing utilities, XML error unmarshalling, and lifecycle handler endpoint registration.

Risks: the success test is order-dependent, so running individual cases independently would not be meaningful. It asserts exact lifecycle XML bytes for the GET response, making it sensitive to marshaling order or namespace changes. It only uses V4 signing and does not test V2 signing.

Test signals: strong signals for auth rejection, invalid XML validation, persistence across PUT/GET, deletion, and S3 error body shape. Missing signals include Content-MD5 enforcement, object-lock lifecycle validation, transition tier validation in the handler path, and MinIO-specific updated-at header handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle.go -->
## sources/object-store/minio/cmd/bucket-lifecycle.go

Purpose: implements lifecycle subsystem glue for MinIO ILM: loading bucket lifecycle config, queuing expiration and transition work, deleting expired local and remote objects, transitioning objects to warm tiers, reading restored/transitioned data, and parsing restore-object request/status metadata.

Important APIs and types: `LifecycleSys` exposes `Get` and tracing helpers. `expiryState` manages sharded worker channels for `expiryTask`, `noncurrentVersionsTask`, `freeVersionTask`, and tier journal `jentry` operations, with `expiryStats` counters. `transitionState` owns immediate transition queueing, worker resize, active/missed task metrics, and last-day tier stats. Other key functions include `validateTransitionTier`, `enqueueTransitionImmediate`, `expireTransitionedObject`, `transitionObject`, `getTransitionedObjectReader`, `parseRestoreRequest`, `RestoreObjectRequest.validate`, `postRestoreOpts`, `putRestoreOpts`, `parseRestoreObjStatus`, `isRestoredObjectOnDisk`, and `ObjectInfo.ToLifecycleOpts`.

Control flow: background expiry is initialized with `newExpiryState`, which creates workers and hashes operations to channels using `OpHash` for object/tier locality. Expiry workers dispatch by concrete task type: normal object expiry, batch noncurrent deletion, remote tier deletion, or free-version cleanup. Transition state queues immediate transition tasks after uploads when lifecycle evaluation returns a transition action; workers call `transitionObject`, log non-benign failures, and update tier stats. Restore parsing validates SELECT restore constraints, output location, days, destination bucket existence, and encryption limitations.

State and persistence behavior: state is mostly in-memory queues and atomics, but operations mutate object metadata and storage through `ObjectLayer.DeleteObject`, `ObjectLayer.TransitionObject`, remote tier drivers, event notifications, lifecycle audit tags, and restore metadata such as `x-amz-restore`. Remote object names are generated using deployment/bucket hash plus UUID. `IsRemote` derives state from transition status and restore header expiry.

Dependencies and integration points: integrates lifecycle evaluator, bucket versioning, tier config manager, scanner metrics, global trace, event notification, remote warm-tier drivers, KMS-aware object readers, S3 Select restore structs, object lock indirectly through lifecycle handlers, and audit logging.

Risks: queue overflow drops work and only increments missed counters, shifting responsibility to later scanner passes. Worker resizing sends nil sentinel values on old channels; misuse could leave queued tasks behind. Restore header parsing is strict and string based. Remote deletion followed by local namespace deletion can leave free-version cleanup work if tier deletion fails. Transition and expiry code depends heavily on global state.

Test signals: `bucket-lifecycle_test.go` covers restore header parse/roundtrip, on-disk decisions, remote object state, and invalid transition tiers. Handler tests cover lifecycle config persistence. There is no direct unit coverage here for worker queue dispatch, remote tier deletion failure handling, restore request validation, or transition worker resize behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle_test.go -->
## sources/object-store/minio/cmd/bucket-lifecycle_test.go

Purpose: unit tests lifecycle helper logic that can be exercised without a full HTTP handler path: restore status parsing, restore status serialization, restored-object presence decisions, remote-object detection, and transition tier validation.

Important APIs and tests: `TestParseRestoreObjStatus` checks valid completed and ongoing `x-amz-restore` header forms and invalid combinations. `TestRestoreObjStatusRoundTrip` verifies `restoreObjStatus.String()` can be parsed back. `TestRestoreObjOnDisk` checks expiry-based `OnDisk`. `TestIsRestoredObjectOnDisk` checks metadata map interpretation. `TestObjectIsRemote` checks both `FileInfo.IsRemote` and `ObjectInfo.IsRemote`. `TestValidateTransitionTier` parses lifecycle XML and tests nonexistent storage class rejection.

Control flow: each test defines table cases and compares exact return values. `TestObjectIsRemote` creates valid `FileInfo`, marks transition status complete for metadata cases, converts to `ObjectInfo`, and finally verifies a non-transitioned object is not remote. Tier validation resets `globalTierConfigMgr` and parses lifecycle XML before invoking `validateTransitionTier`.

State and persistence behavior: no persistent state is written. The only global mutation is replacing `globalTierConfigMgr` in the tier validation test.

Dependencies and integration points: depends on lifecycle XML parsing, MinIO HTTP constants, `FileInfo`/`ObjectInfo` conversion, restore header time formatting, and tier config manager behavior.

Risks: tests using `time.Now().Add(...)` rely on immediate evaluation and could become flaky only under extreme clock or scheduling issues. The transition tier test covers rejection and no-transition success but not a configured valid transition target.

Test signals: good focused coverage for restored/remote state interpretation, including expired restored copies. It does not cover restore request XML validation, transition object execution, background queues, or audit tag generation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-lifecycle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-listobjects-handlers.go -->
## sources/object-store/minio/cmd/bucket-listobjects-handlers.go

Purpose: implements S3 list operations for objects and object versions, including V1, V2, metadata-enriched variants, archive listing, continuation-token proxy handling, argument validation, ETag decryption, and XML response generation.

Important APIs and functions: `validateListObjectsArgs` checks max keys, encoding type, object prefix validity, and marker/prefix compatibility. `ListObjectVersionsHandler` and `ListObjectVersionsMHandler` call `listObjectVersionsHandler`. `ListObjectsV2Handler` and `ListObjectsV2MHandler` call `listObjectsV2Handler`. `ListObjectsV1Handler` handles legacy listing. `parseRequestToken`, `proxyRequestByToken`, and `proxyRequestByNodeIndex` interpret continuation tokens containing node indexes and proxy to remote endpoints when needed.

Control flow: each handler builds context, audits, extracts bucket, verifies object API and authorization, parses query args with helper functions, validates arguments, calls the appropriate `ObjectLayer` list method, decrypts ETags via `DecryptETags`, generates S3 response structs, and writes XML. Metadata variants install `checkObjMeta` closures that re-check request auth per object/action during response generation. V2 additionally supports archive extraction listing when `xMinIOExtract` is true and the prefix includes the archive pattern.

State and persistence behavior: list handlers are read-only from the object namespace perspective. They may proxy requests to another node based on continuation token suffix, and they may consult KMS for encrypted ETag presentation.

Dependencies and integration points: integrates HTTP auth, mux route vars, policy actions, object-layer list APIs, response generators, archive listing, KMS ETag decryption, global proxy endpoints, and distributed node proxying.

Risks: `validateListObjectsArgs` comments mention delimiter constraints but the current code does not enforce delimiter equals `/`, so behavior may differ from comments. Marker must have prefix or returns `ErrNotImplemented`, a compatibility edge. Continuation-token parsing uses `getKeySeparator` and `strconv.Atoi`; malformed suffixes silently become local tokens.

Test signals: this exact file has no dedicated test in the subset. Related bucket handler tests cover multipart upload listing, not object listing. Risks around V2 continuation, metadata authorization, archive listing, and proxying require other test coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-listobjects-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-metadata-sys.go -->
## sources/object-store/minio/cmd/bucket-metadata-sys.go

Purpose: provides the cluster-wide in-memory bucket metadata subsystem backed by per-bucket `.metadata.bin` records. It centralizes update, delete, load, cache, refresh, and typed access for policy, lifecycle, notification, object lock, versioning, SSE, tagging, quota, replication, and bucket target configs.

Important APIs and types: `BucketMetadataSys` holds `objAPI`, `initialized`, `singleflight.Group`, and `metadataMap` under an RW mutex. Main mutators are `Set`, `Remove`, `RemoveStaleBuckets`, `Update`, `Delete`, `updateAndParse`, and `save`. Typed getters include `GetVersioningConfig`, `GetBucketPolicy`, `GetTaggingConfig`, `GetObjectLockConfig`, `GetLifecycleConfig`, `GetNotificationConfig`, `GetSSEConfig`, `GetPolicyConfig`, `GetQuotaConfig`, `GetReplicationConfig`, and `GetBucketTargetsConfig`. Loading and lifecycle APIs include `GetConfigFromDisk`, `GetConfig`, `Init`, `concurrentLoad`, `refreshBucketsMetadataLoop`, `Initialized`, `Reset`, and `NewBucketMetadataSys`.

Control flow: updates load metadata from disk, patch the relevant raw config bytes and updated-at timestamp, optionally encrypt bucket targets, save through `BucketMetadata.Save`, update the in-memory map, and notify peers via `globalNotificationSys.LoadBucketMetadata`. `GetConfig` returns cached metadata if present; otherwise singleflight loads from disk and caches it. `Init` concurrently heals and loads buckets in endpoint-scaled batches, then marks the subsystem initialized and starts a distributed refresh loop. Refresh periodically lists buckets, removes stale cached entries, reloads disk metadata, and replaces cache entries only if disk has a newer `lastUpdate`.

State and persistence behavior: the cache is shallow-copy based; comments warn that referenced fields must be replaced atomically rather than mutated. Disk state is the canonical `.metadata.bin`. Deleting lifecycle config is special: when expiry rules are removed, it saves an empty lifecycle config carrying `ExpiryUpdatedAt` so scanners can observe the change, while `GetLifecycleConfig` still reports no lifecycle config when no rules remain.

Dependencies and integration points: depends on object-layer config read/write, `singleflight`, errgroup concurrent loading, bucket monitor cleanup, global notification and replication target systems, lifecycle XML parsing for delete semantics, KMS encryption for bucket targets, and distributed erasure flags.

Risks: shallow copies can race if callers mutate referenced parsed configs. Global state makes tests and initialization order important. Refresh compares only aggregate `lastUpdate`; if timestamps are wrong or zeroed, stale cache may persist. `GetConfig` returns `errBucketMetadataNotInitialized` for missing disk metadata before initialization, which callers must handle distinctly.

Test signals: no direct tests in this subset for `BucketMetadataSys`. Handler tests indirectly exercise update/delete/get paths for policy and lifecycle. Generated metadata tests cover serialization but not cache refresh, singleflight, lifecycle delete semantics, or target encryption migration.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-metadata-sys.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-metadata.go -->
## sources/object-store/minio/cmd/bucket-metadata.go

Purpose: defines the persisted `BucketMetadata` record, metadata file format, migration from legacy per-config files, parsing of raw config bytes into typed private fields, serialization to `.metadata.bin`, and optional KMS encryption/decryption for bucket target metadata.

Important APIs and types: constants include `bucketMetadataFile`, `bucketMetadataFormat`, and `bucketMetadataVersion`. `BucketMetadata` stores bucket name, creation time, raw XML/JSON config bytes, per-config updated timestamps, and unexported parsed configs. Key methods/functions are `newBucketMetadata`, `lastUpdate`, `Versioning`, `ObjectLocking`, `SetCreatedAt`, `readBucketMetadata`, `loadBucketMetadataParse`, `loadBucketMetadata`, `parseAllConfigs`, `getAllLegacyConfigs`, `convertLegacyConfigs`, `defaultTimestamps`, `Save`, `migrateTargetConfig`, `encryptBucketMetadata`, and `decryptBucketMetadata`.

Control flow: loading reads `.minio.sys/buckets/<bucket>/.metadata.bin`, validates a four-byte little-endian format/version header, and msgp-unmarshals the payload. If metadata is absent or has zero creation time, legacy config files are discovered and converted into raw fields, saved as metadata, and legacy files are deleted best-effort. `parseAllConfigs` builds typed policy, notification, lifecycle, SSE, tagging, object lock, versioning, quota, replication, and target configs from raw bytes. `Save` re-parses first, writes the binary header, appends msgp data, and calls `saveConfig`.

State and persistence behavior: `.metadata.bin` is the main persisted state for bucket settings. Legacy object-lock enabled state is migrated to current object-lock and versioning XML. Updated timestamps default to `Created` if missing. Bucket target config may be encrypted with KMS and SIO, with crypto metadata stored separately in the metadata record.

Dependencies and integration points: integrates MinIO policy, event notification, lifecycle, object lock, versioning, encryption, tagging, quota, replication, bucket targets, object-layer config helpers, KMS, and msgp generated methods in `bucket-metadata_gen.go`.

Risks: adding or removing fields requires regenerating msgp code and considering format/version semantics. `parseAllConfigs` returns on first error, so one malformed config can prevent loading other metadata. Legacy migration deletes old files after saving; partial failures can leave mixed state. Encryption depends on `GlobalKMS` and associated-data consistency.

Test signals: generated msgp tests verify empty `BucketMetadata` serialization behavior. Handler tests indirectly verify policy/lifecycle persistence. There is no direct test here for legacy migration, parse failure handling, encryption/decryption, timestamp defaulting, or object-lock/versioning migration.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-metadata_gen.go -->
## sources/object-store/minio/cmd/bucket-metadata_gen.go

Purpose: generated msgp serialization code for `BucketMetadata`. It provides high-performance encode/decode, marshal/unmarshal, skip compatibility, and size estimation used by `.metadata.bin` persistence.

Important APIs and functions: `DecodeMsg` and `EncodeMsg` implement msgp stream interfaces. `MarshalMsg` and `UnmarshalMsg` implement byte-slice marshal/unmarshal. `Msgsize` estimates upper-bound serialized size. The generated map includes 25 fields: name, creation time, legacy lock flag, raw config bytes, target config metadata bytes, and all updated-at timestamps.

Control flow: decoders read a map header, loop over keys, match field names, read typed values, and skip unknown fields. Encoders write a fixed 25-entry map with field names and values in generated order. Byte-slice methods mirror stream behavior with `msgp.Read*Bytes` and append helpers.

State and persistence behavior: this file does not own state, but it defines the exact wire representation saved after the four-byte metadata header. Unknown-field skipping gives some forward/backward tolerance, while missing fields remain zero-valued and are handled by `defaultTimestamps` or parser defaults.

Dependencies and integration points: generated by `github.com/tinylib/msgp`; called by `BucketMetadata.Save` and `readBucketMetadata`. It must stay synchronized with the struct in `bucket-metadata.go`.

Risks: manual edits would be overwritten and are unsafe. If `BucketMetadata` changes without regenerating this file, persistence will silently omit or fail to read fields. `Msgsize` is an estimate used for allocation; inaccurate estimates affect performance, not correctness unless severely wrong.

Test signals: `bucket-metadata_gen_test.go` exercises empty struct marshal/unmarshal, stream encode/decode, skip, and benchmarks. It does not test non-empty metadata fields or compatibility across schema changes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-metadata_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-metadata_gen_test.go -->
## sources/object-store/minio/cmd/bucket-metadata_gen_test.go

Purpose: generated unit and benchmark coverage for msgp serialization of `BucketMetadata`.

Important APIs and tests: `TestMarshalUnmarshalBucketMetadata` marshals an empty struct, unmarshals it, and verifies no bytes remain; it also checks `msgp.Skip`. `TestEncodeDecodeBucketMetadata` stream-encodes and decodes an empty struct and verifies reader skip. Benchmarks cover marshal, append-style marshal reuse, unmarshal, encode, and decode allocation/throughput.

Control flow: tests construct zero-value `BucketMetadata`, run generated methods, and fail on leftover bytes or serialization errors. Benchmarks precompute buffers where appropriate, report allocations, and use `msgp.NewEndlessReader` for decode loops.

State and persistence behavior: no persistent state is written. The tests validate the generated codec used for persisted `.metadata.bin` payloads, but only for zero-value data.

Dependencies and integration points: depends on `github.com/tinylib/msgp/msgp` and generated methods from `bucket-metadata_gen.go`. These tests are tied to generated code and should be regenerated with it.

Risks: because tests use an empty struct, they can miss field-specific encode/decode regressions, timestamp handling, byte-slice preservation, or compatibility issues when fields are added. Benchmarks are useful for performance but not correctness gates.

Test signals: confirms basic codec roundtrip and skip support. Missing signal: populated `BucketMetadata` roundtrip equality and persistence header validation from `bucket-metadata.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-metadata_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-notification-handlers.go -->
## sources/object-store/minio/cmd/bucket-notification-handlers.go

Purpose: implements S3 bucket notification configuration GET and PUT handlers. It loads/stores notification XML in bucket metadata and synchronizes runtime event notifier rules.

Important APIs and functions: `bucketNotificationConfig` names the config as `notification.xml`. `GetBucketNotificationHandler` authorizes `policy.GetBucketNotificationAction`, verifies bucket existence, loads `globalBucketMetadataSys.GetNotificationConfig`, sets region, validates against `globalEventNotifier.targetList`, prunes stale ARN entries for `event.ErrARNNotFound`, marshals XML, and writes it. `PutBucketNotificationHandler` authorizes `policy.PutBucketNotificationAction`, requires positive Content-Length, parses with `event.ParseConfig` using site region and target list, stores XML via `globalBucketMetadataSys.Update`, converts config to rules, and calls `globalEventNotifier.AddRulesMap`.

Control flow: both handlers follow the standard MinIO handler pattern: context, audit defer, object API nil check, mux bucket extraction, auth, bucket existence, parse/load, validate, persist/respond. GET has compatibility cleanup for stale ARNs that older versions may have accepted; non-ARN validation errors are returned.

State and persistence behavior: notification XML is persisted inside `BucketMetadata`. PUT also updates in-memory notifier rules immediately. GET may remove stale queue entries from the response object but does not persist that cleanup in this handler.

Dependencies and integration points: integrates event config parsing/validation, global site region, event notifier target list/rules map, bucket metadata system, S3 auth policy, XML marshalling, mux, and audit logging.

Risks: GET's stale ARN pruning mutates the config object returned from metadata; because metadata getters return shallow copies with referenced parsed config pointers, this can have in-memory side effects. PUT rejects missing content length and maps non-event parse errors to malformed XML, so diagnostics depend on `event.IsEventError`.

Test signals: no direct tests in this subset. Behavior is likely covered elsewhere by notification handler tests, but this work item provides no local coverage for stale ARN pruning, target validation, or rules-map updates.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-notification-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-object-lock.go -->
## sources/object-store/minio/cmd/bucket-object-lock.go

Purpose: implements object lock/retention decision helpers used by delete, put, lifecycle, quota, and replication paths. It reads bucket retention defaults and enforces legal hold, governance, and compliance semantics.

Important APIs and functions: `BucketObjectLockSys.Get` returns bucket retention from `globalBucketMetadataSys.GetObjectLockConfig`, treating not-found as no retention. `enforceRetentionForDeletion` blocks lifecycle/quota deletion when legal hold is on or retention is unexpired. `enforceRetentionBypassForDelete` evaluates delete requests against object legal hold, compliance retention, governance bypass headers, and `policy.BypassGovernanceRetentionAction`. `enforceRetentionBypassForPut` validates retention updates/overwrites with owner and credential context. `checkPutObjectLockAllowed` parses WORM headers, bucket defaults, version-specific existing object state, replica behavior, and permission errors.

Control flow: delete enforcement first handles benign get-object errors such as not found, version not found, or method-not-allowed for delete markers. Legal hold always blocks. Compliance blocks until retain-until is before NTP time. Governance blocks unless retention is expired or bypass header and permission are present. Put enforcement computes remaining days for policy checks, then applies expired, governance, compliance, or new-retention rules. Header validation in `checkPutObjectLockAllowed` rejects lock headers on non-lock buckets, parses legal hold and retention headers when requested, and applies bucket default retention when appropriate.

State and persistence behavior: this file does not persist state itself. It reads parsed object-lock bucket config and object metadata, then returns retention/legal-hold values or errors that control later object writes/deletes.

Dependencies and integration points: integrates auth credentials, object-lock metadata parsing, replication status, NTP time, S3 policy checks, request headers, versioning options via `getOpts`, object info callbacks, and MinIO error types.

Risks: many branches depend on accurate NTP time; failures conservatively lock objects. Governance bypass requires both header and permission, so authorization regressions can block legitimate operations. Replica handling deliberately differs from normal writes and must stay aligned with replication semantics. Passing precomputed permission errors into `checkPutObjectLockAllowed` makes caller correctness important.

Test signals: no direct tests in this subset. Lifecycle and delete tests may indirectly encounter object-lock paths only if metadata is configured, which these tests do not do. Dedicated object-lock tests are needed for compliance/governance/legal-hold matrices.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-object-lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-policy-handlers.go -->
## sources/object-store/minio/cmd/bucket-policy-handlers.go

Purpose: implements S3 bucket policy PUT, GET, and DELETE handlers. Policies are validated, stored in bucket metadata, returned as JSON, and replicated through site-replication hooks.

Important APIs and functions: `maxBucketPolicySize` enforces the S3 20 KiB policy limit. `bucketPolicyConfig` names the metadata slot as `policy.json`. `PutBucketPolicyHandler` authorizes `policy.PutBucketPolicyAction`, checks bucket existence, requires positive Content-Length, rejects oversized policy bodies, parses with `policy.ParseBucketPolicyConfig`, rejects empty policy version, stores canonical JSON through `globalBucketMetadataSys.Update`, and calls `globalSiteReplicationSys.BucketMetaHook`. `DeleteBucketPolicyHandler` authorizes delete, checks bucket existence, deletes metadata through `globalBucketMetadataSys.Delete`, and emits a replication hook. `GetBucketPolicyHandler` authorizes get, checks bucket existence, loads through `globalPolicySys.Get`, marshals JSON, and writes it.

Control flow: all handlers follow context/audit/objectAPI/auth/bucket-exists patterns. PUT reads the exact declared content length using `io.LimitReader`, converts parser errors into `MalformedPolicy` API errors, and persists marshaled policy rather than raw request bytes. DELETE returns no content on success. GET uses policy subsystem rather than metadata system directly.

State and persistence behavior: policy JSON is stored in bucket metadata with an updated-at timestamp. PUT and DELETE notify site replication using the original policy bytes for PUT and timestamp-only metadata for DELETE.

Dependencies and integration points: integrates HTTP request handling, MinIO auth, bucket metadata system, policy parser/evaluator, site replication metadata hooks, mux route vars, and audit logging.

Risks: PUT relies on `ContentLength`; chunked or missing-length policy uploads are rejected. Parser/canonical JSON output can change response ordering. Site replication hook failures are logged with `replLogIf` rather than failing the client after local persistence succeeds.

Test signals: `bucket-policy-handlers_test.go` covers create bucket concurrency, policy PUT validation, oversized/missing body, invalid policy, resource bucket mismatch, missing/invalid buckets, empty version, GET/DELETE behavior, anonymous request denial, V2/V4 signing, and nil object-layer paths. It does not assert replication hook behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-policy-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-policy-handlers_test.go -->
## sources/object-store/minio/cmd/bucket-policy-handlers_test.go

Purpose: tests bucket creation concurrency and bucket policy HTTP handlers across V4/V2 signed requests, anonymous requests, invalid inputs, and nil object-layer handling.

Important APIs and helpers: helper policy builders create anonymous read/write bucket/object policies. `TestCreateBucket` verifies concurrent `MakeBucket` has exactly one success. `TestPutBucketPolicyHandler`, `TestGetBucketPolicyHandler`, and `TestDeleteBucketPolicyHandler` use request builders, policy templates, `getPutPolicyURL`, `getGetPolicyURL`, `getDeletePolicyURL`, and policy parser equality checks.

Control flow: create-bucket launches 100 goroutines synchronized by a channel and expects one success plus 99 `BucketExists` errors. PUT policy tests valid policy, over-limit content length, zero content length, nil body, empty credentials, malformed JSON, policy resource mismatch, nonexistent/invalid buckets, and empty `Version`. GET tests first install a policy, then fetch valid/nonexistent/invalid buckets and compares parsed policy equality for successful responses. DELETE installs policy, deletes it for valid/nonexistent/invalid buckets, repeats for V2 signing, and checks anonymous/nil object-layer paths.

State and persistence behavior: tests mutate object-layer bucket state and bucket metadata policy state. They verify policy persistence is visible through GET and removable by DELETE. Anonymous tests verify bucket policy changes do not grant access to policy-management APIs.

Dependencies and integration points: integrates object-layer API, HTTP router, signing V2/V4, policy parser, bucket metadata persistence, anonymous access harness, and nil object-layer harness.

Risks: some request bodies are `io.ReadSeeker` instances reused between V4 and V2 requests inside the same test case; depending on request builder behavior, reader position could matter. Exact policy equality is parsed before comparison, reducing JSON ordering brittleness. Tests do not directly inspect metadata updated-at timestamps or replication hooks.

Test signals: strong coverage for policy handler validation and auth behavior. Missing signals include site-replication hook failures, concurrent policy updates, and behavior for chunked/missing content-length transports beyond explicit zero length.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-policy-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-policy.go -->
## sources/object-store/minio/cmd/bucket-policy.go

Purpose: provides the bucket policy subsystem and request-condition construction used by authorization decisions. It loads stored bucket policies, evaluates actions, maps request/credential/header/query context into policy condition keys, and converts between MinIO and minio-go policy representations.

Important APIs and functions: `PolicySys.Get` loads a bucket policy via `globalBucketMetadataSys.GetPolicyConfig`. `PolicySys.IsAllowed` evaluates `policy.BucketPolicyArgs`, falling back to owner-only allow when policy is absent. `getSTSConditionValues` extracts STS duration. `getConditionValues` builds policy condition values including time, source IP, user agent, referer, principal type, user IDs, version ID, signature version, auth type, location constraint, signature age, object tags, object-lock headers, arbitrary headers/query values, JWT string claims, and groups. `PolicyToBucketAccessPolicy` and `BucketAccessPolicyToPolicy` bridge MinIO's internal policy type with minio-go's type.

Control flow: condition construction normalizes derived credentials to parent user, classifies principal type, finds version ID from query or copy-source, maps auth type to signature/auth strings, clones headers and query values before consuming special keys, expands object tags into existing/request tag keys, appends duplicate values, and folds JWT/group claims into the result.

State and persistence behavior: the subsystem is read-only except for logging unexpected metadata errors. It consumes parsed policy objects stored by bucket metadata.

Dependencies and integration points: integrates auth credentials, request auth-type helpers, handler source IP utilities, MinIO HTTP constants, object tags parser, JWT claims, policy condition evaluation, and json/jsoniter conversion.

Risks: condition keys are string-sensitive and must match policy engine expectations. Header/query cloning prevents mutation of requests but broad inclusion of headers and query values means new request inputs can affect policy evaluation. Derived credential parent-user substitution is security-sensitive. `IsAllowed` logs unexpected errors and falls back to owner-only behavior, so metadata errors may deny non-owner access even if a policy should allow it.

Test signals: policy handler tests cover storing and fetching policies, and bucket handler tests indirectly cover anonymous policy authorization. There are no direct table tests in this subset for `getConditionValues`, JWT claims, object-lock condition keys, copy-source version IDs, or conversion helpers.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-quota.go -->
## sources/object-store/minio/cmd/bucket-quota.go

Purpose: implements bucket quota retrieval, cached bucket usage lookup, quota JSON parsing, and hard-quota enforcement before writes.

Important APIs and functions: `BucketQuotaSys.Get` loads quota config from `globalBucketMetadataSys.GetQuotaConfig`. `NewBucketQuotaSys` constructs the subsystem. `bucketStorageCache` caches `DataUsageInfo`. `BucketQuotaSys.Init` initializes a 10-second cache with last-good/no-wait options and a 2-second backend load timeout. `GetBucketUsageInfo` retrieves cached usage and logs fallback conditions. `parseBucketQuota` unmarshals `madmin.BucketQuota` and validates it, explicitly rejecting old `fifo` quota configs. `enforceQuotaHard` and package helper `enforceBucketQuotaHard` block writes that would exceed hard quota.

Control flow: quota enforcement ignores negative sizes, loads quota config, selects quota size from `Size` or legacy `Quota`, rejects if the incoming object size itself exceeds quota, then fetches cached bucket usage and rejects if current size plus incoming size reaches quota. Cache initialization is idempotent and uses the current object layer.

State and persistence behavior: quota configuration is persisted by bucket metadata elsewhere; this file reads it. Usage state is cached in-memory through `cachevalue` and populated from backend data usage. Enforcement uses cached usage, so it is approximate within cache freshness and backend load success.

Dependencies and integration points: integrates madmin quota types, bucket metadata system, data usage loader, cachevalue, object-layer initialization, MinIO logging, and write paths that call `enforceBucketQuotaHard`.

Risks: stale or missing usage data can allow temporary quota overshoot; when no reliable usage is available, enforcement may not block except for single object size exceeding quota. The comparison uses `>=`, so writes exactly reaching quota are rejected. `GetBucketUsageInfo` logs a formatting string inside `errors.New`, losing the bucket/error interpolation in one branch.

Test signals: no direct tests in this subset. Quota parsing, cache fallback, exact-boundary enforcement, and stale usage behavior need dedicated coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-quota.go -->
