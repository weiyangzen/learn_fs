# Research: subset-b-000206

Grouped research report for the assigned Moby integration networking, plugin, and secret sources. Each file section preserves the original source path and is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/bridge_linux_test.go -->
# sources/cloud-native/moby/integration/networking/bridge_linux_test.go

## Purpose
Linux bridge-network integration coverage for Docker Engine. The file exercises bridge driver behavior across inter-container communication, inter-network isolation, NAT/routed/nat-unprotected gateway modes, published-port reachability, default bridge IPv6 addressing, internal networks, per-endpoint sysctls, IPv4/IPv6 disablement, docker-proxy gateway selection, gratuitous ARP/neighbour advertisement, firewall ordering, legacy links, Swarm DNS interaction, explicit IP assignment, network disconnect recovery, and publish-all regressions.

## Important APIs, Types, And Functions
The tests use `daemon.New`, `StartWithBusybox`, `Restart`, `StartAndSwarmInit`, and `NewClientT` to run isolated daemon instances. Network setup flows through `integration/internal/network` helpers such as `CreateNoError`, `RemoveNoError`, `WithDriver`, `WithIPv6`, `WithIPv4(false)`, `WithInternal`, `WithIPAM`, `WithOption`, `WithIPvlan`, and endpoint `DriverOpts`. Container lifecycle uses `container.Run`, `RunAttach`, `ExecT`, `Inspect`, `WithNetworkMode`, `WithEndpointSettings`, `WithPortMap`, `WithExposedPorts`, `WithIPv4`, `WithIPv6`, `WithMacAddress`, `WithSysctls`, `WithLinks`, and `WithPublishAllPorts`.

The local `expProxyCfg` type describes expected docker-proxy processes, and `checkProxies` inspects child processes of the daemon, parses `docker-proxy` flags, resolves expected container IPs from inspect output, and compares exact proxy bindings.

## Control Flow
Most tests create a daemon, create one or more bridge networks with explicit options, start containers, then assert connectivity or isolation using `ping`, `ping6`, `wget`, `httpd`, `ip`, `sysctl`, `nslookup`, or inspect output. Matrix tests iterate gateway modes, IP families, userland proxy settings, internal/external networks, and firewall backends. Several tests run subtests in parallel only after shared network setup is complete.

`TestBridgeICC` verifies same-network DNS, ARP/NDP, and IPv4/IPv6 connectivity, including link-local and SLAAC cases. `TestBridgeINC`, `TestBridgeINCRouted`, `TestAccessToPublishedPort`, and `TestInterNetworkDirectRouting` validate cross-network isolation and gateway-mode semantics. `TestDefaultBridgeIPv6` and `TestDefaultBridgeAddresses` check default bridge IPv6 assignment and daemon restart behavior when `fixed-cidr-v6` changes. `TestGatewaySelection` mutates network attachments and expects docker-proxy bindings to move between IPv4-only, IPv6-only, dual-stack, and ipvlan endpoints. `TestAdvertiseAddresses` and `TestAdvertiseAddressesLiveRestore` listen for unsolicited ARP/NA packets and verify neighbor cache updates.

## State And Persistence Behavior
The tests deliberately mutate daemon state, bridge interfaces, firewall rules, network endpoint membership, proxy processes, ARP/ND neighbor caches, and container inspect metadata. Persistence is tested across container stop/start and daemon restart in default bridge addressing, live-restore advertisement, configured gateway recovery, and publish-all behavior. Cleanup is handled through deferred network removal, container removal, daemon stop, and helper cleanup for synthetic interfaces.

## Dependencies And Integration Points
This file integrates with Linux kernel networking, iptables/nftables, firewalld reloads, docker-proxy process management, libnetwork bridge labels (`bridge.*`, `netlabel.*`), Swarm initialization, OpenTelemetry test spans, Moby integration helpers, and BusyBox tools. Some paths depend on host namespace visibility and are skipped for rootless or incompatible firewall backends.

## Risks
Primary risks are host-network flakiness, timing-sensitive ARP/NA packet capture, dependence on `ps` output format for proxy inspection, firewall backend differences, rootless namespace differences, and assumptions about BusyBox command behavior. Tests that mutate firewall policies or host bridge state must clean up reliably or can affect later integration tests. Link-local IPv6 and firewalld interactions are especially sensitive to environment configuration.

## Test Signals
Strong signals include explicit exit-code checks, stdout/stderr substring assertions, `NetworkInspect` and container inspect validation, exact docker-proxy process comparisons, golden-style packet count/interval checks, and daemon restart assertions. Several comments tie cases to regressions such as issues 46829, 47329, 47619, 47751, 49509, 49518, 51491, 51569, 51578, 51620, and feature request 51796.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/bridge_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/drivers_windows_test.go -->
# sources/cloud-native/moby/integration/networking/drivers_windows_test.go

## Purpose
Windows-specific integration coverage for Docker network drivers and endpoint behavior. It validates NAT, transparent, and l2bridge network creation; NAT port mapping; DNS resolution; lifecycle connect/disconnect/delete operations; network isolation; and endpoint management for multiple containers on one network.

## Important APIs, Types, And Functions
Uses `testEnv.APIClient`, `client.NetworkCreateOptions`, `NetworkInspect`, `NetworkConnect`, `NetworkDisconnect`, `container.Run`, `RunAttach`, `Inspect`, `WithNetworkMode`, `WithExposedPorts`, `WithPortMap`, and Windows ping/PowerShell commands. `network.WithDriver` and `network.WithOption("com.docker.network.windowsshim.dnsservers", ...)` supply Windows driver options. `poll.WaitOn` wraps host-to-container HTTP readiness.

## Control Flow
`TestWindowsNetworkDrivers` iterates `nat`, `transparent`, and `l2bridge`, creates a network, tolerates known l2bridge host-config failure, then inspects driver/name. `TestWindowsNATDriverPortMapping` runs a PowerShell `HttpListener` in a NAT container, maps port 80 to host 8080, checks inspect metadata, and polls `http://localhost:8080`. `TestWindowsNetworkDNSResolution` creates NAT networks with optional DNS options and validates name resolution by pinging one container from another. Lifecycle and isolation tests attach/detach containers and assert inspect state or failed cross-network pings. Endpoint management creates three containers and checks network inspect container count plus same-network pings.

## State And Persistence Behavior
State is limited to temporary Windows networks and containers. The lifecycle test explicitly proves endpoint detachment removes inspect state, reconnection restores it, and network deletion makes inspect fail. No daemon restart or persistent on-disk state is tested.

