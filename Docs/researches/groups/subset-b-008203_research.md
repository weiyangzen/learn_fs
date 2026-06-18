# subset-b-008203 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/s3-zip-handlers.go -->
# sources/object-store/minio/cmd/s3-zip-handlers.go

Purpose: This file implements MinIO's S3 "zip object as virtual prefix" behavior. A stored object whose name contains `.zip/` can be treated as an archive, allowing GET, HEAD, and ListObjectsV2 to address entries inside the zip without materializing them as separate objects. It also maintains internal archive metadata (`x-minio-internal-archive-type` and `x-minio-internal-archive-info`) so future archive operations can avoid rescanning the zip central directory.

Important APIs and types: Key constants define archive routing (`archiveExt`, `archivePattern`, `archiveSeparator`, `xMinIOExtract`) and metadata keys. `splitZipExtensionPath` separates the actual zip object path from the inner member path. `objectAPIHandlers.getObjectInArchiveFileHandler` and `headObjectInArchiveFileHandler` are HTTP handlers for virtual GET/HEAD. `listObjectsV2InArchive` synthesizes `ListObjectsV2Info` from a serialized `zipindex.Files`. `getFilesListFromZIPObject` reads suffix ranges from the zip object until `zipindex.ReadDir` can parse the directory, and `updateObjectMetadataWithZipInfo` serializes and persists the archive index through `ObjectLayer.PutObjectMetadata`.

Control flow: GET/HEAD reject SSE-S3/SSE-KMS request headers for archive extraction, split the path, build `ObjectOptions`, enforce authorization against the real zip object, reject part-number and range addressing inside archive members, evaluate preconditions against the parent object, obtain or lazily create serialized zip metadata, locate the requested entry with `zipindex.FindSerialized`, then either stream the compressed entry range through `file.Open` or return headers for HEAD. Listing splits the archive prefix, loads or updates archive metadata, sorts zip entries by name, applies `startAfter`, continuation token, prefix, delimiter, and max-keys rules, and returns either object rows or common prefixes.

State and persistence behavior: The durable state is the original zip object plus optional metadata on the same object version. `updateObjectMetadataWithZipInfo` preserves mtime and version ID, may encrypt archive info metadata when the source object requires metadata encryption, and writes the index in-place through object metadata evaluation. GET/HEAD never create separate objects; they synthesize `ObjectInfo` from the zip member and parent object's modtime. `getFilesListFromZIPObject` increases suffix reads based on `zipindex.ErrNeedMoreData` and rejects directories larger than 100 MiB.

Dependencies and integration points: This code depends on MinIO object-layer calls (`GetObjectInfo`, `GetObjectNInfo`, `PutObjectMetadata`), request auth and policy evaluation, object precondition helpers, server-side encryption metadata helpers, response header helpers, and `github.com/minio/zipindex`. It integrates with normal S3 object routing, list-object responses, internal reserved metadata, and encrypted-object metadata handling.

Risks: The feature relies on accurate zip central-directory parsing from suffix ranges and on trusting serialized index metadata once present. Lazy metadata updates introduce write behavior on first archive access and can fail under metadata quorum, encryption-key, versioning, or permission edge cases. Range and part-number requests are intentionally rejected for virtual members, which can surprise generic S3 clients. Listing uses object-name string comparison for token/startAfter behavior, so path encoding and delimiter semantics need compatibility attention.

Test signals: There is no direct test file in this work item. Useful coverage should verify GET/HEAD success and `NoSuchKey` behavior for archive entries, anonymous AccessDenied-vs-NoSuchKey mapping, metadata creation and reuse, encrypted metadata paths, invalid range/part-number errors, delimiter/common-prefix listing, continuation tokens, malformed zip handling, large central-directory rejection, and versioned object metadata preservation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/s3-zip-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/scannermetric_string.go -->
# sources/object-store/minio/cmd/scannermetric_string.go

Purpose: This is generated `stringer` output for the `scannerMetric` enum defined elsewhere in the data scanner code. It provides stable, allocation-light names for scanner metrics used in tracing, logging, metrics labels, or diagnostics.

Important APIs and types: The only exported behavior here is `(scannerMetric).String() string`. The generated `_()` function contains compile-time array-index checks tying this file to exact enum ordinal values from `scannerMetricReadMetadata` through `scannerMetricLast`. `_scannerMetric_name` stores concatenated names, and `_scannerMetric_index` stores byte offsets into that string.

Control flow: `String` bounds-checks the metric value against the index table. Known values return a slice of `_scannerMetric_name`; unknown values return a fallback of the form `scannerMetric(<n>)` using `strconv.FormatInt`.

State and persistence behavior: There is no runtime mutable state or persistence. The important state is generated source consistency: if enum order changes without regenerating this file, compile-time checks should fail.

Dependencies and integration points: It depends on the `scannerMetric` constants in data scanner code and on Go's `strconv`. Consumers use the string form when scanner phases are reported or traced, so name stability matters for observability.

