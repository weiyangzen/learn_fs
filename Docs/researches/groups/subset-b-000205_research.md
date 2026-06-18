# Research: subset-b-000205

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/termtest/stripansi.go -->
# sources/cloud-native/moby/integration/internal/termtest/stripansi.go

Purpose: provides a test helper that parses ANSI terminal output and returns the final visible one-dimensional character stream. It is aimed at integration tests that compare output passing through a Windows pseudoterminal with output redirected to a file.

Important APIs/types/functions: `StripANSICommands` builds an `Azure/go-ansiterm` parser with a package-local `stringHandler`, parses the input bytes, and returns the rendered string plus parser error. `stringHandler` embeds `ansiterm.AnsiEventHandler`, tracks a byte buffer and cursor, and implements `Print`, `Execute`, `ED`, `CUP`, `DECTCEM`, `SGR`, `DA`, `Flush`, and `String`.

Control flow: printable bytes append or overwrite at `cursor`; backspace moves the cursor left and trims a trailing space in one narrow case; carriage return and newline are treated as printed bytes. `ED` implements erase-display modes by blanking before the cursor, replacing the current buffer with spaces, or truncating after the cursor. `CUP` rejects multi-row cursor movement (`x > 1`) and otherwise maps ANSI column `y` onto the linear cursor.

State/persistence: state is transient per call: a byte slice and cursor. There is no filesystem or daemon state, but the lossy rendering intentionally persists overwrite/erase effects in the returned string.

Dependencies/integration: depends on `github.com/Azure/go-ansiterm`. The helper is internal to integration tests and supplies a lightweight alternative to a full terminal screen model.

Risks: the model is one-dimensional and byte-oriented, so multi-line cursor movement, wide runes, combining characters, and unsupported ANSI sequences can produce wrong output or parser errors. `CUP` has a suspicious padding loop (`len(h.b) - y`) that does not append when `y` is beyond the buffer, and default `ED` truncates to `cursor+1`, so edge cases around cursor bounds deserve care.

Test signals: `stripansi_test.go` covers realistic PTY escape streams with clear-screen, cursor visibility, graphics rendition, title-setting, cursor-home, cursor-column movement, and backspace behavior. Additional signals should include explicit unsupported cursor-row errors and erase/truncate boundary cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/termtest/stripansi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/termtest/stripansi_test.go -->
# sources/cloud-native/moby/integration/internal/termtest/stripansi_test.go

Purpose: regression tests for `StripANSICommands`, using Windows-shell-like ANSI streams that include screen erases, cursor motion, title updates, cursor visibility toggles, SGR, and backspace.

Important APIs/types/functions: `TestStripANSICommands` is table-driven over `input` and `want`, calls `StripANSICommands`, asserts no parse error, and compares the rendered output with `gotest.tools/v3/assert.DeepEqual`.

Control flow: each case runs as a subtest. The first input rewrites the beginning of the line and uses backspace before appending more text; the second omits one NUL-delimited title-sequence variant. Both are expected to collapse to `this is fineaccidents happen`.

State/persistence: no persistent state. Each subtest exercises a fresh parser/handler instance.

Dependencies/integration: imports only Go `testing` and `gotest.tools/v3/assert`, and validates the helper used by terminal-related integration tests.

Risks: coverage is intentionally narrow and does not test parser errors, multi-row cursor movement rejection, erase modes independently, Unicode, or malformed escape sequences. Empty subtest names make failures less descriptive than named cases.

Test signals: successful tests signal that the helper handles the concrete PTY escape streams currently produced by targeted integration scenarios. Broader terminal semantics remain unverified.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/termtest/stripansi_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/testutils/networking/firewall.go -->
# sources/cloud-native/moby/integration/internal/testutils/networking/firewall.go

Purpose: supplies firewall helpers for Moby integration tests that need to modify or observe host firewall state around daemon networking behavior.

Important APIs/types/functions: `SetFilterForwardPolicies` reads and temporarily changes `iptables` and `ip6tables` `FORWARD` chain policies. `FirewalldRunning` probes `firewall-cmd --state`. `FirewalldReload` triggers a firewalld reload and polls a daemon-reported reload timestamp until it changes.

Control flow: `SetFilterForwardPolicies` extracts the current policy with `rePolicy`, skips commands already at the desired policy, changes others with `-P FORWARD`, and registers `t.Cleanup` to restore originals. `FirewalldReload` exits early if firewalld is not running, captures `d.FirewallReloadedAt`, runs `firewall-cmd --reload`, then polls until the daemon reports a new non-empty reload time.

State/persistence: directly mutates host IPv4/IPv6 filter policies and relies on cleanup to restore them. `FirewalldReload` mutates firewalld runtime state and observes daemon state through the test daemon helper.

Dependencies/integration: uses `os/exec`, `icmd`, `poll`, gotest assertions, and `internal/testutil/daemon`. Bridge tests use these helpers to create controlled FORWARD-policy and firewalld reload scenarios.

Risks: requires privileged firewall tools and assumes English iptables output containing `policy WORD`. Cleanup logs but does not fail if restoration fails, so later tests can inherit bad firewall policy. Firewalld reload behavior is asynchronous and can be flaky if daemon reload tracking is delayed.

Test signals: consumers verify policies are set/restored, firewalld reloads complete, and deleted-network firewall rules do not return after reload. There are no direct unit tests for regex parsing or restore failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/testutils/networking/firewall.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/testutils/networking/l3_segment_linux.go -->
# sources/cloud-native/moby/integration/internal/testutils/networking/l3_segment_linux.go

Purpose: creates disposable Linux layer-3 network segments for integration tests, with isolated network namespaces, a bridge, veth peers, and helpers to run commands inside namespace context.

