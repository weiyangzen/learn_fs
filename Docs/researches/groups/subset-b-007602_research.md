# Research: subset-b-007602

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/cid_base_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/cid_base_test.go

Purpose: integration coverage for global `--cid-base` formatting across CLI commands that create, inspect, remove, or display CIDs. The test uses an offline daemon and `base16`, expecting CIDv1 strings beginning with `f01` so default base32 changes cannot create false positives.

Important APIs/functions: `TestCidBase`, local `makeDaemon`, `harness.Node` helpers `Init`, `StartDaemon`, `IPFSAddStr`, `PipeStrToIPFS`, `PipeToIPFS`, and `IPFS`; JSON decoding of `dag stat` output.

Control flow: subtests add blocks/files, run commands with and without `--cid-base=base16`, and assert CIDv0 values are upgraded for display when a non-base58btc base is requested. Coverage includes `add`, `pin ls`, `dag import`, `block put/stat/rm`, `dag stat`, `object patch`, `refs local`, and `object diff`.

State/persistence: each subtest owns a temporary initialized repo and daemon, writes MFS directories for object patch/diff, imports CAR bytes through stdin, and removes blocks for `block rm`.

Dependencies/integration: exercises the CLI formatting layer, blockservice, DAG import/export, MFS/object commands, refs, pinning, and the harness daemon runner.

Risks/test signals: strong regression signal for output encoding consistency. Risk is broad command coverage under parallel subtests can expose daemon startup/resource contention; assertions depend on human-readable outputs containing CIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/cid_base_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/cid_profiles_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/cid_profiles_test.go

Purpose: deterministic IPIP-499 UnixFS import profile test vectors for legacy `unixfs-v0-2015`, recommended `unixfs-v1-2025`, and the current default profile. It verifies CID version, hash, raw leaf behavior, chunk thresholds, max-link rebalancing, and HAMT directory sharding thresholds.

Important APIs/types/functions: `cidProfileExpectations`, profile fixtures `unixfsV02015`, `unixfsV12025`, `defaultProfile`, `TestCIDProfiles`, `runProfileTests`, helpers `verifyCIDVersion`, `verifyHashFunction`, `verifyRawLeaves`, `getBlockSize`, size/seed helpers, `TestDefaultMatchesExpectedProfile`, and `TestProtobufHelpers`.

Control flow: for each profile, subtests initialize nodes with profile args, add deterministic data at exact boundary sizes, inspect PB nodes and UnixFS data types, compare known CIDs, optionally export CARs via `CID_PROFILES_CAR_OUTPUT`, and build threshold-sized directories with testutils helpers.

State/persistence: creates large deterministic files, temporary directories with thousands of entries, daemon-backed blockstores, and optional CAR artifacts. Tests are parallel and isolated per repo.

Dependencies/integration: `harness`, `testutils`, UnixFS protobuf helpers, `boxo/ipld/unixfs`, `cid format`, `block stat`, `dag export`, and profile initialization.

Risks/test signals: high-value compatibility gate for future default/profile changes. It is expensive, including a 1 GiB synthetic v1 max-link case and thousands of file creations; expected CIDs must be updated intentionally when import semantics change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/cid_profiles_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/cid_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/cid_test.go

Purpose: black-box CLI coverage for `ipfs cid` subcommands: `inspect`, `base32`, `format`, `bases`, `codecs`, and `hashes`.

Important APIs/functions: `TestCidCommands`, `testCidInspect`, `testCidBase32`, `testCidFormat`, `testCidBases`, `testCidCodecs`, `testCidHashes`, and `assertExactSet`. It uses `go-cid`, libp2p `peer.ToCid`, and multihash construction for unknown-codec cases.

Control flow: subtests run CID commands without daemon setup, validate exact stdout/stderr, test JSON schema fields, convert CID versions/bases/codecs, feed stdin, and confirm mixed valid/invalid inputs return exit code 1 while still printing valid conversions.

State/persistence: no repo state or daemon persistence is required beyond harness temp command context; all inputs are literal CIDs or generated in memory.

Dependencies/integration: command parser/output layer, multibase registry, multicodec registry, multihash registry, libp2p-key CID handling, JSON encoder, and error aggregation for stream/list processing.

