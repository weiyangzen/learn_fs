# subset-b-008195 grouped research

This grouped report covers MinIO server command-layer files for KMS HTTP APIs, KMS routing, recent latency histograms, lifecycle event string generation, goroutine leak-test helpers, notification streaming, local and grid-backed distributed locks, logging category wrappers, CLI startup, and metacache listing state. Each source file section is bounded by reconciliation markers for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/kms-handlers.go -->
# sources/object-store/minio/cmd/kms-handlers.go

## Purpose

`kms-handlers.go` implements MinIO's `/minio/kms/v1` admin-style HTTP handlers for status, metrics, API discovery, version, key creation, key listing, and key health checks. These handlers bridge authenticated admin requests to `GlobalKMS`, converting KMS responses and errors into JSON API responses while auditing every request.

## Important APIs, Control Flow, And State

The handler methods live on `kmsAPIHandlers`. `KMSStatusHandler`, `KMSMetricsHandler`, `KMSAPIsHandler`, and `KMSVersionHandler` validate the request with the corresponding `policy.KMS*Action`, reject uninitialized `GlobalKMS` with `ErrKMSNotConfigured`, call the KMS method, marshal the response, and write JSON. `KMSCreateKeyHandler` additionally extracts `key-id`, revalidates the signature, and calls `checkKMSActionAllowed` against the specific key name before `GlobalKMS.CreateKey`. `KMSListKeysHandler` asks the KMS for the requested pattern and then filters the returned key names in place through resource-specific IAM checks. `KMSKeyStatusHandler` defaults an empty `key-id` to `GlobalKMS.DefaultKey`, authorizes the concrete key, generates a test data key, decrypts it with the same associated data, and constant-time compares plaintexts to populate `madmin.KMSKeyStatus`.

Persistent state is in the external or stub KMS, not in this file. Dependencies include `GlobalKMS`, `validateAdminReq`, `validateAdminSignature`, `globalIAMSys`, MinIO API error helpers, `madmin-go`, internal `kms`, and MinIO policy types. The notable integration detail is the resource overload: `checkKMSActionAllowed` passes the KMS key name as `BucketName` because the shared policy engine builds resources from that field.

## Risks And Test Signals

Risks are subtle authorization regressions: broad admin validation is not enough for key-specific create/list/status, and list filtering must preserve order while removing unauthorized keys. Key status intentionally returns HTTP success with `EncryptionErr` or `DecryptionErr` fields for failed KMS operations after authorization. `kms-handlers_test.go` covers root/user access, resource-matching policies, no-resource legacy behavior, not-configured KMS, invalid credentials, and parity/differences with legacy admin KMS endpoints.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/kms-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/kms-handlers_test.go -->
# sources/object-store/minio/cmd/kms-handlers_test.go

## Purpose

`kms-handlers_test.go` is the behavioral test matrix for the `/minio/kms/v1` router and related admin KMS endpoints. It verifies authentication, IAM policy action matching, KMS key-resource filtering, response bodies, and fallback errors when KMS is absent or credentials are invalid.

## Important Tests And Control Flow

The file defines route constants for KMS and admin KMS paths plus `kmsTestCase`, which carries method, path, query, policy, root/user mode, expected status, expected key names, and response snippets. `TestKMSHandlersCreateKey` checks denied access without policy, allow without resources, allow with matching `arn:minio:kms` resource, and deny on nonmatching resources. `TestKMSHandlersKeyStatus` creates a key as root, checks root success, user denial, legacy no-resource success, matching resource success, and nonmatching resource denial. `TestKMSHandlersAPIs` covers version/apis/metrics/status and confirms their resource field is ignored once the action is allowed. `TestKMSHandlersListKeys` verifies root returns all keys, user policy can filter keys by resource, query `pattern` combines with IAM filtering, empty filtered lists are successful, and a deny statement still blocks the action for backward compatibility. `TestKMSHandlerAdminAPI` documents that old admin KMS actions ignore resources. `TestKMSHandlerNotConfiguredOrInvalidCreds` asserts `501` when `GlobalKMS` is nil and `403` for invalid user credentials once a KMS exists.

The helpers set up an erasure admin testbed, register the KMS router, install `kms.NewStub`, create signed V4 requests, create users, parse inline policy JSON, and attach/detach policies through `globalIAMSys`.

## Risks And Test Signals

The strongest signal is authorization coverage, especially the newer KMS resource semantics. Gaps remain around KMS backend runtime failures, malformed KMS JSON from non-stub providers, pagination/list continuation, concurrent policy mutation, and malformed query values. The tests use the stub backend, so they validate MinIO routing and IAM behavior rather than external KMS interoperability.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/kms-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/kms-router.go -->
# sources/object-store/minio/cmd/kms-router.go

## Purpose

`kms-router.go` registers MinIO's KMS API routes below the reserved `/minio/kms/v1` prefix. It binds HTTP methods and paths to the handlers in `kms-handlers.go`, applies tracing and gzip compression, and installs default not-found/method-not-allowed handlers.

## Important APIs, Control Flow, And State

The constants `kmsPathPrefix`, `kmsAPIVersion`, and `kmsAPIVersionPrefix` define the public route namespace. `kmsAPIHandlers` is an empty receiver type used to group handler methods. `registerKMSRouter` creates a subrouter from the supplied `mux.Router`, initializes a `gzhttp` wrapper with minimum size 1000 and `gzip.BestSpeed`, and fatal-exits on wrapper initialization failure. For each version currently listed, it registers GET routes for `/status`, `/metrics`, `/apis`, `/version`, POST `/key/create` requiring a `key-id` query, GET `/key/list` requiring a `pattern` query, and GET `/key/status`. Each concrete handler is wrapped as `gz(httpTraceAll(...))`.

