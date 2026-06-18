# subset-b-007605 research

Grouped research for the subset B work item. Each section is source-tree aligned and bounded for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/transports_test.go -->
## sources/distributed-fs/ipfs-kubo/test/cli/transports_test.go

Purpose: Go CLI integration coverage for Kubo swarm transport combinations. `TestTransports` creates local harness nodes and verifies the same add/cat and recursive refs workflows over TCP, TCP with TLS disabled so Noise is used, QUIC, QUIC WebTransport, QUIC with announced non-dialable WebTransport addresses, and WebRTC Direct.

Important APIs and control flow: local closures `disableRouting`, `checkSingleFile`, `checkRandomDir`, `runTests`, and `tcpNodes` configure `config.Config`, create random content with `go-test/random` and `random/files`, start daemons, connect peers, and assert retrieval from every node. State is persisted only in temporary harness repositories and their Kubo config files; routing is set to `none` and bootstrap is cleared to force direct transport behavior. Dependencies and integration points include `test/cli/harness`, Kubo `config`, local daemon startup, `ipfs add`, `ipfs cat`, and `ipfs refs -r`.

Risks: all subtests run in parallel and use live daemons, random ports, and local networking, so regressions can be timing-sensitive. The non-dialable announce case is explicitly coupled to Kubo address-selection internals. Test signals are successful daemon connection and byte/refs retrieval under each transport-specific config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/transports_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/update_test.go -->
## sources/distributed-fs/ipfs-kubo/test/cli/update_test.go

Purpose: offline, deterministic CLI coverage for the `ipfs update` command tree, including read-only release queries, daemon-lock behavior, full binary install, revert, and stash cleanup.

Important APIs and helpers: `TestUpdate`, `TestUpdateWhileDaemonRuns`, `TestUpdateInstall`, `TestUpdateRevert`, and `TestUpdateClean` use `httptest.Server`, `TEST_KUBO_UPDATE_GITHUB_URL`, and `TEST_KUBO_VERSION` to avoid real GitHub calls. Helpers `newMockGitHubReleases`, `copyBuiltBinary`, `buildTestTarGz`, and `buildTestZip` fabricate release metadata, platform asset names, archives, and SHA-512 sidecars. Control flow checks help text, `check`, `versions`, JSON encodings, same-version install rejection, missing-stash revert errors, then copies the built `ipfs` binary to a temp path so install/revert mutate a disposable executable.

State and persistence: tests create `$IPFS_PATH/old-bin` stashes, replace a temporary binary, verify archive checksums and backup names, and preserve unrelated files during `clean`. Windows-specific fallbacks validate manual move paths when in-place executable replacement is locked. Dependencies include archive libraries, SHA-512, runtime OS/arch selection, Kubo CLI harness, and testify.

Risks: install/revert tests are intentionally not parallel because concurrent forks can cause ETXTBSY on Unix-like systems. Test signals include stdout/stderr content, JSON shape, stash presence/removal, exact binary bytes, and successful read-only update commands while a daemon holds the repo lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/webui_test.go -->
## sources/distributed-fs/ipfs-kubo/test/cli/webui_test.go

Purpose: CLI harness coverage for gateway `/webui/` error handling when the WebUI cannot or must not be served.

Important APIs and control flow: `TestWebUI` has three parallel subtests that create a single harness node, update `config.Config`, start a daemon, and call `node.APIClient().Get("/webui/")`. The cases set `Gateway.NoFetch=true`, `Gateway.DeserializedResponses=false`, and both together. State is limited to temporary repo config and daemon runtime.

Dependencies and integration points: the test drives the HTTP API/gateway path through the Kubo daemon, using `net/http` status constants and testify assertions. It depends on the WebUI gateway handler returning `503 Service Unavailable` and on stable explanatory body text.

Risks: assertions match human-facing error strings such as WebUI availability, NoFetch, deserialized response settings, pin/import advice, and release URL. This is useful regression coverage for operator guidance but can be brittle if wording changes. Test signal is priority ordering: `DeserializedResponses=false` must produce the incompatible message and suppress NoFetch messaging when both settings are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/webui_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/GNUmakefile -->
## sources/distributed-fs/ipfs-kubo/test/dependencies/GNUmakefile

Purpose: legacy make target for restoring Go test tool dependencies with `godep`.

Important targets and control flow: `all` aliases `restore`; `restore` checks for `godep`, creates `tmp_gopath`, saves `GOPATH`, exports a temporary GOPATH rooted at the dependencies directory, runs `godep restore` from the repository root, removes `tmp_gopath`, and restores `GOPATH`. State is filesystem-only: temporary GOPATH contents are created and deleted.

Dependencies and integration points: depends on `godep`, shell environment mutation, and relative path movement from `test/dependencies` to the project root. `.PHONY` marks `all` and `restore`.

Risks: the commands are line-by-line make recipes, so `OLD_GOPATH` and `export` do not persist across separate shell invocations unless make is configured to run one shell, making this target fragile as written. It also references legacy dependency tooling. Test signal is successful dependency restoration for test helper tools, but modern Go module tracking is primarily represented by `dependencies.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/dependencies.go -->
## sources/distributed-fs/ipfs-kubo/test/dependencies/dependencies.go

Purpose: Go tools tracking file that pins test-only command dependencies in `go.mod` without linking them into production binaries.

Important APIs and control flow: the file is guarded by `//go:build tools`, declares package `tools`, and imports tool packages only for side effects. There is no runtime control flow or persistence.

Dependencies and integration points: imported tools include `gocovmerge`, `golangci-lint`, `cid-fmt`, `random-data`, `random-files`, `hang-fds`, `multihash`, and `gotestsum`. These binaries are used by sharness, CI, linting, coverage, and helper command targets under `test/bin`.

Risks: removing or renaming blank imports can silently drop tool versions from the module graph and break test harness builds. Because the build tag excludes it from normal builds, test signal is indirect: `go install` or make rules for test dependencies continue to resolve exact tool modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/dependencies.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/go-sleep/go-sleep.go -->
## sources/distributed-fs/ipfs-kubo/test/dependencies/go-sleep/go-sleep.go

Purpose: tiny portable sleep helper for shell tests, accepting Go duration strings instead of relying on platform-specific `sleep` subsecond syntax.

