# subset-b-008184 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-replicate_gen.go -->
# sources/object-store/minio/cmd/batch-replicate_gen.go

This generated `tinylib/msgp` file supplies MessagePack serialization for the batch replication job model. It implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize` for `BatchJobReplicateCredentials`, `BatchJobReplicateFlags`, `BatchJobReplicateResourceType`, `BatchJobReplicateSource`, `BatchJobReplicateTarget`, `BatchJobReplicateV1`, and `BatchReplicateFilter`.

The encoded schema is map-based for structs and string-based for enum-like resource types. Important persisted field names are `AccessKey`, `SecretKey`, `SessionToken`, `Filter`, `Notify`, `Retry`, `Type`, `Bucket`, `Prefix`, `Endpoint`, `Path`, `Creds`, `Snowball`, `APIVersion`, `Target`, `Source`, `NewerThan`, `OlderThan`, `CreatedAfter`, `CreatedBefore`, `Tags`, and `Metadata`. Nested structs such as credentials and flags are expanded explicitly rather than delegated everywhere, which makes schema drift easy to miss if source struct definitions change without regenerating the file.

Control flow is the standard msgp pattern: read a map header, switch on each map key, decode known fields, and call `msgp.Skip` for unknown fields. Slice fields allocate or reuse backing arrays for prefixes, tags, and metadata. The marshal paths append into caller-provided buffers using `msgp.Require` and return leftover bytes from unmarshalling, so callers and tests can detect trailing data.

State and persistence behavior matters because these codecs are used for batch job definitions and resume metadata. Any field rename, type change, or generated-code mismatch can make previously persisted replication jobs decode incorrectly. Unknown-field skipping gives limited forward compatibility, but removed or retyped fields still risk zero-value behavior.

Dependencies are `github.com/tinylib/msgp/msgp` plus the batch-job types declared elsewhere in `cmd`. Test signals come from `batch-replicate_gen_test.go`, which exercises round-trip encode/decode, skip, and allocation benchmarks for each generated type. Main risks are stale generated code, accidental credential exposure in serialized blobs, and insufficient semantic tests around non-zero values or unknown-field compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-replicate_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-replicate_gen_test.go -->
# sources/object-store/minio/cmd/batch-replicate_gen_test.go

This generated test file validates the msgp serialization surface generated for batch replication job types. It contains paired tests and benchmarks for `BatchJobReplicateCredentials`, `BatchJobReplicateFlags`, `BatchJobReplicateSource`, `BatchJobReplicateTarget`, `BatchJobReplicateV1`, and `BatchReplicateFilter`.

Each test follows the same control flow: instantiate a zero-value object, call `MarshalMsg(nil)`, unmarshal the bytes into the same object, assert no leftover bytes remain, then call `msgp.Skip` on the encoded payload and assert it consumes the full message. Separate encode/decode tests use `msgp.Encode` into a `bytes.Buffer`, compare the buffer length with `Msgsize`, decode into a fresh value, and verify reader-level `Skip`.

The benchmarks measure marshal, append-style marshal into a preallocated buffer, unmarshal, stream encode, and stream decode. They set byte counts from encoded size and call `ReportAllocs`, so they are useful as allocation/performance regression detectors after struct changes or msgp regeneration.

There is no persistent state in the tests, but they protect persistence compatibility indirectly by ensuring the generated methods remain syntactically functional. Dependencies are `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`.

Risk coverage is shallow: all fixtures are zero-value structs, so the tests do not validate non-empty credentials, multi-prefix values, endpoint strings, snowball config, tags, metadata, retry settings, or notify fields. They also do not assert backward compatibility with older serialized payloads or behavior with unknown fields. Their strongest signal is generated-code health, not semantic correctness of replication jobs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-replicate_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-replicate_test.go -->
# sources/object-store/minio/cmd/batch-replicate_test.go

This hand-written test file verifies YAML parsing behavior for batch replication job definitions. The single test, `TestParseBatchJobReplicate`, unmarshals representative YAML into `BatchJobRequest` and checks that the source prefix model accepts both a scalar prefix and a list of prefixes.

The first fixture describes a `replicate` job with API version `v1`, local MinIO source bucket `mytest`, scalar prefix `object-prefix1`, disabled snowball transfer, remote MinIO target endpoint `http://127.0.0.1:9001`, credentials, and filter entries for age, tags, and metadata. After `yaml.Unmarshal`, the test asserts `job.Replicate.Source.Prefix.F()` equals `[]string{"object-prefix1"}`.

