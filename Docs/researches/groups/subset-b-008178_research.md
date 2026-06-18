# subset-b-008178 grouped research

Work item: `subset-b-008178`

This grouped report covers the requested MinIO Client command files. Each source file has a separately delimited section so reconciliation can split this report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/suite_test.go -->
# sources/object-store/minio-mc/cmd/suite_test.go

Purpose: this file is a gated full integration test suite for `mc`, enabled only when `MC_TEST_RUN_FULL_SUITE=true`. It builds or locates the `mc` binary, configures an alias against a MinIO endpoint, creates temporary local files and buckets, then exercises a broad set of end-user commands: alias, admin user, share upload/download, cp/cat/pipe/mirror/rm/stat/ls/du/find, bucket error cases, and server-side encryption modes.

Important APIs/types/functions: `Test_FullSuite` is the orchestrator; `initializeTestSuite`, `preflightCheck`, `preRunCleanup`, and `postRunCleanup` own environment setup and teardown. `newTestFile` and `testFile` model generated local files plus observed MinIO object metadata. Helpers such as `RunMC`, `RunCommand`, JSON parsers, `CreateBucket`, `createFile`, `openFileAndGetMd5Sum`, and fatal wrappers provide the test harness. Encryption coverage is split across SSE-C, SSE-KMS, and SSE-S3 helpers.

Control flow: setup reads many `MC_TEST_*` variables, optionally builds `../mc`, fills deterministic/random file fixtures, configures global CLI flags, registers users, and creates two buckets. The dependent lane uploads fixtures, captures `ls`/`stat` outputs into `fileMap`, validates metadata, then tests pipe, mirror, tag preservation, find filters, and downloads. Optional branches run HTTPS-only SSE-C tests, KMS-only tests, SSE-S3 tests, and KMS-to-SSE-C copy tests.

State and persistence: the suite mutates real MinIO state by creating buckets, users, policies, objects, tags, metadata, and encryption-protected objects. It writes temporary local files under `tempDir`, may build `../mc`, stores bucket/user names in package-level maps/slices, and deletes buckets/users/temp files at cleanup.

Dependencies and integration points: it shells out to `go build`, `curl`, and the generated `mc` binary, and depends on a reachable MinIO server, configured credentials, optional HTTPS/KMS/SSE-S3 support, and JSON output schemas from many command implementations in the same package.

Risks and test signals: because tests share global mutable state and depend on external services, order matters and failures can cascade. The suite is valuable as an end-to-end regression signal for CLI compatibility, JSON contracts, object metadata, encryption flags, and cleanup behavior, but it is unsuitable for normal fast unit-test lanes without the environment gate.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-callhome.go -->
# sources/object-store/minio-mc/cmd/support-callhome.go

Purpose: implements `mc support callhome enable|disable|status ALIAS`, a support subcommand that manages MinIO server callhome configuration.

Important APIs/types/functions: `supportCallhomeCmd` defines the CLI; `supportCallhomeMessage` renders text and JSON output; `isDiagCallhomeEnabled`, `mainCallhome`, `printCallhomeStatus`, `toggleCallhome`, and `setCallhomeConfig` implement status and mutation.

Control flow: `mainCallhome` initializes license/support colors, validates the two-argument toggle syntax through shared support helpers, and requires cluster registration for non-development operation. `status` reads the server config via `isFeatureEnabled`; `enable` and `disable` call `setCallhomeConfig`, which creates an admin client, checks subsystem support, and writes `callhome enable=on|off`.

State and persistence: persistent state is stored in the remote MinIO server config through `madmin.AdminClient.SetConfigKV`. The command itself only emits output.

Dependencies and integration points: depends on shared support registration checks, MinIO admin config APIs, `madmin.Default`, `minioConfigSupportsSubSys`, and global JSON/text output plumbing.

Risks and test signals: risks include server-version compatibility and permission/configuration failures. Useful tests should cover invalid toggle args, unsupported subsystem handling, JSON output, and status behavior when the `enable` key is absent or explicitly off.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-callhome.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-diag-spinner-v3.go -->
# sources/object-store/minio-mc/cmd/support-diag-spinner-v3.go

Purpose: provides progress spinner handling for the current `madmin.HealthInfo` diagnostics stream used by support diagnostics.

Important APIs/types/functions: `receiveHealthInfo` is the only exported-to-package function. It decodes a JSON stream of `madmin.HealthInfo`, tracks expected health sections, and updates `mpb` spinner bars as each section arrives.

Control flow: the function creates an `mpb.Progress` with a wait group, defines a small `progressSpinner` struct, registers section predicates for CPU, disk, net, OS, memory, process, server config, system errors/services/config, and admin info, then decodes the response in a goroutine. Each decoded health frame updates the accumulated `info`; when a predicate is satisfied or the final admin server list is observed, the corresponding spinner is marked complete. `pg.Wait()` blocks until all spinners finish.

State and persistence: all state is in memory: accumulated health info, wait group, progress bars, and decode error. No disk or server state is changed.

Dependencies and integration points: used by `fetchServerDiagInfo` for `madmin.HealthInfoVersion`. It depends on `colorjson.Decoder`, `madmin.HealthInfo`, `mpb`, and shared console color helpers from the diagnostics file.

Risks and test signals: if a stream ends before any condition satisfies and no final server info is sent, the wait group can block. Tests should simulate complete, EOF, and partial streams, especially ensuring EOF clears the error and all expected bars complete for final frames.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-diag-spinner-v3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-diag.go -->
# sources/object-store/minio-mc/cmd/support-diag.go

Purpose: implements `mc support diag` / `diagnostics`, collecting MinIO health data, optionally saving it for airgapped use, and otherwise uploading it to SUBNET.