Important APIs and control flow: `main` requires exactly one argument, parses it with `time.ParseDuration`, sleeps for that duration, and exits. `usageError` prints accepted units and exits with `-1`. There is no persisted state.

Dependencies and integration points: uses only `fmt`, `os`, and `time`; sharness helpers call `go-sleep 100ms`, `200ms`, and similar values in polling loops.

Risks: invalid duration strings or wrong arity abort the helper and can cause retry loops to fail immediately. Exit code `-1` maps through the OS to a nonzero status, which is enough for shell tests but not semantically specific. Test signals are stable timing behavior across Linux, BSD, and macOS shells.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/go-sleep/go-sleep.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/go-timeout/main.go -->
## sources/distributed-fs/ipfs-kubo/test/dependencies/go-timeout/main.go

Purpose: portable timeout wrapper used by tests where GNU `timeout` may not be available.

Important APIs and control flow: `main` parses `<timeout-in-sec> <command ...>`, creates `context.WithTimeout`, runs `exec.CommandContext`, wires stdin/stdout/stderr through, waits, and exits with `124` on timeout. For command failures it extracts `syscall.WaitStatus` and forwards the child exit status; unexpected execution or wait-status errors exit `255`.

State and dependencies: no persistent state is written; it depends on Go `context`, `os/exec`, and platform wait status support. Integration point is shell tests that need bounded command execution while preserving child output and exit codes.

Risks: signal termination and non-Unix wait semantics can be platform-sensitive, and `cmd.Start` errors are printed but still followed by `cmd.Wait`, which may produce a secondary error path. Test signal is command timeout returning 124 and normal failures retaining the child code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/go-timeout/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/iptb/iptb.go -->
## sources/distributed-fs/ipfs-kubo/test/dependencies/iptb/iptb.go

Purpose: embeds the local iptb plugin into a standalone `iptb` test binary for sharness cluster tests.

Important APIs and control flow: `init` registers a `testbed.IptbPlugin` with local plugin callbacks (`NewNode`, `GetAttrList`, `GetAttrDesc`, `PluginName`) as a built-in plugin. `main` creates `cli.NewCli()`, runs it with `os.Args`, prints errors to the CLI error writer, and exits nonzero on failure.

State and dependencies: state is managed by iptb itself, usually under test-controlled directories. Dependencies include `github.com/ipfs/iptb/cli`, `github.com/ipfs/iptb/testbed`, and `github.com/ipfs/iptb-plugins/local`.

Risks: registration panics on failure, so plugin/API drift breaks the binary at startup. Test signal is that sharness helpers can call `iptb init/start/stop/connect` for multi-node clusters without external plugin discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/iptb/iptb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/ma-pipe-unidir/main.go -->
## sources/distributed-fs/ipfs-kubo/test/dependencies/ma-pipe-unidir/main.go

Purpose: one-way multiaddr pipe used by transport tests to send stdin over a `manet` connection or receive a connection to stdout.

Important APIs and control flow: `Opts` tracks `--listen/-l` and `--pidFile`. `app` parses flags, validates mode (`send` or `recv`) and multiaddr, either listens and accepts or dials, optionally writes a pid file while active, then copies data with `io.Copy`. `main` exits with `app`'s status. State is limited to the optional pid file, removed via `defer`.

Dependencies and integration points: uses `go-multiaddr` and `go-multiaddr/net`; shell tests can use it for raw multiaddr transport assertions independent of Kubo's CLI.

Risks: error handling intentionally collapses most failures to exit 1 without diagnostics, which keeps scripts simple but makes debugging harder. Listener accept is blocking and needs external timeout or process cleanup. Test signals are successful byte transfer and pid-file lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/ma-pipe-unidir/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/pollEndpoint/main.go -->
## sources/distributed-fs/ipfs-kubo/test/dependencies/pollEndpoint/main.go

Purpose: polling utility that waits for a multiaddr endpoint, and optionally an HTTP URL over that endpoint, to become available.

Important APIs and control flow: flags define `-host`, `-tries`, `-tout`, `-http-url`, `-http-out`, and `-v`. `main` parses a multiaddr, optionally enables debug logging, loops `manet.Dial` until success or exhaustion, then, when `-http-url` is set, builds an HTTP client using `connDialer` to dial the same multiaddr and retries `tryHTTPGet` until HTTP 200. `tryHTTPGet` can copy the body to stdout; `connDialer.DialContext` ignores the HTTP transport's network/address and dials the configured multiaddr.

State and dependencies: no persistent state; dependencies include go-log, multiaddr, manet, and net/http. It integrates heavily with `test_launch_ipfs_daemon` and Docker sharness checks.

Risks: only HTTP 200 is accepted, and the helper sleeps the full timeout between retries. A minor code smell is `tryHTTPGet(client, url)` using `*httpURL` rather than its `url` parameter. Test signal is reliable daemon/API/gateway readiness detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/dependencies/pollEndpoint/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/GNUmakefile -->
## sources/distributed-fs/ipfs-kubo/test/integration/GNUmakefile

Purpose: legacy Docker-oriented benchmark harness for integration tests with CPU profiling.

Important targets and control flow: `all` aliases `collect`, which runs `clean`, `build_image`, `run_profiler`, and `cp_pprof_from_container`. It builds a Docker image from the repo root, runs `go test` inside the container with `--cpuprofile=cpu.out`, copies the profile and test binary into `./build/bench`, and provides `analyze` to open `go tool pprof`.

State and dependencies: writes `build/bench`, creates/removes Docker container `go-ipfs-bench`, and depends on Docker plus a configured `IMAGE` variable. The package path still references `go-ipfs` naming conventions.

Risks: stale naming and implicit `IMAGE` can break the makefile; container lifecycle is not robust if `docker run` fails before cleanup. Test signal is successful benchmark profile collection for integration package performance investigations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/addcat_test.go -->
## sources/distributed-fs/ipfs-kubo/test/integration/addcat_test.go

Purpose: core integration test for UnixFS add/get across two in-memory Kubo nodes connected by libp2p mocknet under configurable latency.