Important APIs/types/functions: `CurrentNetns` names the current namespace sentinel. `L3Segment` owns a bridge `Host` and a map of named `Host`s. `NewL3Segment` creates a bridge namespace/link with addresses. `AddHost` creates a host namespace and veth pair attached to the bridge. `Destroy` tears down hosts and bridge. `Host.Run`, `MustRun`, `Do`, and `Destroy` execute commands, enter namespaces with `netns.Set`, and clean up links/namespaces.

Control flow: `newHost` creates the namespace unless `nsName == CurrentNetns`; `Host.Run` wraps commands in `ip netns exec` when needed. `Host.Do` locks the OS thread, switches into the target namespace, runs a callback, and defers restoration of the original namespace. `AddHost` validates interface-name length, creates a veth pair, enslaves the bridge side, brings interfaces and loopback up, enables IPv4/IPv6 forwarding, and assigns requested addresses.

State/persistence: mutates host network namespace state, veth links, bridge links, sysctls, and named netns objects. Cleanup explicitly deletes veth links before namespaces to avoid delayed kernel peer cleanup causing `EEXIST` in later tests.

Dependencies/integration: depends on Linux `ip` and `sysctl`, `github.com/vishvananda/netns`, `runtime.LockOSThread`, and `syscall.IFNAMSIZ`. Bridge and firewall documentation tests use it to run Docker daemons and firewall commands in isolated namespaces.

Risks: privileged Linux-only helper; failures can leak namespaces or leave sysctl/firewall state until cleanup. Namespace switching must stay thread-locked or unrelated goroutines can observe wrong network context. `Destroy` is fatal on cleanup command failures, which may obscure original test failures.

Test signals: indirect coverage comes from bridge FORWARD-policy, backend-switch, and iptables/nftables documentation tests that depend on isolated daemons and firewall state. There is no direct unit coverage for namespace switching or partial cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/testutils/networking/l3_segment_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/bridge_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/bridge_linux_test.go

Purpose: Linux bridge-driver integration suite covering network creation semantics, IPAM, gateway modes, firewall policy/backend behavior, port mappings, legacy links, live daemon restarts, API compatibility, and rollback after failed joins.

Important APIs/types/functions: tests use the Moby API client, `integration/internal/network` creation options, `integration/internal/container` helpers, `daemon.Daemon`, bridge driver labels/options, `netlink`/`nlwrap`, and `networking` firewall/L3 helpers. Key tests include `TestCreateWithMultiNetworks`, IPv6 ULA/default-option tests, `TestFilterForwardPolicy`, `TestPointToPoint`, `TestIsolated`, custom-ifname, port-binding, firewalld, legacy-link, backend-switch, IPAM status, join-error, and preferred-subnet-restore scenarios.

Control flow: most tests start from `setupTest`, create or restart daemons with specific flags, create bridge networks with driver/IPAM/options, run containers, inspect network/container state, and assert routes, addresses, port maps, firewall rules, or daemon startup outcomes. Firewall tests build isolated `L3Segment` namespaces, start daemons inside them with OTLP disabled, mutate sysctls/policies, and compare expected iptables/ip6tables/nftables cleanup. Port-binding tests create containers under old/new API versions and, for old-container compatibility, stop the daemon, tamper on-disk container config, restart, and inspect backfilled bindings.

State/persistence: heavily exercises persisted network configuration across daemon restart (`PreferredSubnetRestore`, port mapping restore, live restore), container config backfilling, bridge IPAM counters, host firewall rules/chains/tables, sysctls, netlink bridge devices, and firewalld reload state. Cleanup removes networks/containers and sometimes starts a fresh daemon to clear docker0 rules.

Dependencies/integration: integrates Docker API types, libnetwork bridge labels, daemon test harness, netlink, host `iptables`, `ip6tables`, `nft`, `firewall-cmd`, `ip`, and BusyBox images. API-version gates guard features such as multi-network create and gateway priority/status fields.

Risks: tests require privileged Linux networking and are sensitive to rootless, firewalld, firewall backend, IPVS, and kernel behavior. Hard-coded subnets, ports like `8000`, and bridge names can collide if cleanup fails. Several tests intentionally manipulate global firewall state; failed cleanup can poison later tests. The suite also encodes API compatibility details such as port-binding backfill warnings, so version changes must update assertions carefully.

Test signals: asserts include network inspect IPAM config/status, route table contents, firewall rule existence/removal, daemon startup failure/success, service/container reachability, port map shape, custom interface names, and exact rollback after join error. Skips and TODOs document known gaps, including API 1.53 port-binding behavior and a firewalld/IPv6 isolated XFAIL.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/bridge_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/iptablesdoc/iptablesdoc_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/iptablesdoc/iptablesdoc_linux_test.go

Purpose: generates and verifies Markdown documentation for bridge-driver iptables rules across selected daemon/network/container/swarm configurations.

Important APIs/types/functions: data structs `ctrDesc`, `networkDesc`, and `section` describe documentation scenarios; `index` lists scenarios such as new daemon, port mapping with/without userland proxy, ICC disabled, internal networks, routed/nat-unprotected gateway modes, swarm ingress, and loopback-published ports. `TestBridgeIptablesDoc`, `runTestNet`, `createBridgeNetworks`, `createServices`, `pollService`, `runIptables`, and `generate` orchestrate the test.

Control flow: the test skips under firewalld, rootless, or nftables backend. It creates an `L3Segment`, then one host namespace per section. For each section it starts a daemon in that namespace, optionally initializes swarm or creates bridge networks/containers, zeroes iptables counters, captures several `iptables` views, normalizes packet/byte counters, renders a template from `templates/<section>`, writes the generated Markdown under the bundle directory, and compares with `generated/<section>`.

State/persistence: creates temporary namespaces, daemons, networks, containers, services, firewall rules, generated bundle files, and golden-doc comparisons. No repository files are updated unless the test is run with gotest golden update flags.