Risks/test signals: intentionally brittle registry lists catch accidental support changes. Emoji base output and exact spacing are output-format-sensitive; changes to supported codecs/hashes need coordinated test updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/cid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/cli_https_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/cli_https_test.go

Purpose: verifies the CLI uses TLS when `--api` is given HTTPS-style multiaddrs.

Important APIs/functions: `TestCLIWithRemoteHTTPS`, `httptest.NewTLSServer`, `net.SplitHostPort`, `url.Parse`, and `harness.Node.RunIPFS`.

Control flow: for both `/https` and `/tls/http` multiaddr suffixes, the test starts a TLS server that records whether `r.TLS` is populated, initializes a Kubo repo, and runs `ipfs id --api /ip4/127.0.0.1/tcp/<port>/<suffix>`.

State/persistence: only a temporary repo is initialized; no daemon is required. The remote endpoint is an in-process TLS server with a self-signed certificate.

Dependencies/integration: API endpoint multiaddr parsing, HTTP client scheme selection, TLS handshake behavior, and CLI remote API path.

Risks/test signals: expected failure is certificate verification, not a plaintext request. Error text is exact enough to catch regressions but may vary if Go TLS messages change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/cli_https_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/commands_without_repo_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/commands_without_repo_test.go

Purpose: ensures repo-independent commands work when `IPFS_PATH` points at an uninitialized temporary directory.

Important APIs/functions: `TestCommandsWithoutRepo`, direct `exec.Command("ipfs", ...)`, and standard stdin/stdout assertions.

Control flow: subtests run `ipfs cid base32`, `cid format`, `cid bases`, `cid codecs`, `cid hashes`, and `multibase list/encode/decode/transcode` with only environment setup, then assert exact known outputs or expected registry entries.

State/persistence: no repo is initialized. Each command receives an isolated `IPFS_PATH` via `cmd.Env`.

Dependencies/integration: installed `ipfs` binary on PATH, repo-opening bypass for pure CID/multibase commands, multibase codec implementation, and CLI command classification.

Risks/test signals: catches accidental repo requirements in stateless commands. It uses direct OS execution rather than harness wrappers, so failures can reflect PATH/build environment problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/commands_without_repo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/completion_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/completion_test.go

Purpose: verifies shell completion generation for Bash and Zsh.

Important APIs/functions: `TestBashCompletion`, `TestZshCompletion`, harness `IPFS("commands", "completion", ...)`, `testutils.RequiresLinux`, and shell runner invocation for `bash`/`zsh`.

Control flow: each test requests generated completion script text, fails if it is unexpectedly short, writes it to a temporary file, then sources it in the target shell and checks the IPFS completion function registration.

State/persistence: uses temporary files only; no daemon or repo persistence is needed.

Dependencies/integration: CLI command tree, completion generator, local `bash` and `zsh` availability, shell startup behavior, and harness temp file helpers.

Risks/test signals: validates generated scripts are syntactically loadable, not full interactive completion semantics. Zsh tool availability and shell environment can affect results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/completion_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/config_secrets_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/config_secrets_test.go

Purpose: security regression coverage for config secret redaction and TLS-insecure flags.

Important APIs/functions: `TestConfigSecrets`, `harness.Node.ReadFile`, `ConfigFile`, `RunIPFS`, `WriteBytes`, and `sjson.Set`.

Control flow: private key subtests compare raw config file contents to `ipfs config show`, reject direct `Identity.PrivKey` and `Identity` reads, reject `config replace` attempts that set `PrivKey`, and verify replacing redacted config preserves the existing key. TLS subtests confirm insecure skip-verify fields default non-true and can be explicitly set.

State/persistence: initializes repos, reads and writes config JSON, and relies on offline config replacement preserving secret fields.

Dependencies/integration: config command redaction, config validation/replacement, identity private key storage, and optional config fields `AutoConf.TLSInsecureSkipVerify` and `HTTPRetrieval.TLSInsecureSkipVerify`.

Risks/test signals: high security value. Line-based private-key extraction is simple and assumes pretty JSON formatting with a `PrivKey` line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/config_secrets_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/content_blocking_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/content_blocking_test.go

Purpose: end-to-end denylist/content-blocking coverage across CLI, HTTP gateway, NoFetch gateway, subdomain/IPNS gateway paths, CAR output filtering, and Gateway-over-libp2p.