Important APIs and control flow: tests call `DirectAddCat` with deterministic `RandomBytes`; epic variants use `SkipUnlessEpic` and larger/slow latency configs. `DirectAddCat` creates mocknet, builds online adder and catter `core.IpfsNode`s with mock hosts, links all peers, bootstraps each node to the other, adds bytes through `coreapi.NewCoreAPI(adder).Unixfs().Add`, retrieves via `catterAPI.Unixfs().Get`, copies the reader, and byte-compares output. `AddCatPowers` scales sizes by powers of two; `SkipUnlessEpic` skips unless `IPFS_EPIC_TEST` is set.

State and dependencies: state is in-memory node/blockstore/exchange state only; no repo persists. Dependencies include boxo bootstrap/files, Kubo core/coreapi/mock, libp2p mocknet, and latency configs.

Risks: large epic tests can be expensive; mocknet timing does not cover real network failures. Test signals are successful transfer and exact bytes under instantaneous, slow blockstore, slow network, slow routing, and large transfer scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/addcat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/bench_cat_test.go -->
## sources/distributed-fs/ipfs-kubo/test/integration/bench_cat_test.go

Purpose: benchmark-only measurement of UnixFS cat/get throughput after content has already been added.

Important APIs and control flow: `BenchmarkCat1MB`, `BenchmarkCat2MB`, and `BenchmarkCat4MB` call `benchmarkVarCat`, which pre-generates deterministic bytes, sets benchmark bytes, and repeatedly calls `benchCat`. `benchCat` stops the timer while creating mocknet nodes, APIs, links, bootstrap records, and adding content, then starts the timer immediately before `catterAPI.Unixfs().Get` and the verification copy.

State and dependencies: all state is in-memory Kubo node state and mocknet links. Dependencies mirror `addcat_test.go`, with `testing.B` timer control.

Risks: the measured region includes both retrieval and verification copy, so it is a practical end-to-end cat benchmark rather than a pure exchange benchmark. Test signals are benchmark throughput and exact byte equality after retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/bench_cat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/bench_test.go -->
## sources/distributed-fs/ipfs-kubo/test/integration/bench_test.go

Purpose: benchmark matrix for complete add-and-cat flows across content sizes and latency profiles.

Important APIs and control flow: `benchmarkAddCat` pre-generates deterministic data outside the timed section, sets bytes, then repeatedly calls `DirectAddCat`. Benchmark functions cover instantaneous 1KB through 256MB, slow routing through 512MB, slow network through 256MB, and slow blockstore sizes using latency presets from `go-libp2p-testing/net`.

State and dependencies: uses the shared `RandomBytes` and `DirectAddCat` from `addcat_test.go`; every iteration creates fresh in-memory nodes and mocknet state.

Risks: larger benchmarks are resource-intensive and include node construction/bootstrap/add/retrieve costs, so results are system-sensitive and not isolated microbenchmarks. Test signals are benchmark throughput and failure if any add/get byte verification fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/bitswap_wo_routing_test.go -->
## sources/distributed-fs/ipfs-kubo/test/integration/bitswap_wo_routing_test.go

Purpose: verifies Bitswap block exchange can work among directly connected peers without routing.

Important APIs and control flow: `TestBitswapWithoutRouting` creates four online core nodes on a mocknet with `libp2p.NilRouterOption`, links all peers, fully connects every node to every other peer, manually inserts blocks into node blockstores, and retrieves them through each node's `Blocks.GetBlock`. It skips the original provider for the first block because the block is not in that node's exchange path.

State and dependencies: state is in-memory blockstore and Bitswap exchange state. Dependencies include go-block-format, go-cid, Kubo core/mock/libp2p, and libp2p mocknet.

Risks: the test relies on direct full-mesh connections and does not exercise provider discovery. The skip for the provider node documents an exchange edge case that could hang if changed carelessly. Test signals are no retrieval errors and exact raw block byte equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/bitswap_wo_routing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/three_legged_cat_test.go -->
## sources/distributed-fs/ipfs-kubo/test/integration/three_legged_cat_test.go

Purpose: tests a three-node retrieval path where an adder and catter discover each other through a bootstrap/routing node rather than direct pair bootstrap.

Important APIs and control flow: `RunThreeLeggedCat` creates a mocknet, a public bootstrap node, adder, and catter, links all peers, bootstraps both data nodes to the bootstrap peer, adds data via the adder CoreAPI, explicitly provides the root CID through routing, then gets the UnixFS path through the catter CoreAPI and byte-compares. Tests cover instantaneous 1MB plus epic slow blockstore/network/routing and 100MB coast-to-coast presets.

State and dependencies: all state is in-memory mocknet, DHT/routing records, and UnixFS blockstores. Dependencies include Kubo mock public nodes, boxo bootstrap/files, coreapi, libp2p mocknet, and latency configs.

Risks: explicit `Routing.Provide` is required to avoid racing the async reprovider; removing it may make tests flaky. Epic cases are expensive and gated by `IPFS_EPIC_TEST`. Test signal is successful routed discovery and exact content retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/three_legged_cat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/wan_lan_dht_test.go -->
## sources/distributed-fs/ipfs-kubo/test/integration/wan_lan_dht_test.go

Purpose: validates Kubo's split LAN/WAN DHT behavior in mocknet with synthetic LAN and WAN IPv6 listen addresses.

Important APIs and control flow: `makeAddr` derives LAN or WAN multiaddrs from `lanPrefix`/`wanPrefix`; `RunDHTConnectivity` creates a test peer plus WAN server peers and LAN peers, links peers within their domains, listens on synthetic addresses, connects the test peer to LAN first, refreshes the LAN routing table, verifies provider discovery for a LAN-provided CID, then connects WAN peers, refreshes WAN routing, verifies WAN provider discovery, and finally checks merged provider results when a WAN peer also provides the LAN CID. Tests include fast and epic slow network/routing profiles.

State and dependencies: in-memory mocknet peer connections, DHT routing tables, provider records, and peerstore addresses. Dependencies include Kubo DHT options, libp2p core network/mocknet, multiaddr, and cid.

Risks: uses real-looking WAN prefix for peer diversity behavior and timeout loops up to 60s; random peer selection can expose connectivity edge cases. Test signals are non-empty LAN/WAN routing tables and expected provider IDs/counts from `FindProvidersAsync`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/integration/wan_lan_dht_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/ipfs-test-lib.sh -->
## sources/distributed-fs/ipfs-kubo/test/ipfs-test-lib.sh