Risks: Manual edits or stale generation can mislabel scanner phases. The index table uses `uint8`, which is sufficient for the current concatenated string length but would need regeneration if names or count grow beyond its assumptions. The file should not be hand-maintained.

Test signals: There are no direct tests in this subset. Compiler failures from the generated guard are the main safety signal; observability tests elsewhere could assert selected metric names.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/scannermetric_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/server-main.go -->
# sources/object-store/minio/cmd/server-main.go

Purpose: This file defines the `minio server` CLI command and the main server bootstrap sequence. It translates CLI flags, environment variables, and optional YAML config into a `serverCtxt`, configures network/TLS/transports/global subsystems, starts the S3 HTTP server, creates the object layer, initializes configuration/IAM/bucket subsystems, starts optional FTP/SFTP/Console services, prints startup information, and then waits for shutdown signals.

Important APIs and types: `ServerFlags` exposes server flags for addresses, timeouts, network interface, FTP/SFTP, memory limit, socket buffers, and log rotation. `serverCmd` registers the CLI action. `serverCmdArgs`, `configCommonToSrvCtx`, and `mergeServerCtxtFromConfigFile` form the config ingestion path. `serverHandleCmdArgs` validates endpoints, TLS, root CAs, setup type, node identity, transports, proxying, and port availability. `initAllSubsystems`, `initServerConfig`, and `initConfigSubsystem` initialize global runtime systems. `bootstrapTrace` and `bootstrapTraceMsg` record startup traces. `getServerListenAddrs` computes listen addresses, `initializeLogRotate` configures JSON log rotation, `serverMain` is the main orchestrator, and `newObjectLayer` constructs erasure server pools.

Control flow: Startup registers signal handling, initializes logging, loads env files and early env vars, builds server context and endpoints, starts DNS cache, runs self-tests and KMS setup, loads or generates root credentials, initializes help and global subsystems, validates distributed TLS endpoint consistency, starts update checks and resource-limit tuning, configures grid and lock-grid RPC services, creates the HTTP server, verifies distributed system config, optionally freezes services for sync boot, creates the object layer, waits for read quorum, initializes config, starts IAM/Console/FTP/SFTP in a goroutine, starts scanner/replication/ILM/transition/notification/bucket metadata/site replication/batch job systems in another goroutine, creates a local MinIO client, starts resource metrics, notifies systemd, then blocks on `globalOSSignalCh`.

State and persistence behavior: The file mutates most process-level server globals: endpoints, node identity hashes, TLS/root CA state, transports, proxy forwarder, subsystem singletons, active credentials, node auth token, bucket/config/IAM systems, log output, object layer, HTTP server, console server, warning list, MinIO client, and bootstrap traces. YAML config parsing persists nothing directly but builds disk layout state. Log rotation persists server logs under `--log-dir`. Config subsystem initialization reads and may migrate configuration through the object layer.

Dependencies and integration points: It is the central integration point for `cli`, MinIO config/env packages, TLS cert loading, DNS cache, grid RPC, lock grid, HTTP routing and CORS, erasure object layer, KMS, IAM, policy, bucket metadata, lifecycle, replication, tiering, notifications, console, FTP/SFTP, metrics, systemd notifications, logger, and MinIO client libraries. `server-main_test.go` directly covers config-file parsing and object-layer creation.

Risks: The bootstrap sequence depends heavily on global state and goroutines, making order and test isolation critical. Retriable config errors loop with jitter and can mask persistent quorum/config problems until cancellation. Startup warnings are appended from multiple goroutines without explicit synchronization. Distributed TLS mismatch, dynamic port use, DNS lookup failures, and old/low-resource host settings affect whether startup fails or warns. `serverMain` blocks on global signal channels, so tests generally exercise helper functions rather than the full entry point.

Test signals: `TestServerConfigFile` verifies valid and invalid YAML config parsing and stable pool command-line hashes. `TestNewObjectLayer` verifies one-drive and sixteen-drive temporary backends produce `*erasureServerPools`. Broader integration signals come from `server_test.go`, which starts test servers across erasure modes and exercises S3 behavior through the HTTP stack initialized by this path.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/server-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/server-main_test.go -->
# sources/object-store/minio/cmd/server-main_test.go

Purpose: This file contains focused tests for server configuration-file parsing and object-layer initialization. It protects `mergeServerCtxtFromConfigFile` compatibility with bundled YAML fixtures and verifies that `newObjectLayer` produces the erasure server-pool implementation for supported local disk counts.

Important APIs and types: `TestServerConfigFile` uses `mergeServerCtxtFromConfigFile`, `serverCtxt`, and expected `Layout.pools` hashes. `TestNewObjectLayer` uses `getRandomDisks`, `removeRoots`, `mustGetPoolEndpoints`, `newObjectLayer`, and checks the returned object with `reflect.TypeOf` / type assertion to `*erasureServerPools`.

Control flow: The config test iterates valid and invalid fixture paths, expects errors for invalid YAML/type/disk layouts, and for valid fixtures asserts that two pools were parsed and the first pool's stable hash matches the fixture expectation. The object-layer test creates temporary disk paths for a single-drive backend, initializes the layer, validates its concrete type, then repeats for a sixteen-disk backend.