Important APIs/types/functions: `supportDiagCmd`, `supportDiagFlags`, `supportDiagMessage`, `checkSupportDiagSyntax`, `execSupportDiag`, `fetchServerDiagInfo`, `TarGZHealthInfo`, `tarGZ`, `HealthDataTypeSlice`, and `HealthDataTypeFlag` define CLI behavior, serialization, server collection, and custom flag parsing. Constants define anonymization modes.

Control flow: `mainSupportDiag` validates one target and anonymization mode, initializes SUBNET connectivity, enforces registration when needed, builds an admin client, and calls `execSupportDiag`. Non-airgapped mode pre-fetches upload URL/headers before collection. `fetchServerDiagInfo` resolves requested health sections, starts progress spinners for non-JSON output, calls `ServerHealthInfo`, then decodes version-specific streaming health formats. Version 0 is mapped to V1 after fetching `ServerInfo`; version 2 decodes `HealthInfoV2`; current version delegates to `receiveHealthInfo`. Results are gzip-compressed as JSON header plus health payload, saved locally, and uploaded unless airgapped.

State and persistence: writes a `<alias>-health_<timestamp>.json.gz` report locally. In non-airgapped mode, `SubnetFileUploader` deletes the file after successful upload. It does not mutate server config.

Dependencies and integration points: integrates with MinIO admin health APIs, SUBNET upload helpers, support registration, global JSON/airgap flags, colorized console output, and `madmin.HealthDataTypesMap/List`.

Risks and test signals: streaming decode and spinner cancellation are sensitive to partial responses and deadlines. Tests should cover invalid anonymization, custom health type parsing, airgapped JSON behavior, upload failure, gzip contents, and old health-version conversion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-diag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-inspect.go -->
# sources/object-store/minio-mc/cmd/support-inspect.go

Purpose: implements `mc support inspect`, which downloads raw object/metadata inspection data from MinIO, optionally encrypts it with a public key, and either uploads it to SUBNET or saves it for airgapped/manual sharing.

Important APIs/types/functions: `supportInspectCmd`, `supportInspectFlags`, `inspectMessage`, `mainSupportInspect`, and `saveInspectDataFile` define CLI, output, admin-client interaction, stream validation, upload, and local persistence.

Control flow: the command validates a single target, initializes SUBNET connectivity and registration, creates an admin client, parses alias/bucket/prefix, warns when shell wildcard support is likely missing, loads `support_public.pem` from the mc config directory or falls back to `defaultPublicKey`, then calls `client.Inspect`. If the server did not return an encryption key, the response is piped through `estream.NewReader` to validate stream structure while simultaneously writing to a temp file. Airgapped mode moves the temp file to a stable inspect filename. Online mode uploads with `SubnetFileUploader`; if upload fails, it saves locally instead.

State and persistence: writes temporary `mc-inspect-*` files, final `inspect-...enc` or `inspect-data.<crc>.enc` files, and rotates an existing final file with a timestamp suffix. The returned decryption key is printed only once for locally saved encrypted data.

Dependencies and integration points: depends on MinIO admin inspect API, `madmin.InspectOptions`, `madmin-go/estream`, SUBNET upload helpers, config-dir helpers, shell detection, and shared `moveFile` from support profile code.

Risks and test signals: sensitive-data handling and one-time key display are critical. Tests should cover public key override, legacy mode, stream validation failures, upload fallback, existing-file rotation, wildcard shell warnings, and airgapped output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-client.go -->
# sources/object-store/minio-mc/cmd/support-perf-client.go

Purpose: runs the client-to-server performance test used by `mc support perf client` and by the default support performance bundle.

Important APIs/types/functions: `mainAdminSpeedTestClientPerf` creates an admin client, parses the hidden `duration` flag, calls `AdminClient.ClientPerf`, and emits `PerfTestResult` messages.

Control flow: after duration validation, a goroutine calls `client.ClientPerf` and sends either an error or `madmin.ClientPerfResult`. In JSON mode, the first result/error is converted to `PerfTestOutput` and printed. In interactive mode, a Bubble Tea speed-test UI is started; a second goroutine sends periodic empty progress messages every 100 ms until the final result/error arrives, then forwards the final `PerfTestResult` to the UI and optional aggregation channel.

State and persistence: no local persistence. Results may be accumulated by `support-perf.go` and later zipped/uploaded.

Dependencies and integration points: depends on admin client construction, `madmin.ClientPerf`, `PerfTestResult`, `ClientPerfTest`, `convertPerfResult`, and `initSpeedTestUI` from nearby perf UI code.

Risks and test signals: unbuffered channel sequencing and closed error/result channels can produce zero-value results if not carefully handled. Tests should validate duration errors, JSON error output, final-result forwarding to `outCh`, and UI progress behavior under delayed server responses.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-drive.go -->
# sources/object-store/minio-mc/cmd/support-perf-drive.go

Purpose: runs server-side drive speed tests for `mc support perf drive`.

Important APIs/types/functions: `mainAdminSpeedTestDrive` parses `blocksize`, `filesize`, and `serial`, calls `AdminClient.DriveSpeedtest`, and emits typed `PerfTestResult` values containing `[]madmin.DriveSpeedTestResult`.

Control flow: the command validates positive byte sizes, invokes the admin API with `madmin.DriveSpeedTestOpts`, then branches on global JSON mode. JSON mode drains versioned results from the result channel and prints converted output. Interactive mode starts the shared speed-test Bubble Tea UI, forwards progress events when result frames lack `Version`, accumulates final versioned drive results, sends a final message, and optionally writes to `outCh`.

State and persistence: no direct persistence; final results can be bundled by the parent support perf command.

Dependencies and integration points: depends on `go-humanize` parsing, MinIO admin drive speedtest, shared perf conversion types, and speed-test UI messaging.

Risks and test signals: size parsing, zero/negative validation, API errors before channel creation, and result frames without `Version` are important edge cases. Tests should check JSON output for API errors and that all versioned drive endpoint results survive conversion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-drive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-net.go -->
# sources/object-store/minio-mc/cmd/support-perf-net.go