Purpose: generic shell helper library shared by sharness tests, with comparison utilities, Docker wrappers, portable sequence/base64 helpers, and safer command quoting.

Important functions and control flow: `ansi_strip`, `shellquote`, `test_fsh`, `test_cmp`, `test_sort_cmp`, and `test_path_cmp` normalize diagnostics and comparisons. Docker helpers wrap build/run/exec/stop/rm/rmi. `test_includes_lines` validates expected-line subsets; `test_seq` avoids depending on GNU seq; `b64decode` chooses platform-specific base64 flags.

State and dependencies: writes temporary sorted/standardized comparison files next to inputs and operates on Docker state when used. It depends on sed, diff, sort, comm, docker, expr, uname, and base64.

Risks: helper behavior is global to many shell tests, so changes can alter diagnostics or comparison semantics broadly. `shellquote` and `eval` in `test_fsh` must stay correct for arguments with quotes. Test signals come from `t0015-basic-sh-functions.sh` and broad use across the sharness suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/ipfs-test-lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/GNUmakefile -->
## sources/distributed-fs/ipfs-kubo/test/sharness/GNUmakefile

Purpose: local entry makefile for running individual sharness scripts or the aggregate suite from the `test/sharness` directory.

Important targets and control flow: `all` depends on `aggregate`. `SH` expands `t[0-9][0-9][0-9][0-9]-*.sh`. The `.DEFAULT $(SH)` rule delegates to `$(MAKE) -C ../.. test/sharness/$@`, ensuring top-level make rules build dependencies and run the selected test. `ALWAYS` forces delegation.

State and dependencies: no direct state is written; state is handled by top-level make and the tests themselves. It depends on GNU make pattern/default behavior and the top-level `test/sharness/<script>` targets.

Risks: direct execution from this directory relies on top-level make rule names staying aligned. Test signal is the ability to run `make tXXXX-name.sh` or `make aggregate` locally and have dependency preparation happen centrally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/Rules.mk -->
## sources/distributed-fs/ipfs-kubo/test/sharness/Rules.mk

Purpose: top-level make fragment that defines sharness test discovery, dependencies, execution, aggregation, and cleanup.

Important variables and control flow: defines `SHARNESS_$(d)`, `T_$(d)`, and `DEPS_$(d)` including helper binaries, `cmd/ipfs/ipfs`, result cleanup, and sharness installation. On Linux it copies plugin `.so` files into `test/sharness/plugins` when plugin tests are enabled. Each test target runs from its directory, optionally continuing on failure when `CONTINUE_ON_S_FAILURE=1`. Aggregate targets run `test-aggregate-results.sh` and `test-aggregate-junit-reports.sh`.

State and dependencies: creates plugin copies and `test-results`, exports `MAKE_SKIP_PATH=1`, and depends on make include conventions plus sharness scripts. `CLEAN` includes test result files.

Risks: dependency list is broad; missing helper binaries break many tests. Plugin copying is Linux-specific. Test signals are successful per-test execution, aggregate text status, and JUnit XML generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/install-sharness.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/lib/install-sharness.sh

Purpose: installs the vendored/expected sharness framework into `test/sharness/lib/sharness` when required.

Important APIs and control flow: the script sets strict shell behavior, computes directories, defines `die`, verifies prerequisites, fetches or prepares sharness assets, and creates the local `sharness.sh`/library layout consumed by `test-lib.sh`. State is written under `test/sharness/lib/sharness`.

Dependencies and integration points: depends on POSIX shell utilities and the sharness source location configured by the script. It integrates with `Rules.mk` through the `$(SHARNESS_$(d))` dependency.

Risks: network or upstream layout assumptions can break bootstrapping if sharness is not already present. Because the test framework is sourced by every shell test, a partial install creates broad failures. Test signal is the presence of sourceable `lib/sharness/sharness.sh` and `lib-sharness`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/install-sharness.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/iptb-lib.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/lib/iptb-lib.sh

Purpose: sharness helper library for iptb-backed multi-node Kubo clusters.

Important functions and control flow: `ipfsi` runs `ipfs` commands in a numbered iptb node. `check_has_connection` inspects swarm peers for expected connectivity. `iptb` wraps the binary with the local testbed path. `startup_cluster` initializes, starts, waits for, and connects a cluster, writing useful node addresses and peer IDs. `iptb_wait_stop` waits for node shutdown.

State and dependencies: operates on iptb testbed directories in the current test trash area and on daemon processes managed by iptb. Dependencies include the `iptb` helper binary, Kubo daemons, shell polling, and sharness assertions.

Risks: cluster startup is timing-sensitive and depends on process cleanup. Incorrect testbed paths can leak or target wrong nodes. Test signals are successful cluster start/connect/stop and expected swarm peer visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/iptb-lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-aggregate-junit-reports.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-aggregate-junit-reports.sh

Purpose: combines per-sharness JUnit XML result files into a single aggregate XML report.

Important control flow: the script scans sharness `test-results` XML files, wraps or concatenates their testcase/testsuite content into `test-results/sharness.xml`, and is invoked from `Rules.mk` after test targets. State is the aggregate XML report under `test/sharness/test-results`.

Dependencies and integration points: depends on sharness running with JUnit output (`TEST_JUNIT=1`) and common shell/XML text utilities. CI systems consume the resulting XML.

Risks: XML aggregation via shell text processing can be brittle if sharness output format changes or filenames contain unexpected characters. Test signal is a non-empty aggregate JUnit report with all executed tests represented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-aggregate-junit-reports.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-aggregate-results.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-aggregate-results.sh

Purpose: aggregates sharness textual result files into a suite-level pass/fail summary.

Important control flow: invoked by `Rules.mk` target `aggregate`, it scans `test-results`, summarizes successes/failures/skips, and exits according to aggregate status. State is read from sharness result files and written to stdout/stderr rather than persistent domain state.

Dependencies and integration points: depends on the result format emitted by sharness scripts and shell utilities. It is the main local signal for `make test_sharness` style runs.

