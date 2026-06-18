# Group Research: subset-b-000010

This grouped report covers the BuildKit client worker API, buildctl CLI commands, buildkitd configuration and startup paths, CDI setup helpers, control service glue, and examples listed in work item `subset-b-000010`. Each section is bounded for deterministic reconciliation into source-tree-aligned per-file research files.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/client/workers.go -->
# Research: sources/cloud-native/buildkit/client/workers.go

Purpose: exposes the client-side worker listing API used by `buildctl debug workers` and other callers that need daemon worker capabilities. The main data model is `WorkerInfo`, which mirrors control-service `WorkerRecord` fields for ID, labels, supported platforms, GC policy, BuildKit/Dockerfile versions, and CDI devices.

Important APIs and control flow: `Client.ListWorkers(ctx, opts...)` accumulates `ListWorkersOption` values into `ListWorkersInfo`, calls `ControlClient().ListWorkers`, wraps RPC errors with context, and converts protobuf records into stable client structs. `fromAPIGCPolicy` translates API GC policy durations and byte thresholds into `client.PruneInfo`.

State, dependencies, and integration: this file does not persist state; it is a typed adapter over the control gRPC API. It depends on `controlapi`, API type structs, platform conversion helpers in `solver/pb`, and version/CDI conversion helpers defined elsewhere in the client package.

Risks and test signals: incorrect conversion would make CLI worker output and programmatic worker discovery misleading, especially GC thresholds and platform lists. Tests are indirect through `buildctl debug workers` integration and daemon `Controller.ListWorkers`, with no file-local unit tests for filtering or conversion edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/client/workers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/build.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/build.go

Purpose: implements `buildctl build`, the primary CLI command that turns local CLI flags, stdin LLB, frontend options, sessions, cache settings, and exporters into a BuildKit solve/build request. It is the user-facing adapter between shell arguments and `client.Build`/gateway solve execution.

Important APIs and control flow: `buildCommand` defines flags for outputs, progress, tracing, local mounts, OCI layouts, frontend attrs, cache import/export, secrets, SSH, entitlements, metadata, source policy, proxy networking, ref file output, registry auth TLS, and debug cache metrics. `read` loads an LLB definition from stdin and optionally mutates metadata to ignore cache. `buildAction` resolves the client, opens optional trace/cache metric sinks, loads Docker auth and registry TLS context, attaches auth/SSH/secret providers, validates entitlements, parses outputs/cache/local/OCI options, loads source policy JSON, and builds a `client.SolveOpt`. It chooses stdin LLB when no frontend is set, injects frontend no-cache otherwise, sets up progress writers, tees status to trace/cache metrics, calls `c.Build` with a gateway solve callback, writes metadata, prints subrequest text metadata, and waits for metric emission.

State and persistence: persistent side effects are user requested: trace file append, cache metrics file/truncation, metadata JSON atomic write, and optional ref-file atomic write. The build itself persists through daemon workers, exporters, caches, and histories rather than local CLI state.

Dependencies and integration: integrates `cmd/buildctl/build` parsers, Docker CLI config auth, BuildKit sessions, auth/SSH/secret providers, gateway frontend client, progress writer, source policy protobuf, LLB protobuf, and containerd continuity atomic writes. Risk centers on flag parsing and concurrent progress tee lifetimes; malformed cache/secret/auth options fail early. Test signals include integration tests for local input, local/containerd exporters, metadata file decoding, push progress, and unit coverage of `writeMetadataFile`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/build_test.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/build_test.go

Purpose: provides integration coverage for `buildctl build` behavior across local inputs, exporters, metadata files, containerd image unpacking, registry push progress, and LLB stdin marshaling. The tests run through BuildKit integration sandboxes rather than isolated mocks.

Important functions and flow: `testBuildWithLocalFiles` builds an LLB graph that compares a local file mount against generated output. `testBuildLocalExporter` exports a generated file to a local directory and normalizes Windows CRLF. `testBuildContainerdExporter` exports an image with unpacking and verifies the image in containerd namespace `buildkit`. `testBuildMetadataFile` writes image exporter metadata and checks image name, digest, descriptor shape, and optional containerd digest match. `testBuildPushProgress` starts a registry and asserts push progress text. `marshal` serializes an LLB state to the protobuf stream consumed by `buildctl build`.

State and dependencies: tests create temporary filesystem inputs/outputs, containerd clients, registry sandboxes, and image records. They depend on integration helpers, LLB, containerd namespaces, OCI descriptors, and official base images mirrored by the suite.

Risks and test signals: these tests exercise high-value paths but are environment dependent, with Windows skips or behavior normalization. They validate that CLI arguments are wired into real daemon state, but they do not directly cover every parser failure branch or tracing/cache metrics behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/build_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/buildctl_test.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/buildctl_test.go

Purpose: is the top-level integration test harness for the `buildctl` binary plus a focused unit test for metadata file serialization. It initializes OCI and containerd workers so the integration suite can exercise multiple daemon backends.

Important APIs and flow: `init` registers worker fixtures. `TestCLIIntegration` delegates to `integration.Run` with disk usage, build, prune, and usage tests and mirrors official images. `testUsage` verifies the base command and help path succeed. `TestWriteMetadataFile` feeds exporter responses through `writeMetadataFile`, including ordinary strings, base64 JSON objects, empty objects, non-object JSON, invalid semantic JSON for this purpose, and null-containing objects.

State and dependencies: test state is temporary directories plus integration daemon/containerd state. The metadata test verifies local atomic file output and JSON unmarshaling behavior without daemon dependencies.

Risks and test signals: this file gives good regression signals for CLI wiring and metadata conversion, especially the intentionally narrow rule that only non-empty JSON objects are embedded as raw JSON. It does not validate trace/cache metric output or every command in the CLI tree.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/buildctl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/cachemetrics.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/cachemetrics.go

Purpose: implements the optional `--debug-json-cache-metrics` build output that summarizes cache behavior from streamed `client.SolveStatus` vertex updates. It helps users inspect cache misses without parsing full progress JSON.

Important APIs and flow: `vtxInfo` tracks vertex cached/completed/from/name booleans. `tailVTXInfo` consumes the status channel until close, records every vertex by digest, marks Dockerfile `FROM` vertices using a regexp, and records cached/completed state. `outputCacheMetrics` computes total, completed, user total, user cached/completed/cacheable, `FROM`, miss count, and client duration, writes one line per non-FROM user cache miss, then writes a JSON metrics object.

State and dependencies: all state is in-memory and derived from progress stream tails. It depends on `client.SolveStatus`, OCI digests, regexp matching, and elapsed wall-clock time from build start.

Risks and test signals: metrics are heuristic because vertex names classify internal/auth/import/export and `FROM` operations by strings. Name changes in progress output can skew counts. There is no direct unit test in this group; coverage is indirect through build progress code paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/cachemetrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/common/common.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/common/common.go

Purpose: contains shared buildctl helpers for resolving daemon clients, TLS files, and Go-template output formats. It centralizes connection behavior used by build, debug, disk usage, prune, and history commands.

Important APIs and flow: `ResolveClient` derives TLS server name from `--addr` when omitted, rejects simultaneous `--tlsdir` and explicit TLS file flags, resolves cert files, attaches tracing client options when the command context has an active span, applies CA/client credentials, wraps the command context with an optional timeout, creates `client.New`, and optionally waits for backend readiness. `ParseTemplate` supports the `json` alias and a Docker-style `json` template function. `resolveTLSFilesFromDir` searches for PEM or cert-manager style names and fails if any CA/cert/key component is missing.

State and dependencies: no persistent state; it depends on CLI metadata, BuildKit client options, OpenTelemetry span context, URL parsing, templates, and filesystem stat calls for TLS material.

Risks and test signals: connection setup is security-sensitive because wrong server names or credential file selection can break TLS validation. `common_test.go` covers TLS directory resolution precedence and mixed file naming, while client resolution is covered indirectly by every integration CLI command.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/common/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/common/common_test.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/common/common_test.go

Purpose: unit-tests TLS directory discovery for `buildctl` client resolution. It is focused on `resolveTLSFilesFromDir`, avoiding daemon dependencies.