## Dependencies And Integration Points
Depends on Windows container networking, HNS/network drivers, Windows ping output, PowerShell, HTTP listener behavior, and container runtime support. `TestWindowsNetworkLifecycle` skips Windows containerd because `NetworkConnect` is known unsupported in that mode.

## Risks
Tests can be environment-sensitive: transparent and l2bridge require host network configuration, custom DNS option behavior may vary by Windows networking stack, ping output localization could affect string assertions, and fixed host port 8080 can collide with local services.

## Test Signals
Signals include driver/name equality in network inspect, port binding metadata, successful host HTTP response containing `OK`, ping success text (`Sent = 1, Received = 1, Lost = 0`), failed ping indicators for isolation, and network inspect container count.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/drivers_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/etchosts_test.go -->
# sources/cloud-native/moby/integration/networking/etchosts_test.go

## Purpose
Validates container `/etc/hosts` generation and update behavior for IPv4/IPv6 and multi-network disconnect scenarios. It protects regressions where IPv6-disabled containers received IPv6 host entries or stale network aliases remained after disconnect.

## Important APIs, Types, And Functions
Uses daemon helpers with `--ipv6` and `--fixed-cidr-v6`, container helpers for sysctls, hostname, extra hosts, and network mode, plus `NetworkConnect` and `NetworkDisconnect`. Golden assertions compare exact `/etc/hosts` content for multi-network state transitions.

## Control Flow
`TestEtcHostsIpv6` starts an IPv6-enabled daemon and runs two containers: one default and one with `net.ipv6.conf.all.disable_ipv6=1`. It pings `::1` to confirm IPv6 availability, reads `/etc/hosts`, appends expected container self entries from inspect output, and compares exact text. `TestEtcHostsDisconnect` creates bridge and ipvlan dual-stack networks, starts a container with hostname and extra hosts, connects/disconnects networks in different orders, and compares five golden states.

## State And Persistence Behavior
The file tests generated container filesystem state, specifically `/etc/hosts` content as endpoint attachments change. It confirms disconnect removes only entries for the detached network while preserving extra hosts and remaining network entries. No daemon restart persistence is exercised.

## Dependencies And Integration Points
Depends on Linux container filesystem generation, bridge and ipvlan network drivers, Docker endpoint bookkeeping, golden files under `integration/networking/testdata`, and BusyBox `cat`/`ping`.

## Risks
Exact text comparison is sensitive to line ordering, hostname formatting, and generated address ordering. The disconnect test deliberately avoids initial multi-network creation because generated entry order may be nondeterministic.

## Test Signals
Signals are precise: IPv6 ping exit code, exact `/etc/hosts` content for enabled/disabled IPv6, and five golden snapshots across connect/disconnect ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/etchosts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/firewall_linux_test.go -->
# sources/cloud-native/moby/integration/networking/firewall_linux_test.go

## Purpose
Checks that daemon `GET /info` exposes the expected Linux firewall backend metadata and that older API versions omit the field for compatibility.

## Important APIs, Types, And Functions
Uses `daemon.New`, `StartWithBusybox`, `client.Info`, `request.NewAPIClient` with API version `1.48`, `networking.FirewalldRunning`, and `DOCKER_FIREWALL_BACKEND`. The expected default backend is the local constant `defaultFirewallBackend = "iptables"`.

## Control Flow
The test starts a daemon, determines expected driver from `DOCKER_FIREWALL_BACKEND`, appends `+firewalld` when non-rootless and firewalld is running, then calls `Info` and asserts `Info.FirewallBackend` is present with the expected driver. A subtest creates an API 1.48 client and asserts the same field is nil.

## State And Persistence Behavior
No persistent network state is mutated beyond daemon startup. The test reads runtime daemon/firewall state and compatibility serialization behavior.

## Dependencies And Integration Points
Integrates Docker API version negotiation, daemon info response shape, rootless detection, firewalld detection, and configured firewall backend selection.

## Risks
Environment variables and firewalld state directly affect expectations. Backend naming changes or API version gates would break this test even if firewall behavior still works.

## Test Signals
Main signal is the exact `Info.FirewallBackend.Driver` match and presence/absence of the field by API version.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/firewall_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/mac_addr_test.go -->
# sources/cloud-native/moby/integration/networking/mac_addr_test.go

## Purpose
Tests MAC address allocation, persistence, inspect serialization, legacy API migration, and `NetworkConnect` endpoint MAC support. It focuses on distinguishing generated MACs from configured MACs and preserving/omitting them correctly across API versions and restart paths.

## Important APIs, Types, And Functions
Uses `container.WithMacAddress`, `EndpointSettings.MacAddress`, `NetworkConnect`, `ContainerStop`, `ContainerStart`, daemon restart, and low-level `request.Post` to send a legacy `MacAddress` field. The local `legacyCreateRequest` embeds `containertypes.CreateRequest` with deprecated top-level `MacAddress`, and `createLegacyContainer` posts directly to `/v<version>/containers/create`.

## Control Flow
`TestMACAddrOnRestart` verifies a stopped generated-MAC container receives a non-conflicting MAC when restarted after another container may have reused its original address. `TestCfgdMACAddrOnRestart` ensures a configured MAC survives container and daemon restart. `TestInspectCfgdMAC` compares inspect `Config.MacAddress` for generated, endpoint-configured, custom network, and legacy container-wide paths. `TestWatchtowerCreate` uses API 1.25 to migrate container-wide MAC into endpoint settings when network mode uses network ID but endpoint config is keyed by name. `TestNetworkConnectWithMACAddress` connects a running container to a network with a MAC and verifies inspect plus `/sys/class/net/eth1/address`.

## State And Persistence Behavior
Persistent behavior is central: configured MACs must be stored and restored, generated MACs must be regenerated safely when necessary, and legacy container create data must migrate into endpoint state. Inspect output is treated as API state and validated for backward compatibility.

## Dependencies And Integration Points
Depends on libnetwork bridge and macvlan drivers, API version gates (`1.25`, `1.43`, `1.51`), daemon env `DOCKER_MIN_API_VERSION`, request helper raw API calls, and Linux container interface state.

## Risks
MAC allocation tests can depend on address reuse probabilities, though the scenario is designed to expose the original bug. Legacy API behavior is brittle by design and may require updates when deprecated fields are removed. Macvlan availability and Windows/rootless limitations require skips.

## Test Signals
Signals include inspect `NetworkSettings.Networks[*].MacAddress`, raw inspect `Config.MacAddress`, successful container start/restart, expected IP/MAC on macvlan, and in-container interface address validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/mac_addr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/main_test.go -->
# sources/cloud-native/moby/integration/networking/main_test.go

