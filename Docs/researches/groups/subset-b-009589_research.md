# Research Group subset-b-009589

Grouped source research for the listed gcsfuse storage, utility, workerpool, workload insight, main, and metrics files. Each section is source-tree aligned and intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storage_handle_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storage_handle_test.go

Purpose: Suite-level tests for storage handle construction, bucket handle lookup, HTTP/gRPC client option construction, HNS/zonal/Pirlo bucket routing, billing-project wrapping, auth error propagation, tracing, gRPC metrics, local socket binding, and custom retry selection.

Important APIs/types/functions: `StorageHandleTest`, `fakeStorageControlServer`, `mockStorageLayout`, `controlClientCallOptionsWithRetry`, and tests around `NewStorageHandle`, `BucketHandle`, `createHTTPClientHandle`, `createClientOptionForGRPCClient`, `CreateGRPCControlClient`, `lookupBucketType`, and `controlClientForBucketHandle`.

Control flow: setup creates a fake storage backend and mocked storage control client; individual cases mutate `StorageClientConfig`, construct handles or client options, then assert concrete wrappers and retry call-option choices. gRPC socket-address tests stand up a local control server and verify peer source address. Bucket type tests mock `GetStorageLayout` responses and inspect inferred `gcs.BucketType`.

State and persistence behavior: mostly in-memory tests, but they temporarily mutate environment variables such as `GOOGLE_CLOUD_ENABLE_DIRECT_PATH_XDS` and global OpenTelemetry providers. The suite calls `fakeStorage.ShutDown()` in teardown and uses local listeners that must be stopped to avoid leakage.

Dependencies and integration points: depends on `cfg`, `gcs`, `storageutil`, fake storage helpers, testify suites/mocks, Google Storage Control v2 clients, gRPC, and OpenTelemetry SDKs. It verifies the public behavior of internal storage client wiring rather than only isolated helper functions.

Risks: broad setup means tests can become brittle when generated Google clients change call-option defaults. Auth tests rely on fixture service-account JSON and invalid token/key paths. Environment/provider mutation needs cleanup discipline. The mocked Pirlo layout still has a TODO for native Pirlo storage-layout responses.

Test signals: high-value coverage for auth success/failure, custom endpoints, anonymous access, Google library auth on/off, read-stall retry validation, direct-path env cleanup, billing project wrappers, zonal/non-zonal retry strategy, tracing option count, and local socket binding for both HTTP and gRPC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storage_handle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/auth_client_option.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/auth_client_option.go

Purpose: Builds Google API client auth options and an OAuth2 token source for storage clients, supporting token URL credentials, key-file credentials, ADC, universe-domain discovery, and a quota-project workaround.

Important APIs/types/functions: `GetClientAuthOptionsAndToken(ctx, config)` returns `[]option.ClientOption`, `oauth2.TokenSource`, and error. It uses `auth2.NewTokenSourceFromURL`, `auth2.GetCredentials`, `oauth2adapt.TokenSourceFromTokenProvider`, `cred.UniverseDomain`, `NewRetryConfig`, and `ExecuteWithRetryAtLogLevel`.

Control flow: token URL takes precedence and produces only `option.WithTokenSource`. Otherwise credentials are loaded, converted to token source, and a universe domain is chosen. Standard ADC on commercial GCP bypasses metadata lookup; other cases retry `cred.UniverseDomain` and fall back to `googleapis.com` on failure. Final options include universe domain plus `option.WithAuthCredentials` using a reconstructed credentials object.

State and persistence behavior: reads environment `GOOGLE_CLOUD_UNIVERSE_DOMAIN` and may contact credential providers or metadata services through auth libraries. It logs universe-domain decisions but does not persist state.

Dependencies and integration points: used by HTTP/gRPC storage client creation when Google library auth is enabled. Tightly coupled to `StorageClientConfig`, internal auth package constants, retry helper defaults, and Google API option semantics.

Risks: fallback to default universe domain can mask auth environment problems. Token URL path returns fewer options than key/ADC path. The TODO workaround intentionally drops quota project ID until an upstream auth issue is resolved, so future auth-library upgrades must revisit this file.

Test signals: `auth_client_option_test.go` covers token URL success/error and key-file fallback success/error, including expected client option counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/auth_client_option.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/auth_client_option_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/auth_client_option_test.go

Purpose: Unit tests for `GetClientAuthOptionsAndToken`.

Important APIs/types/functions: tests exercise token URL success via `httptest.Server`, malformed token URL error, key-file fallback using `testdata/key.json`, and invalid key-file failure. They assert token source presence and the number of returned client options.

Control flow: each test builds a minimal `StorageClientConfig`, calls `GetClientAuthOptionsAndToken(context.TODO(), config)`, then checks returned option slice and token source according to the selected branch.

State and persistence behavior: creates an in-process HTTP server for token URL success and reads the test key fixture. No persistent state is written.

Dependencies and integration points: verifies interaction with internal auth URL token source and key-file credential loader, but does not inspect the concrete option values because `option.ClientOption` is opaque.

Risks: success for key-file fallback depends on fixture JSON shape remaining accepted by auth libraries. Option-count assertions are useful but brittle if additional auth options become necessary.

Test signals: validates both primary auth branches and their error propagation, providing a focused guard for storage client auth setup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/auth_client_option_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/client.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/client.go

Purpose: Defines storage client configuration and constructs HTTP clients/token sources for gcsfuse storage backends.

Important APIs/types/functions: `StorageClientConfig` carries protocol, endpoint, auth, retry, HTTP, gRPC, tracing, DNS cache, metrics, GKE, and write settings. `ConfigureDialerWithLocalAddr`, `CreateHttpClient`, `CreateTokenSource`, and `StripScheme` are the main functions.

Control flow: `CreateHttpClient` builds a `net.Dialer`, optionally binds `LocalSocketAddress`, optionally installs a caching DNS resolver, creates HTTP/1 or HTTP/2 transport, then either returns an anonymous timeout-only client or wraps transport with OAuth2, user-agent middleware, and optional OpenTelemetry HTTP tracing.

State and persistence behavior: no persistent state. It may resolve local socket addresses and may use auth/token providers. Client configuration determines connection pooling, keepalive, timeout, and tracing state.

Dependencies and integration points: integrates `cfg.Protocol`, internal auth token source, metrics handle, DNS cache package, oauth2 transport, `userAgentRoundTripper`, and OpenTelemetry HTTP instrumentation. Called by storage handle creation.

Risks: anonymous access path intentionally omits custom transport and user-agent injection, which affects observability and local socket/DNS behavior. HTTP/2 disables keepalives and ignores some HTTP/1 tuning assumptions. `StripScheme` preserves Google internal schemes and only splits the first generic scheme separator.

Test signals: `client_test.go` covers HTTP client creation, token source creation, scheme stripping, tracing span generation, user-agent/auth headers, and socket-address success/failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/client_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/client_test.go