Important functions and flow: `writeTempFile` creates test certificate/key placeholders. `TestResolveTLSFilesFromDir` covers cert-manager names (`ca.crt`, `tls.crt`, `tls.key`), PEM names (`ca.pem`, `cert.pem`, `key.pem`), mixed sets, and the precedence rule that PEM names are selected when both naming schemes exist.

State and dependencies: state is limited to `t.TempDir` files. It uses `stretchr/testify/require` for assertions and standard filesystem writes.

Risks and test signals: the test protects a common deployment path where TLS secrets are mounted into a directory. Missing negative tests mean errors for partial directories or stat failures are not explicitly verified here, though the production function returns clear errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/common/common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/common/trace.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/common/trace.go

Purpose: attaches OpenTelemetry tracing to buildctl commands and stores the command context in root CLI metadata so other helpers can retrieve it consistently. It also delegates trace export over BuildKit client connections.

Important APIs and flow: `AttachAppContext` builds a base app context, creates a detected span exporter plus delegated exporter, wraps each top-level command `Before` hook to start a span named after the command, stores the span context under `Root().Metadata["context"]`, records errors in `ExitErrHandler`, ends the span in `After`, and shuts down the tracer provider with a short `exportTimeout`. `CommandContext` retrieves the context from CLI metadata.

State and dependencies: state is per-process CLI metadata plus an active span. It depends on BuildKit app context helpers, tracing detection, delegated exporter, OTEL SDK trace provider, and urfave/cli hooks.

Risks and test signals: `CommandContext` assumes metadata was initialized, so commands must go through `AttachAppContext`. The short 50 ms shutdown avoids hanging CLIs but can drop slow trace exports. There are no file-local tests; behavior is exercised indirectly by CLI execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/common/trace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug.go

Purpose: defines the `buildctl debug` command namespace and registers all debug subcommands. It is a thin command tree assembly file.

Important APIs and flow: `debugCommand` names the group `debug`, sets usage text, and wires `dump-llb`, `dump-metadata`, `workers`, `info`, `monitor`, `logs`, `ctl`, `get`, and `histories` from `cmd/buildctl/debug`.

State and dependencies: no runtime state or persistence is owned here. It depends on the debug subpackage and urfave/cli command definitions.

Risks and test signals: the risk is primarily command registration drift; missing a subcommand here makes its implementation unreachable from the binary. It is covered only indirectly through CLI help/usage and any integration tests that call debug subcommands.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/cli.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/cli.go

Purpose: supplies a small adapter that converts debug package functions of shape `func(*cli.Command) error` into urfave/cli v3 `ActionFunc`.

Important APIs and flow: `commandAction` ignores the context argument supplied by cli v3 and passes the command object to the package command function. This keeps debug command implementations consistent with the main package command style.

State and dependencies: no state or persistence. It depends only on `context` and `github.com/urfave/cli/v3`.

Risks and test signals: because it discards the passed action context, debug commands rely on app-level context storage via common helpers or `appcontext.Context()`. There are no direct tests; errors surface when debug commands are executed through the CLI.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/cli.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/ctl.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/ctl.go

Purpose: implements `buildctl debug ctl`, a command for mutating build history records by pinning, unpinning, or deleting a reference.

Important APIs and flow: `CtlCommand` defines `--pin`, `--unpin`, and `--delete`. `ctl` requires a build ref argument, resolves the BuildKit client, validates that exactly one operation mode is selected, and calls `ControlClient().UpdateBuildHistory` with `Pinned` or `Delete` fields.

State and dependencies: this command mutates daemon history state stored by the control service, not local files. It depends on `controlapi.UpdateBuildHistoryRequest`, shared client resolution, and app context.

Risks and test signals: validation prevents contradictory flags, but delete is irreversible at daemon history level. There are no direct unit tests for this command in the listed files; history mutation is indirectly covered by control service behavior and debug CLI use.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/ctl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/dumpllb.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/dumpllb.go

Purpose: implements `buildctl debug dump-llb`, a daemonless diagnostic command for decoding serialized LLB definitions into JSON lines or Graphviz DOT.

Important APIs and flow: `dumpLLB` reads from a named file or stdin, calls `loadLLB`, and either JSON-encodes each `llbOp` or writes DOT. `loadLLB` uses `llb.ReadFrom`, unmarshals each protobuf op, computes its digest, and attaches metadata. `writeDot` emits nodes and dependency edges, using mount destinations as edge labels for exec ops. `attr` maps op kinds to readable labels and DOT shapes.

State and dependencies: no persistence; input is an LLB stream and output is stdout. Dependencies include LLB serialization, solver protobufs, OCI digest, JSON, and DOT-compatible formatting.

Risks and test signals: DOT labels are derived from op fields and do not include full metadata; unknown ops fall back to digest labels. Malformed protobufs fail during load. No direct tests are listed, but the command is isolated enough for future golden tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/dumpllb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/dumpmetadata.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/dumpmetadata.go

Purpose: implements `buildctl debug dump-metadata`, an offline inspection command for worker `metadata_v2.db` Bolt databases. It intentionally requires the daemon not to be running to avoid concurrent metadata access issues.

Important APIs and flow: `DumpMetadataCommand` accepts `--root`, finds per-worker `metadata_v2.db` files under root subdirectories, prints file headers, opens each database read-only with a timeout, and recursively prints buckets and key/value entries through `dumpBucket`.

State and dependencies: reads persistent BuildKit metadata databases but does not modify them. It depends on app default root paths, filesystem traversal, and bbolt read-only transactions.

Risks and test signals: raw key/value stringification can produce noisy or binary-looking output, and the command assumes the daemon is stopped. There are no direct tests here; operational safety relies on read-only Bolt open and user discipline.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/dumpmetadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/get.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/get.go

Purpose: implements `buildctl debug get`, a low-level content-store blob retrieval command. It streams a blob addressed by digest from the daemon content service to stdout.

Important APIs and flow: `get` requires a digest argument, parses it, resolves the BuildKit client, creates a proxy content store over `c.ContentClient()`, opens a `ReaderAt` with an OCI descriptor, and copies the content to stdout using a 1 MiB buffer.

State and dependencies: no local persistence. It reads daemon content-store state and depends on containerd content/proxy APIs, OCI descriptors, digest parsing, and app context.

Risks and test signals: stdout receives raw blob bytes, so users can corrupt terminals if retrieving binary content. Errors are mainly invalid digest or missing content. There are no direct tests in this group.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/histories.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/histories.go

Purpose: implements `buildctl debug histories`, a read-only command for listing build history records from the daemon.

Important APIs and flow: `histories` resolves the client, calls `ListenBuildHistory` with `EarlyExit`, and either applies a user template to each event or prints a tabular stream via `printRecordsTable`. The table includes event type, ref, created/completed timestamps, generation, and a pinned marker.

State and dependencies: reads daemon history DB through the control API. It depends on common template parsing, app context, control API stream clients, `io.EOF` handling, tabwriter, and local timezone formatting.

Risks and test signals: template mode exposes raw events while table mode only shows selected fields. Streaming errors abort output. Direct tests are absent, but `prune-histories` uses similar stream handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/histories.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/info.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/info.go

Purpose: implements `buildctl debug info`, which displays BuildKit and Dockerfile frontend version information reported by the daemon.

Important APIs and flow: `info` resolves the client, calls `c.Info` with the command context, then either executes a template or prints a small tabwriter table with BuildKit package/version/revision and optional Dockerfile version.

State and dependencies: no persistence; reads daemon version state through the client info API. Dependencies are shared client resolution, template parsing, tabwriter, and standard output.

Risks and test signals: output depends on daemon capability and Dockerfile version availability. The command is simple and has no direct test in this subset; version response construction is covered on the daemon side by `Controller.Info`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/logs.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/logs.go

Purpose: implements `buildctl debug logs`, allowing users to replay build progress logs or retrieve an attached OpenTelemetry trace for a build reference.

