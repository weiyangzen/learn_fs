# subset-b-008207 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-client.go -->
## sources/object-store/minio/cmd/storage-rest-client.go

Purpose: implements the remote `StorageAPI` client used when an erasure set disk lives on another MinIO node. It translates local disk calls into either `grid` RPCs for structured metadata operations or authenticated REST/HTTP calls for bulk and streaming payloads.

Important APIs/types/functions: `storageRESTClient` holds the endpoint, REST client, grid subroute, cached disk ID, and one-second `DiskInfo` cache. `isNetworkError` and `toStorageErr` normalize transport and peer errors into canonical disk errors such as `errDiskNotFound`, `errFileNotFound`, `errDiskStale`, and quorum-relevant storage errors. Core methods mirror `StorageAPI`: `DiskInfo`, `StatVol`, `AppendFile`, `CreateFile`, `WriteMetadata`, `UpdateMetadata`, `DeleteVersion`, `WriteAll`, `CheckParts`, `RenameData`, `ReadVersion`, `ReadXL`, `ReadAll`, `ReadFileStream`, `ReadFile`, `ListDir`, `Delete`, `DeleteVersions`, `RenamePart`, `ReadParts`, `RenameFile`, `VerifyFile`, `DeleteBulk`, `StatInfoFile`, `ReadMultiple`, and `CleanAbandonedData`. `newStorageRESTClient` builds the REST base path and grid subroute.

Control flow: every call injects the current disk ID so the server can reject stale-drive requests. Lightweight metadata calls use pre-registered `grid` handlers with typed msgp payloads; read paths that may include inline object data fall back to HTTP GET so the body can be streamed. Long-running HTTP operations use the keepalive framing from the server side and wait with `waitForHTTPResponse` or `waitForHTTPStream`. `ReadMultiple` marshals a request, pipes the framed HTTP stream through msgp decoding, and closes the response channel when complete. `DiskInfo` uses direct grid calls for `NoOp` probes and a short cache for metrics probes to reduce remote fanout.

State and persistence behavior: the client persists no object data locally. Its only mutable state is the atomic disk ID pointer, online/last-connection state inside the REST client, and the cached `DiskInfo`. Actual persistence is delegated to the remote `StorageAPI` implementation after request validation.

Dependencies/integration: integrates with `rest.Client`, internode auth tokens, `grid.Manager` subroutes, msgp-encoded storage structs, `cachevalue`, `bpool` pooled readers, bitrot verifiers, global drive timeout config, and erasure-set disk construction in `erasure-sets.go`/`object-api-common.go`.

Risks/test signals: correctness depends on mapping transport failures to `errDiskNotFound` so quorum code treats dead peers like missing disks. Mixed HTTP and grid transports must keep request parameters and msgp schemas synchronized with `storage-rest-server.go`. Some methods return `errInvalidArgument` for unsupported remote volume creation/listing. `storage-rest_test.go` exercises the client through a two-node test grid for disk info, stat, list, read, append, delete, and rename, but many newer paths such as multipart part metadata, `ReadMultiple`, and cleanup are covered mostly by higher-level object tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-common.go -->
## sources/object-store/minio/cmd/storage-rest-common.go

Purpose: defines the shared storage REST protocol constants and msgp payload structs used by both the remote storage client and server.

Important APIs/types/functions: `storageRESTVersion` is `v63`, with a comment noting the introduction of `RenamePart` and `ReadParts`. `storageRESTPrefix` mounts the storage API under MinIO's reserved bucket path. Method constants define compact endpoint suffixes for health, append/create/read/delete/rename/stat/verify/bulk APIs. Query/form constants define compact keys such as `vol`, `fp`, `did`, `offset`, `length`, `incl-fv`, and bitrot fields. `nsScannerOptions` carries disk ID, scan mode, and a `dataUsageCache`; `nsScannerResp` carries either an incremental `dataUsageEntry` update or final cache.

Control flow: this file has no executable flow beyond constants and type definitions. Its values are consumed by `storage-rest-client.go` while constructing HTTP query strings and by `storage-rest-server.go` while parsing requests and registering routes. The two scanner structs are serialized by generated msgp code for the streaming namespace scanner RPC.