Purpose: Tests storage HTTP client configuration helpers.

Important APIs/types/functions: `clientTest`, `newInMemoryExporter`, and test methods for HTTP/1/HTTP/2 creation, auth-enabled creation, token source creation, `StripScheme`, HTTP tracing, user-agent/auth header propagation, local socket binding, and invalid socket address handling.

Control flow: uses default test config from `test_util.go`, mutates relevant fields, invokes `CreateHttpClient` or `CreateTokenSource`, and validates client timeout, headers, spans, or connection source address through local `httptest` servers.

State and persistence behavior: sets global OpenTelemetry tracer provider for tracing tests with cleanup reset. Reads `testdata/key.json`; local servers are closed per test.

Dependencies and integration points: asserts that `CreateHttpClient` composes oauth2, user-agent middleware, and OpenTelemetry HTTP transport correctly. The socket test checks real `net.Dialer.LocalAddr` behavior.

Risks: tests use real networking on loopback and timing-sensitive span collection; they do not introspect transport internals for HTTP/1 versus HTTP/2 settings.

Test signals: strong guard for external request behavior: user-agent, bearer token, trace spans, scheme preservation, and bind address errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/control_client.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/control_client.go

Purpose: Creates a Google Storage Control gRPC client with optional default GAX retries disabled.

Important APIs/types/functions: `CreateGRPCControlClient(ctx, clientOpts, disableDefaultGaxRetries)` sets `GOOGLE_CLOUD_ENABLE_DIRECT_PATH_XDS`, calls `control.NewStorageControlClient`, optionally replaces `CallOptions` with an empty `StorageControlCallOptions`, then unsets the environment variable.

Control flow: environment is set before client construction and unset after successful setup. On client creation failure it returns wrapped error before reaching the unset call.

State and persistence behavior: mutates process environment. This is transient on success, but the error path can leave direct-path XDS enabled because unset happens after successful client creation.

Dependencies and integration points: used by storage handle creation for raw control clients with and without GAX retries. Depends on Google Storage Control v2 generated client and internal logger fatal behavior for env mutation failures.

Risks: process-wide environment mutation is not concurrency-safe and has an error-path leakage risk. Emptying `CallOptions` changes retry behavior for folder and layout APIs and must match wrapper retry logic.

Test signals: `control_client_test.go` verifies default call options are populated and disabled options are empty when requested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/control_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/control_client_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/control_client_test.go

Purpose: Tests `CreateGRPCControlClient` call-option behavior.

Important APIs/types/functions: `ControlClientTest` creates unauthenticated control clients and asserts `CallOptions` for Create/Get/Delete/Rename folder APIs.

Control flow: one test requests normal GAX retries and expects non-empty call-option slices; another requests disabled defaults and expects empty slices if `CallOptions` is present.

State and persistence behavior: constructing the client mutates the direct-path environment internally; the test does not explicitly check cleanup.

Dependencies and integration points: depends on Google generated control client defaults and `option.WithoutAuthentication`.

Risks: tests may be brittle across Google client library changes to default call options. They do not cover client construction error cleanup.

Test signals: confirms the key behavior used by storage retry wrappers: raw clients can be created with or without generated retry policy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/control_client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/crc32c.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/crc32c.go

Purpose: Provides a helper for computing GCS-compatible CRC32C checksums.

Important APIs/types/functions: package variable `crc32cTable` uses `crc32.Castagnoli`; `CRC32C(contents []byte) *uint32` returns a pointer suitable for `gcs.CreateObjectRequest.CRC32C`.

Control flow: computes checksum over the supplied byte slice and returns the address of a local checksum value, which safely escapes to the heap.

State and persistence behavior: immutable checksum table is initialized once. No persistence or external state.

Dependencies and integration points: used by tests or callers creating object requests with checksum preconditions. Depends only on Go `hash/crc32`.

Risks: caller receives a mutable pointer; no nil/streaming variant exists for large data.

Test signals: no direct test in this subset, but object creation tests elsewhere can validate server-side checksum behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/crc32c.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_empty_objects.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_empty_objects.go

Purpose: Convenience helper to create many empty GCS objects.

Important APIs/types/functions: `CreateEmptyObjects(ctx, bucket, names)` builds a `map[string][]byte` with nil contents for each name and delegates to `CreateObjects`.

Control flow: linear conversion from names slice to map, then parallel creation via `CreateObjects`.

State and persistence behavior: persists objects to the supplied `gcs.Bucket`; duplicate names collapse due to map keys.

Dependencies and integration points: depends on `CreateObjects` and internal `gcs.Bucket`. Useful for tests and fixture setup.

Risks: duplicate input names are silently de-duplicated and creation order is undefined. Errors are only those returned by `CreateObjects`.

Test signals: no direct test in this subset; behavior is simple delegation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_empty_objects.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_object.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_object.go

Purpose: Thin wrapper for creating one object with byte-slice contents.

Important APIs/types/functions: `CreateObject(ctx, bucket, name, contents)` creates `gcs.CreateObjectRequest{Name, Contents: bytes.NewReader(contents)}` and calls `bucket.CreateObject`.

Control flow: no retries or attribute handling; all behavior is delegated to the bucket implementation.

State and persistence behavior: writes one object to the remote or fake bucket.

Dependencies and integration points: used by `CreateObjects` and tests needing direct object setup.

Risks: no checksum, metadata, generation precondition, or content-type support. Callers needing those must use `gcs.CreateObjectRequest` directly.

Test signals: indirectly covered by helpers that create/list/read/delete fake bucket objects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_objects.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_objects.go

Purpose: Parallel helper for creating multiple objects from a name-to-contents map.

Important APIs/types/functions: `CreateObjects(ctx, bucket, input)` uses `errgroup.WithContext`, a buffered channel of records, and a fixed parallelism of 64 workers.

Control flow: all records are enqueued before workers start; each worker drains the channel and calls `CreateObject`. First error cancels the errgroup context and is returned by `group.Wait`.

State and persistence behavior: persists a subset or all requested objects depending on when errors occur. No rollback is attempted.

Dependencies and integration points: depends on `CreateObject`, `gcs.Bucket`, and `golang.org/x/sync/errgroup`; useful for test fixture setup.

Risks: fixed parallelism can be excessive for small inputs or constrained fake services. Map iteration makes creation order nondeterministic. Partial creation on error is possible.

Test signals: no direct local test; correctness depends on bucket fake/integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/create_objects.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/custom_retry.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/custom_retry.go

Purpose: Classifies storage errors for retry and records retry metrics.

Important APIs/types/functions: `retryAction` enum, `determineRetryAction`, `ShouldRetryWithoutLogging`, `ShouldRetry`, and `ShouldRetryWithMonitoring`.

