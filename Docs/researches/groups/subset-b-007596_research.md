# subset-b-007596 research

Grouped research for Kubo core commands, CoreAPI, and core HTTP files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/repo_verify_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/repo_verify_test.go

Purpose: Go 1.25-only unit coverage for `ipfs repo verify` worker healing timeout behavior. It isolates `verifyWorkerRun` with mocked blockstore and CoreAPI block access so timeout logic can be tested with `testing/synctest` virtual time instead of real sleeps.

Important APIs/types/functions: `TestVerifyWorkerHealTimeout` contains subtests for successful heal before deadline, timeout failure, zero timeout meaning no deadline, concurrent multiple-block healing, and valid-block no-op behavior. `mockBlockstore`, `mockBlockAPI`, and `mockCoreAPI` implement the minimum interfaces needed by the worker: block reads, delete/put stubs, `Block().Get`, and CoreAPI method stubs.

Control flow: each corruption case sends one or more CIDs through `keys`, starts `verifyWorkerRun` in goroutines with a `sync.WaitGroup`, advances virtual time, waits, closes `results`, and asserts the resulting state/message. Mock `BlockAPI.Get` waits on `time.After(getDelay)` or returns `ctx.Err()` when the worker's heal context expires.

State and persistence behavior: no durable state is written. The mocked blockstore simulates corrupt or valid local blocks and the mocked block API simulates remote healing data. The test verifies in-memory result states such as `verifyStateCorruptHealed`, `verifyStateCorruptHealFailed`, and `verifyStateValid`.

Dependencies and integration points: depends on the production `verifyWorkerRun`, `verifyResult`, and verify state constants defined elsewhere in the commands package; uses `boxo/path`, Kubo `coreiface`, and `coreiface/options` only to satisfy interfaces.

Risks: build-tagged `go1.25`, so coverage is absent on older Go versions. The mocks cover timeout outcomes but not full CLI flags, repo traversal, block replacement durability, or network behavior. The concurrent subtest uses identical fast mock behavior for both blocks, so it does not actually exercise mixed success/failure outcomes despite the name.

Test signals: directly tests heal timeout semantics and explicitly points end-to-end coverage to `test/cli/repo_verify_test.go`. Failures here would indicate worker context/deadline regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/repo_verify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/resolve.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/resolve.go

Purpose: implements `ipfs resolve`, resolving IPNS, DNSLink, IPFS, and IPLD paths to immutable IPFS/IPLD targets while honoring recursive resolution and CID output encoding options.

Important APIs/types/functions: `ResolveCmd` is a `cmds.Command` with options `--recursive`, `--dht-record-count`, and `--dht-timeout`. It emits `name.ResolvedPath` and has a text encoder that prints the resolved path.

Control flow: the command gets a CoreAPI via `cmdenv.GetApi`. For non-recursive `/ipns/` names, it calls `api.Name().Resolve` with depth 1 and optional DHT record count/timeout, tolerating `namesys.ErrResolveRecursion` as a valid partial result. Other inputs choose a CID encoder from explicit global options or from the input path, parse with `cmdutils.PathOrCidPath`, resolve through `api.ResolvePath`, rebuild the path with the selected CID base, validates it with `path.NewPath`, and emits it.

State and persistence behavior: read-only. It may consult name-system caches, DHT/IPNS records, DNS, and block/path resolvers through CoreAPI, but it does not mutate repo state.

Dependencies and integration points: bridges CLI command parsing to CoreAPI `Name().Resolve` and `ResolvePath`. Uses `boxo/namesys` resolve options, `go-cidutil` encoders, and Kubo command environment helpers.

Risks: DHT timeout parsing rejects negative values but permits zero as no timeout. Non-recursive behavior is special-cased only for `/ipns/`; other mutable protocols are resolved through `ResolvePath`. Incorrect CID-base selection can alter output compatibility for scripts.

