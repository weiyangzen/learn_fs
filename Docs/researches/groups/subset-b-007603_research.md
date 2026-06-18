# subset-b-007603 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/gateway_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/gateway_test.go

Purpose: integration coverage for Kubo HTTP gateway, API HTTP edge cases, pprof controls, gateway config flags, IPNS resolution through the gateway, and streaming logs. It exercises a real test daemon through `harness.NewT`, `Node.Init`, `StartDaemon`, `GatewayClient`, and `APIClient`.

Important APIs/functions: `TestGateway` is a large parallel subtest tree; `TestLogs` separately verifies `/logs` streaming with `GOLOG_LOG_LEVEL=info`. Test data is created through `IPFSAddStr`, recursive `ipfs add`, raw `block put`, `name publish`, and direct config mutation through `UpdateConfig`.

Control flow: the main node starts offline for deterministic local gateway tests, then nested subtests request `/ipfs`, `/ipns`, `/webui`, `/api/v0/version`, `/debug/pprof-*`, and content-negotiated trustless gateway paths. Other subtests create fresh nodes for pprof, content-type, fixed gateway-address, `NoFetch`, `DeserializedResponses`, and `DisableHTMLErrors` scenarios.

State and persistence: writes temporary files, imports blocks into the repo, publishes IPNS records, mutates gateway/API config, and checks generated `gateway` repo file contents. Daemons are stopped via cleanup.

Dependencies/integration: uses Kubo config structs, libp2p peer CIDs, multibase base36, multiaddr conversion, HTTP clients, and testify assertions. It directly validates gateway behavior exposed by the CLI daemon and gateway server.

Risks: heavy `t.Parallel` sharing around one gateway client can expose redirect-client mutation hazards; fixed port `32563` may collide; output parsing of daemon stdout and CID list ordering is brittle. Test signals are status codes, headers, body bytes, JSON version fields, pprof methods, file contents, and streamed log lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/gateway_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/buffer.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/buffer.go

Purpose: provides `Buffer`, a concurrency-safe output sink for subprocess stdout/stderr captured by the CLI harness.

Important APIs/types/functions: `Buffer` wraps a `strings.Builder` and `sync.Mutex`. It implements `Write(p []byte)`, `String()`, `Trimmed()`, `Bytes()`, and `Lines()`. `Lines` delegates line splitting to `testutils.SplitLines`.

Control flow: process runners write concurrently into the buffer through `Write`; readers acquire the same mutex and snapshot the builder contents. `Trimmed` removes at most one trailing newline, preserving other whitespace for exact-output assertions.

State and persistence: state is in-memory only. There is no file or repo persistence; the buffer stores subprocess output for the lifetime of a harness command result.

Dependencies/integration: integrated by `Runner.Run` as the default stdout/stderr capture target and by tests that inspect `RunResult.Stdout`/`Stderr`.

Risks: `strings.Builder` contents are copied into byte slices and strings on read, so very large command output can allocate. `Trimmed` only handles `\n`, not `\r\n`, which may matter on Windows-style output. Test signals are exact output comparisons, line parsing, and error diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/dht_stub_peers.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/dht_stub_peers.go

Purpose: supplies in-process loopback libp2p DHT peers so tests can exercise provider records without the public DHT.

Important APIs/types/functions: `stubPeerPool` owns libp2p hosts, DHT instances, a shared `records.ProviderStore`, and a cancel function. `newStubPeerPool(count)` creates server-mode DHT peers, full-mesh connects them, and shares `sharedMemStore`. `Close` tears down hosts and DHTs. `sharedMemStore` implements `AddProvider`, `GetProviders`, and `Close`.

Control flow: harness code lazily creates a pool, injects peer multiaddrs into node bootstrap config, and sets `TEST_DHT_STUB`. Kubo daemons send real DHT messages over loopback; provider records are accumulated in the shared in-memory map keyed by hex-encoded record key.

State and persistence: all provider state is in memory and disappears on cleanup. The only persistent effect is node config bootstrap mutation performed by the caller.

Dependencies/integration: depends on go-libp2p, go-libp2p-kad-dht, peer IDs, DHT provider-store interfaces, and harness cleanup.

Risks: full-mesh connection cost grows quadratically; stale peers can leak ports if cleanup is skipped. The fixed `stubDHTPeerCount` of 20 is tied to Kademlia bucket assumptions. Test signal is whether provider discovery works locally in DHT-dependent CLI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/dht_stub_peers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/harness.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/harness.go

Purpose: top-level test harness for Kubo CLI integration tests. It creates temporary workspaces, locates the built `cmd/ipfs/ipfs` binary, manages nodes, temp files, shell execution, stub DHT bootstrap, and cleanup.

