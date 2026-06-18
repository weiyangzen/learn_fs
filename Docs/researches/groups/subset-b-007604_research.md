# Research Report: subset-b-007604

This grouped report covers the Kubo CLI test files assigned to `subset-b-007604`. Each section is delimited for deterministic splitting into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/p2p_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/p2p_test.go

Purpose: tests foreground `ipfs p2p listen` and `ipfs p2p forward` behavior when libp2p stream mounting is enabled. It verifies listener/forwarder registration, cleanup on signals, cleanup when closed through `ipfs p2p close`, data-plane tunnel behavior, and command termination when the daemon exits.

Important APIs and helpers: `waitForListenerCount` and `waitForListenerProtocol` poll `ipfs p2p ls --enc=json` and unmarshal `commands.P2PLsOutput` to check listener count and protocol names. The tests use `harness.Node.Runner.Run` with `RunFunc: (*exec.Cmd).Start` for long-running foreground commands, `syscall.SIGTERM` for interrupt simulation, `harness.NewRandPort` for local TCP endpoints, and ordinary `node.IPFS` calls for non-foreground command setup and cleanup.

Control flow: `TestP2PForeground` is a parallel top-level suite with subtests for listen and forward. Each test starts one or two nodes, sets `Experimental.Libp2pStreamMounting=true`, starts daemons, launches foreground p2p commands asynchronously, waits until the daemon reports the listener, then either signals the child process, closes it with `p2p close`, or stops the daemon. Tunnel tests create a local HTTP server, bind a p2p listener on one node and a forwarder on another, and confirm HTTP body bytes cross the p2p tunnel before teardown.

State and persistence: p2p listener state lives in the daemon and is observed through the RPC command. Foreground mode is expected to bind command lifetime to daemon listener lifetime; non-foreground mode is expected to return immediately and leave daemon state until an explicit close. No on-disk persistence is asserted.

Dependencies and integration points: integrates CLI, daemon RPC streaming, libp2p p2p stream mounting, OS process signals, local TCP listeners, and JSON command encoding. It depends on command text such as `waiting for interrupt` and cleanup messages.

Risks and test signals: the tests are timing-sensitive and depend on process signal semantics, available local ports, and RPC stream behavior. They deliberately distinguish SIGTERM output, where cleanup messages may be hidden by stream closure, from `p2p close` output, where both wait and cleanup messages should be visible. Failure signals include leaked listeners, hung foreground commands, missing text output, or broken tunnel data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/p2p_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/peering_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/peering_test.go

Purpose: verifies configured peering relationships reconnect automatically across disconnects and daemon start order. It exercises the harness peering configuration and Kubo's peering service through observable swarm peers.

Important APIs and helpers: local closures `containsPeerID`, `assertPeered`, `assertNotPeered`, and `assertPeerings` convert `from.Peers()` multiaddrs into peer IDs with `h.ExtractPeerID`, then poll with `assert.Eventuallyf`. `harness.CreatePeerNodes` creates initialized nodes with a list of `harness.Peering{From, To}` relationships.

Control flow: `TestPeering` runs four parallel scenarios. The first starts three nodes with bidirectional and one-way peering, verifies all configured peers, disconnects two nodes, and expects reconnection. The second disconnects the target side and expects the configured source to reconnect. The third starts only two nodes, verifies available peerings, starts the third later, and expects the delayed peering to come online. The fourth stops a peered daemon, waits until it is not connected, restarts it, and expects re-peering.

State and persistence: peering configuration is written before daemon startup by the harness. Runtime connection state is transient, but the peering service should continuously enforce configured peerings while daemons run and after peer restarts.

Dependencies and integration points: uses libp2p peer IDs, swarm peer lists, harness peering config generation, daemon lifecycle, and peer disconnect helpers. `testutils.ForEachPar` is used to parallelize peer assertions.

Risks and test signals: reconnection is inherently asynchronous, so the test uses one-minute positive waits and shorter negative waits. It can be flaky under slow networking or delayed peer discovery. Failures indicate that configured peerings are not enforced, reconnection is not triggered, or peer ID extraction from swarm addresses changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/peering_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pin_ls_names_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/pin_ls_names_test.go

Purpose: validates `ipfs pin ls --names` and name filtering across direct, recursive, indirect, JSON, text, update, removal, GC, concurrency, and restart scenarios. It focuses on pin-name visibility and preservation in local pinning commands.

Important APIs and types: `pinInfo` and `pinLsJSON` model the JSON output shape. `setupTestNode` initializes a node and starts an offline daemon. Assertion helpers check named output, CID-only output, and absent CID/name pairs. Tests use `IPFSAddStr`, `PipeStrToIPFS`, `pin add`, `pin ls`, `pin update`, `pin rm`, `repo gc`, `cat`, and UnixFS/DAG commands.

Control flow: `TestPinLsWithNamesForSpecificCIDs` creates many isolated nodes and exercises named single-CID queries, multi-CID queries, full pin listing, type filters, JSON output, direct plus indirect pin relationships, update preservation, invalid/unpinned errors, special-character names, concurrent pin creation, removal, GC preservation, duplicate names, and daemon restart persistence. `TestPinLsEdgeCases` checks invalid pin types, the non-listable `internal` mode, fake paths, and unpinned CIDs.

State and persistence: pin names are expected to be stored with pin metadata, survive daemon restarts, transfer from old CID to new CID during `pin update`, and disappear when the pin is removed. GC must preserve named and unnamed pins while collecting unpinned blocks.

Dependencies and integration points: depends on the pinner, pin index, MFS/DAG/UnixFS creation, JSON encoding, output formatting, offline daemon operation, and datastore persistence. The tests also exercise concurrent CLI operations against one node.

Risks and test signals: exact text assertions may fail if command formatting changes. Concurrent pin operations can expose pin-index races. Indirect-pin checks depend on directory DAG layout. Critical failure signals include missing names with `--names`, leaked names without `--names`, panic for `--type=internal`, name loss across update/restart, or GC deleting pinned content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pin_ls_names_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pin_name_validation_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/pin_name_validation_test.go