Control flow: `determineRetryAction` first delegates to `storage.ShouldRetry`, then special-cases HTTP 401 `googleapi.Error` and gRPC `codes.Unauthenticated` for credential-refresh retries. Logging variants emit warning messages; monitoring variant records `metrics.GcsRetryCount` for retryable errors and distinguishes `context.DeadlineExceeded` as stalled read requests.

State and persistence behavior: no persistent state; writes logs and metrics through global logger/metric handle.

Dependencies and integration points: used by generic retry executor and storage operations. Coupled to Cloud Storage SDK retry policy, Google API errors, gRPC status codes, and generated metric attributes.

Risks: retrying 401/Unauthenticated is a workaround for token timing issues and can hide persistent auth failures until retry budgets expire. `ShouldRetryWithMonitoring` assumes non-nil metric handle. Logging can be noisy on repeated transient errors.

Test signals: `custom_retry_test.go` covers 401/429/502, 400, unexpected EOF, network reset/refused, gRPC Unauthenticated, non-logging behavior, log contents, and metric category recording.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/custom_retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/custom_retry_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/custom_retry_test.go

Purpose: Unit tests for custom retry classification, logging, and retry metrics.

Important APIs/types/functions: tests cover `ShouldRetry`, `ShouldRetryWithoutLogging`, `determineRetryAction`, and `ShouldRetryWithMonitoring`; helper `logBuffer` captures logger output; `fakeMetricHandle` records retry metric calls.

Control flow: table-driven tests pass representative errors from Google API, gRPC status, net/url wrappers, context deadlines, and generic errors, then assert retry decision or metric/log side effects.

State and persistence behavior: temporarily redirects the global logger output and restores it to `os.Stdout`. No files or external services are used.

Dependencies and integration points: verifies assumptions about `storage.ShouldRetry` for network and HTTP classes, plus integration with generated `metrics.RetryErrorCategory` values.

Risks: retry classification inherited from `cloud.google.com/go/storage` may change. String-based network error cases depend on SDK behavior.

Test signals: strong coverage of retry edge cases, especially credential-refresh workarounds and stalled-read metric tagging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/custom_retry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/delete_all_objects.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/delete_all_objects.go

Purpose: Deletes every object from a bucket using pipelined listing and parallel deletion.

Important APIs/types/functions: `DeleteAllObjects(ctx, bucket)` uses `ListPrefix`, an object-name channel, and 64 deletion workers that call `bucket.DeleteObject`.

Control flow: one goroutine lists all objects into `minObjects`; a second goroutine extracts names into `objectNames`; workers drain names and delete. `errgroup.WithContext` cancels the pipeline on first error.

State and persistence behavior: destructively removes objects from the supplied bucket. Concurrent bucket updates produce undefined results and no rollback is attempted.

Dependencies and integration points: depends on `ListPrefix`, `gcs.Bucket`, `gcs.DeleteObjectRequest`, and `errgroup`; likely used in tests or cleanup utilities.

Risks: partial deletion on error, fixed high parallelism, and undefined behavior during concurrent writes. It ignores generations and deletes by name with default generation semantics.

Test signals: no direct test in this subset; integration cleanup behavior is the likely signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/delete_all_objects.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/delete_object.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/delete_object.go

Purpose: Thin helper to delete one object by name.

Important APIs/types/functions: `DeleteObject(ctx, bucket, name)` creates `gcs.DeleteObjectRequest{Name: name, Generation: 0}` and delegates to `bucket.DeleteObject`.

Control flow: no retry or precondition logic in the helper.

State and persistence behavior: removes a named object from the bucket according to bucket implementation semantics.

Dependencies and integration points: used by test utilities and callers needing a concise delete wrapper.

Risks: generation is hard-coded to zero, so callers needing generation-specific deletes cannot use this helper.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/delete_object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/list_all.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/list_all.go

Purpose: Collects all pages for a `ListObjectsRequest`.

Important APIs/types/functions: `ListAll(ctx, bucket, req)` returns accumulated `[]*gcs.MinObject`, collapsed runs, and error; it mutates `req.ContinuationToken`.

Control flow: repeatedly calls `bucket.ListObjects`, appends objects and collapsed runs, exits when continuation token is empty, otherwise updates the request token.

State and persistence behavior: no persistent state, but it mutates the caller-provided request.

Dependencies and integration points: used by tests or higher-level listing helpers over `gcs.Bucket`.

Risks: callers reusing `req` after failure or completion see its continuation token changed. It accumulates all results in memory and may be expensive for large buckets.

Test signals: no direct local test; behavior can be validated via fake bucket paging tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/list_all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/list_prefix.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/list_prefix.go

Purpose: Streams all objects with a given prefix into a caller-provided channel.

Important APIs/types/functions: `ListPrefix(ctx, bucket, prefix, minObjects)` builds `gcs.ListObjectsRequest{Prefix: prefix}` and sends each `MinObject` through `minObjects`.

Control flow: paginates via continuation token, sends each page's objects, and respects context cancellation while sending. It wraps list errors as `ListObjects: ...`.

State and persistence behavior: no persistence; caller owns channel closure.

Dependencies and integration points: used by `DeleteAllObjects` and fixture/listing utilities.

Risks: if receiver does not drain the channel, the function blocks until context cancellation. It does not emit collapsed runs, only objects.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/list_prefix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/md5.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/md5.go

Purpose: Provides an MD5 checksum helper for object creation requests.

Important APIs/types/functions: `MD5(contents []byte) *[md5.Size]byte` returns `md5.Sum(contents)` as a pointer.

Control flow: one-shot checksum over an in-memory byte slice.

State and persistence behavior: no state beyond returned heap-escaped checksum.

Dependencies and integration points: depends on Go `crypto/md5`; intended for `gcs.CreateObjectRequest.MD5`.

Risks: MD5 may be unavailable or discouraged for security use, but here it is an integrity checksum. Large content requires full byte slice in memory.

Test signals: object attribute tests validate MD5 byte conversion paths, though not this helper directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/md5.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/object_attrs.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/object_attrs.go

Purpose: Converts between Cloud Storage SDK object attributes and gcsfuse internal object models, and applies internal create-object attributes to `storage.Writer`.

Important APIs/types/functions: ACL converters, `ObjectAttrsToBucketObject`, `ObjectAttrsToMinObject`, `SetAttrsInWriter`, `ConvertObjToMinObject`, `ConvertObjToExtendedObjectAttributes`, `ConvertMinObjectAndExtendedObjectAttributesToObject`, and `ConvertMinObjectToObject`.

Control flow: conversion functions copy fields directly, translate ACL project-team structures, convert MD5 slices to fixed arrays, copy CRC32C values so returned pointers do not alias SDK structs, and split/merge minimal versus extended object attributes.