Important APIs/types/functions: `Harness` stores `Dir`, `IPFSBin`, `Runner`, `NodesRoot`, `Nodes`, and optional `stubPeers`. `NewT` registers cleanup with testing, `New` initializes paths, `BootstrapWithStubDHT` wires local DHT peers, `NewNode`/`NewNodes` allocate repos, `WriteToTemp`, `TempFile`, `WriteFile`, `Mkdirs`, `WaitForFile`, `Sh`, `Cleanup`, and `ExtractPeerID` support tests.

Control flow: `New` walks up to `go.mod`, sets the binary path, creates a temp root, and applies options. Node creation delegates to `BuildNode`. Cleanup stops all daemons, closes stub peers, and removes temp dirs.

State and persistence: all state lives under a temporary directory and node repo directories. Cleanup is destructive for the harness temp root.

Dependencies/integration: imports Kubo testutils, go-log, libp2p peer IDs, and multiaddr. It is the primary integration point used by almost every CLI test in this subset.

Risks: `osEnviron` splits on every `=`, which can truncate env values containing `=`. `h.stubPeers.Close()` is called without a nil guard at the call site, relying on the method receiver check. Test signals are clean temp setup, successful command runs, and daemon teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/harness.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/http_client.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/http_client.go

Purpose: small HTTP testing wrapper for Kubo gateway/API requests with template-expanded paths and buffered responses.

Important APIs/types/functions: `HTTPClient` contains an underlying `*http.Client`, `BaseURL`, optional `Timeout`, and `TemplateData`. `HTTPResponse` exposes body, status, headers, and raw response. Methods include `WithHeader`, `DisableRedirects`, `Do`, `BuildURL`, `Get`, `Post`, `PostStr`, and `Head`.

Control flow: request helpers build URLs by executing a Go `text/template` against `TemplateData`, prepend `BaseURL`, apply request mutators, then call `Do`. `Do` executes the request, closes the body, reads it fully, and returns a structured response.

State and persistence: no persistent state, but `DisableRedirects` mutates the shared `http.Client.CheckRedirect`, so the redirect behavior can affect later requests using the same client.

Dependencies/integration: used by `Node.GatewayClient` and `Node.APIClient`; integrates with Go `net/http` and template rendering.

Risks: the `Timeout` field is unused; global `http.DefaultClient` reuse plus `DisableRedirects` mutation can make parallel tests interdependent. Full body buffering is convenient but unsuitable for large streams except where tests use raw `http.Client` directly. Test signals are status, headers, and body string assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/http_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/ipfs.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/ipfs.go

Purpose: convenience methods on `Node` for common `ipfs` CLI operations and config mutation.

Important APIs/functions: `IPFSCommands`, `SetIPFSConfig`, `GetIPFSConfig`, `IPFSAddStr`, `IPFSAddDeterministic`, `IPFSAddDeterministicBytes`, `IPFSAdd`, `IPFSBlockPut`, `IPFSDAGPut`, `IPFSDagImport`, and `IPFSDagExport`.

Control flow: helpers assemble CLI args, pipe readers to stdin when needed, run commands through `Runner.MustRun`, trim CIDs from stdout, and validate config writes by reading back JSON into a value of the same type. DAG import verifies success by checking `block stat --offline` for the expected root CID.

State and persistence: operations mutate the node repo by writing config, adding blocks, importing CARs, and exporting CAR files. Deterministic random readers make CIDs reproducible across tests.

Dependencies/integration: uses Kubo testutils for random data and line splitting, JSON reflection for config verification, and the process runner for CLI execution.

Risks: reflection-based config comparison can be sensitive to JSON number types and nil representation. `IPFSDagImport` uses `MustRun`, so command errors panic before returned errors are useful. Test signals are returned CIDs, successful config round trips, and block availability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/ipfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/log.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/log.go

Purpose: buffered hierarchical logger for tests that only prints on failure or explicit enablement, keeping verbose `go test` output readable.

Important APIs/types/functions: `event`, sortable `events`, and `TestLogger`. `NewTestLogger` registers cleanup. `Log`, `Logf`, `Fatal`, `Fatalf`, `AddPrefix`, `EnableLogs`, and `flush` manage buffered log events.

Control flow: log methods timestamp and annotate entries with caller file/line plus prefixes, then append under a mutex. Child loggers register their own cleanup; because testing cleanup runs LIFO, children flush into parents before the root sorts and prints.

State and persistence: in-memory event buffers only. Output is printed to stdout during cleanup if the test failed or logging was enabled.