The second fixture is structurally similar but changes `source.prefix` to a YAML list containing `object-prefix1` and `object-prefix2`. It asserts the normalized prefix accessor returns both values in order. This is an important integration signal because replication job code consumes normalized prefix slices even though user-facing YAML allows a scalar or list shape.

There is no runtime state or persistence in this test. It depends on `gopkg.in/yaml.v3`, `slices.Equal`, and the batch job request model defined elsewhere. The main risk addressed is accidental breakage of flexible YAML decoding for source prefixes. Uncovered risks include validation of endpoints and credentials, target prefix semantics, snowball option parsing, retry/notify defaults, invalid YAML, remote-source tag restrictions, and execution behavior after parsing.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-replicate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-rotate.go -->
# sources/object-store/minio/cmd/batch-rotate.go

This file implements MinIO batch key-rotation jobs. It defines the YAML/JSON job model for rotating encryption metadata on existing objects, validates KMS settings, filters candidate objects, executes rotation concurrently, persists job progress, and emits metrics/audit/notification events.

Important types are `BatchKeyRotationType` (`sse-s3`, `sse-kms`), `BatchJobKeyRotateEncryption`, `BatchKeyRotateFilter`, `BatchKeyRotateNotification`, `BatchJobKeyRotateFlags`, `BatchJobKeyRotateV1`, and `batchKeyRotationJobError`. `BatchJobKeyRotateEncryption.Validate` checks the requested type, rejects leading/trailing spaces in SSE-KMS key IDs, decodes base64 JSON encryption context, copies it into a `kms.Context`, and performs a `GlobalKMS.GenerateKey` probe. `BatchJobKeyRotateV1.Validate` checks API version, bucket existence, KMS availability, encryption options, tag/metadata filter validity, and retry settings.

`KeyRotate` is the per-object operation. It ignores delete markers and purge-status objects, requires the object to already be SSE-S3 or SSE-KMS encrypted, rejects KMS-to-SSE-S3 downgrade, acquires a namespace lock, reloads object info with versioning options, extracts reserved encryption metadata, validates and prepares the new key/context for SSE-KMS, calls `rotateKey`, marks the object info as metadata-only key rotation, and calls `CopyObject` onto the same object/version with `NoLock`.

`Start` resumes or initializes `batchJobInfo`, stores metrics, computes retry settings, defines a `selectObj` filter over mod time, tags, metadata, and KMS key ID, creates a worker pool sized by `_MINIO_BATCH_KEYROTATION_WORKERS`, walks the object layer, and launches per-object retry loops. It records trace metrics, logs/audits terminal failures, tracks current object progress, periodically persists `ri.updateAfter`, applies optional global throttle waits, marks completion/failure, persists final state, and notifies the configured endpoint.

Key dependencies include `ObjectLayer`, bucket versioning, KMS, crypto metadata helpers, tags parsing, batch metrics, env config, worker pool, audit logging, and batch job persistence. Risks include expensive per-object KMS validation, filter edge cases around `CreatedAfter`/`CreatedBefore`, concurrent mutation of shared `batchJobInfo`, lock correctness, KMS context decoding failures, partial progress after retries, and generated msgp schema staying synchronized with these structs. No direct test file in this subset exercises the full rotation execution path; generated tests only cover serialization.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-rotate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-rotate_gen.go -->
# sources/object-store/minio/cmd/batch-rotate_gen.go

This generated `tinylib/msgp` file serializes the batch key-rotation job model. It implements the standard msgp methods for `BatchJobKeyRotateEncryption`, `BatchJobKeyRotateFlags`, `BatchJobKeyRotateV1`, `BatchKeyRotateFilter`, `BatchKeyRotateNotification`, and `BatchKeyRotationType`.

The persisted schema uses map keys `Type`, `Key`, `Context`, `Filter`, `Notify`, `Retry`, `APIVersion`, `Flags`, `Bucket`, `Prefix`, `Encryption`, `NewerThan`, `OlderThan`, `CreatedAfter`, `CreatedBefore`, `Tags`, `Metadata`, `KMSKeyID`, `Endpoint`, and `Token`. `BatchKeyRotationType` is encoded as a string. The unexported `kmsContext` field in `BatchJobKeyRotateEncryption` is ignored by the source annotation, so only the user-supplied base64 context string persists; runtime validation reconstructs the derived context.

