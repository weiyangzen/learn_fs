# subset-b-000200 research

Grouped research for Moby integration CLI tests. Each section preserves its source path and is bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_info_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_info_test.go

Purpose: tests `docker info` baseline output and container state counters. `DockerCLIInfoSuite` delegates teardown and timeout to `DockerSuite`, so each test relies on the shared integration cleanup model.

Important APIs and functions: `cli.DockerCmd` drives the CLI, `testEnv.DaemonInfo` and `DaemonIsLinux` gate expected fields, and `existingContainerStates` runs `docker info --format {{json .}}`, unmarshals it into `map[string]any`, and extracts `Containers`, `ContainersRunning`, `ContainersPaused`, and `ContainersStopped`.

Control flow: `TestInfoEnsureSucceeds` builds a required-prefix list, conditionally adds Linux, runtime, and experimental fields, then scans raw `docker info` text. The running, paused, and stopped tests snapshot existing counters, create or transition a busybox container, rerun `docker info`, and assert only the intended counter changes.

State and persistence: the tests intentionally mutate daemon container state but do not inspect disk. They are sensitive to pre-existing containers, so the helper snapshots current counts before creating new state.

Dependencies and integration points: relies on busybox, the integration CLI wrapper, daemon OS capability checks, and JSON formatting from the CLI info command.

Risks: output-prefix assertions can break on CLI wording changes; JSON numeric decoding assumes float64; counter tests are vulnerable to concurrent container creation by other tests or leaked containers.

Test signals: success means `docker info` exposes required metadata and accurately reflects running, paused, and stopped container totals after lifecycle transitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_info_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_info_unix_test.go

Purpose: Unix-only security option validation for daemon info. It extends `DockerCLIInfoSuite` with coverage for AppArmor and seccomp reporting.

Important APIs and functions: `client.New(client.FromEnv)` creates an Engine API client, `apiClient.Info` fetches structured daemon info, `config.SeccompProfileDefault` provides the expected default profile name, and local helpers `Apparmor`, `seccompEnabled`, `DaemonIsLinux`, and `testEnv.IsLocalDaemon` gate the test.

Control flow: the test skips unless running against a local Linux daemon and at least one of seccomp or AppArmor is enabled. It calls the API, reads `result.Info.SecurityOptions`, and checks for `name=apparmor` and/or `name=seccomp,profile=default` as appropriate.

State and persistence: read-only against daemon state. It validates current runtime security configuration rather than changing containers, images, or files.

Dependencies and integration points: depends on host kernel/security module configuration, Engine API behavior, and the daemon environment inherited through `client.FromEnv`.

Risks: host configuration variability is high; a daemon compiled or configured without these features skips. The test is intentionally Linux/local-only because remote or Windows daemons may report different security option sets.

Test signals: structured API info must include security option entries that match the enabled host security features.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_info_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_inspect_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_inspect_test.go

Purpose: broad `docker inspect` integration coverage for images, containers, plugins, formatting, size fields, mounts, network settings, object lookup precedence, and error behavior.

Important APIs and functions: `DockerCLIInspectSuite`, `cli.DockerCmd`, `dockerCmdWithError`, `inspectField`, `inspectFieldJSON`, `inspectFilter`, `loadSpecialImage`, typed decoders for `container.MountPoint`, `container.LogConfig`, and `image.InspectResponse`, plus `icmd` for explicit process assertions.

Control flow: tests create named containers/images, inspect specific paths or JSON blobs, decode typed output when structure matters, and verify CLI formatting. Object resolution tests cover container-vs-image precedence, `--type` filtering, invalid type values, ID prefixes, multiple object inspect with missing entries, and plugin inspection. Lifecycle state tests transition running, paused, unpaused, stopped, and committed objects before inspecting.

State and persistence: creates containers, named volumes, bind mounts, committed images, plugins, and networks. It checks persisted inspect fields such as `Created`, `State.StartedAt`, `Mounts`, `HostConfig.LogConfig`, `SizeRw`, `SizeRootFs`, image `RootFS.Layers`, and network IDs.

Dependencies and integration points: integrates with special image fixtures, busybox, plugin installation, container/image inspect API schemas, Go template rendering, and daemon-specific paths via `dPath`.

