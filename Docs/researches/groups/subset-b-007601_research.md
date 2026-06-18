# subset-b-007601 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bench/offline_add/main.go -->
# sources/distributed-fs/ipfs-kubo/test/bench/offline_add/main.go

Purpose: standalone Go benchmark driver for measuring `ipfs add` throughput in an offline-style fresh-repo loop. It creates an isolated temporary IPFS repo, runs `ipfs init`, generates deterministic random file contents, and times only the `ipfs add` command.

Important APIs and functions: `main` calls `compareResults`; `compareResults` iterates `unit.Information` sizes and logs `testing.BenchmarkResult`; `benchmarkAdd` uses `testing.Benchmark`, `b.SetBytes`, `b.TempDir`, `exec.Command`, `config.EnvDir`, `config.DefaultPathName`, and `random.NewSeededRand`. Control flow stops the benchmark timer for repo setup and test-file generation, starts it around `ipfs add`, then stops again before the next iteration. The loop condition in `compareResults` starts at `10 * unit.MB` and doubles while `amount > 0`, so it intentionally runs until integer overflow wraps to non-positive.

State and persistence: all repo state is under `b.TempDir()` via the IPFS path environment variable; input data is a temporary OS file removed with `defer os.Remove`. Dependencies are the installed `ipfs` binary, Kubo config constants, and go-test deterministic random data. Integration is external-process based, so benchmark validity depends on PATH, binary build, and host filesystem behavior. Risks include extremely long/overflow-driven benchmarking, no result comparison despite the TODO, and benchmark noise from repeated repo initialization. Test signal is performance-only, not a unit assertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bench/offline_add/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bin/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/test/bin/Rules.mk

Purpose: makefile fragment that builds Go-based test helper binaries into `test/bin` and adds that directory to PATH for the test harness. It defines a reusable `go-build-testdep` recipe that changes into `test/dependencies` and runs `$(GOCC) build $(go-flags-with-tags) -o "$OUT" "$<"`.

Important targets: `pollEndpoint`, `go-sleep`, `go-timeout`, `iptb`, `ma-pipe-unidir`, `json-to-junit`, `gotestsum`, `hang-fds`, `multihash`, `cid-fmt`, `random-data`, `random-files`, `gocovmerge`, and `golangci-lint`. Each target is declared `.PHONY` against its Go import path, maps to `$(d)/binary-name`, appends itself to `TGTS_$(d)`, and depends on `$(DEPS_GO)` through the aggregate rule.

Control flow is standard make expansion: include `mk/header.mk`, accumulate targets, declare cleanup with `CLEAN += $(TGTS_$(d))`, prepend `$(realpath $(d))` to PATH, and include `mk/footer.mk`. State is the generated helper binaries; cleanup is delegated to the larger make system. Risks include network/module resolution if dependencies are not vendored or cached, PATH shadowing from generated helpers, and brittle import-path target names if dependencies move. Test signal is indirect: many sharness/CLI tests rely on these helpers being present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bin/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bin/checkflags -->
# sources/distributed-fs/ipfs-kubo/test/bin/checkflags

Purpose: POSIX shell helper that prints a message only when a persisted flag value changes. It is used as a small stateful gate for test or build messages.

Important interface: `checkflags FILE VALUES MSG...`. It validates at least three arguments, assigns the first argument to `FLAG_FILE`, the second to `FLAG_VALS`, and the remainder to `FLAG_MSGS`. If the file does not exist it is touched. The script compares `x"$FLAG_VALS"` to `x"$(cat "$FLAG_FILE")`; the `x` prefix prevents values that begin with `-` or are empty from being interpreted specially by `test`.

Control flow is linear: validate arguments, ensure the state file exists, compare stored and new values, then echo the message and overwrite the file on change. State and persistence are exactly the contents of `FLAG_FILE`. Dependencies are `/bin/sh`, `cat`, `touch`, and shell redirection. Risks include an unquoted `test -f $FLAG_FILE` path, so paths with whitespace or glob characters are unsafe, and concurrent writers can race because updates are not atomic. Test signal is minimal; correctness is observable by repeated invocations with changed or unchanged values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bin/checkflags -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bin/continueyn -->
# sources/distributed-fs/ipfs-kubo/test/bin/continueyn

Purpose: interactive shell confirmation helper that exits successfully for yes and unsuccessfully for no, with non-interactive contexts treated as yes.

Important interface: no arguments are used. The script first checks `test -t 1 || exit 0`, so when stdout is not a terminal it exits 0 immediately. In interactive use it prompts with `read -p "continue? [y/N] " REPLY`, emits a blank line, and returns 0 only for replies beginning with `Y` or `y`; all other replies return 1.