Risks: if individual tests are run without producing result files, aggregation can misreport or lack coverage. Test signal is an aggregate nonzero exit on failed sharness tests and readable summary output for CI logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-aggregate-results.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-lib-hashes.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-lib-hashes.sh

Purpose: centralizes stable CID/hash constants used by sharness scripts.

Important content: defines common known hashes such as the empty-directory CID or canonical fixture CIDs before `test-lib.sh` sources sharness. There is no control flow beyond shell variable assignment and no persistence.

Dependencies and integration points: sourced early by `lib/test-lib.sh`, making constants globally available to command tests. Many scripts compare CLI output against these values.

Risks: changing constants can break broad expected-output coverage and should only follow intentional CID/profile changes. Test signal is exact expected hash matching across add, cat, object, dag, and gateway tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-lib-hashes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-lib.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-lib.sh

Purpose: Kubo-specific sharness bootstrap and helper library, sourced by nearly every shell test.

Important APIs and control flow: it configures PATH unless `MAKE_SKIP_PATH=1`, maps environment flags to sharness prerequisites, sources `test-lib-hashes.sh`, symlinks and sources sharness, aborts if leftover daemons have CWDs under the current test directory, sets `IPFS_PATH`, imports `ipfs-test-lib.sh` and `iptb-lib.sh`, and defines helpers for repeat comparisons, polling, daemon launch, mount/unmount, daemon kill, curl response checks, content assertions, disk/stat portability, peer ID checks, multiaddr conversion, provider assertions, and blockstore purge.

State and persistence: creates symlinks, `stuck_cwd_list`, temporary assertion files, `.ipfs` repos, mount directories, daemon output files, and process state. It also controls `IPFS_PID`, API/gateway/swarm address variables, and ulimit.

Dependencies and integration points: relies on local `ipfs`, sharness, `pollEndpoint`, `go-sleep`, lsof, netstat, curl, FUSE tools, and many POSIX utilities.

Risks: this is high-blast-radius infrastructure. Daemon cleanup, polling timeouts, platform-specific stat/base64/FUSE behavior, and global variables can affect unrelated tests. Test signals include stable daemon startup readiness, mount output, peer ID validation, and reusable assertion helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0001-tests-work.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0001-tests-work.sh

Purpose: meta-test that validates sharness scripts are structurally well-formed.

Important control flow: after sourcing `lib/test-lib.sh`, it iterates over top-level `t*.sh` files and asserts each has `test_done` and `test_description`. For most scripts it also uses awk to ensure daemon launch/kill helper calls are balanced. It exempts daemon/shutdown tests that intentionally manage process lifecycle manually.

State and dependencies: reads sibling test files only; no Kubo state is created except normal test framework setup. Dependencies include grep, awk, find, basename, and sharness assertions.

Risks: static checks can reject legitimate new patterns unless exemptions are updated. Test signal is early detection of missing descriptions, missing `test_done`, or unbalanced daemon helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0001-tests-work.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0002-docker-image.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0002-docker-image.sh

Purpose: end-to-end Docker image validation for Kubo container startup, init hooks, API/gateway readiness, and basic content commands.

Important control flow: gated by `DOCKER` prereq, checks Docker version, builds the image from the repo Dockerfile, writes two `/container-init.d` scripts, runs the container with API/gateway ports bound to localhost, waits for gateway and API via `pollEndpoint`, checks init script log ordering and config effects, performs `ipfs add`/`cat` inside the container, compares API `/version` commit with `ipfs version --enc json`, then stops/removes container and image.

State and dependencies: creates a Docker image/tag, container, mounted init scripts, and temporary expected/actual files. Depends on Docker, pollEndpoint, local network ports, and shell helpers.

Risks: requires Docker group access and available ports 5001/8080. Cleanup happens at script end, so early hard failures can leave images/containers. Test signals are container liveness, init ordering, config persistence, content round trip, and commit metadata consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0002-docker-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0003-docker-migrate.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0003-docker-migrate.sh

Purpose: Docker image migration-path test verifying an old repo triggers migration download from configured distribution sources.

Important control flow: gated by Docker, builds the image, configures migration source variables, stages a fake HTTP response, mutates repo version metadata to simulate an old repo, starts a fake distribution server, runs the container, verifies the container attempted to pull the expected migration asset, inspects logs, stops the container, kills the fake server, and checks the requested version.

State and dependencies: manipulates a test repo, Docker container/image state, netcat or equivalent fake server state, and migration config files. It integrates Kubo container startup with fs-repo migration logic.

Risks: depends on networking, Docker, migration naming conventions, and precise HTTP request behavior. Process cleanup for the fake server is important. Test signals are observed migration request path/version and expected container log behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0003-docker-migrate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0012-completion-fish.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0012-completion-fish.sh

Purpose: validates generated fish shell completions for the Kubo CLI.

Important control flow: runs `ipfs commands completion fish`, writes/generated completion content, and checks that completion data can complete a representative command such as `ipfs version`. No daemon is required.

State and dependencies: writes temporary completion files in the sharness trash directory. Depends on the built `ipfs` CLI and fish-compatible completion syntax expectations.

Risks: brittle if command completion output format changes or if the test environment lacks assumptions needed to evaluate completions. Test signal is successful generation and expected completion for a known subcommand.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0012-completion-fish.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0015-basic-sh-functions.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0015-basic-sh-functions.sh

Purpose: unit-style shell tests for shared helper functions, especially robust quoting.

Important control flow: sources `lib/test-lib.sh`, invokes `shellquote` with simple strings, complex printf inputs, quotes, whitespace, and varied bytes, then compares output to expected quoted forms. No daemon or repo behavior is under test.

State and dependencies: uses expected/actual files in the sharness trash directory. Depends on `printf`, sed quoting behavior, and `test_cmp`.

Risks: because `shellquote` is used by diagnostic failure helper `test_fsh`, quoting regressions can hide or distort many later test failures. Test signal is exact quoted output for edge-case arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0015-basic-sh-functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0018-indent.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0018-indent.sh

Purpose: style/meta-test ensuring sharness test scripts do not use tab indentation.

Important control flow: iterates over `../t*.sh` and asserts each file has no tab-indented lines according to the grep pattern used in the test. It relies on sharness `test_expect_success` for each file.

State and dependencies: read-only over test scripts; no Kubo repo or daemon state. Depends on find/grep and shell iteration.