Purpose: runs MinIO network throughput tests for `mc support perf net`.

Important APIs/types/functions: `mainAdminSpeedTestNetperf` parses a duration, calls `AdminClient.Netperf`, and converts `madmin.NetperfResult` into support performance output.

Control flow: the function builds an admin client, creates a cancellable context, validates positive duration, and starts a goroutine that calls `client.Netperf`. JSON mode selects the first error or result and prints converted `PerfTestOutput`. Interactive mode starts the shared speed-test UI and sends empty progress updates until a final result/error arrives, then forwards the final `PerfTestResult` to the UI and optional parent channel.

State and persistence: no direct persistence; parent `support-perf.go` may archive/upload the result.

Dependencies and integration points: depends on MinIO admin network perf API, `PerfTestResult`, `NetPerfTest`, conversion functions, and Bubble Tea UI.

Risks and test signals: select behavior with closed channels and long-running server calls are the main control-flow risks. Tests should cover invalid duration, admin API error, JSON result conversion, and interactive finalization.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-net.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-object.go -->
# sources/object-store/minio-mc/cmd/support-perf-object.go

Purpose: runs object PUT/GET performance tests for `mc support perf object` and keeps the hidden legacy `admin speedtest` command deprecated.

Important APIs/types/functions: `adminSpeedtestCmd`, `mainAdminSpeedtest`, and `mainAdminSpeedTestObject`. The object test parses `duration`, `size`, `concurrent`, `bucket`, `noclear`, and `verbose`, then calls `AdminClient.Speedtest`.

Control flow: the legacy admin command only reports deprecation. The support path validates positive duration, object size, and concurrency. It enables autotuning unless the `concurrent` flag was explicitly set, then starts `client.Speedtest` with `madmin.SpeedtestOpts`. JSON mode drains the stream and prints the last versioned result. Interactive mode starts the speed-test UI, forwards every stream result as progress, and finally sends the last result as final.

State and persistence: the server-side speed test may create and clear objects in a bucket, controlled by hidden `bucket` and `noclear` flags. The client itself only forwards results.

Dependencies and integration points: uses MinIO admin speedtest, shared perf conversion/output, `go-humanize` byte parsing, and the speed-test UI.

Risks and test signals: autotune behavior depends on `ctx.IsSet("concurrent")`; hidden bucket/noclear flags can leave server artifacts. Tests should cover parse failures, concurrency validation, JSON final result selection, and error conversion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-site-replication.go -->
# sources/object-store/minio-mc/cmd/support-perf-site-replication.go

Purpose: runs site-replication network performance tests for `mc support perf site-replication`.

Important APIs/types/functions: `mainAdminSpeedTestSiteReplication` validates duration, calls `AdminClient.SiteReplicationPerf`, and converts `madmin.SiteNetPerfResult` into the support perf result model.

Control flow: after admin-client setup and positive duration validation, a goroutine invokes the admin API and sends one result or error. JSON mode prints the selected result/error directly. Interactive mode starts the shared speed-test UI and periodically sends empty site-replication result messages until completion, then forwards the final message to the UI and optional parent channel.

State and persistence: no direct local persistence. Results become part of the parent performance archive when run through `support perf`.

Dependencies and integration points: integrates with MinIO admin site-replication perf, shared `PerfTestResult` type constants, conversion helpers in `support-perf.go`, and Bubble Tea speed-test UI.

Risks and test signals: meaningful output requires a site-replication topology and server support. Tests should cover unsupported server errors, duration parsing, JSON conversion of per-node TX/RX durations and connection counts, and UI finalization.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf-site-replication.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf.go -->
# sources/object-store/minio-mc/cmd/support-perf.go

Purpose: defines `mc support perf`, aggregates object/network/drive/client/site-replication performance results, renders JSON, and packages/upload results to SUBNET.

Important APIs/types/functions: `supportPerfCmd`, `supportPerfFlags`, `PerfTestOutput`, all result DTOs (`ObjTestResults`, `NetTestResults`, `DriveTestResults`, `ClientResult`, `SiteReplicationTestResults`), conversion helpers, `mainSupportPerf`, `execSupportPerf`, `runPerfTests`, `zipPerfResult`, and `savePerfResultFile`.

Control flow: `mainSupportPerf` accepts either `TARGET` for default tests or `TYPE TARGET` for a specific test. `execSupportPerf` initializes SUBNET connectivity/registration, runs requested tests, skips file upload for global JSON mode, then writes a JSON result plus `cluster.info` into a temporary zip. Airgapped mode moves it to `<alias>-perf_<timestamp>.zip`; online mode uploads to SUBNET and falls back to local save on upload failure. `runPerfTests` dispatches to per-test functions sequentially and collects one result per test.

State and persistence: writes temporary `mc-perf-*.zip`; final local zip is preserved in airgapped or upload-failure cases. Object speed tests may mutate server buckets through hidden flags; packaging includes cluster registration info.

Dependencies and integration points: depends on SUBNET upload helpers, MinIO admin perf APIs via sibling files, `madmin` result structs, JSON/zip standard libraries, and global output flags.

Risks and test signals: the parent waits on `resultCh` after each interactive test, so child functions must always send a final result. Tests should cover type dispatch, default test order, conversion correctness, zip contents, upload fallback, and JSON-mode no-upload behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-perf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-profile.go -->
# sources/object-store/minio-mc/cmd/support-profile.go

Purpose: implements `mc support profile`, collecting MinIO server profiling data and uploading it to SUBNET or saving it locally.

Important APIs/types/functions: `profileFlags`, `supportProfileMessage`, `supportProfileCmd`, `checkAdminProfileSyntax`, `moveFile`, `saveProfileFile`, `mainSupportProfile`, and `execSupportProfile`.