Control flow and state are trivial; there is no persistence. Dependencies are `/bin/sh` and a shell supporting `read -p`, which is common but not strictly POSIX in all shells. Integration points are build/test scripts that want opt-in pauses for human runs but must not block automation. Risks include checking stdout rather than stdin for terminal detection, shell portability of `read -p`, and default-deny behavior in terminals. Test signal is manual or wrapper-level: automated use should observe a zero exit without blocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/bin/continueyn -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/add_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/add_test.go

Purpose: large CLI integration suite for `ipfs add`, import defaults, configuration overrides, UnixFS traversal behavior, and fast provide behavior. It uses the Kubo CLI harness to create isolated repos, start daemons, execute commands, and inspect resulting DAGs or logs.

Important functions: `waitForLogMessage`, `TestAdd`, `TestAddFastProvide`, and deterministic directory helpers `createDirectoryForHAMTLinksEstimation`, `createDirectoryForHAMTBlockEstimation`, and `createDeterministicFiles`. The tests cover CID version and hash selection from `Import.CidVersion` and `Import.HashFunction`, CLI override precedence, raw leaf behavior, `--pin-name` validation, `--max-file-links`, hidden file inclusion, empty directory inclusion/exclusion, and symlink preservation versus `--dereference-args` and `--dereference-symlinks`.

Control flow is subtest-heavy and parallelized. Most tests allocate a new node, mutate config, start a daemon, run `ipfs add`, and validate CIDs, `ipfs ls`, `ipfs get`, pin output, or daemon logs. State is per-test repo contents, generated files, pins, UnixFS DAGs, and daemon stderr buffers. Dependencies include config optional fields, harness helpers, deterministic random file generation, and PB node inspection. Risks include timing-sensitive fast-provide log waits, filesystem symlink behavior, and expensive large-file generation. Test signals are strong end-to-end regressions for CLI/config precedence and traversal semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/add_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/agent_version_unicode_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/agent_version_unicode_test.go

Purpose: unit-style tests for `cmdutils.CleanAndTrim`, focused on peer agent/version string sanitization with Unicode. It ensures useful Unicode remains visible while dangerous invisible/control formatting characters are replaced and overly long strings are truncated.

Important tests: `TestCleanAndTrimUnicode`, `TestCleanAndTrimIdempotent`, and `TestCleanAndTrimSecurity`. The table covers ASCII, Polish, Chinese, Arabic, emoji, combining marks, private-use characters, leading/trailing whitespace, zero-width characters, bidi overrides/isolates, controls, soft hyphen and other format characters, and 128-rune truncation. Idempotence applies the sanitizer twice and requires identical output. Security assertions ensure no zero-width spaces, bidi overrides, or ASCII control characters survive.

Control flow is simple table-driven testing with `assert.Equal` and custom predicate checks. State is only in-memory strings. Dependencies are `cmdutils.CleanAndTrim`, `strings`, and testify assertions. Integration point is user-visible and network-visible agent version metadata, where misleading bidirectional or invisible characters are a security risk. Risks include rune-count truncation splitting grapheme clusters and tests intentionally preserving complex combining marks that may still render oddly. Test signal is precise for sanitization categories and stable across platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/agent_version_unicode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/api_file_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/api_file_test.go

Purpose: integration test for daemon readiness ordering of `$IPFS_PATH/api` and `$IPFS_PATH/gateway` address files. It guards tools such as systemd path units that react as soon as those files appear.

Important test: `TestAddressFileReady` has `api file` and `gateway file` subtests. Each starts `ipfs daemon` in the background using `(*exec.Cmd).Start` instead of the harness helper that waits for readiness. It polls for the address file up to 100 times with 100 ms sleeps, then immediately reads the address and performs an HTTP request.

Control flow for API extracts IP and TCP port from the multiaddr and posts to `/api/v0/id`; gateway reads the URL from the `gateway` file and GETs `/ipfs/bafkqaaa`. State is daemon-managed repo address files and live HTTP listeners. Dependencies include `net/http`, `os.Stat`, multiaddr protocol values, and harness process management. Risks include timing flakes on slow hosts, assumption of IPv4/TCP address extraction for API, and external HTTP server readiness subtleties. Test signal is direct: file existence must imply immediate successful HTTP status 200.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/api_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/autoconf_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/autoconf_test.go

Purpose: broad AutoConf integration suite covering fetch, cache, background refresh, fallback, disabled behavior, bootstrap expansion, HTTPS, and daemon use of resolved bootstrap peers. It establishes the expected architecture: daemon/network refresh populates cache, user-facing config preserves `auto`, and explicit expansion resolves placeholders.