Dependencies/integration: depends on `networking.L3Segment`, `daemon.Daemon`, `netlink.GenlFamilyGet("IPVS")`, swarm APIs, bridge driver options, text templates, gotest `golden`, and host `iptables`. It documents libnetwork's iptables backend by observing real rules rather than mocking them.

Risks: highly environment-sensitive: requires privileged iptables backend, no firewalld, working IPVS for swarm sections, and stable rule ordering/output. Template/golden drift must be reviewed carefully because expected rule changes can be functional regressions or legitimate backend changes. Counter normalization handles only one class of CI noise.

Test signals: failures provide generated docs in the bundle path and diffs against `generated/`. Passing tests signal that the iptables rules emitted by bridge networking still match the documented rule set for all configured scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/iptablesdoc/iptablesdoc_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/iptablesdoc/main_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/iptablesdoc/main_linux_test.go

Purpose: package-level test harness for the iptables documentation integration package.

Important APIs/types/functions: declares package globals `testEnv` and `baseContext`, `TestMain`, and `setupTest`. `TestMain` configures tracing, initializes `environment.Execution`, ensures frozen Linux images, prints environment info, records non-zero test exit status on the span, shuts tracing down, and exits with `m.Run()`'s code. `setupTest` starts a child span, protects all environment resources, and schedules environment cleanup.

Control flow: all tests in the package share the initialized execution environment. Errors during environment creation or image setup panic after marking the tracing span.

State/persistence: owns process-wide test environment state and base tracing context. Cleanup is per-test through `environment.ProtectAll` and `testEnv.Clean`.