State and persistence behavior: no persistent state is stored here. Protocol version and field names are compatibility state: changing them requires coordinated client/server updates across a cluster.

Dependencies/integration: depends on MinIO reserved path constants and data scanner structs. It is tightly coupled with generated code in `storage-rest-common_gen.go`, generated tests, the storage REST server route table, and remote disk client methods.

Risks/test signals: compact path names are easy to collide; notably both `storageRESTMethodReadFile` and `storageRESTMethodRenameFile` are `"/rfile"`, but they are distinguished by HTTP method/grid use in practice. Protocol additions need version bumps and generated msgp refreshes. Generated msgp tests cover scanner payload serialization, while storage REST integration tests validate a subset of route behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-common_gen.go -->
## sources/object-store/minio/cmd/storage-rest-common_gen.go

Purpose: generated msgp serialization for `nsScannerOptions` and `nsScannerResp`, enabling efficient `grid` streaming of data-usage scanner requests and updates between storage REST clients and servers.

Important APIs/types/functions: for each struct, generated methods implement `DecodeMsg`, `EncodeMsg`, `MarshalMsg`, `UnmarshalMsg`, and `Msgsize`. `nsScannerOptions` serializes map keys `id`, `m`, and `c` for disk ID, scan mode, and optional cache. `nsScannerResp` serializes map keys `u` and `f` for optional update and final cache.

Control flow: decode paths read a map header, switch on compact field names, allocate nested `dataUsageCache` or `dataUsageEntry` values only when the field is non-nil, skip unknown fields for forward compatibility, and wrap field-specific errors with msgp context. encode/marshal paths write fixed map headers and either nil markers or nested msgp payloads. `Msgsize` returns upper-bound estimates used to preallocate buffers.

State and persistence behavior: no independent persistence. These methods serialize scanner state snapshots in memory while a namespace scanner RPC is active; the real scanner cache is maintained by the storage layer.

Dependencies/integration: generated by `github.com/tinylib/msgp` from `storage-rest-common.go` and depends on msgp support from `dataUsageCache` and `dataUsageEntry`. Used by `storageNSScannerRPC` in `storage-rest-server.go` and `storageRESTClient.NSScanner`.

Risks/test signals: generated code must be regenerated whenever scanner structs or msg tags change. The nil-vs-empty distinction matters because the server rejects nil input cache and the client requires a final response. Generated tests verify empty struct round trips, skipping, and benchmarks, but they do not exercise non-empty nested scanner caches.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-common_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-common_gen_test.go -->
## sources/object-store/minio/cmd/storage-rest-common_gen_test.go

Purpose: generated tests and benchmarks for msgp serialization of storage REST namespace scanner payloads.

Important APIs/types/functions: `TestMarshalUnmarshalnsScannerOptions`, `TestEncodeDecodensScannerOptions`, `TestMarshalUnmarshalnsScannerResp`, and `TestEncodeDecodensScannerResp` exercise byte-slice and stream-based round trips. Benchmarks cover marshal, append-style marshal, unmarshal, encode, and decode for both structs.

Control flow: tests instantiate zero-value structs, marshal them, unmarshal and ensure no trailing bytes remain, verify `msgp.Skip` consumes the entire encoded value, and stream encode/decode through a `bytes.Buffer`. Benchmarks use zero values and `msgp.NewEndlessReader` for decode throughput measurements.

State and persistence behavior: all state is in memory. No scanner or disk state is constructed.

Dependencies/integration: depends on `testing`, `bytes`, and `github.com/tinylib/msgp/msgp`. It guards the generated code used by `storageNSScannerRPC`.

Risks/test signals: useful for detecting stale or syntactically broken generated msgp code, but narrow because only zero values are tested. It will not catch nested `dataUsageCache` compatibility issues, scanner update/final sequencing errors, or server-side nil-cache validation regressions.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-common_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-server.go -->
## sources/object-store/minio/cmd/storage-rest-server.go

Purpose: exposes local disks to other MinIO nodes as authenticated storage REST/grid endpoints and owns the server-side implementation of remote `StorageAPI` calls.