State and persistence behavior: Tests create temporary backend directories and remove them after each object-layer initialization. Config parsing reads YAML files from `testdata/config` but does not persist state. Object-layer initialization may create MinIO metadata on the temporary disks as part of erasure pool setup.

Dependencies and integration points: These tests connect CLI config parsing to erasure layout construction and object-layer initialization. They depend on test helpers from the MinIO cmd package, context cancellation, local filesystem temp roots, and the erasure server-pool implementation.

Risks: The expected pool hash values couple the test to layout hashing details; legitimate config parser or layout changes require fixture/hash updates. The object-layer test asserts a concrete type rather than an interface contract, which is useful for detecting backend selection changes but brittle if implementation names change.

Test signals: Success means valid config files produce two pools with expected hashes, invalid fixtures fail, and both one-disk and sixteen-disk endpoint sets initialize without error as `*erasureServerPools`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/server-main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/server-rlimit.go -->
# sources/object-store/minio/cmd/server-rlimit.go

Purpose: This file centralizes process resource-limit tuning and a Linux kernel age check used during server startup. It tries to raise Go runtime and OS limits to values suitable for MinIO's high-concurrency object server workload.

Important APIs and types: `oldLinux` calls `kernel.CurrentVersion` and compares it to `kernel.Version(4,0,0)`. `setMaxResources` reads max kernel threads, open-file limits, virtual memory limits, and optional `serverCtxt.MemLimit`; it calls `debug.SetMaxThreads`, `sys.SetMaxOpenFileLimit`, and `debug.SetMemoryLimit`.

Control flow: `oldLinux` returns false if the kernel cannot be probed or returns zero, otherwise reports whether it is older than Linux 4.0. `setMaxResources` sets Go's max thread count to 90% of the kernel setting when above the default threshold, retrieves the max file descriptor limit, warns if it is below 4096 on non-Windows, sets the soft/hard open-file limits to the maximum, warns for very small virtual memory limits, applies a Go memory limit if configured, and deliberately avoids setting RLIMIT_AS.

State and persistence behavior: There is no application persistence. The function mutates process/runtime limits for the running server process and may change OS resource-limit soft values. It logs warnings for low production limits.

Dependencies and integration points: `serverMain` calls `setMaxResources` during bootstrap and uses `oldLinux` to append startup warnings. The file depends on MinIO's `serverCtxt`, `logger`, `sys` package abstractions, `madmin-go/kernel`, Go runtime/debug, and `humanize`.

Risks: Resource-limit changes are platform-sensitive and permission-sensitive. Errors from open-file or memory-limit probing propagate, but `serverMain` currently ignores the returned error. Raising max threads and file limits can fail under containers or restricted services. The code intentionally avoids RLIMIT_AS because small values can crash the Go runtime.

Test signals: There are no direct tests here. Indirect signals are startup warnings for old kernels or low limits, and successful server boot under constrained environments.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/server-rlimit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/server-startup-msg.go -->
# sources/object-store/minio/cmd/server-startup-msg.go

Purpose: This file formats and prints MinIO startup output: banner, API endpoints, WebUI endpoints, root credentials when allowed, region, configured notification/lambda ARNs, CLI setup guidance, and docs link. It also normalizes displayed endpoint URLs by stripping standard ports in multi-endpoint output.

Important APIs and types: `getFormatStr` builds printf width strings. `printStartupMessage` orchestrates banner and startup sections. `isIPv6` detects IPv6 hosts. `stripStandardPorts` removes `:80` from HTTP and `:443` from HTTPS endpoint displays when multiple endpoints are present. `printServerCommonMsg`, `printObjectAPIMsg`, `printLambdaTargets`, `printEventNotifiers`, and `printCLIAccessMsg` print individual startup sections.

Control flow: `printStartupMessage` prints the distributed banner framing when needed, reports startup errors to console, prints the startup banner unless subnet is registered, strips standard API ports, prints common API/WebUI info, prints CLI access using the first endpoint, prints docs, and closes the distributed banner. Common message printing reads global active credentials, region, API endpoints, Console endpoints, browser flag, API root-access permission, terminal/color state, notification targets, and lambda targets.

State and persistence behavior: There is no persistence. The code reads global server state and emits to `logger.Startup` and sometimes `globalConsoleSys`. It may reveal root credentials on terminal output when anonymous/JSON modes are off and root access is permitted.

Dependencies and integration points: It integrates with startup bootstrap in `server-main.go`, `logger`, color handling, Console system, subnet registration state, global API/browser config, notification system, lambda target list, endpoint discovery helpers, and MinIO documentation links.

Risks: Startup output depends on global state and terminal detection, so behavior can differ under JSON logging, tests, consoles, or non-interactive services. Credential printing is intentionally gated but security-sensitive. `stripStandardPorts` leaves empty strings for skipped IPv6 entries when host is empty and multiple endpoints are processed, which callers must tolerate in joined output.