Control flow: syntax validation enforces one target, duration >= 1 second, and profiler types from the `madmin.Profiler*` set. The command initializes SUBNET connectivity and registration, creates an admin client, optionally precomputes upload URL/headers, calls `client.Profile`, saves the returned zip stream to `profile.zip`, then uploads it unless airgapped. Upload failure is reported as an error status while retaining the local file.

State and persistence: writes a temporary profile file, rotates existing `profile.zip` to `profile.zip.<timestamp>`, and moves the new data into `profile.zip`. `moveFile` copies then removes to work across filesystems.

Dependencies and integration points: depends on MinIO admin profiling API, SUBNET upload helpers, shared registration/airgap/global JSON handling, and console message plumbing.

Risks and test signals: profile files may contain sensitive operational data. Tests should cover profiler validation, duration validation, cross-device move fallback, existing-file rotation, upload failure output, and airgapped persistence.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-remove.go -->
# sources/object-store/minio-mc/cmd/support-proxy-remove.go

Purpose: implements `mc support proxy remove TARGET`, deleting the configured SUBNET proxy from a MinIO cluster.

Important APIs/types/functions: `supportProxyRemoveCmd`, `supportProxyRemoveMessage`, `checkSupportProxyRemoveSyntax`, and `mainSupportProxyRemove`.

Control flow: the command validates exactly one argument, sets success color, extracts the alias, requires registration, creates an admin client via `getClient`, calls `DelConfigKV(globalContext, "subnet proxy")`, and prints a success message.

State and persistence: persistent mutation is remote server config deletion for the `subnet proxy` key. No local state is written.

Dependencies and integration points: part of `support proxy`; uses shared support registration and output helpers plus MinIO admin config deletion.

Risks and test signals: behavior depends on server support for the subnet config subsystem and caller permissions. Tests should cover argument count, successful JSON/text output, and delete failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-set.go -->
# sources/object-store/minio-mc/cmd/support-proxy-set.go

Purpose: implements `mc support proxy set TARGET PROXY_URL`, storing a SUBNET proxy URL in MinIO server config.

Important APIs/types/functions: `supportProxySetCmd`, `supportProxySetMessage`, `checkSupportProxySetSyntax`, and `mainSupportProxySet`.

Control flow: after two-argument validation and registration enforcement, it builds an admin client, rejects an empty proxy string, parses the URL with `net/url.Parse`, writes `subnet proxy=<proxy>` via `SetConfigKV`, and prints a success message.

State and persistence: persists the proxy setting in remote MinIO server config. No local files are modified.

Dependencies and integration points: integrated under `support proxy`; depends on shared output/color helpers, `url2Alias`, `getClient`, and admin config APIs.

Risks and test signals: `url.Parse` alone accepts some strings without scheme/host, so validation may be looser than expected. Tests should cover empty proxy, malformed or scheme-less strings, config write errors, JSON output, and registration requirements.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-show.go -->
# sources/object-store/minio-mc/cmd/support-proxy-show.go

Purpose: implements `mc support proxy show TARGET`, retrieving the configured SUBNET proxy from MinIO.

Important APIs/types/functions: `supportProxyShowCmd`, `supportProxyShowMessage`, `checkSupportProxyShowSyntax`, and `mainSupportProxyShow`.

Control flow: validates one argument, sets success color, extracts alias, requires registration, calls `getKeyFromSubnetConfig(alias, "proxy")`, errors when the server does not support proxy configuration, and prints either the proxy value or "Proxy is not configured".

State and persistence: read-only; no local or remote mutation.

Dependencies and integration points: part of the support proxy command group; depends on MinIO config access through shared `getKeyFromSubnetConfig` and global JSON/text output.

Risks and test signals: output semantics distinguish unsupported config from supported-but-empty config. Tests should cover both cases, JSON status fields, missing argument handling, and registration failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy-show.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy.go -->
# sources/object-store/minio-mc/cmd/support-proxy.go

Purpose: defines the `mc support proxy` command namespace and wires its subcommands.

Important APIs/types/functions: `supportProxySubcommands`, `supportProxyCmd`, and `mainSupportProxy`.

Control flow: the command registers `set`, `remove`, and `show` subcommands with support/global flags. If invoked without a valid subcommand, `mainSupportProxy` delegates to `commandNotFound`.

State and persistence: no state changes in this file; stateful behavior lives in subcommand files.

Dependencies and integration points: integrates with the top-level `supportSubcommands` list in `support.go` and uses the MinIO CLI framework.

Risks and test signals: low logic risk, but command registration is user-facing. Tests should confirm the subcommand list is reachable, help text is correct, and invalid subcommands produce standard command-not-found behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-register.go -->
# sources/object-store/minio-mc/cmd/support-register.go

Purpose: preserves the old `mc support register` command as a deprecated wrapper pointing users to `mc license register`.

Important APIs/types/functions: `supportRegisterFlags`, `supportRegisterCmd`, and `mainSupportRegister`.

Control flow: the command definition still exposes the old name and flags/template, but its action immediately calls `deprecatedError("mc license register")`.

State and persistence: no state is read or written by this deprecated path.

Dependencies and integration points: remains listed under `supportSubcommands` for compatibility and uses shared `subnetCommonFlags`.

Risks and test signals: compatibility risk is in preserving the command while clearly directing users to the replacement. Tests should assert invocation fails or exits with the expected deprecation messaging and does not attempt registration side effects.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-api.go -->
# sources/object-store/minio-mc/cmd/support-top-api.go

Purpose: implements `mc support top api`, a real-time terminal summary of in-flight/API trace events.

Important APIs/types/functions: `supportTopAPIFlags`, `supportTopAPICmd`, `checkSupportTopAPISyntax`, and `mainSupportTopAPI`.

