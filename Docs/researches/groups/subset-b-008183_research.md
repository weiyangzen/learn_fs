# subset-b-008183 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/background-newdisks-heal-ops.go -->
# sources/object-store/minio/cmd/background-newdisks-heal-ops.go

Purpose: Implements MinIO automatic healing for newly added or replaced local erasure-set disks, including persistent progress tracking in `.minio.sys/buckets/.healing.bin`. The file lets a node resume a partially completed disk heal after restart, expose status through `madmin.HealingDisk`, and coordinate one healer per erasure set.

Important APIs/types/functions: `healingTracker` is the durable state object, with disk identity/location, endpoint/path, current bucket/object cursor, bucket queues, healed buckets, totals, counters, retry count, and `Finished`. `loadHealingTracker`, `initHealingTracker`, `save`, `update`, `delete`, `bucketDone`, `resume`, `setQueuedBuckets`, and `toHealingDisk` form the persistence and reporting API. `initAutoHeal`, `getLocalDisksToHeal`, `healFreshDisk`, and `monitorLocalDisksAndHeal` connect this tracker to server startup and background disk monitoring.

Control flow: Startup calls `initAutoHeal`, starts normal background healing, pushes local unformatted/incomplete disks when auto-drive healing is enabled, and launches the monitor. The monitor polls every 10 seconds, reformats healable disks with `HealFormat`, and starts one goroutine per endpoint. `healFreshDisk` looks up the disk, skips root drives, acquires a namespace lock for the pool/set, loads or initializes the tracker, lists buckets plus MinIO metadata buckets, sorts metadata/latest buckets first, records data-usage totals, saves the tracker, and calls `healErasureSet`. On failures it retries up to four attempts, resetting counters to resume from queued buckets; on completion it marks matching heal IDs finished across disks in the set.

State/persistence behavior: Tracker updates are protected by `sync.RWMutex`, serialized with msgp, and written to the disk metadata bucket. Resume state is bucket-granular: per-bucket counters are snapshotted by `bucketDone`, and `resume` rolls counters back to the bucket start. On successful completion, all trackers with the same `HealID` are marked `Finished`, preserving history instead of deleting modern tracker files; pre-February-2023 empty `HealID` trackers are deleted.

Dependencies/integration: Relies on `StorageAPI`, `erasureServerPools`, erasure set healing, namespace locks, global local drive maps, `globalBackgroundHealState`, `globalMRFState`, data usage cache, MinIO meta bucket paths, `madmin.HealingDisk`, env/config switches, and logging helpers. It is tightly coupled to drive endpoint location and distributed erasure-set layout.

Risks/test signals: Correctness depends on monotonic tracker saves, lock coverage, and consistent disk IDs. A stale or corrupt `.healing.bin` can cause reinitialization or skipped work; bucket-granular resume can repeat work inside a partially healed bucket. The generated msgp tests cover serialization of `healingTracker`; this file has no direct behavioral unit test for monitor concurrency, retry behavior, or tracker cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/background-newdisks-heal-ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/background-newdisks-heal-ops_gen.go -->
# sources/object-store/minio/cmd/background-newdisks-heal-ops_gen.go

Purpose: Generated `tinylib/msgp` serialization for `healingTracker`, used by `background-newdisks-heal-ops.go` to persist disk-healing progress in `.healing.bin`.

Important APIs/types/functions: Implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `*healingTracker`. The serialized map has 29 fields: ID, pool/set/disk indexes, path, endpoint, started/last update times, object totals, healed/failed/skipped item and byte counters, bucket/object cursor, resume counters, queued/healed buckets, heal ID, retry attempts, and finished flag.

Control flow: Decode/unmarshal reads a msgpack map, switches on string field names, populates primitive fields, resizes bucket slices, and skips unknown fields for forward compatibility. Encode/marshal writes the same fixed field set in generated order. `Msgsize` computes an upper-bound allocation estimate used by `MarshalMsg`.

State/persistence behavior: The file defines the binary compatibility boundary for on-disk healing trackers. Fields with `msg:"-"` in the source type, such as `disk` and mutex, are intentionally omitted and must be reattached after load. Because unknown fields are skipped, older binaries can ignore newer fields, but missing fields fall back to Go zero values.

