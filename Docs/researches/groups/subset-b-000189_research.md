# Research Report: subset-b-000189

Grouped research for the requested Moby daemon/libnetwork/logger files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/store.go -->
## sources/cloud-native/moby/daemon/libnetwork/store.go

Purpose: Implements libnetwork controller helpers for loading, updating, deleting, caching, and cleaning persisted network and endpoint objects from the configured datastore. This is the persistence bridge between in-memory `Controller`, `Network`, and `Endpoint` state and the `datastore.KVObject` backend.

Important APIs and functions: `Controller.getNetworkFromStore`, `getNetworks`, and `getNetworksFromStore` enumerate persisted `Network` objects, restore their `ctrlr` pointer, default empty scope to `scope.Local`, and optionally cache them. `Network.getEndpointFromStore` and `getEndpointsFromStore` restore endpoints and cache them in the controller. `Controller.updateToStore` wraps `PutObjectAtomic` with an OpenTelemetry span and preserves `datastore.ErrKeyModified` for optimistic-lock callers. `deleteFromStore` retries `DeleteObjectAtomic` after refreshing the object on `ErrKeyModified`. `networkCleanup` scans persisted networks marked `inDelete` and invokes `n.delete(true, true)`.

Control flow and state: List operations tolerate missing keys as empty state, but propagate or log other store errors depending on caller strictness. Objects loaded from the store are mutable in-memory objects whose controller pointer is reattached; `getNetworksFromStore` locks each network while mutating `ctrlr` and `scope`. Deletion uses a goto retry loop to converge on the latest KV revision.

Dependencies and integration points: Relies on the libnetwork datastore abstraction, `scope.Local`, controller endpoint/network caches, containerd logging, and OpenTelemetry tracing. Network cleanup integrates with network delete semantics and is sensitive to the `inDelete` persisted flag.

Risks: Retrying delete without an explicit retry limit can spin if the store is continually modified. `context.TODO()` in several paths limits cancellation observability. `getNetworks` and `getNetworksFromStore` overlap but differ in caching and error behavior, which the FIXME notes as a maintenance risk.

Test signals: The adjacent store tests validate persistence, restore, and non-persistence behavior for networks and endpoints through controller restarts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/store_linux_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/store_linux_test.go

Purpose: Linux-specific tests for the libnetwork local datastore backend and the `NetworkOptionPersist(false)` path.

Important APIs and functions: `TestBoltdbBackend` builds a temporary BoltDB path and delegates to `testLocalBackend`, exercising normal network and endpoint persistence. `TestNoPersist` creates a controller with a temp data directory, creates a host network with `NetworkOptionPersist(false)`, creates an endpoint, stops the controller, and creates a new controller over the same data directory.

Control flow and state: The test explicitly checks the store after restart by constructing `Network{id: nw.ID()}` and `Endpoint{network: nw, id: ep.ID()}` KV objects and calling `GetObject`. It expects `store.ErrKeyNotFound` and verifies `Exists()` stays false, proving both network and endpoint skipped persistent KV writes when the network is non-persistent.

Dependencies and integration points: Uses `config.OptionDataDir`, `New`, `NewNetwork`, `CreateEndpoint`, and the internal kvstore error contract. It depends on Linux datastore behavior and BoltDB availability.

Risks covered: Guards against accidentally persisting built-in or ephemeral networks when `persist=false` is requested. Also covers endpoint persistence inheritance from the parent network.

Test signals: Strong integration-style signal across controller construction, datastore reopen, network creation, endpoint creation, and object-level store reads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/store_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/store_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/store_test.go

Purpose: Shared helper test logic for validating local libnetwork datastore persistence and restore.

Important APIs and functions: `testLocalBackend` configures `OptionDataDir` and `DatastoreBucket`, creates a controller, creates a host network and endpoint, directly checks network and endpoint KV entries with `GetObject`, stops the controller, then constructs a second controller and resolves the network by ID.

Control flow and state: The test verifies both immediate store writes (`Exists()` on network and endpoint KV objects) and restart restore via `NetworkByID`. It intentionally closes and reopens the controller to prove the configured local store path and bucket are durable.

Dependencies and integration points: Exercises controller initialization, Bolt/local datastore configuration, network and endpoint creation paths, and network lookup after restore. It is called by platform-specific tests such as `TestBoltdbBackend`.

Risks covered: Prevents regressions where objects are only present in memory, the wrong bucket/data-dir is used, endpoint persistence is skipped, or restored networks fail to reattach enough controller state for lookup.

Test signals: Integration-level persistence coverage but limited to happy path; detailed stale-key/retry behavior in `store.go` is not directly exercised here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/support/Dockerfile -->
## sources/cloud-native/moby/daemon/libnetwork/support/Dockerfile

Purpose: Defines a diagnostic support container image for collecting Docker/libnetwork datapath and control-plane state inside a Docker-in-Docker environment.

Important instructions: Starts from `docker:18-dind`, adds Alpine edge repositories, installs networking/debugging tools (`util-linux`, `bridge-utils`, `iptables`, `iputils`, `iproute2`, `ipvsadm`, `conntrack-tools`, `jq`, `bash`), copies shell scripts into `/bin`, and runs `/bin/run.sh` by default.

Control flow and state: Build-time state is limited to package installation and script copy. Runtime behavior is delegated fully to `run.sh`, which may update `support.sh` before execution.

Dependencies and integration points: Depends on Docker-in-Docker, Alpine packages, and the support scripts in the same directory. The image is coupled to Docker networking internals such as `/var/run/docker/netns` and expects privileged/network access when run for diagnostics.

Risks: Base image `docker:18-dind` is old and may contain outdated tooling or package compatibility issues. Adding Alpine edge repositories can reduce reproducibility. The support image is diagnostic rather than production code, but it may need privileged host access and should be handled accordingly.

Test signals: No local tests; correctness is operational and depends on successful package install plus script behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/support/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/support/run.sh -->
## sources/cloud-native/moby/daemon/libnetwork/support/run.sh

Purpose: Runtime entrypoint for the libnetwork support container. It opportunistically refreshes `support.sh` from the upstream Docker/libnetwork repository, then executes it.

Important commands: Uses `wget -O support.sh.new` against the raw GitHub URL, replaces `support.sh` on success, marks it executable, otherwise prints a fallback message, then runs `./support.sh`.

Control flow and state: The only persisted runtime state is the local replacement of `/bin/support.sh` inside the container filesystem. A failed download leaves the baked script in place.

Dependencies and integration points: Requires network access to GitHub, `wget`, and the copied support script. It integrates with the Dockerfile `CMD`.