State and persistence behavior: no persistence, but returned objects often share maps/slices from inputs except checksum scalar copies. `SetAttrsInWriter` mutates a supplied `storage.Writer` and enables `SendCRC32C` when CRC is present.

Dependencies and integration points: central adapter between `cloud.google.com/go/storage`, JSON storage v1 ACL structures, and internal `gcs` types used by bucket implementations and file-system metadata paths.

Risks: some fields are intentionally omitted, so SDK attribute additions require review. `SetAttrsInWriter` ignores `time.Parse` errors for custom time. Metadata maps are not deep-copied. Nil handling differs: merge requires both min and extended attributes non-nil.

Test signals: `object_attrs_test.go` provides broad field-by-field coverage for ACL conversion, writer assignment, nil handling, split/merge conversions, and default extended-field values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/object_attrs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/object_attrs_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/object_attrs_test.go

Purpose: Field-level tests for object attribute conversion helpers.

Important APIs/types/functions: OgleTest suite `objectAttrsTest` covers ACL conversions, `ObjectAttrsToBucketObject`, `SetAttrsInWriter`, `ConvertObjToMinObject`, `ConvertObjToExtendedObjectAttributes`, `ConvertMinObjectAndExtendedObjectAttributesToObject`, and `ConvertMinObjectToObject`.

Control flow: tests build representative SDK/internal objects with timestamps, metadata, MD5/CRC, ACLs, and extended fields, invoke conversion helpers, and assert each relevant output field. Nil input cases verify safe nil returns.

State and persistence behavior: all in-memory; no external services.

Dependencies and integration points: depends on Cloud Storage SDK objects, internal `gcs` types, OgleTest, and JSON API ACL types.

Risks: field-by-field expectations can lag when object schemas evolve. Some assertions compare map/slice identity values and time string forms rather than deep normalized semantics.

Test signals: strong adapter coverage; gaps include parse-error behavior for invalid custom time and deep-copy/aliasing guarantees for maps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/object_attrs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/read_object.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/read_object.go

Purpose: Reads an entire object's latest generation into memory.

Important APIs/types/functions: `ReadObject(ctx, bucket, name)` creates `gcs.ReadObjectRequest`, calls `bucket.NewReaderWithReadHandle`, defers close, and returns `io.ReadAll` bytes.

Control flow: reader construction errors return directly; read errors are wrapped as `ReadAll`; close errors are returned only if no previous error occurred.

State and persistence behavior: no persistence; consumes a storage reader and closes it.

Dependencies and integration points: depends on `gcs.Bucket`, `gcs.StorageReader`, and Go `io`.

Risks: reads whole object into memory, unsuitable for large objects. It does not request a specific generation or byte range.

Test signals: no direct test in this subset; behavior is simple and suited for fixture assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/read_object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/retry.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/retry.go

Purpose: Implements generic retry execution with per-attempt deadlines, total retry budget, max attempts, jittered exponential backoff, logging, and custom retry predicates.

Important APIs/types/functions: constants `DefaultRetryDeadline`, `DefaultTotalRetryBudget`, `DefaultInitialBackoff`; `exponentialBackoffConfig`, `exponentialBackoff`; `RetryConfig`; `NewRetryConfig`; `ExecuteWithCustomShouldRetryAtLogLevel`, `ExecuteWithCustomShouldRetry`, `ExecuteWithRetryAtLogLevel`, and `ExecuteWithRetry`.

Control flow: executor checks pre-cancelled context, wraps parent with total budget, then loops attempts with per-attempt timeout. It logs initial call at caller-supplied level and retries at warning, stops on success, max attempts, non-retryable error, parent timeout, or backoff cancellation.

State and persistence behavior: no persistent state. Backoff state is per operation. Uses package-global `math/rand` for jitter and internal logger.

Dependencies and integration points: used by auth universe-domain lookup and storage retry wrappers. Coupled to `StorageClientConfig` retry fields and `ShouldRetryWithoutLogging`.

Risks: random jitter and real timers make tests timing-sensitive. If retry predicate is too broad, errors can be retried until budget exhaustion. Error wrapping mixes last server/client error with context errors; callers should use `errors.Is` for context.

Test signals: `retry_test.go` covers backoff growth, jitter bounds, cancellation, retry config construction, success/failure paths, parent versus total deadlines, max attempts, custom predicates, and retry log content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/retry_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/retry_test.go

Purpose: Unit tests for retry backoff and generic retry executor behavior.

Important APIs/types/functions: suites `ExponentialBackoffTestSuite`, `RetryConfigTestSuite`, and `ExecuteWithRetryTestSuite`; tests cover `newExponentialBackoff`, `nextDuration`, `waitWithJitter`, `NewRetryConfig`, `ExecuteWithRetry`, and custom retry variants.

Control flow: backoff tests use small durations and assert growth/caps; executor tests use mock API functions returning success, retryable gRPC errors, non-retryable errors, context timeouts, and custom errors.

State and persistence behavior: temporarily redirects logger output for log verification. Tests rely on wall-clock timers but do not write persistent files.

Dependencies and integration points: validates compatibility with gRPC `codes.Unavailable`, context cancellation/deadline propagation, and internal logger levels.

Risks: timing thresholds may be flaky on overloaded systems. The suite does not seed or control jitter randomness, only bounds elapsed time.

Test signals: broad coverage of retry control-flow edges including parent context pre-cancel, shorter/longer deadline interactions, max attempts, total budget exhaustion, and log diagnostics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/retry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/test_util.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/test_util.go

Purpose: Supplies shared storage client test defaults and constants.

Important APIs/types/functions: `CustomEndpoint`, `CustomTokenUrl`, and `GetDefaultStorageClientConfig(keyFile)` returning a populated `StorageClientConfig`.

Control flow: constructs an HTTP/1 config with retry, timeout, user-agent, auth, HNS, read-stall retry defaults, and empty write config.

State and persistence behavior: no state; returns a new config value.

Dependencies and integration points: used heavily by storageutil and storage handle tests to reduce setup duplication and keep test defaults aligned with production config shape.

Risks: if production defaults change but this helper does not, tests may validate stale assumptions. User-agent string is fixed to a test build signature.

Test signals: not directly tested; its correctness is exercised by many dependent tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/test_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/testdata/key.json -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/testdata/key.json

Purpose: Minimal service-account-style JSON fixture for auth tests.

Important APIs/types/functions: contains standard service account fields including `type`, `project_id`, private key metadata placeholders, token/auth URLs, client IDs, cert URLs, and `universe_domain`.

Control flow: consumed by auth credential loaders in tests; not executable code.

State and persistence behavior: static testdata file. It must not contain real secrets; all values are placeholders.

Dependencies and integration points: used by `CreateTokenSource`, `GetClientAuthOptionsAndToken`, and storage handle auth tests.

Risks: auth library validation requirements can change and reject placeholder private key material. Any accidental replacement with real credentials would be a security incident.