Control flow mirrors msgp output: decoders read map headers and switch on field names, skip unknown fields, allocate/reuse slices for tag and metadata filters, and delegate nested types where available. Encoders write fixed map sizes and field names in generated order. `Msgsize` methods provide upper-bound estimates used by append benchmarks and callers that preallocate buffers.

The state impact is high because batch rotation jobs can be persisted/resumed. If source structs change without rerunning msgp generation, persisted job definitions may silently drop new fields or decode old fields incorrectly. Unknown-field skipping supports forward compatibility for extra fields but not type changes. The generated code also serializes notification tokens and key identifiers, so storage and logs around these payloads should be treated as sensitive.

Dependencies are the msgp runtime and the batch rotation model from `batch-rotate.go`. Test signals come from `batch-rotate_gen_test.go`, which validates zero-value round trips and skip behavior. Semantic coverage for non-zero encryption contexts, filters, retry settings, and KMS-key values is absent.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-rotate_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batch-rotate_gen_test.go -->
# sources/object-store/minio/cmd/batch-rotate_gen_test.go

This generated test file verifies the msgp methods for key-rotation job types. It covers `BatchJobKeyRotateEncryption`, `BatchJobKeyRotateFlags`, `BatchJobKeyRotateV1`, `BatchKeyRotateFilter`, and `BatchKeyRotateNotification` with round-trip and benchmark scaffolding.

Each `TestMarshalUnmarshal...` uses a zero-value object, marshals it to bytes, unmarshals it, checks that no bytes are left over, and verifies `msgp.Skip` consumes the payload. Each `TestEncodeDecode...` streams the value through `msgp.Encode`/`msgp.Decode`, logs if `Msgsize` is smaller than the actual buffer, and checks reader `Skip`. Benchmarks measure allocation and throughput for marshal, append marshal, unmarshal, stream encode, and stream decode.

The tests do not create persistent state, but they exercise generated code used for persisted batch key-rotation definitions. Their dependencies are `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`.

The strongest test signal is that generated methods compile and can process the zero-value schema without leftover bytes. Important gaps remain: no non-zero `Type`, `Key`, base64 `Context`, filters, tags, metadata, KMS key IDs, notify endpoint/token, retry values, or full `BatchJobKeyRotateV1` fixtures are asserted. There is also no compatibility fixture for older serialized jobs or unknown-field handling. These tests should be treated as generated-code smoke tests, not validation of batch rotation semantics.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batch-rotate_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/batchjobmetric_string.go -->
# sources/object-store/minio/cmd/batchjobmetric_string.go

This generated `stringer` file provides `String()` for the `batchJobMetric` enum defined elsewhere, with a trim prefix of `batchJobMetric`. It maps metric constants to compact human-readable labels used in metric/logging paths.

The compile-time guard in `_()` indexes an array by `batchJobMetricReplication-0`, `batchJobMetricKeyRotation-1`, and `batchJobMetricExpire-2`. If enum values are reordered or changed without regenerating this file, compilation fails with an invalid array index. `_batchJobMetric_name` stores the concatenated labels `ReplicationKeyRotationExpire`, and `_batchJobMetric_index` slices that string into the three names.

`func (i batchJobMetric) String() string` returns the generated label for valid values and falls back to `batchJobMetric(<number>)` for out-of-range values via `strconv.FormatInt`. There is no persistent state, but the string output is an integration point for observability, metric naming, trace reporting, and diagnostics around replication, key rotation, and expiration batch jobs.

Dependencies are minimal: only `strconv` and the enum constants. Risks are stale generated code when adding new metric types and downstream dashboards depending on exact string values. There is no dedicated test in this subset; compile-time checks are the main safety mechanism.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/batchjobmetric_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/benchmark-utils_test.go -->
# sources/object-store/minio/cmd/benchmark-utils_test.go

This test utility file defines shared benchmark helpers for object-layer write paths. It benchmarks `ObjectLayer.PutObject`, multipart `PutObjectPart`, backend setup for different instance types, parallel put-object workloads, and random test payload generation.

`runPutObjectBenchmark` creates a random bucket, generates repeated-byte data of the requested size, computes MD5, and repeatedly writes distinct object names through `obj.PutObject` using `mustGetPutObjReader`. It validates returned ETags against the expected MD5. `runPutObjectPartBenchmark` creates a multipart upload for a 128 MiB object and loops through parts sized by the benchmark argument, putting each part and checking part ETags.