Dependencies/integration: integrates `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry. The documentation test depends on this for daemon API access and image availability.

Risks: harness failures abort the package before any documentation test runs. It calls `EnsureFrozenImagesLinux`, so Windows or image-preload changes can alter package startup behavior.

Test signals: successful package startup means the environment can create daemons with frozen BusyBox images and has tracing configured for per-test spans.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/iptablesdoc/main_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/main_test.go -->
# sources/cloud-native/moby/integration/network/bridge/main_test.go

Purpose: shared test harness for the Linux bridge integration package.

Important APIs/types/functions: exports package-level `testEnv`, `baseContext`, `TestMain`, and `setupTest`. It configures tracing, initializes environment metadata/client access, preloads frozen Linux images, prints environment details, and wraps tests with resource protection/cleanup.

Control flow: `TestMain` establishes `baseContext`, handles initialization errors by marking the root span and panicking, then runs the package tests. `setupTest` starts a span from `baseContext`, calls `environment.ProtectAll`, and schedules `testEnv.Clean`.

State/persistence: package-global environment and tracing context. Per-test cleanup resets Docker resources managed by the environment helper.

Dependencies/integration: depends on `testutil`, `environment`, and OpenTelemetry. All bridge tests use it to acquire an API client, daemon feature flags, firewall backend, rootless status, and cleanup behavior.

Risks: image setup is Linux-specific; a failure in global setup prevents all bridge tests from running. Tests that manually start daemons or mutate host state still need their own cleanup beyond environment cleanup.

Test signals: harness success indicates the bridge suite can rely on a configured daemon environment and frozen images.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/netinit_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/netinit_linux_test.go

Purpose: regression tests for bridge network initialization failure paths, ensuring daemon recovery and cleanup when bridge setup fails.

Important APIs/types/functions: `TestNetworkInitErrorDocker0`, `TestNetworkInitErrorUserDefined`, and `TestNetworkCreateErrorNoBridge` use `daemon.Daemon`, `DOCKER_TEST_BRIDGE_INIT_ERROR`, bridge driver option `BridgeName`, `network.CreateNoError/Create`, `nlwrap.LinkByName`, and `netlink.LinkNotFoundError`.

Control flow: the default-bridge test starts a daemon, injects an init error for `docker0`, expects restart failure, clears the injection, and starts successfully. The user-defined test creates a named bridge network, restarts with injected failure, removes the failed network, clears injection, restarts, and recreates it. The create-error test injects failure before daemon start, attempts network creation, checks the error, and verifies no bridge link remains.

State/persistence: exercises daemon restart state, persisted user-defined network metadata, bridge link creation/deletion, and test-only environment variable fault injection.

Dependencies/integration: Linux-only bridge driver, daemon test harness, netlink wrappers, and internal network helpers.

Risks: relies on a test-only environment variable recognized by the daemon; if fault-injection semantics change, tests can give false failures. Cleanup must handle daemon processes that may have exited during startup.

Test signals: passing tests show bridge init errors do not permanently wedge default or user-defined network restore, and failed creates do not leak bridge devices.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/netinit_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/nftablesdoc/main_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/nftablesdoc/main_linux_test.go

Purpose: package-level test harness for bridge nftables documentation generation.

Important APIs/types/functions: defines `testEnv`, `baseContext`, `TestMain`, and `setupTest`, matching the iptables documentation harness. It configures tracing, creates the test environment, ensures frozen Linux images, prints environment details, and wraps individual tests in cleanup.

Control flow: initialization failures mark the root span and panic; otherwise `m.Run()` decides the exit code. `setupTest` starts a span and protects/cleans environment resources.

State/persistence: holds process-global test environment and tracing context. Per-test cleanup is scheduled through the environment helper.

Dependencies/integration: OpenTelemetry, Moby `testutil`, and `environment`. The nftables documentation test uses `testEnv` to detect rootless/firewall backend state.

Risks: Linux image availability and environment initialization are package-wide prerequisites. Because this package documents nftables output, an incorrectly detected firewall backend can skip or run the wrong test.

Test signals: package startup success provides a daemon-capable environment with frozen images for nftables rule generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/nftablesdoc/main_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/nftablesdoc/nftablesdoc_linux_test.go -->
# sources/cloud-native/moby/integration/network/bridge/nftablesdoc/nftablesdoc_linux_test.go

Purpose: generates and verifies Markdown documentation for the bridge driver's nftables backend using live daemon/network/container scenarios.

Important APIs/types/functions: shares scenario descriptors with the iptables documentation test: `ctrDesc`, `networkDesc`, `section`, `index`, `TestBridgeNftablesDoc`, `runTestNet`, `createBridgeNetworks`, `createServices`, `runNftables`, `lines`, and `generate`. `runNftables` captures `nft -s list table ip docker-bridges`, normalizes the output priority wording, and breaks the table into template-addressable blocks.

Control flow: the test skips when firewalld is running, rootless mode is active, or the daemon is not using nftables. It creates isolated L3 host namespaces, starts a daemon per scenario, creates configured bridge networks and containers, captures nftables state, renders a Markdown template, writes a bundle artifact, and golden-compares with `generated/`. Swarm support is present in struct fields but commented out in the nftables scenario/index and service helper.

State/persistence: creates temporary netns/daemons/networks/containers and writes generated docs to the test bundle directory. Repository golden files are read for comparison and updated only under external golden update mode.

Dependencies/integration: depends on Linux nftables, bridge driver options, `networking.L3Segment`, daemon helper, templates, gotest `golden`, and `iter.Seq` for line iteration.

Risks: requires stable nftables output format and rule ordering. The parser uses string keys derived from block headers, so template keys can break if nft syntax changes. Swarm sections are disabled/commented, leaving ingress nftables documentation less covered than iptables.

Test signals: passing tests mean observed nftables bridge rules match the documented generated Markdown for new daemon, port publishing, ICC, internal, routed, nat-unprotected, and loopback host-port scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/bridge/nftablesdoc/nftablesdoc_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/delete_test.go -->
# sources/cloud-native/moby/integration/network/delete_test.go

Purpose: verifies Docker network create/delete behavior and ambiguity resolution when network names resemble network IDs.

Important APIs/types/functions: `containsNetwork` scans `networktypes.Summary` items by ID. `createAmbiguousNetworks` creates three networks: a normal network, one named with the first network's ID prefix, and one named with the full first network ID. Tests are `TestNetworkCreateDelete` and `TestDockerNetworkDeletePreferID`.

Control flow: create/delete test creates a named network, asserts it appears, removes it by name, and asserts absence. Ambiguity test creates the three networks, removes by the first network's 12-character ID prefix, then removes by full ID, and verifies the full-ID-named network remains while the ID-targeted networks are gone.

State/persistence: creates Docker networks in the daemon and removes them through the API. No file state.

Dependencies/integration: uses package `setupTest`, API client, internal network helpers, gotest assertions, and OS skips for Linux/Windows differences.

Risks: ambiguous name/ID behavior is subtle; changing API lookup precedence can break compatibility. The Windows skip documents shared-network limitations in that environment.

Test signals: passing tests confirm basic network lifecycle and that ID/prefix deletion preference is preserved over same-looking names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/delete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/dns_test.go -->
# sources/cloud-native/moby/integration/network/dns_test.go

Purpose: tests daemon DNS behavior for fallback resolvers, avoiding recursive use of Docker's internal DNS as an external resolver, and DNS forwarding from IPv6-only bridge networks.

Important APIs/types/functions: `TestDaemonDNSFallback`, `TestIntDNSAsExtDNS`, and `TestExtDNSInIPv6OnlyNw` use daemon restart/config helpers, container `nslookup`, `network.StartDaftDNS`, `network.GenResolvConf`, `container.WithDNS`, and internal network creation options.

Control flow: DNS fallback starts a daemon with a bad DNS server followed by `8.8.8.8`, creates a network, runs `nslookup docker.com`, and polls for success. Internal-DNS test runs cases where external DNS list is only `127.0.0.11` or self plus external DNS, expecting `SERVFAIL` or a non-authoritative answer. IPv6-only test runs a local daft DNS server on loopback, starts a daemon using generated resolv.conf, creates an IPv6-only bridge network, and validates container lookup of `test.example`.

State/persistence: creates daemon instances, temp resolver configuration through daemon helper, networks, containers, and a local test DNS server. No repository state.

Dependencies/integration: depends on Linux daemon networking, internal DNS resolver behavior, external internet DNS for some cases, and host loopback resolver setup. Skips remote daemon, Windows, user namespace, and rootless modes where unsupported.

Risks: tests can be flaky if external DNS is unreachable or blocked. The internal DNS address is a special Docker resolver constant; behavior changes require clear compatibility decisions. IPv6-only DNS relies on host resolver visibility from the daemon namespace.

Test signals: passing tests show resolver fallback works, self-recursive resolver configurations fail safely instead of looping, and IPv6-only networks can still use external DNS via the daemon resolver path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/dns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/helpers.go -->
# sources/cloud-native/moby/integration/network/helpers.go

Purpose: Linux-oriented helper functions for network integration tests, covering dummy/VLAN link setup, link existence assertions, and network-list comparisons.

Important APIs/types/functions: `CreateMasterDummy`, `CreateVlanInterface`, `DeleteInterface`, `LinkExists`, `LinkDoesntExist`, `IsNetworkAvailable`, and `IsNetworkNotAvailable`.

Control flow: link helpers shell out through `testutil.RunCommand` to `ip link` and `iptables`, asserting expected success/failure with `icmd`. Network comparison helpers return gotest comparison closures that call `NetworkList`, scan by network name, and return success or descriptive failure.

State/persistence: mutates host network interfaces and flushes iptables nat/filter tables in `DeleteInterface`. Network comparisons are read-only API calls.

Dependencies/integration: Linux `ip` and `iptables` tools, Docker `client.NetworkAPIClient`, `testutil`, `icmd`, and gotest comparison API. Macvlan/ipvlan/mixed-network tests rely on these helpers.

Risks: flushing iptables is broad and can affect other tests if used outside isolated contexts. Link names are hard-coded by callers and can collide if cleanup fails. Helpers assume Linux command output/exit codes.

Test signals: indirect coverage from macvlan, ipvlan, and mixed bridge/ipvlan tests that create dummy parents, VLAN subinterfaces, and assert network presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/helpers_windows.go -->
# sources/cloud-native/moby/integration/network/helpers_windows.go

Purpose: Windows build of shared network availability comparison helpers.

Important APIs/types/functions: `IsNetworkAvailable` and `IsNetworkNotAvailable` return `gotest.tools/v3/assert/cmp.Comparison` closures that list Docker networks and check whether a network name is present or absent.

Control flow: each closure calls `NetworkList`, propagates API errors as comparison errors, scans returned items by `Name`, and returns success/failure with a formatted message.

State/persistence: read-only; no network creation or host interface mutation.

Dependencies/integration: Docker `client.NetworkAPIClient`, context, and gotest `cmp`. It mirrors the portable subset of the Linux helper file without `ip`/`iptables` functions.

Risks: checks only by name, so duplicate names or ambiguous IDs are outside scope. Network-list API failures become assertion failures in callers.

Test signals: Windows network tests use these comparisons for default network availability and create/delete assertions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/helpers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/inspect_test.go -->
# sources/cloud-native/moby/integration/network/inspect_test.go

Purpose: validates verbose overlay network inspection across a multi-manager Swarm cluster before and after a leader change.

Important APIs/types/functions: `TestInspectNetwork` uses `swarm.NewSwarm`, `daemon.StartAndSwarmJoin`, `NetworkCreate` with overlay driver and IPAM config, `swarm.CreateService`, `NetworkInspect` with `Verbose` and optional `Scope`, `NodeList`, and manager restart helpers.

Control flow: the test creates three manager daemons and one worker, creates an overlay network with a constrained IPAM range, deploys a worker-only replicated service, waits for running tasks, then inspects the network by full ID, partial ID, name, and name+swarm scope from every node. It checks IPAM config, manager-only global IPAM status counters, and worker-local service task details. It then forces a leader change by restarting the current leader and repeats the inspection checks.

State/persistence: creates a Swarm cluster, overlay network, VXLAN kernel state, service tasks, and cluster IPAM state. Cleanup removes the network and polls until it is removed from the worker to avoid VXLAN leakage across tests.

Dependencies/integration: Swarm test helpers, daemon harness, API client, `networktypes.SubnetStatus`, poll helpers, and rootless/Windows skips.

Risks: multi-daemon swarm tests are slow and sensitive to leader election timing, VXLAN cleanup, and local kernel state. IPAM counter expectations encode knowledge of manager/worker/task endpoint reservations.

Test signals: passing tests show overlay network inspect remains consistent by ID/name/scope, manager status survives leader change, and worker-local service information is available where the network is instantiated.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/ipvlan_test.go -->
# sources/cloud-native/moby/integration/network/ipvlan/ipvlan_test.go

Purpose: Linux ipvlan driver integration suite covering persistence, parent/subinterface handling, L2/L3/L3S routing, internal networks, multi-subnet dual-stack behavior, IPAM status, overlapping IPAM pools, DNS forwarding, point-to-point allocation, and custom interface names.

Important APIs/types/functions: top-level tests include `TestDockerNetworkIpvlanPersistence`, `TestDockerNetworkIpvlan`, `TestIpvlanIPAM`, `TestIpvlanIPAMOverlap`, `TestIPVlanDNS`, `TestPointToPoint`, and `TestEndpointWithCustomIfname`. Helper tests create dummy parents with `integration/network` helpers and networks with `net.WithIPvlan`, IPAM, IPv4/IPv6 flags, internal mode, and endpoint `netlabel.Ifname`.

Control flow: persistence creates a VLAN parent, creates an ipvlan network, restarts the daemon, and checks network availability. The table-driven driver test starts a fresh daemon per subcase and runs subinterface, overlap, nil-parent, internal, L2/L3 multi-subnet, and addressing checks. IPAM tests create networks under multiple API versions/IPv4/IPv6 combinations, run containers, inspect loopback/eth0 address state, sysctls, and API 1.52 subnet status while ensuring API 1.51 hides status. DNS tests use a loopback test resolver and compare parent/internal combinations for expected forwarding or `SERVFAIL`.

State/persistence: mutates dummy/VLAN links, creates ipvlan networks/containers, relies on daemon restart persistence, and observes per-network IPAM counters. No repository state.

Dependencies/integration: requires Linux privileged networking, non-rootless local daemon, BusyBox image, `ip` commands inside containers, Docker network/client APIs, `cmpopts.EquateEmpty`, and helper package aliases `net` and `n`.

Risks: hard-coded link names and subnets can collide if cleanup fails. Parentless ipvlan behaves like internal networking, and tests rely on that subtle semantic. Overlapping IPAM status counts are global across same-driver subnets, so allocator changes can require updates. Legacy API behavior intentionally ignores `enableIPv4=false` for API 1.46.

Test signals: pings, route/default-gateway assertions, DNS lookup outcomes, network availability checks, inspect IPAM status, sysctl values, and custom interface-name checks provide broad coverage of ipvlan functional and compatibility behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/ipvlan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/main_test.go -->
# sources/cloud-native/moby/integration/network/ipvlan/main_test.go

Purpose: non-Windows test harness for the ipvlan integration package.

Important APIs/types/functions: package globals `testEnv` and `baseContext`, `TestMain`, and `setupTest`. It configures tracing, initializes `environment.Execution`, ensures frozen Linux images, prints environment info, records failed exit code on the span, and wraps tests with environment protection/cleanup.

Control flow: initialization errors mark the span, end tracing, shut down, and panic. `setupTest` starts a per-test span from `baseContext`, calls `environment.ProtectAll`, and schedules `testEnv.Clean`.

State/persistence: holds package-global environment state and OpenTelemetry base context. Per-test cleanup is delegated to the environment helper, while individual ipvlan tests clean host links/daemons.

Dependencies/integration: `testutil`, `environment`, and OpenTelemetry. The build tag excludes Windows.

Risks: frozen Linux image setup is mandatory for the package; failures abort all ipvlan tests. Host link mutations still rely on test-specific cleanup.

Test signals: package startup success indicates the ipvlan suite has daemon/image resources and tracing context available.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/main_windows_test.go -->
# sources/cloud-native/moby/integration/network/ipvlan/main_windows_test.go

Purpose: Windows package stub for `integration/network/ipvlan`.

Important APIs/types/functions: declares `package ipvlan` only; there are no tests, setup functions, or exported helpers.

Control flow: none.

State/persistence: none.

Dependencies/integration: exists so the package has a Windows build target despite the real ipvlan tests being behind `!windows` build tags.

Risks: no Windows coverage for ipvlan behavior; this is expected because ipvlan is not exercised by this package on Windows.

Test signals: compile-only signal that the package is valid on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/ipvlan/main_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/macvlan_test.go -->
# sources/cloud-native/moby/integration/network/macvlan/macvlan_test.go

Purpose: Linux macvlan driver integration suite covering persistence, parent/subinterface lifecycle, passthru overlap rejection, nil-parent/internal behavior, multi-subnet dual-stack addressing, IPAM status/overlap accounting, DNS forwarding, point-to-point allocation, custom interface names, and attachment when the parent is down.

Important APIs/types/functions: top-level tests include `TestDockerNetworkMacvlanPersistence`, `TestDockerNetworkMacvlan`, `TestMacvlanIPAM`, `TestMacvlanIPAMOverlap`, `TestMACVlanDNS`, `TestPointToPoint`, `TestEndpointWithCustomIfname`, and `TestParentDown`. Helper functions exercise overlap variants, dynamic parent creation, parent preservation/deletion, multi-subnet addressing, and route assertions.

Control flow: the table-driven driver test starts a new daemon for each subcase and manipulates dummy/VLAN parents. Overlap tests check when shared parents are allowed, when passthru blocks sharing, and when generated subinterfaces are deleted only after the final owning network is removed. IPAM tests vary IPv4/IPv6 flags and API version, run a container, inspect addresses/sysctls, and compare API 1.52 status counters with API 1.51 hiding status. DNS tests use a loopback daft DNS resolver to distinguish parent/internal behavior.

State/persistence: creates host dummy/VLAN/tap interfaces, macvlan networks, containers, daemon state across restart, and IPAM allocations. `TestParentDown` creates a tap interface without bringing it up to verify attachment still succeeds.

Dependencies/integration: requires Linux privileged networking, `ip`/`tuntap`, Docker daemon/client helpers, network helper package, BusyBox image, and gotest assertions. Rootless/remote daemon modes are skipped for most host-link tests.

Risks: parent-link ownership semantics are delicate; cleanup failure can leak interfaces or delete an interface expected by another test. IPAM counters encode allocator details including gateway, broadcast, aux, anycast, and container reservations. Nil-parent macvlan connectivity expectations differ from ipvlan and can be easy to regress.

Test signals: network availability, link existence/nonexistence, ping success or expected failure, route output, DNS success/SERVFAIL, inspect IPAM status, sysctl values, and custom-ifname output collectively validate macvlan driver behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/macvlan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/main_test.go -->
# sources/cloud-native/moby/integration/network/macvlan/main_test.go

Purpose: non-Windows test harness for macvlan integration tests.

Important APIs/types/functions: defines `testEnv`, `baseContext`, `TestMain`, and `setupTest`. It configures tracing, initializes the execution environment, ensures frozen Linux images, prints environment details, records the exit code as an OpenTelemetry attribute, and cleans test resources.

Control flow: `TestMain` sets up package-global state, panics on initialization/image errors after marking span status, runs tests, records non-zero status, and exits. `setupTest` starts per-test spans and schedules environment cleanup.

State/persistence: package-global environment and tracing state. Individual tests manage host interfaces and daemons beyond this harness.

Dependencies/integration: `testutil`, `environment`, OpenTelemetry `attribute`/`codes`. Build tag excludes Windows.

Risks: global setup failure stops the package. Environment cleanup does not replace explicit cleanup needed for host networking objects.

Test signals: successful startup means macvlan tests have a prepared daemon environment and frozen images.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/main_windows_test.go -->
# sources/cloud-native/moby/integration/network/macvlan/main_windows_test.go

Purpose: Windows package stub for `integration/network/macvlan`.

Important APIs/types/functions: contains only `package macvlan`.

Control flow: none.

State/persistence: none.

Dependencies/integration: keeps the package buildable on Windows while real macvlan tests are Linux-only.

Risks: there is no Windows functional coverage in this package; that matches driver/platform availability expectations.

Test signals: compile-only Windows package presence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/macvlan/main_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/main_test.go -->
# sources/cloud-native/moby/integration/network/main_test.go

Purpose: shared test harness for the general `integration/network` package.

Important APIs/types/functions: declares `testEnv`, `baseContext`, `TestMain`, and `setupTest`. It configures tracing, initializes `environment.Execution`, ensures frozen Linux images, prints environment info, tracks non-zero package exits on the root span, and protects/cleans resources per test.

Control flow: global setup runs before all tests and panics on environment/image failures. `setupTest` starts a per-test span, calls `environment.ProtectAll`, and registers `testEnv.Clean`.

State/persistence: package-global environment and tracing context. Per-test cleanup resets daemon resources known to the environment helper.

Dependencies/integration: `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry. General network tests use `testEnv` for daemon info, rootless/remote flags, API client, and firewall backend.