Risks: Pulling the latest upstream script at runtime makes diagnostics non-reproducible and can change behavior independent of the image. The URL references the historical `docker/libnetwork` repository, not necessarily the vendored Moby copy. There is no checksum or signature verification.

Test signals: No automated tests. Failure handling is simple and visible through stdout.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/support/run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/support/support.sh -->
## sources/cloud-native/moby/daemon/libnetwork/support/support.sh

Purpose: Bash diagnostic script that gathers host, overlay network, namespace, iptables, IPVS, bridge FDB, container networking, and optional SSD consistency data for Docker/libnetwork troubleshooting.

Important functions and options: Parses `-s` to enable SSD checks. Tool paths are overrideable by environment variables (`DOCKER`, `NSENTER`, `BRIDGE`, `IPTABLES`, `IPVSADM`, `IP`, `SSDBIN`, `JQ`). `echo_and_run` echoes commands before executing them. `check_ip_overlap` scans network inspect output for duplicate endpoint/VIP addresses.

Control flow and state: The script prints host iptables tables and routes, iterates overlay networks plus `ingress_sbox`, finds matching netns files in `/var/run/docker/netns`, dumps namespace addresses/routes/neighbors/bridges/iptables/IPVS, then iterates all containers and inspects network settings. Counters track processed networks, running containers, and IP overlaps, ending with a summary.

Dependencies and integration points: Integrates with Docker CLI, Linux network namespaces via `nsenter`, iptables, `iproute2`, bridge tooling, IPVS, jq JSON parsing, and optional SSD binary. It uses `docker network inspect --verbose` when available.

Risks: Requires high privileges and host namespace access. Some shell constructs are fragile: command output is evaluated in `echo_and_run`, unquoted variables may break on spaces, and `nspath[0]` array syntax is used around Docker inspect output. It prints potentially sensitive container labels/environment/network data.

Test signals: No automated tests; diagnostic value depends on command availability and host topology.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/support/support.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/types/types.go -->
## sources/cloud-native/moby/daemon/libnetwork/types/types.go

Purpose: Shared libnetwork type and utility definitions for IP families, encryption keys, QoS, transport ports, port bindings, protocol parsing, IP network manipulation, static routes, interface statistics, and libnetwork error classification.

Important APIs and types: Exposes `IPFamily` constants (`IP`, `IPv4`, `IPv6`), `EncryptionKey`, `QosPolicy`, `TransportPort`, `PortBinding`, `Protocol` constants (`ICMP`, `TCP`, `UDP`, `SCTP`), `RouteType`, `StaticRoute`, `InterfaceStatistics`, `MaskableError`, and `InternalError`. Key functions include `PortBinding.HostAddr`, `Copy`, `Equal`, `String`, `Protocol.String`, `ParseProtocol`, `GetIPNetCopy`, `GetIPNetCanonical`, `CompareIPNet`, `GetHostPartIP`, `GetBroadcastIP`, `ParseCIDR`, and error constructors wrapping `errdefs`.

Control flow and state: Most functions are pure helpers. `PortBinding.String` conditionally formats host/container IPs, IPv6 brackets, host-port ranges, and protocol suffix. IP utilities clone input bytes to avoid mutating caller-owned slices. `compareIPMask` normalizes IPv4-in-IPv6 representations and validates mask/address compatibility before host/broadcast bit operations.

Dependencies and integration points: Uses Go `net`, SCTP address support from `github.com/ishidawataru/sctp`, `slices.Clone`, and Moby `errdefs`. These types feed endpoint, driver, route, and port-mapping code throughout libnetwork.

Risks: `ParseProtocol` returns zero for unknown input, so callers must distinguish unset/invalid. `StaticRoute.Copy` assumes a non-nil receiver. IP/mask compatibility logic is subtle around IPv4-in-IPv6 forms and non-canonical masks.

Test signals: `types_test.go` covers error constructor classification, IP/mask index calculation, host/broadcast extraction across IPv4/IPv6 representations, and CIDR parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/types/types_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/types/types_test.go

Purpose: Unit tests for libnetwork common type helpers, especially error wrappers and IP/mask utilities.

Important tests: `TestErrorConstructors` verifies each public error constructor returns the expected text and containerd errdefs classification, and checks `InternalError`/`MaskableError` marker interfaces. `TestCompareIPMask` validates internal start indexes for IPv4, IPv4-in-IPv6, IPv6, and incompatible masks. `TestGetHostPartIP` and `TestGetBroadcastIP` exercise bitwise host/broadcast extraction without changing representation. `TestParseCIDR` confirms `ParseCIDR` preserves the parsed IP as supplied rather than canonicalizing to the network address.

Control flow and state: Tests are table driven and compare both success values and expected error substrings. They intentionally use mixed representations such as `net.IPv4(...)[12:]` and 16-byte masks to protect compatibility behavior.

Dependencies and integration points: Uses `gotest.tools` assertions and containerd errdefs predicates. It validates helpers used by route, address, and port-mapping code in libnetwork.

Risks covered: Prevents silent regressions in IPv4/IPv6 compatibility, accidental mutation/canonicalization expectations, and error typing. It does not cover `PortBinding.String`, `HostAddr`, `Copy`, or `StaticRoute.Copy`, leaving those utilities with weaker test signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/types/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/licensing.go -->
## sources/cloud-native/moby/daemon/licensing.go

Purpose: Populates daemon system information with the product license string.

Important API: `(*Daemon).fillLicense(v *system.Info)` sets `v.ProductLicense` to `dockerversion.DefaultProductLicense`.

Control flow and state: The function is a direct assignment with no conditional logic and no daemon state dependency beyond being a method. It mutates the passed `system.Info`.

Dependencies and integration points: Integrates with system info response construction and the `dockerversion` package as the source of the default product license.

Risks: Minimal. Any change to `dockerversion.DefaultProductLicense` flows directly into API responses. A nil `*system.Info` would panic, but callers are expected to pass a valid info object.

Test signals: `licensing_test.go` verifies the assigned field equals `dockerversion.DefaultProductLicense`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/licensing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/licensing_test.go -->
## sources/cloud-native/moby/daemon/licensing_test.go

Purpose: Unit test for daemon license population.

Important test: `TestFillLicense` constructs an empty `system.Info`, creates a minimal `Daemon`, calls `fillLicense`, and asserts `ProductLicense` equals `dockerversion.DefaultProductLicense`.

Control flow and state: No external state is used. The daemon `root` field is populated but not used by the tested method.

Dependencies and integration points: Uses `gotest.tools/assert`, `system.Info`, and `dockerversion`.

Risks covered: Protects against dropping or changing the system-info product license assignment. It does not cover nil input handling, which the implementation does not support.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/licensing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/links.go -->
## sources/cloud-native/moby/daemon/links.go