Risks: stable image ID assertions intentionally catch serialization changes but may fail when snapshotter behavior changes; template error text is brittle; plugin tests require Linux amd64 network access; mount behavior differs by OS.

Test signals: inspect must return correctly typed and formatted data, preserve timestamps as RFC3339Nano, include expected mount/network/log fields, continue inspecting valid objects when others are missing, and produce clear not-found or template errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_links_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_links_test.go

Purpose: regression tests for legacy `--link` behavior across default networking, user-provided aliases, `/etc/hosts` injection, inspect metadata, rename/restart handling, and invalid link combinations.

Important APIs and functions: `DockerCLILinksSuite`, `testLinkPingOnNetwork`, `cli.DockerCmd`, `dockerCmdWithError`, `inspectFieldJSON`, `readContainerFileWithExec`, regex parsing of `/etc/hosts`, and sorting before comparing `HostConfig.Links`.

Control flow: tests create upstream containers, start linked consumers with aliases, then verify ping by alias, container name, and hostname. Inspect tests decode `HostConfig.Links`. Restart tests compare linked host IPs before and after upstream restart. Negative tests cover bogus targets, host-network containers, duplicate alias names, and unlinked name lookup.

State and persistence: mutates container names, link definitions, `/etc/hosts` content inside containers, bridge IP assignments, and inspect metadata. State is expected to update after rename/restart without stale link data.

Dependencies and integration points: Linux-only networking behavior, busybox ping/top, daemon link implementation, inspect JSON, `/etc/hosts` generation, and user namespace restrictions for host-network cases.

Risks: legacy links are deprecated and have network-mode-specific behavior; ping timing and DNS/hosts propagation can be flaky; duplicate alias behavior depends on resolver ordering.

Test signals: linked containers can resolve and reach expected names, inspect records exact link definitions, link host entries update after restart, and invalid combinations fail with clear conflict messages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_links_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_login_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_login_test.go

Purpose: validates CLI login behavior without a TTY and against an htpasswd-protected private registry.

Important APIs and functions: `DockerCLILoginSuite`, `exec.Command(dockerBinary, "login")`, `bytes.NewBufferString` to provide non-TTY stdin, `dockerCmdWithError`, and `cli.DockerCmd` for registry login.

Control flow: `TestLoginWithoutTTY` runs `docker login` with stdin backed by a buffer and expects failure when no interactive TTY is available, except for a Windows skip. `TestLoginToPrivateRegistry` first attempts wrong credentials and expects `401 Unauthorized`, then logs in with suite-provided registry credentials.

State and persistence: successful registry login writes auth material through the CLI's normal config path; the test itself does not inspect the config file.

Dependencies and integration points: private registry auth suite, `dockerBinary`, OS-specific terminal behavior, and registry username/password helpers.

Risks: TTY error behavior can vary by CLI version and OS; password-on-command-line usage is test-only but mirrors legacy CLI behavior; registry auth failures depend on exact server response text.

Test signals: login must reject non-interactive use when credentials cannot be gathered and must authenticate correctly with valid private registry credentials after rejecting invalid ones.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_login_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_logout_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_logout_test.go

Purpose: validates logout behavior with external credential helpers, including hostnames stored with and without URL schemes.

Important APIs and functions: registry auth suite methods, fixture credential helper `docker-credential-shell-test`, `os.MkdirTemp`, `os.WriteFile`, `os.ReadFile`, `filepath.Abs`, `exec.Command`, `s.d.Cmd`, and `cli.DockerCmd`.

Control flow: one test adds the auth fixture to `PATH`, creates a temp `config.json` with `credsStore`, logs in, confirms no inline `"auth"` is stored, tags/pushes, logs out, confirms registry entries are removed, and verifies pull fails without credentials. The hostname test preloads the helper with `https://host`, writes config entries for scheme and bare host, logs in, then logs out and asserts both entries disappear.

State and persistence: intentionally writes temp Docker config files and uses an external credential store. It also tags and pushes registry images through a daemon started with busybox.