Dependencies/integration: depends on `testing.T`, runtime caller metadata, sorting, and synchronization. It is a harness utility rather than daemon log capture.

Risks: `EnableLogs` has confusing parent recursion and prints diagnostic “enabling children” text itself. Caller depth is fixed and may point at helper internals after wrapper changes. Test signals are failure-time logs and prefixed contextual events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/node.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/node.go

Purpose: core harness abstraction for a single Kubo repo and daemon. It owns process execution, repo config, daemon lifecycle, API readiness, swarm connectivity, gateway/API clients, and offline datastore helpers.

Important APIs/types/functions: `Node`, `BuildNode`, file/config helpers, `IPFS`/`RunIPFS`/pipe variants, `Init`, `StartDaemonWithReq`, `StartDaemon`, `StopDaemon`, `APIAddr`, `APIURL`, `checkAPI`, `PeerID`, `WaitOnAPI`, `IsAlive`, swarm address/connection helpers, `PeerWith`, `Disconnect`, `GatewayURL`, client constructors, and datastore diagnostics.

Control flow: `BuildNode` creates `IPFS_PATH` and runner env. `Init` runs `ipfs init` and rewrites config for local random ports, disabled bootstrap, disabled telemetry, mDNS choice, and test routing behavior. `StartDaemonWithReq` starts `ipfs daemon`, stores the process result, then polls `/api/v0/id`. Shutdown escalates from SIGTERM to SIGQUIT/SIGKILL with Windows handling.

State and persistence: each node has a repo directory containing config, version, api/gateway files, datastore, blocks, and optional resource-manager overrides. Daemon state is a running OS process.

Dependencies/integration: uses Kubo config serialization, libp2p peer IDs, multiaddr/manet conversion, HTTP API checks, and the harness `Runner`.

Risks: many methods panic on errors, which is intentional for tests but reduces recoverability. `ExitCode` assumptions can break for still-running processes. Swarm connect methods sometimes ignore failures for resilience, which can hide setup issues. Test signals are API id responses, peer IDs, swarm peers, gateway file URLs, and datastore command output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/nodes.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/nodes.go

Purpose: collection helpers for operating on multiple `Node` instances in integration tests.

Important APIs/types/functions: `Nodes` is `[]*Node`. Methods include `Init`, `ForEachPar`, `Connect`, `StartDaemons`, and `StopDaemons`.

Control flow: initialization and daemon start/stop are parallelized with goroutines and a wait group. `Connect` intentionally connects nodes serially to avoid TLS handshake problems, then verifies each node has at least one peer address with a peer ID.

State and persistence: mutates every node repo and daemon process through delegated `Node` methods. No separate persistence exists in the collection.

Dependencies/integration: relies on `Node` methods, `testutils.ForEachPar` for initialization, sync wait groups, multiaddr peer-ID parsing, and harness logging.

Risks: `Connect` assumes `node.Peers()[0]` exists and will panic if peer setup silently failed. Parallel start/stop increases speed but can expose shared binary or port races. Test signals are successful multi-node daemon startup and peer table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/nodes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/pbinspect.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/pbinspect.go

Purpose: low-level UnixFS and DAG-PB inspection helpers for tests that need to assert internal block structure rather than CLI text.

Important APIs/types/functions: `UnixFSDataType`, `UnixFSHAMTFanout`, `InspectPBNode`, and JSON structs `PBHash`, `PBLink`, `PBData`, `PBNode`.

Control flow: data-type and fanout helpers run `ipfs block get`, parse the dag-pb bytes with `merkledag.DecodeProtobuf`, then parse UnixFS data with `FSNodeFromBytes`. `InspectPBNode` runs `ipfs dag get --output-codec=dag-json`, unmarshals logical DAG-PB JSON, and returns a typed view of links/data.

State and persistence: read-only against the node blockstore. It uses buffers but does not mutate the repo.

Dependencies/integration: depends on Boxo merkledag/unixfs packages, protobuf UnixFS enums, JSON, and the harness runner.

Risks: `MustRun` panics before returned errors can be inspected. The JSON struct mirrors a specific dag-json logical shape, so codec output changes may break callers. Test signals are UnixFS type enum, HAMT fanout, link CIDs/names/sizes, and data bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/pbinspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/peering.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/peering.go

Purpose: helpers for constructing peered node topologies with deterministic local listen ports.

Important APIs/types/functions: `Peering{From, To}` describes config-level peering edges. `NewRandPort` allocates unique TCP ports with a process-wide map and mutex. `CreatePeerNodes` creates a harness, initializes nodes, disables routing, assigns local swarm ports, and applies peering config edges.