Purpose: Maintains daemon-level indexes for legacy container link relationships from parent container and alias to child container, plus reverse child-to-parent alias mappings.

Important APIs and types: `linkIndex` holds `idx map[parent]map[alias]child`, `childIdx map[child]map[parent]set(alias)`, and a mutex. `newLinkIndex`, `link`, `unlink`, `children`, `parents`, and `delete` manage the relationship graph.

Control flow and state: `link` initializes nested maps and records both forward and reverse indexes. `unlink` removes a single alias from the parent map and removes the parent entry under the child. `children` returns the stored alias-to-child map for a parent. `parents` builds a fresh alias-to-parent map for a child. `delete` removes all links where the container is parent or child and returns aliases removed from the parent side.

Dependencies and integration points: Uses `daemon/container.Container` pointers as map keys, so identity is object-pointer based. This index supports legacy `--link` behavior and environment/hosts wiring elsewhere in the daemon.

Risks: `children` returns the internal mutable map after releasing the lock, so callers can observe races or mutate index state if misused. `unlink` deletes the entire parent entry under `childIdx[child]`, not just one alias, which is correct only when each parent/child relationship should be removed wholesale. Empty nested maps are not pruned consistently.

Test signals: Separate `daemon/links/links_test.go` covers environment generation, not this index. Direct linkIndex concurrency and alias deletion behavior are not tested in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/links.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/links/links.go -->
## sources/cloud-native/moby/daemon/links/links.go

Purpose: Generates legacy Docker link environment variables describing a linked child container's address, exposed ports, name, and selected environment variables.

Important APIs and types: `Link` stores parent IP, child IP, link name, child environment, and exposed ports. `EnvVars` is the one-shot helper, `NewLink` constructs a `Link` from a `network.PortSet`, `(*Link).ToEnv` renders environment variables, and `withTCPPriority` sorts ports with TCP first, then by port/protocol.

Control flow and state: `ToEnv` derives the alias from the basename of the link name, uppercases it, and replaces hyphens with underscores. It sorts ports, emits a primary `<ALIAS>_PORT` for the first port, emits per-port URL/address/port/proto variables for every port, detects consecutive same-protocol ranges and emits START/END variables, appends `<ALIAS>_NAME`, then copies child env vars except malformed entries and `HOME`/`PATH`.

Dependencies and integration points: Uses `api/types/network.Port`, Go `maps` and `slices`, and is consumed by daemon legacy link setup to populate container startup environments.

Risks: Environment output is legacy compatibility surface and order-sensitive enough that tests sort before comparison. Alias normalization only replaces hyphens, so other unusual name characters are preserved. The first primary port depends on the TCP-priority sort.

Test signals: `links_test.go` covers naming, constructor output, child env propagation, port sorting, continuous TCP ranges, mixed protocols, and includes a benchmark for multi-port env generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/links/links.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/links/links_test.go -->
## sources/cloud-native/moby/daemon/links/links_test.go

Purpose: Unit tests and benchmark for legacy link environment generation.

Important tests: `TestLinkNaming` validates alias derivation from `/db/docker-1` to `DOCKER_1`. `TestLinkNew` checks `NewLink` field population. `TestLinkEnv` verifies child env propagation. `TestSortPorts` protects TCP-first and port/protocol ordering. `TestLinkMultipleEnv` verifies mixed TCP/UDP output and continuous TCP range START/END variables. `BenchmarkLinkMultipleEnv` measures repeated env generation.

Control flow and state: Tests sort generated environment variables before comparison because map-derived port order is not semantically relevant after rendering. `cmpopts.EquateComparable(network.Port{})` handles comparable port structs.

Dependencies and integration points: Uses `api/types/network.PortSet` and `network.MustParsePort`. The tested output is consumed by container runtime environment setup for links.

Risks covered: Prevents regressions in legacy env names, skipped reserved child env vars, port range compaction, and protocol ordering. It does not cover malformed child env entries explicitly or unusual alias characters beyond hyphen replacement.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/links/links_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/list.go -->
## sources/cloud-native/moby/daemon/list.go

Purpose: Implements daemon container listing (`docker ps`) by validating filters, building a reusable filter context, selecting candidate containers, applying list predicates, refreshing image display data, optionally computing sizes, and returning ordered `container.Summary` values.

Important APIs and types: `acceptedPsFilterTags` defines allowed filters. `iterationAction` controls include/exclude/stop. `(*Daemon).List` returns all registered containers. `listContext` stores folded filters: names, images, exited codes, before/since snapshots, task/is-task flags, publish/expose maps, and original `ContainerListOptions`. Key functions are `(*Daemon).Containers`, `filterByNameIDMatches`, `foldFilter`, `idOrNameFilter`, `portOp`, `includeContainerInList`, `refreshImage`, and `populateImageFilterByParents`.

Control flow and state: `Containers` validates filters, snapshots the container view, folds filters, optionally narrows candidates by name/ID, sorts by creation time, and launches an errgroup with `log2(n)` worker limit. Each included container is assigned a stable result index before goroutine processing, preserving output order. `includeContainerInList` implements before/since, stopped/all/limit, name/id, task, label, isolation, exit/status/health, volume, ancestor, network, publish, and expose checks. `refreshImage` replaces stale image references with the original image ID if the reference no longer resolves to the stored image ID.

Dependencies and integration points: Integrates with `container.ViewDB`, daemon name reservation, image service (`GetImage`, `Children`, layer size), filters package, API container/network types, platform-specific `excludeByIsolation`, and errdefs.

Risks: Filter semantics are broad and order-dependent. `filter.idx` is mutated while goroutines run, but only the main loop mutates it; results use a mutex. Ancestor expansion recursively walks image children and can be expensive. Size calculation can dominate latency and returns errors for individual container layer failures. Name/ID shortcut must remain consistent with full-list filtering.

Test signals: `list_test.go` covers invalid filter validation, creation-order listing across several counts, name filter slash/regex behavior, and limit semantics. Many filters are not covered in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/list_test.go -->
## sources/cloud-native/moby/daemon/list_test.go

Purpose: Unit tests for core container listing behavior using an in-memory container view database.

Important helpers and tests: `TestMain` creates a temporary root. `setupContainerWithName` constructs a base container with a UUID, digest-derived image ID, running state, host config, image config, creation time, saves it to `containersReplica`, and reserves its name. `containerListContainsName` searches summary names. `TestContainerList` checks empty through 100-container cases and descending creation order. `TestContainerList_InvalidFilter` rejects unknown filters. `TestContainerList_NameFilter` validates regex and exact names with and without slash prefixes. `TestContainerList_LimitFilter` checks zero, negative, smaller, equal, and larger limits.