Risks: image setup is Linux-oriented even though some package files have Windows behavior; platform-specific skips must prevent incompatible execution. Host-level mutations in tests still need explicit cleanup.

Test signals: successful harness setup is a prerequisite for all general network integration tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/nat/main_windows_test.go -->
# sources/cloud-native/moby/integration/network/nat/main_windows_test.go

Purpose: Windows NAT network package test harness.

Important APIs/types/functions: declares `testEnv`, `baseContext`, `TestMain`, and `setupTest`, configuring tracing and the test execution environment for NAT tests.

Control flow: `TestMain` initializes environment state, calls `EnsureFrozenImagesLinux`, prints environment details, records failed exit status on the span, shuts down tracing, and exits. `setupTest` starts a child span and schedules environment cleanup.

State/persistence: package-global environment and tracing context; per-test environment cleanup.

Dependencies/integration: Moby `testutil`, `environment`, and OpenTelemetry. Although the file is Windows-named, it shares the same environment setup pattern as other network packages.

Risks: `EnsureFrozenImagesLinux` in a Windows-named harness is surprising and may rely on the broader integration test environment's conventions. If Windows image preparation diverges, this harness may need adjustment.

Test signals: package setup success allows the Windows NAT behavior test to run against `testEnv.APIClient()`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/nat/main_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/nat/nat_windows_test.go -->
# sources/cloud-native/moby/integration/network/nat/nat_windows_test.go