`benchmarkPutObjectPart`, `benchmarkPutObject`, and `benchmarkPutObjectParallel` prepare temporary test backends with `prepareTestBackend`, clean roots with `removeRoots`, and dispatch to the core benchmark routines. `runPutObjectBenchmarkParallel` uses `b.RunParallel` to write objects concurrently into a single bucket. `getRandomByte` seeds `math/rand` with `UTCNow().UnixNano()` and returns one alphabetic byte; `generateBytesData` repeats that byte to the target size.

State is temporary: buckets, uploads, and backend roots are created during benchmark execution and removed by deferred cleanup. Dependencies include `ObjectLayer`, object reader helpers, hashing helpers, random bucket/object helpers, `go-humanize`, and Go benchmark APIs.

Risks include benchmark-only code using deprecated global `rand.Seed`, possible object-name collisions in the parallel helper because each goroutine starts its local counter at zero, and an apparent off-by-one slice for non-final multipart parts (`(j+1)*partSize-1`) that benchmarks a part one byte short. These helpers are performance signals, not correctness tests, but they can expose allocation and ETag regressions in object write paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/benchmark-utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bitrot-streaming.go -->
# sources/object-store/minio/cmd/bitrot-streaming.go

This file implements streaming bitrot protection for `HighwayHash256S`, where every shard is stored as `hash || data` instead of maintaining one whole-file checksum. It provides writer and reader implementations used by the generic bitrot factory functions.

`streamingBitrotWriter` wraps an `io.WriteCloser`, hash, shard size, optional close wait group, pooled byte buffer, and finished flag. `Write` rejects empty writes as no-ops, rejects writes after the final short shard, rejects buffers larger than the shard size, hashes the provided shard, writes hash bytes followed by data, and propagates errors via `closeWithErr`. `Close` closes the underlying writer, waits for the async disk writer if present, and returns the pooled buffer.

`newStreamingBitrotWriterBuffer` is an in-memory/test helper. `newStreamingBitrotWriter` obtains a buffer from `globalBytePoolCap`, creates a blocking ring buffer wrapped in a deadline writer, starts a goroutine that computes the total on-disk size when object length is known, and calls `disk.CreateFile` with the ring-buffer reader. This decouples shard hashing from disk writes while preserving close ordering with a wait group.

`streamingBitrotReader.ReadAt` requires offsets aligned to shard size and sequential access. On the first read it opens a disk stream at the translated offset `(offset/shardSize)*hashSize + offset`, or uses in-memory data. Each read consumes stored hash bytes and the requested data, recomputes the hash, compares it, and advances `currOffset`. `Close` drains and closes the stream for connection reuse.

Dependencies include `StorageAPI`, MinIO deadline writer and ring buffer utilities, HTTP body draining, global byte pools, and hash algorithms from `bitrot.go`. Risks are strict offset/sequential assumptions, final-shard detection based on short writes, race potential around async writer close, and correctness of translated offsets and `tillOffset` sizing.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bitrot-streaming.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bitrot-whole.go -->
# sources/object-store/minio/cmd/bitrot-whole.go

This file implements whole-file bitrot protection for non-streaming algorithms. Instead of storing per-shard hashes in the object stream, it appends raw bytes to disk while maintaining a hash over the whole written content, then verifies reads using a `BitrotVerifier`.

`wholeBitrotWriter` holds a `StorageAPI`, target volume, file path, shard size, and embedded `hash.Hash`. `Write` appends bytes to the disk file through `disk.AppendFile`, then writes the same bytes into the hash and returns the full input length. `Close` is a no-op. `newWholeBitrotWriter` constructs the writer with `algo.New()`.

`wholeBitrotReader` holds disk location, a verifier containing algorithm and expected sum, a `tillOffset`, and an internal verified buffer. On the first `ReadAt`, it allocates `tillOffset-offset` bytes and calls `disk.ReadFile` with the verifier. Subsequent reads copy out of the verified buffer and shrink it. If the requested buffer is larger than remaining verified data, it returns `errLessData`.

State is local to the reader/writer, but the design relies on the storage layer honoring `BitrotVerifier` during `ReadFile`. The reader caches verified data after the first read, so it assumes the caller reads forward through that cached slice. Dependencies include `StorageAPI`, `context.TODO`, Go `hash` and `io`, and bitrot algorithm definitions.