Important APIs/functions: `TestContentBlocking`, denylist file creation under `$IPFS_PATH/denylists`, `IPFS_NS_MAP`, `carstore.NewReadOnly`, libp2p host/client setup, and many CLI commands (`block`, `dag`, `cat`, `ls`, `get`, `refs`).

Control flow: the test creates allowed and blocked content, writes explicit and double-hash denylist rules, primes namesys mappings, enables GatewayOverLibp2p, starts a daemon, validates allowed reads, then iterates blocked paths across CLI and gateway entry points expecting HTTP 410 or stderr containing the blocked message.

State/persistence: mutates repo denylists, blockstore contents, environment variables, gateway config, daemon restarts for NoFetch, and libp2p streams.

Dependencies/integration: denylist loader/matcher, namesys, gateway path handling, CAR traversal/filtering, CLI content fetchers, NoFetch blockservice swapping, and libp2p HTTP gateway transport.

Risks/test signals: broad regression gate but globally mutates `IPFS_NS_MAP`, so it intentionally avoids top-level parallelism. Duplicate CAR subtest names and path `/subdir` versus `blocked-subdir` should be watched for intent drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/content_blocking_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/content_routing_http_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/content_routing_http_test.go

Purpose: verifies delegated HTTP content routing is used for uncached block retrieval and sends the Kubo version as User-Agent.

Important APIs/types/functions: `userAgentRecorder`, `TestContentRoutingHTTP`, `httprouting.MockHTTPContentRouter`, `boxo/routing/http/server.Handler`, `httptest.NewServer`, and async `Runner.Run`.

Control flow: a mock HTTP routing server records user agents, a node is configured with `Routing.DelegatedRouters`, content is added in no-pin/offline mode to compute a CID, and a long-running `block stat` for that CID is started. The test waits until `FindProviders` is called and compares recorded user agents with `ipfs id -f <aver>`.

State/persistence: temporary daemon config and mock router call counters; the spawned `block stat` process is killed in cleanup.

Dependencies/integration: delegated routing client, content router server adapter, command runner lifecycle, user-agent version formatting, and provider lookup paths.

Risks/test signals: asynchronous and timeout-sensitive. It confirms lookup initiation, not successful retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/content_routing_http_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/daemon_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/daemon_test.go

Purpose: daemon lifecycle regression tests for null API config and graceful shutdown while operations are active.

Important APIs/types/functions: `TestDaemon`, `infiniteReader.Read`, `StartDaemon`, `StartDaemonWithReq`, `StopDaemon`, `Runner.Run`, `multiaddr.NewMultiaddr`, `manet.ToNetAddr`, and gateway HTTP client.

Control flow: one subtest starts `ipfs daemon` with `Addresses.API = nil`. The larger subtest enables pubsub, P2P HTTP proxy, gateway-over-libp2p, and GC, starts continuous stdin `ipfs add` plus a slow gateway CAR read, sleeps briefly, stops the daemon, asserts shutdown under ten seconds, ensures background operations terminate, and restarts the repo.

State/persistence: daemon config changes, repo lock lifecycle, gateway addresses, background processes/goroutines, and random blockstore content.

Dependencies/integration: daemon startup/shutdown, repo locking, command cancellation, gateway streaming, experimental components, and GC-enabled daemon paths.

Risks/test signals: good deadlock/shutdown signal. Timing is synthetic and could be flaky under very slow CI; background goroutines intentionally ignore expected shutdown errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dag_layout_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/dag_layout_test.go

Purpose: verifies Kubo’s default UnixFS DAG layout is balanced, while `--trickle` produces non-uniform leaf depths.

Important APIs/functions: `TestBalancedDAGLayout`, recursive `collectLeafDepths`, `IPFSAddDeterministic`, `InspectPBNode`, `cid format -f %c`, and optional CAR export via `DAG_LAYOUT_CAR_OUTPUT`.

Control flow: the balanced subtest adds a 45 MiB deterministic file and asserts all leaf depths are equal. The trickle subtest adds a similarly sized file with `--trickle` and asserts min/max leaf depths differ. The recursive walker treats raw blocks or PB nodes without links as leaves.

State/persistence: temporary daemon blockstores and optional exported CAR files.