## Purpose
Defines shared test-suite setup for the `integration/networking` package. It initializes tracing, creates the execution environment, preloads/freeze-checks Linux images, exposes global `testEnv` and `baseContext`, and provides per-test cleanup helpers.

## Important APIs, Types, And Functions
`TestMain` calls `testutil.ConfigureTracing`, creates an OpenTelemetry span, runs `environment.New`, `environment.EnsureFrozenImagesLinux`, prints environment details, runs the package tests, sets span status on failure, and exits. `setupTest` starts a child span, calls `environment.ProtectAll`, and schedules `testEnv.Clean`. `sanitizeCtrName` replaces `/` and `=` with `-` for Docker-safe names.

## Control Flow
Suite initialization happens once before tests. Individual tests call `setupTest` to attach to the shared context and ensure environment cleanup after each test. Fatal environment errors panic after closing tracing.

## State And Persistence Behavior
Maintains package-level `testEnv` and `baseContext`. Per-test cleanup protects and clears daemon/container/network artifacts through the environment helper.

## Dependencies And Integration Points
Integrates all networking tests with Moby's environment abstraction, frozen image setup, OpenTelemetry, and name sanitation used by tests that derive names from `t.Name()`.

## Risks
If image preparation or environment discovery fails, no package tests run. The global context and environment are shared, so cleanup discipline in tests is important to avoid cross-test leakage.

## Test Signals
The file itself has no assertions besides setup failure handling; its signal is whether suite setup completes and whether non-zero test exit is reflected in tracing status.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/nat_windows_test.go -->
# sources/cloud-native/moby/integration/networking/nat_windows_test.go

## Purpose
Windows NAT networking coverage for same-network container communication and cross-network hairpin access to a mapped host port.

## Important APIs, Types, And Functions
Uses `testEnv.APIClient`, `network.CreateNoError` with `network.WithDriver("nat")`, container run/attach helpers, `container.WithPortMap`, `networktypes.PortMap`, `net.Dial` to discover host address, and Windows ping/wget commands.

## Control Flow
`TestNatNetworkICC` covers the default `nat` network and a user-created `nat` network. It starts `ctr1`, runs `ctr2` on the same network, and pings by hostname to validate DNS and communication. `TestFlakyPortMappedHairpinWindows` creates separate NAT networks, runs an HTTP server with an ephemeral host port, then uses a client container on another network to access the server via the host address and mapped port.

## State And Persistence Behavior
State is transient networks and containers. The tests validate endpoint registration, DNS records, and host port mappings, but no restart persistence.

## Dependencies And Integration Points
Depends on Windows NAT driver, Windows ping output, host outbound connectivity to determine a source address, and BusyBox/Windows container command availability depending on the test image.

## Risks
The hairpin test is explicitly marked flaky and linked to issue 48881. Host address discovery depends on network access to `hub.docker.com:80`, and port mapping behavior can vary by Windows networking stack.

## Test Signals
Signals are successful ping output, empty stderr, and `wget` stderr containing `404 Not Found` from the mapped HTTP server.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/nat_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/port_mapping_linux_test.go -->
# sources/cloud-native/moby/integration/networking/port_mapping_linux_test.go

## Purpose
Comprehensive Linux integration coverage for published port behavior, NAT disablement, direct routing, userland proxy, loopback scoping, firewall marks, raw table skipping, rootless loopback address distinction, and host/container/remote access paths.

## Important APIs, Types, And Functions
Uses `networktypes.PortMap`, `PortBinding`, `bridge` driver options (`IPv4GatewayMode`, `IPv6GatewayMode`, `TrustedHostInterfaces`), daemon flags (`--userland-proxy`, `--allow-direct-routing`, `--bridge-accept-fwmark`), synthetic L3 segments from `testutils/networking`, and BusyBox/httpd/nc/curl/wget/ping commands. Helpers include `getIfaceAddrs`, `enableIPv6OnAll`, `retryFlaky`, `sendPayloadFromHost`, and `getContainerStdout`.

## Control Flow
The file starts isolated daemons for most cases, creates bridge networks with IPv4/IPv6/gateway-mode combinations, runs server containers with mapped or exposed ports, then probes from the host, peer containers, or synthetic remote hosts. `TestDisableNAT` checks inspect port metadata for routed gateway modes. Hairpin tests cover TCP and UDP mapped access from other networks. Host access tests exercise loopback, physical interface, IPv4/IPv6, userland proxy on/off, and bridge-nf-call-iptables. Direct-routing tests build L3 segments, add routes, and compare NAT, nat-unprotected, and routed modes for ping and HTTP to mapped/unmapped ports. Attack-oriented tests confirm exposed ports and loopback-published ports are not directly reachable unless trusted interfaces or `--allow-direct-routing` apply.

## State And Persistence Behavior
Tests mutate daemon port allocator state, host sysctls, host interface IPv6 addresses, L3 namespace routes, iptables/nftables state, and container log streams. `TestRestartUserlandProxyUnder2MSL` verifies a port can be reused after a proxy connection enters TIME_WAIT. `TestMixAnyWithSpecificHostAddrs` validates allocator consistency across any-address and specific-address bindings.

## Dependencies And Integration Points
Deeply integrates with Linux networking, iptables/nftables raw and filter chains, firewalld presence, docker-proxy, RootlessKit behavior, L3 namespace utilities, BusyBox tools, golden files for raw rules, and stdcopy log decoding.

## Risks
High flake surface: host sysctl writes, fixed host ports, remote route simulation, TIME_WAIT timing, firewalld rpfilter behavior, network access for host address discovery, and UDP retries. Several tests skip rootless because firewall rules or namespace visibility would not reflect host behavior. Exact golden raw rules are backend- and environment-sensitive.

## Test Signals
Signals include inspect `Ports` equality, HTTP status/body checks, ping/curl exit codes, daemon process behavior, container stdout payload detection, golden iptables raw table snapshots, and assertions about port allocator uniqueness and loopback address routing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/port_mapping_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/resolvconf_test.go -->
# sources/cloud-native/moby/integration/networking/resolvconf_test.go

## Purpose
Tests Docker resolver behavior for localhost upstream resolvers, internal networks, container-local DNS servers, and Windows external DNS lookup. It protects resolver regressions around internal DNS forwarding and generated `/etc/resolv.conf`.

## Important APIs, Types, And Functions
Uses `daemon.WithResolvConf`, `network.GenResolvConf`, `network.StartDaftDNS`, `container.WithDNS`, bind mounts for `dnsd.conf`, and container `nslookup`. Network helpers create bridge networks with `WithInternal`, IPv6, and IPAM.