Control flow and state: Tests replace the view DB per case to avoid cross-contamination. Creation timestamps are separated by milliseconds so sort order is deterministic.

Dependencies and integration points: Exercises `Daemon.Containers`, `container.NewViewDB`, name reservation, filter parsing, and image refresh prerequisites. It avoids real image service calls by setting `Config.Image` equal to `ImageID`.

Risks covered: Protects ordering, name-filter slash normalization, accepted filter validation, and limit handling. Remaining filters such as ancestor, before/since, health, volumes, ports, network, size, and isolation are not exercised here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/list_unix.go -->
## sources/cloud-native/moby/daemon/list_unix.go

Purpose: Provides the Unix implementation of isolation filtering for container listing.

Important API: `excludeByIsolation(container *container.Snapshot, ctx *listContext) iterationAction` always returns `includeContainer`.

Control flow and state: No state is read. The function is a platform stub because container isolation is a Windows-only concept in this daemon path.

Dependencies and integration points: Built for Linux and FreeBSD. Called from `includeContainerInList` after label checks.

Risks: Minimal; the main risk is expectation mismatch if an isolation filter is accepted on Unix but effectively ignored by this stub. The accepted filter set includes `isolation`, so behavior differs by platform.

Test signals: No direct Unix-specific test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/list_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/list_windows.go -->
## sources/cloud-native/moby/daemon/list_windows.go

Purpose: Implements Windows-specific container isolation filtering for `docker ps`.

Important API: `excludeByIsolation(container *container.Snapshot, ctx *listContext)` lowercases `container.HostConfig.Isolation`, defaults empty isolation to `default`, and matches it against the user filter.

Control flow and state: If the filter does not match the normalized isolation value, returns `excludeContainer`; otherwise returns `includeContainer`.

Dependencies and integration points: Called by shared `includeContainerInList`. Depends on Windows `HostConfig.Isolation` semantics and the filters package matching behavior.

Risks: Assumes `HostConfig` is non-nil for snapshots reaching this code. Empty isolation is surfaced as `default`, which is API-visible filtering behavior. Case normalization is one-way and depends on filter matching expectations.

Test signals: No direct Windows-specific tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/list_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/listeners/group_unix.go -->
## sources/cloud-native/moby/daemon/listeners/group_unix.go

Purpose: Resolves the Unix socket group used when creating Docker daemon Unix sockets.

Important API: `lookupGID(name string) (int, error)` first attempts `usergroup.LookupGroup`, then accepts a numeric string via `strconv.Atoi`, otherwise returns `-1` and an error. `defaultSocketGroup` is `docker`.

Control flow and state: This is a pure lookup helper. It allows both group names and numeric GIDs.

Dependencies and integration points: Used by Unix listener initialization before `sockets.NewUnixSocket`. Depends on daemon internal `usergroup` lookup and the host group database.

Risks: If the configured group does not exist and is not numeric, socket creation falls back or fails depending on caller handling. Numeric strings bypass group existence validation.

Test signals: No direct tests in this subset; behavior is indirectly relevant to listener setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/listeners/group_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/listeners/listeners_linux.go -->
## sources/cloud-native/moby/daemon/listeners/listeners_linux.go

Purpose: Initializes Linux daemon API listeners for systemd socket activation, TCP, and Unix socket protocols.

Important APIs: `Init(proto, addr, socketGroup string, tlsConfig *tls.Config)` dispatches on `fd`, `tcp`, and `unix`. `listenFD(addr string, tlsConfig *tls.Config)` loads systemd-activated listeners, optionally wraps TLS listeners, returns all listeners for empty or `*`, or selects one listener by numeric fd address.

Control flow and state: TCP uses `sockets.NewTCPSocket`. Unix resolves a GID with `lookupGID`; if the default group is missing it logs a warning and falls back to current GID, but non-default explicit group errors are returned. After `sockets.NewUnixSocket`, it asks `homedir.StickRuntimeDirContents` to protect sockets under `XDG_RUNTIME_DIR`. `listenFD` validates listener presence, parses fd numbers relative to systemd fd 3, closes unselected listeners, and returns the requested one.

Dependencies and integration points: Integrates with `go-systemd/activation`, Docker go-connections sockets, TLS, homedir runtime-dir sticky-bit handling, and containerd logging.

Risks: fd selection error messages are critical for service startup diagnosis. Closing unselected activated listeners must not close the selected fd. Unix socket permissions depend on group lookup and filesystem behavior.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/listeners/listeners_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/listeners/listeners_windows.go -->
## sources/cloud-native/moby/daemon/listeners/listeners_windows.go

Purpose: Initializes Windows daemon API listeners for TCP, named pipes, and Unix sockets.

Important APIs: `Init(proto, addr, socketGroup string, tlsConfig *tls.Config)` supports `tcp`, `npipe`, and `unix`. `getSecurityDescriptor(additionalUsersAndGroups []string)` builds an SDDL DACL from default administrator/system permissions plus optional user/group read-write ACEs.

Control flow and state: `socketGroup` is treated as a comma-separated list of additional users/groups. TCP uses `sockets.NewTCPSocket`. Named pipes resolve SIDs and call `winio.ListenPipe` with message mode and 64 KiB buffers. Unix sockets use Windows go-connections support with the additional principals. Unsupported protocols return a Windows-specific error.

Dependencies and integration points: Uses `Microsoft/go-winio`, Docker go-connections sockets, Windows SID lookup, and TLS for TCP.

Risks: Security descriptor construction is access-control sensitive. Any unresolvable extra principal fails listener creation. Named pipe message mode is required for `CloseWrite`, so changing it can break HTTP over npipe semantics.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/listeners/listeners_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logdrivers_linux.go -->
## sources/cloud-native/moby/daemon/logdrivers_linux.go

Purpose: Registers Linux daemon logging drivers by blank-importing their packages for init-time factory registration.

Important imports: Registers `awslogs`, `fluentd`, `gcplogs`, `gelf`, `journald`, `jsonfilelog`, `local`, `loggerutils/cache`, `splunk`, and `syslog`.

Control flow and state: All behavior occurs through imported package `init` functions, which call `logger.RegisterLogDriver` and often `RegisterLogOptValidator`.

Dependencies and integration points: This file connects build tags/platform selection to the global logger factory. Linux includes journald and omits Windows ETW.

Risks: Removing or build-tagging an import changes available daemon log drivers. Init panics in driver registration would fail daemon startup.

Test signals: Driver-specific tests validate many imported packages; this registration aggregator has no direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logdrivers_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logdrivers_windows.go -->
## sources/cloud-native/moby/daemon/logdrivers_windows.go