Risks: purely stylistic and can fail after harmless formatting changes. Test signal is uniform indentation across sharness scripts, reducing noisy diffs and shell readability problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0018-indent.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0021-config.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0021-config.sh

Purpose: comprehensive shell coverage for `ipfs config`, `config show`, `config replace`, and `config profile apply`.

Important helpers and control flow: `test_config_cmd_set` validates setting scalar and JSON config values; `test_profile_apply_revert` verifies profile application and inverse profile restoration; `test_profile_apply_dry_run_not_alter` ensures dry-run output does not mutate config; `test_config_cmd` orchestrates config show, replace, identity privacy, addr filters, backup creation, profile output, and daemon-running behavior. The script launches a daemon near the end to verify config commands while online.

State and dependencies: mutates `.ipfs/config`, creates backups, reads real config files, and compares JSON/text output. Depends on jq-like config behavior through the CLI, shell comparisons, and daemon helpers.

Risks: exact config output, private key redaction, and profile side effects are high-value but brittle to config schema changes. Test signals include successful writes, no PrivKey leakage in show/dry-run, replacement rejection when private keys are included, backup files, and daemon-safe config reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0021-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0022-init-default.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0022-init-default.sh

Purpose: validates `ipfs init` behavior with default configuration.

Important control flow: initializes a repo, asserts `.ipfs/config` exists, reads config through `ipfs config`, removes the repo, runs default init again, and compares expected config output. State is the temporary `.ipfs` repository.

Dependencies and integration points: uses the local `ipfs` binary and shared shell comparison helpers. It exercises fs-repo initialization and default config generation without a daemon.

Risks: expected output can shift with intentional default config changes. Test signal is that init succeeds, writes config, and produces readable default config values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0022-init-default.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0023-shutdown.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0023-shutdown.sh

Purpose: validates the `ipfs shutdown` command against online and offline-mode daemons.

Important control flow: starts a normal daemon, runs `ipfs shutdown`, asserts the daemon process no longer runs, then repeats with `test_launch_ipfs_daemon_without_network`. This script intentionally does not use the standard kill helper after shutdown because the command under test should terminate the daemon.

State and dependencies: creates temporary repo/daemon process state and uses `IPFS_PID` from `test-lib.sh`. Depends on API readiness and shell `kill -0`.

Risks: process termination timing can be flaky if shutdown is asynchronous; the script must avoid double-killing successfully stopped daemons. Test signal is successful shutdown command and dead process in both networked and offline daemon modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0023-shutdown.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0024-datastore-config.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0024-datastore-config.sh

Purpose: verifies datastore spec configuration integrity and daemon behavior when runtime versus on-disk datastore parameters change.

Important control flow: starts and stops a daemon with the existing datastore config, edits runtime-only values in the spec and confirms the daemon can still start, then edits on-disk values and asserts daemon startup fails. Fixtures under `t0024-files` provide alternate specs such as nosync and changed shard functions.

State and dependencies: mutates `.ipfs/config` datastore spec and starts daemons to validate repo opening. Depends on Kubo datastore config parsing and lock/open validation.

Risks: datastore specs are sensitive persistence contracts; allowing incompatible on-disk changes can corrupt or orphan data. Test signal is acceptance of runtime-only changes and rejection of on-disk layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0024-datastore-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0025-datastores.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0025-datastores.sh

Purpose: smoke-tests non-standard datastore profiles.

Important control flow: defines a list of profiles and iterates over them, initializing and exercising repos under each datastore profile enough to ensure the profile can be used. The script is compact and relies on shared init/daemon helpers for most behavior.

State and dependencies: creates temporary `.ipfs` repos for profile variants and may start daemons depending on helper use. Depends on Kubo profile names and datastore backends available in the build.

Risks: profile availability and backend behavior can vary by build tags or platform. Test signal is that each listed non-standard datastore profile initializes and completes the basic sharness lifecycle without failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0025-datastores.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0026-id.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0026-id.sh

Purpose: verifies `ipfs id` output, peer ID formatting, and agent version suffix behavior.

Important helper and control flow: `test_id_compute_agent` builds expected AgentVersion strings. The script checks local self ID, converts/random peer ID behavior while offline, starts a daemon with `--agent-version-suffix`, verifies local and remote identify-protocol AgentVersion values, then tests JSON config `Version.AgentSuffix` overriding an ignored CLI suffix.

State and dependencies: mutates config, starts daemons, and uses peer ID assertion helpers. Depends on identify protocol propagation and version string construction.

Risks: exact AgentVersion formatting is externally visible and changes may affect interoperability diagnostics. Test signal is valid peer ID length/encoding and expected suffix source precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0026-id.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0027-rotate.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0027-rotate.sh

Purpose: tests identity/key rotation command behavior.

Important control flow: `test_rotate` runs rotation scenarios, captures old/new identities, validates repo config changes, and checks command output. It exercises rotation across supported key types or formats defined in the script and finishes without daemon use.

State and dependencies: mutates `.ipfs/config` identity material and key-related repo state. Depends on Kubo identity generation, config persistence, and peer ID validation helpers.

Risks: identity rotation is destructive if run outside test repos; sharness isolation via `IPFS_PATH` is critical. Test signals are changed PeerID/private key material, successful command exit, and valid rotated identities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0027-rotate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0040-add-and-cat.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0040-add-and-cat.sh

Purpose: broad sharness coverage for `ipfs add` and `ipfs cat` across files, directories, stdin, mount paths, raw leaves, wrapping, dereference behavior, named pipes, symlinked working directories, large/expensive data, and offline only-hash behavior.

Important helpers and control flow: `test_add_cat_file`, `test_add_cat_5MB`, `test_add_cat_raw`, `test_add_cat_derefargs`, `test_add_cat_expensive`, `test_add_named_pipe`, `test_add_pwd_is_symlink`, and `add_directory` generate content, run add variants, capture hashes, cat content back, and compare expected output. The script launches a daemon with mounts for FUSE cases, checks help text, stdin behavior, recursive directory output, CID version validation, and then separately verifies `--only-hash` cannot be catted from an offline daemon.

State and dependencies: writes many fixture files/directories, uses `.ipfs` repo/blockstore/pins, daemon/FUSE mounts, random-data, and shell comparison helpers.