Control flow: after one-target validation and registration check, the command creates an admin client, builds trace options with `tracingOpts`, builds filters with `matchingOpts`, starts `client.ServiceTrace`, and forwards matching `madmin.ServiceTraceInfo` values into a buffered channel consumed by `initTraceStatsUI(false, 30, filteredTraces)`. Trace errors kill the UI and are reported after `Run`.

State and persistence: read-only streaming command; no persistent state.

Dependencies and integration points: depends on trace filtering helpers from the broader trace command implementation, MinIO admin service tracing, Bubble Tea UI in `trace-stats-ui.go`, and support registration.

Risks and test signals: long-lived goroutines and error propagation via captured `te` are sensitive to races. Tests should cover filter option construction, trace error handling, UI channel forwarding, and graceful cancellation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-drive.go -->
# sources/object-store/minio-mc/cmd/support-top-drive.go

Purpose: implements `mc support top drive`, showing real-time per-drive IO metrics.

Important APIs/types/functions: `supportTopDriveFlags`, `supportTopDriveCmd`, `checkSupportTopDriveSyntax`, and `mainSupportTopDrive`.

Control flow: the command validates one target, enforces registration, builds an admin client, fetches `ServerInfo` to obtain disk metadata, then starts a Bubble Tea UI from `initTopDriveUI`. A goroutine calls `client.Metrics` with `madmin.MetricsDisk`, one-second interval, `ByDisk=true`, and count `N`; each disk metric is sent as `topDriveResult` to the UI.

State and persistence: read-only; maintains transient previous/current IO counters in the UI.

Dependencies and integration points: integrates with MinIO realtime metrics API, `top-drives-spinner.go` UI code, and support registration.

Risks and test signals: correctness depends on matching disk endpoint keys from `ServerInfo` and metrics. Tests should cover invalid count behavior, server-info failures, metric callback mapping, and UI rate calculations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-drive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-locks.go -->
# sources/object-store/minio-mc/cmd/support-top-locks.go

Purpose: implements `mc support top locks`, listing active or stale MinIO locks.

Important APIs/types/functions: `supportTopLocksCmd`, `supportTopLocksFlag`, `lockMessage`, `checkSupportTopLocksSyntax`, `mainSupportTopLocks`, `printHeaders`, and `printLocks`.

Control flow: validates one target, enforces registration, sets colors, creates an admin client, calls `TopLocksWithOpts` with hidden `count` and `stale` flags, then prints a table header and each lock message unless JSON output is active. `lockMessage.String` computes elapsed time, detects stale locks by comparing quorum to server list length, and renders a fixed-width row.

State and persistence: read-only command; no local or remote mutation.

Dependencies and integration points: depends on MinIO admin lock API, humanized time formatting, pretty-table utilities in the cmd package, support registration, and global JSON mode.

Risks and test signals: old servers may return zero elapsed, so fallback uses timestamp. Tests should cover stale detection, JSON fields, count/stale option propagation, and table formatting for long resources.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-locks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-net.go -->
# sources/object-store/minio-mc/cmd/support-top-net.go

Purpose: implements `mc support top net`, a real-time view of network metrics per host/interface.

Important APIs/types/functions: `supportTopNetFlags`, `supportTopNetCmd`, `checkSupportTopNetSyntax`, and `mainSupportTopNet`.

Control flow: after syntax and registration checks, the command creates an admin client and constructs `madmin.MetricsOptions` with `MetricNet`, configurable interval/count, and `ByHost=true`. JSON mode prints every `RealtimeMetrics` callback as `metricsMessage`. Interactive mode starts `initTopNetUI`, maps each host's `Net` metrics into `topNetResult`, forwards first host errors if present, and quits when the metrics call ends.

State and persistence: read-only; UI keeps previous/current samples to compute rates.

Dependencies and integration points: depends on MinIO realtime metrics API, `top-net-spinner.go`, shared metrics JSON message type, support registration, and global JSON mode.

Risks and test signals: interval values are not explicitly validated for positivity. Tests should cover JSON streaming, context cancellation, host error forwarding, and rate calculation for counter wraparound in the UI.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-net.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-rpc.go -->
# sources/object-store/minio-mc/cmd/support-top-rpc.go

Purpose: implements `mc support top rpc`, a real-time or replayable terminal UI for MinIO grid/RPC metrics.

Important APIs/types/functions: `supportTopRPCFlags`, `supportTopRPCCmd`, `checkSupportTopRPCSyntax`, `mainSupportTopRPC`, `topRPCUI`, `Update`, `View`, and `initTopRPCUI`. Sort constants define sort modes for host, reconnections, queue, and ping.

Control flow: if `--in` is provided, no target is required; the command opens a JSON-lines file, optionally wraps it in zstd decompression for `.zst`, replays `madmin.RealtimeMetrics` frames preserving capped inter-frame delay, and exits. Live mode validates target, enforces registration, creates an admin client, and streams `madmin.MetricsRPC` with interval, count, host filters, and `ByHost=true`. JSON mode prints raw metrics; interactive mode sends each metrics frame into `topRPCUI`.

State and persistence: read-only live mode; replay mode reads local files. UI state includes current/frozen metrics, offset, page size, direction toggle, and sort mode.

Dependencies and integration points: uses MinIO realtime metrics, Bubble Tea, lipgloss spinner, zstd, tablewriter, support registration, and global terminal sizing.

Risks and test signals: replay mode calls `os.Exit(0)` from a goroutine, which complicates tests and cleanup. Tests should cover `--in` parsing, zstd replay, host filters, JSON mode, freeze/toggle/sort keys, and nil RPC metrics rendering.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top-rpc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top.go -->
# sources/object-store/minio-mc/cmd/support-top.go

Purpose: defines the `mc support top` command namespace for real-time MinIO operational views.

Important APIs/types/functions: `supportTopSubcommands`, `supportTopCmd`, and `mainSupportTop`.