Important APIs and flow: `logs` requires a build ref and resolves the client. With `--trace`, it fetches a history record, validates trace metadata, opens the trace blob from the content store, and copies raw trace bytes to stdout. Without `--trace`, it opens a `Status` stream for the ref, creates a progress writer with the requested mode, converts each protobuf status response into `client.SolveStatus`, and feeds the writer until EOF.

State and dependencies: reads daemon history, content store, and solver status state. It depends on control API streams, content proxy, progresswriter, OCI descriptor/digest handling, and app context.

Risks and test signals: progress mode can block if writer shutdown is mishandled, and trace mode outputs binary data. Missing refs and records without trace are explicit errors. There are no direct tests in this group.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/logs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/monitor.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/monitor.go

Purpose: implements `buildctl debug monitor`, a live build-history event monitor for active or completed builds.

Important APIs and flow: `monitor` resolves the client, calls `ListenBuildHistory` with `ActiveOnly` inverted from `--completed` and optional `--ref`, then prints each event with ref, cache counts, warning count, logs/trace descriptors, result descriptors, attestations, and named result groups.

State and dependencies: reads history event stream state from the daemon and does not persist locally. It depends on control API history records, app context, and straightforward formatted stdout.

Risks and test signals: the loop currently returns any receive error, including EOF, so it is mainly intended for continuous streams. The printed shape is ad hoc and not template driven. There are no direct tests in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/workers.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/workers.go

Purpose: implements `buildctl debug workers`, the CLI display path for daemon worker inventory. It exposes filtering, templates, and verbose detail for platforms, labels, GC policies, versions, and CDI devices.

Important APIs and flow: `listWorkers` resolves the client, calls `Client.ListWorkers` with filter strings, and chooses template output, verbose output, or compact table output. `printWorkersVerbose` prints stable sorted label and annotation keys, BuildKit/Dockerfile versions, CDI device auto/on-demand mode, and every GC policy rule with human-readable units. `joinPlatforms` normalizes platform specs.

State and dependencies: reads daemon worker state only. It depends on the client worker adapter, common template parsing, tabwriter, platform formatting, sorted map iteration, unit formatting, and command context metadata.

Risks and test signals: verbose output is sensitive to nil/empty fields and map order, which sorted keys mitigate. Template mode ignores `--verbose`. Direct tests are absent, but the daemonless example uses this command as a readiness probe.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/debug/workers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/dialstdio.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/dialstdio.go

Purpose: implements hidden `buildctl dial-stdio`, used by connection helpers to proxy stdin/stdout to a Unix daemon socket. It is not a normal user command.

Important APIs and flow: `dialStdioAction` dials the configured address with timeout, adapts the connection to half-close interfaces, starts copy goroutines for stdin-to-connection and connection-to-stdout, and returns when either direction finishes according to TTY-friendly rules. `dialer` accepts only `unix://` addresses. `copier` performs `io.Copy` and closes read/write halves with logged close errors.

State and dependencies: no persistence; it moves stream bytes between process stdio and a socket. Dependencies are net dialing, half-close interface support, BuildKit logging, CLI flags, and OS stdio wrappers.

Risks and test signals: non-Unix or connections lacking half-close support fail. Returning immediately when socket-to-stdout finishes avoids hanging on TTY stdin but can hide late stdin errors. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/dialstdio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/diskusage.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/diskusage.go

Purpose: implements `buildctl du`, a cache disk usage inspection command. It retrieves usage records from the daemon and renders table, verbose, or template output.

Important APIs and flow: `diskUsage` resolves the client, calls `c.DiskUsage` with filter options, chooses template mode if requested, otherwise prints verbose records or a compact table, and prints aggregate summary when no filter is applied. Helpers print key/value records, table headers/rows, and total/reclaimable/shared/private byte summaries.

State and dependencies: reads daemon worker disk usage state without mutating it. It depends on client disk usage APIs, common template parsing, tabwriter, BuildKit logging for ignored verbose mode, and human-readable units.

Risks and test signals: compact table omits `Last accessed` content despite the header, and formatting appends markers for mutable/shared records. `diskusage_test.go` only smoke-tests command success in integration, so output details need manual/golden coverage for regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/diskusage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/diskusage_test.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/diskusage_test.go

Purpose: provides a minimal integration smoke test for the `buildctl du` command.

Important function and flow: `testDiskUsage` runs `sb.Cmd("du")` against an integration sandbox and asserts that the command exits without error.

State and dependencies: depends on the integration sandbox daemon and worker cache state. It does not create specific cache records or validate output.

Risks and test signals: the test confirms basic command-to-daemon wiring and avoids output regressions only at the level of fatal errors. It does not verify table columns, summary math, filtering, template output, or verbose formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/diskusage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/main.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/main.go

Purpose: is the entrypoint for the `buildctl` CLI binary. It defines global flags, registers subcommands, initializes logging, tracing, profiling, version output, and central error handling.

Important APIs and flow: `init` sets exported product/version info and suppresses OTEL stdio errors. `main` computes default address from `BUILDKIT_HOST` or app defaults, defines global debug/address/TLS/timeout/wait/log flags, registers `du`, `prune`, `prune-histories`, `build`, `debug`, and `dial-stdio`, disables slice flag separators recursively, configures logrus in `Before`, attaches command tracing, attaches profiler flags, and runs the CLI. `handleErr` prints source locations, policy deny messages, and either stack-formatted or concise errors before exiting.

State and dependencies: process-global state includes logrus formatter/level, OTEL error handler, stack version info, and CLI metadata context. It imports connection helper packages for side effects.

Risks and test signals: global command initialization is central; mistakes affect every command. TLS and timeout flags feed common client resolution. Integration `testUsage` checks base/help success, while most command behavior is covered elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/main_unix.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/main_unix.go

Purpose: applies Unix-specific process initialization for `buildctl` by zeroing the process umask and telling fsutil copy that the umask is zero.

Important APIs and flow: the `init` function calls `syscall.Umask(0)` and sets `copy.UmaskIsZero = true`. This affects file mode behavior for operations that rely on fsutil copy semantics.

State and dependencies: changes process-global umask on non-Windows builds. It depends on `syscall` and `github.com/tonistiigi/fsutil/copy`.

Risks and test signals: a process-wide umask change can affect any files created by buildctl commands, though this is intentional for reproducible copy/export behavior. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/main_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/prune.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/prune.go

Purpose: implements `buildctl prune`, the cache cleanup command that streams records removed by daemon workers and summarizes reclaimed space.

Important APIs and flow: `pruneCommand` defines keep-duration, storage thresholds, filters, `--all`, verbose, and format flags. `prune` resolves the client, builds `client.PruneOption` values with filter and keep settings, appends `client.PruneAll` when requested, starts an output goroutine for template or table/verbose mode, invokes `c.Prune` with a channel, closes the channel, waits for printing, returns prune errors, and prints total reclaimed bytes when applicable.

State and dependencies: mutates daemon cache state through worker prune operations; local state is only a streaming channel and summary counter. Depends on client prune options, common templates, tabwriter, units, and disk usage row printers shared with `du`.

Risks and test signals: template output panics inside the goroutine on write/template errors, which would crash rather than return a normal error. `prune_test.go` smoke-tests successful integration execution but not filters, keep thresholds, all mode, or output formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/prune_test.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/prune_test.go

Purpose: provides a minimal integration smoke test for the `buildctl prune` command.

Important function and flow: `testPrune` runs `sb.Cmd("prune")` against the sandbox and asserts no error. It does not seed specific cache entries or validate output.

State and dependencies: mutates sandbox cache state by asking the daemon to prune. It depends on the integration test harness and `stretchr/testify/require`.

Risks and test signals: this confirms basic command and RPC wiring but does not protect nuanced behavior such as keep-duration, storage limits, all/internal pruning, template mode, verbose mode, or reclaimed-byte summary.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/prunehistories.go -->
# Research: sources/cloud-native/buildkit/cmd/buildctl/prunehistories.go

Purpose: implements `buildctl prune-histories`, which deletes unpinned build history records and prints the records it removed.