Dependencies and integration points: credential helper fixture, private registry, temp Docker config directories, daemon command wrapper, and filesystem config persistence.

Risks: sensitive to credential-helper protocol behavior and config key normalization; failures can leave temp helper state outside the Docker config if the fixture is broken.

Test signals: logout removes credentials from helper-backed config for both scheme-qualified and bare registry hostnames, and registry access fails after logout.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_logout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_logs_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_logs_test.go

Purpose: tests `docker logs` output correctness, pagination boundaries, stdout/stderr routing, timestamps, tail/since/follow behavior, details fields, missing containers, and daemon goroutine cleanup.

Important APIs and functions: `DockerCLILogsSuite`, `testLogsContainerPagination`, `ConsumeWithSpeed`, `exec.Command`, `io.Pipe`, local daemon creation via `daemon.New`, `waitForStableGoroutineCount`, `waitForGoroutines`, and `icmd`.

Control flow: pagination tests generate exact byte counts around page-size boundaries. Timestamp tests parse RFC3339Nano with fixed padding. Tail and since tests create known log streams and filter them. Follow tests start `docker logs -f`, wait or kill the client, and assert clean process exit. Goroutine tests use a separate daemon and compare daemon goroutine counts before and after killed follow clients with and without output.

State and persistence: creates containers whose log files persist after exit, exercises log-driver detail metadata from labels/env, and starts temporary daemons with disabled iptables for leak checks.

Dependencies and integration points: busybox shell output, json-file logging behavior, `containerd/log` timestamp format, process pipes, daemon API goroutine metrics, and Linux/local daemon constraints for leak tests.

Risks: timing-sensitive follow and since tests can be flaky; goroutine counts require stabilization; slow-consumer behavior depends on pipe buffering; Windows tty/stderr behavior differs and is gated.

Test signals: logs return exact byte counts, stream separation is correct, `--tail`, `--since`, `--timestamps`, `--details`, and `--follow` behave correctly, and killed log followers do not leak daemon goroutines.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_logs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_netmode_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_netmode_test.go

Purpose: validates CLI/daemon rejection or acceptance of `--net` combinations with hostname, links, MAC addresses, DNS, add-host, publish, and expose options.

Important APIs and functions: `DockerCLINetmodeSuite`, constant `stringCheckPS`, helper `dockerCmdWithFail`, `cli.DockerCmd`, and `dockerCmdWithError`.

Control flow: positive tests run `busybox ps` with host, bridge, none, and hostname combinations and check command output. Negative tests call `dockerCmdWithFail`, assert nonzero exit, and inspect conflict messages for container network mode, host network mode, invalid `container:` syntax, unknown networks, links, DNS, add-host, `-P`, `-p`, `--expose`, and MAC address conflicts.

State and persistence: only transient containers are created; no persistent daemon configuration is changed.

Dependencies and integration points: Linux and user-namespace gates, busybox, CLI validation layer, and daemon-side network mode validation.

Risks: some validation is noted as missing or skipped; error text assertions are brittle; behavior differs between CLI-side and daemon-side validation.

Test signals: supported network modes run a command successfully, while invalid option combinations fail before producing ambiguous container networking state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_netmode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_network_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_network_test.go

Purpose: defines shared suite types for CLI network tests and full daemon/network-driver integration tests.

Important APIs and types: `DockerCLINetworkSuite` wraps `*DockerSuite` for ordinary CLI-network tests, while `DockerNetworkSuite` holds an `httptest.Server`, `*DockerSuite`, and `*daemon.Daemon` for tests that need local daemon control or remote driver simulation.

Control flow: only lifecycle hooks are present here. `DockerCLINetworkSuite` delegates teardown and timeout to `DockerSuite`; `DockerNetworkSuite` fields are initialized and exercised in the Unix-specific file.

State and persistence: no direct state changes in this file. It establishes the storage for per-test daemon handles and remote plugin HTTP server references used elsewhere.

Dependencies and integration points: `context`, `testing`, `net/http/httptest`, and the integration `daemon` helper. This file is the cross-platform suite declaration paired with Unix implementation in `docker_cli_network_unix_test.go`.

Risks: because behavior lives in build-tagged companions, missing or mismatched suite hooks can silently affect a large number of network tests.