Purpose: Registers Windows daemon logging drivers by blank-importing their packages for init-time factory registration.

Important imports: Registers `awslogs`, `etwlogs`, `fluentd`, `gcplogs`, `gelf`, `jsonfilelog`, `loggerutils/cache`, `splunk`, and `syslog`.

Control flow and state: Behavior is entirely side-effect imports. Windows includes ETW logs and omits journald/local from this list.

Dependencies and integration points: Bridges platform build selection to `logger` factory availability. Each driver package must successfully register at init time.

Risks: Registration availability differences are platform API behavior. Duplicate registration panics in any driver init would affect daemon startup.

Test signals: No direct tests for this aggregation file in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logdrivers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/adapter.go -->
## sources/cloud-native/moby/daemon/logger/adapter.go

Purpose: Adapts external logging plugins to the daemon `Logger` and optional `LogReader` interfaces using the internal logdriver protobuf framing.

Important APIs and types: `pluginAdapter` stores plugin identity, FIFO path, capabilities, `Info`, mutex, encoder, stream, and reusable `logdriver.LogEntry` buffer. `Log` encodes `Message` fields and partial-log metadata into the shared buffer. `Close` calls plugin `StopLogging`, closes the FIFO stream, removes the FIFO path, and releases the plugin. `pluginAdapterWithRead.ReadLogs` reads plugin logs through `plugin.ReadLogs`, decodes entries, filters by `Since`/`Until`, and streams messages through a `LogWatcher`.

Control flow and state: `Log` serializes writes with a mutex and returns messages to the pool only on successful encode. Partial metadata is translated into protobuf metadata. `ReadLogs` runs in a goroutine, closes `watcher.Msg` on exit, stops on context cancellation, EOF, decode errors, until cutoff, or consumer-gone signal.

Dependencies and integration points: Uses internal `logdriver` encoder/decoder, plugin lifecycle APIs, `plugingetter.Release`, FIFO filesystem cleanup, and log watchers used by `docker logs`.

Risks: Shared buffer correctness depends on mutex discipline and reset after encode. If plugin `StopLogging` succeeds but stream close/remove fails, errors are logged but close continues. Read filtering is defensive but plugin-side filtering is still expected.

Test signals: `adapter_test.go` uses an in-memory mock plugin to verify log encode/decode, follow mode, live messages, closure, and message equality.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/adapter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/adapter_test.go -->
## sources/cloud-native/moby/daemon/logger/adapter_test.go

Purpose: Tests plugin logger adapter read/write behavior using a mock logging plugin.

Important fixtures and tests: `mockLoggingPlugin` uses an `io.Pipe`, protobuf delimited reader, log slice, condition variable, and optional error. `StartLogging` decodes entries into memory. `ReadLogs` re-encodes stored entries, optionally waits in follow mode, and closes on plugin error or non-follow exhaustion. `newMockPluginAdapter` builds a `pluginAdapterWithRead`. `TestAdapterReadLogs` logs two messages, reads them without follow, reads them with follow, logs a live third message, closes the logger, and checks watcher closure.

Control flow and state: The condition variable synchronizes producer/consumer tests. `waitLen` blocks until plugin ingestion sees expected messages. Test helper `testMessageEqual` compares line bytes, nanosecond timestamp, and source.

Dependencies and integration points: Exercises internal `logdriver` protobuf framing and the `Logger`/`LogReader` contract.

Risks covered: Validates follow mode, EOF closure, live append delivery, message timestamp preservation, and clean close propagation. Does not cover partial-log metadata or error paths from plugin `ReadLogs`/decode.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/adapter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/awslogs/cloudwatchlogs.go -->
## sources/cloud-native/moby/daemon/logger/awslogs/cloudwatchlogs.go

Purpose: Implements the `awslogs` Docker log driver, forwarding container logs to Amazon CloudWatch Logs with stream creation, optional log group creation, non-blocking queueing, multiline aggregation, UTF-8-safe splitting, batch limits, sequence-token handling, and option validation.

Important APIs and types: `logStream` is the logger and `logger.SizedLogger`, storing group/stream names, create flags, flush interval, multiline regex, CloudWatch client, message queue, closed flag, and sequence token. `logStreamConfig` holds parsed options. `api` abstracts CloudWatch calls for tests. Key functions are `New`, `newStreamConfig`, `parseMultilineOptions`, `newAWSLogsClient`, `Log`, `Close`, `create`, `createLogGroup`, `createLogStream`, `collectBatch`, `processEvent`, `effectiveLen`, `findValidSplit`, `publishBatch`, `putLogEvents`, `ValidateLogOpt`, `unwrapEvents`, and `eventBatch` methods.

Control flow and state: `New` parses config, builds an AWS SDK client, creates a bounded message queue, creates the log stream synchronously unless `mode=non-blocking`, and starts `collectBatch`. In non-blocking mode stream creation retries with exponential backoff until success or close. `Log` enqueues messages and maps closed queue errors to `errClosed`. `collectBatch` waits for creation, ticks at the configured flush interval, buffers multiline events until a new pattern match, max size, age expiry, negative timestamp age, queue close, or tick, and publishes accumulated batches. `processEvent` splits oversized messages without breaking valid UTF-8 and respects CloudWatch per-event and per-put byte overhead. `publishBatch` sorts events by timestamp then insert order, uses the current sequence token, retries on invalid sequence token, and advances token on success or already-accepted responses.

Dependencies and integration points: Uses AWS SDK v2 CloudWatch Logs, IMDS region detection, optional credentials endpoint provider, Docker-specific user agent, optional EMF log format request header, `loggerutils.MessageQueue`, logger tag parsing, containerd logging, and Moby version metadata.

Risks: CloudWatch API constraints are strict, so size accounting and UTF-8 normalization are high-risk. Global variables (`newTicker`, `newRegionFinder`, `newSDKEndpoint`) aid testing but must be restored carefully in tests. `context.TODO()` limits cancellation. Non-blocking creation can delay visibility of configuration errors. Multiline buffering can hold logs until flush and must not exceed memory/age expectations.

Test signals: The large test file covers config parsing, client headers/endpoints/credential endpoint/region discovery, create success/error/idempotence, blocking queue behavior, publish sequencing, multiline and ticker batching, max event/put constraints, duplicate timestamp ordering, UTF-8 and binary splitting, option validation, and benchmarks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/awslogs/cloudwatchlogs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/awslogs/cloudwatchlogs_test.go -->
## sources/cloud-native/moby/daemon/logger/awslogs/cloudwatchlogs_test.go

Purpose: Comprehensive unit and benchmark coverage for the `awslogs` CloudWatch log driver.