## Control Flow
`TestResolvConfLocalhostIPv6` starts a daemon whose host resolv.conf points at `127.0.0.53`, creates an IPv6 bridge network, runs a container, and compares generated `/etc/resolv.conf` text with the daemon path normalized. `TestInternalNetworkDNS` starts a loopback DNS server, verifies external DNS works on an external network, remains available after adding an internal network, fails with `SERVFAIL` after external disconnect, and works after reconnect. `TestInternalNetworkLocalDNS` runs a DNS server container on an internal network and queries it via `--dns` through Docker's internal resolver. `TestNslookupWindows` checks Windows external DNS forwarding for `docker.com`.

## State And Persistence Behavior
The tests mutate daemon resolver configuration, network attachments, and container DNS settings. They validate resolver behavior as network membership changes, not persistent daemon restarts.

## Dependencies And Integration Points
Integrates `/etc/resolv.conf` generation, Docker embedded DNS (`127.0.0.11`), host loopback DNS server behavior, internal network isolation, bind mounts, and Windows DNS proxy behavior.

## Risks
Assumes no conflicting DNS server on `127.0.0.1`, skips rootless when host loopback resolver is inaccessible, and uses external `docker.com` lookup on Windows. Exact resolv.conf text can change with resolver generation policy.

## Test Signals
Signals include exact resolv.conf content, `nslookup` exit codes, `SERVFAIL`, configured fake DNS response address, and Windows stdout containing `Addresses:`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/networking/resolvconf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/authz/authz_plugin_test.go -->
# sources/cloud-native/moby/integration/plugin/authz/authz_plugin_test.go

## Purpose
Integration tests for legacy authorization plugin API behavior on non-Windows platforms. The file verifies allow/deny/error paths for request and response authorization hooks, TLS user propagation, event stream behavior, duplicate plugin registration, image load/save/import streaming, container archive copy, and response headers.

## Important APIs, Types, And Functions
Defines `authorizationController`, constants for plugin name/messages/endpoints, `setupTestV1`, `isAllowed`, `socketHTTPClient`, `newTLSAPIClient`, `systemTime`, `systemEventsSince`, image helper functions, and `assertURIRecorded`. It uses `authorization.Response`, Docker client APIs, raw HTTP over daemon socket, TLS client config, `go-archive`, and event stream APIs.

## Control Flow
`setupTestV1` writes `/etc/docker/plugins/authzplugin.spec` pointing at the suite test server and resets global `ctrl`. Tests configure `ctrl.reqRes` and `ctrl.resRes`, start the daemon with `--authorization-plugin`, execute API calls, and assert authorization callbacks and client errors. Allow tests create containers and call `/version`; deny/error tests assert exact daemon error strings and request/response hook counts. Stream and archive tests ensure long-lived or body-heavy APIs pass through authorization without truncation or duplicate registration issues.

## State And Persistence Behavior
State is held in the global `ctrl` request/response controller and plugin spec files under `/etc/docker/plugins`. Temporary image/archive files and containers are created during streaming tests. Cleanup removes plugin specs and stops daemon state through shared setup.

## Dependencies And Integration Points
Depends on the httptest authorization server from `main_test.go`, Docker authorization plugin contract (`/Plugin.Activate`, `/AuthZPlugin.AuthZReq`, `/AuthZPlugin.AuthZRes`), daemon socket HTTP transport, TLS cert fixtures, event APIs, image APIs, archive copy APIs, and Linux-only plugin support.

## Risks
Global mutable `ctrl` requires tests to avoid unsafe parallelism. Exact error message assertions are brittle. Tests that write `/etc/docker/plugins` assume local daemon privileges and can interfere if cleanup fails.

## Test Signals
Signals include request/response callback counts, recorded URI substrings, exact error strings, HTTP 403 status, TLS authenticated user `client`, event stream create/start events, successful image/archive round trips, and JSON content-type preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/authz/authz_plugin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/authz/authz_plugin_v2_test.go -->
# sources/cloud-native/moby/integration/plugin/authz/authz_plugin_v2_test.go

## Purpose
Tests managed v2 authorization plugin behavior: install, enable as daemon authorization plugin, allow non-volume requests, reject volume APIs, disable plugin recovery, and daemon startup failure for bad/nonexistent plugins.

## Important APIs, Types, And Functions
Defines plugin image names and `setupTestV2`, which requires non-Windows, Docker Hub connectivity, and starts a daemon. `pluginInstallGrantAllPermissions` calls `PluginInstall` with `AcceptAllPermissions` and drains the response body to EOF.

## Control Flow
Tests install remote plugins, restart the daemon with `--authorization-plugin=<plugin>`, and execute Docker APIs. Allow test runs a container and inspects it. Reject tests call volume create/list/remove/inspect/prune and assert plugin failure messages. Bad manifest and nonexistent plugin tests expect daemon restart errors, then verify daemon can start without the plugin.

## State And Persistence Behavior
Plugin installation persists in daemon plugin state across daemon restart. Disabling the plugin is tested as a live state transition that restores volume API access.

## Dependencies And Integration Points
Depends on Docker Hub connectivity, amd64 plugin images, plugin install/enable/disable APIs, daemon restart, volume APIs, and the authorization plugin manifest contract.

## Risks
Remote image availability and registry connectivity are major risks. Tests skip non-amd64 and Windows, but still depend on plugin image names remaining valid. Restart failure assertions are coarse and could miss detailed reason changes.

## Test Signals
Signals are successful non-volume container inspect, volume API errors containing the plugin name, successful API call after disable, and expected restart errors for invalid plugin configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/authz/authz_plugin_v2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/authz/main_test.go -->
# sources/cloud-native/moby/integration/plugin/authz/main_test.go

## Purpose
Package-level harness for non-Windows authz plugin integration tests. It initializes tracing/environment, creates per-test daemon instances, and hosts a fake authorization plugin server that implements the Docker plugin activation and authorization request/response endpoints.

## Important APIs, Types, And Functions
`TestMain` configures tracing, initializes `environment.Execution`, ensures frozen Linux images, calls `setupSuite`, runs tests, and tears down the HTTP server. `setupTest` skips remote daemons/Windows, protects the environment, creates an experimental daemon, and schedules daemon/environment cleanup. `setupSuite` creates an `httptest.Server` with handlers for `/Plugin.Activate`, `/AuthZPlugin.AuthZReq`, and `/AuthZPlugin.AuthZRes`. `assertAuthHeaders` and `assertBody` enforce sanitization rules.