Test signals: successful auth-helper tests confirm the fixture remains structurally acceptable for local credential parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/testdata/key.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/unsupported_path_util.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/unsupported_path_util.go

Purpose: Detects GCS object names/prefixes that are valid in GCS but unsupported by gcsfuse path semantics.

Important APIs/types/functions: unsupported substring/prefix/suffix/name lists and `IsUnsupportedPath(name string) bool`.

Control flow: returns true for `//`, `/../`, `/./`, leading slash, suffix `/.` or `/..`, and exact empty, `.`, or `..`; otherwise false.

State and persistence behavior: read-only package-level slices.

Dependencies and integration points: used by storage/listing or path validation layers to filter object names that cannot map cleanly to filesystem paths.

Risks: path rules are exact string checks, not normalization. Changes affect visible object filtering and may be user-facing.

Test signals: `unsupported_path_util_test.go` covers supported normal paths and unsupported empty/root/dot/double-slash/path traversal forms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/unsupported_path_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/unsupported_path_util_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/unsupported_path_util_test.go

Purpose: Table-driven tests for unsupported GCS path detection.

Important APIs/types/functions: `GcsUtilTest` suite and `TestIsUnsupportedPathName` cases call exported `IsUnsupportedPath`.

Control flow: tests names such as `foo`, `foo/bar`, `abc/`, double slashes, leading slash, empty, dot/dotdot suffixes, and benign strings containing dots.

State and persistence behavior: no state or external resources.

Dependencies and integration points: external-package test imports `storageutil` with dot import, validating only the public API.

Risks: tests encode current policy exactly; future support for some path forms requires intentional updates.

Test signals: good coverage of boundary strings for path traversal and empty/root names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/unsupported_path_util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/user_agent_round_tripper.go -->
## sources/user-network-fs/gcsfuse/internal/storage/storageutil/user_agent_round_tripper.go

Purpose: HTTP RoundTripper middleware that injects a configured User-Agent header when a custom HTTP client is used.

Important APIs/types/functions: `userAgentRoundTripper` with fields `wrapped http.RoundTripper` and `UserAgent string`; method `RoundTrip`.

Control flow: mutates the outgoing request header with `Set("User-Agent", UserAgent)` then delegates to wrapped transport.

State and persistence behavior: no persistent state; mutates request headers in-flight.

Dependencies and integration points: used by `CreateHttpClient` because `option.WithUserAgent` is incompatible with direct `WithHTTPClient` injection.

Risks: panics if `wrapped` is nil. It overwrites any existing User-Agent. Mutating shared requests could surprise callers, although normal `http.Client` use is per request.

Test signals: `client_test.go` verifies a server receives the configured user agent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storageutil/user_agent_round_tripper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/testify_mock_bucket.go -->
## sources/user-network-fs/gcsfuse/internal/storage/testify_mock_bucket.go

Purpose: Testify mock implementation of the internal `gcs.Bucket` interface for unit tests.

Important APIs/types/functions: `TestifyMockBucket` embeds `mock.Mock` and implements bucket operations: name/type, readers, object create/copy/compose/stat/list/update/delete/move, folder APIs, appendable/chunk writers, finalize/flush, multi-range downloader, and `GCSName`.

Control flow: each method calls `m.Called(...)`, type-asserts expected return values, and maps nil/error combinations to interface returns. Some methods pass simplified arguments, such as `FinalizeUpload` using `w.ObjectName()`.

State and persistence behavior: stores invocation expectations and call history in testify's mock state; no storage persistence.

Dependencies and integration points: supports tests across storage, file cache, writes, and folder logic that depend on `gcs.Bucket` without using the older Ogle mock.

Risks: several methods type-assert return values without nil guards, so tests must configure returns precisely. Argument lists differ from production signatures in a few methods, which can hide callback/chunk-size issues.

Test signals: no direct tests here; it is a test support adapter and failures surface in dependent suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/testify_mock_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/diskutil/disk_util.go -->
## sources/user-network-fs/gcsfuse/internal/util/diskutil/disk_util.go

Purpose: Disk allocation helpers for estimating on-disk file size and discovering filesystem block size.

Important APIs/types/functions: constants `defaultVolumeBlockSize` and `maxVolumeBlockSize`; `GetSpeculativeFileSizeOnDisk(fileContentSize, volumeBlockSize)`; `GetVolumeBlockSize(path)`.

Control flow: speculative size rounds content bytes up to block size unless block size is 0 or 1. Volume block size calls `syscall.Statfs`, prefers `Frsize` over `Bsize`, and falls back to 4096 on statfs errors, zero, or suspiciously large block sizes.

State and persistence behavior: no persistence; reads filesystem metadata and logs fallback decisions.

Dependencies and integration points: used by cache/disk-accounting code that needs conservative allocation estimates.

Risks: syscall is Unix-specific. Overflow is not explicitly guarded in rounding formula for extreme sizes. Fallback log messages reference `Bsize` even when `Frsize` was used.

Test signals: `disk_util_test.go` covers rounding cases, valid temp directory block size, and invalid path fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/diskutil/disk_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/diskutil/disk_util_test.go -->
## sources/user-network-fs/gcsfuse/internal/util/diskutil/disk_util_test.go

Purpose: Tests disk utility rounding and block-size fallback behavior.

Important APIs/types/functions: `TestGetSpeculativeFileSizeOnDisk`, `TestGetVolumeBlockSize_ProperDir`, and `TestGetVolumeBlockSize_InvalidDir`.

Control flow: table-driven rounding cases cover zero/one block size, zero file size, exact block alignment, and round-up. Statfs tests use `t.TempDir()` and a definitely invalid path.

State and persistence behavior: creates a temporary directory; no persistent state.

Dependencies and integration points: validates syscall-backed block size only by positive power-of-two shape, not exact value.

Risks: filesystems can theoretically report non-power-of-two fragment sizes; test assumes common power-of-two behavior.

Test signals: focused coverage for the disk accounting API.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/diskutil/disk_util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/file_util.go -->
## sources/user-network-fs/gcsfuse/internal/util/file_util.go

Purpose: Represents FUSE file open modes and converts FUSE open flag abstractions into internal access/behavior flags.

Important APIs/types/functions: access constants `ReadOnly`, `WriteOnly`, `ReadWrite`; file flags `O_APPEND`, `O_DIRECT`; `OpenMode`; `NewOpenMode`; accessors; `IsAppend`; `IsDirect`; `OpenFlagAttributes`; `FileOpenMode`.

Control flow: access mode priority is read-only, then write-only, otherwise read-write. File flags OR append/direct bits. Append is considered active only for non-read-only modes.

State and persistence behavior: pure value logic, no persistence.

Dependencies and integration points: decouples gcsfuse logic from concrete `jacobsa/fuse` internal flag types and feeds metrics/write-mode decisions.