Risks: high coverage but high timing/platform sensitivity around FUSE, named pipes, random data, and daemon lifecycle. Test signals are exact hashes/output, successful cat byte comparisons, expected failures for invalid CID version and absent only-hash blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0040-add-and-cat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0042-add-skip.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0042-add-skip.sh

Purpose: tests `ipfs add` path skipping/exclusion behavior.

Important control flow: `test_add_skip` builds directory/file fixtures, runs add commands with skip options, and checks that skipped paths are absent while included paths can still be added and retrieved. It runs both offline/repo and daemon-backed portions through standard daemon helpers.

State and dependencies: creates fixture trees and mutates the test repo/blockstore. Depends on `ipfs add`, `ipfs cat`/listing commands, and comparison helpers.

Risks: path matching semantics are user-visible and can be platform-sensitive for separators or hidden files. Test signal is expected add output and retrieval behavior when skip rules are applied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0042-add-skip.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0043-add-w.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0043-add-w.sh

Purpose: tests `ipfs add -w` wrapping behavior for files, directories, and path naming.

Important control flow: `test_add_w` prepares fixtures, runs add with wrapping options, captures wrapper/root hashes, and validates listing/cat paths through the wrapper. It includes daemon-backed validation after launching a daemon and then kills it.

State and dependencies: writes fixture files/directories and stores resulting DAGs in the temporary repo. Depends on `ipfs add -w`, `ipfs ls`, `ipfs cat`, and deterministic expected output.

Risks: wrapper DAG layout and path names are compatibility-sensitive. Test signal is that wrapped roots expose expected child names and content under both CLI and daemon contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0043-add-w.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0044-add-symlink.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0044-add-symlink.sh

Purpose: validates symlink handling during `ipfs add`.

Important control flow: creates files and symlinks, then `test_add_symlinks` runs add variants and checks resulting links/content. It launches a daemon for the online half and stops it afterward.

State and dependencies: creates filesystem symlinks and stores UnixFS DAGs in the repo. Depends on platform symlink support, `ipfs add`, `ipfs ls`/`cat`, and expected UnixFS symlink encoding.

Risks: symlink behavior can differ on Windows or restricted filesystems; dereference versus preserve semantics must remain clear. Test signal is expected representation and retrieval of symlink entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0044-add-symlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0045-ls.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0045-ls.sh

Purpose: comprehensive coverage for `ipfs ls` output modes, streaming behavior, raw leaves, object links, and behavior when child blocks are missing.

Important helpers and control flow: `test_ls_cmd`, `test_ls_cmd_streaming`, `test_ls_cmd_raw_leaves`, and `test_ls_object` create DAGs and compare listing output. The script tests online daemon behavior, removes a file/block from a directory DAG, checks failures with default resolution and size resolution, then starts offline and online daemons to verify `--resolve-type=false --size=false` succeeds and does not hang.

State and dependencies: mutates repo/blockstore, starts/stops daemons, and uses add output-derived hashes. Depends on `ipfs add -r`, `ipfs ls`, raw leaf DAG layout, and block removal.

Risks: missing-block behavior is easy to regress into hangs or over-fetching. Test signals are exact `ls` output, expected failures when metadata needs missing blocks, and non-hanging success when resolution is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0045-ls.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0046-id-hash.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0046-id-hash.sh

Purpose: tests identity multihash behavior for inline CIDs and identity-hash content.

Important control flow: fetches and pins a random identity hash, adds small content with inline identity hash, confirms content is not stored as a normal block but remains retrievable, verifies block removal is a no-op, tests `--inline` and `--inline --raw-leaves`, exercises size threshold behavior with a larger file, then repeats key operations after enabling filestore and `--nocopy`.

State and dependencies: mutates blockstore, pins, and filestore config. Depends on `ipfs add`, `cat`, `pin`, `block rm`, `repo` semantics, and known identity multihash formatting.

Risks: inline data is intentionally not persisted like normal blocks, so blockstore/pin assumptions are subtle. Test signal is retrievability without stored block presence and correct identity multihash CIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0046-id-hash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0047-add-mode-mtime.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0047-add-mode-mtime.sh

Purpose: exhaustive tests for preserving, setting, changing, retrieving, and stat-formatting UnixFS mode and mtime metadata for files, symlinks, and directories.

Important helpers and control flow: `mk_name`, `mk_file`, `mk_dir`, `test_file`, `setup_directory`, `test_directory`, `test_stat_template`, `test_stat`, and `test_all` generate fixtures and run the same matrix over CID/layout modes. The script sets import defaults for deterministic CIDs, checks that metadata flags have no effect unless used, verifies preserve/set options including nanoseconds, tests symlink restrictions, recursively restores directories, and validates `ipfs files stat` templates.

State and dependencies: creates files/directories/symlinks with specific modes and mtimes, stores DAGs, uses an offline daemon, and compares stat/cat/restored filesystem output.

Risks: platform filesystem timestamp precision and symlink metadata support can vary. Test signal is exact mode/mtime preservation, successful recursive restoration, and template output for string/octal/seconds/nanoseconds fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0047-add-mode-mtime.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0050-block.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0050-block.sh

Purpose: sharness coverage for `ipfs block put/get/stat/rm`, CID codec/hash options, pin safety, and block size limits.

Important control flow: creates blocks from stdin/files, validates put output and get bytes, stats block size, removes blocks, verifies pinned and indirectly pinned blocks cannot be removed, tests multi-block removal with invalid/valid inputs, `-f` and `-q` modes, deprecated `--format=protobuf`, `--cid-codec=dag-pb`, raw blocks with custom multihash type/length, conflict between legacy format and codec, empty stdin handling, sha3 with CIDv0 rejection, and oversized block rejection.

State and dependencies: mutates blockstore and pins; uses fixture protobuf data. Depends on `ipfs block`, `ipfs add`, `ipfs pin`, and exact CID/multihash behavior.

Risks: block command semantics are low-level and compatibility-sensitive. Test signals include exact command output, block presence/absence, pin-protection errors, no panic on empty stdin, and expected limit errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0050-block.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0051-object.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0051-object.sh

Purpose: broad legacy `ipfs object` command coverage for get/put/data/links/stat/patch operations.