## Control Flow
The fake plugin server marshals a manifest implementing `authorization.AuthZApiImplements`. Request and response handlers decode `authorization.Request`, reject leaked auth headers, reject bodies for auth or non-text/non-JSON requests, count `/version` hooks, record URIs, choose configured responses from global `ctrl`, and write JSON `authorization.Response`.

## State And Persistence Behavior
Global state includes `testEnv`, `d`, `server`, `baseContext`, and the `ctrl` object created by individual tests. The server persists for the package run; daemon instances are per test.

## Dependencies And Integration Points
Integrates plugin contract types from `pkg/plugins` and `pkg/authorization`, `otelhttp`, Moby daemon test utilities, and the authz tests' global controller.

## Risks
Panics in HTTP handlers fail tests abruptly. Operator precedence in `assertBody` is significant: JSON content type returns early because of the `|| v == "application/json"` clause. Shared globals make parallel tests unsafe unless isolated.

## Test Signals
Harness signals are indirect: tests fail if plugin activation manifest is wrong, if auth headers/bodies leak to the plugin, or if daemon setup/cleanup fails.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/authz/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/authz/main_windows_test.go -->
# sources/cloud-native/moby/integration/plugin/authz/main_windows_test.go

## Purpose
Windows package stub for `integration/plugin/authz`. It declares `package authz` so the package has a Windows file even though the actual authz plugin tests are non-Windows build-tagged.

## Important APIs, Types, And Functions
No imports, functions, types, or runtime behavior are defined.

## Control Flow
There is no executable control flow.

## State And Persistence Behavior
No state or persistence behavior.

## Dependencies And Integration Points
Its integration point is Go package/build compatibility on Windows when `main_test.go`, `authz_plugin_test.go`, and `authz_plugin_v2_test.go` are excluded by `//go:build !windows`.

## Risks
Low risk. Any Windows-specific authz setup would need to be added here or in another Windows file.

## Test Signals
No direct test signals; successful package loading on Windows is the only signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/authz/main_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/common/main_test.go -->
# sources/cloud-native/moby/integration/plugin/common/main_test.go

## Purpose
Shared test harness for common plugin integration tests. It configures tracing, initializes the test environment, exposes `testEnv` and `baseContext`, and provides `setupTest` for environment protection and cleanup.

## Important APIs, Types, And Functions
`TestMain` calls `testutil.ConfigureTracing`, `environment.New`, `testEnv.Print`, `m.Run`, and records OpenTelemetry span status/exit attribute. `setupTest` starts a per-test span, calls `environment.ProtectAll`, and schedules `testEnv.Clean`.

## Control Flow
Suite setup runs once, then common plugin tests call `setupTest` or use `baseContext` directly. The process exits with the test runner's code.

## State And Persistence Behavior
Package globals hold environment and base context. Per-test cleanup is delegated to the environment helper.

## Dependencies And Integration Points
All common plugin tests depend on this file for environment discovery and cleanup. It integrates with OpenTelemetry and Moby's integration environment utilities.

## Risks
If environment initialization fails, the package panics before any tests run. Tests that bypass `setupTest` must handle cleanup themselves.

## Test Signals
No direct assertions except setup failure handling and non-zero exit marking in tracing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/common/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/common/plugin_test.go -->
# sources/cloud-native/moby/integration/plugin/common/plugin_test.go

## Purpose
Common plugin API integration coverage: invalid JSON handling for plugin endpoints, plugin install from registries with/without auth/digest/insecure registry, plugins with configured runtimes, and backward-compatible Docker schema2 plugin media types.

## Important APIs, Types, And Functions
Uses raw `request.Post`, plugin fixture helpers (`plugin.Create`, `CreateInRegistry`), test registry helpers, `PluginInstall`, `PluginPush`, `PluginRemove`, `PluginInspect`, `PluginEnable`, `jsonmessage.DisplayStream`, containerd/docker resolver, and OCI manifest decoding. It also writes a temporary runtime wrapper script and daemon config JSON.

## Control Flow
`TestPluginInvalidJSON` posts bad content type, invalid JSON, trailing JSON content, and empty bodies to plugin endpoints and validates HTTP errors are 4xx rather than 5xx. `TestPluginInstall` creates plugin images in local registries and installs them through unauthenticated, digest, htpasswd-authenticated, and insecure registry paths. `TestPluginsWithRuntimes` enables a plugin, configures custom runtimes, restarts the daemon with each default runtime, and checks wrapper side-effect files. `TestPluginBackCompatMediaTypes` pushes a plugin, resolves it with a Docker schema2 accept header, and validates manifest/layer media types.

## State And Persistence Behavior
Tests mutate daemon plugin store, local registry content, runtime config files, and temporary filesystem markers. Plugin install/remove and daemon restart persistence are part of the behavior under test.

## Dependencies And Integration Points
Depends on local daemon, registry test server, containerd image media types, Docker resolver, plugin fixture builder, daemon runtime configuration, and non-Windows plugin support.

## Risks
Registry and network binding assumptions can make install tests flaky. The insecure registry test needs a non-loopback interface. Runtime wrapper tests depend on `runc` being in PATH and rootless is skipped due daemon restart setup issues.

## Test Signals
Signals include HTTP status/error body text for JSON validation, successful plugin inspect after install, extracted push digest, wrapper-created `success` files, and manifest media type/layer count equality.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/common/plugin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/close_on_start/main.go -->
# sources/cloud-native/moby/integration/plugin/logging/cmd/close_on_start/main.go

## Purpose
Minimal log driver plugin binary used to simulate a log plugin that closes the log FIFO immediately after `StartLogging`, approximating plugin crash or early close behavior.

## Important APIs, Types, And Functions
Defines `start{File string}` and `main`. `main` listens on Unix socket `/run/docker/plugins/plugin.sock`, registers `/LogDriver.StartLogging`, decodes JSON, opens the provided file read-only, closes it immediately, writes HTTP 200 and `{}`, then serves through `http.Server` with `ReadHeaderTimeout`.

## Control Flow
The process blocks in `server.Serve(l)`. Each StartLogging request opens then closes the log file before responding. Bad JSON returns 400; open failures return 500.

## State And Persistence Behavior
No persistent state. The only side effect is temporarily opening and closing the daemon-provided log file.

## Dependencies And Integration Points
Used by logging integration tests through plugin fixture creation. It implements only enough of the log driver API to test daemon behavior after log sink closure.

## Risks
The plugin intentionally omits other log driver endpoints. If daemon startup begins requiring capabilities or stop endpoints for this path, the fixture would need expansion.