Risks: if a flag object reports inconsistent access booleans, read-only wins silently. `IsReadWrite` is not directly checked except by fallback behavior.

Test signals: `file_util_test.go` covers access modes and append/direct combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/file_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/file_util_test.go -->
## sources/user-network-fs/gcsfuse/internal/util/file_util_test.go

Purpose: Tests conversion from generic open flags to `OpenMode`.

Important APIs/types/functions: `mockOpenFlags` implements `OpenFlagAttributes`; `TestFileOpenMode` covers read-only, write-only, read-write, append, direct, and combined flags.

Control flow: each case constructs mock booleans, calls `FileOpenMode`, and compares to `NewOpenMode`.

State and persistence behavior: no state.

Dependencies and integration points: validates the abstraction used to avoid importing FUSE internal flag types.

Risks: does not test inconsistent flag combinations such as read-only and write-only both true, where production priority matters.

Test signals: good nominal coverage of all exported file-mode bits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/file_util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/sizeof.go -->
## sources/user-network-fs/gcsfuse/internal/util/sizeof.go

Purpose: Estimates nested memory footprint for selected gcsfuse data structures without general reflection-heavy traversal.

Important APIs/types/functions: initialized raw sizes for strings/slices; generic `UnsafeSizeOf`; content-size helpers for strings, string slices, maps, `googleapi.ServerResponse`; `NestedSizeOfGcsMinObject`; `NestedSizeOfGcsFolder`.

Control flow: raw size comes from `unsafe.Sizeof(*ptr)`. Content helpers recursively add string contents, map keys/values, slice members, and pointed-to CRC32C values. Nested object functions add raw struct size plus selected dynamic fields.

State and persistence behavior: package init records runtime raw sizes. No persistence.

Dependencies and integration points: supports memory accounting for metadata/cache objects using `gcs.MinObject`, `gcs.Folder`, and Google API responses.

Risks: estimates are convention-based and omit Go runtime/map overhead beyond key/value sizes. `UnsafeSizeOf` on interface pointers returns interface header size, documented as unsafe. Schema changes to `gcs.MinObject` require manual update.

Test signals: `sizeof_test.go` validates raw and content-size arithmetic; benchmarks measure helper overhead.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/sizeof.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/sizeof_bench_test.go -->
## sources/user-network-fs/gcsfuse/internal/util/sizeof_bench_test.go

Purpose: Benchmarks `UnsafeSizeOf` for common input categories.

Important APIs/types/functions: `BenchmarkUnsafeSizeOf_Int`, `BenchmarkUnsafeSizeOf_String`, and `BenchmarkUnsafeSizeOf_MinObject`.

Control flow: each benchmark constructs one value, resets timer, and repeatedly calls `UnsafeSizeOf`.

State and persistence behavior: no state or I/O.

Dependencies and integration points: validates performance expectation for low-overhead memory accounting helpers.

Risks: only benchmarks raw-size helper, not nested size functions where more work occurs.

Test signals: benchmark-only file; no correctness assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/sizeof_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/sizeof_test.go -->
## sources/user-network-fs/gcsfuse/internal/util/sizeof_test.go

Purpose: Correctness tests for raw and nested size calculations.

Important APIs/types/functions: tests for `UnsafeSizeOf`, `contentSizeOfString`, `contentSizeOfArrayOfStrings`, `contentSizeOfStringToStringMap`, `contentSizeOfStringToStringArrayMap`, `contentSizeOfServerResponse`, `NestedSizeOfGcsMinObject`, and `NestedSizeOfGcsFolder`.

Control flow: expected sizes are computed from `unsafe.Sizeof`, known string lengths, and helper constants; tests compare helper results across empty and populated values.

State and persistence behavior: in-memory only.

Dependencies and integration points: covers `gcs.MinObject`, `gcs.Folder`, `googleapi.ServerResponse`, and `http.Header` map structures.

Risks: expected values mirror implementation conventions and do not prove real heap usage. Map iteration order does not matter because values are summed.

Test signals: strong guard against accidental arithmetic/schema changes in manual memory-estimation code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/sizeof_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/test_util.go -->
## sources/user-network-fs/gcsfuse/internal/util/test_util.go

Purpose: Shared test helpers for random byte generation and read response flattening.

Important APIs/types/functions: `GenerateRandomBytes(length int)` and `ConvertReadResponseToBytes(data [][]byte, size int)`.

Control flow: random generation fills bytes with uppercase ASCII A-Z using `math/rand`; conversion copies each data slice into a fixed-size buffer in sequence.

State and persistence behavior: uses package-global pseudo-random source; no persistence.

Dependencies and integration points: used by tests that need reproducible-shape byte payloads or flatten chunked read responses.

Risks: random bytes are not cryptographic and are not seeded here. Conversion truncates or leaves zeros according to provided `size`; it does not validate total input length.

Test signals: not directly tested because it is test support code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/test_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/util.go -->
## sources/user-network-fs/gcsfuse/internal/util/util.go

Purpose: General utilities for path resolution, size-unit conversion, and global constants.

Important APIs/types/functions: constants `GCSFUSE_PARENT_PROCESS_DIR`, `MaxMiBsInUint64`, `MaxMiBsInInt64`, `MiB`, `KiB`, `HeapSizeToRssConversionFactor`, `MaxTimeDuration`; functions `GetResolvedPath`, `MiBsToBytes`, `BytesToHigherMiBs`.

Control flow: `GetResolvedPath` returns absolute/empty paths unchanged, expands `~/`, otherwise resolves relative paths against `GCSFUSE_PARENT_PROCESS_DIR` if set or current working directory via `filepath.Abs`. `MiBsToBytes` left-shifts with upper bound panic; `BytesToHigherMiBs` rounds bytes up using integer arithmetic and caps overflow shape.

State and persistence behavior: reads environment and current working directory; no persistence.

Dependencies and integration points: used by child process/config path handling and size limit calculations across gcsfuse.

Risks: `path.IsAbs` is used instead of `filepath.IsAbs`, which matters primarily on non-Unix paths. `MiBsToBytes` panics above supported range. Parent process directory is joined without cleaning.

Test signals: `util_test.go` covers path resolution with/without parent env and unit conversion boundaries; benchmark covers byte-to-MiB conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/util_benchmark_test.go -->
## sources/user-network-fs/gcsfuse/internal/util/util_benchmark_test.go

Purpose: Benchmarks `BytesToHigherMiBs`.

Important APIs/types/functions: `BenchmarkBytesToHigherMiBs` repeatedly converts one MiB in bytes.

Control flow: uses Go benchmark `b.Loop()` and discards result.

State and persistence behavior: no state.

Dependencies and integration points: protects performance of a conversion helper likely used in hot-ish configuration/accounting paths.

Risks: only one input size is benchmarked; overflow and non-aligned cases are not benchmarked.