Purpose: enforces the 255-byte pin-name limit for `ipfs pin add`, `ipfs pin ls --name`, and `ipfs add --pin-name`. It distinguishes byte length from rune count by including Unicode cases.

Important APIs and functions: `TestPinNameValidation` creates one offline daemon node and one test CID, then runs valid and invalid name cases. `TestAddPinNameValidation` creates a file and verifies `ipfs add --pin-name` accepts and persists valid names and rejects over-limit names. The tests use `strings.Repeat`, `fmt.Sprintf("--pin-name=%s", ...)`, `RunIPFS`, `pin rm`, and `pin ls --names --type=recursive`.

Control flow: valid cases accept empty names, short ASCII, exactly 255 bytes, and Unicode strings within the byte limit. Invalid cases submit 256-byte, 300-byte, and 300-byte Unicode names and expect non-zero exits plus an error mentioning `max 255 bytes`. Name-filter validation checks that a 255-byte filter succeeds while 256 bytes fails. Add-command validation confirms a successfully added file can be listed with the requested pin name, then unpins it.

State and persistence: successful names become pin metadata and are observable through `pin ls --names`. Failed validations must not mutate pin state. Cleanup unpins successfully added CIDs to keep sequential subtests isolated within the shared node.

Dependencies and integration points: covers CLI option parsing, config-independent pin validation, pinner metadata storage, `add` command integration with recursive pin creation, and byte-length validation with UTF-8 input.

Risks and test signals: the tests share nodes inside each top-level test, so state cleanup matters. Regressions show up as accepted over-limit names, rejected valid 255-byte names, missing `max 255 bytes` diagnostics, or `add --pin-name` storing content without the requested name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pin_name_validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/ping_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/ping_test.go

Purpose: smoke-tests `ipfs ping` against connected peers, unreachable peers, self, zero count, and an offline peer.

Important APIs and functions: `TestPing` uses `harness.NewT(t).NewNodes(2).Init().StartDaemons().Connect()`, `PeerID().String()`, `IPFS`, and `RunIPFS`. Assertions inspect exit codes, stdout prefixes, and stderr messages.