Important helpers and tests: `TestAutoConf` delegates to `testAutoConfBasicFunctionality`, `testAutoConfBackgroundService`, `testAutoConfHTTPErrors`, `testAutoConfCacheBasedExpansion`, `testAutoConfDisabled`, `testBootstrapListResolved`, `testDaemonUsesResolvedBootstrap`, `testEmptyCacheUsesFallbacks`, `testStaleCacheWithUnreachableServer`, `testAutoConfDisabledWithAutoValues`, `testAutoConfNetworkBehavior`, and `testAutoConfWithHTTPS`. `loadTestData` reads JSON fixtures.

Control flow uses `httptest` servers with ETags, changing payloads, unreachable URLs, and self-signed TLS. Nodes are configured via `AutoConf.URL`, `Enabled`, `RefreshInterval`, `Bootstrap`, `Routing.DelegatedRouters`, and `DNS.Resolvers`; daemons are started to trigger fetch or background update. State includes the AutoConf cache, repo config with literal `auto`, daemon logs, and live peer connections. Dependencies are the harness, HTTP servers, JSON fixtures, and Kubo config expansion. Risks include sleeps up to several seconds, port assumptions in bootstrap peer tests, and fallback values changing. Test signals are end-to-end daemon responsiveness, request counts, expanded config JSON, and preserved `auto` config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/autoconf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/dns_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/dns_test.go

Purpose: tests AutoConf-provided DNS-over-HTTPS resolver integration for IPNS/DNSLink resolution. It verifies that `DNS.Resolvers` entries set to `auto` remain visible in config but resolve through endpoints supplied by AutoConf.

Important types and functions: `mockDoHServer`, `newMockDoHServer`, `handleDNSQuery`, `getRequests`, `testDNSResolutionWithAutoDoH`, and `testDNSErrorHandling`. The mock server accepts DoH GET `?dns=` and POST wire-format requests, unpacks `miekg/dns` messages, records query names, and returns TXT DNSLink answers or NXDOMAIN depending on `responseFunc`.

Control flow builds an AutoConf JSON whose `DNSResolvers` maps a suffix such as `foo.` or `bar.` to the mock `/dns-query` URL, starts a daemon, runs `ipfs resolve /ipns/...`, and checks output or failure. State is mock request history plus node config/cache. Dependencies include `github.com/miekg/dns`, `httptest`, base64url DNS wire encoding, and the CLI harness. Risks include resolver behavior changing between GET and POST, DNS name normalization/trailing dots, and reliance on a fixed CID in DNSLink. Test signal confirms both successful DNSLink resolution and proper error propagation while still proving the DoH endpoint was queried.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/dns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_comprehensive_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_comprehensive_test.go

Purpose: comprehensive `--expand-auto` validation across all AutoConf-supported fields with a daemon-populated cache. It documents the intended split: daemon startup/background tasks perform network fetches, while CLI expansion reads cached AutoConf data.

Important functions: `TestExpandAutoComprehensive`, `testAllAutoConfFieldsResolve`, `testBootstrapCommandConsistency`, `testWriteOperationsFailWithExpandAuto`, `testConfigShowExpandAutoComplete`, `testMultipleExpandAutoUsesCache`, `testCLIUsesCacheOnlyDaemonUpdatesBackground`, `loadTestDataComprehensive`, and `startDaemonAndWaitForAutoConf`. The helper starts a daemon and polls an atomic request counter instead of sleeping blindly.

Control flow creates mock AutoConf data with `SystemRegistry`, `DNSResolvers`, and `DelegatedEndpoints`, starts a daemon, then runs `ipfs config FIELD --expand-auto`, `ipfs bootstrap list --expand-auto`, and `ipfs config show --expand-auto`. It parses JSON outputs and requires exact mock URLs for delegated routers and IPNS publishers. Write operations with `--expand-auto` must fail because expansion is read-only. State is cache content, request counters, and CLI JSON output. Dependencies include `httptest`, `atomic.Int32`, Kubo harness, and fixture JSON. Risks include strict request-count assumptions if background refresh timing changes and hard-coded fallback/mock endpoint expectations. Test signal is high-value for cache-only CLI behavior and field consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_comprehensive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_fallback_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_fallback_test.go

Purpose: verifies `--expand-auto` fallback behavior when AutoConf cannot fetch or parse remote data, when AutoConf is disabled, and when configs mix static and `auto` values.