Control flow: port allocation first asks the OS for an available port, records it, and falls back to random ports in the 30000-39999 range. Node config updates run in parallel, then requested `PeerWith` relationships are applied.

State and persistence: global `allocatedPorts` tracks ports for the test process. Node configs persist routing type, swarm addresses, and peering entries in repo config files.

Dependencies/integration: uses Go networking, Kubo config structs, `testing.T`, and harness `Node` configuration helpers.

Risks: a port can be allocated then taken by another process before daemon bind. The global map never releases ports, acceptable for tests but long-lived. Test signals are successful daemon startup and expected peering behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/peering.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/run.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/harness/run.go

Purpose: process execution layer for the CLI harness, with captured output, environment injection, and command customization.

Important APIs/types/functions: `Runner`, `CmdOpt`, `RunFunc`, `RunRequest`, `RunResult`, `ExitCode`, `environToMap`, `Run`, `MustRun`, `AssertNoError`, and command options `RunWithEnv`, `RunWithPath`, `RunWithStdin`, `RunWithStdinStr`, `RunWithStdout`, `RunWithStderr`.

Control flow: `Run` creates `exec.Command`, attaches `Buffer` captures, optionally mirrors output in verbose mode, sets working directory and env, applies options, and calls either `cmd.Run` or a custom function such as `Start`. It returns a `RunResult` with output, error, exit error, and command.

State and persistence: no persistence beyond spawned processes and their outputs. `Runner.Env` and `Dir` define command context.

Dependencies/integration: central for all `Node.IPFS`, daemon startup, and shell/build helpers.

Risks: `strings.Split` without `SplitN` can truncate env values containing `=`. `RunWithStderr` writes to `cmd.Stdout` instead of `cmd.Stderr`, likely a bug in stderr mirroring. `ExitCode` requires a populated process state and is unsafe for running started commands. Test signals are process exit status and captured stdout/stderr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/harness/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/http_gateway_over_libp2p_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/http_gateway_over_libp2p_test.go

Purpose: verifies experimental HTTP gateway over libp2p behavior using two real Kubo nodes and libp2p HTTP clients.

Important APIs/functions: `TestGatewayOverLibp2p` configures `Experimental.Libp2pStreamMounting`, later enables `Experimental.GatewayOverLibp2p`, runs `ipfs p2p forward --allow-custom-protocol /http/1.1`, parses `commands.P2PLsOutput`, and uses both ordinary HTTP and `libp2phttp.Host.NamespacedClient`.

Control flow: two nodes start and connect. One holds gateway data; another acts as HTTP-over-libp2p proxy. Before enabling the gateway feature, HTTP through the proxy is expected to fail. After restart/reconnect, tests assert remote content is not fetched, deserialized responses are rejected, and raw block responses are served through both Kubo p2p proxy and direct libp2p namespaced client.

State and persistence: mutates experimental config, adds blocks to each repo, starts p2p listeners, and restarts the gateway node.

Dependencies/integration: depends on Kubo p2p commands, go-cid, go-libp2p, libp2p HTTP transport, multiaddr conversion, and harness multi-node connectivity.

Risks: experimental flags, p2p listener parsing, and daemon restart timing make this integration-sensitive. Test signals are connection errors before enablement, HTTP status codes, and exact raw block bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/http_gateway_over_libp2p_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/http_retrieval_client_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/http_retrieval_client_test.go

Purpose: end-to-end test for HTTP-only content retrieval through delegated routing and trustless gateway block responses.

Important APIs/functions: `TestHTTPRetrievalClient`, `NewMockHTTPProviderServer`, and `splitHostPort`. The test configures `HTTPRetrieval.Enabled`, `TLSInsecureSkipVerify`, and `Routing.DelegatedRouters`, then uses a `httprouting.MockHTTPContentRouter`.

Control flow: the test computes a CID without adding data locally (`ipfs add -n`), starts an HTTPS HTTP/2 mock provider that serves `/ipfs/{cid}` with `application/vnd.ipld.raw`, registers that provider in a delegated routing server, starts Kubo, verifies `routing findprovs`, and finally runs `ipfs cat` to retrieve bytes over HTTP.

State and persistence: node config changes persist in the test repo; the actual content is intentionally not added to the local repo. Mock routing/provider state is in-memory httptest server state.

Dependencies/integration: integrates Boxo routing HTTP server/types, Kubo HTTP retrieval config, random test data, peer/multiaddr types, and harness daemon lifecycle.