Control flow: registers `api`, `drive`, `locks`, `net`, and `rpc` subcommands. If invoked without a known subcommand, `mainSupportTop` delegates to `commandNotFound`.

State and persistence: no state changes in this file; streaming/read-only behavior is implemented in subcommand files.

Dependencies and integration points: integrated under top-level `support` command and the MinIO CLI package.

Risks and test signals: low logic risk; command availability and help behavior are the main concerns. Tests should verify subcommand registration and invalid-subcommand handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-top.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-upload.go -->
# sources/object-store/minio-mc/cmd/support-upload.go

Purpose: implements `mc support upload`, uploading a local file to a SUBNET issue with optional comment and encryption.

Important APIs/types/functions: `uploadFlags`, `supportUploadMessage`, `supportUploadCmd`, `checkSupportUploadSyntax`, `mainSupportUpload`, and `execSupportUpload`.

Control flow: the command requires `ALIAS FILE` and a positive `--issue`. It initializes SUBNET connectivity/registration, builds URL parameters for issue number and optional comment, prepares the attachment upload URL, and invokes `SubnetFileUploader` with auto-compression and optional auto-encryption. Success output includes the issue URL.

State and persistence: reads a local file and uploads it; does not mutate MinIO cluster config. The uploader may create transient compressed/encrypted artifacts depending on implementation.

Dependencies and integration points: depends on SUBNET URL/auth helpers, `SubnetFileUploader`, support registration/dev mode, global output handling, and URL query encoding.

Risks and test signals: validates issue number but not local file existence directly before uploader call. Tests should cover syntax, issue validation, comment parameter encoding, encryption flag propagation, upload errors, and JSON/text output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support.go -->
# sources/object-store/minio-mc/cmd/support.go

Purpose: defines the top-level `mc support` command, shared support flags/helpers, registration enforcement, feature-status helpers, and JSON utility.

Important APIs/types/functions: `supportGlobalFlags`, `supportSubcommands`, `supportCmd`, `toggleCmdArgs`, `validateToggleCmdArg`, `checkToggleCmdSyntax`, `setSuccessMessageColor`, `setErrorMessageColor`, `featureStatusStr`, `validateClusterRegistered`, `isFeatureEnabled`, `toJSON`, and `mainSupport`.

Control flow: `supportCmd` wires subcommands for register/callhome/diag/perf/inspect/profile/top/proxy/upload. Toggle helpers enforce `enable|disable|status ALIAS`. `validateClusterRegistered` checks whether SUBNET registration is required based on dev and airgap modes, then retrieves the SUBNET API key. `isFeatureEnabled` reads server config, handles unsupported subsystems and missing targets, and treats absent `enable` keys as enabled.

State and persistence: this file does not mutate state directly except color registry changes; it reads remote config and SUBNET registration info.

Dependencies and integration points: central integration point for support subcommands, MinIO admin client/config helpers, `madmin` config constants, console color tags, and global CLI flags.

Risks and test signals: registration logic is subtle: commands that talk to SUBNET require stricter dev+airgap bypass behavior. Tests should cover registration combinations, missing config targets, default target mapping, unsupported subsystems, and JSON marshal failures.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/table-ui.go -->
# sources/object-store/minio-mc/cmd/table-ui.go

Purpose: provides a tiny shared color abstraction for table/status UIs.

Important APIs/types/functions: `col` string type, color constants (`colGrey`, `colRed`, `colYellow`, `colGreen`), and `getPrintCol`.

Control flow: `getPrintCol` maps symbolic color names to bold terminal colors from `fatih/color`; unknown values return nil.

State and persistence: no persistent state. It allocates color objects per call.

Dependencies and integration points: used by terminal/table rendering code elsewhere in the command package when status colors are represented as values instead of direct `color.Color` instances.

Risks and test signals: low risk, but nil on unknown color requires callers to handle absence. Tests should assert mappings and unknown behavior if callers depend on non-nil colors.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/table-ui.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-list.go -->
# sources/object-store/minio-mc/cmd/tag-list.go

Purpose: implements `mc tag list`, listing bucket/object tags for a target, optional versions, rewind time, and recursive object traversal.

Important APIs/types/functions: `tagListFlags`, `tagListCmd`, `tagListMessage`, `parseTagListSyntax`, `showTags`, `showTagsSingle`, and `mainListTag`.

Control flow: syntax validation requires one target, rejects simultaneous `--version-id` and `--rewind`, parses rewind, and infers current UTC time when `--versions` is set without rewind. For a single non-recursive object/bucket, it calls `GetTags` directly. Recursive/versioned mode lists objects with `ListOptions`, skips delete markers, stops at the target when not recursive, and invokes `showTagsSingle` per content item.

State and persistence: read-only against S3/MinIO tag state.

Dependencies and integration points: depends on generic `Client` tag APIs, alias expansion/client creation, list traversal, `parseRewindFlag`, `minio.ToErrorResponse` for `NoSuchTagSet`, and colorized/JSON output.

Risks and test signals: recursive/versioned traversal can produce many per-object client creations. Tests should cover empty tag sets, version-id vs rewind validation, delete-marker skipping, recursive boundaries, sorted text output, and JSON schema.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-main.go -->
# sources/object-store/minio-mc/cmd/tag-main.go

Purpose: defines the `mc tag` command namespace.

Important APIs/types/functions: `tagSubcommands`, `tagCmd`, and `mainTag`.

Control flow: registers `list`, `remove`, and `set` as subcommands. Unknown or missing subcommands are handled through `commandNotFound`.

State and persistence: no state changes here; subcommands read or mutate tags.

Dependencies and integration points: integrated into the main command tree and uses the MinIO CLI framework plus global flags.

Risks and test signals: low risk. Tests should verify command registration, help text, and invalid-subcommand behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-remove.go -->
# sources/object-store/minio-mc/cmd/tag-remove.go