Important APIs/types/functions: `storageRESTServer` wraps an endpoint and resolves it to `StorageAPI` via `globalLocalSetDrives`/`globalLocalDrivesMap`. Registered grid handlers include disk info, scanner, read/write metadata, read xl, list dir, rename data/file/part, delete, and stat volume. HTTP handlers cover payload-heavy or streaming routes such as append/create, read file/stream, read version with data, delete versions, verify, stat info, delete bulk, read parts, read multiple, and cleanup. Auth helpers include `validateStorageRequestToken`, `storageServerRequestValidate`, `IsAuthValid`, `IsValid`, and `checkID`. Framing helpers include `keepHTTPReqResponseAlive`, `keepHTTPResponseAlive`, `waitForHTTPResponse`, `streamHTTPResponse`, and `waitForHTTPStream`.

Control flow: incoming HTTP requests authenticate with an internode JWT, enforce timestamp skew, parse form values, and compare the request disk ID with the live disk's ID unless the request intentionally sends an empty disk ID during bootstrap. Grid handlers perform equivalent disk-ID checks through typed params. Long-running operations first send periodic filler bytes, then a success byte or text error; streaming responses send framed data blocks with a byte tag and little-endian block length. `registerStorageRESTHandlers` builds local-drive tables, registers HTTP routes and grid handlers per local endpoint, constructs `xlStorageDiskIDCheck`, and retries failed local disk initialization asynchronously.

State and persistence behavior: this file maintains process-local maps/slices from endpoints to live disk objects under `globalLocalDrivesMu`. Persistent writes are delegated to `StorageAPI` operations: object metadata, parts, versions, temporary data, abandoned data cleanup, and raw files are stored by `xlStorage`. No protocol response state is persisted.

Dependencies/integration: integrates with MinIO router setup, `grid.Manager`, internode auth/JWT, global active credentials, endpoint pools, `xlStorage`, disk ID checks, logger/config fatal paths, msgp storage payloads, bitrot verifiers, and HTTP tracing/stat collection. It is the server counterpart to `storage-rest-client.go` and is registered from `routers.go`.

Risks/test signals: auth, clock skew, and disk ID checks are critical for preventing stale or cross-drive writes. Error framing intentionally loses concrete Go error types across HTTP and relies on client-side `toStorageErr` string mapping. Keepalive goroutines must be completed by calling the returned done function to avoid leaks. Multipart/delete-version handlers currently create empty `DeleteOptions` server-side for some paths, so option propagation must be watched. `storage-rest_test.go` verifies representative client/server calls through a test grid; higher-level erasure and multipart tests exercise additional handlers indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest-server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest_test.go -->
## sources/object-store/minio/cmd/storage-rest_test.go

Purpose: integration-style tests for the storage REST client/server pair using a two-host in-process `grid` setup and real temporary `xlStorage`.

Important APIs/types/functions: helper tests cover `DiskInfo`, `StatInfoFile`, `ListDir`, `ReadAll`, `ReadFile`, `AppendFile`, `Delete`, and `RenameFile`. `newStorageRESTHTTPServerClient` builds the test grid, endpoint, pool metadata, registers storage REST handlers on both nodes, creates volumes, waits for remote disk info to become reachable, and returns a `storageRESTClient`.

Control flow: each `TestStorageRESTClient*` obtains a fresh remote client and runs a helper against the `StorageAPI` interface. Helpers create files through the remote client, then verify reads, stats, directory listings, deletion idempotence, rename behavior, and error classification for missing files or volumes. Append tests include path names with whitespace/control-like characters and skip those cases on Windows.

State and persistence behavior: tests create real volumes and files in temporary directories behind `xlStorage`. Global MinIO host/port and node auth token are adjusted during client creation; cleanup hooks tear down the grid and temp roots.

Dependencies/integration: depends on `grid.SetupTestGrid`, endpoint parsing/locality update, `registerStorageRESTHandlers`, `newStorageRESTClient`, `globalLocalSetDrives`, and low-level storage APIs. This file validates the protocol boundary between `storage-rest-client.go`, `storage-rest-server.go`, and `xlStorage`.

Risks/test signals: good signal for representative REST/grid connectivity and path encoding, but it does not cover every `StorageAPI` method in the remote client. Disk info expectation is tied to an unformatted disk state, and global host/port mutation requires careful cleanup to avoid order sensitivity.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-rest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storagemetric_string.go -->
## sources/object-store/minio/cmd/storagemetric_string.go