Dependencies/integration: UnixFS importer layout selection, dag-pb inspection helpers, deterministic file generation, CID codec formatting, and refs reachable through the blockstore.

Risks/test signals: useful cross-implementation compatibility signal for IPIP-499. It is moderately expensive due to 45 MiB test vectors and recursive DAG traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dag_layout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dag_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/dag_test.go

Purpose: broad integration coverage for DAG stats, CARv2 imports, fast-provide behavior, and partial CAR local-only import/export semantics.

Important APIs/types/functions: `DagStat`, `Data`, `TestDag`, `TestDagImportCARv2`, `TestDagImportFastProvide`, helpers `dagRefs`, `countCARBlocks`, `makePartialDAG`, and local-only tests.

Control flow: fixture CARs are imported, `dag stat` JSON/text outputs are validated for dedup/shared sizes, CARv2 import through stdin is checked, fast-provide config/flag combinations assert daemon log messages and expected DHT failure propagation, and partial DAG helpers remove blocks to test `dag export --local-only` and `dag import --local-only` flag implications/conflicts.

State/persistence: fixture CAR files, temporary exported CARs, daemon stderr logs, block removal, pin removal, and fresh import nodes for block counts.

Dependencies/integration: DAG traversal/stats, CAR reader/importer, pinning, provider subsystem, config `Import.FastProvide*`, DHT availability, and CLI flag validation.

Risks/test signals: high behavioral value. Log-message assertions and DHT failure text are brittle; local-only tests pin DAG shape with chunker/max-links to reduce importer-default coupling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dag_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_client_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_client_test.go

Purpose: client-side HTTP delegated routing coverage for custom routing config, provider parsing, metrics, and provider address advertisement.

Important APIs/functions: `TestHTTPDelegatedRouting`, `TestHTTPDelegatedRoutingProviderAddrs`, fake `httptest.Server`, `captureProviderAddrs`, `customRoutingConf`, `ToJSONStr`, and `JSONObj`.

Control flow: the first test verifies default no-router behavior, daemon startup failures for missing/unsupported methods, JSON and NDJSON provider responses from an HTTP router, `routing findprovs` ordering, and Prometheus metrics. The provider-address test captures `/routing/v1/providers` payloads and checks `Addresses.Announce`, `AppendAnnounce`, and wildcard bind address resolution.

State/persistence: node config is repeatedly mutated and daemon restarted; mock servers capture request bodies under mutex protection.

Dependencies/integration: `config.Routing` custom schema, HTTP routing client, provider record serialization, metrics endpoint, address resolution logic, and CLI `routing provide/findprovs`.

Risks/test signals: strong for config validation and provider-record correctness. Reusing one node across early subtests requires careful daemon stop/start sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_proxy_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_proxy_test.go

Purpose: verifies a Kubo node can use another Kubo node’s exposed Routing V1 HTTP API as its routing backend.

Important APIs/functions: `TestRoutingV1Proxy`, `setupNodes`, `waitUntilProvidesComplete`, IPNS helpers, and `config.RouterParser`/`config.Methods`.

Control flow: setup creates three nodes: node 0 exposes Routing V1 with DHT, node 1 uses custom HTTP routing pointing at node 0 and no DHT, and node 2 keeps the DHT operative. Subtests cover provider lookup, peer lookup, IPNS record get/resolve through proxy routing, and publishing an IPNS record from the proxy-backed node for retrieval by the DHT node.

State/persistence: multiple daemons, peer connectivity, DHT provider/IPNS records, and published names.

Dependencies/integration: gateway Routing API exposure, DHT routing, HTTP delegated routing client, IPNS record marshaling, and harness multi-node connectivity.

Risks/test signals: meaningful end-to-end proxy signal; depends on local multi-node DHT convergence and provider completion waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_proxy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_server_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_server_test.go

Purpose: server-side Routing V1 API coverage for providers, peers, IPNS get/put, and `GetClosestPeers` behavior across routing modes.

Important APIs/functions: `TestRoutingV1Server`, local `setupNodes`, `boxo/routing/http/client`, `types`, `iter.ReadAllResults`, `autoconf.FallbackBootstrapPeers`, `peer.ToCid`, and IPNS helpers.