Test signals: no direct file-local tests; command-tree validation in `root_test.go` covers command schema. CoreAPI path behavior is covered by `coreapi/test/path_test.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/resolve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/root.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/root.go

Purpose: defines the root `ipfs` command, global options, command help, shared online errors, and the map of all top-level command implementations.

Important APIs/types/functions: `Root` is the top-level `cmds.Command`. Global option constants include repo/config/debug/offline/API/auth options plus CID base, encoding, stream, and timeout options. `rootSubcommands` wires commands such as add, block, repo, stats, dht, routing, swarm, update, version, and shutdown. `init` calls `Root.ProcessHelp()` and assigns subcommands. `MessageOutput` is a shared simple message struct.

Control flow: command registration is static. The root command itself primarily exposes help and global options; actual behavior delegates to subcommands. `CommandsDaemonCmd = CommandsCmd(Root)` allows the daemon command tree to expose command listing.

State and persistence behavior: no state mutation in this file. Options here affect downstream repo selection, offline mode, API endpoint/auth, output encoding, and command timeout handling.

Dependencies and integration points: central integration point for all core command packages and subpackages (`dag`, `name`, `object`, `pin`). Shared errors `ErrNotOnline` and `ErrSelfUnsupported` are referenced by network/DHT commands.

Risks: any omission or key collision in `rootSubcommands` hides or replaces CLI functionality. Global option naming must remain stable for scripts and RPC clients.

Test signals: `root_test.go` calls `Root.DebugValidate()` to catch malformed command definitions, argument/option conflicts, and encoder/type mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/root.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/root_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/root_test.go

Purpose: validates the entire registered command tree rooted at `Root`.

Important APIs/types/functions: `TestCommandTree` invokes `Root.DebugValidate()` and prints any returned errors grouped by command path.

Control flow: the test treats a nil error map as success; otherwise it records each command and validation error with `t.Errorf`.

State and persistence behavior: no durable state. It only inspects in-memory command definitions.

Dependencies and integration points: depends on `root.go` initialization and every subcommand attached to `Root`. It is a broad schema/sanity test rather than behavioral coverage.

Risks: validation catches structural command issues but not runtime command behavior, repo mutation, network behavior, or text/JSON output correctness beyond command metadata.

Test signals: a failure here usually points to malformed command declarations, incompatible encoders/types, or invalid argument/option definitions introduced anywhere in the root command tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/root_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/routing.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/routing.go

Purpose: implements `ipfs routing` subcommands for finding providers/peers, getting/putting routing records, and legacy provide/reprovide operations. Several commands are deprecated or experimental and proxy newer systems while keeping script compatibility.

Important APIs/types/functions: `RoutingCmd` registers `findprovs`, `findpeer`, `get`, `put`, `provide`, and `reprovide`. `provideCids`, `provideCidsRec`, `printEvent`, and `escapeDhtKey` are helpers. `errAllowOffline` rewrites offline put errors into a user-facing hint.

Control flow: provider/peer lookup requires an online node, wraps the request context with routing query event registration, starts async routing calls, publishes events, and emits each event. Legacy `routing provide` parses stdin arguments, checks `Provide.Enabled`, requires local blocks, starts provider records through `nd.Provider`, optionally walks DAGs recursively, and if a DHT client is active performs synchronous `provideCIDSync` for immediate announcement. `routing reprovide` checks legacy provider support and calls `provider.Reprovider.Reprovide`. `routing get` and `put` go through CoreAPI `Routing()`, base64-wrapping record bytes in query events for command transport.

State and persistence behavior: `put` writes routing records via CoreAPI and can write local-only IPNS data when `--allow-offline` is accepted by the routing layer. `provide` and `reprovide` mutate provider announcement state but not block data. Recursive provide walks local DAG data.

Dependencies and integration points: uses libp2p `routing.QueryEvent`, Kubo node routing/provider/DHTClient, CoreAPI routing, IPNS key parsing, CID parsing, blockstore/DAG service, and repo config `Provide.*`.

Risks: legacy recursive provide re-walks shared subgraphs and can re-announce duplicates. Event output is best-effort; some verbose provider events do not fully reflect provider-system internals. `put` validates IPNS names before emitting the peer ID, but routing validation still depends on record validators. Direct use of `nd.DHTClient` relies on `HasActiveDHTClient` to avoid typed-nil panics.

Test signals: no direct tests in this file. Related risk is covered indirectly by CoreAPI routing tests in the interface test suite and by `core_test.go` typed-nil DHT client tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/shutdown.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/shutdown.go

Purpose: implements `ipfs shutdown`, a daemon-only command that closes the running node.

Important APIs/types/functions: `daemonShutdownCmd` retrieves the node from command environment and calls `nd.Close()`.

Control flow: if the node cannot be retrieved, the error is returned. If `nd.IsDaemon` is false, it returns a client error "daemon not running". On daemon nodes it invokes `Close`; close errors are logged but not returned to the client.

State and persistence behavior: triggers node shutdown through `IpfsNode.Close`, which cascades through the node stop function and services. It does not directly flush state here, so correctness depends on lower-level close handlers.

Dependencies and integration points: depends on `cmdenv.GetNode`, shared package logger, and `core.IpfsNode` lifecycle.

Risks: close errors are swallowed after logging, so callers may see success even if a component reports shutdown failure. Command is meaningful only when executed against a daemon environment.

Test signals: no direct tests in this file. HTTP/server shutdown behavior is separately represented in `corehttp/corehttp.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/shutdown.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/stat.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/stat.go

Purpose: defines the `ipfs stats` command tree and implements bandwidth statistics under `ipfs stats bw`.

Important APIs/types/functions: `StatsCmd` wires `bw`, `repo`, `bitswap`, `dht`, `provide`, and `reprovide`. `statBwCmd` supports `--peer`, `--proto`, `--poll`, and `--interval`; `printStats` formats totals/rates.

Control flow: `statBwCmd` requires an online node and non-nil bandwidth reporter. It rejects simultaneous peer and protocol filters, decodes peer IDs, parses polling intervals, then emits either peer, protocol, or total bandwidth stats. In polling mode it loops until the request context is canceled, sleeping for the configured interval.

State and persistence behavior: read-only. It reads in-memory libp2p bandwidth counters and does not mutate repo or network state.

Dependencies and integration points: uses `cmdenv.GetNode`, libp2p metrics, peer/protocol types, command post-run CLI formatting, and `humanize` for byte output.

Risks: polling writes carriage-return terminal output and can run indefinitely until cancellation. Reporter-disabled configs return an error. Protocol/peer strings are not cross-validated against active connections.

Test signals: no direct tests here; command-tree validation covers schema. Runtime behavior depends on libp2p metrics reporter tests elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/stat_dht.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/stat_dht.go

Purpose: implements `ipfs stats dht`, returning routing table statistics for WAN/LAN DHT server/client tables and accelerated DHT clients.

Important APIs/types/functions: output structs `dhtPeerInfo`, `dhtStat`, and `dhtBucket`. `statDhtCmd` accepts DHT names (`wanserver`, `lanserver`, `wan`, `lan`) and emits one `dhtStat` per requested table.

Control flow: the command requires online mode and an initialized DHT. It defaults to `wan` and `lan`. For separate active accelerated DHT client (`DHTClient != DHT`), `wan` is reported from `fullrt.FullRT.Stat` and `lan` errors. Otherwise it selects the dual DHT WAN/LAN table, groups peers by common-prefix length against local identity, copies agent version, useful/query timestamps, connectedness, and bucket last-refresh timestamps, then emits stats.

State and persistence behavior: read-only. It inspects routing tables, peerstore metadata, and network connectedness.

Dependencies and integration points: integrates with Kubo `IpfsNode.HasActiveDHTClient`, libp2p-kad-dht dual/fullrt tables, kbucket prefix metrics, peerstore `AgentVersion`, and libp2p network connectedness.

Risks: accelerated client support assumes `*fullrt.FullRT`; other active DHT client types error. The text encoder checks `p.LastUsefulAt != ""` before parsing `LastQueriedAt`, so a peer with only `LastQueriedAt` set is printed as never queried; this looks like a formatting bug. Peerstore `AgentVersion` type assertions are defensive but unexpected errors are only logged.

Test signals: no direct tests here. `core_test.go` covers `HasActiveDHTClient`, which protects this command from typed-nil DHT clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/stat_dht.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/stat_provide.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/stat_provide.go

Purpose: deprecated compatibility shim for `ipfs stats provide`.

Important APIs/types/functions: `statProvideCmd` copies arguments, options, run function, encoders, and type from `provideStatCmd`.

Control flow: command execution is entirely delegated to `provideStatCmd`; only help/status differ.

State and persistence behavior: same as `provideStatCmd`, expected to be read-only provider statistics. This file itself has no state behavior.

Dependencies and integration points: depends on the provide command implementation being in the same package and stable enough for direct field reuse.

Risks: wrapper can drift in help text only; behavioral drift is avoided by direct delegation. It remains deprecated, so scripts should migrate to `ipfs provide stat`.

Test signals: command-tree validation covers structural correctness; provider stats behavior is covered where `provideStatCmd` is tested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/stat_provide.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/stat_reprovide.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/stat_reprovide.go