Purpose: generated `String()` implementation for the `storageMetric` enum used by storage disk metrics and tracing.

Important APIs/types/functions: the compile-time `_()` function indexes every expected enum value from `storageMetricMakeVolBulk` through `storageMetricLast` to force regeneration when constants shift. `_storageMetric_name` and `_storageMetric_index` encode all names compactly. `(storageMetric).String()` returns the corresponding metric name or `storageMetric(<n>)` for out-of-range values.

Control flow: valid enum values slice into the compact name table using the index array; invalid values are formatted with `strconv.FormatInt`.

State and persistence behavior: no mutable or persistent state. The generated name table affects metric labels and logs, which are externally visible observability contracts.

Dependencies/integration: generated by `stringer` from `xl-storage-disk-id-check.go` and used wherever storage metrics are labeled. It must match the enum order in the source constants.

Risks/test signals: stale generated output can silently mislabel metrics unless the compile-time index checks fail. There is no direct test in this subset; correctness is guarded primarily by compilation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storagemetric_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/streaming-signature-v4.go -->
## sources/object-store/minio/cmd/streaming-signature-v4.go

Purpose: validates and decodes AWS S3 Signature V4 streaming chunked uploads, including signed trailers, into a normal payload reader for object and multipart PUT paths.

Important APIs/types/functions: constants define streaming payload markers, chunk-signing algorithms, `aws-chunked` encoding, trailer header names, and parser limits. `calculateSeedSignature` verifies the request authorization header and seed signature. `newSignV4ChunkedReader` constructs an `s3ChunkedReader`. `s3ChunkedReader.Read` parses chunk sizes and `chunk-signature` extensions, enforces `maxChunkSize`, reads payload bytes, computes SHA-256, validates chained HMAC signatures, handles the final zero-size chunk, and optionally reads trailers. Helpers include `getChunkSignature`, `getTrailerChunkSignature`, `readTrailers`, `readCRLF`, `readChunkLine`, `parseS3ChunkExtension`, `parseChunkSignature`, and `parseHexUint`.

Control flow: the seed signature is checked first using canonical SigV4 request construction and the expected streaming payload hash. Each read drains any buffered chunk data before parsing a new chunk. Chunk signatures chain by replacing `seedSignature` with the previously verified signature, so any tampered chunk breaks all subsequent verification. Trailer mode pre-populates `req.Trailer` only with names declared in `X-Amz-Trailer`, then `readTrailers` verifies the trailer-signature chunk and rejects undeclared or missing trailers.

State and persistence behavior: all state is per-reader: credentials, seed date/region/signature, requested trailers, a reusable chunk buffer, hash writer, offset, and sticky error. No data is persisted; decoded bytes flow into object-layer write paths.

Dependencies/integration: used by object and multipart handlers for `authTypeStreamingSigned` and `authTypeStreamingSignedTrailer`. It integrates with SigV4 parsing/auth helpers, MinIO credentials, `globalSite.Region`, S3 service signing keys, SHA-256, HTTP request trailers, and API error codes.

Risks/test signals: this is security-sensitive parsing. Boundary risks include accepting malformed chunk framing, allowing chunks above 16 MiB, trailer canonicalization mismatches, case handling for declared trailer names, and sticky error behavior after partial reads. Unit tests cover helper parsing (`readChunkLine`, extension parsing, CRLF, and hex parsing), while full signed streaming behavior is exercised indirectly through S3 handler tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/streaming-signature-v4.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/streaming-signature-v4_test.go -->
## sources/object-store/minio/cmd/streaming-signature-v4_test.go

Purpose: unit tests for low-level helpers used by the signed SigV4 streaming reader.

Important APIs/types/functions under test: `readChunkLine`, `parseS3ChunkExtension`, `readCRLF`, and `parseHexUint`.

Control flow: table-driven tests validate small-buffer and overlong-line errors, unexpected EOF handling, extraction of chunk size/signature values, trimming of trailing whitespace, strict CRLF matching, invalid hex byte errors, 16-hex-digit limits, and a sweep of small integer hex encodings.

State and persistence behavior: all tests use in-memory byte readers and buffers. No HTTP request signing or object write state is created.