Important functions: `TestExpandAutoFallbacks`, `testExpandAutoWithUnreachableServer`, `testExpandAutoWithDisabledAutoConf`, `testExpandAutoWithMalformedResponse`, `testExpandAutoMixedConfigPreservesStatic`, `testDaemonWithMalformedAutoConf`, and `loadTestDataForFallback`. The malformed-daemon test also uses `autoconf.GetMainnetFallbackConfig` to compare expected fallback bootstrap peers.

Control flow uses unreachable URLs, malformed JSON servers, valid fixture servers, and daemon-start flows. It runs `ipfs config Bootstrap --expand-auto`, `DNS.Resolvers --expand-auto`, and daemon health checks. Static peers surrounding `auto` must stay at the beginning/end after expansion. State is repo config, fallback output, and daemon cache/error handling. Dependencies include boxo AutoConf fallback constants, harness config setters, `httptest`, and JSON parsing. Risks include fallback fixture drift and the invalid port string `127.0.0.1:99999`, which depends on URL parsing/fetch error handling. Test signal ensures broken AutoConf services do not make daemons unusable and do not persist literal `auto` in expanded views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_fallback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_test.go

Purpose: focused tests for preserving literal `auto` in stored config and expanding it only on explicit read paths. It also validates delegated endpoint filtering for supported routing/IPNS paths and native-versus-delegated system selection.

Important functions: `TestAutoConfExpand`, `testConfigCommandsShowAutoValues`, `testMixedConfigurationPreserved`, `testConfigReplacePreservesAuto`, `testExpandAutoFiltersUnsupportedPathsDelegated`, `testExpandAutoWithAutoRouting`, `testExpandAutoWithMixedSystems`, `testExpandAutoWithFiltering`, `testExpandAutoWithoutCacheDelegated`, `testExpandAutoWithoutCacheAuto`, and `loadTestDataExpand`.

Control flow sets `Bootstrap`, `DNS.Resolvers`, `Routing.DelegatedRouters`, and `Ipns.DelegatedPublishers` to `auto` or mixed static values, reads them normally, then uses `--expand-auto`. Some tests start daemons and wait for cache prewarming before asserting filtered endpoints from fixture files; no-cache tests expect hardcoded fallbacks. State includes stored config, daemon cache, and expanded JSON output. Dependencies are the CLI harness, `httptest`, fixture AutoConf JSON, and config replace. Risks include sleeps for cache fetch, exact endpoint expectations, and behavior changes in fallback routing systems. Test signal protects user-facing config semantics: `auto` remains durable, expansion is explicit, ordered, and filtered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/expand_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/extensibility_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/extensibility_test.go

Purpose: integration/regression test proving AutoConf can describe previously unknown routing systems and Kubo can use their delegated endpoints without hard-coding every system name.

Important test: `TestAutoConfExtensibility_NewSystem`. It is skipped in short mode. The test builds AutoConf JSON containing `AminoDHT`, `IPNI`, and `NewSystem`, with native bootstrap data and delegated endpoint data. It uses two `httptest` servers: one for AutoConf and one for the NewSystem routing endpoint.

Control flow configures a node with `AutoConf.URL`, `AutoConf.Enabled`, short refresh interval, `Routing.Type=auto`, `Bootstrap=["auto"]`, and `Routing.DelegatedRouters=["auto"]`. After daemon startup and a wait, `bootstrap list --expand-auto` must include AminoDHT bootstrap peers, while `config Routing.DelegatedRouters --expand-auto` must include IPNI and NewSystem provider URLs with `/routing/v1/providers`. State is daemon cache and expanded routing output. Dependencies include `config.Config` mutation, slices/string matching, and live HTTP servers. Risks include timing wait, endpoint exactness, and duplicated initial mock-server setup. Test signal validates extensibility and native/delegated filtering boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/extensibility_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/fuzz_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/fuzz_test.go

Purpose: adversarial/table-driven tests for the boxo AutoConf client parser and validation behavior. Despite the filename, these are deterministic fuzz-style cases run through `httptest` servers and fallback detection.

Important helpers: `testAutoConfWithFallback`, `testAutoConfWithFallbackAndTimeout`, and `generateManyResolvers`. Test groups cover AutoConf version types/ranges, bootstrap arrays, DNS resolvers, delegated endpoints/routers, delegated publisher URLs, malformed JSON, and large payloads. A custom fallback config with marker version `-999` proves when parsing or validation falls back.

Control flow creates JSON maps per case, serves them over HTTP, constructs an `autoconf.Client` with URL, user agent, refresh interval, timeout, and fallback function, then calls `GetCachedOrRefresh`. Success cases validate parsed `autoconf.Config` fields; expected-error cases require fallback usage. State is in-memory config plus fallback boolean. Dependencies include `github.com/ipfs/boxo/autoconf`, `context`, `httptest`, JSON, and testify. Risks include expectations documenting current parser leniency, such as negative versions and HTTP delegated publisher URLs being accepted, and large payload tests consuming time/memory. Test signal is strong for schema hardening and graceful fallback instead of panic or partial invalid cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/ipns_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/ipns_test.go