Purpose: verifies that Docker's Windows `nat` driver rejects disabling IPv4.

Important APIs/types/functions: `TestWindowsNoDisableIPv4` calls `network.Create` with `network.WithDriver("nat")` and `network.WithIPv4(false)`, then asserts the error contains `IPv4 cannot be disabled on Windows`.

Control flow: setup obtains context and API client, attempts to create an IPv6-only NAT network, and expects failure instead of cleanup.

State/persistence: no successful persistent network is created; the test validates rejection at creation time.

Dependencies/integration: Windows network package harness, internal network helper, Docker API client, and gotest comparison assertions.

Risks: exact error text is part of the test signal and may need updating if user-facing wording changes while preserving behavior.

Test signals: passing test confirms the Windows NAT driver enforces IPv4 availability and surfaces a clear error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/nat/nat_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/network_linux_test.go -->
# sources/cloud-native/moby/integration/network/network_linux_test.go

Purpose: Linux-focused general network integration tests for disabled default bridge behavior, bridge SNAT host IPv4 option, default network options, duplicate names, host-gateway resolution, gateway priority routing, and bridge/ipvlan mixed routing.

Important APIs/types/functions: top-level tests include `TestRunContainerWithBridgeNone`, `TestHostIPv4BridgeLabel`, `TestDefaultNetworkOpts`, `TestForbidDuplicateNetworkNames`, `TestHostGatewayFromDocker0`, `TestCreateWithPriority`, `TestConnectWithPriority`, `TestMixL3IPVlanAndBridge`, and helper `checkCtrRoutes`.