Dependencies/integration: Depends only on `github.com/tinylib/msgp/msgp` and the source `healingTracker` type. It is called by `loadHealingTracker`, `save`, and any code that writes or reads `.healing.bin`.

Risks/test signals: Manual edits would be overwritten by `go generate`. Schema changes in `healingTracker` must regenerate this file or persisted state will diverge. Generated tests verify marshal/unmarshal, streaming encode/decode, skip behavior, and benchmark allocation/performance, but they only use zero-value data and do not test compatibility with real tracker payloads.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/background-newdisks-heal-ops_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/background-newdisks-heal-ops_gen_test.go -->
# sources/object-store/minio/cmd/background-newdisks-heal-ops_gen_test.go

Purpose: Generated tests and benchmarks for `healingTracker` msgp serialization.

Important APIs/types/functions: `TestMarshalUnmarshalhealingTracker` checks `MarshalMsg`, `UnmarshalMsg`, and `msgp.Skip` leave no trailing bytes. `TestEncodeDecodehealingTracker` exercises streaming `msgp.Encode`, `msgp.Decode`, `Msgsize`, and reader skip. Benchmarks cover marshal, append marshal, unmarshal, encode, and decode paths.

Control flow: Tests instantiate a zero-value `healingTracker`, serialize it, deserialize it into another value or itself, and fail on serialization errors or unread bytes. Benchmarks reuse encoded bytes and `msgp.NewEndlessReader` for repeated decode measurement.

State/persistence behavior: No disk state is touched; it indirectly protects the `.healing.bin` persistence format by ensuring the generated methods round-trip syntactically valid payloads.

Dependencies/integration: Uses Go `testing`, `bytes.Buffer`, and `tinylib/msgp`. It is generated alongside the msgp implementation and should be refreshed rather than manually maintained.

Risks/test signals: The tests are shallow: they do not populate non-zero fields, slices, times, retry counters, or finished state, and they do not compare semantic equality after decoding. They are still useful as smoke tests for generated code compilation, no-leftover-byte handling, and basic msgp compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/background-newdisks-heal-ops_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-expire.go -->
# sources/object-store/minio/cmd/batch-expire.go

Purpose: Defines and runs MinIO batch expiration jobs. These jobs scan a bucket, match object/delete-marker versions against YAML rules, delete matching versions or whole version histories, update persistent job metrics, retry failed deletes, and optionally notify an HTTP endpoint.

Important APIs/types/functions: `BatchJobExpirePurge` validates `retainVersions`. `BatchJobExpireFilter` models one rule and implements YAML location capture, `Matches`, and `Validate`. `BatchJobExpire` stores API version, bucket, multi-prefix field, notification, retry, and rules, with `RedactSensitive`, `Notify`, `Expire`, `Start`, and `Validate`. `expireObjInfo` carries an `ObjectInfo` plus `ExpireAll` and delete-marker counts. `objInfoCache` maps delete requests back to object metadata for metric tracking.

Control flow: `Start` loads or initializes `batchJobInfo`, configures worker count from `_MINIO_BATCH_EXPIRATION_WORKERS`, walks all requested prefixes with all versions sorted newest first, and starts a saver goroutine. As walk results arrive, only latest versions are matched against rules; once a latest version matches, older versions of the same object are counted until `retainVersions` is exceeded. `pushToExpire` batches more than ten selected versions to `batchObjsForDelete`, which separates whole-object prefix deletion (`ExpireAll`) from explicit version deletes. Version deletes use `DeleteObjects` in `maxDeleteList` chunks; failures are retried with configured/default attempts and delay, and metrics are updated per object or per multi-version delete.

State/persistence behavior: Progress is stored in `batchJobInfo` reports under `batch-jobs/reports/<jobID>/batch-expire.bin`, with periodic `updateAfter` saves plus a final save on exit. The last object cursor supports resume through `WalkOptions.Marker`. Metrics are also cached in `globalBatchJobsMetrics`. Notification tokens are redacted when job definitions are described.