Test signals: `server-startup-msg_test.go` verifies standard-port stripping behavior and smoke-tests the printing functions after creating test config.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/server-startup-msg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/server-startup-msg_test.go -->
# sources/object-store/minio/cmd/server-startup-msg_test.go

Purpose: This test file verifies endpoint-display normalization and smoke-tests the startup message printers against initialized test configuration.

Important APIs and types: Tests call `stripStandardPorts`, `printServerCommonMsg`, `printCLIAccessMsg`, and `printStartupMessage`. Setup helpers include `prepareFS`, `newTestConfig`, and `globalMinioDefaultRegion`.

Control flow: `TestStripStandardPorts` asserts that HTTP `:80` and HTTPS `:443` are stripped from a multi-endpoint list, malformed URLs are left unchanged, and non-standard scheme/port pairings are preserved. The print tests prepare a filesystem object layer, initialize test config, and call the printing functions with `http://127.0.0.1:9000`.

State and persistence behavior: The print tests create temporary filesystem state through `prepareFS`, initialize global MinIO test config, and remove the temp directory. The output itself is written to the startup logger and is not captured for content assertions.

Dependencies and integration points: The tests depend on server test helpers and global startup/config state. They exercise formatting functions without running a full server bootstrap.

Risks: The smoke tests primarily guard against panics, not exact logged content. Changes to terminal/color/global credential behavior may not be caught unless they affect execution. `TestStripStandardPorts` is the main functional assertion.

Test signals: Expected stripped endpoints, unchanged malformed/nonstandard endpoints, and successful execution of message printers after test config initialization.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/server-startup-msg_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/server_test.go -->
# sources/object-store/minio/cmd/server_test.go

Purpose: This is a broad S3 API integration suite run against MinIO test servers across multiple backend modes and signing modes. It validates bucket, object, listing, policy, notification, range, checksum, multipart, CORS, metrics, and security-regression behavior through real HTTP requests.

Important APIs and types: `TestSuiteCommon` holds test server, endpoint, credentials, signer, TLS flag, and HTTP client. `check` wraps `testing.T` with `Assert`. `verifyError` parses XML `APIErrorResponse`. `runAllTests` sequences the full suite. `TestServerSuite` runs ErasureSD with V4, ErasureSD with V2, ErasureSD over TLS, Erasure, and ErasureSet. Suite methods cover metrics, CORS, directory objects, unsigned streaming trailer CVE regression, bucket notifications, bucket policies, bucket/object create/delete/head/get, anonymous access, list objects and versions, content type, range reads, invalid parameters, large objects, multipart initiation/list/abort/complete, MD5 validation, and signature validation.

Control flow: Each suite setup starts a temporary MinIO test server, records credentials and endpoint, and each test constructs signed or unsigned HTTP requests with helper URL builders. Operations usually create a random bucket, perform one or more S3 actions, then assert status codes, XML error payloads, response headers, response bodies, or parsed XML structures. Some tests use concurrency to expose bucket-creation races, restart support to reuse object layers, or TLS test servers. The suite is explicitly ordered by `runAllTests`.

State and persistence behavior: The tests create real buckets, objects, bucket policies, notification configs, versioning state, multipart upload state, and temporary erasure/fs backend data under the test server. They verify persistence across API calls for object contents, content type metadata, Last-Modified headers, bucket creation timestamps, object delete behavior, version/delete-marker listing, multipart upload records, and ETag/MD5 semantics. Teardown stops the test server and object layer.

Dependencies and integration points: This suite integrates the HTTP router, authentication/signature V2/V4 signing helpers, object layer implementations, XML marshaling/unmarshaling, bucket policy parser, notification validation, metrics JWT auth, MinIO test server harness, range handling, multipart implementation, CORS middleware, SHA256/checksum code, and platform-specific path length behavior.

Risks: The suite is large, ordered, and stateful, so failures can cascade when setup or global state is contaminated. It is timing-sensitive for bucket creation times and can be expensive because it writes 10 MiB and 11 MiB objects repeatedly across backend/signing combinations. Some tests assert exact XML fragments rather than parsed semantic structures. The concurrent bucket test is intended for race detection but does not assert detailed correctness inside goroutines. The MD5-invalid case expects a signature mismatch because the signature covers the header, which can be non-obvious.

Test signals: Strong signals include exact HTTP status codes, exact S3 error code/message/status triples, response body equality, ETag equality for multipart, Last-Modified precondition outcomes, Content-Type preservation, partial byte-range equality, list XML content and ordering, version/delete-marker ordering, metrics paths accepting JWT auth, invalid notification ARNs, invalid bucket/key/range/max-parts errors, SHA256 mismatch errors for V4, and successful multipart abort/list/complete flows.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/service.go -->
# sources/object-store/minio/cmd/service.go

Purpose: This file defines service-level control signals and process control helpers used for restart, stop, reload/freezing operations, and global shutdown cancellation. It also implements the request-freeze mechanism used during synchronized boot.