Risks: depends on TLS skip verify and HTTP/2 test server behavior. The provider peer ID is static and only the multiaddr matters, so peer identity is not deeply validated. Test signals are provider lookup output and exact `ipfs cat` body.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/http_retrieval_client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/identity_cid_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/identity_cid_test.go

Purpose: regression suite for identity-hash CID size limits and MFS conversion behavior when inline data would exceed `verifcid.DefaultMaxIdentityDigestSize`.

Important APIs/functions: `TestIdentityCIDOverflowProtection` covers `ipfs add --hash=identity`, `ipfs add --inline --inline-limit`, `ipfs files write --hash=identity`, `ipfs block put --format=raw --mhtype=identity`, `cid format`, and `files stat/read`.

Control flow: each parallel subtest creates a node, writes temp files, invokes add/files/block commands, and asserts either identity hash use or fallback to `config.DefaultHashFunction`. MFS append cases start from identity CIDs and verify overflow converts to a cryptographic hash or UnixFS dag-pb structure.

State and persistence: creates files in node repos, writes to MFS paths, adds blocks, and mutates the local blockstore/MFS root. No network state is required beyond the daemon.

Dependencies/integration: depends on Boxo `verifcid`, Kubo default hash config, harness process helpers, and file system operations.

Risks: extracting CID with `strings.Fields(stdout)[1]` assumes `ipfs add` output format. Parallel daemon-heavy subtests can be slow. Test signals include command failure text, CID multihash names/codecs, MFS hashes, and read-back content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/identity_cid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/init_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/init_test.go

Purpose: validates `ipfs init` output, repo layout, key algorithms, profiles, config defaults, existing-config initialization, and daemon-lock behavior.

Important APIs/functions: `validatePeerID`, `testInitAlgo`, and `TestInit`. It uses peer public-key extraction, libp2p crypto key types, welcome-doc CID from testutils, and harness node commands.

Control flow: `testInitAlgo` runs two variants: empty repo and non-empty welcome-doc repo. It checks exact stdout, repo directories/files, peer ID validity, mount config, and welcome-doc availability. `TestInit` adds failure for unreadable repo dir, ed25519/rsa/default algorithm cases, invalid/valid profiles, server profile config checks, init from an existing config, and refusal while daemon is running.

State and persistence: creates repo directories, config, datastore, blocks, and possibly welcome docs. It reads and validates repo files and starts a daemon only for the lock test.

Dependencies/integration: depends on Kubo CLI init, peer ID extraction behavior, OS permissions, and harness temp repos.

Risks: exact stdout is brittle; permission test may behave differently under privileged users or non-Unix filesystems. Test signals are stdout/stderr strings, file existence, config values, peer key type, and command exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/init_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/ipfswatch_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/ipfswatch_test.go

Purpose: tests the `ipfswatch` command-line tool on platforms with fsnotify support, including basic file ingestion and datastore plugin loading.

Important APIs/functions: `TestIPFSWatch` builds `cmd/ipfswatch/ipfswatch` if absent, starts it via `Runner.Run` with `RunFuncStart`, watches a temp directory, and validates emitted CIDs. It also mutates datastore config for pebbleds.

Control flow: before parallel subtests, the binary is built once. The first subtest starts ipfswatch, waits for initialization, writes a unique file, polls stderr for `added ... key: CID`, stops the watcher to release the repo lock, then reads content with `ipfs cat --offline`. The second configures pebbleds as the root datastore and checks startup stderr for plugin errors.

State and persistence: builds a binary under the repo, modifies node repo config/datastore directory, creates watched files, and adds content to the repo.

Dependencies/integration: depends on fsnotify, Go build, Kubo datastore plugins, pebbleds support, regex parsing, and process cleanup.

Risks: fixed sleeps and stderr log parsing are timing-sensitive. Killing background processes must release repo locks. Test signals are absence of “unknown datastore type,” captured CID, successful offline cat, and exact content match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/ipfswatch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/key_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/key_test.go

Purpose: verifies exported private key files are written with owner-only permissions.

Important APIs/functions: `TestKeyExportFilePermissions` initializes a node, generates an ed25519 key, and runs subtests for default `libp2p-protobuf-cleartext` and `pem-pkcs8-cleartext` export formats.

Control flow: the test skips Windows, generates `testkey`, exports it to a temporary path in each format, stats the output file, and asserts `0600` permissions.

State and persistence: mutates the node keystore by generating a key and writes exported key material to `t.TempDir` files. No daemon is required.

Dependencies/integration: depends on OS permission semantics, Kubo `key gen/export`, harness CLI execution, and testify assertions.

Risks: permission checks are Unix-specific and can be affected by filesystem mount behavior or umask interactions if command implementation changes. The key is cleartext by design in the tested formats, so temp-file cleanup is important. Test signals are file existence and exact permission bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/key_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/log_level_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/log_level_test.go