Test signals: benchmark-only, no correctness assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/util_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/util_test.go -->
## sources/user-network-fs/gcsfuse/internal/util/util_test.go

Purpose: Tests path resolution and MiB/byte conversion utilities.

Important APIs/types/functions: Ogle-style `UtilTest` suite covers `GetResolvedPath`, `MiBsToBytes`, and `BytesToHigherMiBs`.

Control flow: path tests exercise absolute, empty, tilde, dot, dotdot, and plain relative paths with and without `GCSFUSE_PARENT_PROCESS_DIR`. Conversion tests cover zero, normal values, maximum supported MiB, and overflow-to-next-MiB behavior.

State and persistence behavior: temporarily sets/unsets `GCSFUSE_PARENT_PROCESS_DIR` and reads current working/home directories.

Dependencies and integration points: validates child-process path behavior described in `util.go`.

Risks: several suite methods are named without the `Test` prefix (`ResolveEmptyFilePath`, `ResolveWhen...`) and may not run under the suite framework depending on its discovery rules. The panic path for `MiBsToBytes` is not covered.

Test signals: useful coverage for common path and conversion cases, with a possible test-discovery gap for non-prefixed methods.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/util/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workerpool/static_worker_pool.go -->
## sources/user-network-fs/gcsfuse/internal/workerpool/static_worker_pool.go

Purpose: Fixed-size goroutine worker pool with separate priority and normal queues.

Important APIs/types/functions: `staticWorkerPool`, `NewStaticWorkerPool`, `NewStaticWorkerPoolForCurrentCPU`, `newStaticWorkerPoolForCurrentCPU`, `Start`, `Stop`, `Schedule`, and worker loop `do`.

Control flow: constructor validates nonzero workers and sizes channels by worker count capped by `2*readGlobalMaxBlocks`. CPU helper chooses `3*numCPU`, caps to `ceil(1.1*readGlobalMaxBlocks)`, reserves 10% priority workers, starts pool. Priority workers only consume priority tasks; normal workers prefer priority tasks but also consume normal tasks. `Stop` closes `stop`, waits, then closes task channels.

State and persistence behavior: maintains goroutines, channels, and wait group only in memory. Scheduled tasks execute side effects defined by `Task.Execute`.

Dependencies and integration points: implements `WorkerPool` for read/download scheduling or other background task execution. Uses internal logger and runtime CPU count.

Risks: reading from closed task channels yields nil `Task` and `task.Execute()` would panic if channels close before workers stop; current stop ordering mitigates by waiting before close. `Schedule` after stop panics. Zero `readGlobalMaxBlocks` with nonzero workers creates zero-cap channels and CPU helper can select zero total workers, causing constructor error.

Test signals: `static_worker_pool_test.go` covers constructor sizing, start/schedule/stop behavior, high task volume, post-stop panic, and CPU-based worker count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workerpool/static_worker_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workerpool/static_worker_pool_test.go -->
## sources/user-network-fs/gcsfuse/internal/workerpool/static_worker_pool_test.go

Purpose: Tests static worker pool construction, scheduling, execution, stop behavior, and CPU-based sizing.

Important APIs/types/functions: `dummyTask`, `TestNewStaticWorkerPool_Success/Failure`, `TestStaticWorkerPool_Start`, priority/normal scheduling tests, high task count, schedule-after-stop panic, stop channel closure assertions, and CPU helper tests.

Control flow: tests create pools, start them when needed, schedule dummy tasks, and use `assert.Eventually` to wait for execution or queue drain. Sizing tests assert channel capacities and worker counts.

State and persistence behavior: starts goroutines and closes them with `Stop`; no external state.

Dependencies and integration points: validates workerpool contract and runtime CPU helper. Uses testify assertions and timing loops.

Risks: `dummyTask.executed` is a plain bool written/read across goroutines, so tests have a data race under `-race`. Queue-empty assertions do not prove all tasks finished because a worker may have dequeued but not completed a task.

Test signals: broad functional coverage, with concurrency-race caveat.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workerpool/static_worker_pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workerpool/worker_pool.go -->
## sources/user-network-fs/gcsfuse/internal/workerpool/worker_pool.go

Purpose: Defines worker pool abstraction used by concrete schedulers.

Important APIs/types/functions: `Task` interface with `Execute()` and `WorkerPool` interface with `Start`, `Stop`, and `Schedule(urgent bool, task Task)`.

Control flow: interface-only file; concrete implementations decide scheduling and lifecycle semantics.

State and persistence behavior: none.

Dependencies and integration points: allows consumers to depend on a small interface rather than `staticWorkerPool`.

Risks: interface does not specify error handling, post-stop behavior, backpressure, or whether `Stop` drains queued tasks.