Purpose: tests IPNS publishing with AutoConf-resolved delegated publisher endpoints and documents resilient publish semantics when endpoints fail.

Important functions and types: `TestAutoConfIPNS`, `testIPNSPublishingWithWorkingEndpoint`, `testIPNSPublishingResilience`, `setupNodeWithAutoconf`, `createAutoconfJSON`, and `mockIPNSPublisher` with `handleIPNS`, `getPublishedKeys`, `getRecordPayload`, and `close`. The mock publisher implements `/routing/v1/ipns/{peerID}` for PUT and GET-like inspection state.

Control flow creates an AutoConf server with a delegated endpoint supporting `/routing/v1/ipns`, starts a node with `Ipns.DelegatedPublishers=["auto"]`, publishes an IPNS record, waits for async HTTP PUT, compares the captured PUT payload with `ipfs routing get /ipns/<peer>`, and inspects the record. Resilience subtests force publisher HTTP 500 responses for `Routing.Type=auto` and `delegated` and require local publish commands to still succeed. State includes node key/IPNS records, delegated endpoint request payloads, and local repo storage. Dependencies include boxo AutoConf fallback bootstrappers, harness CLI commands, JSON, HTTP servers, and IPNS record tooling. Risks include asynchronous timing sleeps and subtle distinction between delegated failure and local publish success. Test signal validates both endpoint use and non-fatal delegated publish failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/ipns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/routing_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/routing_test.go

Purpose: tests that AutoConf can supply delegated routing endpoint configuration and that daemon startup remains healthy when endpoints are empty or offline-mode routing cannot be exercised fully.

Important types/functions: `mockRoutingServer`, `newMockRoutingServer`, `handleProviders`, `testDelegatedRoutingWithAuto`, and `testRoutingErrorHandling`. The mock routing server serves NDJSON provider records at `/routing/v1/providers/{cid}` and records requested CIDs. `providerFunc` allows normal provider records or empty responses.

Control flow creates AutoConf JSON with a `DelegatedEndpoints` entry supporting providers, peers, and IPNS read paths, configures a node with `Routing.DelegatedRouters=["auto"]`, and starts the daemon with `--offline`. It then confirms stored config still shows `auto` and the daemon accepts `version`. The error-handling variant uses empty provider responses but the same startup/config assertions. State is node config/cache and mock request history, though actual routing calls are not deeply exercised. Dependencies include `httptest`, JSON, harness, and delegated routing HTTP response format. Risks include limited behavioral coverage because offline mode avoids real routing queries. Test signal is startup/config preservation rather than provider retrieval correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/routing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/swarm_connect_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/swarm_connect_test.go

Purpose: regression test for `ipfs swarm connect` when AutoConf is enabled and a daemon is already running. It guards a previous failure mode where AutoConf interfered with CLI fallback/API behavior and produced a generic connect error.

Important functions: `TestSwarmConnectWithAutoConf` and `testSwarmConnectWithAutoConfSetting`. The test runs two cases, AutoConf disabled and enabled, both expecting success.

Control flow initializes a test-profile node, sets `AutoConf.Enabled`, installs bootstrap peers from AutoConf fallback defaults, starts the daemon, waits three seconds, verifies `ipfs id`, then runs `ipfs swarm connect /dnsaddr/bootstrap.libp2p.io`. It checks exit code 0, stdout containing `success`, and `ipfs id` output with non-null `Addresses`. State is daemon process, bootstrap config, swarm connection attempts, and address output. Dependencies are public DNS/bootstrap reachability, harness, and Kubo daemon API routing. Risks include network flakiness, public bootstrap availability, and the fixed sleep. Test signal is a direct CLI regression check across the AutoConf toggle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/swarm_connect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_amino_and_ipni.json -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_amino_and_ipni.json

Purpose: AutoConf fixture with both a native AminoDHT system and a delegated IPNI system. It supports tests that verify `Routing.Type=auto` treats AminoDHT as native while still delegating IPNI endpoints.

Important schema fields: `AutoConfVersion` `2025072901`, `AutoConfSchema` `1`, `AutoConfTTL` `86400`, `SystemRegistry`, `DNSResolvers`, and `DelegatedEndpoints`. `AminoDHT` includes a native bootstrap peer and delegated read/write capability declarations. `IPNI` declares provider-read delegated capability. `DNSResolvers` maps `eth.` to `https://dns.eth.limo/dns-query`.