Dependencies/integration: protects parser helpers consumed by `s3ChunkedReader.Read` and related chunk framing logic.

Risks/test signals: the tests are precise for helper boundaries but do not construct complete signed chunk streams, verify HMAC chains, exercise signed trailers, or test the unsigned streaming reader. Regression coverage for full upload behavior relies on higher-level handler tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/streaming-signature-v4_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/streaming-v4-unsigned.go -->
## sources/object-store/minio/cmd/streaming-v4-unsigned.go

Purpose: decodes AWS SigV4-compatible unsigned chunked uploads, optionally with signed request authentication and declared trailers, for object and multipart handlers that accept unsigned streaming payloads.

Important APIs/types/functions: `newUnsignedV4ChunkedReader` optionally validates the request signature with `doesSignatureMatch(unsignedPayloadTrailer, ...)`, initializes declared trailers from `X-Amz-Trailer`, and returns an `s3UnsignedChunkedReader`. `s3UnsignedChunkedReader.Read` parses hex chunk sizes, enforces `maxChunkSize`, reads payloads, validates CRLF separators, and returns decoded bytes. `readTrailers` reads the terminal trailer block and only accepts keys declared in the request trailer header.

Control flow: reads first drain buffered chunk bytes, then parse a size line ending in CRLF, read exactly that many bytes, and consume the following CRLF. A zero-size chunk ends the stream and, if trailer mode is active, reads a final trailer block ending in CRLFCRLF. Trailer keys are normalized to lowercase for comparison with declared keys.

State and persistence behavior: per-reader state consists of a buffered source, optional trailer map, chunk buffer, offset, sticky error, and debug flag. No payload data is persisted here.

Dependencies/integration: shares constants and errors with `streaming-signature-v4.go`, is called from object and multipart handlers for unsigned trailer/chunked auth types, and integrates with SigV4 request authentication only when an Authorization header is present.

Risks/test signals: because payload chunks are unsigned, integrity depends on the surrounding request mode, checksums, TLS, or object-layer validation. Parser risks mirror the signed reader: chunk-size bounds, strict malformed encoding handling, and trailer allow-list enforcement. There are no dedicated tests for this file in the subset; coverage is indirect through upload handlers.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/streaming-v4-unsigned.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/sts-datatypes.go -->
## sources/object-store/minio/cmd/sts-datatypes.go

Purpose: defines XML response models for MinIO's AWS STS-compatible APIs.

Important APIs/types/functions: `AssumedRoleUser`, `AssumeRoleResponse`/`AssumeRoleResult`, `AssumeRoleWithWebIdentityResponse`/`WebIdentityResult`, `AssumeRoleWithClientGrantsResponse`/`ClientGrantsResult`, `AssumeRoleWithLDAPResponse`/`LDAPIdentityResult`, `AssumeRoleWithCertificateResponse`, and `AssumeRoleWithCustomTokenResponse`. Result structs carry temporary `auth.Credentials`, optional assumed-user identity, packed-policy size, provider/audience/subject fields, and request metadata.

Control flow: this file has no executable behavior. Handlers instantiate these structs, set credentials and request IDs, then serialize them through `encodeResponse` and `writeSuccessResponseXML`.

State and persistence behavior: no state is persisted here. The structs define externally visible XML wire contracts for clients and SDKs consuming STS responses.

Dependencies/integration: depends on `encoding/xml` and MinIO `auth.Credentials`. Used exclusively by `sts-handlers.go` success paths.

Risks/test signals: XML names and element names must remain AWS-compatible or clients may fail to parse credentials. Several fields are currently omitted in handler responses despite being modeled. STS integration tests in `sts-handlers_test.go` cover successful credential acquisition and use across LDAP/OpenID flows, but this file has no direct unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/sts-datatypes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/sts-errors.go -->
## sources/object-store/minio/cmd/sts-errors.go

Purpose: maps internal STS error codes to AWS-style XML error responses and HTTP status codes.

Important APIs/types/functions: `writeSTSErrorResponse` builds and writes an `STSErrorResponse`. `STSError` describes code, description, and HTTP status. `STSErrorCode` enumerates access denied, missing/invalid parameters, expired tokens, malformed policies, TLS certificate errors, STS/IAM initialization errors, upstream failures, and internal errors. `stsErrorCodeMap.ToSTSErr` provides fallback to internal error. `stsErrCodes` contains the concrete AWS-style code strings and statuses.