Risks include no explicit close flushing, memory use proportional to `tillOffset-offset`, limited random-access behavior after the initial read, and reliance on callers passing the exact checksum from `bitrotWriterSum`. Test coverage comes from `bitrot_test.go`, which writes and reads shard-sized chunks for all registered algorithms.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bitrot-whole.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bitrot.go -->
# sources/object-store/minio/cmd/bitrot.go

This file defines MinIO's bitrot algorithm registry, verifier type, factories for whole-file versus streaming bitrot readers/writers, helper close/sum/size routines, stream verification logic, and startup self-test.

The supported algorithms map `SHA256`, `BLAKE2b512`, `HighwayHash256`, and `HighwayHash256S` to string names. `BitrotAlgorithm.New` constructs the corresponding `hash.Hash`, using MinIO's SHA-256 implementation, `blake2b.New512`, or HighwayHash with a fixed 256-bit magic key. `Available`, `String`, `BitrotAlgorithmFromString`, and `NewBitrotVerifier` provide lookup and verification helpers.

`newBitrotWriter` and `newBitrotReader` dispatch to streaming implementations only for `HighwayHash256S`; all other algorithms use whole-file mode. `closeBitrotReaders` and `closeBitrotWriters` close heterogeneous reader/writer slices and preserve per-writer errors. `bitrotWriterSum` returns the whole-file writer checksum and `nil` for streaming writers. `bitrotShardFileSize` accounts for per-shard hash overhead in streaming mode.

`bitrotVerify` verifies either a whole stream against one expected checksum or a streaming layout of repeated hash/data shards. The streaming branch first checks protected file size, uses an ODirect small buffer, reads each stored hash, hashes the following data shard, and returns corruption errors on short reads or mismatches. `bitrotSelfTest` computes deterministic chained hashes for each available algorithm and fatally aborts if any checksum differs from known constants.

Dependencies include highwayhash, BLAKE2b, MinIO SHA-256, internal IO pools, logging, and storage-facing errors. Risks center on algorithm registry compatibility, hard-fail behavior for unsupported algorithms, correct size accounting for streaming layouts, distinguishing `errFileCorrupt` from underlying I/O errors, and self-test constants staying aligned with algorithm implementations. `bitrot_test.go` verifies basic writer/reader interoperability for every registered algorithm.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bitrot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bitrot_test.go -->
# sources/object-store/minio/cmd/bitrot_test.go

This test file exercises the bitrot reader/writer factory path for every algorithm registered in `bitrotAlgorithms`. It is the main direct correctness signal for the bitrot files in this subset.

`testBitrotReaderWriterAlgo` creates a temporary local XL storage backend, creates a test volume, constructs a bitrot writer with object length `35` and shard size `10`, writes three full 10-byte chunks and one 5-byte final chunk, closes the writer if it implements `io.Closer`, then constructs the matching reader with `bitrotWriterSum(writer)` and reads offsets `0`, `10`, `20`, and `30`. For streaming algorithms the sum is nil because hashes are embedded per shard; for whole-file algorithms the writer sum is used by the verifier.

`TestAllBitrotAlgorithms` loops over the algorithm registry and calls the helper. This ensures newly registered algorithms get at least basic write/read coverage if they are added to `bitrotAlgorithms`.

State is temporary filesystem state under `t.TempDir`, plus local storage volumes/files. Dependencies include `newLocalXLStorage`, `newBitrotWriter`, `newBitrotReader`, and storage volume creation.

The test covers successful sequential reads with aligned offsets and final short shard handling. It does not intentionally corrupt data or hashes, test unaligned offsets, test short reads, test random access out of order, verify `bitrotVerify` directly, or assert self-test behavior. It is a useful integration smoke test but not exhaustive corruption-detection coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bitrot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bootstrap-messages.go -->
# sources/object-store/minio/cmd/bootstrap-messages.go

This file implements a small in-memory tracer for bootstrap messages. It records early startup trace events and can replay them into MinIO's pubsub trace stream after subscribers become available.

`bootstrapTraceLimit` caps stored events at `4 << 10`. `bootstrapTracer` contains an RW mutex and a slice of `madmin.TraceInfo`. `globalBootstrapTracer` is the package-level recorder. `Record` takes the write lock and appends an event unless the slice length is already greater than the limit. `Events` copies the current slice under a read lock. `Publish` iterates over the copied events and publishes only entries with non-empty messages unless the context is done.

The state is process-local and transient. It is not persisted; its purpose is preserving useful diagnostics from the bootstrap phase before normal tracing infrastructure is fully wired. Integration points are `madmin.TraceInfo`, `madmin.TraceType`, and `pubsub.PubSub`.