Test signals: concrete behavior is tested in `static_worker_pool_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workerpool/worker_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workloadinsight/io_renderer.go -->
## sources/user-network-fs/gcsfuse/internal/workloadinsight/io_renderer.go

Purpose: Renders byte-range I/O access patterns as ASCII charts with file offset axes and summary statistics.

Important APIs/types/functions: constants `blockChar`, `emptyChar`, `labelHeader`; `Range`; `Renderer`; `NewRenderer`; `NewRendererWithSettings`; `Render`; helpers `humanReadable`, `buildStats`, `buildHeader`, `buildRow`, and `mapCoord`.

Control flow: renderer validates dimensions, builds header with name, stats, offset labels, and axis, then builds one row per range. Rows validate range ordering and file bounds, map start/end offsets to plot columns, mark covered columns with block characters, and truncate/pad labels.

State and persistence behavior: pure string rendering; no persistence.

Dependencies and integration points: intended for workload insight/debug output that visualizes file access distributions. Depends only on standard library formatting, math, sorting, and strings.

Risks: `buildRow` computes `e := rg.End - 1`, so zero-length ranges underflow and can produce misleading errors or plotting behavior. `mapCoord` treats zero file size as invalid, so rendering empty files with ranges fails. Unicode block character makes output non-ASCII.

Test signals: `io_renderer_test.go` covers constructor validation, human-readable formatting, coordinate mapping, golden outputs for several file sizes/range sets, and invalid render ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workloadinsight/io_renderer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workloadinsight/io_renderer_test.go -->
## sources/user-network-fs/gcsfuse/internal/workloadinsight/io_renderer_test.go

Purpose: Tests ASCII I/O renderer formatting and validation.

Important APIs/types/functions: tests for `NewRenderer`, `NewRendererWithSettings`, `humanReadable`, `mapCoord`, `Render`, golden output comparisons, and invalid range handling.

Control flow: constructor tests check invalid and valid settings; mapping tests cover start/end/middle offsets; render tests compare exact strings from testdata golden files for default/custom settings and different file sizes.

State and persistence behavior: reads golden files under `testdata/io_renderer`; no writes unless commented regeneration lines are enabled.

Dependencies and integration points: validates user-visible debugging output exactly, including whitespace and block characters.

Risks: golden files make output changes intentional but can be brittle for formatting tweaks. Invalid settings test labels mention zero label width but use valid label widths in valid cases.

Test signals: strong regression signal for chart layout and range validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/workloadinsight/io_renderer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/main.go -->
## sources/user-network-fs/gcsfuse/main.go

Purpose: Entry point for the gcsfuse command-line binary.

Important APIs/types/functions: `logPanic`, `main`, and `go:generate` directives for config and metrics code generation.

Control flow: `main` defers panic recovery through `logPanic`, configures standard log timestamp flags, starts goroutines for CPU and memory profiling signal handlers, then delegates command execution to `cmd.ExecuteMountCmd()`.

State and persistence behavior: process-level logging configuration and profiling signal handlers. Any persistent effects are downstream of mount command execution.

Dependencies and integration points: integrates `cmd`, internal logger, and internal perf signal handlers. Generation directives connect `cfg/params.yaml` and `metrics/metrics.yaml` to generated Go files.

Risks: `logPanic` only catches panics in the main goroutine, not profiling goroutines or workers. Profiling handlers run for process lifetime. Generation comments are operationally important and should not be removed.

Test signals: no direct test in this subset; behavior is typically covered by command/integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/constants.go -->
## sources/user-network-fs/gcsfuse/metrics/constants.go

Purpose: Defines numeric read-type constants and maps them to generated metric attribute values.

Important APIs/types/functions: `ReadTypeUnknown`, `ReadTypeSequential`, `ReadTypeRandom`, `ReadTypeParallel`, and `ReadTypeNames map[int64]ReadType`.

Control flow: static map lookup converts numeric classifier output into `ReadType` attributes.

State and persistence behavior: package-level map is mutable at runtime unless treated as constant by convention.

Dependencies and integration points: connects read classification code to generated metrics attributes from `metric_handle.go`.

Risks: map mutability could allow accidental test or runtime mutation. Numeric constants must stay aligned with read-classifier producers.

Test signals: no direct test here; metrics behavior tests using read types can catch mismatches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/helper.go -->
## sources/user-network-fs/gcsfuse/metrics/helper.go

Purpose: Convenience helper for recording paired GCS read metrics.

Important APIs/types/functions: `CaptureGCSReadMetrics(mh MetricHandle, readType ReadType, downloadBytes int64)`.

Control flow: increments read count by one and download byte count by the provided byte count for the same read type.

State and persistence behavior: no local state; emits metric side effects through `MetricHandle`.

Dependencies and integration points: used by read paths to avoid duplicating two metric calls.

Risks: assumes `mh` is non-nil. It records download bytes but not `GcsReadBytesCount`, so callers must understand which metric pair is intended.

Test signals: no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/metric_handle.go -->
## sources/user-network-fs/gcsfuse/metrics/metric_handle.go

Purpose: Auto-generated metrics API defining attribute types/constants and the `MetricHandle` interface.

Important APIs/types/functions: attribute string types for entry status, filesystem errors/ops, GCS methods, I/O method, lookup detail, open mode, read type, fallback reason, request type, retry category, and write fallback reason. `MetricHandle` declares methods for all generated counters and histograms.

Control flow: interface-only generated file; concrete implementations record metrics, while noop implementation discards them.

State and persistence behavior: no state. The generated constants are compile-time labels used by metric emitters.

Dependencies and integration points: generated from `metrics.yaml` and used throughout gcsfuse for OpenTelemetry instrumentation and tests.

Risks: manual edits will be overwritten. Schema changes must keep `metrics.yaml`, generated handle, noop implementation, and otel implementation synchronized.

Test signals: metrics implementation tests and helpers validate concrete emission; this file itself is compile-time checked by implementers such as `noopMetrics`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/metric_handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/metrics.yaml -->
## sources/user-network-fs/gcsfuse/metrics/metrics.yaml

Purpose: Source schema for generated metrics code.

Important APIs/types/functions: YAML entries define metric names, descriptions, units, types, histogram boundaries, attributes, and allowed values. Anchors share microsecond, millisecond, byte, read-type, and GCS-method lists.

Control flow: consumed by `tools/metrics-gen` from the `main.go` go-generate directive to produce `metric_handle.go`, `noop_metrics.go`, and concrete OpenTelemetry code.

State and persistence behavior: static configuration; edits regenerate code and affect telemetry contracts.

Dependencies and integration points: defines all observable gcsfuse metric names including buffered read fallback/latency, file cache reads, fs ops/errors/latency, streaming write fallback, GCS read/download/request/retry metrics, metadata cache reads, block sizes, and test up-down counters.

Risks: changing names, units, boundaries, or attribute values is a telemetry compatibility change. YAML anchors reduce duplication but can hide broad impact from local edits.

Test signals: generated code compilation and OpenTelemetry metric tests validate schema consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/metrics.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/metrics_test_utils.go -->
## sources/user-network-fs/gcsfuse/metrics/metrics_test_utils.go

Purpose: Shared assertions for OpenTelemetry metric tests.

Important APIs/types/functions: `verifyConfig`, `VerifyOption`, `AtLeast`, `Subset`, `matchesAttributes`, `verifyValue`, `VerifyCounterMetric`, `VerifyHistogramMetric`, and `VerifyHistogramFull`.

Control flow: helpers collect from a `metric.ManualReader`, scan all scope metrics by name, match attribute sets exactly or as subset, assert values exactly or at least, and support integer/float histograms with optional bucket verification.

State and persistence behavior: reads metric data from in-memory OpenTelemetry reader; no persistence.

Dependencies and integration points: used by metrics implementation tests to verify generated instruments without duplicating OpenTelemetry traversal code.

Risks: helpers fail on the first matching data point and do not aggregate multiple data points. Exact attribute encoding depends on OpenTelemetry encoder behavior.

Test signals: these are test support utilities; reliability affects all metrics tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/metrics_test_utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/noop_metrics.go -->
## sources/user-network-fs/gcsfuse/metrics/noop_metrics.go

Purpose: Auto-generated no-op implementation of `MetricHandle`.

Important APIs/types/functions: unexported `noopMetrics` implements every `MetricHandle` method with empty bodies; `NewNoopMetrics()` returns it as a `MetricHandle`.

Control flow: all metric calls are accepted and discarded.

State and persistence behavior: no state or metric emission.

Dependencies and integration points: used when metrics are disabled and in tests that need a non-nil metric handle, such as retry monitoring tests.

Risks: must be regenerated whenever `MetricHandle` changes. Because it silently drops metrics, accidental use in production instrumentation paths can hide telemetry.

Test signals: compile-time interface conformance is the main signal; dependent tests use it as a safe stub.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/metrics/noop_metrics.go -->