Test signals: indirect; successful compilation and suite registration enable the network integration tests to run with the correct fixture ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_network_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_network_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_network_unix_test.go

Purpose: comprehensive Unix network integration coverage for `docker network`, container network settings, remote network/IPAM plugins, daemon restart persistence, aliases, DNS, host/default bridge behavior, port mapping interactions, and conntrack cleanup.

Important APIs and functions: `DockerNetworkSuite` setup/teardown, `setupRemoteNetworkDrivers`, helpers `assertNwIsAvailable`, `assertNwNotAvailable`, `assertNwList`, `getNwResource`, `connectContainerToNetworks`, `verifyContainerIsConnectedToNetworks`, `verifyPortMap`, `verifyIPAddressConfig`, and `verifyIPAddresses`. It uses API structs from `container` and `network`, libnetwork remote driver/IPAM APIs, plugin spec files, `netlink`, `nlwrap`, and `unix`.

Control flow: suite setup starts an `httptest.Server` that implements network and IPAM plugin endpoints and writes `/etc/docker/plugins/*.spec`. Tests then cover default networks, create/rm/list filters, inspect by name/ID/multiple inputs, connect/disconnect paths, IPAM valid and invalid combinations, plugin v2 network drivers, default bridge discovery, anonymous endpoints, links, overlay-like port output, graceful and ungraceful daemon restarts, host mode restrictions, port mapping stability across network connect/disconnect, MAC assignment, stopped-container network edits, preferred IPv4/IPv6/link-local addresses, alias scoping, embedded DNS, internal networks, special-character names, live-restore bridge restoration, IP validation, bridge disconnect by ID, and conntrack flow deletion.

State and persistence: this file mutates daemon networks, plugin spec files under `/etc/docker/plugins`, kernel links/veths, conntrack tables, container endpoint configs, daemon restart state, IP allocation state, `/etc/hosts`, and port bindings. Several tests explicitly restart or kill daemons to validate disk-persisted network attachments and live-restore behavior.

Dependencies and integration points: Linux-only kernel networking, local daemon control, busybox/debian images, libnetwork remote driver contract, plugin installation, API inspect JSON, netlink, DNS at `127.0.0.11`, and swarm/overlay-adjacent behavior through dummy drivers.

Risks: high environmental sensitivity: requires local Linux privileges, available subnets/ports, netlink/conntrack access, amd64 for some plugin tests, and stable timing around daemon restart. Global `/etc/docker/plugins` writes and kernel resources must be cleaned or later tests can fail.

Test signals: network commands must reject invalid built-ins, preserve inspect and endpoint state, maintain IP/MAC/alias/link-local settings across starts and restarts, keep port mappings coherent, keep DNS scoped to user-defined networks, avoid stale inspect mutations after failed connects, restore live bridge allocations, and remove NAT conntrack flows when containers are deleted.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_network_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_plugins_logdriver_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_plugins_logdriver_test.go

Purpose: validates v2 plugin log drivers for container logs and daemon info reporting.

Important APIs and functions: `DockerCLIPluginLogDriverSuite`, `cli.DockerCmd`, Engine `client.Info`, `client.New(client.FromEnv)`, and `testutil.GetContext`.

Control flow: `TestPluginLogDriver` installs `cpuguy83/docker-logdriver-test:latest`, runs a container with `--log-driver`, checks logs after first run, starts it attached again, checks accumulated logs, then removes container and plugin. `TestPluginLogDriverInfoList` installs the plugin, reads daemon info through the API, joins `info.Plugins.Log`, and asserts built-in `json-file` appears while the v2 plugin name does not.

State and persistence: installs and removes a daemon plugin, creates log records for a named container, and reads daemon plugin metadata.

Dependencies and integration points: Linux amd64 daemon, network/plugin distribution access, Docker plugin subsystem, log driver integration, and daemon info API.

Risks: plugin availability and architecture are external; log output accumulation can fail if the driver changes retention semantics; info-list behavior is intentionally subtle because v2 plugins should not appear in the legacy log plugin list.