Purpose: implements `mc tag remove`, deleting bucket/object tags, optionally across versions and recursively.

Important APIs/types/functions: `tagRemoveFlags`, `tagRemoveCmd`, `tagRemoveMessage`, `parseRemoveTagSyntax`, `deleteTags`, `deleteTagsSingle`, and `mainRemoveTag`.

Control flow: syntax validation requires one target and rejects `--version-id` combined with `--rewind` or `--versions`. Single non-recursive mode creates one client and calls `DeleteTags`. Recursive/versioned mode lists objects with time/version options, skips delete markers, respects non-recursive target boundary, and deletes tags for each listed object version.

State and persistence: mutates remote bucket/object tag state by calling `Client.DeleteTags`.

Dependencies and integration points: uses alias expansion, `newClient`/`newClientFromAlias`, list traversal, `parseRewindFlag`, global context, colorized/JSON output, and probe errors.

Risks and test signals: broad recursive deletes are destructive. Tests should cover argument validation, version delete targeting, recursive traversal boundaries, delete-marker skipping, client creation errors, and JSON/text output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-set.go -->
# sources/object-store/minio-mc/cmd/tag-set.go

Purpose: implements `mc tag set`, assigning tags to a bucket/object or to multiple object versions recursively.

Important APIs/types/functions: `tagSetFlags`, `tagSetCmd`, `tagSetMessage`, `parseSetTagSyntax`, `setTags`, `setTagsSingle`, and `mainSetTag`.

Control flow: validation requires `TARGET TAGS`, rejects `--version-id` with rewind/versions, and requires `--exclude-folders` to be paired with `--recursive`. Single mode calls `SetTags` on one client. Recursive/versioned mode lists matching objects, skips delete markers, optionally skips folder-like objects when `excludeFolders` is set, respects non-recursive target boundary, and applies tags per content item/version.

State and persistence: mutates remote tag state through `Client.SetTags`; tags string format is passed through to client implementation.

Dependencies and integration points: uses list traversal, alias/client helpers, URL bucket/object parsing, rewind parsing, global context, and JSON/text output.

Risks and test signals: recursive tagging can affect many objects and the folder exclusion check is path-separator based. Tests should cover invalid flag combinations, tag string validation via client errors, version handling, delete-marker skipping, folder exclusion, and JSON schema.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tag-set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/term-pager.go -->
# sources/object-store/minio-mc/cmd/term-pager.go

Purpose: implements a terminal pager writer backed by Bubble Tea viewport, with fallback to stdout if the TUI cannot initialize.

Important APIs/types/functions: `model`, its `Init`, `Update`, `View`, `headerView`, and `footerView`; `termPager`, `init`, `Write`, `WaitForExit`, and `newTermPager`.

Control flow: `termPager.Write` lazily initializes a Bubble Tea program in a goroutine. The pager waits for the first window-size render or an initialization error. Data written into `buf` is sent to the Bubble Tea model as strings, where content is accumulated and word-wrapped to viewport width. Key events `q`, `esc`, and `ctrl+c` quit. Footer renders scroll percentage and a simple progress bar.

State and persistence: all state is in memory: accumulated content, viewport dimensions, channels, and program status. No files are written.

Dependencies and integration points: depends on Bubble Tea, bubbles viewport, lipgloss, wordwrap, stdout fallback, and callers that need an `io.Writer`-like pager.

Risks and test signals: `Write` blocks on an unbuffered channel after initialization; callers must eventually allow the pager goroutine to receive. Tests should cover fallback path, window resize, quit handling, scroll percent rendering, and `WaitForExit` behavior before/after initialization.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/term-pager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tofu.go -->
# sources/object-store/minio-mc/cmd/tofu.go

Purpose: implements trust-on-first-use handling for self-signed TLS certificates, prompting the user to trust a server certificate and saving it in the local CA directory.

Important APIs/types/functions: `marshalPublicKey`, `promptTrustSelfSignedCert`, and `fetchPeerCertificate`.

Control flow: `promptTrustSelfSignedCert` skips HTTP endpoints, then attempts an HTTPS request using loaded root CAs. If the request succeeds, nothing is needed. If the failure is an unknown/untrusted authority, it fetches the peer cert with `InsecureSkipVerify`, verifies that the certificate is self-signed using subject/authority key IDs or a SHA-1 public-key check for self-CA certs, prints the SHA-256 public-key fingerprint, and asks for `y/yes`. On confirmation, it writes `<alias>.crt` to `mustGetCAsDir`.

State and persistence: persists trusted certificates as PEM files in the mc CAs directory. Reads from stdin for confirmation.

Dependencies and integration points: uses custom TLS dialing, global root CAs, config directory helpers, probe errors, and standard x509/asn1 handling for RSA/ECDSA/Ed25519 public keys.

Risks and test signals: interactive trust prompts are security-sensitive. Tests should cover HTTP bypass, already trusted certs, non-self-signed unknown cert rejection, fingerprint confirmation rejection, PEM write errors, and public-key marshal variants.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tofu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/top-drives-spinner.go -->
# sources/object-store/minio-mc/cmd/top-drives-spinner.go

Purpose: provides the Bubble Tea UI model used by `support top drive` to render per-drive IO statistics.

Important APIs/types/functions: `topDriveUI`, `topDriveResult`, `initTopDriveUI`, `Update`, `View`, `driveIOStat`, `generateDriveStat`, `drivesSorter`, `sortDriveIOStat`, and sorter constants.

Control flow: initialization maps disk endpoints to `madmin.Disk` metadata and tracks maximum pool index. Updates handle quit keys, pool navigation, sort-key changes, sort-order toggling, and incoming `topDriveResult` samples. Each sample shifts current stats to previous and stores new stats. `View` filters disks by current pool, computes deltas over a one-second interval, sorts/truncates to requested count, and renders a table with used percent, TPS, read/write/discard MiB/s, await, and utilization.