Important APIs and types: `serviceSignal` enumerates `serviceRestart`, `serviceStop`, `serviceReloadDynamic`, `serviceFreeze`, and `serviceUnFreeze`. `globalServiceSignalCh` carries service commands. `GlobalContext` and `cancelGlobalContext` represent process-wide lifetime. `restartProcess` replaces or reruns the current process. `freezeServices` and `unfreezeServices` manage `globalServiceFreeze`, `globalServiceFreezeCnt`, and `globalServiceFreezeMu`.

Control flow: `restartProcess` on Windows starts a child process with the same args/env/stdio and exits only on success; on other systems it resolves the original executable with `exec.LookPath` and calls `syscall.Exec` with the same args/env, preserving PID where possible. `freezeServices` increments a counter and creates a channel on the first freeze. `unfreezeServices` decrements the counter and closes/swaps out the freeze channel when the count reaches zero.

State and persistence behavior: There is no persistence. Runtime state includes the process-wide context, service signal channel, and freeze counter/channel. `restartProcess` mutates process identity and exits/replaces the current process.

Dependencies and integration points: `signals.go` consumes `globalServiceSignalCh` and calls `restartProcess`. HTTP request handling elsewhere checks `globalServiceFreeze` to block S3 APIs during boot or administrative freeze. The file depends on Go `os/exec`, `syscall`, runtime OS checks, and MinIO's safe-close helper.

Risks: Freeze/unfreeze is reference-counted; unmatched calls can leave services frozen or prematurely unfreeze. Process restart behavior differs substantially between Windows and Unix. `GlobalContext` is package global and must be reset carefully in tests that simulate server lifecycles.