Test signals: containers using the plugin log driver produce retrievable logs, repeated starts append as expected, and daemon info separates built-in log drivers from v2 plugin drivers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_plugins_logdriver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_plugins_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_plugins_test.go

Purpose: broad Docker plugin lifecycle tests for install, disable, enable, remove, active-use protection, setting configurable fields, create/inspect/list/upgrade, ID prefix addressing, default formatting, and plugin metrics.

Important APIs and functions: `DockerCLIPluginsSuite`, `DockerPluginSuite` methods such as `getPluginRepoWithTag`, plugin helpers from `internal/testutil/plugin`, `plugintypes`, Engine API client via `testEnv.APIClient`, `cli.DockerCmd`, `dockerCmdWithError`, temp filesystem creation for `plugin create`, and HTTP metrics reads.

Control flow: tests install plugins with and without `--disable`, verify active volume/network plugins cannot be disabled/removed until resources are removed, mutate settable env/mount/device fields, reject invalid set operations, install with args, reject installing a container image as a plugin, check duplicate enable/disable errors, create plugins from a local config/rootfs, inspect by full ID, short ID, tag, and untagged name, verify Windows unsupported errors, operate by ID prefix, honor `pluginsFormat`, upgrade only after disable, and fetch metrics from a plugin endpoint.

State and persistence: installs plugins into daemon plugin storage, creates volumes/networks, writes local plugin config/rootfs directories, touches plugin rootfs files during upgrade, and reads daemon root plugin paths. Plugin enable/disable state and settings are persisted and inspected.

Dependencies and integration points: Linux amd64 plugin runtime, private/public plugin registries, network access, Docker volume/network subsystems, daemon root directory, HTTP metrics endpoint, and platform gates.

Risks: external plugin images can disappear or change; upgrade test inspects daemon internals; metrics port conflicts are possible; test state is heavy and requires careful cleanup.

Test signals: plugin lifecycle commands must enforce active-use constraints, preserve and expose settings, resolve IDs consistently, format lists according to config, reject unsupported artifacts/platforms, upgrade rootfs only when disabled, and expose plugin-provided metrics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_plugins_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_port_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_port_test.go

Purpose: validates `docker port`, published/exposed port display in `docker ps`, host binding reachability, port range allocation, protocol handling, and internal-network sandbox port behavior.

Important APIs and functions: `DockerCLIPortSuite`, `assertPortList`, `assertPortRange`, `stopRemoveContainer`, Engine API `ContainerInspect`, `client.ContainerInspectOptions`, regex assertions for dynamic ports, and `getNetworkResource`.

Control flow: `TestPortList` runs containers with single, multiple, duplicate, ranged, invalid, host-container range, and mixed TCP/UDP mappings, then compares `docker port` output. `assertPortList` sorts mappings and accepts old IPv6 formatting. `assertPortRange` inspects API port bindings and verifies host ports fall within expected ranges. Other tests check unpublished exposed ports in `ps`, connectivity through host networking, binding release after container removal, and port mapping becoming reachable only after an internal-network container connects to a normal bridge.

State and persistence: creates/removes containers, port bindings, internal and bridge networks, and inspects live network settings. Port allocation reuse is explicitly tested after removal.

Dependencies and integration points: Linux networking, host network mode, busybox `nc`, Engine inspect API, IPv4/IPv6 display, dynamic host port allocation, and user namespace constraints.

Risks: fixed ports can conflict with host services or parallel tests; IPv6 formatting compatibility adds ambiguity; internal network reachability depends on gateway selection and sandbox updates.

Test signals: port mappings must be listed accurately, invalid ranges must fail, exhausted ranges must fail, freed ranges must be reusable, `ps` must show exposed/published ports, and host connectivity must match network attachment state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_port_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_proxy_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_proxy_test.go

Purpose: verifies Docker CLI proxy environment handling for Unix sockets and TCP daemon endpoints.

Important APIs and functions: `DockerCLIProxySuite`, `DockerDaemonSuite`, `icmd.RunCmd`, `appendBaseEnv`, `net.InterfaceAddrs`, and daemon start with `-H tcp://...:2375`.