Purpose: deprecated compatibility shim for `ipfs stats reprovide`.

Important APIs/types/functions: `statReprovideCmd` delegates arguments, options, run function, encoders, and type to `provideStatCmd`.

Control flow: identical runtime behavior to `provideStatCmd`; only deprecation status and help text differ.

State and persistence behavior: expected read-only provider/reprovider stats via delegated command. This file has no direct state mutation.

Dependencies and integration points: keeps old command path alive while provider stats live under `ipfs provide stat`.

Risks: users may misread it as a separate reprovide-only statistic; help text explains provider stats are consolidated. Future removal can break legacy scripts.

Test signals: command-tree validation verifies schema; detailed behavior follows `provideStatCmd` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/stat_reprovide.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/swarm.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/swarm.go

Purpose: implements `ipfs swarm` networking commands for addresses, connections, peers, peering, resource-manager stats, and address filters.

Important APIs/types/functions: `SwarmCmd` registers `addrs`, `connect`, `disconnect`, `filters`, `peers`, `peering`, and experimental `resources`. Output helpers include `stringList`, `addrMap`, `peeringResult`, `connInfo`, `connInfos`, and `addrInfos`. Address helpers `parseAddresses` and `resolveAddresses` resolve DNS multiaddrs. Filter helpers mutate config: `filtersAdd`, `filtersRemoveAll`, and `filtersRemove`.

Control flow: peering add/rm parse multiaddrs or peer IDs and call `node.Peering` methods; peering changes are explicitly not persisted. `swarm peers` obtains CoreAPI connections, optionally enriches with latency, streams, direction, and identify data from peerstore. `resources` recomputes configured libp2p limits, merges live resource-manager stats, and emits text/JSON. `addrs` lists known/local/listen addresses via CoreAPI. `connect` resolves peer addresses then calls CoreAPI `Swarm().Connect`; `disconnect` resolves addresses then closes matching connections. `filters` lists in-memory deny filters; add/rm update both `n.Filters` and the repo config opened via `fsrepo.Open`.

State and persistence behavior: connects/disconnects mutate live libp2p network state and connection-manager tags via CoreAPI. Peering commands mutate live peering service only, not config. Filter add/rm persist `Swarm.AddrFilters` using `Repo.SetConfig` and also mutate live filters. Resource stats and address listings are read-only.

Dependencies and integration points: uses CoreAPI `Swarm`, command environment node/config root, libp2p peerstore/network/protocol/resource-manager, Kubo `libp2p.LimitConfig`, multiaddr DNS resolver, multiaddr-filter parsing, and fsrepo config persistence.

Risks: `resolveAddresses` launches DNS resolution goroutines and reports one buffered error after collecting results; simultaneous errors are collapsed. It assumes a non-nil DNS resolver for non-`/p2p` addresses. Filter config updates open the repo separately and can race with other config writers. Peering runtime changes disappear after daemon restart. `swarm peers --identify` ignores `identifyPeer` errors.

Test signals: no local tests. Behavioral coverage is largely through CoreAPI swarm interface tests and command-tree validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/swarm_addrs_autonat.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/swarm_addrs_autonat.go

Purpose: implements `ipfs swarm addrs autonat`, reporting AutoNAT V2 overall and per-address reachability.

Important APIs/types/functions: `reachabilityHost` and `confirmedAddrsHost` are small capability interfaces checked against `nd.PeerHost`. `autoNATResult` is the JSON/text output. Helpers convert multiaddrs to strings and render address sections.

Control flow: command requires an online node. It defaults reachability to unknown, then conditionally reads `ConfirmedAddrs` for reachable/unreachable/unknown address lists and `Reachability` for overall state. It adds best-effort NAT classification through `libp2p.DetectNAT`, emits the result, and text-encodes a human-readable report.

State and persistence behavior: read-only. It reports live AutoNAT/libp2p host state and does not mutate repo, peerstore, or network.

Dependencies and integration points: depends on the libp2p host implementation exposing optional methods from embedded BasicHost/AutoNAT V2 support, Kubo libp2p NAT detection, and shared `ErrNotOnline`.

Risks: when host capabilities are absent, it returns unknown/empty data rather than an error. NAT classification is best-effort and may be empty. Text output can show no per-address data even when overall reachability is known.

Test signals: no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/swarm_addrs_autonat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/sysdiag.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/sysdiag.go

Purpose: implements system diagnostic output used for support/debugging.

Important APIs/types/functions: `sysDiagCmd` emits `getInfo(nd)`; helper functions populate runtime, environment, disk, memory, and network maps.

Control flow: command obtains node, builds a `map[string]any`, sequentially calls `runtimeInfo`, `envVarInfo`, `diskSpaceInfo`, `memInfo`, and `netInfo`, then adds Kubo version and commit.

State and persistence behavior: read-only. It reads environment variables, repo root path, disk usage, memory info, network interface addresses, and node online status.

Dependencies and integration points: uses `config.PathRoot`, `go-sysinfo` disk/memory helpers, `manet.InterfaceMultiaddrs`, runtime package, and Kubo version constants.

Risks: diagnostics may expose environment paths and interface addresses. Any helper error aborts the whole command. Memory field names are terse (`swap`, `virt`) and depend on go-sysinfo semantics.

Test signals: no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/sysdiag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/update.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/update.go

Purpose: implements experimental local `ipfs update` commands for checking, listing, installing, reverting, and cleaning Kubo binaries from GitHub Releases.

Important APIs/types/functions: `UpdateCmd` is `NoRemote` and repo/config-input independent. Outputs include `UpdateCheckOutput`, `UpdateVersionsOutput`, `UpdateInstallOutput`, `UpdateRevertOutput`, and `UpdateCleanOutput`. Helpers cover context timeout, daemon lock check, stash path management, binary replacement, archive extraction, and semver comparison.

Control flow: `check` gets latest release with platform asset and compares versions. `versions` lists releases. `install` refuses to run while daemon lock is active when detectable, resolves target tag, rejects same/older versions unless forced, downloads and verifies archive, extracts `kubo/ipfs`, resolves current executable path, stashes current binary under `$IPFS_PATH/old-bin`, and atomically replaces it or writes a temp fallback on permission errors. `revert` finds newest semver-named stash, reads it, replaces the current binary or writes fallback, then removes restored stash. `clean` deletes semver-named stashes and reports freed bytes.

State and persistence behavior: mutates the local executable and `$IPFS_PATH/old-bin` stash directory. Uses `atomicfile.New` for replacement, `fsrepo.BestKnownPath` for stash location, `dst.Sync` and temp file sync/chmod for durability. It does not open or mutate repo config.