Important helpers and control flow: `test_patch_create_path` builds nested patch paths; `test_object_cmd` creates objects, validates object data and links, performs puts from JSON/protobuf forms, checks stats, and exercises patch add-link/rm-link/append-data/set-data/create-path behavior. It runs around a daemon lifecycle to cover API-backed operation too.

State and dependencies: writes object fixtures and mutates the repo DAG/blockstore. Depends on legacy dag-pb object encoding, `ipfs object` command output, and comparison helpers.

Risks: `ipfs object` is legacy but compatibility-sensitive; exact JSON/text output can change. Test signal is successful object mutation and exact data/link/stat output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0051-object.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0052-object-diff.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0052-object-diff.sh

Purpose: tests `ipfs object diff` for identity, added, removed, nested, and changed links, with raw-leaves variants.

Important control flow: creates directory/file objects, captures CIDs, runs diff against self and expects empty output, then compares expected diff records for added links, verbose added links, removed links, nested additions, and changed links. Raw-leaves versions ensure DAG layout differences do not break diff semantics.

State and dependencies: creates DAGs through `ipfs add` and stores them in the test repo. Depends on object diff output format, raw leaf behavior, and deterministic CIDs.

Risks: exact diff output is a stable CLI contract; changing path or type markers breaks users and tests. Test signal is empty self-diff and exact expected diff lines for each mutation category.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0052-object-diff.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0053-dag.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0053-dag.sh

Purpose: extensive `ipfs dag` command coverage for put/get/resolve/stat/import-related codecs and selectors.

Important helpers and control flow: prepares JSON/IPLD fixtures, creates equivalent objects in dag-json, dag-cbor, and dag-pb, and `test_dag_cmd` exercises many get/put combinations, codec conversions, path traversal, output encodings, error cases, and block size checks. The script also runs daemon-backed DAG command coverage.

State and dependencies: writes fixture files including non-canonical CBOR, stores DAG blocks in the repo, and starts a daemon. Depends on IPLD codecs, CID determinism, `ipfs dag` output formats, and comparison helpers.

Risks: codec behavior is compatibility-sensitive; output and error messages can be brittle. Test signal is successful round trips across codecs, expected CIDs/output, rejection of invalid/oversized input, and daemon-safe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0053-dag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0054-dag-car-import-export.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0054-dag-car-import-export.sh

Purpose: tests CAR import/export behavior for DAGs, roots, pins, stats, large blocks, CARv2, IPLD codec decoding, and incomplete DAG pin failures.

Important helpers and control flow: `test_cmp_sorted`, `reset_blockstore`, `do_import`, and `run_online_imp_exp_tests` coordinate blockstore cleanup, multi-node online import/export, and output comparison. The script sets up an iptb testbed, stops nodes for offline cases, exports known DAGs, validates nonexistent CID errors, imports multiroot CARs with JSON/stats output, tests `--pin-roots=false`, naked root imports, block size enforcement and `--allow-big-block`, CARv2 import, dag-json/dag-cbor/json/cbor decode paths, and IPIP-402 partial DAG behavior.

State and dependencies: uses CAR fixtures, iptb-managed repos, pins, blockstores, and daemon state. Depends on `ipfs dag import/export`, `ipfs pin`, CAR test data, and sharness/iptb helpers.

Risks: CAR semantics are interoperability-critical; incomplete DAG handling differs depending on pinning. Test signals are exact root/stat output, pin state, block size errors, and expected exit code 1 on pin failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0054-dag-car-import-export.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0055-dag-put-json-new-line.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0055-dag-put-json-new-line.sh

Purpose: regression test ensuring JSON put as CBOR retrieves without an added trailing newline.

Important control flow: creates JSON files with and without trailing newline, runs `ipfs dag put` as CBOR, asserts both hashes are equal and match the expected value, then retrieves by hash and verifies the output has no trailing newline.

State and dependencies: writes tiny JSON fixtures and stores a CBOR DAG block in the repo. Depends on `ipfs dag put/get`, codec normalization, and exact expected CID.

Risks: newline normalization is subtle and user-visible for byte-sensitive DAG data. Test signal is equal CIDs for equivalent JSON input and retrieval bytes without an extra newline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0055-dag-put-json-new-line.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0060-daemon.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0060-daemon.sh

Purpose: broad daemon command coverage for initialization, runtime addresses, API/gateway access, version/help output, transport security negotiation, streaming output, stdin pipe behavior, failure cleanup, and file descriptor limits.

Important control flow: creates a Pebble init config, runs daemon `--init` with profiles, verifies config materialization, sets resource manager env vars, launches a normal daemon, checks PeerID, swarm local/listen addresses, allowed-origin API/gateway requests, daemon output text, version/deps/help output, socat-based TLS/Noise/plaintext transport probes, streaming command output, manual daemon kill, daemon startup with stdin pipe, cleanup after failed start, and raised fd limit with `hang-fds`.

State and dependencies: creates `.ipfs`, daemon logs, API/gateway files, network listeners, and process state. Depends on `pollEndpoint`, curl, socat prereq, hang-fds, ulimit behavior, and daemon helper functions.

Risks: high platform and timing sensitivity, especially fd limits, socat probes, and process cleanup. Test signals are readiness, expected daemon output, security handshake acceptance/rejection, successful streaming output, and absence of daemon errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0060-daemon.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0061-daemon-opts.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0061-daemon-opts.sh

Purpose: focused daemon option tests for transport encryption disabling, offline gateway behavior, and invalid DHT option errors.

Important control flow: starts daemon with `--disable-transport-encryption` and, when `SOCAT` is available, verifies plaintext transport works; starts an offline daemon and confirms gateway access still works for locally available content; then asserts daemon startup fails for bad DHT options and deprecated/unsupported `supernode` mode with informative output.

State and dependencies: creates temporary repo/daemon state and network listeners. Depends on socat for plaintext probe, gateway/API readiness helpers, and exact daemon error text.

Risks: security-option behavior is sensitive; plaintext should only be enabled when explicitly requested. Error-message assertions may need updates if CLI wording changes. Test signals are plaintext availability under the flag, offline gateway success, and nonzero exits for invalid DHT modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0061-daemon-opts.sh -->