Control flow is data-only: tests load the JSON, serve it over `httptest`, and expand `Routing.DelegatedRouters` or `Ipns.DelegatedPublishers`. State represented is external AutoConf service data, not repo persistence. Dependencies are the boxo AutoConf schema and Kubo filtering code. Risks include fixture drift from real defaults and the use of example endpoints that should not be contacted as real services. Test signal: expanded routers should include `https://cid.contact/routing/v1/providers` for IPNI and should not delegate AminoDHT URLs in auto-routing mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_amino_and_ipni.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_new_routing_system.json -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_new_routing_system.json

Purpose: compact AutoConf fixture for a non-native `NewRoutingSystem`, used to prove new delegated systems can populate routing and IPNS publisher fields under auto routing.

Important fields: `SystemRegistry.NewRoutingSystem` has `URL`, description, `DelegatedConfig.Read` for providers, peers, and IPNS, and `DelegatedConfig.Write` for IPNS. `DNSResolvers.eth.` points at `dns.eth.limo`. `DelegatedEndpoints` maps `https://new-routing.example.com` to `Systems: ["NewRoutingSystem"]`, read providers/peers, and write IPNS.

Control flow is data-only. `expand_test.go` serves this fixture, starts a daemon to cache it, and expects `config Routing.DelegatedRouters --expand-auto` to include provider and peer URLs under `new-routing.example.com`, while `Ipns.DelegatedPublishers` includes `/routing/v1/ipns`. State is the declared service registry and endpoint capability matrix. Dependencies are path-joining/filtering logic in AutoConf expansion. Risks include unsupported endpoint schemes or path policy changes invalidating expected URLs. Test signal demonstrates extensibility for unknown delegated systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_new_routing_system.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_new_routing_with_filtering.json -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_new_routing_with_filtering.json

Purpose: AutoConf fixture for testing path filtering on a delegated `NewRoutingSystem`. It intentionally mixes supported and unsupported read/write paths.

Important fields: the system declares delegated support for `/routing/v1/providers`, `/routing/v1/peers`, `/routing/v1/ipns` reads and `/routing/v1/ipns` writes. `DelegatedEndpoints` includes `supported-new.example.com` with valid provider/peer read and IPNS write paths, `unsupported-new.example.com` with custom unsupported paths, and `mixed-new.example.com` with both valid and invalid paths.

Control flow is data-only. Tests load and serve the fixture, then require expansion to include only supported provider/peer/IPNS URLs and exclude custom paths such as `/custom/v0/read`, `/api/v1/nonstandard`, and `/invalid/path`. State is endpoint capabilities. Dependencies are Kubo's supported-path filter and URL construction rules. Risks include adding new supported delegated-routing paths without updating this fixture/test. Test signal validates path-level filtering without discarding an entire mixed endpoint that has at least one valid path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_new_routing_with_filtering.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_with_unsupported_paths.json -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_with_unsupported_paths.json

Purpose: AutoConf fixture for delegated-routing path filtering on an AminoDHT-associated endpoint set. It verifies that unsupported API paths are not exposed through `--expand-auto`.

Important fields: `AminoDHT` includes native bootstrap and delegated read/write declarations. `DNSResolvers.eth.` maps to `dns.eth.limo`. `DelegatedEndpoints` has `supported.example.com` with valid `/routing/v1/providers`, `/routing/v1/peers`, and `/routing/v1/ipns`; `unsupported.example.com` with nonstandard `/example/v0/*` and `/api/v1/custom`; and `mixed.example.com` with valid provider/peer/IPNS plus `/unsupported/path`.

Control flow is data-only and consumed by expansion tests after daemon cache prewarming. State is the remote capability description. Dependencies are AutoConf parser and supported-path filtering. Risks include differences between delegated routing mode and auto routing: AminoDHT can be native in auto mode but delegated in explicit delegated mode. Test signal is expected inclusion of valid supported/mixed URLs and exclusion of unsupported paths while preserving endpoint-level valid capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_with_unsupported_paths.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/updated_autoconf.json -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/updated_autoconf.json

Purpose: updated AutoConf fixture used by refresh/cache tests to simulate a newer remote configuration. It expands the bootstrap set, adds DNS resolver data, and includes more delegated endpoints than the baseline fixture.