Dependencies and integration points: relies on GitHub helpers in `update_github.go`, Kubo version constants, fsrepo lock detection, migration executable naming for `.exe`, `hashicorp/go-version`, and fsrepo migrations `atomicfile`.

Risks: trust boundary is GitHub API/CDN plus SHA-512 sidecar fetched from adjacent URL; it verifies integrity but not an independent signature. Lock check warnings allow proceeding when repo path/lock cannot be checked. Stashing happens before replacement, so permission fallback can leave an extra backup. Archive extraction limits decompressed binary size but does not inspect file mode or signatures.

Test signals: `update_github_test.go` covers helper hashing/API/archive behavior. CLI/integration tests referenced by comments cover `TEST_KUBO_VERSION` and mock GitHub URL flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/update_github.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/update_github.go

Purpose: implements GitHub Release discovery, asset download, checksum download, SHA-512 verification, and platform asset naming for `ipfs update`.

Important APIs/types/functions: `ghRelease`, `ghAsset`, `githubGet`, `githubToken`, `githubLatestRelease`, `githubListReleases`, `githubReleaseByTag`, `findReleaseAsset`, `downloadAsset`, `downloadAndVerifySHA512`, `verifySHA512`, and `assetNameForPlatformTag`.

Control flow: API calls use `githubReleaseBaseURL`, which can be overridden only through `TEST_KUBO_UPDATE_GITHUB_URL`. `githubGet` sets GitHub JSON accept headers, Kubo user agent, and optional bearer token, then maps 403/429 to rate-limit errors. Release listing over-fetches when prereleases are excluded. Latest release scans for a matching platform asset. Downloads stream through `io.LimitReader` capped at 200 MiB. Checksum verification downloads `archiveURL + ".sha512"`, parses the first field as hex, and compares to `sha512.Sum512(data)`.

State and persistence behavior: no durable state; all downloads are in-memory. Environment variables `GITHUB_TOKEN`/`GH_TOKEN` affect API auth, and test env var affects base URL.

Dependencies and integration points: used by `update.go`; depends on `net/http`, `runtime.GOOS/GOARCH`, Kubo current version for User-Agent, and GitHub release asset naming convention.

Risks: checksum sidecar is fetched from the same distribution origin as the archive, so it detects corruption but not compromise of release assets. No retry/backoff. `githubListReleases` can return fewer than requested if more than 3x prereleases appear before stable releases. Download limit protects memory but still reads full allowed payload into memory.

Test signals: `update_github_test.go` provides extensive unit coverage for headers, rate-limit errors, release filtering, asset lookup, download errors, checksum verification, archive extraction, and version helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/update_github.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/update_github_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/update_github_test.go

Purpose: unit tests for the GitHub/update helper layer that protects `ipfs update install` from malformed metadata, failed downloads, and checksum mismatches.

Important APIs/types/functions: tests cover `verifySHA512`, `downloadAndVerifySHA512`, `githubGet`, `githubListReleases`, `githubLatestRelease`, `findReleaseAsset`, `downloadAsset`, `extractBinaryFromArchive`, `assetNameForPlatformTag`, `trimVPrefix`, `normalizeVersion`, and `isNewerVersion`. `makeTarGz` builds in-memory archives.

Control flow: most tests use `httptest.Server`; tests that override package-level `githubReleaseFmt` are intentionally not parallel and restore the var with `t.Cleanup`. Other tests use `t.Parallel`. Assertions verify both happy paths and clear error messages.

State and persistence behavior: no durable state. Temporary HTTP servers and package variable overrides are cleaned up. Archive data is in-memory.

Dependencies and integration points: validates `update_github.go` and parts of `update.go` archive/version helpers. Uses runtime OS/arch to assert platform-dependent asset names.

Risks: tests do not cover real GitHub pagination, redirects, proxy behavior, auth token presence, zip extraction, permission fallback, actual binary replacement, or daemon lock behavior. Package global override requires non-parallel grouping for affected tests.

Test signals: strong local signal for integrity checks and API error mapping. A failure likely indicates a direct regression in update safety or release metadata assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/update_github_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/version.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/version.go

Purpose: implements `ipfs version`, dependency reporting, and swarm-based version-check heuristics.

Important APIs/types/functions: `VersionCmd`, `depsVersionCommand`, `checkVersionCommand`, output structs `Dependency` and `VersionCheckOutput`, and `DetectNewKuboVersion`.

Control flow: root version command emits `version.GetVersionInfo()` and text-encodes number/commit/repo/all variants. `deps` reads embedded Go build info and emits main plus dependencies, including replacements. `version check` requires online mode, reads a percentage threshold, and calls `DetectNewKuboVersion`. Detection parses local version, samples peerstore `AgentVersion` values from accelerated fullrt client or dual DHT WAN/LAN tables, ignores non-Kubo and pre/dev versions, counts peers running greater stable versions, and returns whether the fraction meets threshold.

State and persistence behavior: read-only. It reads build metadata, repo version info, DHT routing tables, and peerstore metadata.

Dependencies and integration points: integrates with Kubo version/config defaults, libp2p peerstore and fullrt DHT, `IpfsNode.HasActiveDHTClient`, and `hashicorp/go-version`.

Risks: type assertion `v.(string)` in `processPeerstoreEntry` can panic if peerstore stores non-string `AgentVersion`; other files guard this assertion. Sampling depends on DHT availability and may miss connected peers not in DHT tables. Threshold option name says min-percent but help mentions min-fraction in text.

Test signals: no direct tests in this file. `core_test.go` protects DHT client activity detection used by version checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/core.go -->
# sources/distributed-fs/ipfs-kubo/core/core.go

Purpose: defines the central `IpfsNode` runtime object and core lifecycle helpers for context, shutdown, bootstrap, DHT-client detection, and temporary bootstrap peer persistence.

Important APIs/types/functions: `IpfsNode` aggregates identity, repo, pinning, block/DAG services, fetchers, path resolvers, networking, routing/provider/DHT, pubsub, P2P, and lifecycle flags. `Mounts`, `Close`, `HasActiveDHTClient`, `Context`, `Bootstrap`, `TempBootstrapPeersKey`, `loadBootstrapPeers`, `saveTempBootstrapPeers`, `loadTempBootstrapPeers`, and `ConstructPeerHostOpts` are defined here.