Important APIs and flow: `pruneHistories` resolves the client, opens a `ListenBuildHistory` stream with `EarlyExit`, then either templates each deleted event or delegates to `pruneHistoriesWithTableOutput`. Both modes skip nil and pinned records, call `UpdateBuildHistory(Delete: true)` for each remaining ref, collect deletion errors, and continue processing other records.

State and dependencies: mutates daemon history DB through the control API. It depends on app context, control API stream/update calls, common template parsing, tabwriter, local timestamp formatting, and joined errors.

Risks and test signals: the command is destructive for unpinned histories and has no confirmation. It intentionally aggregates per-record errors. There are no direct tests in this subset; behavior overlaps with debug history APIs and daemon history queue logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildctl/prunehistories.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/config.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/config.go

Purpose: defines the TOML-backed BuildKit daemon configuration schema. It is the shared contract consumed by daemon startup, worker initializers, resolver setup, GC policy construction, CDI setup, frontend gating, provenance, and cache backends.

Important types: `Config` includes root path, deprecated debug/trace flags, insecure entitlements, proxy network, log, gRPC/TLS, OTEL, CDI, worker configs, registry resolver config, DNS, history, frontends, system tuning, provenance env dir, and cache config. Worker structs split OCI and containerd options, each embedding `GCConfig` and `NetworkConfig`. `GCPolicy`, `DiskSpace`, `Duration`, `DNSConfig`, `HistoryConfig`, frontend configs, and GHA cache config shape nested TOML sections.

State and dependencies: this file defines data only; persistence is in the TOML file and daemon root directories. It depends on GHA cache types and resolver registry config types.

Risks and test signals: schema tags are compatibility-sensitive because user config files depend on them. Deprecated fields remain for backward compatibility. `load_test.go` validates many nested TOML mappings, but not every field such as CDI, frontends, system tuning, provenance, or cache GHA.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy.go

Purpose: implements parsing and defaulting for daemon garbage-collection thresholds and policy rules. It translates human TOML values into durations and byte/percentage disk-space controls.

Important APIs and flow: `Duration.UnmarshalText` accepts Go duration strings or integer seconds. `DiskSpace.UnmarshalText` accepts percentages or Docker unit strings. `DefaultGCPolicy` preserves deprecated `gckeepstorage` compatibility, detects default caps when unset, and returns four ordered policies: quick cleanup of reproducible sources/cache mounts, old-data cleanup, unshared cache cap, and all-data cap. `DetectDefaultGCCap` computes reserve/max/free settings from platform constants. `DiskSpace.AsBytes` converts bytes or percentages against disk stats, with `defaultCap` fallback when disk total is unknown. `GCConfig.IsUnset` checks modern threshold fields.

State and dependencies: no persistence, but outputs feed worker GC policies that later delete cache. Depends on docker/go-units, disk stats, platform constants from OS-specific files, and TOML text unmarshaling.

Risks and test signals: percentage rounding and deprecated field fallback affect data-retention behavior. `gcpolicy_test.go` verifies the first default policy filter matches only intended cache record types, but threshold parsing itself is mostly covered through config load tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_test.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_test.go

Purpose: validates that default GC policy filters remain compatible with containerd-style filter parsing and target the intended cache record types.

Important function and flow: `TestDefaultGCPolicyFiltersMatch` builds default policies with a 1 TB disk stat, parses the first rule's filters, adapts selected `client.UsageRecordType` values into filter fields, and asserts local source, exec cache mount, and git checkout records match while regular cache does not.

State and dependencies: no persistence; it depends on containerd filters, BuildKit client usage record constants, disk stats, and testify assertions.

Risks and test signals: this protects the most subtle part of the default policy, where filter strings must match worker usage record typing. It does not verify byte thresholds, policy ordering beyond first-rule selection, or OS-specific percentage constants.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_unix.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_unix.go

Purpose: supplies non-Windows default GC cap constants used by `DetectDefaultGCCap`.

Important constants: Unix builds reserve 10% up to 10 GB, set max cache use to 60% up to 100 GB, and target 20% free disk space.

State and dependencies: no runtime state or imports. The constants feed daemon worker GC policy defaulting.

Risks and test signals: these defaults directly influence automatic cache deletion behavior on Unix systems when users omit explicit GC thresholds. There are no direct tests for these exact constants in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_windows.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_windows.go

Purpose: supplies Windows-specific default GC cap constants used by `DetectDefaultGCCap`.

Important constants: Windows builds reserve 10% up to 10 GB, set max cache use to 60% up to 50 GB, and target 20% free disk space. The lower max-byte cap differs from Unix.

State and dependencies: no runtime state or imports. The constants feed default GC policies for Windows workers.

Risks and test signals: incorrect constants can cause over-aggressive or under-aggressive cache cleanup on Windows. There are no file-local tests; behavior is indirectly exercised when config defaults are built on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/load.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/load.go

Purpose: provides daemon config loading from TOML streams and files.

Important APIs and flow: `Load` decodes a `Config` from an `io.Reader` using `pelletier/go-toml/v2` and wraps parse errors. `LoadFile` opens a path, returns an empty config when the file does not exist, wraps other open errors with the path, defers close, and delegates to `Load`.

State and dependencies: reads config file state but does not write. Depends on TOML decoding, standard I/O, and pkg/errors wrapping.

Risks and test signals: returning empty config for missing files is intentional and supports default startup, but can hide typoed default paths while explicit load errors still surface for non-ENOENT. `load_test.go` covers complex TOML decoding but not missing-file behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/load.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/load_test.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/load_test.go

Purpose: validates TOML decoding for a representative `buildkitd.toml` configuration covering root, logging compatibility fields, entitlements, gRPC/TLS, OTEL, OCI and containerd worker settings, GC policy variants, registry config, and DNS.

Important flow: `TestLoad` decodes an inline TOML string with nested tables and repeated `gcpolicy` entries, then asserts primitive values, pointer fields, labels with dotted keys, runtime options, bytes/percentage/duration parsing, registry mirror/TLS/keypair values, and DNS lists.

State and dependencies: no persisted files; it uses an in-memory buffer and the config loader. Dependencies are `time` and testify assertions.