Important fields: `AutoConfVersion` is `2025072902`, distinguishing it from `valid_autoconf.json`. `AminoDHT.NativeConfig.Bootstrap` contains seven bootstrap multiaddrs, including DNS, TCP, and QUIC variants. `IPNI` points to `https://ipni.example.com`. `DNSResolvers` includes two `eth.` DoH URLs and `test.`. `DelegatedEndpoints` includes IPNI, routing.example.com, delegated-ipfs.dev with providers/peers/IPNS read plus IPNS write, and ipns.example.com for IPNS read/write.

Control flow is fixture-only: servers switch from initial to updated content or serve it for post-refresh tests. State represented is a remote versioned config and cache replacement candidate. Dependencies are schema compatibility and validation of multiaddrs/URLs. Risks include hard-coded public bootstrap peers and example endpoints becoming inconsistent with validation policy. Test signal is request-count and expansion behavior when remote AutoConf changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/updated_autoconf.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/valid_autoconf.json -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/valid_autoconf.json

Purpose: baseline valid AutoConf fixture used across basic, expansion, fallback, cache, and consistency tests. It represents mainnet-like AminoDHT plus IPNI data in a small stable JSON payload.

Important fields: `AutoConfVersion` `2025072901`, schema `1`, TTL `86400`, `SystemRegistry.AminoDHT` with seven bootstrap multiaddrs and delegated read/write path capabilities, `SystemRegistry.IPNI` with provider-read capability, `DNSResolvers.eth.` with two DoH URLs, and `DelegatedEndpoints` for `https://ipni.example.com` and `https://delegated-ipfs.dev`.

Control flow is data-only. Tests serve it over `httptest`, use it to populate the daemon AutoConf cache, and assert that `Bootstrap`, `DNS.Resolvers`, `Routing.DelegatedRouters`, `Ipns.DelegatedPublishers`, and full config show can expand away from literal `auto`. State is remote AutoConf content that may be cached by the daemon. Dependencies are valid multiaddr parsing and HTTP/HTTPS URL validation. Risks include fixture duplication with fallback defaults and exact endpoint assumptions. Test signal is broad because many tests rely on this file as the canonical valid payload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/valid_autoconf.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/validation_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/validation_test.go

Purpose: daemon-level validation tests ensuring invalid AutoConf payloads do not prevent daemon startup and do not become trusted cached configuration.

Important functions: `TestAutoConfValidation`, `testInvalidAutoConfJSONPreventsCaching`, `testMalformedMultiaddrInAutoConf`, and `testMalformedURLInAutoConf`. Each creates an `httptest` AutoConf server returning invalid payloads: malformed bootstrap multiaddrs, invalid mixed multiaddr lists, or malformed DNS resolver URLs.

Control flow configures a test-profile node with `AutoConf.URL`, `AutoConf.Enabled=true`, and relevant `auto` config fields, starts the daemon, then runs `ipfs version` to prove daemon health. The first test also counts server requests to confirm validation was attempted. State includes daemon process, attempted remote payload, and any cache behavior inside the repo. Dependencies are AutoConf validation code, harness daemon startup, and JSON/URL/multiaddr parsing. Risks include tests not directly inspecting cache absence, only daemon survival and fetch attempt. Test signal protects graceful degradation: invalid remote AutoConf must be rejected without making core CLI commands unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/autoconf/validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/backup_bootstrap_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/backup_bootstrap_test.go

Purpose: integration test for backup bootstrap peer persistence and reconnection. It verifies that peers learned during runtime can be saved as temporary backup bootstrap peers and used after restart to rejoin a small network.

Important test: `TestBackupBootstrapPeers`. It creates three nodes, clears configured bootstrap peers, assigns random local swarm ports, disables mDNS, and sets `Internal.BackupBootstrapInterval` to 250 ms. Nodes 0 and 1 are connected, then stopped after backup time; nodes 1 and 2 form a connection; node 0 restarts and is expected to discover both peers.

Control flow starts all daemons, checks initial peer counts, connects pairs, sleeps for backup persistence, restarts selected daemons, then asserts all three peer counts reach 2. State includes peerstore/swarm connections and whatever backup bootstrap storage Kubo writes in the repo. Dependencies include local networking, harness `Connect`, config mutation, and timing intervals. Risks include sleep-based timing, port contention, and peer connection convergence delays. Test signal is end-to-end: backup bootstrap should restore enough connectivity to bridge the three-node graph.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/backup_bootstrap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/basic_commands_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/basic_commands_test.go

Purpose: broad CLI sanity suite covering version output, command discovery, help consistency, documentation width, bad flag handling, and command flag listing.