## Test Signals
Signal is indirect through `TestContinueAfterPluginCrash`, which expects containers to continue producing stdout without daemon "broken pipe" log entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/close_on_start/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/discard/driver.go -->
# sources/cloud-native/moby/integration/plugin/logging/cmd/discard/driver.go

## Purpose
Implements a discard log driver plugin fixture. It consumes log data and reports that plugin-side log reading is unsupported, allowing tests to verify Docker's log cache behavior.

## Important APIs, Types, And Functions
Defines request/response structs, `driver` with mutex-protected `logs map[string]io.Closer`, `handle`, and `respond`. Endpoints include `/LogDriver.StartLogging`, `/LogDriver.StopLogging`, and `/LogDriver.Capabilities`.

## Control Flow
`StartLogging` decodes a file path, opens it read-only, stores the closer under lock, starts `io.Copy(io.Discard, f)` in a goroutine, and responds with an error string if any. `StopLogging` closes the stored file. `Capabilities` returns `ReadLogs: false`.

## State And Persistence Behavior
Runtime state is the in-memory map of open log files. No persistent state is written. File descriptors remain open until stop or process exit.

## Dependencies And Integration Points
Used by the logging read tests as a plugin fixture behind `/run/docker/plugins/plugin.sock`. It exercises daemon behavior when plugin read capability is false.

## Risks
If `os.OpenFile` fails, the code still stores `f` only after the call; however it calls `respond(err, w)` without returning before later map assignment in the current control flow, which would risk storing nil if future changes moved code. The fixture is intentionally simple and not production-hardened.

## Test Signals
Indirect signals come from `ContainerLogs` behavior with log cache enabled/disabled when this plugin is selected.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/discard/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/discard/main.go -->
# sources/cloud-native/moby/integration/plugin/logging/cmd/discard/main.go

## Purpose
Entry point for the discard logging plugin fixture. It exposes the handlers from `driver.go` over Docker's expected plugin Unix socket.

## Important APIs, Types, And Functions
`main` listens on `/run/docker/plugins/plugin.sock`, creates an HTTP mux, calls `handle(mux)`, constructs `http.Server` with `ReadHeaderTimeout`, and serves forever.

## Control Flow
Startup either panics on socket listen failure or blocks serving log driver endpoints.

## State And Persistence Behavior
No state beyond the driver state registered by `handle`.

## Dependencies And Integration Points
Depends on Unix sockets and the companion driver implementation. Used by plugin fixture build helpers in logging tests.

## Risks
Linux/Unix-socket specific. No graceful shutdown handling is implemented because test plugin lifecycle is managed by the daemon/plugin fixture.

## Test Signals
Indirectly verified by logging read tests that enable the built plugin and use it as a log driver.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/discard/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/discard/main_test.go -->
# sources/cloud-native/moby/integration/plugin/logging/cmd/discard/main_test.go

## Purpose
Package declaration file for the discard logging plugin command tests/build context.

## Important APIs, Types, And Functions
No imports, tests, functions, or types are defined.

## Control Flow
No executable control flow.

## State And Persistence Behavior
No state.

## Dependencies And Integration Points
Keeps the command package valid in test discovery. Real behavior is in `driver.go` and `main.go`.

## Risks
No direct risk.

## Test Signals
No direct test signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/discard/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/dummy/main.go -->
# sources/cloud-native/moby/integration/plugin/logging/cmd/dummy/main.go

## Purpose
No-op logging plugin fixture used when tests need a plugin process/socket that can be enabled but does not implement meaningful log driver behavior.

## Important APIs, Types, And Functions
`main` listens on `/run/docker/plugins/plugin.sock` and serves an empty HTTP mux with `ReadHeaderTimeout`.

## Control Flow
The process panics if the Unix socket cannot be opened; otherwise it serves indefinitely without registered handlers.

## State And Persistence Behavior
No internal or persistent state.

## Dependencies And Integration Points
Built by logging helper `ensurePlugin` and packaged by plugin fixture creation with logdriver capability metadata supplied outside the binary.

## Risks
Because it has no handlers, it only suits daemon paths that do not call log driver endpoints during the specific test phase. If daemon validation becomes stricter, tests may need a richer dummy.

## Test Signals
Indirectly used by `TestDaemonStartWithLogOpt`, which verifies daemon startup with the plugin configured as default log driver.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/cmd/dummy/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/helpers_test.go -->
# sources/cloud-native/moby/integration/plugin/logging/helpers_test.go

## Purpose
Shared helper utilities for logging plugin integration tests. It builds local plugin binaries, creates plugin fixtures, sets socket paths, and marks plugin configs as Docker log drivers.

## Important APIs, Types, And Functions
`pluginBuildLock` serializes builds by plugin name. `ensurePlugin` checks `$GOPATH/bin/<name>`, builds `./cmd/<name>` with `CGO_ENABLED=0` and `GO111MODULE=off` if missing, and returns the binary path. `withSockPath` mutates `plugin.Config.Interface.Socket`. `createPlugin` combines binary/socket options and calls fixture `plugin.Create`. `asLogDriver` sets capability `{Prefix:"docker", Capability:"logdriver", Version:"1.0"}`.

## Control Flow
Tests call `createPlugin`, which builds once per binary and creates a plugin fixture under the requested alias. The build lock prevents concurrent subtests from racing on the same output path.

## State And Persistence Behavior
Built binaries persist under `$GOPATH/bin`. Plugin fixture state is created in the daemon through `plugin.Create`.

## Dependencies And Integration Points
Depends on the Go toolchain, GOPATH, local command sources under `cmd/`, Moby plugin fixture helpers, and logdriver capability metadata.

## Risks
Builds use `GO111MODULE=off`, so command packages must be compatible with GOPATH mode. Missing GOPATH or write permissions can fail tests. Shared binary paths require the lock to avoid races.

## Test Signals
Failures surface as build errors, fixture creation errors, or later plugin enable failures in caller tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/logging_linux_test.go -->
# sources/cloud-native/moby/integration/plugin/logging/logging_linux_test.go

## Purpose
Linux logging plugin regression test ensuring a container continues producing output and the daemon does not log broken-pipe errors when a log plugin closes its file immediately.

## Important APIs, Types, And Functions
Uses `daemon.New`, daemon flags disabling iptables/ip6tables plus `--init`, logging `createPlugin` with `close_on_start`, `PluginEnable`, `container.Run` with `WithLogDriver("test")`, `ContainerAttach`, and direct daemon log file scanning.

## Control Flow
The test starts a daemon, creates/enables the close-on-start log plugin, runs a container that emits `hello` repeatedly, attaches to stdout, reads five lines asynchronously with a timeout, then scans the daemon log file and asserts no line contains `broken pipe`.