This file has no persistent state of its own. It integrates with the global HTTP router startup path, `github.com/minio/mux`, `httpTraceAll`, KMS handler methods, and shared error handlers.

## Risks And Test Signals

Route shape is the main risk: `key/create` and `key/list` use `Queries(...)`, so missing query keys may miss the route and fall into default error handling rather than handler-level validation. Compression wrapping changes response behavior for larger JSON bodies and must remain compatible with tracing. `kms-handlers_test.go` registers this router in the testbed and exercises the declared routes, including query-bearing key APIs.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/kms-router.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/last-minute.go -->
# sources/object-store/minio/cmd/last-minute.go

## Purpose

`last-minute.go` implements a compact rolling one-minute latency histogram split by object-size buckets. It is used to accumulate recent operation timing and byte counts and expose them as `madmin.TimedAction`-compatible counters.

## Important APIs, Types, Control Flow, And State

The size bucket constants classify objects into less than 1 KiB, 1 MiB, 10 MiB, 100 MiB, 1 GiB, and greater than 1 GiB. `sizeToTag` maps a byte size to an index; `sizeTagToString` returns stable diagnostic labels. `AccElem` stores accumulated duration in nanoseconds, total bytes, and count. Its `add` clamps negative durations to zero, `merge` combines totals, `avg` returns mean latency, and `asTimedAction` converts to madmin's wire type.

`lastMinuteLatency` stores 60 `AccElem` slots and `LastSec`. `add`, `addAll`, and `getTotal` call `forwardTo` before reading or writing so stale second slots are cleared. `forwardTo` clears the entire ring when the gap is at least 60 seconds, or advances one second at a time clearing overwritten slots. `LastMinuteHistogram` is an array of `lastMinuteLatency` indexed by size bucket; `Merge` aligns and merges two histograms, `Add` records an event, and `GetAvgData` returns the per-bucket one-minute totals.

State is entirely in memory, with generated MessagePack support in `last-minute_gen.go` for transport or persistence by callers. Dependencies are `time` and `madmin-go`.

## Risks And Test Signals

Risks include second-boundary behavior, wall-clock jumps, zero initialization where `LastSec` starts at zero, and callers forgetting to increment `AccElem.Size` before `addAll`/merge paths. The generated tests validate serialization shape, but this file lacks direct unit tests for bucket boundary classification, ring expiry, negative duration clamping, or merge alignment.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/last-minute.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/last-minute_gen.go -->
# sources/object-store/minio/cmd/last-minute_gen.go

## Purpose

`last-minute_gen.go` is `tinylib/msgp` generated serialization code for the latency histogram types in `last-minute.go`. It provides MessagePack encode/decode, marshal/unmarshal, and size-estimation methods for `AccElem`, `LastMinuteHistogram`, and `lastMinuteLatency`.

## Important APIs, Control Flow, And State

For `AccElem`, the generated code serializes a three-field map containing `Total`, `Size`, and `N` as int64 values. For `lastMinuteLatency`, it serializes a two-field map containing `Totals`, a fixed array of 60 `AccElem` maps, and `LastSec`. For `LastMinuteHistogram`, it serializes a fixed array with `sizeLastElemMarker` elements, each in the same `lastMinuteLatency` map shape. Decode and unmarshal paths validate the fixed array lengths and return `msgp.ArrayError` on mismatch. Unknown map fields are skipped, which gives forward compatibility for added fields but not for changed array lengths.

This file has no business logic or persistent state beyond the binary wire representation it defines. It depends only on `github.com/tinylib/msgp/msgp` and the source types.

## Risks And Test Signals

The biggest risk is schema coupling to constants: changing `sizeLastElemMarker` or the 60-second ring shape makes existing serialized data incompatible unless migration is handled elsewhere. Because the file is generated, manual edits would be overwritten and should be avoided. `last-minute_gen_test.go` covers marshal/unmarshal, stream encode/decode, `Skip`, `Msgsize` upper-bound checks, and benchmarks for all three generated types, but it uses zero-value data only.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/last-minute_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/last-minute_gen_test.go -->
# sources/object-store/minio/cmd/last-minute_gen_test.go

## Purpose

`last-minute_gen_test.go` is generated `msgp` test and benchmark coverage for the serialization methods produced in `last-minute_gen.go`. It checks that zero-value latency histogram types can round-trip through both byte-slice and stream APIs and that encoded messages can be skipped.

## Important Tests And Control Flow

For each generated type (`AccElem`, `LastMinuteHistogram`, and `lastMinuteLatency`), the file has a `TestMarshalUnmarshal*` test that marshals a zero value, unmarshals it back into the same value, verifies there are no leftover bytes, and verifies `msgp.Skip` consumes the full message. Each `TestEncodeDecode*` writes the zero value with `msgp.Encode`, checks that the actual buffer length does not exceed `Msgsize`, decodes into a fresh value, and verifies reader-level `Skip`. The benchmark sets measure allocation and throughput for marshal, append-reuse marshal, unmarshal, stream encode, and stream decode.

The tests depend on `bytes`, `testing`, and `tinylib/msgp`. They are mechanical and tightly aligned to generated code.

## Risks And Test Signals

The tests provide a basic generation sanity signal, not semantic histogram coverage. They do not use non-zero totals, sizes, counts, non-zero `LastSec`, boundary array-length failures, unknown fields, or corrupted payloads. If the struct fields change without regenerating, compilation or these tests should fail; if the runtime meaning of the fields changes while the shape stays the same, these tests will not catch it.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/last-minute_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/lceventsrc_string.go -->
# sources/object-store/minio/cmd/lceventsrc_string.go