State and persistence: transient UI state only: previous/current disk stat maps, selected pool, sort mode, and disk metadata.

Dependencies and integration points: consumed by `support-top-drive.go`; depends on Bubble Tea, lipgloss spinner, tablewriter, `madmin.Disk`/`DiskIOStats`, and shared styles/cell constants.

Risks and test signals: rate math assumes 1000 ms intervals and nondecreasing counters; zero total space suppresses metrics and marks endpoints. Tests should cover sorting modes, pool boundaries, healing/scanning markers, zero-space disks, and utilization/await calculations.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/top-drives-spinner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/top-net-spinner.go -->
# sources/object-store/minio-mc/cmd/top-net-spinner.go

Purpose: provides the Bubble Tea UI model used by `support top net` to render per-interface network throughput.

Important APIs/types/functions: `topNetUI`, `topNetResult`, `GetTotalBytes`, `Update`, `calculationRate`, `View`, and `initTopNetUI`.

Control flow: the UI stores previous/current `topNetResult` samples per endpoint. On each view render, it computes per-second RX/TX rates from counter deltas and sample duration, handles uint64 counter wraparound, sorts endpoints by total throughput, and renders server/interface/receive/transmit rows. Error rows show cross-tick cells and the error string. Quit keys stop the UI.

State and persistence: transient in-memory sample maps and sort flag. No persistence.

Dependencies and integration points: consumed by `support-top-net.go`; depends on Bubble Tea, lipgloss spinner, tablewriter, `madmin.NetMetrics`, Prometheus `procfs.NetDevLine`, humanized byte formatting, and shared UI styles.

Risks and test signals: zero or negative sample durations could divide by zero or produce misleading rates. Tests should cover wraparound, error rendering, missing previous sample, sort order, and quit behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/top-net-spinner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/trace-stats-ui.go -->
# sources/object-store/minio-mc/cmd/trace-stats-ui.go

Purpose: implements the terminal statistics UI for service trace events, used by `support top api` and related trace summaries.

Important APIs/types/functions: `traceStatsUI`, `Update`, `View`, `ibytesShort`, `roundDur`, and `initTraceStatsUI`.

Control flow: initialization creates a spinner, configures console colors, constructs a `statTrace`, and starts a goroutine that adds incoming `madmin.ServiceTraceInfo` values to the stats accumulator. `Update` handles quit, reset min/max (`r`), and scrolling keys. `View` reads accumulated calls under lock, computes duration, RX/TX rates, total RPM, sorts calls by count, applies viewport truncation based on `maxEntries` and offset, optionally includes TTFB columns, colors durations by thresholds, and truncates rendered lines to terminal width.

State and persistence: in-memory aggregate stats only. Reset mutates current min/max fields but does not clear counts.

Dependencies and integration points: depends on `statTrace`/`statItem` types from trace code, Bubble Tea, spinner, tablewriter, terminal width detection, console color registry, and humanized byte formatting.

Risks and test signals: duration can be zero early in collection, which can affect rate calculations. Tests should cover empty state, reset behavior, TTFB column appearance, truncation/offset boundaries, duration color thresholds, and concurrent add/render locking.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/trace-stats-ui.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tree-main.go -->
# sources/object-store/minio-mc/cmd/tree-main.go

Purpose: implements `mc tree`, rendering buckets/objects in tree form or delegating JSON output to recursive `ls`.

Important APIs/types/functions: tree glyph constants, `treeMessage`, `treeFlags`, `treeCmd`, `parseTreeSyntax`, `doTree`, and `mainTree`.

Control flow: syntax parsing accepts multiple targets, validates depth (`-1` unlimited, positive limited), parses rewind time, and pre-validates each target with `url2Stat`. `mainTree` defaults to `.` when no target is given, sets colors, and either calls `doTree` for text mode or `doList` with recursive options for JSON mode. `doTree` normalizes trailing separators, lists one directory level with `ShowDir: DirFirst`, delays printing each previous item until it knows whether it is the last child, recursively descends into directories within depth, and formats branch prefixes.

State and persistence: read-only listing command; only recursion stack and previous item are transient state.

Dependencies and integration points: uses generic client list/stat APIs, alias expansion, rewind parsing, `doList`, `printMsg`, and console colors.

Risks and test signals: recursion can be expensive on deep trees, and prefix/branch formatting is path-separator sensitive. Tests should cover depth validation, default target, JSON delegation, files vs directories, Windows-style examples, rewind propagation, and branch rendering for last/non-last children.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/tree-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/typed-errors.go -->
# sources/object-store/minio-mc/cmd/typed-errors.go

Purpose: defines typed error constructors used throughout the command package so callers can distinguish common validation and operation failures while presenting consistent messages.

Important APIs/types/functions: error marker types such as `dummyErr`, `invalidArgumentErr`, `unableToGuessErr`, `invalidAliasedURLErr`, `invalidAliasErr`, `invalidURLErr`, copy/move target/source errors, and SSE-specific errors; constructor variables like `errDummy`, `errInvalidArgument`, `errInvalidAlias`, `errRequiresRecursive`, `errSSEKeyMissing`, and `errSSEClientKeyFormat`.

Control flow: each constructor builds a message, wraps it in `probe.NewError`, and often calls `.Untrace()` to suppress stack traces for user-facing validation errors. Some constructors format dynamic values such as URLs, aliases, diff types, API signatures, or overlapping SSE prefixes.

State and persistence: no state; constructors allocate probe errors.

Dependencies and integration points: heavily used across CLI validation paths, copy/move/encryption code, and tests that inspect error JSON. Depends on `probe` and shared package constants like `validAPIs`.

Risks and test signals: misspellings and message text changes can affect scripted users and tests. Tests should validate error types/messages for CLI JSON output, trace suppression, and sentinel wrapping where callers use type assertions.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/typed-errors.go -->