Purpose: comprehensive coverage for `ipfs log level` behavior across CLI, HTTP RPC, wildcard aliases, default levels, shell escaping, and go-log/slog interoperability.

Important APIs/functions: `TestLogLevel`, helpers `getExpectedSubsystems`, `parseCLIOutput`, `parseHTTPResponse`, `validateAllSubsystemsPresent`, and `validateAllSubsystemsPresentCLI`. Inline helpers start `ipfs log tail`, trigger identify protocol, and wait for subsystem log matches.

Control flow: CLI subtests start daemons, list subsystems, get/set levels for `*`, `all`, specific subsystems, default keyword, and shell-escaped wildcard forms. HTTP RPC subtests POST to `/api/v0/log/level` and validate JSON `Levels` or `Message`. Slog tests set levels via env or CLI, tail logs, trigger a normal CLI request and libp2p identify, and wait for both `cmds/http` and `net/identify` loggers.

State and persistence: runtime log levels are process state, not repo persistence. Test daemons and log-tail subprocesses are started/stopped per subtest.

Dependencies/integration: uses Kubo log RPC, go-log subsystem list, go-libp2p slog bridge, HTTP API, shell execution, and harness process env.

Risks: large parallel daemon count and timing-sensitive log tailing can flake. Subsystem names are implementation-coupled. Test signals are CLI lines, JSON fields, messages, and streamed JSON log entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/log_level_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/ls_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/ls_test.go

Purpose: validates `ipfs ls --long` formatting for mode, mtime, size, headers, directories, and stable output.

Important APIs/functions: `TestLsLongFormat` creates filesystem fixtures, uses `ipfs add` with `--preserve-mode` and/or `--preserve-mtime`, copies files into MFS where needed, and inspects `ipfs ls` output.

Control flow: parallel subtests create known files/directories with explicit modes and timestamps, add them recursively or as single files, obtain directory CIDs, run `ls --long` with combinations of `--headers` and `--size=false`, then assert columns and substrings/regexes.

State and persistence: temp files are written in node repos; blockstore and MFS state are mutated by add/cp/stat commands. Timestamps are fixed in the past to avoid current-year formatting variance.

Dependencies/integration: depends on OS file modes/mtime, Kubo UnixFS import metadata preservation, and CLI output formatting.

Risks: Unix permission rendering may differ on non-Unix systems; output parsing with whitespace fields can be sensitive to date format spacing. Test signals are mode strings, header order, CID prefixes, numeric size fields, date tokens, trailing slash for directories, and filename presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/ls_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_16_to_latest_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_16_to_latest_test.go

Purpose: reference migration suite for upgrading a real v16 repo fixture to latest, covering daemon `--migrate`, `repo migrate`, reverse migration, corrupted config handling, missing/default field behavior, temp-file cleanup, and backup files.

Important APIs/types/functions: `TestMigration16ToLatest`, `MigrationTestHelper` and assertion methods, `setupStaticV16Repo`, `cloneStaticRepoFixture`, `runDaemonMigrationWithMonitoring`, `runDaemonWithExpectedMigrations`, `runDaemonWithMultipleMigrationMonitoring`, `assertNoTempFiles`, `backupPath`, and cleanup/backup test helpers.

Control flow: each test clones `testdata/v16-repo`, runs daemon or repo migration, monitors stdout for migration messages and “Daemon is ready,” then shuts down. JSON helpers inspect nested config paths including map-key syntax. Failure tests corrupt config and verify atomic non-overwrite. Backup tests check `.bak` files and manual restore.

State and persistence: heavily mutates copied repo config/version files, creates backups, may create temp files, and starts daemons. Source fixture is copied, not modified.

Dependencies/integration: requires built `ipfs` in PATH, uses current `ipfs.RepoVersion`, harness node runner, JSON maps, exec pipes, and testify.

Risks: assumes latest includes 16-to-17 and 17-to-18 migrations; backup assertions mention v18 explicitly. Daemon output patterns are brittle. Test signals are version file, config JSON fields such as `AutoConf` and `auto`, output patterns, backup/temp file presence, and stderr emptiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_16_to_latest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_17_to_latest_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_17_to_latest_test.go

Purpose: focused 17-to-latest migration tests for consolidating legacy `Provider`/`Reprovider` config into the new `Provide` section.

Important APIs/functions: `TestMigration17ToLatest`, migration case functions, setup helpers `setupV17RepoWithProviderConfig`, `setupV17RepoWithFlatStrategy`, `setupV17RepoWithConfig`, empty/partial/invalid strategy setup helpers, `runDaemonMigrationFromV17`, and `MigrationTestHelper.RequireProviderMigration`.