Risks are modest but include the off-by-one style limit check (`len > limit` permits one more than the nominal limit), memory growth up to the trace cap, and event loss after the cap is exceeded. There is no test in this subset. Correctness mostly depends on lock discipline and callers using `globalBootstrapTracer` for early events.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bootstrap-messages.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bootstrap-peer-server.go -->
# sources/object-store/minio/cmd/bootstrap-peer-server.go

This file implements peer configuration verification during distributed MinIO bootstrap. It exposes a grid handler that returns local system configuration and a client loop that waits until enough remote peers are online with matching configuration.

`ServerSystemConfig` captures endpoint count, endpoint command lines, selected hashed `MINIO_*` environment values, and the running binary checksum. `Diff` compares checksum, endpoint count, command-line entries, and environment maps, returning descriptive errors for missing, mismatching, and extra environment keys. `skipEnvs` excludes intentionally node-specific or sensitive variables such as credentials, debug options, operator/plugin versions, and CI/CD markers.

`getServerSystemCfg` lists `MINIO_` environment variables, skips whitelisted names, hashes values with `logger.HashString`, records global endpoint count and command lines, and attaches `binaryChecksum`. `getBinaryChecksum` computes an MD5 of the current executable and falls back to zeroes on errors. `bootstrapRESTServer.VerifyHandler` returns local config via a grid single handler registered by `registerBootstrapRESTHandlers`.

`bootstrapRESTClient.Verify` skips checks once the object layer is initialized, calls the remote verify handler, returns the response to the handler pool, and diffs against local config. `verifyServerSystemConfig` builds one client per unique remote host, repeatedly checks connected peers in parallel with 2-second timeouts, and waits until at least half the remote clients are online and valid. It logs bootstrap trace messages, classifies network versus incorrect-config errors, reports status every 20 retries, and honors context cancellation. `newBootstrapRESTClients` deduplicates endpoints by host.

State is runtime-only except the binary checksum global. Dependencies include grid RPC, endpoint topology, env utilities, logging, set utilities, random jitter, and object-layer initialization. Risks include MD5 being used only as an identity checksum, command-line order sensitivity, environment hash mismatch diagnostics not revealing values, quorum threshold interpretation, and startup delay if peers are unreachable or config differs. Generated msgp files serialize `ServerSystemConfig` for the grid response.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bootstrap-peer-server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bootstrap-peer-server_gen.go -->
# sources/object-store/minio/cmd/bootstrap-peer-server_gen.go

This generated msgp file serializes `ServerSystemConfig`, the bootstrap peer verification payload. It implements `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`.

The encoded schema is a four-field map: `NEndpoints` as int, `CmdLines` as an array of strings, `MinioEnv` as a string-to-string map, and `Checksum` as string. Decoders read map keys and skip unknown fields, which allows extra future fields to be ignored by older readers. Slice and map decoders reuse existing allocations where possible and explicitly nil out fields when encoded lengths are zero.

This serialization is part of startup configuration verification over MinIO's grid transport. It does not persist durable state, but incorrect serialization can cause peers to reject each other or miss real mismatches. The payload intentionally contains hashed environment values rather than raw secrets, but command lines and env key names may still be operationally sensitive.

Dependencies are `github.com/tinylib/msgp/msgp` and the `ServerSystemConfig` type in `bootstrap-peer-server.go`. Test coverage in `bootstrap-peer-server_gen_test.go` verifies zero-value marshal/unmarshal, stream encode/decode, skip behavior, and benchmark allocation profiles. Missing coverage includes non-empty command-line arrays, non-empty environment maps, unknown fields, and mismatched schema compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bootstrap-peer-server_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bootstrap-peer-server_gen_test.go -->
# sources/object-store/minio/cmd/bootstrap-peer-server_gen_test.go

This generated test file validates msgp serialization for `ServerSystemConfig`. It follows the standard generated pattern used elsewhere in this subset.

`TestMarshalUnmarshalServerSystemConfig` marshals a zero-value config, unmarshals it, checks for no leftover bytes, and verifies `msgp.Skip` consumes the whole payload. `TestEncodeDecodeServerSystemConfig` encodes through the streaming API, logs if `Msgsize` underestimates the encoded length, decodes into a new config, then tests reader-level skip. Benchmarks cover marshal, append marshal, unmarshal, stream encode, and stream decode with allocation reporting.