Control flow: local multi-node subtests expose routing APIs on DHT nodes and assert provider, peer, and IPNS responses. Disabled-routing subtests configure `none`, `delegated`, and `custom` modes and expect `GetClosestPeers` errors. Enabled-routing subtests use `auto`, `autoclient`, `dht`, and `dhtclient` with fallback bootstrap peers, retrying until WAN DHT returns peer records capped at 20.

State/persistence: local DHT nodes, published IPNS records, lonely node record insertion, bootstrap peer config, and external network routing table state.

Dependencies/integration: Routing V1 server, DHT routers, delegated/custom routing configs, IPNS routing storage, HTTP client iterators, and WAN bootstrap.

Risks/test signals: high coverage but live-network `GetClosestPeers` lane is inherently slower/flakier and can consume minutes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/delegated_routing_v1_http_server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dht_autoclient_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/dht_autoclient_test.go

Purpose: smoke-tests DHT `autoclient` routing in a local ten-node network.

Important APIs/functions: `TestDHTAutoclient`, `harness.NewNodes`, `ForEachPar`, `StartDaemons`, `Connect`, `IPFSAdd`, and `cat`.

Control flow: nodes 8 and 9 are configured as `Routing.Type=autoclient`, all ten daemons start and connect, then one subtest verifies content added by an autoclient node can be retrieved by another autoclient node, while another verifies server-mode-added content is retrievable from every node.

State/persistence: multi-node blockstores, DHT routing state, provider records, and random byte payloads.

Dependencies/integration: DHT mode selection, autoclient behavior, provider discovery, Bitswap/content retrieval, and harness network connection helpers.

Risks/test signals: concise but depends on local routing convergence. Use of `Stdout.Trimmed()` with random bytes plus appended carriage return is intended to preserve comparison shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dht_autoclient_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dht_opt_prov_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/dht_opt_prov_test.go

Purpose: smoke test for experimental optimistic DHT provide.

Important APIs/functions: `TestDHTOptimisticProvide`, `config.Experimental.OptimisticProvide`, `config.Provide.DHT.SweepEnabled`, `routing provide`, and `routing findprovs`.

Control flow: two nodes are initialized, node 0 enables optimistic provide and disables the sweeping provider to use the legacy path, daemons connect, node 0 adds content and runs explicit provide, and node 1 searches for one provider, expecting node 0’s peer ID.

State/persistence: two daemon repos, provider records, and random content.

Dependencies/integration: experimental provide path, DHT provider storage/query, config flags, and local harness networking.

Risks/test signals: minimal smoke coverage; it confirms basic discoverability but not timing, retries, or large provider sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dht_opt_prov_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/diag_datastore_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/diag_datastore_test.go

Purpose: tests `ipfs diag datastore` offline access, counting, JSON output, raw get/put helpers, repo-lock behavior, and provider-keystore namespace visibility.

Important APIs/functions: `TestDiagDatastore`, harness datastore helpers `DatastoreCount`, `DatastorePut`, `DatastoreHasKey`, `DatastoreGet`, and provider config flags.

Control flow: subtests cover missing-key errors, counts after pinning, JSON count format, offline operation without daemon, put/get roundtrip, failure while daemon holds the repo lock, unified provider keystore counts under `/provider/keystore/{0,1}/`, and behavior when provider keystore directories are absent.

State/persistence: creates pins, direct datastore entries, provider-keystore directories, and toggles `Provide.DHT.SweepEnabled`/`Provide.Enabled`.

Dependencies/integration: repo datastore layer, diagnostic CLI, JSON encoder, provider keystore stores, pinning, and daemon lock detection.

Risks/test signals: validates operational tooling and hidden provider datastores. Several subtests only assert counts are nonzero/nonnegative, so they are smoke-level rather than byte-level format checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/diag_datastore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dns_resolvers_multiaddr_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/dns_resolvers_multiaddr_test.go

Purpose: regression coverage that `DNS.Resolvers` applies to multiaddr DNS resolution while `libp2p.direct` peer-address hostnames still resolve locally.

Important APIs/constants/functions: `testDomainSuffix`, `TestDNSResolversApplyToMultiaddr`, config `DNS.Resolvers`, bootstrap clearing, `swarm connect`, `id --peerid-base base36`, and `SwarmAddrs`.