## Purpose

`lceventsrc_string.go` is generated by `stringer` for the `lcEventSrc` enum defined in lifecycle audit code. It provides stable human-readable names for lifecycle event sources such as scanner, healing, decomposition, S3 operations, and multipart completion.

## Important APIs, Control Flow, And State

The compile-time `_()` function references every expected enum constant with its numeric value. If the enum values drift without regeneration, the generated invalid-index checks fail compilation. `_lcEventSrc_name` concatenates all string names and `_lcEventSrc_index` stores byte offsets. `func (i lcEventSrc) String() string` bounds-checks `i`; valid values slice the concatenated string, while out-of-range values return `lcEventSrc(<number>)` through `strconv.FormatInt`.

The file has no mutable state. It integrates with lifecycle audit/logging paths that need readable event source labels, including list-driven lifecycle expiry paths that use `lcEventSrc_s3ListObjects`.

## Risks And Test Signals

The main risk is stale generated output after enum changes, which is mitigated by the compiler guard. There is no dedicated test file here; coverage is by compilation and by downstream lifecycle/logging tests that compare or display string values. Manual edits should be avoided because `stringer` owns the file.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/lceventsrc_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/leak-detect_test.go -->
# sources/object-store/minio/cmd/leak-detect_test.go

## Purpose

`leak-detect_test.go` provides test-only goroutine leak detection helpers. It snapshots relevant goroutine stacks before a test and compares them after the test, retrying briefly to allow legitimate goroutines to exit.

## Important APIs, Control Flow, And State

`LeakDetect` holds a map of relevant stack dumps. `NewLeakDetect` calls `pickRelevantGoroutines` and stores the initial set. `CompareCurrentSnapshot` returns stacks present now but absent in the initial snapshot. `DetectLeak` exits early if the test already failed, then retries until either no leaked stacks remain or a five-second deadline expires, sleeping 50 ms between checks. On timeout it reports each leaked stack through the `TestErrHandler` interface. `DetectTestLeak` is the public helper intended for `defer DetectTestLeak(t)()`.

`ignoredStackFns` filters known testing/runtime/signal/snapshot stacks. `isIgnoredStackFn` returns true when a stack contains one of the ignored markers. `pickRelevantGoroutines` uses `debug.Stack`, splits goroutine dumps on blank lines, trims the stack body, skips testing runners and ignored functions, sorts the remaining stacks, and returns them.

State is only the in-memory snapshot. Dependencies are `runtime/debug`, `sort`, `strings`, and `time`.

## Risks And Test Signals

Risks are false positives from long-lived background goroutines, false negatives from overly broad ignored substrings, and reliance on textual stack formatting. The helper itself has no direct tests in this file. Its value is visible in tests that opt into `DetectTestLeak`; this file should be treated as test infrastructure rather than production behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/leak-detect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/listen-notification-handlers.go -->
# sources/object-store/minio/cmd/listen-notification-handlers.go

## Purpose

`listen-notification-handlers.go` implements the S3-compatible event stream endpoint for listening to local and peer object notifications. It authenticates listen requests, validates filters, subscribes to local events, fans in peer events, and streams JSON event records with optional keepalive behavior.

## Important APIs, Control Flow, And State

`ListenNotificationHandler` builds a request context and audit log, verifies the object layer exists, extracts the optional bucket from mux vars, and chooses `policy.ListenNotificationAction` for cluster-wide listening or `policy.ListenBucketNotificationAction` for a bucket. Query parameters `prefix` and `suffix` are validated with `event.ValidateFilterRuleValue`; multiple values produce S3 filter errors. Event names are parsed into `event.Name` values and merged into a `pubsub.Mask`. When a bucket is specified, `GetBucketInfo` ensures it exists.

The handler creates an event rules map with a UUID target, sets event-stream headers, and creates buffered `mergeCh` and `localCh`. A goroutine encodes local events as `{"Records":[...]}` JSON using a reusable grid byte buffer. `globalHTTPListen.Subscribe` filters by bucket and rules map. Peer REST clients receive `Listen` calls with the same query values and feed `mergeCh`. The response loop writes peer/local JSON bytes, flushes when the queue drains, emits empty JSON records on explicit `ping=<seconds>`, or emits a deprecated space keepalive every 500 ms when `ping` is absent.

State is streaming and subscription state tied to request cancellation. Dependencies include MinIO event, grid buffer pool, peer REST clients, pubsub, HTTP flush helpers, mux vars, and policy checks.

## Risks And Test Signals

Risks include slow clients consuming buffer memory, goroutine lifetime if context cancellation is missed, byte-buffer ownership between JSON encoding and write paths, peer fan-in partial failure handling, and deprecated keepalive compatibility. No direct test in this subset covers the handler; likely coverage is integration-level notification tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/listen-notification-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/local-locker.go -->
# sources/object-store/minio/cmd/local-locker.go

## Purpose

`local-locker.go` implements the local node side of MinIO's distributed lock interface (`dsync.NetLocker`). It maintains in-memory read/write locks for object resources, tracks lock UIDs for refresh and force-unlock, rejects overload, and expires stale locks.

## Important APIs, Types, Control Flow, And State

`lockRequesterInfo` records resource name, writer/read mode, UID, timestamps, source, group flag, owner, quorum, and an internal resource index. `localLocker` protects `lockMap` (`resource -> []lockRequesterInfo`) and `lockUID` (`UID+index -> resource`) with a mutex and tracks waiters, read/write stats, cleanup time, and overload count with atomics. `Lock` rejects too many resources, overload, canceled contexts, and any already-locked resource; otherwise it writes one lock entry per resource and one UID index per resource. `RLock` only accepts one resource and appends a reader if no writer exists. `Unlock` and `RUnlock` enforce write/read mode expectations and call `removeEntry`, which removes an entry only when UID and optional owner match.