Risks and test signals: the test is strong for schema/tag regression and text unmarshaling compatibility, especially percentage and unit values. It does not cover all newer config fields, invalid TOML, missing file handling, or default application performed in `cmd/buildkitd/main.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/config/load_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/debug.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/debug.go

Purpose: registers and implements buildkitd HTTP debug endpoints for expvar, pprof, net/trace, Prometheus metrics, GC triggering, in-flight trace recording, and cache-debug inspection. It is enabled only when `debugAddress` is configured.

Important APIs and flow: `setupDebugHandlers` mounts `/debug/vars`, pprof, `/debug/requests`, `/debug/events`, cache endpoints, `/debug/gc`, `/metrics`, and flight recorder routes, then listens through the same listener abstraction used by the daemon. Cache endpoints load plaintext digest debug records, lookup individual digests, parse cache import JSON into temporary cache key storage, and render cache-store records as text or JSON. `debugCacheStore` walks solver cache records, resolves related digests/selectors through the cachedigest DB, and attaches readable debug frames.

State and persistence: reads and sometimes triggers runtime state. `/debug/gc` forces Go GC. Cache debug reads `cachedigest` and solver cache stores; `/debug/cache/load` parses request bodies but does not persist them to daemon state. `cacheStoreForDebug` is set during controller creation.

Dependencies and risks: depends on HTTP, pprof, expvar, Prometheus, cachedigest, cache import parser, cache store internals, and listener security. Debug address is opt-in, but endpoints expose sensitive cache/build internals and should be bound carefully. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/debug_flight.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/debug_flight.go

Purpose: adds HTTP endpoints for Go execution flight recorder traces under the daemon debug server.

Important APIs and flow: `flightRecorder` wraps an `x/exp/trace.FlightRecorder` with a mutex. `StartTrace`, `StopTrace`, `SetTracePeriod`, and `Trace` validate current recorder state, parse period values, set response headers, and write trace data. `setupDebugFlight` registers POST start/stop/set-period routes and a GET trace download route.

State and dependencies: state is the in-memory flight recorder and its enabled/period settings. It depends on `net/http`, mutex locking, duration parsing, and `golang.org/x/exp/trace`.

Risks and test signals: mutex serialization prevents concurrent recorder mutation, but trace downloads can expose detailed runtime behavior. Errors are returned as HTTP status codes. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/debug_flight.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/devices_nvidia.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/devices_nvidia.go

Purpose: conditionally imports the NVIDIA CDI setup package when the `nvidia` build tag is enabled. Its only job is side-effect registration.

Important behavior: the file has build tag `nvidia`, package `main`, and a blank import of `github.com/moby/buildkit/contrib/cdisetup/nvidia`, causing that package's `init` to register its `nvidia.com/gpu` setup with the CDI device manager.

State and dependencies: no local state. Runtime state is created by the imported package's registration and later device setup.

Risks and test signals: build-tag selection controls whether experimental NVIDIA on-demand setup is present in the daemon. There are no direct tests for tag wiring here; `nvidia_test.go` covers a helper in the imported package.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/devices_nvidia.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/devices_venus.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/devices_venus.go

Purpose: conditionally imports the Venus CDI setup package when the `venus` build tag is enabled. Its behavior is side-effect registration for Docker Desktop GPU support.

Important behavior: the file has build tag `venus`, package `main`, and a blank import of `github.com/moby/buildkit/contrib/cdisetup/venus`, causing package init to register the `docker.com/gpu` setup.

State and dependencies: no local state. The imported package may later inspect devices and write CDI specs when invoked through the CDI manager.

Risks and test signals: feature availability depends entirely on build tags. There are no direct tests for this import wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/devices_venus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main.go

Purpose: is the BuildKit daemon entrypoint and composition root. It loads/defaults configuration, configures logging/telemetry/listeners, initializes workers/frontends/cache/history/control services, and serves the gRPC API.

Important APIs and control flow: package init sets exported product and trace recorder. `registerWorkerInitializer` stores OCI/containerd worker initializers by priority. `main` builds the CLI, default config, rootless/group/log/TLS/CDI/service flags, then its action loads config, applies defaults and flags, configures logrus, system tuning, debug handlers, tracer/meter providers, gRPC server interceptors, absolute root, service registration, root lock, listeners, optional cache debug DB, controller, health/reflection, entitlements, service launch, and server lifecycle with graceful stop plus telemetry shutdown in `After`. Helpers implement listener creation, systemd readiness, config defaults, rootless detection, flag application, group lookup/security descriptor dispatch, TLS credentials, worker controller assembly, platform parsing, GC policy conversion, DNS config, bool-or-auto parsing, trace collector, OTEL providers/views, CDI manager construction, and lazy GHA policy verifier creation.

State and persistence: persistent state includes daemon root, lock file, cache DB, history DB, optional cache-debug DB, worker storage, policy verifier state, CDI spec scanning, and provenance env JSON input. It also mutates process-global logging, tracing, umask via platform files, and registry concurrency.

Dependencies and integration: integrates almost every daemon subsystem: gRPC, worker/controller, Dockerfile/gateway frontends, remote cache import/export backends, resolver config, session manager, OpenTelemetry/Prometheus, systemd, service wrappers, CDI, policy verifier, and app defaults.

Risks and test signals: risks include security of unauthenticated TCP listeners, rootless requirements, TLS config completeness, root lock contention, worker absence, and lifecycle cleanup. `main_test.go` covers proxy-network flag override only; most behavior is integration-tested elsewhere or relies on subsystem tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker.go

Purpose: registers and implements the containerd worker initializer for buildkitd. It translates config/CLI flags into containerd worker options and constructs a BuildKit worker when a usable containerd daemon is available.

Important APIs and flow: init computes defaults for containerd address, namespace, runtime, rootless, GC flags, network flags, snapshotter, labels, apparmor/SELinux, and parallelism, then registers priority 1. `applyContainerdFlags` applies CLI overrides and validates rootless requirements. `containerdWorkerInitializer` skips disabled/unavailable sockets in auto mode, adjusts rootless network default to host, builds DNS/CDI/network/parallelism/runtime options, calls `containerd.NewWorkerOpt`, sets GC policy, BuildKit version, registry hosts, optional platforms, and wraps the result in `base.NewWorker`. `validContainerdSocket` checks socket existence, client connection, and containerd introspection.

State and dependencies: persists through worker root and containerd namespace/snapshotter state. Depends on containerd client/defaults/runtime options, TOML conversion for runtime options, network providers, CDI manager, disk/GC helpers, semaphore parallelism, and BuildKit worker/base packages.

Risks and test signals: auto mode can silently skip containerd if the socket is absent or unhealthy; explicit enable turns errors into startup failures. Runtime option unmarshaling is type-dependent via platform files. No direct tests in this group cover flag interactions or socket probing.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker_unix.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker_unix.go

Purpose: provides Unix runtime option type selection for containerd worker runtime configuration.

Important API: `getRuntimeOptionsType` returns `runcoptions.Options` for `plugins.RuntimeRuncV2`; otherwise it returns generic `runtimeoptions.Options`. The selected struct is the TOML unmarshal target for configured runtime options.

State and dependencies: no persistence here; it shapes how config data is decoded before being passed to containerd. Depends on containerd runtime option packages and plugin runtime names.

Risks and test signals: choosing the wrong options type would drop or reject runtime-specific options. There are no direct tests for this mapping in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker_windows.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker_windows.go

Purpose: provides Windows runtime option type selection for containerd worker runtime configuration.

Important API: `getRuntimeOptionsType` returns `runhcsoptions.Options` for `plugins.RuntimeRunhcsV1`; otherwise it returns generic `runtimeoptions.Options`. This allows TOML runtime options to decode into the correct Windows shim struct.

State and dependencies: no persistence here; decoded options are later included in containerd worker runtime info. Depends on hcsshim runhcs options and containerd plugin constants.

Risks and test signals: a mismatched runtime type can make Windows containerd worker startup fail or ignore options. There are no direct tests for this mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_containerd_worker_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_nolinux.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_nolinux.go

Purpose: provides non-Linux reexec initialization for buildkitd.

Important behavior: on `!linux` builds, package init calls `reexec.Init()` and exits with status 0 when the process is a reexecuted child command.

State and dependencies: process-control side effect only. Depends on `github.com/moby/sys/reexec` and `os.Exit`.

Risks and test signals: incorrect reexec handling can break helper subprocesses on non-Linux platforms. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_oci_worker.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_oci_worker.go

Purpose: registers and implements the Linux OCI/runc worker initializer. It selects snapshotters, applies worker flags, handles rootless and process sandbox modes, and constructs a worker backed by runc.

Important APIs and flow: init registers OCI flags and priority 0. `applyOCIFlags` applies enable/auto, labels, snapshotter, rootless, no-process-sandbox, platforms, GC thresholds, network/CNI paths, worker binary, proxy snapshotter, apparmor/SELinux, and parallelism. `ociWorkerInitializer` skips auto mode when no runc/buildkit-runc exists, parses user remapping, builds resolver/session-aware snapshotter factory, validates unsafe no-process-sandbox requires rootless, builds DNS/CDI/network/parallelism options, calls `runc.NewWorkerOpt`, attaches GC policy/version/registry hosts/platforms, and creates a base worker.

State and persistence: worker state lives under daemon root with chosen snapshotter (`native`, `overlayfs`, `fuse-overlayfs`, `stargz`, or proxy). Stargz setup persists filesystem/snapshotter state and uses session-aware resolver labels. User remap can alter state compatibility.

Dependencies and risks: depends on Linux-only containerd snapshotters, fuse-overlayfs, stargz, network providers, semaphores, userns, resolver/session manager, and runc worker. Risks include snapshotter auto-detection, unsafe process sandbox mode, rootless requirements, typo-prone CNI flag application, and proxy snapshotter socket validation. Direct tests are absent in this group.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_oci_worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_test.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_test.go

Purpose: unit-tests the `--proxy-network` main daemon flag override behavior.

Important functions and flow: `TestApplyMainFlagsProxyNetwork` starts from empty config and confirms `--proxy-network` sets `cfg.ProxyNetwork` true. `TestApplyMainFlagsProxyNetworkOverridesConfig` starts from true config and confirms `--proxy-network=false` overrides it to false. `runApplyMainFlags` builds a minimal urfave CLI command with only that flag and invokes `applyMainFlags`.

State and dependencies: no persistence; tests mutate in-memory config structs. Dependencies are config package, urfave/cli, context, and testify.

Risks and test signals: this protects a subtle cli v3 bool flag override case where false values must override config. It does not test the rest of `applyMainFlags`, listener creation, TLS, rootless, or worker flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_unix.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_unix.go

Purpose: supplies Unix-specific listener, umask, and security descriptor behavior for buildkitd.

Important APIs and flow: init sets process umask to zero and marks fsutil copy accordingly. `listenFD` consumes systemd socket activation listeners, optionally wrapping them with TLS, returns the first listener by default, and rejects explicit fd selection. `getLocalListener` creates a Unix listener through containerd sys helpers and chmods it to `0666`. `groupToSecurityDescriptor` is a no-op on Unix.

State and dependencies: mutates process umask and Unix socket file mode. Depends on systemd activation, containerd sys local listener helpers, filesystem chmod, TLS, and fsutil copy.

Risks and test signals: permissive socket chmod is intentional but security-sensitive and relies on listener path placement. Systemd fd selection is not implemented beyond default first fd. There are no direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_windows.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/main_windows.go

Purpose: supplies Windows named-pipe listener and security descriptor behavior for buildkitd.

Important APIs and flow: `listenFD` rejects fd activation on Windows. `getLocalListener` creates a winio named pipe, defaulting to authenticated users and system read/write access when no descriptor is supplied. `groupToSecurityDescriptor` builds an SDDL string granting administrators and system full access plus read/write access for comma-separated group SIDs resolved by name.

State and dependencies: named-pipe security controls daemon access. Depends on go-winio, Windows-specific blank imports needed by BuildKit, TLS type signatures, and SDDL/SID handling.

Risks and test signals: malformed group names fail daemon startup; overly broad descriptors can expose the daemon. There are no direct tests in this subset for descriptor generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/main_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/service_unix.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/service_unix.go

Purpose: provides no-op service-management hooks on non-Windows builds so the cross-platform main daemon code can call service helpers uniformly.

Important APIs and flow: `serviceFlags` returns no flags, `applyPlatformFlags` does nothing, `registerUnregisterService` returns `(false, nil)`, and `launchService` returns nil.

State and dependencies: no state or persistence. Depends only on urfave/cli and gRPC types to match the shared signatures.

Risks and test signals: low-risk shim; incorrect behavior would unexpectedly stop or alter daemon startup on Unix. There are no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/service_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/service_windows.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/service_windows.go

Purpose: implements Windows Service Control Manager integration for buildkitd, including service registration/unregistration, service-mode logging/stderr redirection, panic file handling, and graceful gRPC server control.

Important APIs and flow: `serviceFlags` exposes service name, register/unregister, hidden run-service, and log-file flags. `registerService` creates an automatic service with restart failure actions and reuses current args minus registration flags. `unregisterService` deletes the service. `applyPlatformFlags` stores global flag values. `registerUnregisterService` handles early register/unregister, service-mode detection, log directory creation, panic file setup, stderr redirection, and logrus output. `launchService` starts service handling when `--run-service` is set. `handler.Execute` responds to SCM stop/shutdown by stopping the gRPC server. `initPanicFile` and `removePanicFile` manage a marker for unexpected crashes.

State and persistence: mutates Windows SCM service definitions, writes log and panic files under daemon root or requested log path, redirects process stderr, and controls server lifecycle.

Risks and test signals: service registration requires privileges and unsafe Windows API calls for failure actions/stderr handles. Panic marker correctness affects diagnostics. No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/service_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/util.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/util.go

Purpose: provides daemon utility helpers for GC flag formatting/parsing and provenance environment loading.

Important APIs and flow: `gcConfigToString` converts `GCConfig` thresholds to legacy comma-separated MB flag text by evaluating disk percentages against current disk stats. `int64ToString` formats integer slices. `stringToGCConfig` parses `Reserved[,Free[,Maximum]]` MB values into `config.DiskSpace` byte fields. `loadProvenanceEnv` reads `.json` files from a configured or default provenance directory, unmarshals each into a shared map, and returns nil when the directory is absent.

State and dependencies: reads provenance JSON from disk and disk stats for formatting; no writes. Depends on appdefaults, config types, disk stats, JSON, filesystem traversal, and error wrapping.

Risks and test signals: provenance JSON files merge into one map, so later files can overwrite earlier keys depending on directory order. GC string parsing accepts only integer MB values. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/util_linux.go -->
# Research: sources/cloud-native/buildkit/cmd/buildkitd/util_linux.go

Purpose: implements Linux user namespace remap parsing for the OCI worker's experimental `UserRemapUnsupported` config.

Important API and flow: `parseIdentityMapping` returns nil for an empty string, otherwise splits at most three colon components, rejects too many components, treats the first component as a username, logs the selected subuid owner, loads identity mappings through `moby/sys/user`, and returns them.

State and dependencies: reads system subuid/subgid mapping state through user helpers. It depends on BuildKit logging and error wrapping.

Risks and test signals: comments in the caller warn that changing this should not mutate existing state directories because mappings affect ownership compatibility. The parser ignores fields after the first colon except for rejecting excess parts. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/cmd/buildkitd/util_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/codecov.yml -->
# Research: sources/cloud-native/buildkit/codecov.yml

Purpose: configures Codecov reporting behavior for the BuildKit repository.

Important settings: pull-request comments are disabled. Project coverage uses an automatic target with a 1% threshold. Patch coverage status is disabled. GitHub check annotations are disabled. Generated protobuf files matching `**/*.pb.go` are ignored.

State and dependencies: this is CI configuration consumed by Codecov, not runtime BuildKit code. It affects repository coverage gates and reporting noise.

Risks and test signals: disabling patch status and annotations reduces friction but can hide localized coverage regressions. Ignoring generated protobuf files is appropriate because generated code would distort coverage. There are no local tests for this YAML.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/log.go -->
# Research: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/log.go

Purpose: adapts command stdout/stderr bytes from NVIDIA CDI setup into BuildKit progress logs.

Important APIs and flow: `newStream` returns a `streamWriter` bound to a progress writer, stream number, and vertex digest. `streamWriter.Write` emits a `client.VertexLog` with timestamp, stream, byte payload, and vertex digest, then returns the full write length.

State and dependencies: no persistence; it writes progress events into the active setup context. Depends on BuildKit progress writer, `client.VertexLog`, time stamps, and digest identifiers.

Risks and test signals: this writer assumes progress writes do not need partial-write semantics; it reports success after emitting a log event. There are no direct tests, but it is used by NVIDIA setup command execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/nvidia.go -->
# Research: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/nvidia.go

Purpose: experimental on-demand CDI setup for NVIDIA GPUs. It validates host GPU/driver availability, installs NVIDIA container toolkit components on Debian/Ubuntu, and writes a generated CDI spec.

Important APIs and flow: init registers `nvidia.com/gpu`. `Validate` succeeds if driver version is readable or PCI/WSL GPU devices are found. `newVertex` creates progress vertices. `Run` checks OS release, detects driver/library needs, runs `apt-get update`, installs `gpg`, configures NVIDIA apt repository, installs toolkit and optional driver-library packages, runs `nvidia-ctk cdi generate`, and writes `/etc/cdi/nvidia.yaml`. Helpers run commands with progress streams, parse `/proc/driver/nvidia/version`, scan PCI vendor IDs, read `/etc/os-release`, detect WSL GPU, and glob libcuda paths.

State and persistence: mutates host/package state through apt, writes `/usr/share/keyrings/nvidia-cuda-keyring.gpg`, `/etc/apt/sources.list.d/nvidia-cuda.list`, and `/etc/cdi/nvidia.yaml`. It reads `/proc`, `/sys`, `/etc/os-release`, and library paths.

Dependencies and risks: depends on Debian/Ubuntu apt, network access to NVIDIA repository, root privileges, gpg, nvidia-ctk, kernel driver state, and BuildKit progress. It is explicitly experimental and not normally shipped. Tests cover version parsing only; setup side effects are not integration-tested here.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/nvidia.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/nvidia_test.go -->
# Research: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/nvidia_test.go

Purpose: unit-tests NVIDIA driver version parsing for two observed `/proc/driver/nvidia/version` formats.

Important flow: `TestParseVersion` passes classic UNIX kernel module text and newer open kernel module text to `parseVersion`, asserting extracted major.minor strings `550.120` and `550.144`.

State and dependencies: no filesystem or package-manager side effects. It depends on testify assertions.

Risks and test signals: the test protects the regex used to choose matching driver-library package names. It does not test validation, apt repository setup, package installation, WSL detection, PCI scanning, or CDI YAML generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/nvidia_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/venus/venus_unix.go -->
# Research: sources/cloud-native/buildkit/contrib/cdisetup/venus/venus_unix.go

Purpose: implements experimental on-demand CDI setup for Docker Desktop Virtio-GPU Venus devices on non-Windows platforms.

Important APIs and flow: init registers `docker.com/gpu`. `Validate` gets the kernel version, requires it to contain `linuxkit`, checks `/dev/dri`, and requires `renderD128` and `card0`. `Run` validates again, writes a fixed CDI YAML spec naming device `venus` with those DRI device nodes, and creates `/etc/cdi` as needed. `getKernelVersion` calls `unix.Uname` and trims the NUL-terminated release string.

State and persistence: reads kernel/device files and writes `/etc/cdi/venus.yaml` with mode 0600. Depends on CDI setup registration, unix uname, and filesystem state.

Risks and test signals: validation is tightly coupled to Docker Desktop/LinuxKit device naming and will reject other Virtio-GPU environments. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/venus/venus_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/venus/venus_windows.go -->
# Research: sources/cloud-native/buildkit/contrib/cdisetup/venus/venus_windows.go

Purpose: provides an empty Windows package stub for the Venus CDI setup package.

Important behavior: the file only declares `package venus`; no registration or setup code is compiled for Windows.

State and dependencies: no state, imports, or side effects.

Risks and test signals: this prevents Unix-specific device probing and `/etc/cdi` writes on Windows, but also means the `venus` build tag import has no setup effect there. No tests are needed beyond successful Windows compilation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/contrib/cdisetup/venus/venus_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/control/control.go -->
# Research: sources/cloud-native/buildkit/control/control.go

Purpose: implements the BuildKit control gRPC service, bridging daemon subsystems to client APIs for solve, status, sessions, disk usage, prune, workers, info, history, trace export, content reads, and gateway forwarding.

Important APIs and flow: `Opt` injects session manager, worker controller, frontends, cache manager/resolvers, entitlements, trace collector, meter provider, history/cache/content stores, lease manager, history config, proxy network, GC callback, graceful stop, and provenance env. `NewController` creates a gateway forwarder, history queue, LLB solver, throttled GC/release callbacks, and optional trace forwarder. `Register` registers control, gateway, trace, and read-only content services. RPCs include `DiskUsage`, `Prune`, `Export`, history listen/update, legacy solve request translation, `Solve`, `Status`, `Session`, `ListWorkers`, and `Info`.

State and persistence: owns long-lived solver, history queue over Bolt DB, cache store, worker controller, trace forwarder, and content-store fallback namespace. It triggers GC and cache metadata release, mutates history records, and streams session connections.

Dependencies and integration: integrates gRPC APIs, LLB solver, workers, exporters, remote cache import/export, attestations/SBOM/provenance processors, entitlements, sessions, history, cache stores, tracing, content services, and BuildKit versioning.

Risks and test signals: solve is high-risk because it validates compatibility, deduplicates cache exports, configures exporters/processors, applies entitlements/source policy/proxy network, and handles sessions. `control_test.go` covers duplicate cache option handling and ignore-error parsing; broad behavior depends on integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/control/control.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/control/control_test.go -->
# Research: sources/cloud-native/buildkit/control/control_test.go

Purpose: unit-tests helper logic used by the control service solve path for cache exporter deduplication and cache export ignore-error parsing.

Important flow: `TestDuplicateCacheOptions` covers unique registry/local cache exports, duplicate registry/local entries, and special inline handling that keeps only the first inline exporter even with attrs. It asserts both duplicate lists and rest lists. `TestParseCacheExportIgnoreError` checks accepted bool spellings and unsupported malformed strings.

State and dependencies: no persistence; tests use in-memory protobuf cache option structs and testify assertions.

Risks and test signals: these helpers guard user-facing solve validation. Duplicate detection affects whether solves are rejected, and inline handling is intentionally permissive. The tests do not cover `cacheOptKey` hash failures or full solve integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/control/control_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/control/gateway/gateway.go -->
# Research: sources/cloud-native/buildkit/control/gateway/gateway.go

Purpose: implements a gRPC gateway bridge forwarder that routes frontend gateway API calls to the active build's registered `LLBBridgeForwarder` based on build ID in the incoming context.

Important APIs and flow: `GatewayForwarder` wraps a generic registrar keyed by build ID. `Register` registers the LLBBridge gRPC server. `RegisterBuild` and `UnregisterBuild` manage active build forwarders. `lookupForwarder` extracts build ID from context and waits/looks up the matching forwarder, converting canceled lookups into unknown-job errors. All gateway RPC methods call `lookupForwarder` and delegate directly: image/source resolution, solve, file and container filesystem operations, evaluate, ping, return, inputs, new/release container, exec process stream, and warnings.

State and dependencies: state is the registrar of active build IDs to forwarders. It depends on buildid context propagation, frontend gateway interfaces/protobufs, registrar synchronization, errdefs, and gRPC registration.

Risks and test signals: missing or stale build IDs produce wrapped forwarding errors; unregister timing must align with build lifecycle to avoid unknown-job failures. There are no direct tests in this subset, so coverage is mostly through gateway frontend integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/control/gateway/gateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/doc.go -->
# Research: sources/cloud-native/buildkit/doc.go

Purpose: declares the root `buildkit` package for repository-level Go documentation/package identity.

Important behavior: the file contains only `package buildkit`, with no exported symbols, runtime control flow, state, imports, or side effects.

State and dependencies: none. It exists so the module root can compile as a Go package when needed.

Risks and test signals: low risk; changes would only affect package naming or documentation tooling. Successful `go list`/package compilation is the relevant signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/docs/generate.go -->
# Research: sources/cloud-native/buildkit/docs/generate.go

Purpose: updates generated command-output blocks in markdown files under `./docs`. It is a documentation maintenance tool, not runtime daemon code.

Important APIs and flow: `main` compiles a regexp matching `<!---GENERATE_START command-->...<!---GENERATE_END-->` blocks, opens `./docs` as an `os.Root`, walks markdown files, replaces each block by running `/bin/sh -c <command>` and embedding stdout in fenced code, writes changed files with original mode, prints changed paths, and exits nonzero on errors.

State and dependencies: reads and writes documentation files and executes shell commands embedded in docs. Depends on `os.OpenRoot`, `fs.WalkDir`, regexp replacement, `os/exec`, and error wrapping.

Risks and test signals: commands embedded in docs execute with shell privileges, so this tool must only run on trusted docs. Replacement captures stdout only; command errors are stored in the outer `err` and reported after traversal. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/docs/generate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/errdefs/internal.go -->
# Research: sources/cloud-native/buildkit/errdefs/internal.go

Purpose: defines BuildKit's internal/system error marker and helpers for classifying syscall failures as internal or resource-exhaustion errors.

Important APIs and flow: `internalError` wraps an error and implements `System()`. `Internal` wraps non-nil errors. `IsInternal` returns true for errors implementing `System()` or syscall errno values known by `isInternalSyscall`. `IsResourceExhausted` returns true only for known syscall errors marked resource-exhaustion. `isInternalSyscall` delegates to platform-specific `syscallErrors`.

State and dependencies: no persistence. Depends on Go error wrapping/as semantics and syscall errno values supplied by OS-specific files.

Risks and test signals: classification affects retry/reporting semantics across BuildKit. Non-Linux builds return no syscall map, so only explicit internal wrappers match. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/errdefs/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/errdefs/internal_linux.go -->
# Research: sources/cloud-native/buildkit/errdefs/internal_linux.go

Purpose: provides Linux syscall errno classification for internal/system errors.

Important API: `syscallErrors` returns a map marking `EIO`, `EFAULT`, `ENOTRECOVERABLE`, and `EHWPOISON` as internal non-resource-exhaustion, while `ENOMEM` and `ENOSPC` are internal resource-exhaustion.

State and dependencies: no persistence or runtime state. Depends on `golang.org/x/sys/unix` errno constants and syscall types.

Risks and test signals: the map defines which low-level failures are treated as infrastructure/system problems. Over-classification can hide user errors; under-classification can reduce diagnostic quality. No direct tests are listed.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/errdefs/internal_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/errdefs/internal_nolinux.go -->
# Research: sources/cloud-native/buildkit/errdefs/internal_nolinux.go

Purpose: supplies the non-Linux implementation of syscall internal-error classification.

Important behavior: `syscallErrors` returns nil, so platform errno values are not automatically considered internal/resource-exhaustion on non-Linux builds.

State and dependencies: no state; imports only `syscall` for signature compatibility.

Risks and test signals: non-Linux platforms rely on explicit `Internal` wrapping instead of errno classification, which may produce different diagnostics from Linux. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/errdefs/internal_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/build-using-dockerfile/main.go -->
# Research: sources/cloud-native/buildkit/examples/build-using-dockerfile/main.go

Purpose: example CLI that mimics a small subset of `docker build` by using BuildKit to build a Dockerfile and load the result into Docker. It is explicitly not a production replacement.

Important APIs and flow: `main` defines flags for build args, Dockerfile path, tag, target, no-cache, BuildKit address, and optional client-side frontend. `action` requires a tag, creates a BuildKit client, builds a `SolveOpt`, runs either `client.Build` with client-side Dockerfile frontend or daemon `Solve`, displays progress, and pipes docker exporter output to `docker load`. `newSolveOpt` maps context and Dockerfile directories to fsutil local mounts, sets frontend attrs, build args, no-cache, and docker exporter output writer. `loadDockerTar` shells out to `docker load`.

State and dependencies: reads local build context/Dockerfile, streams image tar, and mutates local Docker image store via `docker load`. Depends on BuildKit client, Dockerfile builder, fsutil, progress UI, errgroup, and external Docker CLI.

Risks and test signals: the example has limited flag compatibility and no stdin context support. External Docker and daemon availability are required. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/build-using-dockerfile/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildctl-daemonless/buildctl-daemonless.sh -->
# Research: sources/cloud-native/buildkit/examples/buildctl-daemonless/buildctl-daemonless.sh

Purpose: BusyBox-compatible wrapper that launches an ephemeral buildkitd, waits for it to become reachable, runs `buildctl`, then cleans up the daemon and temp directory.

Important flow: configurable environment variables choose `BUILDCTL`, retry count, `BUILDKITD`, `BUILDKITD_FLAGS`, and `ROOTLESSKIT`. The script creates a temp dir containing pid/addr/log, traps exit to kill/wait/remove, starts buildkitd on `/run/buildkit/buildkitd.sock` as root or `$XDG_RUNTIME_DIR/buildkit/buildkitd.sock` under rootlesskit as non-root, polls `buildctl --addr=$addr debug workers` with backoff, dumps daemon log on failure, and finally execs the requested buildctl command against the address.

State and dependencies: creates temporary files and a daemon process; buildkitd creates its own state according to flags/defaults. Depends on sh, mktemp, id, awk, expr, rootlesskit for non-root, buildkitd, and buildctl.

Risks and test signals: cleanup assumes pid file exists and kill is acceptable. Readiness probing depends on `debug workers`. No direct shell tests are listed.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildctl-daemonless/buildctl-daemonless.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit0/buildkit.go -->
# Research: sources/cloud-native/buildkit/examples/buildkit0/buildkit.go

Purpose: first LLB example for constructing a BuildKit image from source using imperative copy helper patterns. It writes the resulting LLB definition to stdout.

Important APIs and flow: flags choose whether to include containerd plus runc/containerd versions. `goBuildBase` builds a Go Alpine state with build dependencies. `runc` and `containerd` clone upstream repos, checkout versions, and compile binaries. `buildkit` clones BuildKit, builds `buildkitd` and `buildctl`, starts from Alpine, copies binaries and optionally containerd in. `copy` uses an Alpine `cp -a` run with source/destination mounts. `main` marshals the final state after a debug `ls -l /bin` run.

State and dependencies: no local persistence except stdout LLB; build state references remote Git repos and images when solved. Depends on LLB DSL and system path helpers.

Risks and test signals: it is an example with hard-coded versions and remote repositories. The cp-based copy helper is less idiomatic than later examples. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit0/buildkit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit1/buildkit.go -->
# Research: sources/cloud-native/buildkit/examples/buildkit1/buildkit.go

Purpose: second LLB example that refactors source checkout and copy behavior into reusable `StateOption` helpers while building a BuildKit image.

Important APIs and flow: `goFromGit` clones a repository into a temporary Alpine/git state, checks out a tag/ref, copies `/go` into the destination Go build state, and asynchronously sets the working directory to the copied repo. `copyFrom` composes copy behavior as a state option. `runc`, `containerd`, and `buildkit` use these helpers to build binaries and assemble an Alpine image. `main` marshals the graph to stdout after a debug listing run.

State and dependencies: output is LLB only; solve-time state pulls images and Git repositories. Depends on LLB async state options, Git, Go build images, and fs copy via `cp`.

Risks and test signals: async `GetDir`/`Reset` usage is more advanced and could be confusing or fragile if LLB APIs change. No direct tests are included.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit1/buildkit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit2/buildkit.go -->
# Research: sources/cloud-native/buildkit/examples/buildkit2/buildkit.go

Purpose: third LLB example that uses `llb.Git` directly as mounted source input instead of shelling out to git clone. It demonstrates cleaner source mounting and scratch output directories.

Important APIs and flow: `goRepo` returns a runner function that sets the working directory, mounts `llb.Git(repo, ref, options...)` at the repo path, and mounts a scratch `bin` directory for outputs. `runc`, `containerd`, and `buildkit` compile into repo-local `bin`. `copyAll` and `copyFrom` copy output trees into an Alpine result using the cp helper. `main` marshals a debug-listing state to stdout.

State and dependencies: no local persistence; solve-time fetches images and Git refs. Depends on LLB Git source operations, run mounts, and Go build commands.

Risks and test signals: remote refs and command paths are hard-coded and example-oriented. Containerd path uses module-style repo path and `KeepGitDir`. There are no direct tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit2/buildkit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit3/buildkit.go -->
# Research: sources/cloud-native/buildkit/examples/buildkit3/buildkit.go

Purpose: fourth LLB example that adds local-source support and uses native `llb.Copy` file operations instead of shell-based copy runs. It builds a scratch image containing BuildKit, runc, and optional containerd binaries.

Important APIs and flow: flags include buildkit/containerd/runc versions, with `"local"` selecting `llb.Local` sources. `goRepo` mounts the chosen source read-only and a scratch `/out`. `runc`, `containerd`, and `buildkit` compile binaries to `/out`. `buildkit` assembles a scratch state with `copyAll`. `copy` uses `dest.File(llb.Copy(..., AllowWildcard, AttemptUnpack, CreateDestPath))`, showing modern LLB copy semantics. `main` marshals the final state to stdout.

State and dependencies: output is serialized LLB; solve-time state may read local named contexts (`runc-src`, `containerd-src`, `buildkit-src`) or remote Git. Depends on LLB file operations and system path helper.

Risks and test signals: local source names must be provided by the solve client when using `"local"`. This example is not unit-tested, but it demonstrates a safer copy primitive than prior examples.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/examples/buildkit3/buildkit.go -->