Dependencies/integration: Integrates with `ObjectLayer` walk/delete APIs, bucket versioning, `BatchJobPrefix`, common YAML types, msgp-generated persistence, global batch job metrics/config, MinIO trace metrics, `tags.ParseObjectTags`, metadata/header helpers, wildcard matching, `workers.Workers`, and admin handler job submission in `batch-handlers.go`.

Risks/test signals: Rule semantics are sensitive: tags/metadata filters are disallowed for `deleted`, `CreatedBefore` must be in the past, and purge of all versions uses prefix delete optimization. `maxBatchRules` is 50 but the error text says 100, a documentation/UX mismatch. Resume by last object may repeat in-flight work after crashes. Unit tests parse representative single and multiple prefix YAML; generated tests cover msgp for expire structs, but there are no focused unit tests for rule matching, retry accounting, walk ordering, or delete failure recovery.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-expire.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-expire_gen.go -->
# sources/object-store/minio/cmd/batch-expire_gen.go

Purpose: Generated msgp serialization for batch-expire job configuration types that are embedded in persisted `BatchJobRequest` values and possibly reused across job state handling.

Important APIs/types/functions: Provides `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `BatchJobExpire`, `BatchJobExpireFilter`, and `BatchJobExpirePurge`. `BatchJobExpire` serializes API version, bucket, prefix, notification config, retry config, and rule list. `BatchJobExpireFilter` serializes older-than duration, optional created-before time, tags, metadata, size filter, type, name, and nested purge retain count. `BatchJobExpirePurge` serializes retain versions.

Control flow: Reader methods consume msgpack maps and skip unknown fields. Slice fields are resized or reused before decoding element structs. Optional `CreatedBefore` uses nil-aware decode/encode, allocating `time.Time` when present. Writer methods emit fixed map sizes and call nested generated methods for common types.

State/persistence behavior: This is the binary format for expire job definitions when `BatchJobRequest` is saved under `batch-jobs/<jobID>`. It excludes unexported YAML source-location fields, so line/column diagnostics are parse-time only and are not recoverable from persisted msgp.

Dependencies/integration: Depends on `time`, `tinylib/msgp`, `BatchJobPrefix`, `BatchJobNotification`, `BatchJobRetry`, `BatchJobKV`, `BatchJobSizeFilter`, and `xtime.Duration` generated methods. Used indirectly by `BatchJobRequest.MarshalMsg` and `UnmarshalMsg`.

Risks/test signals: Any structural change to expire YAML types requires regeneration. Unknown fields are skipped, which helps forward compatibility, but renamed fields or changed semantics can silently zero defaults. Generated tests exercise zero-value round trips and benchmarks for all three types; they do not validate non-empty rules, optional time pointers, or compatibility across releases.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-expire_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-expire_gen_test.go -->
# sources/object-store/minio/cmd/batch-expire_gen_test.go

Purpose: Generated smoke tests and benchmarks for msgp methods on batch expiration structs.

Important APIs/types/functions: Covers `BatchJobExpire`, `BatchJobExpireFilter`, and `BatchJobExpirePurge` with marshal/unmarshal tests, streaming encode/decode tests, skip tests, and marshal/append/unmarshal/encode/decode benchmarks.

Control flow: Each test uses a zero-value instance, serializes it, deserializes it, checks no trailing bytes remain, validates `msgp.Skip`, and confirms streaming decode does not error. Benchmarks report allocations and encoded byte lengths.

State/persistence behavior: No live job state or object storage is mutated. The tests protect the generated serialization contract used when expire job requests are persisted through `BatchJobRequest`.

Dependencies/integration: Uses `bytes`, `testing`, and `tinylib/msgp`. The file is regenerated by msgp and should not be edited manually.

Risks/test signals: The tests are compilation and serialization smoke coverage only. They do not populate rules, tags, metadata, `CreatedBefore`, or purge counts, so regressions in non-zero field semantics may pass. Still, they catch generated method drift, malformed msgpack output, and `Msgsize` underestimation warnings.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-expire_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-expire_test.go -->
# sources/object-store/minio/cmd/batch-expire_test.go

Purpose: Unit test for YAML parsing of batch expiration job definitions, especially the `prefix` field shape.

Important APIs/types/functions: `TestParseBatchJobExpire` unmarshals two YAML documents into `BatchJobRequest`: one with `expire.prefix` as a string and another with `expire.prefix` as a list. It verifies `job.Expire.Prefix.F()` returns the expected slice using `slices.Equal`.

Control flow: The test builds representative YAML with two rules (`object` and `deleted`), tags, metadata, size filters, purge config comments, notification, and retry. It fails immediately on YAML unmarshal error, then asserts prefix normalization.

State/persistence behavior: Pure parser test; it does not save jobs, validate buckets, delete objects, or use msgp state.

Dependencies/integration: Exercises `gopkg.in/yaml.v3`, `BatchJobRequest`, `BatchJobExpire`, `BatchJobPrefix.UnmarshalYAML`, `xtime.Duration` parsing, and common nested job types.

Risks/test signals: It verifies representative YAML remains accepted and that single/multiple prefixes normalize correctly. It does not call `Validate`, does not inspect parsed rule fields beyond prefixes, and does not cover invalid YAML, future `createdBefore`, negative retry, or deletion behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-expire_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-handlers.go -->
# sources/object-store/minio/cmd/batch-handlers.go

Purpose: Implements MinIO batch job admin surface, common job request/state persistence, batch replication execution, job pool scheduling, cancellation, resumption, cleanup, metrics, tracing, and prefix YAML support.

Important APIs/types/functions: `BatchJobRequest` is the top-level union for replicate, key-rotate, and expire jobs. `notifyEndpoint`, `RedactSensitive`, `Type`, `Validate`, `save`, `load`, `delete`, and `getJobReportPath` manage job definitions. Replication functions include `ReplicateFromSource`, `copyWithMultipartfromSource`, `StartFromSource`, `toObjectInfo`, `writeAsArchive`, `ReplicateToTarget`, `batchReplicationOpts`, and `BatchJobReplicateV1.Start/Validate`. `batchJobInfo` tracks durable progress and implements `loadOrInit`, `loadByPath`, `updateAfter`, metric conversion, and counters. Admin handlers include `ListBatchJobs`, `BatchJobStatus`, `DescribeBatchJob`, `StartBatchJob`, and `CancelBatchJob`. `BatchJobPool` owns worker goroutines, job queue, cancelers, resume, and report cleanup. `batchJobMetrics` owns in-memory metrics and trace publishing. `BatchJobPrefix` supports string-or-list YAML prefixes.

Control flow: Admin `StartBatchJob` reads a 4 MiB-limited YAML body, fills snowball defaults for replication, validates the job, assigns a type-prefixed ID with local node token, persists the request, and queues it. Workers dispatch by job type. Replication from local walks source objects, optionally snowballs small MinIO-to-MinIO objects, and uses workers for normal object copies/deletes. Remote-to-local uses minio-go listing/stat/tag retrieval, converts remote metadata to `ObjectInfo`, applies filters, and copies into the local `ObjectLayer`. Both paths retry failed jobs, reset failure counters between attempts, save metrics periodically and finally, and notify endpoints.

State/persistence behavior: Job definitions live under `batch-jobs/<jobID>/job.bin` via msgp. Job reports live under `batch-jobs/reports/<jobID>/{batch-replicate.bin,batch-expire.bin,...}` with a 4-byte format/version header followed by msgp `batchJobInfo`. `BatchJobPool.resume` scans persisted requests on startup and only queues jobs whose node token matches the local proxy endpoint. Completed/failed report and metric retention is three days. In-memory metrics clone under locks.

Dependencies/integration: Heavily integrates with `ObjectLayer`, minio-go clients/core, S3 credentials, encryption/hash/replication options, bucket versioning, config persistence, admin policy checks, proxy request routing, global trace, batch config throttles, `madmin` response types, `workers`, YAML/msgp, and shared types from `batch-expire.go`, `batch-replicate.go`, key-rotation files, and common type files.

Risks/test signals: Sensitive areas include nil handling in `BatchJobRequest.RedactSensitive` if only one job type is set, retry counter accounting, cancellation map cleanup, resume ownership by encoded node index, remote metadata/tag filtering differences, multipart cleanup on failures, and snowball fallback paths. Tests cover prefix YAML parsing and generated msgp round trips for request/state; there are no direct tests for admin authorization flow, queue saturation, resume, cancellation, remote copy behavior, trace publication, or report cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-handlers_gen.go -->
# sources/object-store/minio/cmd/batch-handlers_gen.go

Purpose: Generated msgp serialization for batch handler types: `BatchJobPrefix`, `BatchJobRequest`, and durable `batchJobInfo`.

Important APIs/types/functions: `BatchJobPrefix` serializes as a string array. `BatchJobRequest` serializes ID, user, started time, and nullable nested `Replicate`, `KeyRotate`, and `Expire` request pointers. `batchJobInfo` serializes compact keyed progress fields: version (`v`), job ID/type, start/last update, retry/attempt counts, complete/failed flags, last bucket/object, object/delete-marker success/failure counts, and byte counters.

Control flow: Decode/unmarshal paths use map-key switches and skip unknown fields. Request decoding allocates nested job structs when a non-nil value is present. Prefix decoding resizes the slice directly from an array header. `batchJobInfo` uses short msgp keys to reduce report size, while `BatchJobRequest` uses descriptive keys.

State/persistence behavior: This file defines the binary layout for persisted job requests and job reports. It must match the 4-byte format/version framing implemented by `batchJobInfo.updateAfter` and `loadByPath`; the frame is not handled here, only the body.

Dependencies/integration: Depends on `tinylib/msgp` and generated methods for nested replicate/key-rotation/expire types. Called by `BatchJobRequest.save/load`, `batchJobInfo.updateAfter/loadByPath`, and generated tests.

Risks/test signals: Adding a new batch job type or changing report counters requires regenerating this file and checking backward compatibility. Unknown field skipping helps additive changes, but missing fields decode to zero, which can affect resume and status output. Generated tests cover zero-value round trips and benchmarks for prefix, request, and info.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-handlers_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-handlers_gen_test.go -->
# sources/object-store/minio/cmd/batch-handlers_gen_test.go

Purpose: Generated tests and benchmarks for msgp methods used by batch job prefix, request, and progress state.

Important APIs/types/functions: Covers `BatchJobPrefix`, `BatchJobRequest`, and `batchJobInfo` with marshal/unmarshal tests, streaming encode/decode tests, skip tests, and performance benchmarks.

Control flow: Each type is instantiated as a zero value, marshaled, unmarshaled, checked for no remaining bytes, skipped with `msgp.Skip`, and streamed through `msgp.Encode`/`Decode`. Benchmarks exercise allocation and throughput for both byte-slice and streaming APIs.

State/persistence behavior: Indirectly protects persisted job definitions and reports. It does not create object-store config entries or include the report header bytes used by `batchJobInfo`.

Dependencies/integration: Uses `bytes`, `testing`, and `tinylib/msgp`; generated by the same msgp tool as the implementation.

Risks/test signals: The tests do not populate nested replicate/expire/key-rotate pointers, prefix entries, timestamps, or counters, so they are not semantic equality tests. They mainly guard generated code health and basic reader/writer compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-handlers_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-handlers_test.go -->
# sources/object-store/minio/cmd/batch-handlers_test.go

Purpose: Unit test for `BatchJobPrefix.UnmarshalYAML`, ensuring batch job prefixes can be specified as either a scalar string or a YAML sequence.

Important APIs/types/functions: `TestBatchJobPrefix_UnmarshalYAML` defines a temporary struct with `Prefix BatchJobPrefix`, then runs table cases for `prefix: "foo"` and `prefix: ["foo","bar"]`. It asserts unmarshal success and exact slice output from `F()`.

Control flow: The test uses subtests, unmarshals each YAML snippet into the target struct, compares error presence with `wantErr`, and checks prefix equality with `slices.Equal`.

State/persistence behavior: Parser-only test. It does not persist requests, run jobs, or serialize msgp.

Dependencies/integration: Exercises `gopkg.in/yaml.v3` and the shared `BatchJobPrefix` type used by both expiration and replication jobs.

Risks/test signals: Good coverage for the supported flexible prefix syntax. It does not cover invalid prefix shapes, nil/empty prefix, or integration with full `BatchJobRequest` validation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-job-common-types.go -->
# sources/object-store/minio/cmd/batch-job-common-types.go

Purpose: Defines shared YAML/configuration primitives used across MinIO batch jobs: user-facing validation errors, wildcard key/value matching, notification endpoints, retry policy, snowball transfer options, size filters, and human-readable byte parsing.

Important APIs/types/functions: `BatchJobYamlErr` preserves line/column-aware error messages. `BatchJobKV` captures key/value pairs and implements YAML location capture, `Validate`, `Empty`, and wildcard `Match`. `BatchJobNotification` and `BatchJobRetry` capture endpoint/token and retry attempts/delay; retry rejects negative values. `BatchJobSnowball` configures archive-based replication with optional pointer fields and validates batch size plus `SmallerThan`. `BatchJobSizeFilter` stores upper/lower bounds with `InRange` and `Validate`. `BatchJobSize.UnmarshalYAML` parses humanized byte strings.

Control flow: Each YAML-aware type decodes through an alias to avoid recursion and records the YAML node location for later diagnostics. Filters apply inclusive-style checks as implemented: an upper bound rejects `sz > upper`, and a lower bound rejects `sz < lower`. Wildcard matching is case-insensitive on keys and wildcard-based on values.

State/persistence behavior: These structs are embedded in persisted job requests via generated msgp, but their unexported line/column metadata is not serialized. Pointer fields in `BatchJobSnowball` allow `StartBatchJob` to distinguish omitted values and fill defaults before validation.

Dependencies/integration: Used by expiration, replication, key rotation, admin handlers, and generated serializers. Depends on `humanize.ParseBytes`, MinIO wildcard matching, YAML v3, and time durations.

Risks/test signals: `BatchJobSnowball.Validate` dereferences pointer fields and assumes defaults were filled; calling it before defaulting can panic. The error string for non-positive snowball batch appears to say "non positive zero", which is likely typo-prone. Size-bound comments describe strict inequalities, while implementation treats equality as in range for each individual bound and rejects equal lower/upper during validation. Tests cover size range and invalid range validation; msgp tests cover serialization smoke paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-job-common-types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-job-common-types_gen.go -->
# sources/object-store/minio/cmd/batch-job-common-types_gen.go

Purpose: Generated msgp serialization for common batch job configuration types shared by expire, replicate, and handler request persistence.

Important APIs/types/functions: Implements generated methods for `BatchJobKV`, `BatchJobNotification`, `BatchJobRetry`, `BatchJobSize`, `BatchJobSizeFilter`, and `BatchJobSnowball`. Scalar and map fields serialize as expected; `BatchJobSnowball` pointer fields are nil-aware for omitted/defaultable options.

Control flow: Map decoders switch on field names and skip unknown fields. `BatchJobSize` serializes directly as int64. `BatchJobRetry` encodes duration with msgp duration support. `BatchJobSizeFilter` encodes lower/upper `BatchJobSize` fields. `BatchJobSnowball` allocates pointers when non-nil values are decoded.

State/persistence behavior: Defines the binary representation embedded inside `BatchJobRequest` and nested job-specific structs. Unexported YAML line/column fields are absent, so persisted requests keep values but not source diagnostics.

Dependencies/integration: Depends on `tinylib/msgp` and the common source types. Generated methods are invoked by expire, replicate, key-rotate, and request serializers.

Risks/test signals: Regeneration is required after changes to common types. Pointer nil semantics for snowball are important because handler code fills defaults before validation; persisted nils could be unsafe if consumed without defaulting. Generated tests cover zero-value serialization and benchmarks, but non-nil snowball pointers and non-zero sizes/durations are not explicitly asserted.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-job-common-types_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-job-common-types_gen_test.go -->
# sources/object-store/minio/cmd/batch-job-common-types_gen_test.go

Purpose: Generated msgp tests and benchmarks for shared batch job types.

Important APIs/types/functions: Tests and benchmarks cover `BatchJobKV`, `BatchJobNotification`, `BatchJobRetry`, `BatchJobSizeFilter`, and `BatchJobSnowball`. Although `BatchJobSize` has generated methods, this generated test file focuses on the containing filter rather than a standalone size round trip.

Control flow: Each test performs byte-slice marshal/unmarshal, validates no bytes remain, checks `msgp.Skip`, then performs streaming encode/decode and skip. Benchmarks measure marshal, append marshal, unmarshal, encode, and decode.

State/persistence behavior: No external state is touched. It validates serialization methods used inside persisted batch job definitions.

Dependencies/integration: Uses Go `testing`, `bytes.Buffer`, and `tinylib/msgp`. It is generated and tracks the schema in `batch-job-common-types_gen.go`.

Risks/test signals: Coverage is syntactic and zero-value-heavy. It does not verify wildcard matching, retry validation, size parsing, size bounds, notification values, or non-nil snowball pointer preservation. The handwritten tests in `batch-job-common-types_test.go` provide the main semantic coverage for size filters.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-job-common-types_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-job-common-types_test.go -->
# sources/object-store/minio/cmd/batch-job-common-types_test.go

Purpose: Handwritten semantic tests for batch job size filtering and validation.

Important APIs/types/functions: `TestBatchJobSizeInRange` validates `BatchJobSizeFilter.InRange` for an object inside a lower/upper range, below lower, above upper, only upper, and only lower. `TestBatchJobSizeValidate` verifies unspecified, lower-only, and upper-only filters are valid, while lower greater than or equal to upper returns `BatchJobYamlErr` with message `invalid batch-job size filter`.

Control flow: Table-driven subtests call the target method and compare booleans or error messages. Error comparison intentionally uses `BatchJobYamlErr.message()` to ignore YAML line/column fields.

State/persistence behavior: Pure unit tests; they do not parse YAML, persist jobs, or interact with object storage.

Dependencies/integration: Exercises `BatchJobSizeFilter`, `BatchJobSize`, `BatchJobYamlErr`, and Go `testing`.

Risks/test signals: Good focused coverage for size range behavior, including invalid empty ranges. It does not test exact equality at single bounds, humanized byte YAML parsing, or integration with expiration rule matching.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-job-common-types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-replicate.go -->
# sources/object-store/minio/cmd/batch-replicate.go

Purpose: Defines the YAML/configuration schema for MinIO batch replication jobs: source/target resources, credentials, filters, notification/retry flags, and remote/local direction detection.

Important APIs/types/functions: `BatchReplicateFilter` carries newer/older duration filters, created-after/before times, tags, and metadata. `BatchJobReplicateFlags` groups filter, notify, and retry. `BatchJobReplicateResourceType` validates supported resource types (`minio`, `s3`) and exposes `isMinio`. `BatchJobReplicateCredentials` stores access key, secret key, session token, `Empty`, and credential validation via MinIO auth helpers. `BatchJobReplicateTarget` and `BatchJobReplicateSource` describe endpoints, buckets, path style, prefix, credentials, and source snowball settings. `BatchJobReplicateV1` is the v1 request with API version, flags, source, target, and a non-serialized minio core client. `RemoteToLocal` determines direction by presence of source credentials.

Control flow: This file is mostly declarative; validation and execution live in `batch-handlers.go`. Path-style helpers accept `on`, `off`, `auto`, or empty. Resource type validation rejects anything outside MinIO/S3. Credential validation rejects invalid access/secret key shape.

State/persistence behavior: Exported fields are serialized by generated msgp code from the replication file generation set; the runtime `clnt` pointer is excluded with `msg:"-"`. Credentials are persisted in job requests until redacted for describe output, so access controls around job definition storage matter.

Dependencies/integration: Used by batch admin submission, replication start/validate/execute logic, `BatchJobRequest.Type`, redaction, notification, and minio-go client construction. Depends on `miniogo.Core`, internal `auth`, shared common types, and `xtime.Duration`.

Risks/test signals: `RemoteToLocal` infers direction from source credentials rather than endpoint alone; validation must keep those fields consistent. Credentials are sensitive and rely on redaction before display. There are no tests in this subset specifically for replication schema validation, path validation, credential validation, or direction detection; behavior is covered only indirectly by compilation/generated serializers elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-replicate.go -->