Control flow: connected-peer tests ping each direction with `-n 2`. The unreachable-peer case uses a hard-coded peer ID and expects stdout to include `Looking up peer ...` before stderr begins with `Error:`. Self-ping runs against each node's own peer ID and expects exit code 1 plus `can't ping self`. Count zero expects `ping count must be greater than 0`. Offline peer starts two connected daemons, stops one, then expects `ping failed`.

State and persistence: no persistence is asserted. The test relies on live swarm connections and daemon state.

Dependencies and integration points: exercises libp2p ping, peer lookup, CLI argument validation, daemon connectivity, and harness daemon lifecycle.

Risks and test signals: unreachable peer lookup may vary with routing behavior, so the test checks broad error shape. Failure indicates broken ping validation, self-guard removal, incorrect exit codes, or connectivity cleanup problems after daemon stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/ping_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pinning_remote_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/pinning_remote_test.go

Purpose: validates Kubo's remote pinning CLI and MFS remote pin policy against an in-memory Remote Pinning API service. It covers service registration, credential hiding, service stats, error handling, add/list/remove operations, status transitions, force semantics, and offline warnings.

Important APIs and helpers: `runPinningService` starts a local HTTP server using `testutils/pinningservice.NewRouter`. Tests use `pin remote service add/ls/rm`, `pin remote add/ls/rm`, `Pinning.RemoteServices.*` config keys, `MFS_PIN_POLL_INTERVAL`, `gjson` for JSON assertions, and `sjson` to mutate config JSON.

Control flow: the MFS policy test enables remote MFS pinning and polls until the service receives the MFS root CID, then changes MFS and expects repinning. Credential tests ensure `config Pinning`, direct API key reads, and `config show` do not expose tokens while `config replace` preserves redacted keys but rejects injected keys. Service-stat tests distinguish valid and invalid endpoints. Remote pinning subtests simulate background status changes by mutating `PinStatus`, blocking `--background=false` until pinned, listing multiple statuses, listing by CID, removing by name with and without `--force`, removing all pins, and warning when adding in offline mode.

State and persistence: service definitions and API keys live in Kubo config. Remote pins live only in the mock service's memory. MFS pinning state is derived from MFS root changes and policy config. Credential secrecy is enforced across config display and replacement.

Dependencies and integration points: integrates Kubo CLI, daemon, config redaction, remote pinning client, MFS flush/stat, local HTTP service, bearer authorization, JSON output, DNS failure handling, and service endpoint validation.

Risks and test signals: timing-sensitive polling depends on short MFS poll intervals and daemon scheduling. The service is intentionally minimal, so failures may indicate client/API contract drift. Strong signals include leaked API keys, missing access-denied errors, force removal safeguards failing, or MFS root not repinning after change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pinning_remote_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pins_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/pins_test.go

Purpose: broad CLI coverage for local pin operations, including pin add/rm/update/verify/list, daemon and offline modes, progress output, DAG corruption error reporting, CID base handling, pin names, name filters, overwrite behavior, and JSON wire output.

Important APIs and types: `testPinsArgs` parameterizes daemon use, pin arguments, `pin ls` arguments, and CID base arguments. Helpers `testPins`, `testPinsErrorReporting`, `testPinDAG`, and `testPinProgress` run reusable suites. `StrCat` from testutils composes optional argument slices. `pinLs` local helper splits text output into lines.

Control flow: `TestPins` runs the core helpers without a daemon and with an offline daemon across combinations such as `--progress`, `--stream`, and `--cid-base=base32`. The core test adds seven blocks unpinned, pins them through stdin, verifies output, runs `pin verify`, checks verbose verify, lists pins, removes them, and tests `pin update --unpin=true`, including idempotent update. Error helpers use missing random CIDs and deliberately removed DAG blocks to require `ipld: could not find`. Additional subtests validate text output with `--names`, name substring filtering through `--name` and `-n`, overwriting a pin name on the same CID, and JSON output where `Name` appears only under `--names`.

State and persistence: pin state is local to each node and is mutated sequentially within each helper. `pin update` should transfer recursive pin state and optional name metadata. DAG corruption is produced by removing a referenced block after unpinning.

Dependencies and integration points: exercises pinner, blockstore, DAG traversal, CLI stdin handling, CID encoding, JSON output, progress reporting, and offline daemon RPC behavior.

Risks and test signals: exact progress text such as `5 nodes (1.0 MB)` is format-sensitive. The tests intentionally run many parallel nodes, so repo isolation is critical. Regressions show as wrong pin command output, verify omissions, missing error details, failed name transfer, or JSON/text mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pins_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/provide_stats_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/provide_stats_test.go

Purpose: validates `ipfs provide stat` output, flags, formats, provider-mode differences, integration with scheduled content, documented metrics, and disabled-provider behavior.

Important APIs and types: constants set polling timeout/tick. `sweepStats` mirrors the JSON fields used by tests, and `parseSweepStats` unmarshals `--enc=json` output. The suite configures `Provide.DHT.SweepEnabled`, `Provide.Enabled`, `Provide.DHT.Interval`, and `Provide.Strategy`.

Control flow: `TestProvideStatAllMetricsDocumented` starts a sweep provider, runs `provide stat --all`, extracts metric names, reads `docs/provide-stats.md`, and verifies every emitted metric has documentation. Basic tests check brief output labels and offline rejection. Flag tests cover `--all`, `--compact` requiring `--all`, compact two-column layout, individual section flags, and combined sections. Legacy-provider tests assert old stats fields and rejection of sweep-specific flags. Format tests assert JSON shape has either `Sweep` or `Legacy`. Integration tests verify adding content increases scheduled keys and that all documented strategies render stats. Disabled-config tests distinguish `Provide.Enabled=false` from `Provide.DHT.Interval=0`.

State and persistence: stats reflect live daemon provider state, including queues, schedule, operations, and strategy-dependent scheduling. No on-disk persistence is directly asserted here, but the schedule must update after content is added.

Dependencies and integration points: depends on provider subsystem selection, stats command formatting, documentation file layout, JSON field names, and daemon online mode.

Risks and test signals: the metric-documentation parser contains a suspicious indent condition that currently skips all indented lines because both branches use `HasPrefix`; if fixed, it will enforce docs more strongly. Other risks are timing around schedule updates and exact label churn. Failures signal provider stats unavailable, flag validation drift, undocumented metric additions, or legacy/sweep output shape regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/provide_stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/provider_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/provider_test.go

Purpose: comprehensive integration tests for Kubo content provider behavior across legacy and sweeping providers, DHT and HTTP routing, fast provide, manual `provide once`, strategy filtering, reprovide cycles, provider stats, keystore lifecycle, migration cleanup, and shutdown logging.

Important APIs and types: `cfgApplier` applies provider config, `awaitReprovideFunc` abstracts legacy manual reprovide versus sweep-stat polling, and `runProviderSuite` hosts the common matrix. Helpers `uniq`, `parseProvideStatJSON`, `waitForSweepReprovide`, `dirExists`, `addLargeFileInSubdir`, and `addLargeFilestoreFile` support unique data, stat parsing, sweep waits, filesystem checks, and large DAG setup. The file defines `provideStatJSON` for selected `provide stat --enc=json` fields.

Control flow: common tests start nodes with stub DHT bootstrap, connect them, and assert provider discovery through `routing findprovs`. They verify `Provide.Enabled`, default all-strategy behavior for `add`, `block put`, and `dag put`, manual `routing provide` errors without peers, success through custom HTTP routers, `provide once` with interval zero, disabled provider errors, recursive providing, multiple CIDs, stdin, deduplication, JSON streaming, and fast-provide-root behavior. Strategy tests cover `all`, `pinned`, `roots`, `mfs`, `pinned+mfs`, `+unique`, and `+entities`, including chunk-skipping semantics. Filestore tests assert `--nocopy` provide behavior under all and selective strategies. Reprovide tests add content offline and verify two cycles for each strategy. `provide clear` tests text, quiet, disabled, and JSON output. `TestProvider` runs the suite for legacy and sweeping providers, with resume tests only for sweeping. Additional tests check bloom dedup logs, async fast-provide-dag survival after command return, HTTP-only routing with sweep enabled, provider-keystore datastore purge, migration purge from old inline datastore keys, and quiet shutdown when keystore sync is interrupted.

State and persistence: provider behavior is driven by config and live routing state. Reprovide tests validate repeated cycles and sweep resume persists cycle start across daemon restarts when enabled. Keystore tests inspect `<repo>/provider-keystore/{0,1}` swapping and purging, plus migration removal of `/provider/keystore/*` orphaned keys from the shared datastore. Shutdown tests inspect daemon logs and client behavior during datastore/keystore closure.

Dependencies and integration points: integrates DHT routing, HTTP delegated routing, provider strategy walkers, UnixFS DAG structure, filestore, MFS, pinning, daemon logs, resource timing, `provide stat`, and flat repository filesystem paths. It also uses `httptest`, random data, log-level environment variables, and harness DHT stubs.

Risks and test signals: this file is timing-heavy, parallel, and resource-intensive. It assumes provider records appear within fixed polling windows and that log messages remain stable. Regressions show as missing provider records, chunks incorrectly provided/skipped under strategy modifiers, `provide once` accepting missing CIDs, HTTP-only routing broken by sweep provider, keystore directories not purged, resume offsets reset incorrectly, or shutdown-caused keystore errors logged at Error level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/provider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pubsub_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/pubsub_test.go

Purpose: tests Kubo pubsub CLI behavior and the persistent per-peer seqno validator state used for replay protection.

Important APIs and helpers: `waitForSubscription` polls `pubsub ls` for a topic, `waitForMessagePropagation` sleeps to allow propagation and datastore persistence, and `publishMessages` sends repeated messages with short spacing. `TestPubsub` uses `Pubsub.Enabled=true` and `Routing.Type=none` to simplify node setup.

Control flow: basic delivery starts a subscriber command in a goroutine, waits for the topic, publishes one message, and attempts to parse JSON data from `pubsub sub --enc=json`. Seqno persistence tests subscribe one node to messages from another, stop daemons, and inspect `/pubsub/seqno/` through `diag datastore`. Update tests compare datastore values across daemon restarts and additional messages. Reset tests run `pubsub reset` globally and with `--peer`, then verify datastore keys are deleted selectively. Restart survival tests confirm seqno count remains stable across daemon restart.

State and persistence: the core state is `/pubsub/seqno/<peerid>` in the repo datastore, storing an eight-byte max seqno per publisher peer. `pubsub reset` mutates this state while the daemon is running; datastore inspection generally requires stopped daemons.

Dependencies and integration points: integrates libp2p pubsub, CLI subscriptions, JSON output, datastore diagnostic commands, peer IDs, daemon stop/start, and persistent BasicSeqnoValidator behavior.

Risks and test signals: the tests acknowledge that message delivery may be timing-sensitive and sometimes log instead of failing when a specific seqno key is absent. Stronger assertions cover datastore counts and reset behavior. Failures indicate pubsub subscriptions not registering, seqno state not persisted, reset not deleting keys, or state lost across restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/pubsub_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rcmgr_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/rcmgr_test.go

Purpose: validates `ipfs swarm resources` and libp2p resource-manager configuration behavior, including disabled mode, default scaling, user overrides, allowlist behavior, and daemon startup rejection for unsafe resource limits.

Important APIs and helpers: `TestRcmgr` mutates `config.Config` and user-supplied `rcmgr.PartialLimitConfig` through harness helpers. `unmarshalLimits` parses `libp2p.LimitsConfigAndUsage` JSON. Tests reference `rcmgr.DefaultLimit`, `BlockAllLimit`, `Unlimited`, `LimitVal64`, libp2p `peer.ID`, and `protocol.ID`.

Control flow: disabled-resource-manager tests expect `swarm resources` to fail with `missing ResourceMgr`. High connection-manager high-water tests assert inbound connection and stream limits scale above 2000. Default tests ensure limits are not block-all and usage counters are zero. Override tests check system unlimited inbound values, transient memory, service memory, protocol memory, and peer memory are reflected in JSON output. Blocking/allowlist tests configure node0 to block all conns but allowlist node2, then assert connect/ping fails for node1 and succeeds for node2. Startup validation tests run `ipfs daemon` with connmgr highwater lower than configured system connection/stream limits and expect exit code 1.

State and persistence: resource-manager settings are config-derived at daemon start. No persisted runtime state is asserted except config files generated by harness. Usage counters are live daemon observations.

Dependencies and integration points: integrates Kubo config, libp2p resource manager, connection manager watermarks, swarm connect, ping, JSON output, and allowlist multiaddr syntax.

Risks and test signals: exact resource thresholds depend on libp2p scaling rules. The connect-failure message accepts either routing or resource-limit wording. Regressions appear as resource command success when disabled, block-all limits leaking into defaults, overrides ignored, allowlist bypass failing, or daemon accepting inconsistent connmgr/resource settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rcmgr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/repo_verify_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/repo_verify_test.go

Purpose: tests `ipfs repo verify` for healthy repos, corruption detection, dropping corrupt blocks, healing from peers, partial healing, empty repos, scale, and removal-failure reporting.

Important APIs and helpers: constants name flatfs filenames for empty UnixFS file and directory blocks, which are excluded from corruption due to special behavior. `getEligibleFlatfsBlockFiles` glob-searches `blocks/*/*.data`, filters special blocks, and returns mutable block paths. `corruptRandomBlock` and `corruptMultipleBlocks` overwrite selected flatfs files with invalid bytes.

Control flow: `TestRepoVerify` contains parallel subtests. Healthy and empty repos expect `all blocks validated`. Corruption tests overwrite blocks, then expect non-zero verification and count summaries. `--drop` should remove corrupt blocks and make `block stat` fail. `--heal` requires online mode, can repair by fetching from a connected peer, verifies healed content and raw block equality, can partially heal only available blocks, and fails when no peer has content. Scale tests corrupt 10 of 1000 blocks. Removal-failure tests chmod a corrupted file and directory read-only, then require partial remove failure counts.

State and persistence: tests directly mutate the flatfs blockstore on disk and observe repo state through `repo verify`, `block stat`, `cat`, and `repo gc`. Heal removes corrupt local blocks and attempts network refetch.

Dependencies and integration points: depends on flatfs layout, filesystem permissions, Kubo block validation, Bitswap/network retrieval, pinning/GC to control availability, and diagnostic count reporting.

Risks and test signals: tests are flatfs-specific and may not apply to alternate blockstores. Permission simulation can be platform-sensitive, especially under privileged users. Failures indicate corrupt blocks not detected, summaries wrong, drop/heal exit codes wrong, healed bytes mismatched, or partial failure accounting broken.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/repo_verify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/routing_dht_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/routing_dht_test.go

Purpose: validates DHT routing CLI commands for peer lookup, IPNS get/put, provider lookup, offline errors, and self-lookup failure, with and without pubsub IPNS support.

Important APIs and helpers: `waitUntilProvidesComplete` polls `provide stat -a` and parses `Provide queue` and `Ongoing provides` lines until no queued or ongoing provides remain. `testRoutingDHT` configures five nodes with `Routing.Type=dht` and optionally starts daemons with pubsub flags. `testSelfFindDHT` checks self lookup.

Control flow: each DHT variant starts connected nodes. `routing findpeer` asks node1 for node0 and expects node0's first swarm address. `routing get` publishes an IPNS record on node2 and retrieves it from node1, then nested tests put the returned record back and verify bad keys fail for `routing put` and `routing get`. `routing findprovs` adds content on node3, waits for provider work to complete, and expects node4 to find node3. Offline tests use an initialized but stopped node and expect online-mode errors for `findprovs`/`findpeer` and an offline put error without `--allow-offline`. Self-find uses `dht findpeer` against the node's own peer ID and expects failure.

State and persistence: IPNS records and provider records are stored in the DHT/network, while local content and name records originate in node repositories. No durable state is checked after restart.

Dependencies and integration points: integrates DHT routing, IPNS publishing, provider subsystem stats, pubsub-related daemon flags, swarm addresses, and routing command validation.

Risks and test signals: exact parsing of `provide stat -a` labels is fragile. Provider discovery depends on provide completion and connected DHT nodes. Failures signal DHT lookup regressions, invalid-key validation drift, broken provider announcements, or offline commands unexpectedly acquiring repo locks or running online-only code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/routing_dht_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rpc_auth_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/rpc_auth_test.go

Purpose: tests RPC authorization scopes across HTTP clients and CLI `--api-auth`, including bearer/basic secrets, path restrictions, disabled auth, unauthenticated rejection, version endpoint exception, multi-user separation, and empty allowed paths.

Important APIs and helpers: `rpcDeniedMsg` captures the expected denial message. `makeAndStartProtectedNode` injects `API.Authorizations` into config and starts the daemon using a special starter token allowed on `/api/v0`. `makeHTTPTest` builds clients using `auth.NewAuthorizedRoundTripper`; `makeCLITest` exercises `node.RunIPFS` with `--api-auth`.

Control flow: table-driven cases cover raw bearer token, `bearer:` secret syntax, basic `user:pass`, and pre-encoded basic credentials. Each case verifies allowed `/id` access and forbidden `/config/show` access for HTTP and CLI. Additional subtests check `/api/v0` grants full access, nil and empty maps disable auth checks, missing Authorization header is rejected when auth exists, `/version` is always accessible, Bob's token cannot access Alice-only paths, empty `AllowedPaths` denies all except version, and CLI commands fail without `--api-auth`.

State and persistence: authorization config is written before daemon startup and governs live RPC access. No runtime mutation or persistence after restart is tested.

Dependencies and integration points: integrates Kubo config, RPC HTTP middleware, CLI API auth flag, client/rpc auth transport, endpoint path matching, and daemon startup under protected APIs.

Risks and test signals: path matching must treat `/api/v0` as a prefix while preserving narrower endpoint controls. Failure signals include token leakage across scopes, unauthenticated access when auth is enabled, CLI not sending tokens, or version endpoint accidentally requiring scoped authorization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rpc_auth_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rpc_content_type_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/rpc_content_type_test.go

Purpose: verifies RPC `Content-Type` headers for binary and structured endpoints: `dag export`, `block get`, `diag profile`, `name get`, and `routing get`.

Important APIs and functions: tests build raw HTTP POST requests to `node.APIURL() + /api/v0/...` using `http.DefaultClient`. `TestHTTPRPCNameGet` additionally decodes base64 JSON from `routing get` and pipes raw IPNS bytes to `ipfs name inspect`.

Control flow: `TestRPCDagExportContentType` adds content offline and expects `application/vnd.ipld.car`. `TestRPCBlockGetContentType` expects `application/vnd.ipld.raw`. `TestRPCProfileContentType` uses `profile-time=0` and expects `application/zip`. `TestHTTPRPCNameGet` runs online, publishes an IPNS record, fetches it through `name get` as raw bytes with `application/vnd.ipfs.ipns-record`, fetches the same record through `routing get /ipns/<peer>` as JSON, decodes `Extra`, compares bytes, and verifies the record contains the published CID.

State and persistence: content and IPNS records are created in a temporary repo and served through live daemon RPC. No restart persistence is checked.

Dependencies and integration points: integrates HTTP RPC, content serialization, CAR/raw block/profile ZIP/IPNS content types, IPNS publishing, routing records, JSON/base64 transport, and `name inspect`.

Risks and test signals: exact header values are part of the public API. Failures indicate HTTP response metadata regressions, `name get` returning JSON instead of raw record bytes, or `routing get` record content diverging from the dedicated IPNS endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rpc_content_type_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rpc_get_output_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/rpc_get_output_test.go

Purpose: specifically guards `ipfs get` RPC output `Content-Type` headers for tar and gzip transport formats.

Important APIs and functions: `TestRPCGetContentType` starts an offline daemon, adds one string, then table-drives raw HTTP POST requests to `/api/v0/get` with query combinations for default, `archive=true`, `compress=true`, and `archive=true&compress=true`.

Control flow: each subtest builds the full RPC URL, posts with no body, requires status 200, and compares the `Content-Type` header. Default and archive output are expected to be `application/x-tar`; compressed variants are expected to be `application/gzip`.

State and persistence: only one added CID is needed. The test observes live HTTP RPC output and does not inspect extracted bytes or persisted state.

Dependencies and integration points: integrates `get` command option parsing, RPC response headers, archive/gzip output selection, and the HTTP API transport. The test references the long-standing content-type issue it protects.

Risks and test signals: header comparisons are exact and may need coordinated updates if MIME decisions change. Failures signal that consumers of RPC `get` can no longer infer stream format from headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rpc_get_output_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rpc_unixsocket_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/rpc_unixsocket_test.go

Purpose: verifies the Kubo RPC client and daemon can communicate over a Unix socket API address.

Important APIs and functions: `TestRPCUnixSocket` constructs an API multiaddr by joining `/unix`, the node repo directory, and `sock`, writes it to `cfg.Addresses.API`, starts the daemon, builds a `multiaddr.Multiaddr`, and creates a client with `rpcapi.NewApi`.

Control flow: after daemon startup, the test issues RPC requests for `version` and `id` through the Unix socket client. Both responses must succeed and populate non-empty structs. The daemon is stopped at the end.

State and persistence: the API listen address is a config value set before daemon startup. The socket file lives under the temporary node directory during daemon runtime and is not inspected after shutdown.

Dependencies and integration points: integrates config address parsing, Unix socket listener creation, multiaddr parsing, the Go RPC client transport, and core API commands. It is Unix-specific in practice even though the file has no explicit build tag.

Risks and test signals: path length and platform support for Unix sockets can affect this test. Failures indicate daemon inability to bind Unix API addresses, client transport regression, or multiaddr format changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/rpc_unixsocket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/shutdown_timeout_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/shutdown_timeout_test.go

Purpose: tests daemon bounded-shutdown configuration through end-to-end daemon stop/start behavior.

Important APIs and constants: `testShutdownTimeout` is 10 seconds and `testShutdownCompletionBound` is 15 seconds. Tests update `cfg.Internal.ShutdownTimeout` with `config.NewOptionalDuration`, start daemons, call `node.StopDaemon`, and measure elapsed time.

Control flow: `TestShutdownTimeoutHonored` configures a nonzero timeout, starts a daemon, writes pinned data with `add`, creates an MFS directory, verifies `diag healthy`, stops the daemon and requires completion well under the bound, restarts it, and verifies the pin and MFS directory survived. `TestShutdownTimeoutDisabled` sets timeout zero to opt out of the watchdog/deadline logic, then still expects a clean stop within the same soft bound because no subsystem is hung.

State and persistence: pinned content and MFS state must persist across shutdown and restart in the bounded-shutdown case. ShutdownTimeout is a config value read by daemon lifecycle code.

Dependencies and integration points: integrates internal config, daemon lifecycle, health diagnostics, pin storage, MFS persistence, and harness stop escalation behavior.

Risks and test signals: wall-clock assertions can be noisy on overloaded systems but include a five-second cushion. Failures indicate shutdown timeout not honored, disabled mode hanging unexpectedly, or shutdown corrupting/flushing persistent pin/MFS state incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/shutdown_timeout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/stats_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/stats_test.go

Purpose: a small smoke test for `ipfs stats dht`.

Important APIs and functions: `TestStats` starts two initialized daemons, connects them, runs `node1.IPFS("stats", "dht")`, and checks command result fields through testify assertions.

Control flow: the single subtest requires no stderr, a successful command error state, and non-empty stdout lines. The nodes are stopped through deferred cleanup.

State and persistence: no persistent state is asserted. DHT stats are read from live online daemon state after a two-node connection.

Dependencies and integration points: exercises the `stats dht` CLI command, DHT subsystem, daemon connectivity, and harness result buffering.

Risks and test signals: because it checks only non-empty output, it is a broad availability signal rather than a strict contract test. Failure indicates the command errored, wrote unexpected stderr, or stopped emitting any DHT stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/swarm_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/swarm_test.go

Purpose: tests selected `ipfs swarm` commands, especially `swarm peers --identify` JSON output and `swarm addrs autonat` reachability output.

Important APIs and types: local structs model identify JSON: `identifyType`, `peer`, and `expectedOutputType`. Tests use `RunIPFS("swarm", "peers", "--enc=json", "--identify")`, `id --enc=json`, `SwarmAddrs`, and `swarm addrs autonat --enc=json`.

Control flow: one test verifies a node with no connections returns an empty peers list. Connected-peer tests verify identify fields include the peer ID, public key, agent version, addresses with `/p2p/<peer>`, and protocols. Another test compares the `Identify` object from `swarm peers --identify` to the peer's own `ipfs id --enc=json` output. The AutoNAT test parses reachability, reachable/unreachable/unknown arrays, and asserts reachability is one of `Public`, `Private`, or `Unknown`.

State and persistence: observations are live swarm and identify state. No persisted data is tested.

Dependencies and integration points: integrates swarm peer listing, identify protocol metadata, node IDs, multiaddrs, AutoNAT reachability reporting, and JSON encoding.

Risks and test signals: output assumes at least one connected peer appears at index 0. Address ordering or protocol set changes can affect exact comparisons. Failures indicate identify data not being surfaced, peer list JSON shape drift, or AutoNAT status returning invalid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/swarm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/telemetry_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/telemetry_test.go

Purpose: validates the telemetry plugin's opt-out behavior, first-run messaging, UUID-file handling, and schema stability.

Important APIs and dependencies: `TestTelemetry` manipulates `Plugins.Plugins.telemetry` config, environment variables such as `IPFS_TELEMETRY` and `GOLOG_LOG_LEVEL`, captures daemon stdout/stderr with `harness.Buffer`, uses `httptest.Server` to receive telemetry JSON, and uses `maps.Keys`/`slices.Sort` for schema comparison.

Control flow: environment opt-out and config opt-out tests enable the plugin but opt out, start daemons with debug logging, expect opt-out log messages, and assert `telemetry_uuid` does not exist. A removal test pre-creates `telemetry_uuid`, opts out, and expects a removal log plus file deletion. Enabled-first-run test starts without opt-out and expects informational text and UUID creation. Schema regression test configures a short delay and mock endpoint, starts a daemon, waits for one POST, and compares the exact set of telemetry fields to an expected list.

State and persistence: `telemetry_uuid` is the primary on-disk state. It should be created when telemetry is enabled and absent/removed when opted out. Config controls endpoint, delay, mode, and plugin disabled status.

Dependencies and integration points: integrates plugin config, daemon startup logging, environment opt-out, filesystem state, HTTP posting, JSON schema, and platform/config collectors.

Risks and test signals: the schema list is intentionally strict and must be updated with legitimate telemetry field changes. Timing depends on daemon startup and the configured delay. Failures indicate privacy opt-out regressions, UUID leakage, missing first-run disclosure, or telemetry schema drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/telemetry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/asserts.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/asserts.go

Purpose: provides a small assertion helper for tests that accept one of several possible error strings.

Important API: `AssertStringContainsOneOf(t *testing.T, str string, ss ...string)` loops over accepted substrings and returns as soon as one is present. If none match, it calls `t.Errorf` with the original string and accepted list.

Control flow: the helper is linear and non-fatal; the calling test continues after `t.Errorf` unless it has other fatal assertions. It imports only `strings` and `testing`.

State and persistence: no state or persistence.

Dependencies and integration points: used where external subsystems may produce semantically equivalent but textually different errors, for example resource-manager connection failures in rcmgr tests.

Risks and test signals: because the assertion is non-fatal, subsequent test code may run after failure. It also performs substring matching rather than structured error classification, so accepted message variants should remain narrow enough to avoid false positives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/asserts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/cids.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/cids.go

Purpose: centralizes well-known CID string constants used by CLI tests.

Important APIs: `CIDWelcomeDocs` stores the welcome docs CID and `CIDEmptyDir` stores the empty directory CID.

Control flow: no executable code; constants are imported by tests that need stable CIDs.

State and persistence: no state. The values are stable external identifiers.

Dependencies and integration points: `CIDEmptyDir` is used by routing/offline tests as a syntactically valid CID argument. Other test files can import these constants through dot imports from `testutils`.

Risks and test signals: changing these constants affects many tests and should only happen when fixture assumptions change. Invalid or deprecated CIDs would cause unrelated command validation tests to fail for the wrong reason.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/cids.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/files.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/files.go

Purpose: file-related test helpers for opening fixtures and walking up directories to find a named file.

Important APIs: `MustOpen(name string) *os.File` opens a file or panics with `log.Panicf`. `FindUp(name, dir string) string` scans `dir`, then each parent, returning the first matching path or an empty string at filesystem root.

Control flow: `FindUp` repeatedly calls `os.ReadDir`, compares entry names, advances with `filepath.Dir`, and stops when the parent equals the current directory. ReadDir errors panic.

State and persistence: no persistent state, but `MustOpen` returns an open file descriptor that callers must close if needed.

Dependencies and integration points: supports tests that need fixture discovery independent of current working directory. It uses standard `os`, `filepath`, and `log`.

Risks and test signals: panic-based failure is appropriate for test helpers but can make error recovery impossible. `FindUp` matches only basename equality and does not skip permission-denied directories; such errors panic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/floats.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/floats.go

Purpose: numeric helper for truncating floating-point values to a fixed number of decimal places in tests.

Important API: `FloatTruncate(value float64, decimalPlaces int) float64` computes `10^decimalPlaces`, multiplies the value, casts to `int`, then divides back.

Control flow: a simple loop multiplies `pow` by 10 for each decimal place. Truncation is toward zero because of the `int` conversion.

State and persistence: no state.

Dependencies and integration points: no imports. Useful for tests that need deterministic formatting or approximate numeric comparisons without rounding.

Risks and test signals: negative values truncate toward zero, not toward negative infinity. Large values or high decimal places may lose precision or overflow `int`. Callers should avoid using this for production numeric correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/floats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/httprouting/mock_http_content_router.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/httprouting/mock_http_content_router.go

Purpose: implements a thread-safe in-memory mock for the IPFS HTTP routing v1 server interfaces used by CLI routing tests.

Important APIs and types: `MockHTTPContentRouter` stores call counters, provider records, peer records, and a debug flag behind a mutex. It implements `FindProviders`, `ProvideBitswap`, `FindPeers`, `GetIPNS`, `PutIPNS`, `NumFindProvidersCalls`, `AddProvider`, and `GetClosestPeers`.

Control flow: lookup methods lock, initialize maps as needed, increment counters, return empty iterators when no records exist, and wrap stored records in `iter.Result` slices. `AddProvider` records provider entries by CID and, when the record is a `*types.PeerRecord`, also indexes it by peer ID for peer lookup. IPNS get/put return `routing.ErrNotSupported`. `GetClosestPeers` derives a peer ID from the CID key and returns matching peer records.

State and persistence: all state is in memory and protected by `sync.Mutex`. It is not persisted and is intended to be scoped to individual tests.

Dependencies and integration points: integrates with `boxo/routing/http/server`, `boxo/routing/http/types`, iterator utilities, `go-cid`, libp2p peer IDs, and routing interfaces. It can back an HTTP routing server in delegated routing tests.

Risks and test signals: the mock only implements the behavior needed by tests and does not model network errors, pagination, or full spec semantics. Call counters are useful for verifying cache/fallback behavior. Interface drift in boxo routing types would surface as compile failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/httprouting/mock_http_content_router.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/json.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/json.go

Purpose: tiny helper for constructing JSON strings in tests.

Important APIs: `JSONObj` is a `map[string]any` alias, and `ToJSONStr(m JSONObj) string` marshals it with `encoding/json`.

Control flow: `ToJSONStr` panics on marshal error and returns the JSON string otherwise.

State and persistence: no state.

Dependencies and integration points: used by tests that need compact inline JSON config or request bodies without repetitive marshal boilerplate.

Risks and test signals: map iteration order in JSON output may not be stable for string comparison. Panic behavior is acceptable for test setup but callers should avoid passing non-marshalable values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/json.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/pinningservice/pinning.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/pinningservice/pinning.go

Purpose: provides an in-memory Remote Pinning API implementation for CLI tests.

Important APIs and types: `NewRouter` registers `/api/v1/pins` routes for list/add/get/replace/delete and wraps them in `authHandler`. `PinningService` stores pins, a mutex, and a `PinAdded` callback. `Pin`, `PinStatus`, `AddPinRequest`, and `ListPinsResponse` model API payloads. Constants define match modes, statuses, and timestamp layout. `PinStatus.MarshalJSON` locks per-pin state during JSON marshaling.

Control flow: `authHandler` requires `Authorization: Bearer <token>` and returns structured JSON errors for missing/wrong tokens. `addPin` decodes a request, creates a queued `PinStatus` with UUID and timestamp, appends it under lock, writes HTTP 202, then invokes `PinAdded`. `listPins` parses filters for CID, name/match mode, status, before/after timestamps, limit, and meta, clones pin state for filtering, and returns original pointers up to the limit. `getPin`, `replacePin`, and `removePin` search by request ID and return success or 404 JSON errors.

State and persistence: pins live in memory. Service-level and per-pin mutexes protect concurrent test mutations, especially when tests change statuses while Kubo polls. `Clone` copies current fields but does not deep-copy nested maps/slices.

Dependencies and integration points: uses `httprouter`, Google UUIDs, JSON, HTTP status codes, reflection for meta comparison, and the Kubo remote pinning client.

Risks and test signals: the service is intentionally incomplete and only approximates the Remote Pinning API. It defaults list status to `pinned`, so tests must request queued/pinning/failed explicitly. The callback happens after the HTTP response, which lets tests simulate asynchronous transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/pinningservice/pinning.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/protobuf.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/protobuf.go

Purpose: estimates protobuf serialized sizes for dag-pb directory links, enabling tests to construct directories near block-size thresholds.

Important APIs: `VarintLen(v uint64) int` estimates protobuf varint byte length using `math/bits`. `LinkSerializedSize(nameLen, cidLen int, tsize uint64) int` computes a PBLink's wrapper and inner-field size. `EstimateFilesForBlockThreshold(threshold, nameLen, cidLen int, tsize uint64) int` estimates how many links fit under a block threshold, assuming four bytes of base overhead.

Control flow: size calculation adds field tags, varint lengths, raw CID/name bytes, and Tsize encoding, then divides the remaining threshold by per-link size.

State and persistence: no state.

Dependencies and integration points: mirrors sizing logic from boxo UnixFS directory code and supports CLI tests for UnixFS/HAMT/block threshold behavior.

Risks and test signals: this is an estimate tied to dag-pb encoding details and the empirically chosen base overhead. If upstream serialization changes, threshold tests using this helper may drift and require recalibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/protobuf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/random_deterministic.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/random_deterministic.go

Purpose: creates deterministic pseudo-random byte streams for tests that need large or exact-size data without storing fixtures.

Important APIs and types: `randomReader` holds a ChaCha20 cipher and remaining byte count. `DeterministicRandomReader(sizeStr, seed string)` parses human-readable sizes with `go-humanize`. `DeterministicRandomReaderBytes(size int64, seed string)` hashes the seed to a 32-byte key and returns a reader producing exactly `size` bytes.

Control flow: `randomReader.Read` returns EOF when no bytes remain, otherwise XORs a zero buffer through ChaCha20 into the requested slice, decreases `remaining`, and returns the number of bytes filled.

State and persistence: state is per-reader: cipher stream position and remaining bytes. No external persistence.

Dependencies and integration points: uses SHA-256 for seed-to-key derivation, `x/crypto/chacha20` for deterministic stream generation, and `go-humanize` for size strings.

Risks and test signals: zero nonce is acceptable for deterministic test data but not cryptographic use. Each reader is not concurrency-safe. Exact byte count behavior is the key signal; parse errors surface from humanize size parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/random_deterministic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/requires.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/requires.go

Purpose: skip-gate helpers for optional or environment-dependent CLI test categories.

Important APIs: `RequiresDocker`, `RequiresFUSE`, `RequiresExpensive`, `RequiresPlugins`, and `RequiresLinux` call `t.SkipNow` or `t.Skip` when prerequisites are absent. `isFUSEAvailable` checks platform and required unmount tool.

Control flow: Docker tests run only when `TEST_DOCKER=1`. FUSE tests skip when `TEST_FUSE=0`, always run when `TEST_FUSE=1`, otherwise auto-detect supported OS and `fusermount` on Linux or `umount` elsewhere. Expensive tests skip when `TEST_EXPENSIVE=1` or `testing.Short()` is true. Plugin tests require `TEST_PLUGIN=1`. Linux tests require `runtime.GOOS == "linux"`.

State and persistence: no persistent state; behavior is controlled by environment variables and host platform/tooling.

Dependencies and integration points: used by tests such as tracing and FUSE suites to avoid running unsupported integration tests. It imports `os`, `os/exec`, `runtime`, and `testing`.

Risks and test signals: `RequiresExpensive` appears counterintuitive because it skips when `TEST_EXPENSIVE=1`, which may be intentional inversion or a bug depending on suite conventions. Host tool detection is shallow; presence of `fusermount` does not guarantee FUSE permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/requires.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/strings.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/testutils/strings.go

Purpose: common string, multiaddr, and parallel iteration helpers for CLI tests.

Important APIs and variables: `AlphabetEasy` and `AlphabetHard` provide character sets. `StrCat` concatenates strings and string slices while dropping empty strings. `PreviewStr` returns a 10-byte preview with ellipsis when truncated. `SplitLines` scans a string into lines. `URLStrToMultiaddr` converts a URL host to a TCP multiaddr. `ForEachPar` runs a function over a slice concurrently and waits.

Control flow: `StrCat` type-switches each arg and panics on unsupported types. `PreviewStr` uses byte slicing, not rune slicing. `URLStrToMultiaddr` parses URL and `netip.AddrPort`, converts to `net.TCPAddr`, then to multiaddr. `ForEachPar` uses a `sync.WaitGroup` and launches one goroutine per element.

State and persistence: no persistent state. `ForEachPar` has transient goroutines.

Dependencies and integration points: used widely for command argument composition, log-friendly previews, multiaddr conversion in HTTP routing tests, and parallel harness operations.

Risks and test signals: `PreviewStr` can split UTF-8 sequences because it slices bytes. `URLStrToMultiaddr` panics for hostnames without numeric IP:port. `ForEachPar` does not recover panics and has no concurrency limit, so callers should avoid very large slices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/testutils/strings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/tracing_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/tracing_test.go

Purpose: integration test for OpenTelemetry trace export from the Kubo daemon to an OTLP collector.

Important APIs and data: `otelCollectorConfigYAML` defines an OpenTelemetry Collector config with OTLP gRPC receiver and file exporter to `/traces/traces.json`. `TestTracing` uses `testutils.RequiresDocker`, Docker CLI, host networking, node environment variables, and daemon startup.

Control flow: the test skips unless Docker tests are enabled. It writes collector config and an empty writable `traces.json` into the node directory, runs `docker run --rm --detach` with volume mounts and `--net host`, registers cleanup to stop the named container, sets `OTEL_TRACES_EXPORTER=otlp`, `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`, and `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`, starts the daemon, and waits up to five minutes until `traces.json` contains `go-ipfs`.

State and persistence: trace output is written to the node directory by the collector container. The Docker container is named `ipfs-test-otel-collector` and should be stopped during cleanup.

Dependencies and integration points: requires Docker, host networking, the `otel/opentelemetry-collector-contrib:0.52.0` image, file permissions compatible with container writes, OpenTelemetry environment variable handling, and daemon instrumentation.

Risks and test signals: fixed container name can collide with stale/running containers. Host networking and image pulls can fail in CI. The five-minute wait is long but necessary for collector startup. Failure means traces were not exported, collector did not write the file, or instrumentation service name changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/tracing_test.go -->