Important fixtures and tests: Defines constants, `logGenerator`, `testEventBatch`, mock CloudWatch client usage, and many focused tests. Config tests cover defaults, invalid booleans/intervals/buffer sizes, multiline regex parsing, datetime format conversion, log format conflicts, create-stream validation, and custom log tag generation. Client tests verify Docker user-agent header, EMF header, custom endpoint routing, IMDS region fallback, and credential endpoint signing. Creation tests cover stream creation, skipped stream creation, group creation after not-found, generic errors, and already-exists success.

Control flow and state: Queue tests assert blocking and closed behavior. Publish tests assert sequence-token use, invalid-token retry, data-already-accepted handling, and preserving token on generic errors. Batch tests replace `newTicker` with a channel to deterministically trigger flushes and validate simple, ticker, multiline, close, max event count, max total bytes, duplicate timestamps, long line, emoji, and invalid-binary scenarios.

Dependencies and integration points: Uses AWS SDK types, httptest servers for SDK middleware, loggerutils queues, and test mocks from `cwlogsiface_mock_test.go`.

Risks covered: Strongly protects CloudWatch limits, ordering, UTF-8-safe splitting, nonblocking queue mechanics, API sequence handling, option validation, and AWS client customization. Some tests mutate package globals such as `newTicker`, `newRegionFinder`, and `newSDKEndpoint`, so isolation is important when adding parallel tests.

Test signals: This is one of the strongest test files in the subset and includes benchmarks for batch collection and event unwrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/awslogs/cloudwatchlogs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/awslogs/cwlogsiface_mock_test.go -->
## sources/cloud-native/moby/daemon/logger/awslogs/cwlogsiface_mock_test.go

Purpose: Test doubles for the `awslogs` driver, including a mock CloudWatch Logs API client and mock IMDS region client.

Important APIs and types: `mockClient` has function fields for `CreateLogGroup`, `CreateLogStream`, and `PutLogEvents`. Its methods delegate to those fields, while `PutLogEvents` first calls `checkPutLogEventsConstraints`. `checkPutLogEventsConstraints` enforces maximum bytes per event and maximum bytes per put. `mockmetadataclient`, `regionResult`, `newMockMetadataClient`, and `GetRegion` simulate IMDS region lookup through a buffered channel.

Control flow and state: Tests configure function fields per scenario. Constraint checking makes mocked `PutLogEvents` fail when implementation batching violates CloudWatch size rules, raising test fidelity beyond a simple stub.

Dependencies and integration points: Mirrors the production `api` and `regionFinder` interfaces from `cloudwatchlogs.go` and uses AWS SDK input/output types.

Risks covered: Helps catch regressions in event splitting and batch size accounting even when tests do not hit real AWS. Function fields must be set before use; missing fields would panic.

Test signals: Supports most of the awslogs test suite and provides deterministic API behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/awslogs/cwlogsiface_mock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/awslogs/register.go -->
## sources/cloud-native/moby/daemon/logger/awslogs/register.go

Purpose: Registers the `awslogs` log driver and its option validator with the global logger factory at package initialization.