Control flow: one subtest configures a broken DoH resolver and expects `/dnsaddr/bootstrap.libp2p.io` connection to fail with DNS/dial-related text. The second creates two local nodes, breaks node0’s resolver, constructs a `libp2p.direct` DNS4 multiaddr from node1’s base36 peer ID and TCP port, and asserts swarm connection succeeds.

State/persistence: daemon config, bootstrap lists, local peer connections, and DNS resolver settings.

Dependencies/integration: DNS resolver wiring, multiaddr resolver stack, p2p-forge/libp2p.direct local resolution, peer ID base conversion, and swarm dialer.

Risks/test signals: includes sleeps and error-message alternatives for asynchronous startup and DNS implementation variation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/dns_resolvers_multiaddr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/files_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/files_test.go

Purpose: broad MFS CLI coverage for `files cp`, `rm`, no-flush limits, offline `files chroot`, and import configuration propagation into MFS operations.

Important APIs/functions: `TestFilesCp`, `TestFilesRm`, `TestFilesNoFlushLimit`, `TestFilesChroot`, `TestFilesMFSImportConfig`, plus UnixFS inspection helpers `UnixFSDataType`, `UnixFSHAMTFanout`, and config `Import.*`/`Internal.MFSNoFlushLimit`.

Control flow: tests validate copying valid UnixFS/raw nodes and rejecting dag-cbor/bad dag-pb, `files rm --flush=false` errors, unflushed operation counters and resets, offline chroot confirmation/replacement/failure cases, CIDv1/raw-leaf/chunker/HAMT settings for `files write`, `files mkdir`, `add --to-files`, CID parity with `ipfs add --trickle`, CID builder preservation through mutations and daemon restart, and config changes after restart.

State/persistence: MFS root mutations, repo config edits, daemon restarts, temporary source files, direct block/DAG puts, and chroot changes while daemon is stopped.

Dependencies/integration: MFS layer, UnixFS importer, HAMT conversion/reversion, config loader, repo lock, CID builder, and CLI validation.

Risks/test signals: high-value user-facing coverage. Some tests rely on exact error text and many parallel daemon instances; MFS multi-block behavior intentionally differs from `ipfs add` unless trickle is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/fuse/fuse_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/fuse/fuse_test.go

Purpose: OS-gated end-to-end FUSE integration tests for mounting `/ipfs`, `/ipns`, and `/mfs` through a real daemon.

Important APIs/functions: `TestFUSE`, `mountAll`, `doUnmount`, `lazyUnmount`, Linux xattr helper `getXattr`, `testutils.RequiresFUSE`, and platform unmount tools.

Control flow: subtests cover mount/unmount, explicit unmount, missing mount dirs, IPNS `local` symlink, IPNS resolution through `IPFS_NS_MAP`, MFS file/dir creation, xattr CID lookup, CLI writes visible through FUSE, `add --to-files` visibility, file removal, nested dirs, publish blocking while IPNS is mounted, truncation paths, and reading sharded directories via `/ipfs`.

State/persistence: real mountpoints under the node dir, daemon lifecycle, MFS mutations, IPNS publish state, environment namesys mapping, and config forcing HAMT sharding.

Dependencies/integration: FUSE kernel/userspace support, mount command output, IPFS/IPNS/MFS filesystem implementations, UnixFS HAMT reads, POSIX syscalls, and platform unmount binaries.

Risks/test signals: high fidelity but requires `TEST_FUSE`, supported OS, privileges/device support, and careful cleanup of stale mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/fuse/fuse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/fuse/realworld_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/fuse/realworld_test.go

Purpose: real POSIX-tool FUSE suite exercising writable MFS mount behavior with commands users actually run.

Important APIs/functions: `TestFUSERealWorld`, local helpers `requireTool`, `workdir`, `runCmd`, `randBytes`, daemon config `Mounts.StoreMtime` and `Mounts.StoreMode`, and shared `mountAll`.

Control flow: one daemon/mount is shared, with isolated subdirectories per subtest. Coverage includes shell redirects, `cat`, `seq`, `wc`, `ls`, `stat`, `cp` in/out and recursive, atomic `mv`, `rm -rf`, symlinks/readlink/find traversal, `dd`, `sha256sum`, tar extract/create, `rsync -a`, `rsync --inplace`, and headless `vim` edits. Many assertions compare both FUSE reads and `ipfs files` daemon views.