Control flow: the Unix socket test runs `docker info` with `HTTP_PROXY` pointing at a dead proxy and expects success, proving local Unix socket connections bypass HTTP proxy settings. The TCP test finds a non-loopback host IP, starts the daemon listening on that TCP address, verifies `docker info` fails through the bad proxy, then succeeds when `NO_PROXY` includes the daemon IP.

State and persistence: starts a daemon TCP listener but does not persist config.

Dependencies and integration points: local Linux daemon, host network interfaces, Go proxy environment semantics, Docker CLI transport selection, and daemon command wrapper.

Risks: host interface selection can pick an unsuitable address; port 2375 conflicts or firewall behavior may affect the test; proxy error text is not asserted, only failure.

Test signals: proxy variables must not affect Unix socket connections, must affect TCP connections, and `NO_PROXY` must exempt the TCP daemon host.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_proxy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_prune_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_prune_test.go

Purpose: declares `DockerCLIPruneSuite`, the shared suite holder for prune CLI tests implemented in Unix-specific files.

Important APIs and types: `DockerCLIPruneSuite` contains `ds *DockerSuite`, matching the integration suite pattern used by other CLI command groups.

Control flow: no test logic exists here; lifecycle methods are supplied in `docker_cli_prune_unix_test.go`.

State and persistence: no direct state changes.

Dependencies and integration points: this file exists so prune tests share suite registration and can attach teardown/timeout behavior in build-tagged companions.

Risks: minimal, but suite declaration changes can affect all prune tests.

Test signals: indirect compile-time/suite-registration signal only.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_prune_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_prune_unix_test.go

Purpose: Unix prune coverage for networks, images, containers, and volumes, including filters from CLI flags and Docker config defaults.

Important APIs and functions: `DockerCLIPruneSuite` teardown/timeout, helper `pruneNetworkAndVerify`, `DockerSwarmSuite.TestPruneNetwork`, daemon commands, `cli.BuildCmd`, `build.WithDockerfile`, `poll.WaitOn`, checker predicates, temp config files containing `pruneFilters`, and `daemonUnixTime`.

Control flow: network prune creates unused and in-use bridge/overlay networks, attaches a container and service, prunes, and polls kept/pruned results. Image prune distinguishes dangling vs `--all`, then label filters. Container and volume prune create resources with labels, use config-level `pruneFilters`, override with CLI `label` and `label!=` filters, and verify remaining resources. Network label prune tests include equality and inequality filters.

State and persistence: creates swarm services, networks, containers, volumes, images, temp Docker configs, and daemon-specific image stores. Tests assert destructive prune commands remove only eligible resources.

Dependencies and integration points: local daemon/swarm suite, busybox, build helper, Docker config parsing, prune filter implementation, reconciliation timing, and poll utilities.

Risks: destructive by design; requires isolation from unrelated resources. Timing around service/container activity and image dangling status can be flaky if cleanup or build behavior changes.

Test signals: prune commands must respect in-use protections, dangling/all semantics, until filters, label and label-not filters, and CLI filters overriding configured prune filters.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_prune_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_ps_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_ps_test.go

Purpose: extensive `docker ps` behavior coverage for ordering, limits, filters, sizes, image display, ports, mounts, networks, labels, health, status, and link-name cleanup.

Important APIs and functions: `DockerCLIPsSuite`, `assertContainerList`, `checkPsAncestorFilterOutput`, `ExistingContainerIDs/Names`, `RemoveOutputForExistingElements`, `runSleepingContainer`, `cli.BuildCmd`, `units.FromHumanSize`, `stringid.TruncateID`, `waitForHealthStatus`, and `icmd`.

Control flow: the base test creates running/exited containers and verifies `ps`, `ps -a`, `-n`, `since`, and `before` ordering. Other tests parse `ps -s`, filter by status/health/id/name/ancestor/label/exited/created/network/ports/volume, verify image reference display after retag/commit, hide ports for stopped containers, display mounts and support volume filters, maintain deterministic order, and remove deleted container link aliases from names.

State and persistence: creates many containers, labels, healthchecks, custom images, volumes, bind mounts, networks, port mappings, commits images, and retags images. It uses current daemon state as a baseline and filters out pre-existing resources.