`ForceUnlock` removes all locks for supplied resources when no UID is provided, or walks UID indexes to remove every resource held by a UID. `Refresh` updates `TimeLastRefresh` across all resources for a UID. `expireOldLocks` removes entries whose refresh timestamp exceeds the interval, updates read/write counters, and stores `lastCleanup`. `DupLockMap` returns a shallow copy for diagnostics; `IsOnline` and `IsLocal` report local availability.

All state is process-local memory. Persistence and cross-node behavior come from the surrounding grid/dsync layer, not this file.

## Risks And Test Signals

Risks include lockUID/lockMap divergence, duplicate read locks with the same UID, fairness/starvation under high contention, overloaded wait rejection causing retry storms, group-lock partial cleanup, and expiration under clock jumps. `local-locker_test.go` stresses large read/write sets, unlock/force-unlock cleanup, stale expiration, and UID accounting, including heavy cases skipped in short mode.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/local-locker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/local-locker_gen.go -->
# sources/object-store/minio/cmd/local-locker_gen.go

## Purpose

`local-locker_gen.go` is `tinylib/msgp` generated serialization code for lock diagnostics/state types: `localLockMap`, `lockRequesterInfo`, and `lockStats`. It supports efficient MessagePack encoding for lock inspection and grid/admin transport paths that need these structures.

## Important APIs, Control Flow, And State

`localLockMap` is encoded as a map from resource string to an array of `lockRequesterInfo`. Decode/unmarshal initialize or clear the destination map before filling it. `lockRequesterInfo` encodes nine exported fields: `Name`, `Writer`, `UID`, `Timestamp`, `TimeLastRefresh`, `Source`, `Group`, `Owner`, and `Quorum`; the internal `idx` is excluded by its `msg:"-"` tag. `lockStats` encodes `Total`, `Writes`, `Reads`, `LockQueue`, `LocksAbandoned`, and nullable `LastCleanup` as MessagePack time. All generated decoders skip unknown fields, and all methods wrap errors with field path context.

The generated methods define a binary schema but do not maintain lock state themselves. Dependencies are `time` and `github.com/tinylib/msgp/msgp`.

## Risks And Test Signals

Because `idx` is not serialized, decoded `lockRequesterInfo` is suitable for reporting but not for reconstructing a fully functional `localLocker` UID index without additional rebuild logic. Map iteration means serialized `localLockMap` order is nondeterministic. `local-locker_gen_test.go` validates zero-value round trips and benchmarks generated methods; it does not test populated lock maps, nullable/non-null `LastCleanup`, or unknown-field compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/local-locker_gen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/local-locker_gen_test.go -->
# sources/object-store/minio/cmd/local-locker_gen_test.go

## Purpose

`local-locker_gen_test.go` is generated test and benchmark coverage for the MessagePack methods in `local-locker_gen.go`. It verifies that the generated code compiles, round-trips zero values, skips encoded messages, and provides benchmark baselines.

## Important Tests And Control Flow

For `localLockMap`, `lockRequesterInfo`, and `lockStats`, each `TestMarshalUnmarshal*` marshals a zero value, unmarshals it, checks no trailing bytes remain, and checks `msgp.Skip` consumes the message. Each `TestEncodeDecode*` stream-encodes to a `bytes.Buffer`, checks the `Msgsize` upper bound, decodes into a fresh value, and verifies reader `Skip`. Benchmarks cover marshaling to a new slice, appending into a reused slice, unmarshalling, stream encoding, and stream decoding.

The file depends on `bytes`, `testing`, and `tinylib/msgp`. It does not interact with real locks or grid transport.

## Risks And Test Signals