Control flow: tests start daemons with targeted flags, create networks/containers, execute `ip` commands in containers, inspect network state, and compare firewall or route output. Gateway-priority tests create multiple dual-stack networks with explicit IPAM, attach/disconnect endpoints with different `GwPriority`, and assert route counts/default route selection. Mixed ipvlan/bridge test creates bridge and L3 ipvlan networks, optionally restarts with live-restore, then validates default route transitions as networks are disconnected/reconnected.

State/persistence: creates daemon instances, dummy interfaces, networks, containers, routes, firewall rules, default bridge state, and live-restore state. Some tests delete `docker0` or use isolated `L3Segment` namespaces to avoid host pollution.

Dependencies/integration: Linux `ip`, `iptables`/`nft`, `syscall` address families, daemon helper, network/container helpers, API version gating, and bridge/ipvlan driver labels. Rootless/remote/userns/Windows modes are skipped where incompatible.

Risks: route-count assertions depend on kernel/network-driver route emission. Gateway priority tie-breaking and interface-name prefixes are compatibility-sensitive. Firewall backend checks differ for nftables vs iptables. Deleting or recreating docker0 and dummy links can affect other tests if cleanup fails.

Test signals: passing tests verify disabled bridge mode lacks `eth0`, host networking shares namespace, SNAT rules use configured host IPv4, default MTU options propagate, duplicate names are rejected, host-gateway maps v4/v6, gateway priority controls default routes across connect/disconnect, and L3 ipvlan routes coexist correctly with bridge gateways including live restore.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/network_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/network_test.go -->
# sources/cloud-native/moby/integration/network/network_test.go

Purpose: general API-level network integration tests covering invalid JSON handling, network list endpoints, default network presence, filtering, and scope-aware inspection.

Important APIs/types/functions: `TestNetworkInvalidJSON`, `TestNetworkList`, `TestAPINetworkGetDefaults`, `TestAPINetworkFilter`, and `TestNetworkInspectWithScope` use low-level request helpers, API client filters, swarm helper, and containerd errdefs not-found matching.

Control flow: invalid JSON test iterates POST endpoints and subcases for content type, malformed JSON, trailing content, and empty body. Network list checks `/networks` and `/networks/`. Default/filter tests vary expected network names by OS. Scope test creates a swarm overlay network, verifies default inspect returns swarm scope and ID, then verifies local-scope inspect returns not found.

State/persistence: creates a temporary swarm daemon and overlay network in the scope test; other tests are mostly read-only HTTP/API calls.

Dependencies/integration: `internal/testutil/request`, Docker API client, network API types, swarm helper, `cerrdefs.IsNotFound`, and package harness. Some tests are platform-sensitive through `testEnv.DaemonInfo.OSType`.