Dependencies and integration points: busybox, BuildKit gating for ancestor ordering, healthcheck state transitions, Docker output table formatting, image graph ancestry, mount and network inspect data, and platform-specific size behavior.

Risks: output table parsing is brittle; tests are sensitive to parallel containers despite baseline filtering; health and size checks can be timing/filesystem dependent; Windows paths and pause behavior require skips.

Test signals: `docker ps` must present correct containers in stable order, apply filters with correct AND/OR semantics, report accurate size/mount/port/network/image data, and avoid stale link names after linked containers are deleted.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_ps_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_pull_local_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_pull_local_test.go

Purpose: private-registry pull tests for alias isolation, concurrent pulls, failing pulls, ID stability, zero-layer images, manifest lists, external auth helpers, and implicit pull behavior.

Important APIs and functions: registry suite methods, `cli.BuildCmd`, `build.WithDockerfile`, `icmd.RunCommand`, `digest.FromBytes`, OCI `Index` and descriptors, filesystem writes into the registry v2 storage layout, credential helper fixture setup, and temp Docker config files.

Control flow: tests tag/push multiple aliases and ensure pulling one tag does not fetch others; run concurrent `pull -a`, failed pulls, and multi-tag pulls; compare image IDs before and after push/pull cycles; pull scratch-derived images with no layers; manually inject an OCI manifest list into the registry store; and use external credential helpers for login/push/pull with bare and scheme-qualified registry hosts. The implicit run test confirms only `latest` is pulled.

State and persistence: mutates private registry contents, local image store, temp Docker config with `credsStore`, credential helper storage, and on-disk registry blobs/revisions/tag links.

Dependencies and integration points: private registry fixture, busybox builds, OCI image-spec structs, opencontainers digest, Docker credential helper protocol, filesystem layout of distribution registry, and platform/snapshotter skips.

Risks: direct registry store mutation is tightly coupled to distribution layout; concurrent pulls expose race sensitivity; external auth tests can be affected by helper PATH/config leakage.

Test signals: pulls should be tag-scoped, concurrency-safe, failure-safe, ID-stable, capable of selecting correct manifest-list platform, compatible with external credential storage, and limited to `latest` for implicit pulls without a tag.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_pull_local_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_pull_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_pull_test.go

Purpose: Docker Hub and platform-mismatch pull tests covering output, implicit reference handling, all-tags behavior, client disconnect cancellation, reserved names, and OS manifest errors.

Important APIs and functions: `DockerCLIPullSuite`, `DockerHubPullSuite` command helpers, `digest.Parse`, regex extraction of `Digest:`, `deleteImages`, `s.MakeCmd`, stdout pipe reads, and `dockerCmdWithError`.

Control flow: central registry tests pull `hello-world`, assert default tag/library prefix output and digest validity, then inspect images. Implicit reference tests pull equivalent refs and guard against legacy fallback. Scratch pull expects reserved-name failure. All-tags pulls compare image table size and preserve the `latest` line after normalizing relative age columns. Client-disconnect test kills the pull process after first output and verifies the image is absent. Platform tests pull Linux image on Windows and Windows image on Linux expecting manifest mismatch.

State and persistence: mutates local image store and relies on cleanup via `deleteImages`; process cancellation should prevent image persistence.

Dependencies and integration points: Docker Hub/network access, registry rate limit handling, digest parser, image table formatting, OS-specific manifest resolution, and snapshotter skip for malformed fixture image.

Risks: external network/rate limits can skip or fail tests; output text is CLI-version sensitive; cancellation timing is inherently racy.

Test signals: pull output must include expected defaulting and digest information, all-tags must add tags without corrupting existing latest metadata, cancelled pulls must not leave images, and platform-incompatible manifests must be rejected clearly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_pull_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_push_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_push_test.go

Purpose: registry push coverage for normal pushes, tag handling, empty layers, concurrent pushes, cross-repository blob mounts, unauthorized behavior, and token service error handling.

Important APIs and functions: `DockerCLIPushSuite`, registry auth suites, `cli.BuildCmd`, `tar.NewWriter`, `icmd.RunCmd`, `errgroup.Group`, `reference.DigestRegexp`, `httptest.Server`, `getTestTokenService`, and token-registry setup helpers.