Important API: `init` calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, ValidateLogOpt)`, panicking on either error.

Control flow and state: Package init mutates global logger factory registries. Duplicate registration or registration failure aborts startup/tests through panic.

Dependencies and integration points: Activated by platform `logdrivers_*.go` blank imports or direct imports. Connects the implementation in `cloudwatchlogs.go` to daemon log-driver selection.

Risks: Global init side effects make import order and duplicate names important. `name` must stay aligned with user-facing driver name.

Test signals: Covered indirectly whenever awslogs is imported and option validation or driver lookup is exercised.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/awslogs/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/copier.go -->
## sources/cloud-native/moby/daemon/logger/copier.go

Purpose: Copies container stdout/stderr streams into a `Logger`, assigning timestamps, source names, and partial-log metadata for overlong or unterminated lines.

Important APIs and types: `Copier` holds source readers, destination logger, wait group, close once, and closed channel. `NewCopier`, `Run`, `copySrc`, `Wait`, and `Close` form the lifecycle. Constants `readSize` and `defaultBufSize` define incremental read size and default log line buffer.

Control flow and state: `Run` launches one goroutine per source. `copySrc` chooses buffer size from `SizedLogger` when available, reads up to `readSize` increments, scans buffered bytes for newlines, emits complete messages with current UTC timestamp, and emits partial messages when EOF or full buffer occurs without newline. Partial messages share a generated ID and timestamp across chunks, increment ordinal, and mark the final chunk on the next newline. `Close` closes the shared channel once and causes copy loops to return.

Dependencies and integration points: Uses logger message pooling, `SizedLogger`, daemon backend `PartialLogMetaData`, string ID generation, metrics counters (`totalPartialLogs`, `logReadsFailedCount`), and log driver error reporting.

Risks: Partial metadata logic is subtle around EOF, full buffers, and newline finalization. Destination `Log` errors require returning messages to the pool to avoid leaks. Slow or blocking loggers can stall copy goroutines until `Close` is observed between operations.

Test signals: `copier_test.go` covers normal streams, long lines, slow logger close, sized loggers and ring wrappers, partial metadata, and benchmarks across message sizes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/copier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/copier_test.go -->
## sources/cloud-native/moby/daemon/logger/copier_test.go

Purpose: Unit tests and benchmarks for copying log streams into logger implementations.

Important fixtures and tests: `TestLoggerJSON` and `TestSizedLoggerJSON` encode messages as JSON with mutex protection. `TestCopier` validates stdout/stderr complete and trailing lines. `TestCopierLongLines` verifies long lines are split at default buffer size. `TestCopierSlow` ensures `Close` lets a slow logger exit promptly. `TestCopierWithSized` checks `SizedLogger.BufSize` directly and through ring logger wrapping. `TestCopierWithPartial` verifies partial IDs, timestamps, ordinals, and final flags across stdout/stderr long chunks while normal messages lack partial metadata. Benchmarks run copier with piped data from 64 bytes to 256 KiB.

Control flow and state: Tests use JSON decoding to inspect emitted `Message` values and explicit timeout channels to catch hangs. Partial tests track expected IDs/timestamps per source.

Dependencies and integration points: Exercises `NewCopier`, logger interfaces, partial-log backend metadata, ring logger buffer sizing, and message source attribution.

Risks covered: Protects against hangs, incorrect source assignment, broken buffer sizing, and partial log metadata regressions. Timing-based tests must balance speed with avoiding flakes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/copier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/etwlogs/etwlogs_windows.go -->
## sources/cloud-native/moby/daemon/logger/etwlogs/etwlogs_windows.go

Purpose: Windows-only log driver that emits container logs as Event Tracing for Windows (ETW) provider events.

Important APIs and types: `etwLogs` stores container/image names and IDs. `New` registers the ETW provider and returns a logger. `Log` builds a formatted event string and calls `EventWriteString`. `Close` unregisters the provider. Helper functions include `createLogMessage`, `registerETWProvider`, `unregisterETWProvider`, `callEventRegister`, `callEventWriteString`, and `callEventUnregister`.

Control flow and state: Global `providerHandle`, `refCount`, and mutex manage provider lifetime across logger instances. Registration occurs only when refcount transitions from zero; unregister occurs when it drops to one and `EventUnregister` succeeds. `Log` rejects calls if the provider handle is invalid, returns messages to the pool after formatting, and writes UTF-16 strings through Windows syscalls.

Dependencies and integration points: Uses `Advapi32.dll` lazy procs, `golang.org/x/sys/windows`, a fixed provider GUID, containerd logging, and the logger factory via separate registration file.

Risks: Refcount/provider global state is concurrency-sensitive. `unregisterETWProvider` does not report unregister failure. Event payload is a formatted string, so escaping/field boundaries depend on content. Windows syscall errors are surfaced as numeric return codes.

Test signals: No tests in this subset; behavior depends on Windows runtime APIs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/etwlogs/etwlogs_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/etwlogs/register.go -->
## sources/cloud-native/moby/daemon/logger/etwlogs/register.go

Purpose: Windows-only registration hook for the ETW logging driver.

Important API: `init` calls `logger.RegisterLogDriver(name, New)` and panics on error.

Control flow and state: Mutates the global logger factory during package initialization.

Dependencies and integration points: Activated by Windows log driver blank imports and exposes `etwlogs` as a selectable daemon logging driver.

Risks: Duplicate name registration or init failure panics. There is no option validator registered because the ETW driver has no driver-specific options in this file set.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/etwlogs/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/factory.go -->
## sources/cloud-native/moby/daemon/logger/factory.go

Purpose: Provides the global logging driver registry, plugin fallback lookup, option-validator registry, and built-in logging option validation.

Important APIs and types: `Creator`, `LogOptValidator`, `logdriverFactory`, `ListDrivers`, `RegisterLogDriver`, `RegisterLogOptValidator`, `GetLogDriver`, and `ValidateLogOpts`. The factory stores creators and validators under a mutex. `builtInLogOpts` reserves `mode` and `max-buffer-size`.

Control flow and state: Registration rejects duplicate driver or validator names. Driver existence checks consult the registry and, if missing, ask plugin lookup when `pluginGetter` is available. `GetLogDriver` returns a registered creator or acquires a plugin-backed creator. `ValidateLogOpts` allows `none`, validates blocking/non-blocking mode, ensures `max-buffer-size` is only used with non-blocking mode and parses as bytes, validates external/plugin options, checks driver registration/plugin availability, strips built-in options, then invokes any driver-specific validator.

Dependencies and integration points: Integrates with `containertypes.LogMode`, Docker units parser, plugin getter lifecycle, external logging validation, and all driver `register.go` files.

Risks: Global mutable registry is process-wide; tests adding drivers must avoid duplicate names. Plugin lookup during validation can return errors unrelated to built-in validation. Built-in option stripping means driver validators do not see `mode`/`max-buffer-size`.

Test signals: Driver-specific tests indirectly exercise validator registration and `ValidateLogOpts`; no focused factory tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/factory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/fluentd/fluentd.go -->
## sources/cloud-native/moby/daemon/logger/fluentd/fluentd.go

Purpose: Implements the `fluentd` logging driver, sending container logs to Fluentd over TCP, TLS, or Unix socket with configurable buffering, retries, acknowledgements, async behavior, precision, and read/write timeouts.

Important APIs and types: `fluentd` stores tag, container ID/name, `*fluent.Fluent` writer, and extra attributes. `location` represents parsed address. Public functions are `New`, `Log`, `Close`, `Name`, `ValidateLogOpt`, with internal `parseConfig` and `parseAddress`.

Control flow and state: `New` parses options into `fluent.Config`, parses the log tag, extracts extra attributes, creates a Fluent writer, and stores container metadata. `Log` builds a map with container ID/name, source, log line, extra attributes, and optional partial-log metadata, then posts it with the message timestamp. Messages are returned to the pool only after successful post. `parseConfig` handles address, buffer size, retry wait, max retries, async and async reconnect interval bounds, sub-second precision, request ack, and non-negative read/write timeouts. `parseAddress` defaults empty/host-only addresses to TCP `127.0.0.1:24224`, supports `tcp`, `tls`, and `unix`, validates port range and path rules.

Dependencies and integration points: Uses `fluent-logger-golang`, Docker units parser, logger tag and extra attribute helpers, errdefs invalid-parameter wrapping, and containerd logging.

Risks: Fluentd writer can buffer and retry, so delivery semantics depend on its library. Timeouts are important to avoid indefinite blocking on unhealthy connections. Address parsing must handle IPv6, Unix paths, invalid schemes, and port bounds. Partial metadata fields are stringified and must remain compatible with downstream consumers.

Test signals: `fluentd_test.go` validates reconnect interval bounds, extensive address parsing, write timeout validation, and integration-style read/write timeout effectiveness against Unix socket test servers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/fluentd/fluentd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/fluentd/fluentd_test.go -->
## sources/cloud-native/moby/daemon/logger/fluentd/fluentd_test.go

Purpose: Tests Fluentd driver option validation, address parsing, and read/write timeout behavior.

Important tests: `TestValidateLogOptReconnectInterval` rejects negative, unitless, below-minimum, and above-maximum async reconnect intervals and accepts `100ms` and `10s`. `TestValidateLogOptAddress` table-tests defaults, IPv4, IPv6, hostnames, TCP/TLS schemes, unsupported schemes, invalid ports, forbidden paths, and Unix socket paths. `TestValidateWriteTimeoutDuration` validates non-negative duration parsing. `TestReadWriteTimeoutsAreEffective` starts a Unix socket server and verifies write timeout against a blackhole connection and read timeout when request-ack is enabled but no ack is returned.

Control flow and state: Timeout tests skip Windows, use a context with 10 second deadline, create temporary Unix sockets, disable async behavior, limit retries/buffer size, and close loggers through `closeLoggerWithContext` to avoid hanging on library mutexes.

Dependencies and integration points: Uses real Fluentd client behavior over Unix sockets, logger `Info`, and helper connection handlers.

Risks covered: Protects against invalid address acceptance and indefinite blocking on broken downstream Fluentd endpoints. Timing and socket tests can be platform-sensitive, hence the Windows skip.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/fluentd/fluentd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/fluentd/register.go -->
## sources/cloud-native/moby/daemon/logger/fluentd/register.go

Purpose: Registers the Fluentd log driver and its option validator with the global logger factory.

Important API: `init` calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, ValidateLogOpt)`.