## State And Persistence Behavior
Temporary plugin and container state are created and removed. The daemon log file is read as observational state.

## Dependencies And Integration Points
Depends on local daemon, plugin fixture binary, container attach stream, daemon logging, and Linux-only plugin support.

## Risks
The daemon log scan is acknowledged as hacky and could miss differently worded failures or fail on unrelated log text. Timing depends on container output and attach stream readiness.

## Test Signals
Signals are successful plugin enable, receipt of five stdout lines within 60 seconds, and absence of `broken pipe` in daemon logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/logging_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/main_test.go -->
# sources/cloud-native/moby/integration/plugin/logging/main_test.go

## Purpose
Package harness for logging plugin integration tests. It initializes tracing, environment, frozen Linux images, and package globals.

## Important APIs, Types, And Functions
`TestMain` calls `testutil.ConfigureTracing`, `environment.New`, `environment.EnsureFrozenImagesLinux`, prints the environment, runs tests, marks span status for non-zero exit, and exits.

## Control Flow
Suite initialization happens once before tests. Tests use `baseContext` and `testEnv` directly or through helpers.

## State And Persistence Behavior
Maintains global `testEnv` and `baseContext`; no per-test helper is defined here.

## Dependencies And Integration Points
Integrates logging plugin tests with Moby's environment and tracing utilities.

## Risks
Failure to load frozen images prevents the package from running. Tests must manage their own environment cleanup because this file does not provide a `setupTest` wrapper.

## Test Signals
No direct behavioral assertions; setup failures and non-zero package exit are reflected in tracing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/read_test.go -->
# sources/cloud-native/moby/integration/plugin/logging/read_test.go

## Purpose
Tests container log reads when the selected logging plugin declares `ReadLogs: false`, verifying Docker's local log cache behavior and the `cache-disabled` log option.

## Important APIs, Types, And Functions
Uses the discard plugin, `PluginEnable`, daemon restart with optional `--log-opt=cache-disabled=...`, `ContainerCreate`, `ContainerStart`, `ContainerLogs`, `stdcopy.StdCopy`, and polling for container stop.

## Control Flow
The test builds/enables the discard log plugin, stops the daemon, then runs subtests for default cache, disabled cache, and explicitly enabled cache. Each subtest restarts daemon with options, creates an echo container using log driver `test`, waits for stop, then calls `ContainerLogs`. If caching is disabled, an error is expected; otherwise stdout must decode to `hello world`.

## State And Persistence Behavior
Plugin installation persists across daemon restarts. Container log availability depends on daemon log cache state, not plugin read support.

## Dependencies And Integration Points
Depends on non-Windows Unix socket plugins, daemon log cache implementation, plugin capability endpoint, stdcopy log framing, and container stop polling.

## Risks
Timeouts can occur if log stream EOF is delayed. The test reuses one API client across daemon restarts, so client/daemon reconnection behavior is part of the integration surface.

## Test Signals
Signals are expected `ContainerLogs` error when cache is disabled and decoded stdout exactly `hello world` when cache is available.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/validation_test.go -->
# sources/cloud-native/moby/integration/plugin/logging/validation_test.go

## Purpose
Regression test that a daemon can start with a plugin log driver configured as the default logger and with log options.

## Important APIs, Types, And Functions
Uses local daemon, logging `createPlugin`, dummy plugin binary, `PluginEnable`, plugin removal, and daemon restart with `--log-driver=test --log-opt=foo=bar`.

## Control Flow
The test starts a daemon, creates and enables a dummy logdriver plugin, stops the daemon, then starts it again with the plugin as default log driver and one log option. Successful daemon start is the assertion.

## State And Persistence Behavior
Plugin installation and enablement persist across daemon restart, allowing the default log driver configuration to resolve.

## Dependencies And Integration Points
Depends on local non-Windows daemon, plugin fixture support, and daemon log driver validation during startup.

## Risks
The dummy plugin has no handlers, so this only validates startup/config parsing, not logging operations. Root/daemon locality is required.

## Test Signals
Signal is absence of errors from plugin enable and daemon restart with log driver options.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/logging/validation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/pkg_test.go -->
# sources/cloud-native/moby/integration/plugin/pkg_test.go

## Purpose
Top-level package declaration for `integration/plugin` tests.

## Important APIs, Types, And Functions
No imports, functions, types, or tests.

## Control Flow
No executable control flow.

## State And Persistence Behavior
No state.

## Dependencies And Integration Points
Maintains Go package identity for the directory. Subpackages contain the substantive plugin tests.

## Risks
No direct runtime risk.

## Test Signals
No direct test signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/pkg_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/volumes/cmd/dummy/main.go -->
# sources/cloud-native/moby/integration/plugin/volumes/cmd/dummy/main.go

## Purpose
No-op volume plugin binary fixture. It provides a Docker plugin Unix socket process for tests that need to enable a volume-driver plugin with specific mount configuration.

## Important APIs, Types, And Functions
`main` listens on `/run/docker/plugins/plugin.sock`, creates an empty HTTP mux, sets `ReadHeaderTimeout`, and serves indefinitely.

## Control Flow
The program panics on listen failure; otherwise it blocks in `server.Serve`.

## State And Persistence Behavior
No internal or persistent state.

## Dependencies And Integration Points
Built by volume helper `ensurePlugin` and wrapped by fixture metadata that declares volume-driver capability.

## Risks
Because it implements no volume-driver endpoints, it is only suitable for tests that validate plugin enable/configuration rather than volume operations.

## Test Signals
Indirectly verified by `TestPluginWithDevMounts`, which expects the daemon to enable the plugin successfully.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/volumes/cmd/dummy/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/volumes/helpers_test.go -->
# sources/cloud-native/moby/integration/plugin/volumes/helpers_test.go

## Purpose
Shared helper utilities for volume plugin integration tests. It builds local plugin binaries, creates plugin fixtures with a socket path, and marks plugin configs as Docker volume drivers.

## Important APIs, Types, And Functions
`pluginBuildLock` serializes per-binary builds. `ensurePlugin` resolves GOPATH (default `/go`), builds `./cmd/<name>` to `$GOPATH/bin/<name>` with static/GOPATH-mode settings, and returns the binary. `createPlugin` applies socket and binary options, wraps creation in a 60-second timeout, and calls fixture `plugin.Create`. `asVolumeDriver` sets capability `{Prefix:"docker", Capability:"volumedriver", Version:"1.0"}`.