The tests create no durable state and depend only on `bytes`, `testing`, and `github.com/tinylib/msgp/msgp`. Their integration value is protecting the generated codec used by bootstrap grid verification.

Risk coverage is limited because the fixture is zero-value. It does not validate non-empty `CmdLines`, non-empty `MinioEnv`, checksum strings, map ordering effects, unknown fields, or compatibility with older serialized configs. Operational bootstrap correctness is tested elsewhere, if at all; this file only proves the generated methods are structurally usable.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bootstrap-peer-server_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-encryption-handlers.go -->
# sources/object-store/minio/cmd/bucket-encryption-handlers.go

This file implements S3 bucket encryption configuration handlers: put, get, and delete. It stores encryption XML in bucket metadata, validates KMS availability and key usability, and invokes site-replication metadata hooks.

`bucketSSEConfig` names the metadata object `bucket-encryption.xml`. `PutBucketEncryptionHandler` builds request context/audit logging, checks object layer initialization, extracts the bucket, authorizes `policy.PutBucketEncryptionAction`, verifies bucket existence, parses and validates XML with `validateBucketSSEConfig` under `maxBucketSSEConfigSize`, requires `GlobalKMS`, and if a KMS key ID is configured probes it with `GlobalKMS.GenerateKey`. KES key-not-found is translated to `errKMSKeyNotFound`; other KMS failures are returned as API errors. The validated config is marshaled to XML and written through `globalBucketMetadataSys.Update`. The site-replication hook receives base64 XML in `madmin.SRBucketMeta` with type `SSEConfig`, then the handler returns headers-only success.

`GetBucketEncryptionHandler` authorizes `policy.GetBucketEncryptionAction`, checks bucket existence, retrieves the config from `globalBucketMetadataSys.GetSSEConfig`, marshals it, and writes XML. `DeleteBucketEncryptionHandler` authorizes via put-encryption permission, checks bucket existence, deletes the metadata entry, sends a site-replication hook with nil config, and returns 204.

Persistent state is bucket metadata plus site-replicated metadata timestamps. Dependencies include S3 policy auth, bucket metadata subsystem, KMS/KES, XML/base64 encoding, madmin site replication structs, and audit/error response helpers.

Risks include KMS being mandatory even for delete/put paths where behavior may surprise users, correctness of base64 metadata replication, XML size/parse handling, and mapping KMS failures to S3-compatible errors. `bucket-encryption_test.go` covers validation of single-rule SSE-S3 and SSE-KMS XML but not HTTP handlers, KMS failure paths, persistence, or replication hooks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-encryption-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-encryption.go -->
# sources/object-store/minio/cmd/bucket-encryption.go

This file defines the bucket encryption configuration system wrapper and XML validation helper. It is intentionally small, delegating storage to the global bucket metadata system and parsing to the internal bucket encryption package.

`BucketSSEConfigSys` is an empty struct used as an in-memory system facade. `NewBucketSSEConfigSys` returns a new instance. `(*BucketSSEConfigSys).Get` retrieves a bucket's SSE config through `globalBucketMetadataSys.GetSSEConfig` and returns the parsed `*sse.BucketSSEConfig` plus error.

`validateBucketSSEConfig` calls `sse.ParseBucketSSEConfig` on the provided reader and accepts the config only if it contains exactly one rule. If parsing fails, it returns the parse error; if the rule count is not one, it returns `Unsupported bucket encryption configuration`.

There is no local persistent state. The integration points are `globalBucketMetadataSys`, `internal/bucket/encryption`, and the HTTP handlers in `bucket-encryption-handlers.go`. This function is part of the enforcement boundary for what MinIO supports from AWS S3 bucket encryption XML.

Risks include the one-rule restriction rejecting otherwise valid multi-rule AWS configurations, caller assumptions around nil configs on metadata errors, and semantic validation being delegated to `sse.ParseBucketSSEConfig`. `bucket-encryption_test.go` verifies that single-rule AES256 and aws:kms configs pass validation. It does not cover multi-rule rejection or malformed XML.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-encryption.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-encryption_test.go -->
# sources/object-store/minio/cmd/bucket-encryption_test.go

This test file covers `validateBucketSSEConfig`, the parser/validator used by bucket encryption HTTP handlers. `TestValidateBucketSSEConfig` defines XML fixtures and verifies whether validation succeeds.