Control flow: tests tag busybox and push to a private registry, reject unprefixed/untagged/bad-tag pushes, push all tags and compare subsequent "Image already exists" lines, import an empty tarball and push it, push multiple tags concurrently then repull/run them, verify cross-repo layer mount output and digest stability, ensure unauthenticated pushes do not retry, and exercise token service responses for unauthorized, malformed, rate-limit, unparsable, and no-token bodies with snapshotter-specific expectations.

State and persistence: creates registry repositories/tags, local images, imported empty-layer images, token-service-backed registry configuration, and temporary HTTP servers.

Dependencies and integration points: private registry, central registry unauthorized path, distribution token auth behavior, containerd snapshotter differences, tar import, goroutine concurrency, and digest parsing.

Risks: external registry responses and token semantics can vary; concurrent push checks must avoid goroutine-unsafe assertions; output messages differ between snapshotter and classic graphdriver paths.

Test signals: pushes must upload correct manifests/layers, reject invalid refs and auth states, safely handle concurrent uploads, reuse blobs across repositories, preserve digest identity, and report token service errors without inappropriate retries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_push_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_registry_user_agent_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_registry_user_agent_test.go

Purpose: validates that registry requests carry a combined Engine and upstream Docker client User-Agent.

Important APIs and functions: `unescapeBackslashSemicolonParens`, `regexpCheckUA`, `registerUserAgentHandler`, `registry.NewMock`, `reg.RegisterHandler`, and registry suite pull command.

Control flow: the mock registry registers a `/v2/` handler that returns 404 after recording the `User-Agent` header. The test points the daemon/CLI flow at this registry, triggers an image pull, then `regexpCheckUA` splits the header into Docker engine and `UpstreamClient` portions, unescapes punctuation, and validates both with regexes.

State and persistence: starts a mock registry and captures a header string; no images are expected to persist because the handler returns unsupported/not found.

Dependencies and integration points: internal mock registry helper, HTTP header propagation through registry client stack, environment variables for test setup, and User-Agent escaping rules.

Risks: regex checks intentionally validate shape rather than exact version, but can still break on intentional UA format changes; handler returns 404, so only the first registry negotiation path is covered.

Test signals: outgoing registry requests must include an Engine UA prefix plus an escaped upstream Docker client UA after `UpstreamClient`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_registry_user_agent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_restart_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_restart_test.go

Purpose: integration tests for `docker restart`, restart policies, volumes across restarts, disconnected networks, auto-remove behavior, and restart-policy interaction with process death and user-defined networks.

Important APIs and functions: `DockerCLIRestartSuite`, `cli.DockerCmd`, `runSleepingContainer`, `cli.WaitRun`, `cli.WaitExited`, `waitInspect`, `inspectField`, `inspectFilter`, `inspectMountPoint`, `poll.WaitOn`, `os.FindProcess`, and platform skips for Windows isolation.

Control flow: tests restart stopped and running containers and poll logs for repeated output, verify volume mount count/source survives restart, restart a container disconnected from bridge, inspect `--restart=no`, `always`, and `on-failure` policies including invalid negative retry count, kill container processes to trigger restart policies, verify restart policy still works after manual restart, test links on a user-defined network after restart-policy recovery, exercise stop/start/kill with restart policies, and ensure `--rm` containers are restarted rather than removed by `docker restart`.

State and persistence: creates containers with logs, volumes, restart policies, user-defined networks, links, and process IDs. It relies on daemon state transitions and restart count persistence.

Dependencies and integration points: busybox, process signaling on the host, inspect state fields, mount persistence, network/link resolution, daemon restart manager, and OS-specific process isolation.

Risks: timing-sensitive waits around logs and restart manager; killing host PIDs is not portable to Hyper-V isolation; restart counts can be affected by slow daemon scheduling.

Test signals: restart must rerun commands/logs, preserve mounts and network configuration, correctly store restart policy settings, recover killed containers according to policy, maintain linked user-defined network resolution, and keep auto-remove containers alive through explicit restart.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_restart_test.go -->