## Control Flow
Tests request a plugin alias and binary; the helper builds if needed and creates a daemon plugin fixture. Timeout limits plugin fixture creation.

## State And Persistence Behavior
Built binaries persist under GOPATH. Created plugin fixtures persist in daemon state until removed by caller cleanup.

## Dependencies And Integration Points
Depends on the Go toolchain, GOPATH or `/go`, plugin fixture helpers, and Docker plugin capability metadata.

## Risks
Build environment issues can fail tests. GOPATH-mode build must remain compatible with the command sources. Shared binary output requires lock discipline.

## Test Signals
Failures surface as build errors or plugin fixture creation errors before caller tests proceed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/volumes/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/volumes/main_test.go -->
# sources/cloud-native/moby/integration/plugin/volumes/main_test.go

## Purpose
Package harness for volume plugin integration tests. It configures tracing, initializes environment, ensures frozen Linux images, and exposes shared globals.

## Important APIs, Types, And Functions
`TestMain` uses `testutil.ConfigureTracing`, `environment.New`, `environment.EnsureFrozenImagesLinux`, OpenTelemetry spans, `testEnv.Print`, `m.Run`, and process exit.

## Control Flow
Suite setup runs once, then tests execute with global `baseContext` and `testEnv`.

## State And Persistence Behavior
Maintains package-level environment and base context. No per-test setup helper is provided here.

## Dependencies And Integration Points
All volume plugin tests depend on this file for environment discovery, tracing, and frozen image availability.

## Risks
Environment or image setup failure aborts the package. Tests need to manage daemon cleanup explicitly.

## Test Signals
No direct assertions beyond setup failure handling and non-zero exit tracing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/volumes/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/volumes/mounts_test.go -->
# sources/cloud-native/moby/integration/plugin/volumes/mounts_test.go

## Purpose
Regression test for plugin mount ordering involving `/dev` mounts and other bind mounts. It verifies a plugin with host/dev binds and propagated mount settings can be enabled.

## Important APIs, Types, And Functions
Uses local daemon with iptables disabled, volume `createPlugin`, dummy binary, `asVolumeDriver`, plugin config mutation for `Mounts`, `PropagatedMount`, host networking, and `IpcHost`, then `PluginEnable`, `PluginInspect`, and `PluginRemove`.

## Control Flow
The test creates a temporary directory, creates a plugin with bind mounts for `/` to `/host`, `/dev` to `/dev`, and temp dir to `/etc/foo`, sets propagated mount and host namespace options, enables the plugin, inspects it, and asserts it is enabled.

## State And Persistence Behavior
State includes daemon plugin config, bind mount metadata, and a temporary directory. The plugin is removed in cleanup.

## Dependencies And Integration Points
Depends on local non-rootless Linux daemon, plugin fixture mounting behavior, volume driver capability metadata, and mount ordering inside daemon plugin setup.

## Risks
Requires privileges for host mounts and is skipped for rootless/Windows/remote daemons. It validates enablement rather than volume operations, so it targets a narrow regression.

## Test Signals
Signals are successful plugin creation/enabling and `PluginInspect` reporting `Enabled`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/plugin/volumes/mounts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/secret/main_test.go -->
# sources/cloud-native/moby/integration/secret/main_test.go

## Purpose
Package harness for secret integration tests. It configures tracing, initializes the execution environment, ensures frozen Linux images, and provides `setupTest` for environment protection/cleanup.

## Important APIs, Types, And Functions
`TestMain` calls tracing setup, `environment.New`, `environment.EnsureFrozenImagesLinux`, environment printing, `m.Run`, span status on non-zero exit, shutdown, and `os.Exit`. `setupTest` starts a span, protects the environment, and schedules cleanup.

## Control Flow
Suite setup runs once, while each secret test calls `setupTest` before creating a swarm or client.

## State And Persistence Behavior
Global `testEnv` and `baseContext` are package state. Cleanup clears environment resources after each test.

## Dependencies And Integration Points
Integrates secret tests with Moby environment utilities, frozen image management, and OpenTelemetry.

## Risks
Environment/image setup failure aborts all secret tests. Cleanup correctness is important because swarm tests create daemon and cluster state.

## Test Signals
No direct functional assertions; setup errors and non-zero exit are reflected in tracing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/secret/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/secret/secret_test.go -->
# sources/cloud-native/moby/integration/secret/secret_test.go

## Purpose
Integration coverage for Docker Swarm secret APIs and templated secrets. It tests inspect/list/filter/create/delete/update semantics, immutable data constraints, template rendering with referenced secrets/configs, tmpfs mount behavior, and name/ID resolution edge cases.

## Important APIs, Types, And Functions
Uses `swarm.NewSwarm`, `client.SecretCreate`, `SecretInspect`, `SecretList`, `SecretRemove`, `SecretUpdate`, `ConfigCreate`, service helpers from `integration/internal/swarm`, `stdcopy.StdCopy`, and containerd errdefs predicates. Helpers `createSecret` and `namesFromList` centralize secret creation and sorted name extraction.

## Control Flow
Each test creates a swarm-backed daemon and client. `TestSecretInspect` creates and inspects a secret and compares raw JSON unmarshalling. `TestSecretList` verifies empty list, creates labeled secrets, then applies name/id/label filters. `TestSecretsCreateAndDelete` checks duplicate conflict, removal, not-found errors, and labels. `TestSecretsUpdate` updates labels by full ID, full name, and ID prefix, then asserts data updates are rejected. `TestTemplatedSecret` creates referenced secret/config plus a templated secret using `golang` templating, creates a service mounting all references, waits for a running task, execs `cat` and `mount`, and checks rendered content plus tmpfs mount. `TestSecretCreateResolve` ensures removal resolves full ID before a secret whose name equals that ID, and does not resolve partial names as IDs.

## State And Persistence Behavior
Secret and config objects persist in swarm state during each test. Update behavior is constrained to labels; secret data is intentionally immutable. Service task mounts expose rendered secret content as tmpfs under `/run/secrets`.

## Dependencies And Integration Points
Depends on Swarm mode, secret/config API types, service scheduling, task exec, stdcopy stream decoding, errdefs classification, Linux tmpfs mounts, and polling for running tasks.

## Risks
Swarm scheduling and task startup introduce timing risk. Template rendering depends on referenced target names matching. The prefix-resolution test is subtle because it distinguishes full name, full ID, and partial ID rules.

## Test Signals
Signals include exact errdefs conflict/not-found/invalid-argument checks, sorted list equality, label value checks, rendered secret content equality, empty stderr, mount output containing tmpfs, and final list counts after resolution operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/secret/secret_test.go -->