The first fixture is a single-rule SSE-S3 configuration with `SSEAlgorithm>AES256</SSEAlgorithm>`. The second fixture is a single-rule SSE-KMS configuration with `SSEAlgorithm>aws:kms</SSEAlgorithm>` and `KMSMasterKeyID>my-key</KMSMasterKeyID>`. Both are expected to pass. For failing cases, the test would compare the returned error string to `expectedErr`, but the current table contains no failing entries.

The test has no persistent state and depends only on `bytes`, `testing`, and `validateBucketSSEConfig`. It is a narrow parser-validation signal confirming MinIO accepts the two common single-rule encryption modes.

Coverage gaps are notable: no multi-rule unsupported config, malformed XML, empty config, unsupported algorithms, missing KMS key ID semantics, size limits, HTTP authorization, KMS probing, metadata persistence, or site-replication behavior. Because both fixtures pass, the negative branch in the test is currently unexercised.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-encryption_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-handlers.go -->
# sources/object-store/minio/cmd/bucket-handlers.go

This large file implements major S3 bucket-level HTTP handlers and related helpers. It covers bucket federation DNS initialization, bucket location/listing, multipart upload listing, service bucket listing, multi-object delete, bucket creation/deletion, browser POST policy upload, policy status, object-lock config, and bucket tagging.

`initFederatorBackend` reconciles local buckets with the DNS/etcd federation backend: it lists DNS buckets, detects missing/changed/conflicting entries against `globalDomainIPs`, writes updates concurrently, logs conflicts, and removes stale DNS entries for buckets no longer local. It integrates `globalDNSConfig`, federation flags, and set/errgroup utilities.

Request handlers follow the MinIO S3 pattern: create request context, audit log, fetch bucket from mux vars, ensure `ObjectLayer` is initialized, authorize specific IAM policy actions, call object-layer or metadata APIs, translate errors, and write S3-compatible XML/headers. `GetBucketLocationHandler`, `ListMultipartUploadsHandler`, `ListBucketsHandler`, `HeadBucketHandler`, and `GetBucketPolicyStatusHandler` are mostly read paths, with ListBuckets supporting DNS federation and policy-based filtering for partially authorized users.

`DeleteMultipleObjectsHandler` is a dense write path. It enforces MD5/content length/body size, decodes XML, normalizes object names, authenticates each object/version, validates version IDs, loads object info when replication/object-lock/tiering require it, applies replication delete decisions, enforces retention bypass, deduplicates objects, disables cancellation for the actual delete, calls `DeleteObjects`, builds per-object success/error XML, schedules replication deletes, emits object removal events, and sweeps transitioned tier objects.

`PutBucketHandler` validates object-lock and force-create headers, checks create permissions and extra object-lock permissions, parses location constraints, warns above recommended bucket count, creates the bucket, reconciles DNS when configured, loads metadata, calls site-replication hooks, sets Location, and emits bucket-created events. `DeleteBucketHandler` handles optional force delete with extra authorization and safety checks against object lock or active replication, deletes DNS and metadata, clears resync metadata, calls site-replication hooks, and emits bucket-removed events.

`PostPolicyBucketHandler` implements multipart/form-data browser uploads. It rejects SSE-KMS request headers, parses up to 1000 form parts, limits in-memory form fields, supports MinIO fan-out JSON entries, enforces file-last semantics, verifies POST policy signatures and conditions, handles checksums, metadata, bucket auto-encryption, SSE-C/SSE-S3/SSE-KMS encryption, optional fan-out writes with a 16 MiB cap and concurrent batches, object tags, `PutObject`, event emission, excessive-version audit events, redirects, and success status variants.

Object-lock and tagging handlers persist XML configs through `globalBucketMetadataSys.Update/Delete/Get*`, base64 encode configs for site-replication metadata hooks, and return AWS-compatible XML or status codes. Persistent state touched by this file includes bucket namespace, DNS federation entries, bucket metadata XML files (`object-lock.xml`, `tagging.xml`), replication/delete state, object versions/delete markers, tier cleanup state, and emitted events/audit logs.

Dependencies are broad: IAM policy, mux, object layer, bucket metadata systems, DNS, replication, object lock, tags, crypto/KMS, hash/checksum readers, event subsystem, site replication, tiering, scanner thresholds, and S3 response helpers. Risks include subtle S3 compatibility requirements, multi-delete partial failure mapping, request body memory limits, fan-out concurrency and object-name behavior, object-lock/replication safety checks, DNS rollback on bucket create failure, and many global subsystem interactions. This subset does not include direct tests for these handlers; coverage is likely spread across broader API integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/bucket-handlers.go -->