Control flow: `Close` delegates to the node stop function. `Context` lazily falls back to `context.TODO`. `HasActiveDHTClient` rejects nil, routinghelpers.Null, and typed-nil dual/fullrt DHT clients before treating a client as usable. `Bootstrap` no-ops without routing, closes an existing bootstrapper, installs config-backed peer loading and datastore-backed backup peer save/load when absent, applies backup interval from config, then calls `bootstrap.Bootstrap`.

State and persistence behavior: `saveTempBootstrapPeers` writes JSON-encoded bootstrap peer strings into repo datastore key `/local/temp_bootstrap_peers` and syncs that key. `loadTempBootstrapPeers` reads and parses it. `Bootstrap` mutates `n.Bootstrapper` and may close the previous one.

Dependencies and integration points: this struct is the dependency injection hub for CoreAPI, commands, HTTP, node construction, libp2p services, block services, namesys, provider systems, and repo/config.

Risks: `Close` assumes `stop` is non-nil. Lazy `Context` fallback can mask missing initialization. `HasActiveDHTClient` only knows specific nil/no-op types, so custom routing implementations may be treated as active without deeper validation. Temporary bootstrap peer datastore errors are logged and ignored in bootstrap callbacks.

Test signals: `core_test.go` covers node initialization and DHT-client typed-nil/no-op/valid cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/core.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/core_test.go -->
# sources/distributed-fs/ipfs-kubo/core/core_test.go

Purpose: tests basic node construction and `IpfsNode.HasActiveDHTClient` behavior, especially typed-nil interface hazards.

Important APIs/types/functions: `TestInitialization`, `testIdentity`, `mockHostOption`, and `TestHasActiveDHTClient`.

Control flow: initialization tests create mock repos with good/bad config and expect `NewNode` success/failure. DHT-client tests cover nil interface, typed nil `*ddht.DHT`, typed nil `*fullrt.FullRT`, `routinghelpers.Null`, a valid dual DHT node built on mocknet, and a valid accelerated fullrt client.

State and persistence behavior: uses in-memory datastore/keystore and temporary filestore paths. Valid node cases construct live mocknet/libp2p nodes and close them after assertions.

Dependencies and integration points: integrates with `repo.Mock`, Kubo `NewNode`, libp2p DHT options, mocknet host option, filestore, keystore, and config identity/address setup.

Risks: tests depend on constructing DHT services under mocknet, so they are heavier than pure unit tests. They validate known nil/no-op types but not arbitrary custom routing clients.

Test signals: strong regression coverage for the typed-nil interface bug that affects DHT stats/version/routing commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/core_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/block.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/block.go

Purpose: implements CoreAPI block operations for raw block put/get/remove/stat.

Important APIs/types/functions: `BlockAPI`, `BlockStat`, and methods `Put`, `Get`, `Rm`, `Stat`, plus `BlockStat.Size`/`Path`.

Control flow: `Put` parses options, reads all source bytes, builds a CID with the selected prefix, constructs a block, optionally acquires pin lock, adds the block, optionally recursively pins and flushes. `Get` and `Stat` resolve the input path then fetch the root block. `Rm` resolves the path, calls `blockstoreutil.RmBlocks` with force settings, and consumes one result or context cancellation.

State and persistence behavior: `Put` writes blocks to blockservice/blockstore and may update pin state. Pinning flushes pinner state. `Rm` removes blockstore data subject to pin constraints. Reads are non-mutating.

Dependencies and integration points: uses Kubo tracing, `coreiface/options`, blockstore util removal, boxo path/pinning/block APIs, and CoreAPI path resolution.

Risks: `Put` reads the entire block into memory, appropriate for block API but risky for unbounded callers. Pin lock is only taken when pinning. `Rm` consumes only the first removal result, which matches single-CID removal but would need care if expanded.

Test signals: covered through CoreAPI interface tests in `coreapi/test/api_test.go`; repo verify tests use a mocked `BlockAPI.Get`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/coreapi.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/coreapi.go

Purpose: constructs the experimental embeddable Kubo CoreAPI facade over an `IpfsNode` and exposes typed sub-APIs.

Important APIs/types/functions: `CoreAPI` stores node services and option state. `NewCoreAPI`, sub-API accessors (`Unixfs`, `Block`, `Dag`, `Name`, `Key`, `Object`, `Pin`, `Swarm`, `PubSub`, `Routing`), `WithOptions`, and `getSession`.

Control flow: `NewCoreAPI` initializes default API settings then calls `WithOptions`. `WithOptions` copies parent settings, applies options, copies node dependencies into a new CoreAPI value, installs `checkOnline` and `checkPublishAllowed` closures, reads repo config, and if offline constructs an offline namesys/routing stack and clears peerstore/host/validator. If offline or fetch-blocks disabled, it replaces exchange/blockservice/DAG with offline local-only variants. `getSession` returns a shallow copy with a read-only session DAG.

State and persistence behavior: construction is mostly read-only, but returned APIs mutate underlying node services when sub-APIs are used. Offline options redirect reads/writes to local datastore/router behavior without changing the node. `checkPublishAllowed` prevents manual IPNS publish while IPNS mount is active unless the fusemount context marks a publish.

Dependencies and integration points: central bridge from `core.IpfsNode` to `coreiface`. Integrates namesys, offline routing, blockservice, path resolvers, repo config, fuse mount context, pubsub, provider, and tracing-enabled sub-APIs.

Risks: `WithOptions` requires `api.nd`; manually constructed CoreAPI without node cannot apply options. Offline mode clears several fields, so sub-APIs that assume peerHost/peerstore must return offline errors. Config errors prevent API creation.

Test signals: `coreapi/test/api_test.go` runs the shared CoreAPI interface suite against this implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/coreapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/dag.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/dag.go

Purpose: wraps the node DAG service for CoreAPI and provides DAG adders that also pin.

Important APIs/types/functions: `dagAPI` embeds `ipld.DAGService`; `pinningAdder` implements `ipld.NodeAdder`; methods `Add`, `AddMany`, `Pinning`, and `Session`.

Control flow: `pinningAdder.Add` locks the blockstore pin lock, adds a node to DAG, pins it recursively, and flushes. `AddMany` adds all nodes first, deduplicates CIDs with a CID set, pins each unique CID recursively, and flushes. `Pinning` returns a node adder backed by the CoreAPI. `Session` returns a merkledag session getter.

State and persistence behavior: writes DAG blocks and pin state, flushing pins for durability. Uses pin lock to coordinate with garbage collection.

Dependencies and integration points: used by CoreAPI `Dag()`. Depends on boxo merkledag/session, pinning pinner, blockstore pin locking, and tracing.