Control flow: because no v17 fixture exists, setup clones v16, runs `repo migrate --to=17`, injects Provider/Reprovider JSON, then tests daemon `--migrate` or `repo migrate`. Assertions verify migrated fields (`Provide.Enabled`, `Provide.DHT.MaxWorkers`, `Provide.Strategy`, `Provide.DHT.Interval`), old-section removal, flat-to-all conversion, empty-section omission, partial migrations, and invalid strategy preservation followed by daemon startup failure.

State and persistence: mutates copied repo config/version and starts daemons for daemon migration cases. Invalid strategy test intentionally leaves invalid migrated config and runs daemon with timeout.

Dependencies/integration: depends on helper code from `migration_16_to_latest_test.go`, current `ipfs.RepoVersion`, JSON map edits, and Kubo provide-strategy validation.

Risks: cross-file helper dependency means this test file is not standalone. Numeric JSON values compare as `float64`. Output strings and invalid-strategy error text are implementation-coupled. Test signals are config fields, absent sections, migration output, version file, and daemon error text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_17_to_latest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_concurrent_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_concurrent_test.go

Purpose: verifies concurrent daemon migrations are prevented by repo locking.

Important APIs/functions: `TestConcurrentMigrations`, `testConcurrentDaemonMigrations`, and constant `daemonStartupWait`.

Control flow: the test clones a static v16 repo through shared migration helpers, starts the first `ipfs daemon --migrate` under a timeout context, waits two seconds for it to acquire the repo lock, then starts a second daemon migration against the same repo. The second command must fail and mention “lock.” Cleanup shuts down the first daemon and waits for process exit.

State and persistence: the first daemon may migrate and hold repo state/lock. The test asserts no `.tmp-*` migration files remain after the lock failure.

Dependencies/integration: depends on `setupStaticV16Repo`, `setupDaemonCmd`, and `assertNoTempFiles` from the migration helper suite, plus real OS file locking behavior.

Risks: fixed startup sleep can be too short or unnecessarily slow depending on machine load. If the first daemon exits before the second starts, the assertion loses meaning. Test signals are second command error, output containing “lock,” and no temp migration files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_concurrent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_mixed_15_to_latest_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_mixed_15_to_latest_test.go

Purpose: validates hybrid migration paths between old external migration binaries and newer embedded migrations: v15 to latest and latest back to v15.

Important APIs/functions: `TestMixedMigration15ToLatest`, `TestMixedMigrationLatestTo15Downgrade`, `setupStaticV15Repo`, `runDaemonWithLegacyMigrationMonitoring`, `runDaemonWithMigrationMonitoringCustomEnv`, `buildCustomPath`, `runMigrationWithCustomPath`, `createMockMigrationBinary`, `expectedMigrationSteps`, `verifyMigrationSteps`, `getNestedValue`, and `testRepoReverseHybridMigrationLatestTo15`.

Control flow: tests clone a v15 fixture, compile mock `fs-repo-15-to-16` and reverse binaries into temp PATH directories, then run daemon or repo migration. Daemon monitoring watches hybrid strategy, external phase, embedded phase, and completion messages. Repo tests validate final version/config. Downgrade first migrates to latest, then runs `repo migrate --to=15 --allow-downgrade` using mock external binaries.

State and persistence: mutates copied config/version files, creates mock binaries, writes repo locks in mock migrations, starts/stops daemons, and validates config JSON before/after.

Dependencies/integration: uses `ipfs.RepoVersion`, harness BuildNode, exec, runtime OS extension handling, slices env mutation, and helper fixture cloning.

Risks: generated mock binaries require Go toolchain availability. Output pattern assertions are tightly coupled to migration logging. Test signals are version file, preserved `Identity.PeerID`, `Bootstrap`, `AutoConf` addition/removal, and expected migration step messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/migration_mixed_15_to_latest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/testdata/v15-repo/config -->
# sources/distributed-fs/ipfs-kubo/test/cli/migrations/testdata/v15-repo/config

Purpose: static Kubo repo config fixture representing repository version 15 for migration tests.

Important structure: JSON config includes `Identity` with fixed peer/private key, legacy datastore mount spec using measure wrappers, concrete swarm/API/gateway addresses, default bootstrap peers, `Routing` with null `Routers`/`Methods`, `Ipns`, `DNS.Resolvers`, `Migration`, legacy `Provider` with `Strategy`, `Reprovider`, `Experimental`, `Plugins`, `Pinning`, `Import`, and `Internal`.