Control flow and state: Registration occurs as an import side effect and panics on failure.

Dependencies and integration points: Activated by platform log driver blank imports, enabling user selection of `fluentd` and validation of `fluentd-*` options.

Risks: Duplicate registration or mismatched `name` causes init-time panic or driver lookup failure.

Test signals: Indirectly covered by Fluentd tests and daemon logdriver imports.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/fluentd/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gcplogs/gcplogging.go -->
## sources/cloud-native/moby/daemon/logger/gcplogs/gcplogging.go

Purpose: Implements the `gcplogs` driver, sending container logs to Google Cloud Logging with optional GCE instance metadata and container metadata payloads.

Important APIs and types: `gcplogs` holds a `logging.Client`, `logging.Logger`, optional `instanceInfo`, and `containerInfo`. Payload type `dockerLogEntry` contains instance, container, and message. `initGCP` performs one-time metadata detection. Public functions are `New`, `ValidateLogOpts`, `Log`, `Close`, and `Name`.

Control flow and state: `initGCP` calls `metadata.OnGCE` once and, on GCE, populates package globals for project, zone, instance name, and ID. `New` selects project from metadata or `gcp-project`, requires a project, creates a Cloud Logging client, builds a GCE monitored resource when instance data is known or explicitly configured, pings the service, extracts extra attributes, builds container metadata, optionally includes command when `gcp-log-cmd=true`, and installs an `OnError` handler. Overflow errors increment a global atomic dropped-log counter and log first/every-1000th drop. `Log` sends an async logging entry with timestamp and structured payload, then returns the message to the pool. `Close` flushes and closes the client.

Dependencies and integration points: Uses `cloud.google.com/go/logging`, compute metadata service, Google monitored resource protobufs, logger extra attributes, containerd logging, and application default credentials.

Risks: `Log` returns nil after enqueueing to Cloud Logging; later delivery errors are asynchronous via `OnError`. Metadata globals are process-wide and only initialized once. Project discovery and client `Ping` can fail at driver construction. High log volume can drop entries through client overflow.

Test signals: No direct tests in this subset; registration file connects validator/driver to the factory.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gcplogs/gcplogging.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gcplogs/register.go -->
## sources/cloud-native/moby/daemon/logger/gcplogs/register.go

Purpose: Registers the Google Cloud Logging driver and validator with the daemon logger factory.

Important API: `init` registers `name` with `New` and registers `ValidateLogOpts`, panicking on errors.

Control flow and state: Import side effect mutates the global factory registry and validator map.

Dependencies and integration points: Activated by platform logdriver blank imports; enables `gcplogs` selection and option validation.

Risks: Init-time panics on duplicate registration. Driver availability depends on this blank import being included for the target platform.

Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gcplogs/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gelf/gelf.go -->
## sources/cloud-native/moby/daemon/logger/gelf/gelf.go

Purpose: Implements the GELF log driver for Graylog-compatible endpoints over UDP or TCP, including address validation, UDP compression options, TCP reconnect options, metadata enrichment, and message emission.

Important APIs and types: `gelfLogger` stores a GELF writer, logger info, hostname, and pre-marshaled extra metadata. `New`, `newGELFTCPWriter`, `newGELFUDPWriter`, `Log`, `Close`, `Name`, `ValidateLogOpt`, and `parseAddress` form the driver.

Control flow and state: `New` requires `gelf-address`, resolves host metadata, parses tag, builds `_container_id`, `_container_name`, `_image_id`, `_image_name`, `_command`, `_tag`, `_created`, and extra attributes prefixed with `_`, marshals them once, then constructs a UDP or TCP writer. UDP supports compression type (`gzip`, `zlib`, `none`) and level. TCP supports max reconnect and reconnect delay. `Log` ignores empty lines, maps stderr to GELF error level, converts timestamp to fractional seconds, includes raw extras, writes through the GELF writer, and returns the message to the pool on success.

Dependencies and integration points: Uses `Graylog2/go-gelf`, logger tag and extra attribute helpers, hostname lookup, JSON metadata, and Docker logger factory registration.

Risks: `New` has a default branch that would return a logger with nil writer for unsupported schemes, but `parseAddress` prevents unsupported schemes before the switch. TCP reconnect delay is parsed as an integer and assigned directly as `time.Duration`, so the unit is nanoseconds unless the upstream writer interprets it differently. Metadata is pre-marshaled, so per-message dynamic metadata is not supported.

Test signals: `gelf_test.go` covers address parsing, TCP/UDP option validation, writer construction, and logger construction for both protocols on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gelf/gelf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gelf/gelf_test.go -->
## sources/cloud-native/moby/daemon/logger/gelf/gelf_test.go

Purpose: Linux tests for GELF address parsing, option validation, writer creation, and driver construction.

Important tests: `TestParseAddress` requires protocol and TCP/UDP schemes. `TestTCPValidateLogOpt` accepts TCP basics and reconnect options, rejects compression on TCP, negative/non-integer reconnect values, and TCP-only options on UDP. `TestUDPValidateLogOpt` accepts UDP compression and common tag/label/env options, rejects invalid compression level/type, unknown options, and missing address. `TestNewGELFTCPWriter` creates a local TCP listener and verifies writer setup/close. `TestNewGELFUDPWriter`, `TestNewTCP`, and `TestNewUDP` validate construction and close paths.

Control flow and state: TCP tests bind port 0 to avoid fixed-port conflicts and use the listener address in config. UDP tests use `127.0.0.1:0`.

Dependencies and integration points: Exercises `Graylog2/go-gelf` writers and logger `Info` option handling. The file is Linux-build-tagged, likely because SCTP/network stack or external writer behavior differs elsewhere.

Risks covered: Protects user-facing validation for protocol-specific options and basic endpoint construction. It does not assert actual GELF message payload content from `Log`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gelf/gelf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gelf/register.go -->
## sources/cloud-native/moby/daemon/logger/gelf/register.go

Purpose: Registers the GELF log driver and option validator with the global logger factory.

Important API: `init` calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, ValidateLogOpt)`.

Control flow and state: Import side effect mutates process-global factory state and panics if registration fails.

Dependencies and integration points: Activated by platform logdriver blank imports, enabling `gelf` as a daemon logging driver.

Risks: Duplicate name registration or missing blank import changes driver availability.

Test signals: Indirectly covered by GELF tests and logdriver platform imports.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/logger/gelf/register.go -->