Test signals: No direct tests in this subset. Indirect signals include sync-boot freeze/unfreeze behavior during startup and signal/restart handling through `signals.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/setup-type.go -->
# sources/object-store/minio/cmd/setup-type.go

Purpose: This file defines the enum describing the server deployment/storage setup mode and maps it to MinIO mode strings for logging, startup behavior, and feature decisions.

Important APIs and types: `SetupType` is an `int` enum with `UnknownSetupType`, `FSSetupType`, `ErasureSDSetupType`, `ErasureSetupType`, and `DistErasureSetupType`. Its `String` method maps known values to `globalMinioModeFS`, `globalMinioModeErasureSD`, `globalMinioModeErasure`, or `globalMinioModeDistErasure`, falling back to `"unknown"`.

Control flow: The only logic is the switch in `String`. Other code, notably endpoint creation and `serverHandleCmdArgs`, sets global booleans from this enum.

State and persistence behavior: There is no mutable state or persistence. The enum value is runtime classification derived from command/config endpoints.

Dependencies and integration points: It is consumed by server startup, mode reporting, setup validation, and any code that branches on filesystem, single-drive erasure, local erasure, or distributed erasure behavior.

Risks: Adding a new setup type requires updating `String` and all global-mode branching. Unknown values degrade to `"unknown"`, which avoids panics but may hide unsupported state if not validated earlier.

Test signals: There are no direct tests here. Indirect signals come from server startup tests and mode-specific integration runs in `server_test.go`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/setup-type.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/sftp-server-driver.go -->
# sources/object-store/minio/cmd/sftp-server-driver.go

Purpose: This file adapts SFTP file operations to MinIO S3 operations. It implements the handlers required by `github.com/pkg/sftp` for reading, writing, listing, and file commands, using a MinIO client authenticated with credentials stored in SSH permissions.

Important APIs and types: `sftpDriver` holds SSH permissions, local S3 endpoint, and remote IP. `sftpMetrics` and `sftpTrace` publish FTP/SFTP trace events. `NewSFTPDriver` returns `sftp.Handlers`. `forwardForTransport` injects `X-Forwarded-For`. `getMinIOClient` builds a MinIO client from `AccessKey`, `SecretKey`, and optional `SessionToken`. `Fileread`, `Filewrite`, `Filecmd`, and `Filelist` implement SFTP behavior. `writerAt` adapts out-of-order SFTP writes to a sequential `io.Pipe` with a 100 MiB max forward offset. `listerAt` adapts slices of `os.FileInfo` to SFTP list pagination.

Control flow: Reads validate read flags, split the SFTP path into bucket/object, create a MinIO client, call `GetObject`, stat it, and return the object as `ReaderAt`. Writes validate flags and bucket existence, create a pipe, return a `writerAt`, and concurrently stream pipe data to `PutObject` with inferred content type, disabled SHA256 content hashing, and full-object CRC32C. File commands reject unsupported metadata/link/rename operations, map `Rmdir` to bucket removal or recursive object deletion, map `Remove` to `RemoveObject`, and map `Mkdir` to bucket creation or zero-byte directory marker creation. Listings map root to buckets, bucket/prefix to non-recursive `ListObjects`, and stat paths to bucket existence or object metadata, returning dummy directory info for missing keys to satisfy common SFTP list behavior.

State and persistence behavior: Persistent effects are S3 bucket creation/removal, object upload/removal, recursive prefix deletion, and directory marker object creation. Runtime state includes per-request MinIO clients, per-upload pipes/goroutines, buffered out-of-order write segments, and trace events. `writerAt.Close` fails if any queued segment was not flushed and waits for the upload goroutine.

Dependencies and integration points: It integrates SSH authentication output from `sftp-server.go`, MinIO client-go, global TLS and FTP client transport, S3 path helpers, `minioFileInfo`, tracing infrastructure, MIME database, and SFTP server handlers. It reuses S3 authorization because all operations go through MinIO's own S3 API with the authenticated user's credentials.

Risks: SFTP random writes are only supported by buffering forward segments up to 100 MiB; sparse or very out-of-order clients fail. Recursive prefix deletion via `Rmdir` can remove many objects and stops on the first remove error. `Stat` fabricates a directory for missing object keys, which is useful for clients but can obscure true absence. Each operation builds a MinIO client, which may be overhead. Errors from list goroutines can be dropped if list-object iteration exits early in the producer.

Test signals: Direct driver tests are not in this subset. SFTP authentication tests verify the credentials that feed this driver. Useful driver coverage would exercise read/write round trips, out-of-order writes, far-offset rejection, mkdir/remove/rmdir mappings, bucket root listings, prefix listings, and forwarded remote IP headers.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/sftp-server-driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/sftp-server.go -->
# sources/object-store/minio/cmd/sftp-server.go

Purpose: This file implements MinIO's SFTP server configuration and SSH authentication. It supports internal MinIO users/service accounts, LDAP users, LDAP-backed public key authentication, trusted user CA certificates, configurable SSH algorithms, and optional password-auth disabling.

Important APIs and types: Constants and slices define supported/preferred key exchange, public-key, cipher, and MAC algorithms. Errors describe SFTP auth failures. `globalSFTPTrustedCAPubkey` stores an optional trusted CA. `sshPubKeyAuth`, `sshPasswordAuth`, and `authenticateSSHConnection` are SSH callbacks. `processLDAPAuthentication` authenticates LDAP password/key users and creates temporary STS credentials. `validateClientKeyIsTrusted` verifies SSH certificates against the trusted CA. `sftpLogger` maps SFTP server logs into MinIO logging. `filterAlgos` validates configured algorithm lists. `startSFTPServer` parses `--sftp` args, loads keys, builds `ssh.ServerConfig`, and starts the SFTP listener.

Control flow: Authentication first checks username suffixes: `=ldap` forces LDAP, `=svc` forces internal service-account/user auth. Without suffix, LDAP is attempted first when enabled, then internal auth. Internal auth loads the IAM user, rejects temp credentials for password auth, either validates a trusted SSH certificate or compares the stored secret key in constant time, and returns SSH permissions containing MinIO credentials. LDAP auth accepts service-account password credentials when the username is a service account, otherwise binds or looks up LDAP, requires mapped policies, validates `sshPublicKey` attributes for key auth, creates temporary credentials with LDAP claims and expiry, stores them via IAM, and triggers site-replication IAM hooks. `startSFTPServer` validates key files and algorithm args, configures callbacks, and creates request servers using `NewSFTPDriver`.

State and persistence behavior: The file reads private key and optional trusted CA key files. It mutates `globalSFTPTrustedCAPubkey`. LDAP authentication persists temporary STS credentials in IAM state and replicates them through site replication. Auth returns credentials in SSH critical options, which are then used by the SFTP driver for S3 API calls.

Dependencies and integration points: It depends on MinIO IAM, LDAP config, policy DB, STS credential generation, site replication hooks, logger, pkg/sftp server, `golang.org/x/crypto/ssh`, and the SFTP driver. It is launched from `serverMain` when `globalServerCtxt.SFTP` has arguments.

Risks: Authentication behavior is suffix-sensitive and has fallback paths; operators need to understand `=ldap` and `=svc`. LDAP users without mapped policies are denied even if bind succeeds. Password auth compares against MinIO secret keys, so disabling password auth is important for key-only deployments. Trusted CA mode requires SSH certificates with principals; raw keys are rejected. `filterAlgos` calls `logger.Fatal` on invalid input, making bad flags fatal at startup.

Test signals: `sftp-server_test.go` covers service account login/failure, LDAP missing policy/invalid user/invalid password, forced service-account failure on LDAP users, LDAP password success, LDAP public-key success, invalid key failure, and missing public-key failure.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/sftp-server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/sftp-server_test.go -->
# sources/object-store/minio/cmd/sftp-server_test.go

Purpose: This file tests SFTP authentication behavior for MinIO internal users/service accounts and LDAP users. It verifies password and public-key paths, policy requirements, suffix behavior, and failure cases.

Important APIs and types: `MockConnMeta` implements `ssh.ConnMetadata` with a configurable username. `newSSHConnMock` constructs metadata. `TestSFTPAuthentication` runs the IAM test suites. Suite methods call `sshPasswordAuth` and `sshPubKeyAuth`, use admin APIs to create users/policies, and read public keys from `testdata`.

Control flow: The top-level test starts each IAM suite, runs service-account success and invalid-password checks, then skips LDAP cases unless `EnvTestLDAPServer` is set. When LDAP is available it configures LDAP, verifies missing policy and invalid user failures, verifies forced service-account suffix failure for an LDAP user, verifies invalid password failure, attaches LDAP policies and verifies password login for two users, then tests LDAP public-key success, invalid key failure, and no-public-key failure.

State and persistence behavior: Tests create IAM users, attach policies, add canned policies, attach LDAP policies, and rely on LDAP-backed identities. LDAP successful auth creates temporary credentials through the production auth path. Temporary server state is torn down by suite teardown.

Dependencies and integration points: The tests integrate the MinIO admin client, IAM test harness, optional external LDAP test server, SSH public key parsing, SFTP auth callbacks, and LDAP policy mapping. They do not start a full SFTP listener or exercise the SFTP driver.

Risks: LDAP coverage is environment-gated and skipped unless a test LDAP server is configured. Tests depend on fixed LDAP fixture users such as `dillon` and `fahim` and fixed key files. The non-LDAP portion primarily tests service-account password logic.

Test signals: Expected signals are successful service-account auth with and without `=svc`, `errAuthentication` for wrong service-account passwords, LDAP missing-policy errors, `errNoSuchUser` for invalid/fallback users, successful LDAP password auth after policy attachment, successful LDAP public-key auth for a user with `sshPublicKey`, `errAuthentication` for mismatched keys, and failure for users lacking an SSH public-key attribute.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/sftp-server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/shared-lock.go -->
# sources/object-store/minio/cmd/shared-lock.go

Purpose: This file provides a shared namespace-lock helper that continuously acquires an object-layer lock and hands out derived contexts to consumers. It is used when multiple operations need to share a long-lived cluster lock while still respecting caller cancellation and lock-loss events.

Important APIs and types: `sharedLockTimeout` configures dynamic lock acquisition timeout/retry behavior. `sharedLock` wraps a channel of `LockContext`. `backgroundRoutine` acquires and refreshes the lock. `mergeContext` combines a lock context and caller context. `GetLock` returns a merged context/cancel function. `newSharedLock` starts the background routine.

Control flow: The background goroutine repeatedly creates a namespace lock on `minioMetaBucket` and the provided lock name, attempts `GetLock`, and on success enters a loop sending the same `LockContext` to consumers until the parent context is canceled or the lock context is canceled. If the lock is lost, it breaks out and reacquires. `GetLock` receives a lock context from the channel and returns a context canceled when either the lock is lost, caller context is done, or the returned cancel is called.

State and persistence behavior: No durable state is written. Runtime state is the held namespace lock and the unbuffered channel used to distribute lock contexts. Lock persistence/quorum behavior is delegated to the object layer's namespace lock implementation.

Dependencies and integration points: It depends on `ObjectLayer.NewNSLock`, MinIO metadata bucket naming, `LockContext`, and dynamic timeout support. It is a concurrency primitive for code that needs shared access to a cluster-wide lock.

Risks: `GetLock` blocks until the background routine acquires and sends a lock; if the object layer cannot acquire the lock and caller context is already canceled, `GetLock` still waits because it does not select on caller cancellation before receiving. Consumers must call the returned cancel to release merge goroutines. Lock-loss cancellation must be handled by callers.

Test signals: There are no direct tests here. Useful tests would cover acquisition, caller cancellation, lock-context cancellation, reacquisition after lock loss, and blocked acquisition behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/shared-lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signals.go -->
# sources/object-store/minio/cmd/signals.go

Purpose: This file handles OS, HTTP-server, and service-control signals for graceful shutdown and restart. It coordinates shutting down heal state, global context, HTTP server, object layer, Console, event targets, profilers, log output, and systemd status notifications.

Important APIs and types: `shutdownHealMRFWithTimeout` bounds MRF heal shutdown to one minute. `handleSignals` runs the signal loop and defines local `exit` and `stopProcess` helpers. It consumes `globalHTTPServerErrorCh`, `globalOSSignalCh`, and `globalServiceSignalCh`, and handles `serviceRestart` and `serviceStop`.

Control flow: On HTTP server error, the handler logs it, stops the process, and exits with success/failure based on shutdown result. On OS interrupt/TERM/QUIT, it logs the signal, notifies systemd stopping, stops the process, and exits. On service restart, it notifies reloading, stops the process, calls `restartProcess`, conditionally notifies ready, logs restart errors, and exits based on combined stop/restart success. On service stop, it notifies stopping and exits after shutdown. `stopProcess` first shuts down heal MRF, cancels `GlobalContext`, shuts down HTTP server, object layer, Console, and event targets.

State and persistence behavior: The code closes global log output, stops active profilers, cancels global runtime context, shuts down runtime services, removes notification targets, and exits the process. There is no durable state except whatever subsystem shutdowns flush.

Dependencies and integration points: It integrates with `service.go`, systemd daemon notifications, HTTP server abstraction, object layer shutdown, Console server, event notifier, profiler registry, logger, and heal MRF state. `serverMain` starts this goroutine after registering OS signals.

Risks: `exit` calls `os.Exit`, so deferred cleanup in other goroutines will not run. Shutdown order is important: MRF shutdown happens before S3 operation cancellation. The one-minute MRF timeout prevents indefinite waits but can leave work unfinished. Service reload/freeze signals are enumerated elsewhere but not handled in this switch. Any nil/global function assumptions must hold during partial startup failures.

Test signals: No direct tests are present. Indirect signals are clean test-server teardown paths and operational behavior during SIGTERM, service stop, and restart.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signals.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v2.go -->
# sources/object-store/minio/cmd/signature-v2.go

Purpose: This file implements AWS S3 Signature Version 2 validation and signing helpers for header-authenticated requests, presigned URLs, and browser POST policies. It canonicalizes x-amz headers and selected subresources, computes HMAC-SHA1 signatures, and maps malformed/authentication cases to MinIO S3 API errors.

Important APIs and types: `resourceList` is the sorted whitelist of query resources included in V2 canonical resources. `signV2Algorithm` is `"AWS"`. `doesPolicySignatureV2Match`, `doesPresignV2SignatureMatch`, `getReqAccessKeyV2`, `validateV2AuthHeader`, and `doesSignV2Match` are validation entry points. `calculateSignatureV2`, `preSignatureV2`, and `signatureV2` compute signatures. `compareSignatureV2` compares base64-decoded signatures in constant time. `canonicalizedAmzHeadersV2`, `canonicalizedResourceV2`, and `getStringToSignV2` build canonical signing inputs.

Control flow: Presigned validation splits `RequestURI`, unescapes query parameters, extracts access key/signature/expires, filters remaining queries, validates credentials, parses expiry, rejects expired URLs, resolves the canonical resource with virtual-host/domain support, computes the expected presign signature, compares it, and removes `Expires` from `r.Form`. Header validation checks the `Authorization` header prefix and access-key fields. Signed request validation parses raw URI/query, unescapes queries, resolves resource, ensures the auth prefix matches the credential access key, computes expected signature from method/resource/query/headers, and compares. Policy validation checks credential validity and compares the form policy signature.

State and persistence behavior: The code does not persist state. It reads request headers, URL/query data, global domain names, and credentials from IAM/auth validation. It mutates `r.Form` by deleting `Expires` after successful presign validation.

Dependencies and integration points: It integrates with MinIO's auth credential validation (`checkKeyValid`), S3 error codes, request resource parsing, domain-name support, and HTTP constants. It supports legacy V2 clients and is exercised by server tests when the suite signer is `signerV2`.

Risks: Signature V2 is legacy and sensitive to canonicalization details. `resourceList` must remain sorted and complete for supported subresources. Query unescaping and string joining must match client behavior for encoded values. `compareSignatureV2` rejects non-canonical base64 strings that cannot decode. Header canonicalization joins multiple values with commas but does not trim/fold whitespace beyond Go header normalization.

Test signals: `signature-v2_test.go` verifies resource-list sorting, presigned URL error cases and successful signatures, auth-header validation error mapping, and POST policy signature matching. `server_test.go` also runs the full S3 suite with signer V2 for ErasureSD.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v2_test.go -->
# sources/object-store/minio/cmd/signature-v2_test.go

Purpose: This file tests Signature V2 canonical resource ordering, presigned URL validation, Authorization header validation, and POST policy signature validation.

Important APIs and types: Tests cover `resourceList`, `doesPresignV2SignatureMatch`, `preSignV2` test helper, `validateV2AuthHeader`, `doesPolicySignatureV2Match`, and `calculateSignatureV2`. Setup uses `prepareFS`, `newTestConfig`, and global active credentials.

Control flow: `TestResourceListSorting` copies and sorts `resourceList` and asserts the original is already sorted. `TestDoesPresignedV2SignatureMatch` initializes test config, builds requests with missing/invalid/expired/bad-signature query parameters, and for success cases signs the request with `preSignV2` before validation. `TestValidateV2AuthHeader` table-tests empty, wrong prefix, missing fields, bad access key, and valid access key headers. `TestDoesPolicySignatureV2Match` table-tests invalid access key, wrong signature, and correct signature for a simple policy string.

State and persistence behavior: The tests create a temporary filesystem object layer and global test config so credential validation works. No durable state beyond temp directories is kept.

Dependencies and integration points: These tests use auth/config setup helpers, URL encoding, global credentials, and S3 API error codes. They isolate Signature V2 logic from full HTTP server tests.

Risks: The presign success cases depend on `preSignV2` helper behavior matching production validation; shared helper bugs could reduce independence. Time-based expiry uses `UTCNow()` and short future offsets, but it is deterministic enough for unit tests. The tests do not exhaustively cover canonicalized x-amz headers or every subresource.

Test signals: Expected error codes include `ErrInvalidQueryParams`, `ErrInvalidAccessKeyID`, `ErrMalformedExpires`, `ErrExpiredPresignRequest`, `ErrSignatureDoesNotMatch`, `ErrAuthHeaderEmpty`, `ErrSignatureVersionNotSupported`, `ErrMissingFields`, and `ErrNone`; the policy test verifies correct HMAC-SHA1/base64 matching.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/signature-v2_test.go -->