Control flow: handlers pass an `STSErrorCode` plus optional concrete error. `writeSTSErrorResponse` uses the mapped description unless a concrete error is supplied, attaches the current request ID, logs internal/upstream failures, XML-encodes the response, and writes it with the mapped status.

State and persistence behavior: no persistent state. Error mappings are part of the public STS API behavior and audit/debug surface.

Dependencies/integration: integrates with MinIO HTTP response helpers, request ID headers, XML encoding, and STS handler branches. `apiToSTSError` in `sts-handlers.go` maps S3 auth errors into these codes.

Risks/test signals: returning raw `err.Error()` improves diagnostics but can expose upstream messages, especially for identity providers. Missing map entries default to internal error. There are broad STS integration tests elsewhere, but no focused table test here for every mapping/status.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/sts-errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/sts-handlers.go -->
## sources/object-store/minio/cmd/sts-handlers.go

Purpose: implements MinIO's STS API surface for generating temporary credentials from SigV4-authenticated users, OpenID/web identity tokens, OAuth client grants, LDAP credentials, TLS client certificates, and custom external authentication plugins.

Important APIs/types/functions: constants define STS form/query names, supported actions, request body limit, JWT/LDAP/role claims, and the 2048-byte session policy cap. `stsClaims.populateSessionPolicy` parses and base64-encodes inline session policies. `registerSTSRouter` attaches route matchers for `AssumeRole`, SSO/JWT, LDAP, certificate, and custom-token actions. Auth helpers include `apiToSTSError`, `checkAssumeRoleAuth`, `parseForm`, and `getTokenSigningKey`. Handler methods are `AssumeRole`, `AssumeRoleWithSSO`, wrappers for web identity/client grants, `AssumeRoleWithLDAPIdentity`, `AssumeRoleWithCertificate`, and `AssumeRoleWithCustomToken`.

Control flow: `AssumeRole` verifies SigV4 STS auth, rejects temporary/service-account/session-token callers, validates form/action/version, optional session policy, duration, and parent-user policy lookup, then creates and persists temp credentials. `AssumeRoleWithSSO` validates OpenID/client-grants tokens against role policy or claim-based policy configuration, derives stable parent user from `sub` and `iss`, enforces duration-policy deny conditions, persists credentials, and returns the action-specific XML response. LDAP flow binds username/password, checks user/group policy mapping, copies LDAP DNs/groups/attributes into claims, and persists credentials. Certificate flow requires TLS, one non-CA client certificate, optional CA verification plus client-auth key usage, maps certificate CN to a policy and parent user, and caps credential lifetime by certificate expiration. Custom-token flow delegates opaque token validation to the authn plugin, validates role policy, merges plugin claims without overriding reserved claims, and persists credentials.

State and persistence behavior: all successful flows call `auth.GetNewCredentialsWithMetadata`, set `ParentUser`/groups/policy mapping as appropriate, and persist temporary users through `globalIAMSys.SetTempUser`. Site replication hooks publish STS credential changes via `globalSiteReplicationSys.IAMChangeHook`. Claims encode expiration, parent identity, role ARN, LDAP attributes, optional session policy, and optional token revoke type into the session token.

Dependencies/integration: integrates with MinIO IAM, OpenID config, LDAP config, TLS STS config, global authn/authz plugins, policy parsing/evaluation, site replication credentials, audit logging, request tracing, XML STS datatypes, and STS error response mapping. Generated credentials are later consumed by normal S3 auth and policy evaluation paths.

Risks/test signals: this is security-critical. Risks include policy-claim confusion when dummy RoleARN fallback is allowed, leaking sensitive provider errors, accepting malformed session policies, parent-user stability changes, certificate CN-to-policy ambiguity, clock/duration condition mismatches, and correct redaction of LDAP passwords/custom tokens in audit logs. `sts-handlers_test.go`, LDAP/OpenID integration suites, `http-tracer_test.go`, and IAM object-store tests provide broad external signals for LDAP, OpenID duration conditions, role policies, service accounts, special DN filenames, and redaction, but there is limited local unit coverage for individual branches in this file.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/sts-handlers.go -->