This is a generated sanity suite, not behavioral lock coverage. It does not exercise non-empty maps, multiple resources, read/write flags, owner matching, timestamp values, nullable versus non-null `LastCleanup`, or nondeterministic map ordering. Regeneration drift should be caught by compilation and these basic tests, while lock semantics are covered separately in `local-locker_test.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/local-locker_gen_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/local-locker_test.go -->
# sources/object-store/minio/cmd/local-locker_test.go

## Purpose

`local-locker_test.go` validates the in-memory lock manager's expiration, read/write unlock, UID indexing, and force-unlock behavior under many locks and readers. It is the main safety net for `local-locker.go`.

## Important Tests And Control Flow

`TestLocalLockerExpire` creates 1000 write locks and 1000 read-locked resources, verifies `lockMap` and `lockUID` counts, runs a non-expiring cleanup, then expires everything with a negative interval and expects both maps empty. `TestLocalLockerUnlock` creates 1000 group write locks over five resources each plus read locks with two different UIDs, then releases one read UID, the second read UID, and all write locks while checking both map sizes after each phase. `Test_localLocker_expireOldLocksExpire` uses deterministic random data to create up to one million lock resources with varying reader counts, verifies cleanup keeps fresh locks, manually makes roughly half stale, then expires the rest. `Test_localLocker_RUnlock` similarly stresses force-unlocking a random half of read locks and regular `RUnlock` for the remainder.

The tests use `uuid`, deterministic `math/rand`, `hex` resource names, and `testing.Short` skips for the most expensive combinations.

## Risks And Test Signals

The tests strongly signal expected map cardinality and cleanup performance. They do not directly cover overload rejection, context cancellation while waiting, owner mismatch denial beyond the helper-level behavior, write/read conflict interleavings under concurrent goroutines, or refresh extending lock life. Still, the large deterministic cases are useful for catching UID-index leaks and slice-removal mistakes.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/local-locker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-client.go -->
# sources/object-store/minio/cmd/lock-rest-client.go

## Purpose

`lock-rest-client.go` implements the remote `dsync.NetLocker` client over MinIO's grid RPC layer. It forwards distributed lock operations to a remote lock server and translates `dsync.LockResp` codes into boolean success and Go errors.

## Important APIs, Control Flow, And State

`lockRESTClient` holds a `*grid.Connection`. `IsOnline` reports whether the connection state is `grid.StateConnected`; `IsLocal` is false; `String` returns the remote address; `Close` is a no-op. The shared `call` method invokes a typed `grid.SingleHandler[*dsync.LockArgs,*dsync.LockResp]`, returns `ok` when the response code is `dsync.RespOK`, maps `RespLockConflict`, `RespLockNotFound`, and `RespOK` to no error, maps `RespLockNotInitialized` to `errLockNotInitialized`, and maps other response errors to `errors.New(r.Err)`.

`RLock`, `Lock`, `RUnlock`, `Refresh`, `Unlock`, and `ForceUnlock` are thin wrappers selecting the corresponding global handler. `newLockAPI` returns `globalLockServer` for local endpoints and a new REST client for remote endpoints. `newlockRESTClient` obtains the grid connection from `globalLockGrid` using `Endpoint.GridHost()`.

State is the connection object; lock persistence is on the remote local locker. Dependencies are `internal/dsync`, `internal/grid`, endpoint metadata, and global lock-grid initialization.

## Risks And Test Signals

Risks include stale connection state, response-code compatibility between client and server, and treating lock conflict/not-found as non-error while relying on the boolean. `lock-rest-client_test.go` covers an offline endpoint and verifies all basic lock calls fail with connection errors. It does not cover a successful connected server or every response-code mapping.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-client_test.go -->
# sources/object-store/minio/cmd/lock-rest-client_test.go

## Purpose

`lock-rest-client_test.go` verifies that a remote lock client created for an unreachable endpoint reports offline state and surfaces errors for lock operations. It is a negative-path test for `lock-rest-client.go`.

## Important Test Flow

`TestLockRESTlient` creates one remote endpoint at `localhost:9876` and one local endpoint at `localhost:9012`, marks the second as local, and initializes the global lock grid with both. It constructs a `newlockRESTClient` for the unreachable remote endpoint, expects `IsOnline` to be false, and then attempts `RLock`, `Lock`, `RUnlock`, and `Unlock` with empty `dsync.LockArgs`, expecting each call to return an error.

The test depends on endpoint parsing, `initGlobalLockGrid`, grid connection state, and `dsync.LockArgs`.

## Risks And Test Signals

The test confirms failure propagation for disconnected clients but has a typo in the function name (`TestLockRESTlient`). It does not exercise `Refresh`, `ForceUnlock`, local endpoint selection through `newLockAPI`, response-code translation, or a live server. Its main signal is that calls should not silently succeed when the grid connection is unavailable.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-server-common.go -->
# sources/object-store/minio/cmd/lock-rest-server-common.go

## Purpose

`lock-rest-server-common.go` defines the shared sentinel errors used by the grid lock server and client. These errors form the semantic bridge between local locker outcomes and `dsync.LockResp` response codes.

## Important APIs, Control Flow, And State

The file declares `errLockConflict`, `errLockNotInitialized`, and `errLockNotFound` as package-level `errors.New` values. `lock-rest-server.go` maps them to `dsync.RespLockConflict`, `dsync.RespLockNotInitialized`, and `dsync.RespLockNotFound`; `lock-rest-client.go` maps `RespLockNotInitialized` back to `errLockNotInitialized` and treats conflict/not-found as false replies without Go errors.

There is no mutable state or persistence. The dependency is only the standard `errors` package.

## Risks And Test Signals

Because server response mapping relies on direct error identity in a switch, wrapping these sentinel errors before `makeResp` would break classification. The common test file exercises lower-level lock entry removal, not the sentinel values directly. Response-code behavior is indirectly covered by lock client/server tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-server-common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-server-common_test.go -->
# sources/object-store/minio/cmd/lock-rest-server-common_test.go

## Purpose

`lock-rest-server-common_test.go` provides test setup for a lock server and validates `localLocker.removeEntry`, the helper used by unlock and force-unlock paths. Despite the filename, the concrete assertion is about local lock entry deletion semantics.

## Important Tests And Control Flow

`createLockTestServer` prepares a filesystem-backed test object layer, initializes config, constructs a `lockRESTServer` with a `localLocker` containing a mutex and `lockMap`, authenticates node credentials, and returns the temp path, locker, and token. `TestLockRpcServerRemoveEntry` inserts two write-lock requester entries under `"name"`, verifies an unknown UID does not remove anything, removes the first UID and checks the remaining slice contains the second entry, then removes the second UID and expects the lock map entry to be nil.

Dependencies include `prepareFS`, `newTestConfig`, `globalActiveCred`, `authenticateNode`, `reflect.DeepEqual`, and `dsync.LockArgs`.

## Risks And Test Signals

The test confirms UID/owner matching and slice update behavior in `removeEntry`, but its hand-built locker omits `lockUID`, so it does not validate UID-index cleanup. It also does not exercise grid handlers, response-code mapping, token use, or concurrent access. Its setup helper can support broader server tests if expanded.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-server-common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-server.go -->
# sources/object-store/minio/cmd/lock-rest-server.go

## Purpose

`lock-rest-server.go` exposes the local lock manager over MinIO's grid RPC system. It registers typed lock handlers, translates local locker results into `dsync.LockResp` codes, and starts background maintenance for distributed erasure deployments.

## Important APIs, Control Flow, And State

`lockRESTServer` wraps a `*localLocker`. Handler methods are thin adapters: `RefreshHandler` uses `dsync.DefaultTimeouts.RefreshCall` and returns not-found when refresh fails without error; `LockHandler` and `RLockHandler` use acquire timeouts and translate false success to `errLockConflict`; `UnlockHandler`, `RUnlockHandler`, and `ForceUnlockHandler` call the local locker with background context and ignore boolean replies when errors communicate failure. Global handlers (`lockRPCForceUnlock`, `lockRPCRefresh`, `lockRPCLock`, `lockRPCUnlock`, `lockRPCRLock`, `lockRPCRUnlock`) are created with `newLockHandler`.

`registerLockRESTHandlers` creates a new local locker, registers each handler with the grid manager using `logger.FatalIf`, stores it in `globalLockServer`, and launches `lockMaintenance(GlobalContext)`. `makeResp` maps nil and sentinel errors to `dsync.LockResp` codes and arbitrary errors to `RespErr` with a string. `lockMaintenance` only runs for distributed erasure, ticking once per minute and expiring locks older than `lockValidityDuration`.

State is the process-local `globalLockServer` and its in-memory lock maps. Integration points are grid manager registration, dsync timeout constants, and local locker expiration.

## Risks And Test Signals

Risks include response-code drift with clients, identity-based sentinel matching, background maintenance not running outside distributed erasure, and using background contexts for unlock paths. Tests in this subset cover local removal and offline clients, but not live grid handler round-trips or maintenance ticks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/lock-rest-server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/logging.go -->
# sources/object-store/minio/cmd/logging.go

## Purpose

`logging.go` centralizes category-specific logging wrappers for MinIO subsystems. It gives call sites short, named helpers that route errors and events to `internal/logger` with stable subsystem tags.

## Important APIs, Control Flow, And State

Most functions are one-line wrappers around `logger.LogIf`, `logger.LogOnceIf`, `logger.LogAlwaysIf`, `logger.LogOnceConsoleIf`, or `logger.Event`. Categories include proxy, replication, IAM, rebalance, admin, authN, authZ, peers, internal/bug, healing, batch, bootstrap, DNS, transition, config, scanner, ILM, encryption, storage, decommission, etcd, metrics, S3, SFTP, shutdown, STS, tier, and KMS. `iamLogIf`, `peersLogIf`, `peersLogAlwaysIf`, and `peersLogOnceIf` suppress `grid.ErrDisconnected` to avoid noisy logs during expected peer disconnects. `KMSLogger` implements a small logger interface with `LogOnceIf` and `LogIf` methods for the KMS module.

The file has no persistent state. It depends on `context`, `errors`, `internal/grid`, and `internal/logger`.

## Risks And Test Signals

The value is consistency, but risks include category typos becoming observability contract changes, unexpected suppression of `grid.ErrDisconnected`, and wrapper proliferation hiding severity choices. There are no direct tests in this subset. Coverage is indirect through subsystem tests and runtime logging behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/logging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/main.go -->
# sources/object-store/minio/cmd/main.go

## Purpose

`main.go` builds and runs the MinIO CLI application. It defines global flags, help/version output, command registration, typo suggestions for unknown commands, startup banners, and the debug no-exit mode used for diagnostics.

## Important APIs, Control Flow, And State

`GlobalFlags` declares hidden legacy config/compat flags and visible certs-dir, quiet, anonymous, json, plus hidden no-compat. `minioHelpTemplate` customizes CLI help. `newApp` registers build-enabled commands (`serverCmd` and `fmtGenCmd`) into both a slice and trie, configures help/version behavior, metadata, flags, commands, and a `CommandNotFound` handler. Unknown command suggestions combine trie prefix matches with Damerau-Levenshtein distance less than 2 and then exit.

`startupBanner` writes copyright, license, release tag, Go version, OS, and architecture, updating `CopyrightYear` to the current year. `versionBanner` returns an `io.Reader` with version, commit ID, runtime, license, and copyright. `printMinIOVersion` copies that reader to the CLI writer. `debugNoExit` is controlled by `_MINIO_DEBUG_NO_EXIT`; when enabled, `Main` overrides `logger.ExitFunc`, recovers panics to stdout with stack, then blocks forever. Otherwise `Main` derives the app name from `args[0]`, runs the CLI app, and exits with status 1 on errors.

State is global CLI/logger configuration and environment-driven debug mode. Dependencies include `minio/cli`, console/color helpers, env, trie, words, runtime/debug, and command globals.

## Risks And Test Signals

Risks include `args[0]` assumptions, unknown-command suggestion ordering, hidden flag compatibility, global mutation in debug mode, and immediate process exits complicating tests. No direct tests in this subset cover `newApp` or `Main`; behavior is generally exercised by CLI integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-bucket.go -->
# sources/object-store/minio/cmd/metacache-bucket.go

## Purpose

`metacache-bucket.go` manages all metacache listings for a single bucket. It creates, indexes, updates, cleans, clones, and deletes cache descriptors, and coordinates deletion of on-disk cache data under `.minio.sys`.

## Important APIs, Control Flow, And State

`bucketMetacache` stores the bucket name, `caches` by cache ID, `cachesRoot` by listing root, a mutex, and an `updated` flag. `newBucketMetacache` optionally deletes existing bucket cache data through an object layer implementing `deleteAllStorager`, then initializes maps. `findCache` validates bucket identity, returns an existing cache while updating `lastHandout`, returns a non-created `scanStateNone` cache when `Create` is false, or creates a new metacache from `listPathOptions`, indexes it by ID and root, and marks the bucket updated.

`cleanup` works on a cloned cache map, removing entries that are not worth keeping, have mismatched ID/bucket, or exceed `metacacheMaxEntries` with old `lastHandout` times beyond client wait. `updateCacheEntry` merges a metacache update into an existing entry. `cloneCaches` shallow-copies both indexes. `deleteAll` deletes all on-disk cache data and resets maps. `deleteCache` removes one cache from both indexes under lock, then calls `metacache.delete` outside the lock.

State is in memory plus persisted metacache objects deleted through the object layer. Dependencies include object-layer lookup, logger/console debug, map copy, sorting, and metacache lifecycle methods defined elsewhere.

## Risks And Test Signals

Risks include stale `cachesRoot` entries, cleanup deleting caches still needed by clients, shallow clone sharing metacache values with embedded mutable fields, object-layer absence, and lock ordering around deletes. `metacache-bucket_test.go` benchmarks `findCache` under many IDs and roots but does not assert cleanup/delete correctness.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-bucket_test.go -->
# sources/object-store/minio/cmd/metacache-bucket_test.go

## Purpose

`metacache-bucket_test.go` contains a benchmark for `bucketMetacache.findCache`. It is performance-oriented coverage for cache creation/indexing under many cache IDs and repeated base paths.

## Important Benchmark Flow

`Benchmark_bucketMetacache_findCache` creates an empty bucket metacache without cleanup, defines 50,000 elements across 100 path names, preloads the cache by calling `findCache` with a fresh UUID, bucket `""`, a rotating `BaseDir`, slash separator, strict disk asking, and `Create: true`. After reporting allocations, the benchmark loop continues creating new metacache entries with rotating base dirs and fresh IDs.

The benchmark depends on `mustGetUUID`, `listPathOptions`, and the path/root derivation inside `newMetacache`.

## Risks And Test Signals

The benchmark signals expected allocation/performance pressure for large cache maps, but it has no assertions. It does not cover cache hits, `Create: false`, cleanup thresholds, root-index correctness, deletion, or concurrent access. Functional behavior for `bucketMetacache` is therefore mostly covered indirectly by listing tests outside this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-entries.go -->
# sources/object-store/minio/cmd/metacache-entries.go

## Purpose

`metacache-entries.go` defines the entry model and algorithms used to sort, filter, merge, resolve, and convert metacache listing results. It is central to turning disk-level metadata streams into S3 object and prefix listings.

## Important APIs, Control Flow, And State

`metaCacheEntry` represents either an object with metadata or a prefix directory without metadata. It can test object/dir forms, prefix membership, directory containment, latest delete markers, all-free versions, and decode metadata into `FileInfo`, `FileInfoVersions`, or cached `xlMetaV2`. `matches` compares two entries with strict or non-strict metadata rules, preferring newer modtimes or richer version sets when mismatched.

`metaCacheEntries` provides sorting, sortedness checks, shallow cloning, first-found scans, names, and quorum-based `resolve`. `resolve` counts directory and object validity, requires dir/object quorum, fast-paths complete agreement, and otherwise merges shallow xl.meta versions with `mergeXLV2Versions`, serializing the result into pooled metadata bytes. `metaCacheEntriesSorted` wraps sorted entries with list ID, reuse/pool ownership, and last skipped entry. It converts entries to object-version listings or object listings while collapsing delimiter prefixes, skipping purge-status versions, and consulting bucket versioning. It can forward/truncate by marker, merge sorted lists, filter prefixes/objects/recursive entries, and release pooled metadata when `reuse` is set.

`mergeEntryChannels` is the streaming fan-in: it merges sorted channels, handles same clean paths, discards pure directory entries when an object of the same path exists, merges versions from duplicate object entries using read quorum, emits strictly increasing names, closes output, and honors context cancellation.

State is mostly in-memory slices and optionally pooled metadata buffers. Dependencies include xl.meta decoding, metadata pools, bucket versioning, lifecycle/listing helpers, path normalization, and console/internal logging.

## Risks And Test Signals

Risks are high: quorum resolution can hide or expose versions, non-strict matching changes availability, metadata buffer reuse can leak or corrupt data if ownership is wrong, delimiter collapsing affects S3 compatibility, and corrupted metadata may be treated as delete/all-free in some paths. `metacache-entries_test.go` covers sorting, forwarding, merge ordering, filters, `isInDir`, and many `resolve` quorum/version/delete-marker cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-entries.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-entries_test.go -->
# sources/object-store/minio/cmd/metacache-entries_test.go

## Purpose

`metacache-entries_test.go` validates core metacache entry algorithms: sortedness, marker forwarding, sorted merge behavior, object/prefix filters, directory containment, and quorum-based metadata resolution. It is the strongest direct test coverage for `metacache-entries.go`.

## Important Tests And Control Flow

The early tests load sample metacache entries and check that `sort` repairs ordering, `forwardTo` positions at exact and prefix-like markers, `merge` preserves duplicate names when metadata differs, and filters produce expected object-only, prefix-only, recursive, root-recursive, custom-separator, and prefix-filtered name lists. `Test_metaCacheEntry_isInDir` table-tests root, direct file, direct directory, and deeper path semantics.

`Test_metaCacheEntries_resolve` constructs multiple `xlMetaV2` inputs with different version IDs, modtimes, signatures, zero version IDs, empty version sets, and delete markers. It serializes them into `metaCacheEntry` values and runs a large table over strict/non-strict modes and different object/directory quorum values. Each case is shuffled repeatedly to ensure deterministic resolution independent of input order. Expected outputs include selected single entries, merged multi-version results, delete-marker handling, and below-quorum failures.

## Risks And Test Signals

The tests provide strong signals for resolution semantics and filter outputs. Gaps include `mergeEntryChannels` concurrency/cancellation, metadata pool reuse, `fileInfos`/`fileInfoVersions` delimiter behavior under versioning config, corrupted xl.meta decode paths, and lifecycle/replication side effects in list filtering.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-entries_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-manager.go -->
# sources/object-store/minio/cmd/metacache-manager.go

## Purpose

`metacache-manager.go` coordinates local bucket metacaches for a peer. It lazily creates per-bucket managers, periodically cleans caches, preserves recently deleted cache entries in a trash map, and exposes update/state-check helpers used by peer listing RPCs.

## Important APIs, Control Flow, And State

`localMetacacheMgr` is the process-local manager with `buckets` and `trash` maps. `metacacheManager` protects those maps with a mutex and starts background maintenance once through `init`. `initManager` waits for the object layer to become available, then ticks once per minute until `GlobalContext` closes. Each tick runs `cleanup` on live bucket caches and deletes trashed metacaches whose `lastUpdate` exceeds `metacacheMaxRunningAge`.

`updateCacheEntry` returns a trashed entry unchanged if the ID is in trash, otherwise delegates to the bucket metacache or returns `errVolumeNotFound`. `getBucket` ensures maintenance is started, returns a cached bucket if present, or creates a new bucket metacache with cleanup enabled and stores it. `deleteBucketCache` removes a bucket from the manager, deletes old cache data immediately, and moves recently updated caches into `trash` as `scanStateError` with `"Bucket deleted"`. `deleteAll` deletes and removes all buckets. `listPathOptions.checkMetacacheState` asks a peer for a listing, treats missing/none as `errFileNotFound`, marks stale running/success states as timeout errors on the peer, and reports cached async errors.

State is in memory plus on-disk cache cleanup via bucket metacache operations.

## Risks And Test Signals

Risks include background goroutine lifetime, lock ordering while bucket cleanup may be expensive, stale trash entries masking new updates by ID, and timeout heuristics marking a slow listing as failed. No direct tests in this subset cover the manager; behavior is exercised through listing and peer metacache paths.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-marker.go -->
# sources/object-store/minio/cmd/metacache-marker.go

## Purpose

`metacache-marker.go` embeds and extracts metacache continuation metadata in S3 listing markers. It lets clients resume cached listings by carrying cache ID, pool, and set information inside an otherwise normal marker string.

## Important APIs, Control Flow, And State

`markerTagVersion` is `"v2"`. `(*listPathOptions).parseMarker` only acts on markers containing `[minio_cache:v2`. It splits the marker at the last `[`, keeps the user-visible marker prefix, then parses comma-separated `key:value` tags from the final bracketed section. `id` restores the cache ID; `return` creates a fresh ID and sets `Create` to true; `p` and `s` parse pool and set indexes. Parse failures for pool/set reset to a fresh ID with `Create` true, forcing a new listing path. Unknown tags are ignored.

`(listPathOptions).encodeMarker` appends either `[minio_cache:v2,return:]` when no ID exists or `[minio_cache:v2,id:<id>,p:<pool>,s:<set>]` when resuming a concrete cache. It logs internally if the ID contains characters that break the simple parser (`[`, `:`, or `,`).

The file has no persistent state; it mutates `listPathOptions` fields and relies on callers in `metacache-server-pool.go`.

## Risks And Test Signals

Risks include ad hoc parsing with `strings.Split(tag, ":")`, collision with object names containing bracketed text, malformed trailing brackets, and marker IDs containing reserved characters. There are no direct tests in this subset, so marker compatibility is mostly protected by listing integration tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-marker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-server-pool.go -->
# sources/object-store/minio/cmd/metacache-server-pool.go

## Purpose

`metacache-server-pool.go` implements erasure-server-pool listing over metacache. It handles old-cache cleanup, list argument normalization, cache lookup/resume/create decisions, multi-set listing fan-in, lifecycle/replication side effects, and async list saving.

## Important APIs, Control Flow, And State

`renameAllBucketMetacache` moves old per-bucket `.metacache` directories under `.minio.sys/tmp` for deletion. `(*erasureServerPools).listPath` validates list args, normalizes markers/prefixes/recursive flags/separators, parses cache markers, derives `BaseDir`, marks reserved/invalid buckets transient, and installs filters. If an ID exists and listing is not transient, it asks the hash-selected peer or local manager for the cache. Existing running/success caches are kept alive and resumed; missing/error caches clear the ID; peer failures fall back to transient listing.

When resuming with an ID, `listPath` either creates and saves a new cache via `listAndSave` or streams metadata parts from the recorded pool/set. On failure it truncates results, may asynchronously mark the remote cache as no longer used, and falls back to raw listing. Raw listing creates channels, runs `listMerged` in a goroutine, applies `gatherResults`, truncates to limit, and emits a new list ID when truncated and non-transient.

`listMerged` starts one `set.listPath` per erasure set, merges sorted streams with `mergeEntryChannels`, handles not-found/all-EOF cases, and returns significant errors. `triggerExpiryAndRepl` evaluates lifecycle expiration for latest and all versions and queues expiry and replication heal work. `listAndSave` chooses a pool/set with space, creates a `metaCacheRPC`, saves the full stream asynchronously while returning the first filtered page, and closes channels carefully when the caller returns.

State spans in-memory list options, peer metacache entries, saved metacache stream objects, and side-effect queues for expiry/replication.

## Risks And Test Signals

Risks include cancellation races among listing/saving/filter goroutines, fallback from cached to transient listing, stale or invalid pool/set markers, disk-full behavior, lifecycle deletes triggered by listing, and channel closure/backpressure. Direct tests are not in this subset; `metacache-entries_test.go` covers lower-level merge/filter/resolve pieces.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/metacache-server-pool.go -->