Risks: `AddMany` adds DAG nodes before pinning; partial failure after add but before all pins can leave unpinned blocks. Recursive pinning every unique node may be expensive for large batches.

Test signals: interface-level DAG behavior is exercised by `coreapi/test/api_test.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/dag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/key.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/key.go

Purpose: implements CoreAPI key management plus signing and verification over Kubo/libp2p keys.

Important APIs/types/functions: `KeyAPI`, private `key` implementation, `newKey`, methods `Generate`, `List`, `Rename`, `Remove`, `Self`, `Sign`, and `Verify`, and `signedMessagePrefix`.

Control flow: generation rejects `self`, checks for existing key, creates RSA or Ed25519 private/public keys, stores private key in repo keystore, derives peer ID, and returns an IPNS key object. Listing includes `self` first, sorts keystore names, skips unreadable/bad keys with logs. Rename rejects `self`, fetches old key, optionally deletes destination when forced, writes new key, then deletes old. Remove rejects `self`, derives removed peer ID, deletes key, and returns key info. Sign chooses self or keystore key, prefixes data with a domain string, and signs. Verify accepts self, keystore name, IPNS name, or PeerID with embedded public key, prefixes data the same way, and verifies.

State and persistence behavior: `Generate`, `Rename`, and `Remove` mutate repo keystore. `Sign` and `Verify` are read-only. No explicit keystore sync is visible here; durability is delegated to the keystore implementation.

Dependencies and integration points: used by name publishing and CLI key commands. Integrates repo keystore, libp2p crypto/peer IDs, IPNS name paths, CoreAPI options, and tracing.

Risks: rename is not atomic: after writing new key, delete old can fail, leaving duplicates. Force rename deletes destination before writing old key, so a later write failure can lose destination. Verify by PeerID only works when the public key can be extracted from the peer ID.

Test signals: covered through CoreAPI interface tests; no file-local unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/name.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/name.go

Purpose: implements CoreAPI IPNS publish, search, resolve, and key lookup.

Important APIs/types/functions: `NameAPI` methods `Publish`, `Search`, `Resolve`, and helper `keylookup`.

Control flow: `Publish` checks mount/publish restrictions, parses options, handles delegated publishing mode by requiring configured delegated publishers, otherwise checks online status respecting allow-offline, resolves the private key by name or PeerID, builds EOL/TTL/sequence/v1-compat publish options, calls namesys `Publish`, and returns the IPNS name for the key. `Search` checks online permissively, optionally creates a cache-bypassing namesys resolver, normalizes names to `/ipns/`, starts `ResolveAsync`, and streams results to an output channel. `Resolve` consumes `Search` results until completion or first error and returns the last path.

State and persistence behavior: `Publish` writes IPNS records through the configured namesys/routing stack, which may be local datastore, DHT, or delegated publisher depending on options/config. Search/resolve are read-only but may consult caches and network.

Dependencies and integration points: integrates with CoreAPI key management, repo config `Ipns.DelegatedPublishers`, namesys, routing, DNS resolver, keystore, fusemount publish context, and libp2p peer IDs.

Risks: delegated mode only checks delegated publisher configuration before calling namesys; actual remote publish failures surface later. `Resolve` returns the last successful async result, which is intentional for newer records but depends on namesys stream ordering. Key lookup by PeerID scans the full keystore.

Test signals: covered by CoreAPI interface tests; path/name resolution also indirectly covered by `resolve.go` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/object.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/object.go

Purpose: implements DAG-PB object link add/remove/diff operations for CoreAPI with UnixFS safety checks.

Important APIs/types/functions: `ObjectAPI`, output shapes `Link` and `Node`, methods `AddLink`, `RmLink`, `Diff`, and `core`.

Control flow: add/remove resolve base and child paths, require base as `*dag.ProtoNode`, and unless validation is skipped, parse UnixFS data to permit only plain directories. HAMT shards and file-like UnixFS nodes are rejected because dag-pb link edits would corrupt UnixFS metadata. It then uses `dagutils.Editor` to insert/remove and finalize a new DAG node. `Diff` resolves before/after nodes, calls `dagutils.Diff`, and maps changes to CoreAPI paths.

State and persistence behavior: add/remove write new DAG nodes to the DAG service but do not mutate the original CID and do not pin by themselves. Diff is read-only.

Dependencies and integration points: relies on CoreAPI path resolution, boxo merkledag/dagutils/unixfs, and object command options for skip validation.

Risks: skip-validation can intentionally create invalid UnixFS DAGs. No pinning means new object CIDs may be garbage-collected unless pinned elsewhere. Validation only understands DAG-PB UnixFS data; non-UnixFS DAG-PB requires explicit override.

Test signals: likely covered by CoreAPI interface/object tests in the shared suite; no file-local tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/path.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/path.go

Purpose: implements CoreAPI path and node resolution over namesys plus IPFS/IPLD path resolvers.

Important APIs/types/functions: `CoreAPI.ResolveNode` and `CoreAPI.ResolvePath`.

Control flow: `ResolveNode` calls `ResolvePath` then fetches the resolved root CID from DAG. `ResolvePath` resolves mutable names through `namesys.Resolve`, maps missing namesys to `coreiface.ErrOffline`, selects IPLD or UnixFS resolver by namespace, converts to immutable path, resolves to the last node and remainder, rebuilds a sanitized path from namespace/root/remainder, and returns the immutable path plus unresolved remainder.

State and persistence behavior: read-only. It may fetch blocks through configured online/offline DAG/resolver stack and may consult namesys cache/network.

Dependencies and integration points: central dependency for block, UnixFS, pin, routing, object, and resolve commands. Uses boxo path/namesys/path resolver and Kubo tracing.

Risks: only IPFS and IPLD namespaces are supported after namesys resolution. Resolver behavior depends on whether CoreAPI was created offline or with fetch disabled. Errors from mutable names can become offline errors for callers.

Test signals: `coreapi/test/path_test.go` targets UnixFS HAMT partial-resolution timeout behavior through this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/pin.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/pin.go

Purpose: implements CoreAPI pin add/list/check/remove/update/verify operations.

Important APIs/types/functions: `PinAPI`, methods `Add`, `Ls`, `IsPinned`, `Rm`, `Update`, `Verify`, helper `pinLsAll`, and output implementations `pinStatus`, `badNode`, and `pinInfo`.

Control flow: add resolves a node, parses recursive/name options, locks pin state, pins and flushes. Listing validates pin type then delegates to `pinLsAll`, which streams recursive/direct pins and optionally walks recursive DAGs to emit indirect pins while deduplicating. `IsPinned` resolves path and checks pin mode. Remove/update resolve paths, lock, mutate pinner, and flush. Verify builds an offline DAG service over the blockstore, recursively walks each recursive pin, memoizes visited CIDs, and streams status objects with bad node paths/errors.

State and persistence behavior: add/remove/update mutate pinner state and flush for durability. Listing/checking/verify are read-only, though verify can be expensive over local blockstore.

Dependencies and integration points: integrates CoreAPI resolution, pinner, blockstore pin locks, boxo merkledag walk, offline block exchange, and tracing.

Risks: `pinLsAll` requires callers to drain channels or goroutines can leak, as noted in comment. Recursive/indirect listing can be expensive and context-sensitive. Verify only checks recursive pins. Partial failures during walks return errors or bad nodes but do not repair.

Test signals: covered through CoreAPI interface tests; repo verify is a separate block-integrity command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/pin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/pubsub.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/pubsub.go

Purpose: implements experimental CoreAPI pubsub topic listing, peer listing, publish, subscribe, and message wrappers.

Important APIs/types/functions: `PubSubAPI`, `pubSubSubscription`, `pubSubMessage`, methods `Ls`, `Peers`, `Publish`, `Subscribe`, `checkNode`, subscription `Close`/`Next`, and message accessors.

Control flow: every operation calls `checkNode`, which requires pubsub enabled and online mode. `Ls` returns topics, `Peers` parses options and lists peers for optional topic, `Publish` sends data, `Subscribe` validates options and creates a libp2p pubsub subscription. `Next` blocks on subscription next with context.

State and persistence behavior: no repo persistence. Publish sends network pubsub messages; subscribe mutates in-memory pubsub subscription state until canceled.

Dependencies and integration points: wraps libp2p pubsub, CoreAPI online checks, routing presence, and coreiface pubsub abstractions.

Risks: feature-gated by daemon pubsub enablement; otherwise commands return an explicit experimental feature error. Deprecated libp2p pubsub methods are used with nolint markers. Subscription option discovery is parsed but no-op because discovery is handled by pubsub.

Test signals: shared CoreAPI tests can cover pubsub when `NodeProvider` enables `"pubsub": true`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/routing.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/routing.go

Purpose: implements CoreAPI routing get/put/find/provide operations over libp2p routing and Kubo provider systems.

Important APIs/types/functions: `RoutingAPI`, methods `Get`, `Put`, `FindPeer`, `FindProviders`, `Provide`, helper `normalizeKey`, and recursive helper `provideKeysRec`.

Control flow: `Get` requires node online and fetches normalized key value. `Put` parses allow-offline option, checks online accordingly, normalizes key, and stores value. `FindPeer` and `FindProviders` require online mode; provider lookup resolves the path to a root CID and validates provider count. `Provide` resolves a path, verifies the root block is local, then either starts single-CID providing or recursively walks the local DAG in an offline DAG service, streaming unique CIDs into a multihash slice before one `StartProviding`.

State and persistence behavior: `Put` writes routing records through routing backend; with offline router it can store local records in datastore. `Provide` mutates provider advertisement state. Reads may query network and local routing.

Dependencies and integration points: used by `commands/routing.go` and external CoreAPI callers. Integrates blockstore, provider, routing validators, path resolution, cidutil streaming sets, and tracing.

Risks: `Get` checks `api.nd.IsOnline` directly rather than `checkOnline`, so offline option semantics differ from `Put`. Recursive provide accumulates all multihashes in memory before announcing. `provideKeysRec` has careful errCh race handling; regressions here can hide DAG walk errors or hang on context cancellation.

Test signals: covered by CoreAPI interface tests and provider-related tests. Command-level routing uses this implementation for get/put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/swarm.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/swarm.go

Purpose: implements CoreAPI swarm networking operations.

Important APIs/types/functions: `SwarmAPI`, private `connInfo`, constants `connectionManagerTag` and `connectionManagerWeight`, methods `Connect`, `Disconnect`, `KnownAddrs`, `LocalAddrs`, `ListenAddrs`, `Peers`, and `connInfo` accessors.

Control flow: `Connect` requires peerHost, clears libp2p swarm backoff when possible, connects, and tags the peer in the connection manager. `Disconnect` splits a multiaddr into transport address and peer ID, closes all peer connections when no transport is specified, or closes the matching connection. Address methods read peerstore/local/listen addresses. `Peers` maps each live connection to a `ConnectionInfo` wrapper with peerstore, direction, address, and stream access.

State and persistence behavior: connects/disconnects mutate live libp2p network state and connection-manager tags. Address/peer listing is read-only. No repo persistence.

Dependencies and integration points: used by `commands/swarm.go`; wraps libp2p host/network/swarm, peerstore EWMA latency, stream protocols, and coreiface error types.

Risks: `Disconnect` returns after closing the first matching connection for a specific address; multiple matching connections are not all closed. Connection-manager tagging keeps explicit connections preferred until other logic removes tags. Offline mode is represented by nil peerHost.

Test signals: exercised by CoreAPI swarm interface tests in `coreapi/test/api_test.go`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/test/api_test.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/test/api_test.go

Purpose: adapts Kubo CoreAPI to the shared `coreiface/tests` suite by providing in-memory/mocknet node swarms.

Important APIs/types/functions: `NodeProvider.MakeAPISwarm` and `TestIface`.

Control flow: for each requested node, it generates full identities when requested or uses a fixed peer ID, builds a config with swarm address, filestore enabled, AutoTLS disabled, and provider strategy `roots`, creates a mock repo with map datastore/mem keystore/filestore, constructs `core.NewNode` with mock host and DHT server option, enables pubsub, wraps it with `coreapi.NewCoreAPI`, links all mocknet peers, and bootstraps non-first nodes to the first when online. `TestIface` passes the provider to the shared API test suite.

State and persistence behavior: test-only in-memory repo state plus temporary filestore directory. Network state lives in mocknet and is linked/bootstraped per test.

Dependencies and integration points: covers broad CoreAPI behavior across UnixFS, block, dag, name, key, pin, object, swarm, pubsub, and routing through `coreiface/tests`.

Risks: shared tests only cover behavior represented in the external interface suite. Mocknet differs from real transports/NAT/resource-manager behavior. Full identities are optional, so tests relying on private keys must request them.

Test signals: primary integration signal for CoreAPI conformance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/test/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/test/path_test.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/test/path_test.go

Purpose: regression test for resolving partially missing UnixFS HAMT-sharded directories.

Important APIs/types/functions: `TestPathUnixFSHAMTPartial`.

Control flow: creates one online full-identity API node, temporarily forces HAMT sharding size to 1, builds a directory large enough for multiple HAMT levels, adds it without pinning, fetches the root DAG-PB node, removes one shard block, then attempts to resolve every child path with a one-second timeout. Errors are accepted only when the timeout context expired.

State and persistence behavior: writes test DAG blocks, removes one block through `Block().Rm`, and leaves all state in the test repo/mocknet. Restores global `uio.HAMTShardingSize` afterward.

Dependencies and integration points: exercises UnixFS add, DAG get, block remove, and CoreAPI path resolution over HAMT directories with missing blocks.

Risks: mutates a package global (`uio.HAMTShardingSize`) and must restore it; parallel execution would be unsafe, but the test is not parallel. Expected timeout behavior means it tolerates network lookup delays rather than checking a specific error type.

Test signals: protects against incorrect partial HAMT path resolution returning wrong nodes or non-timeout errors when shard blocks are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/test/path_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/unixfs.go -->
# sources/distributed-fs/ipfs-kubo/core/coreapi/unixfs.go

Purpose: implements CoreAPI UnixFS add/get/list operations.

Important APIs/types/functions: `UnixfsAPI` methods `Add`, `Get`, `Ls`, helper methods `processLink`, `lsFromDirLinks`, `lsFromLinks`, `core`, and `syncDagService`.

Control flow: `Add` parses many UnixFS add options, reads repo config, validates `--nocopy` against filestore/urlstore enablement, selects a blockstore/exchange/pinner strategy for normal, cache/nocopy, or only-hash mode, builds a blockservice/DAG service wrapped in `syncDagService`, configures a `coreunix.Adder` with chunker/layout/CID/raw leaf/pin/metadata/HAMT options, optionally wraps CID builder for inline CIDs, creates a mock MFS root for only-hash, and calls `AddAllAndPin`. `Get` resolves a node through a read-only session and returns a UnixFS file. `Ls` resolves a node, treats directories via `uio.Directory`, otherwise lists raw links; `processLink` resolves child metadata when requested.

State and persistence behavior: normal add writes blocks to blockstore, syncs block and filestore datastore prefixes through `syncDagService`, and may pin. `OnlyHash` uses null datastore/mock DAG and does not persist or pin. `NoCopy` may write filestore references depending on configuration. Get/list are read-only but may fetch blocks.

Dependencies and integration points: core path for CLI `add/get/ls` via CoreAPI. Integrates repo config, blockstore/baseBlocks, exchange, pinning, filestore, MFS, coreunix adder, UnixFS HAMT/file metadata, CID builders, and tracing.

Risks: add option surface is broad; incorrect combinations can affect persistence, pinning, or CID determinism. Only-hash uses mock MFS root to avoid writes. Listing can block or return nil on context cancellation in `lsFromDirLinks`, and `lsFromLinks` sends to output without a context select while draining buffered links.

Test signals: heavily exercised by shared CoreAPI tests and `path_test.go` HAMT partial-resolution regression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/coreapi/unixfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/commands.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/commands.go

Purpose: mounts the command tree under the HTTP RPC API, configures CORS/headers, optional RPC auth secrets, and client/daemon API version checks.

Important APIs/types/functions: constants `APIPath`, `errAPIVersionMismatch`, CORS origin lists, helpers `addCORSFromEnv`, `addHeadersFromConfig`, `addCORSDefaults`, `patchCORSVars`, `commandsOption`, `convertAuthorizationsMap`, `withAuthSecrets`, `CommandsOption`, and `CheckVersionOption`.

Control flow: `commandsOption` builds a `cmdsHttp.ServerConfig`, adds allowed headers/methods, reads repo config, applies configured headers/CORS, env-origin override, defaults, and listener port substitution, creates the command HTTP handler, wraps it with auth-secret middleware if configured, wraps with OpenTelemetry/metrics labels, and mounts at `/api/v0/`. Auth middleware allows `/api/v0/version` implicitly and otherwise requires exact Authorization header matching a converted configured secret and path prefix allowlist. Version middleware intercepts API paths and rejects Kubo/go-ipfs User-Agent mismatches except for the version endpoint.

State and persistence behavior: read-only. It copies config headers into server config to avoid races with shared config. Environment variable `API_ORIGIN` can append allowed origins with a deprecation warning.

Dependencies and integration points: integrates command tree `corecommands.Root`, `go-ipfs-cmds/http`, Kubo config `API.HTTPHeaders` and `API.Authorizations`, HTTP server mux, OpenTelemetry HTTP instrumentation, and API version constants.

Risks: auth compares the raw Authorization header string against converted secrets; prefix allowlists must be configured carefully to avoid overbroad access. CORS defaults include localhost and browser-extension origins. Version check depends on User-Agent formatting and skips non-Kubo clients.

Test signals: no local tests in this file; HTTP API behavior is likely covered by daemon/RPC integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/commands.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/corehttp.go -->
# sources/distributed-fs/ipfs-kubo/core/corehttp/corehttp.go

Purpose: provides generic HTTP serving helpers for Kubo core HTTP interfaces.

Important APIs/types/functions: `ServeOption`, `MakeHandler`, `ListenAndServe`, `Serve`, and `ServeWithReady`; constant `shutdownTimeout`.

Control flow: `MakeHandler` applies serve options in order to a top-level mux and special-cases CONNECT requests with 200 OK because `http.ServeMux` does not handle CONNECT normally. `ListenAndServe` parses a listening multiaddr, listens with manet, prints the actual RPC address, and delegates to `Serve`. `ServeWithReady` closes the listener on exit, builds the handler, checks node context before serving, starts `http.Server.Serve` in a goroutine, closes the ready channel immediately before serving, then waits for server exit or node context cancellation. On node shutdown it logs waiting messages and calls `server.Shutdown` with a 30-second timeout.

State and persistence behavior: manages listener/server lifecycle only. No repo state. It reacts to node context cancellation to stop serving and close listener.

Dependencies and integration points: used by daemon RPC/gateway/webui serve setup through `ServeOption`s. Depends on `core.IpfsNode.Context`, multiaddr network conversion, standard `http.Server`, and Kubo logging.

Risks: `serverError` is written by the serve goroutine and read by the parent without explicit synchronization beyond channel close; channel close provides ordering for reads after `<-serverClosed`. Shutdown waits up to 30 seconds for handlers to respect contexts. Returning `server.Shutdown` error overwrites `server.Serve` error after context shutdown.

Test signals: no direct tests here; daemon lifecycle/integration tests should cover serving and graceful shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/corehttp/corehttp.go -->