Control flow/integration: it is not executable code; tests copy this directory into temp repos via `cloneStaticRepoFixture` and use it as the pre-migration state for hybrid v15-to-latest and latest-to-v15 downgrade scenarios.

State and persistence: persistent fixture data includes sensitive-looking but test-only identity material. Tests must copy it before mutation so the fixture remains stable.

Dependencies/integration: consumed by `setupStaticV15Repo`, mock external migration tests, and JSON assertions around preserved peer ID, bootstrap presence, and `AutoConf` changes.

Risks: because it contains fixed listen ports (`4001`, `5001`, `8080`), daemon tests may need migration/runtime code to adjust or tolerate port use. Drift between this fixture and real historical v15 repos can reduce coverage value. Test signals are valid JSON, version-paired config shape, and legacy fields that embedded/external migrations transform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/testdata/v15-repo/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/testdata/v16-repo/config -->
# sources/distributed-fs/ipfs-kubo/test/cli/migrations/testdata/v16-repo/config

Purpose: static Kubo repo config fixture representing repository version 16, used as the main migration baseline.

Important structure: JSON config includes fixed `Identity`, datastore mount spec with flatfs and levelds, random-port addresses for swarm/API/gateway, `Mounts.MFS`, default bootstrap peers including DNS addr entries, gateway/API headers, swarm transport/resource sections, `AutoTLS`, empty `Routing`, `Provider`, `Reprovider`, `HTTPRetrieval`, import tuning null fields, `Version`, `Internal`, and `Bitswap`.

Control flow/integration: copied by `setupStaticV16Repo` for v16-to-latest, v17 setup, and concurrent migration tests. Migration assertions inspect how this config gains `AutoConf`, replaces default bootstrap/delegated routing/IPNS/DNS values with `auto`, and later moves Provider/Reprovider into Provide.

State and persistence: persistent fixture data is immutable source input for tests; temp copies are mutated by repo/daemon migration commands and backup creation.

Dependencies/integration: paired with a repo `version` file and other fixture files in `testdata/v16-repo`. Used by JSON helpers that compare map/list values.

Risks: fixture has current migration assumptions baked in, especially repo version sequence and default bootstrap values. If historical defaults or latest repo version change, tests may require fixture or assertion updates. Test signals are valid JSON and expected legacy-to-latest field transformations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/migrations/testdata/v16-repo/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/must.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/must.go

Purpose: tiny generic helper for tests that want to unwrap `(value, error)` expressions inline.

Important APIs/functions: `MustVal[V any](val V, err error) V` panics if `err` is non-nil and otherwise returns `val`.

Control flow: single branch checks the error and panics immediately, leaving caller code concise.

State and persistence: no state or persistence.

Dependencies/integration: standard Go generics only. It is available in package `cli` for tests in this directory.

Risks: panic-based error handling is appropriate for setup helpers but can obscure which assertion failed if overused in test logic. Test signals are indirect: callers either receive the value or the test process panics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/must.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/name_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/name_test.go

Purpose: broad integration suite for `ipfs name` publish, resolve, inspect, raw IPNS record get/put, sequence checks, offline behavior, TTL/lifetime validation, and republish config validation.

Important APIs/functions: `TestName`, `TestNameGetPut`, `TestNamePublishFlagValidation`, `TestNameRepublishConfigValidation`, and `TestNamePublishTTLClamp`. Inline helpers create daemons with imported fixture CAR data, generate keys, and create external IPNS records from ephemeral nodes.

Control flow: publish tests cover self keys across default/rsa/ed25519, named keys, CID/subpath/IPLD values, quiet output, offline resolution, V2-only records, TTL inspection, wrong-key validation, custom sequence numbers, and monotonic sequence enforcement. Get/put tests retrieve raw records, accept `/ipns/` prefixes, reject invalid/oversized/empty/garbage records, store external records, preserve bytes, handle offline `--allow-offline`, force lower-sequence puts, allow identical republish, and reject same-sequence different records.

State and persistence: imports fixture CAR blocks, publishes IPNS records to local/routing state, creates keys, writes record files, modifies repo config for republish validation, and starts/stops many daemons.

Dependencies/integration: depends on Boxo `ipns`, Kubo name command result structs, config validation, fixture CAR, harness DAG import, and routing record storage.

Risks: very stateful and daemon-heavy; public DHT avoidance relies on short lifetimes and test profiles. Sequence tests depend on IPNS “best record” semantics. Test signals are exact stdout/stderr, raw record bytes, JSON inspect validity, TTL/sequence values, and resolve output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/name_test.go -->