State/persistence: MFS writes through the mount, metadata preservation, random multi-chunk payloads, symlinks, archives, external command outputs, and daemon-backed content.

Dependencies/integration: FUSE support plus many external binaries; LC_ALL is forced to C for deterministic command output.

Risks/test signals: very high end-user coverage but environment-heavy. Missing tools fail by design; 1 MiB+ payloads exercise multi-chunk paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/fuse/realworld_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/fuse/xattr_linux_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/fuse/xattr_linux_test.go

Purpose: Linux implementation of the FUSE xattr helper used by `fuse_test.go`.

Important APIs/functions: build tag `linux`, `getXattr(path, attr string)`, and `unix.Getxattr`.

Control flow: allocates a 256-byte buffer, calls `unix.Getxattr`, returns the byte slice up to the reported size as a string, or propagates the syscall error.

State/persistence: no persistent state; reads an extended attribute from a filesystem path.

Dependencies/integration: Linux-only `golang.org/x/sys/unix` xattr syscall and MFS FUSE attributes such as `ipfs.cid`.

Risks/test signals: helper assumes CID attribute fits in 256 bytes, which is fine for normal CID strings but should be revisited if attributes grow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/fuse/xattr_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/fuse/xattr_other_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/fuse/xattr_other_test.go

Purpose: non-Linux stub for the FUSE xattr helper.

Important APIs/functions: build tag `!linux`, `getXattr(_, _ string)`, `runtime.GOOS`, and formatted error creation.

Control flow: any call returns an error stating xattr is unsupported on the current OS. In practice, the xattr subtest in `fuse_test.go` skips unless `runtime.GOOS == "linux"`.

State/persistence: none.

Dependencies/integration: keeps the `fuse` package compiling on Darwin/FreeBSD without importing Linux-only syscall APIs.

Risks/test signals: intentionally no behavioral xattr coverage off Linux; platform-specific xattr support on other OSes is not exercised by these tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/fuse/xattr_other_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/gateway_limits_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/gateway_limits_test.go

Purpose: integration smoke tests for gateway retrieval timeout, maximum request duration, and concurrent request limiting.

Important APIs/functions: `TestGatewayLimits`, config fields `Gateway.RetrievalTimeout`, `Gateway.MaxRequestDuration`, `Gateway.MaxConcurrentRequests`, `harness.HTTPClient`, and `GatewayClient`.

Control flow: subtests configure short limits, start daemons, verify local content still returns 200, then request a known unavailable CID. Retrieval timeout and absolute request duration expect 504 responses; concurrent limiting starts one blocking request with a one-slot semaphore and expects the next request to return 429 with `Retry-After`, `Cache-Control: no-store`, and an error body.

State/persistence: daemon config, local gateway server, blocking goroutine, and local content blocks.

Dependencies/integration: gateway middleware for timeout/rate limiting, content routing stalls for nonexistent CIDs, HTTP response headers, and harness client behavior.

Risks/test signals: timing-sensitive but deterministic enough through low limits and blocking CID. It is basic integration coverage; boxo middleware unit tests cover deeper cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/gateway_limits_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/gateway_range_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/gateway_range_test.go

Purpose: verifies gateway range and directory responses for HAMT-sharded UnixFS fixtures with only minimal required blocks imported.

Important APIs/functions: `TestGatewayHAMTDirectory`, `TestGatewayHAMTRanges`, `IPFSDagImport`, `GatewayClient`, fixture CAR files, and HTTP `Range` headers.

Control flow: each test starts an empty offline test-profile node, imports a fixture CAR by expected root, then performs gateway reads. Directory listing of a 10k-item HAMT should succeed with minimal refs. Range subtests request two byte ranges from a large HAMT-sharded file and a multi-range request, expecting 206, exact `Content-Range`, and only the first range body for multi-range.

State/persistence: fixture CAR blocks imported into a temporary repo; daemon runs offline.

Dependencies/integration: trustless/offline gateway block traversal, HAMT directory/file resolution, byte-range serving, fixture integrity, and HTTP header processing.

Risks/test signals: strong regression for over-fetching and range traversal. Fixture CIDs and files are hard-coded and must stay aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/gateway_range_test.go -->