Important functions: `parseVersionOutput`, `TestCurDirIsWritable`, `TestIPFSVersionCommandMatchesFlag`, `TestIPFSVersionAll`, `TestIPFSVersionDeps`, `TestIPFSCommands`, `TestAllSubcommandsAcceptHelp`, `TestAllRootCommandsAreMentionedInHelpText`, `TestCommandDocsWidth`, `TestAllCommandsFailWhenPassedBadFlag`, and `TestCommandsFlags`. It uses `IPFSCommands()` to enumerate commands and runs help/bad-flag checks against each.

Control flow is mostly parallel subtests. Version parsing uses a regexp and semver. Dependency output is split on replacements and validated with `golang.org/x/mod/module.Check`, skipping local replace paths. Help text root commands are compared to command discovery with a small exclusion map; width checks enforce 80 columns unless allowlisted. State is transient command output only. Dependencies are harness command execution, command registry output, semver parsing, module path validation, and testutils helpers. Risks include allowlist churn when docs change, command output formatting changes, and broad loops increasing test time. Test signal is high-level CLI contract coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/basic_commands_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/bitswap_config_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/bitswap_config_test.go

Purpose: integration tests for Bitswap configuration toggles, ensuring server/client behavior and daemon validation match `Bitswap.ServerEnabled`, `Bitswap.Libp2pEnabled`, and `HTTPRetrieval.Enabled`.

Important test: `TestBitswapConfig`. Subtests cover default server-enabled retrieval, server-disabled provider behavior, client retrieval while requester server is disabled, libp2p bitswap disabled with HTTP retrieval enabled, identify protocol suppression, and invalid configurations where both HTTP and libp2p retrieval are disabled.

Control flow creates provider/requester nodes, adds random test data, connects peers, and runs `ipfs cat`, `id`, `bitswap stat`, and `bitswap wantlist`. Some retrievals run in goroutines with timeout to avoid hanging on unavailable data. Identify protocol checks query remote peer protocols and ensure no bitswap protocol constants are advertised. State includes blockstore data, peer connections, config flags, and daemon startup failures. Dependencies include boxo bitswap protocol constants, harness networking, random bytes, and Kubo config. Risks include timing-based negative retrieval tests and changed error strings. Test signal verifies both data-plane behavior and configuration validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/bitswap_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/block_size_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/block_size_test.go

Purpose: boundary tests for Kubo block-size policy, UnixFS chunk-size enforcement, CAR import overrides, and practical Bitswap transfer limits over libp2p.

Important constants and helpers: `twoMiB`, `twoMiBPlus`, `maxChunkSize`, `libp2pMsgMax`, `bsBlockEnvelope`, `maxTransferBlock`, `blockSize`, `allBlockCIDs`, and `assertAllBlocksWithinLimit`. `TestBlockSizeBoundary` covers `block put`, `dag put`, `dag import`, `ipfs add` with raw/non-raw leaves, and peer exchange.

Control flow uses offline daemons for local block/DAG commands, pipes generated byte slices to `ipfs`, asserts success or specific oversized-block errors, exports/imports CAR files, and recursively stats DAG blocks. Exchange subtests start two nodes, connect them, and attempt `block get` or `cat` for exact boundary sizes with timeouts. State includes blockstore contents, CAR files, UnixFS DAGs, and peer transfers. Dependencies include random bytes, JSON block stat output, refs traversal, and libp2p message-size assumptions. Risks include high memory/time use from multi-megabyte blocks, exact protobuf overhead coupling, and transport constant drift. Test signal is precise for soft 2 MiB policy and hard libp2p envelope limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/block_size_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/bootstrap_auto_test.go -->
# sources/distributed-fs/ipfs-kubo/test/cli/bootstrap_auto_test.go

Purpose: tests CLI bootstrap command behavior when AutoConf uses the `auto` placeholder. It verifies adding, listing, removing, and mixed static-plus-auto bootstrap configurations.

Important test: `TestBootstrapCommandsWithAutoPlaceholder`. Subtests cover `bootstrap add default`, explicit `bootstrap add auto`, conversion of `default` to stored `auto`, failure when AutoConf is disabled, selective removal errors when `auto` is present, `rm --all` and `rm all`, and mixed specific peer plus `auto` configurations.

Control flow initializes test-profile nodes, sets `AutoConf.Enabled` and `Bootstrap`, runs `ipfs bootstrap` subcommands, and asserts stdout/stderr plus stored config values. State is persistent repo config for `Bootstrap` and AutoConf settings. Dependencies are harness command execution and bootstrap command validation code. Risks include exact user-facing error strings and semantics around mixing `auto` with specific peers. Test signal is strong for preserving placeholder semantics: `default` maps to `auto`, disabled AutoConf rejects auto insertion, individual removals are blocked when placeholder expansion would be ambiguous, and all-removal clears everything.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/cli/bootstrap_auto_test.go -->