Risks: exact HTTP error text for JSON parsing/content type is asserted and can change with API decoder behavior. Empty-body assertion only guards against 5xx, not exact client error. Scope behavior depends on swarm overlay creation.

Test signals: passing tests show network endpoints reject bad request bodies predictably, list endpoints are backward-compatible with trailing slash, default networks exist, name filters work, and scope selection disambiguates swarm vs local network inspect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/main_test.go -->
# sources/cloud-native/moby/integration/network/overlay/main_test.go

Purpose: non-Windows test harness for overlay network integration tests.

Important APIs/types/functions: package globals `testEnv` and `baseContext`, `TestMain`, and `setupTest`. It configures tracing, creates the execution environment, ensures frozen Linux images, prints environment info, records exit status attribute, and cleans resources per test.

Control flow: setup failures mark span status, end/shutdown tracing, and panic. `setupTest` starts a child span, protects resources, and schedules cleanup.

State/persistence: package-global test environment and tracing context; overlay tests create their own swarm/daemon state.

Dependencies/integration: Moby `testutil`, `environment`, and OpenTelemetry. Build tag excludes Windows.

Risks: global environment setup is a package-wide prerequisite. Overlay tests additionally depend on swarm support and rootless skips.

Test signals: successful harness startup provides the daemon/image environment required for overlay tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/main_windows_test.go -->
# sources/cloud-native/moby/integration/network/overlay/main_windows_test.go

Purpose: Windows package stub for `integration/network/overlay`.

Important APIs/types/functions: contains only `package overlay`.

Control flow: none.

State/persistence: none.

Dependencies/integration: keeps the overlay package buildable on Windows while the real tests are behind `!windows`.

Risks: no Windows overlay behavior is covered in this package.

Test signals: compile-only Windows package signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/main_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/overlay_test.go -->
# sources/cloud-native/moby/integration/network/overlay/overlay_test.go

Purpose: overlay network integration tests for custom container interface names and host-mode swarm port mapping visibility.

Important APIs/types/functions: `TestEndpointWithCustomIfname` creates an attachable overlay network and runs a container with endpoint driver option `netlabel.Ifname`. `TestHostPortMappings` creates a swarm service with host-mode published port and validates `ContainerList` port reporting.

Control flow: custom-ifname test starts and initializes swarm, creates an attachable overlay network, runs a container executing `ip -o link show foobar`, and asserts the output contains the requested interface name. Host-port test starts a swarm node with BusyBox, creates overlay network/service, waits for one task, lists containers, formats public/private port bindings, sorts them, and expects IPv4 plus optional IPv6 wildcard binding.

State/persistence: creates swarm state, overlay networks, services, tasks, and containers, then removes/leaves via cleanup.

Dependencies/integration: swarm helpers, daemon helper, Docker API, container/network helpers, `netlabel.Ifname`, polling, and Linux `ip` inside containers. Rootless mode is skipped because overlay is unsupported there.

Risks: host-mode port list may vary by IPv6 availability, hence the optional second address. Swarm task scheduling/polling can be timing-sensitive. Custom interface-name support depends on overlay driver endpoint implementation.

Test signals: passing tests show overlay endpoints honor custom interface names and `ContainerList` reports the expected one or two host-mode published port bindings for swarm tasks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/overlay/overlay_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/network/service_test.go -->
# sources/cloud-native/moby/integration/network/service_test.go

Purpose: integration suite for daemon network-pool persistence, swarm service/network behavior, ingress/default address pool configuration, live-restore custom interface names, and dynamic interface naming collisions.

Important APIs/types/functions: helper `delInterface` deletes a link and flushes iptables. Tests include daemon restart/pool cases, `TestServiceWithPredefinedNetwork`, skipped `TestServiceRemoveKeepsIngressNetwork`, `swarmIngressReady`, `noServices`, `TestServiceWithDataPathPortInit`, `TestServiceWithDefaultAddressPoolInit`, `TestCustomIfnameIsPreservedOnLiveRestore`, `TestCustomIfnameCollidesWithExistingIface`, `TestCustomIfnameWithMatchingDynamicPrefix`, and `checkIfaceAddr`.

Control flow: daemon pool tests start/restart daemons with `--default-address-pool`, `--bip`, and `--live-restore`, inspect bridge/user-network subnets, and ensure existing networks keep prior allocations. Swarm tests create services on predefined/overlay networks, poll task counts, inspect/remove services, validate data-path port and default address pool allocation for ingress and user overlay networks. Custom-ifname tests run containers with endpoint driver options, restart live-restore daemons, disconnect networks, provoke `eth0` rename collision, and verify dynamic `ethN` reuse after disconnect/reconnect.

State/persistence: mutates `docker0`, iptables, daemon network store, swarm cluster state, ingress/overlay networks, services/tasks, live-restore container sandbox state, and container interface names. Cleanup removes services/networks and may restart daemons to restore default state.

Dependencies/integration: daemon and swarm helpers, Docker API network/service clients, internal container/network helpers, bridge/netlabel options, `ip`/`iptables`, polling, and BusyBox. Many tests skip Windows, rootless, or remote daemon modes.

Risks: broad host-network mutations (`delInterface` and iptables flush) can affect neighboring tests if cleanup fails. Address-pool tests assume deterministic allocator order. Swarm tests can be timing-sensitive and one ingress test is explicitly skipped as flaky. Interface-name assertions encode live-restore sandbox reconstruction details.

Test signals: passing tests verify default pools do not overwrite existing networks or `--bip`, swarm services work with host/predefined networks, data-path/default address pools initialize as configured, ingress/default overlay subnets are allocated as expected, custom interface names survive live restore and collision/reuse behavior is correct.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/network/service_test.go -->
