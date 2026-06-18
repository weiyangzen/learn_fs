# Research: subset-b-000186

Grouped research for Moby libnetwork files in `sources/cloud-native/moby/daemon/libnetwork`. Each section preserves the source path and is intended to be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/libnetwork_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/libnetwork_linux_test.go

## Purpose
Linux-only integration and behavior tests for libnetwork controller, network, endpoint, sandbox, plugin, bridge, host/null, DNS, namespace, and IPAM paths. The suite uses temporary controller data dirs plus isolated test network namespaces to exercise real Linux plumbing without sharing host state.

## Important APIs, Types, And Functions
`newController` constructs a controller with bridge configuration and default local address pools. `createTestNetwork`, `getEmptyGenericOption`, and `getPortMapping` are common helpers. Tests cover `Controller.NewNetwork`, `NewSandbox`, `Network.CreateEndpoint`, endpoint `Join`, `Leave`, `Delete`, `Network.Delete`, lookup APIs, driver plugin discovery, sandbox `SetKey`, and bridge driver operational data. `parallelTester` drives concurrent join/leave loops across host and bridge endpoints.

## Control Flow
Most tests create a controller, create one or more networks, add endpoints, optionally join endpoints into sandboxes, assert state/error behavior, then clean up with deferred deletes. Config-network tests first validate forbidden combinations, then verify config-only networks cannot be deleted while referenced. Remote-driver tests stand up an HTTP plugin mock and write plugin specs under the platform-specific plugin path. `TestExternalKey` optionally exercises the reexec helper path for setting a sandbox namespace key. `TestParallel` switches OS namespace context per goroutine and repeatedly joins/leaves endpoints to stress locking.

## State And Persistence
The tests rely on controller data dirs created by `t.TempDir` and on libnetwork datastore persistence through network/endpoint creation and deletion. Network namespace state is isolated by `netnsutils.SetupTestOSContext`. `TestResolvConf` writes origin and target `resolv.conf` files and verifies generated resolver content and file mode. Remote plugin tests mutate `specPath` and remove it after execution.

## Dependencies And Integration Points
The file integrates with the bridge, null IPAM, default IPAM, plugin registry, netlink namespace helpers, reexec, and containerd errdefs. It depends on Linux netns/netlink availability, IPv6 listenability, and bridge driver behavior.

## Risks
The tests are environment-sensitive: they require namespace operations and may depend on kernel IPv6 support, plugin spec filesystem permissions, and cleanup order. Several assertions note TODOs around error classification. Parallel join/leave tests can expose race regressions in controller, endpoint, or sandbox locking.

## Test Signals
Strong coverage exists for invalid names, duplicate endpoints, active endpoint/container protection, config-only/config-from constraints, host/null special drivers, bridge port mapping, DNS file generation, external namespace key handoff, plugin implementation validation, and null IPAM failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/libnetwork_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/libnetwork_unix_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/libnetwork_unix_test.go

## Purpose
Defines the Unix plugin specification path used by shared libnetwork tests outside Windows.

## Important APIs, Types, And Functions
The only symbol is package-level `specPath = "/etc/docker/plugins"` in `libnetwork_test`.

## Control Flow
There is no executable logic. Other tests in the same package use `specPath` when creating remote network-driver plugin specification files.

## State And Persistence
The value points at the conventional Docker plugin spec directory and causes tests to create/remove files under that path.

## Dependencies And Integration Points
Integrated with remote plugin tests such as `TestInvalidRemoteDriver` and `TestValidRemoteDriver` in the Linux test file.

## Risks
Tests using this path need permissions and must remove the directory/files they create. Because this file is build-tagged `!windows`, Windows uses a different path.

## Test Signals
No direct tests; its correctness is indirectly exercised by remote plugin discovery tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/libnetwork_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/libnetwork_windows_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/libnetwork_windows_test.go

## Purpose
Provides Windows-specific shared test constants for libnetwork tests.

## Important APIs, Types, And Functions
Defines `bridgeNetType = "nat"` and `specPath = filepath.Join(os.Getenv("programdata"), "docker", "plugins")`.

## Control Flow
There is no runtime flow beyond package initialization.

## State And Persistence
Remote plugin tests on Windows use `%ProgramData%\docker\plugins` rather than `/etc/docker/plugins`. Network tests use Windows `nat` as the bridge-equivalent network type.

## Dependencies And Integration Points
Imports `os` and `path/filepath`; integrates with shared tests that refer to `bridgeNetType` and `specPath`.

## Risks
If `programdata` is unset, `specPath` becomes a relative-ish path rooted at `docker/plugins`; tests may behave unexpectedly. The network type alias must remain aligned with Windows driver naming.

## Test Signals
Indirectly exercised by Windows libnetwork tests that create NAT networks or plugin specs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/libnetwork_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netlabel/labels.go -->
# sources/cloud-native/moby/daemon/libnetwork/netlabel/labels.go

## Purpose
Defines the reserved libnetwork label namespace and constants used to pass network, endpoint, driver, IPAM, DNS, gateway, and bridge-related options through generic option maps.

## Important APIs, Types, And Functions
Constants include `Prefix`, `DriverPrefix`, `DriverPrivatePrefix`, `GenericData`, `PortMap`, `MacAddress`, `ExposedPorts`, `DNSServers`, `EndpointName`, `EndpointSysctls`, `Ifname`, `EnableIPv4`, `EnableIPv6`, `DriverMTU`, `AdvertiseAddrNMsgs`, `AdvertiseAddrIntervalMs`, `OverlayVxlanIDList`, `Gateway`, `Internal`, `ContainerIfacePrefix`, `HostIPv4`, `HostIPv6`, and `NoProxy6To4`. `GetIfname(opts map[string]any) string` extracts `Ifname` only when the value is a string.

## Control Flow
The file is mostly declarations. `GetIfname` performs a safe type assertion against a possibly nil map and returns `""` when the label is absent or not string-typed.

## State And Persistence
There is no local mutable state. The constants form persistent API keys stored in network/endpoint generic options and serialized datastore values.

## Dependencies And Integration Points
Used heavily by `network.go`, endpoint creation, bridge/windows drivers, IPAM metadata, resolver setup, and tests. `GenericData` is especially important because driver-specific options are nested under it.

## Risks
These string constants are compatibility-sensitive. Renaming or changing semantics can break persisted networks, plugins, API clients, and drivers. `GetIfname` intentionally ignores malformed values; callers must separately validate interface names if needed.

## Test Signals
`labels_test.go` verifies nil, absent, string, empty string, nil value, and non-string `Ifname` cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netlabel/labels.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netlabel/labels_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/netlabel/labels_test.go

## Purpose
Unit tests for `netlabel.GetIfname`.

## Important APIs, Types, And Functions
`TestGetIfname` table-drives `GetIfname` against nil options, empty maps, valid string values, empty strings, nil values, and wrong types.

## Control Flow
Each table case runs as a subtest and asserts exact equality between expected and returned interface name.

## State And Persistence
No persistent state. All options are in-memory maps.

## Dependencies And Integration Points
Uses `gotest.tools/v3/assert`. It protects callers that consume generic options from panics or accidental non-string interpretation.

## Risks
Coverage is intentionally narrow; it does not validate interface name syntax or integration with endpoint option parsing.

## Test Signals
The test confirms the helper is nil-safe and type-safe, preserving empty string behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netlabel/labels_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils.go -->
# sources/cloud-native/moby/daemon/libnetwork/netutils/utils.go

## Purpose
General network utility functions for MAC generation, random interface/name generation, reverse-DNS key formatting, IPv6 listenability probing, and MAC parsing.

## Important APIs, Types, And Functions
`GenerateMACFromIP` returns a locally administered MAC with OUI-like prefix `02:42` and IPv4-derived suffix when an IP is provided. `GenerateRandomMAC` uses crypto randomness and fixes multicast/local bits. `GenerateRandomName` joins a prefix with random hex to an exact length. `ReverseIP` reverses canonical IPv4 or IPv6 text into dotted form for PTR maps. `IsV6Listenable` caches whether `[::1]:0` can be listened on. `MustParseMAC` panics on invalid MAC strings.

## Control Flow
Random functions fill byte slices via `crypto/rand`. `ReverseIP` branches on `To4`; IPv6 handling expands compressed groups, pads to four hex digits, reverses nibbles, and joins with dots. `IsV6Listenable` uses `sync.Once` to perform a single TCP6 listen probe and cache the result.

## State And Persistence
Only `v6ListenableCached` and `v6ListenableOnce` persist process-local state. Generated values are not stored here but feed endpoint/interface configuration elsewhere.

## Dependencies And Integration Points
Used by endpoint creation for random MACs, DNS service reverse maps in `network.go`, Linux interface-name generation, and bridge tests that adjust expectations based on IPv6 support.

## Risks
`rand.Read` errors in MAC generation are ignored in two helpers, which matches prior behavior but can theoretically produce low-quality values on entropy failure. `ReverseIP` assumes canonical strings and is not a full DNS `arpa` formatter. `MustParseMAC` is appropriate only for constants or tests.

## Test Signals
Linux tests cover random name boundaries, uniqueness sampling, random MAC inequality, and the Linux reserved-network helpers; reverse-IP behavior is indirectly exercised through DNS service records.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils_freebsd.go -->
# sources/cloud-native/moby/daemon/libnetwork/netutils/utils_freebsd.go

## Purpose
FreeBSD implementation of reserved-network inference.

## Important APIs, Types, And Functions
`InferReservedNetworks(v6 bool) []netip.Prefix` always returns an empty slice.

## Control Flow
No branching beyond returning an empty prefix list.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
Satisfies the cross-platform `netutils.InferReservedNetworks` API used by `Network.ipamAllocateVersion` when asking default IPAM to exclude host-reserved prefixes.

## Risks
On FreeBSD, automatic IPAM allocation does not avoid nameserver or route-derived prefixes through this helper. That is intentional in this file but can allow overlaps that Linux attempts to avoid.

## Test Signals
No direct tests in this subset; behavior is covered by compilation and IPAM callers on FreeBSD.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/netutils/utils_linux.go

## Purpose
Linux-specific helpers for inferring host-reserved address prefixes and generating non-conflicting network interface names.

## Important APIs, Types, And Functions
`InferReservedNetworks(v6 bool)` combines nameserver prefixes from `resolv.conf` with IPv4 on-link routes. `tryGetNameserversAsPrefix` parses resolver config and converts nameservers to host prefixes. `queryOnLinkRoutes` returns IPv4 link-scope route destinations from netlink. `GenerateIfaceName` tries up to three random names and checks link existence through `nlwrap`.

## Control Flow
`InferReservedNetworks` best-effort reads `resolvconf.Path()`, filters nameserver prefixes by address family, appends on-link IPv4 routes for IPv4 requests, sorts with `netiputil.PrefixCompare`, and returns the result. Interface generation loops three times, returning the first name for which netlink reports `LinkNotFoundError`.

## State And Persistence
No persistent state. It reads current host `/etc/resolv.conf` and netlink route/link state.

## Dependencies And Integration Points
Called by `network.go` IPAM allocation for non-global networks to avoid selecting subnets likely in use by the host. Depends on `resolvconf`, `ns.NlHandle`, `nlwrap`, and vishvananda netlink.

## Risks
The reservation heuristic is intentionally incomplete and best-effort; users may still need daemon `default-address-pools` tuning. Route listing failures silently produce fewer exclusions. `GenerateIfaceName` has a small retry count and can fail under repeated collisions or netlink errors.

## Test Signals
`utils_linux_test.go` verifies resolver parsing, random name constraints, random MAC generation, and route-scope filtering in an isolated test namespace.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils_linux_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/netutils/utils_linux_test.go

## Purpose
Linux unit/integration tests for `netutils` random name, resolver parsing, MAC generation, and host-reserved network inference.

## Important APIs, Types, And Functions
`TestGenerateRandomName` checks invalid and valid lengths plus duplicate avoidance across 16 samples. `TestGetNameserversAsPrefix` validates parsing comments, search lines, IPv4, IPv6, and scoped IPv6 nameservers. `TestUtilGenerateRandomMAC` checks two generated MACs differ. `TestInferReservedNetworksV4`, `createInterface`, and `addRoute` verify link-scope route inclusion.

## Control Flow
The reserved-network test creates a dummy interface in an isolated namespace, adds two link-scope routes and one universe-scope route, then asserts only link-scope prefixes are present. Resolver parsing tests call the unexported helper directly with in-memory config strings.

## State And Persistence
Netlink state is created inside a test OS context and torn down by test utilities. Other tests use only in-memory values.

## Dependencies And Integration Points
Depends on `netnsutils`, vishvananda netlink, `netiputil`, and `gotest.tools`. It protects the behavior relied on by IPAM subnet exclusion.

## Risks
Tests that touch netlink require suitable privileges/capabilities in the test environment. Random uniqueness checks are probabilistic but low-risk at the sample size used.

## Test Signals
Strong signals for parsing edge cases and route-scope semantics; no direct test for `GenerateIfaceName` collision retry behavior in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/netutils/utils_windows.go

## Purpose
Windows implementation of reserved-network inference.

## Important APIs, Types, And Functions
`InferReservedNetworks(v6 bool) []netip.Prefix` always returns an empty slice.

## Control Flow
The function unconditionally returns an empty prefix list.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
Satisfies the same API used by network IPAM allocation. Windows-specific IPAM and HNS behavior live elsewhere.

## Risks
Windows automatic IPAM does not get Linux-style host route or resolver exclusions from this helper.

## Test Signals
No direct tests in this subset; coverage is build and integration oriented.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/netutils/utils_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network.go -->
# sources/cloud-native/moby/daemon/libnetwork/network.go

## Purpose
Core implementation of libnetwork `Network`: a logical connectivity zone managed by a driver, persisted through the controller datastore, backed by IPAM allocations, endpoint lifecycle operations, service-discovery records, optional load-balancer sandbox, and distributed NetworkDB integration for swarm/dynamic networks.

## Important APIs, Types, And Functions
Key types are `EndpointWalker`, `IpamConf`, `IpamInfo`, `Network`, `NetworkOption`, and `NetworkDeleteOption`. Important methods include datastore `Key`, `Value`, `SetValue`, `CopyTo`, configuration validation/application, option setters, `Delete`, `CreateEndpoint`, endpoint walkers/lookups, service DNS record mutation, IPAM allocation/release/status, accessors, `ResolveName`, `ResolveIP`, `ResolveService`, and load-balancer sandbox creation/deletion.

## Control Flow
Network creation options populate fields and generic labels. Validation rejects invalid config-only/config-from combinations and platform-specific advertise-address settings. Endpoint creation locks by network ID, reloads the freshest network from the store, applies endpoint options, validates link-local addresses, allocates IPs, asks the network driver to create the endpoint, stores it, and rolls back IP/driver/store state on error. Deletion reloads the network, rejects active endpoints unless forced or only the LB endpoint remains, marks `inDelete`, persists, releases IPAM, leaves cluster/watch state, cleans service discovery/bindings, calls driver deletion, stops resolvers, deletes compatibility endpoint count, and removes the stored network.

## State And Persistence
`Network` implements `datastore.KVObject` with keys under `datastore.NetworkKeyPrefix`. JSON marshaling preserves persistent fields, including IPAM config/info encoded as nested JSON strings for compatibility. `dbIndex`, `dbExists`, and `persist` control datastore behavior. In-memory controller caches and `svcRecords` hold live network and DNS state. IPAM pool IDs, gateways, aux addresses, and deletion tombstone state are persisted enough for restore/delete semantics.

## Dependencies And Integration Points
Integrates with controller store/cache, driver API, IPAM registry, default IPAM, netlabel options, netutils reserved-prefix inference, networkdb peer visibility, service discovery/resolver code, OpenTelemetry tracing, errdefs, and platform methods in `network_unix.go`/`network_windows.go`.

## Risks
This file is a high-blast-radius lifecycle path. Risks include rollback gaps after datastore/driver/IPAM partial failures, stale network copies, lock-order regressions, JSON compatibility issues, nil/type assertion panics on malformed persisted data, and service DNS map races if controller locking is bypassed. IPAM release logs but continues on many failures. Load-balancer deletion notes an inconsistent-state boundary after recoverable checks.

## Test Signals
The Linux integration suite covers network/endpoint lifecycle, active endpoint/container errors, config-only/config-from, bridge/null/host behavior, DNS, plugin drivers, and parallel join/leave. Store-specific and Windows resolver tests cover adjacent behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_store.go -->
# sources/cloud-native/moby/daemon/libnetwork/network_store.go

## Purpose
Thread-safe controller helpers for persisting networks and maintaining the controller's in-memory network cache.

## Important APIs, Types, And Functions
`storeNetwork` writes a `Network` via `updateToStore` then caches it. `deleteStoredNetwork` deletes from the datastore and removes the cache entry. `cacheNetwork` inserts by network ID. `findNetworks` filters cached network pointers. `filterNetworkByConfigFrom` matches networks that depend on a named config-only network.

## Control Flow
Store/update succeeds before cache update. Delete succeeds in the datastore before cache removal. Cache access is protected by `networksMu`; `findNetworks` delegates value filtering to `maputil.FilterValues`.

## State And Persistence
Persistent state lives in the controller datastore through `updateToStore`/`deleteFromStore`; live state lives in `Controller.networks`. Returned `findNetworks` values are pointers to cached networks, not copies.

## Dependencies And Integration Points
Used by network creation, deletion, cleanup, and config-network reference checks in `network.go`. Depends on `maputil`.

## Risks
Callers must treat returned pointers carefully because the helper explicitly does not clone networks. Store/cache ordering means cache updates happen only after successful store operations.

## Test Signals
`network_store_test.go` verifies storing, filtering, deleting, pointer identity, and idempotent store update behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_store_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/network_store_test.go

## Purpose
Unit test for controller network store/cache helpers.

## Important APIs, Types, And Functions
`TestNetworkStore` constructs a controller, stores two synthetic networks, exercises `findNetworks` with no filter and `filterNetworkByConfigFrom`, deletes one network, and stores the remaining network again.

## Control Flow
The test sorts found networks by ID before comparing expected pointer identities and lengths.

## State And Persistence
Uses a temporary data dir and real controller store/cache. Synthetic `Network` objects have minimal fields (`id`, `configFrom`).

## Dependencies And Integration Points
Depends on controller construction via `New`, `config.OptionDataDir`, and `gotest.tools` assertions.

## Risks
The test focuses on cache/store helper behavior, not datastore conflict or serialization edge cases.

## Test Signals
Confirms `findNetworks` returns cached pointers, config-from filtering works, deletion removes from cache, and re-storing an existing object succeeds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_unix.go -->
# sources/cloud-native/moby/daemon/libnetwork/network_unix.go

## Purpose
Non-Windows platform implementation for network platform hooks: DNS resolver stubs, default IPAM selection, advertise-address option validation, and prune eligibility.

## Important APIs, Types, And Functions
`platformNetwork` is empty. `startResolver` and `deleteEpFromResolver` are stubs. `defaultIpamForNetworkType` returns default IPAM. `validatedAdvertiseAddrNMsgs` and `validatedAdvertiseAddrInterval` parse driver options and enforce `osl` min/max bounds. `IsPruneable` rejects predefined Docker networks.

## Control Flow
Advertise validators fetch string driver options, convert with `strconv.Atoi`, construct typed values, and return nil when unset. Prune checks call `network.IsPredefined(n.Name())`.

## State And Persistence
No local state. The validators read network driver options stored in `Network.generic`.

## Dependencies And Integration Points
Used by `network.go` validation and advertisement behavior. Integrates with `netlabel`, `osl`, default IPAM, and daemon network predefined-name helpers.

## Risks
Invalid advertise option strings prevent network creation on Unix. Stub DNS resolver behavior means Unix internal DNS setup is handled elsewhere rather than at the network platform hook.

## Test Signals
Linux integration tests exercise network creation with driver options and prune/lifecycle paths indirectly; no direct advertise-option tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/network_windows.go

## Purpose
Windows platform implementation for network compartment execution, internal DNS resolver lifecycle, HNS endpoint resolver configuration, Windows IPAM defaulting, and prune eligibility for HNS-owned networks.

## Important APIs, Types, And Functions
`platformNetwork` stores `resolverOnce` and `dnsCompartment`. `executeInCompartment` locks the OS thread and switches HNS compartment. `ExecFunc` runs a callback inside the DNS compartment. `startResolver` creates resolvers on HNS subnet gateways. `IsPruneable` protects predefined and externally owned HNS networks. `addEpToResolverImpl` and `deleteEpFromResolverImpl` configure per-source external DNS forwarding. `findHNSEp`, `findResolver`, and `defaultIpamForNetworkType` support those flows.

## Control Flow
Resolver startup ignores ICS networks, loads the HNS network by ID from driver options, iterates subnets with gateways, creates resolvers, sets the DNS compartment, retries resolver start up to three times, and stores successful resolvers. Endpoint resolver configuration finds the matching HNS endpoint by IPv4/IPv6 address, ensures internal DNS is enabled, finds the resolver by gateway, removes the resolver itself from the DNS server list, and sets external servers for endpoint source addresses. Deletion clears those per-source mappings.

## State And Persistence
State is process-local in `Network.resolver`, `resolverOnce`, and `dnsCompartment`. HNS network/endpoint state is read through `hcsshim`. Generic driver labels persist ownership and HNS IDs.

## Dependencies And Integration Points
Integrates with Microsoft HNS/hcsshim, Windows libnetwork drivers, Windows IPAM, resolver internals, netlabel generic options, and Windows daemon predefined network names.

## Risks
Compartment switching must stay on a locked OS thread and reset to compartment 0. Resolver setup depends on HNS data shape and gateway/DNS server strings. `addEpToResolver`/`deleteEpFromResolver` ignore HNS list errors, which avoids hard failures but can hide cleanup/configuration gaps. Prune logic is compatibility-sensitive for adopted HNS networks.

## Test Signals
`network_windows_test.go` validates resolver selection, external DNS extraction, IPv4/IPv6 source mappings, disabled internal DNS handling, and cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_windows_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/network_windows_test.go

## Purpose
Windows unit tests for endpoint-to-resolver external DNS configuration.

## Important APIs, Types, And Functions
`TestAddEpToResolver` builds synthetic HNS endpoints and resolvers, calls `addEpToResolverImpl`, validates resolver `ipToExtDNS` maps, then calls `deleteEpFromResolverImpl` and verifies cleanup.

## Control Flow
Table cases cover IPv4, limiting external DNS servers to three, disabled internal DNS, missing matching resolver, multiple resolvers/endpoints, and IPv6. Each case creates resolvers with requested listen addresses and checks only the expected resolver is modified.

## State And Persistence
All state is in-memory: fake `hcsshim.HNSEndpoint` values and resolver objects. Resolver external DNS maps are mutated and then cleared.

## Dependencies And Integration Points
Depends on hcsshim types, resolver internals, `netip`, `go-cmp`, and `gotest.tools`. Protects Windows DNS forwarding behavior in `network_windows.go`.

## Risks
The test does not call real HNS APIs or exercise compartment startup; it isolates pure selection/mapping logic.

## Test Signals
Strong signal for correct endpoint matching, self-resolver filtering, per-source ext DNS mapping, map cleanup, IPv6 handling, and resolver-index isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/network_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/broadcast.go -->
# sources/cloud-native/moby/daemon/libnetwork/networkdb/broadcast.go

## Purpose
Defines NetworkDB memberlist broadcast message wrappers and send helpers for network, node, and table events.

## Important APIs, Types, And Functions
`networkEventMessage`, `nodeEventMessage`, and `tableEventMessage` implement `memberlist.Broadcast`. `sendNetworkEvent`, `sendNodeEvent`, and `sendTableEvent` encode protobuf messages and enqueue them. `getBroadcasts` drains multiple transmit queues within packet limits.

## Control Flow
Network/table broadcast invalidation coalesces messages by network/node or network/table/key. Node events do not invalidate. `sendNodeEvent` waits up to five seconds for `Finished` notification when peers exist. `sendTableEvent` looks up the local joined network before queuing on its table broadcast queue. `getBroadcasts` decreases remaining packet budget after each queue.

## State And Persistence
No persistence. It mutates memberlist transmit queues and reads NetworkDB network/node state under locks.

## Dependencies And Integration Points
Called by `networkdb.go` entry/network lifecycle and by cluster join/leave logic. Uses `memberlist` and `serf` Lamport times.

## Risks
Incorrect invalidation can drop necessary events or flood queues. Node broadcast timeout can surface as join/leave failure when peers are slow. Table events for removed networks are silently skipped.

## Test Signals
No direct tests in this subset; behavior is indirectly covered by NetworkDB integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/broadcast.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/cluster.go -->
# sources/cloud-native/moby/daemon/libnetwork/networkdb/cluster.go

## Purpose
Cluster/memberlist orchestration for NetworkDB: key management, memberlist initialization, join/leave, reconnect/rejoin, periodic reaping, gossip fanout, bulk sync, and random peer sampling.

## Important APIs, Types, And Functions
Key functions include `SetKey`, `SetPrimaryKey`, `RemoveKey`, `clusterInit`, `retryJoin`, `clusterJoin`, `clusterLeave`, `triggerFunc`, `reapDeadNode`, `rejoinClusterBootStrap`, `reconnectNode`, `reapState`, `reapNetworks`, `reapTableEntries`, `gossip`, `bulkSyncTables`, `bulkSync`, `bulkSyncNode`, and `mRandomNodes`. Constants define reap/retry periods and rebroadcast queue limits.

## Control Flow
`clusterInit` builds memberlist config, installs delegates, optional keyring, creates transmit queues, starts memberlist, and launches staggered ticker goroutines. Join sends a node join event after memberlist join. Leave sends node leave, asks memberlist to leave, cancels context, stops tickers, and shuts down. Gossip periodically picks up to three random peers per joined network and sends compound table messages. Bulk sync sends all table entries for common networks over reliable TCP and optionally waits for an ACK response.

## State And Persistence
State is in-memory: memberlist instance, keyring, bootstrap IPs, failed/left node maps, timers, queue counters, random generator, table tombstone reap timers, and health/stat timestamps. No disk persistence.

## Dependencies And Integration Points
Integrates with Hashicorp memberlist, NetworkDB delegates, protobuf message encoding, node management helpers, immutable radix indexes, and Docker logging.

## Risks
Concurrency and timing dominate: ticker goroutines must stop on close, locks must not be held across slow network operations except where intended, bulk sync ACK table cleanup must not leak, and tombstone residual times must avoid premature deletion or endless rebroadcast. `mRandomNodes` fairness matters for convergence and load distribution.

## Test Signals
`cluster_test.go` property-tests `mRandomNodes` for exclusion of local node, uniqueness, sample size, permutation coverage, and approximate distribution fairness.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/cluster.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/cluster_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/networkdb/cluster_test.go

## Purpose
Property and statistical tests for NetworkDB random peer sampling.

## Important APIs, Types, And Functions
`TestMRandomNodes` exercises `mRandomNodes`. Helpers `assertUniqueElements`, `kpermutations`, and `distributionStats` validate uniqueness, possible permutation counts, and distribution metrics.

## Control Flow
The test handles empty and local-only slices, then uses rapid-generated node slices containing the local node at random positions. It checks sample length, local-node exclusion, uniqueness, small permutation coverage, repeated-sample variation, and count distribution across repeated trials.

## State And Persistence
Uses a `newNetworkDB(DefaultConfig())` instance without starting memberlist. The random generator is process-local.

## Dependencies And Integration Points
Depends on `pgregory.net/rapid`, `gotest.tools`, iterators, math/bits, and map/slice helpers. Protects `cluster.go` gossip and bulk sync peer selection.

## Risks
Statistical checks can theoretically flake, so the test tolerates some outlier trials. Saturating permutation math avoids overflow for large generated sets.

## Test Signals
Strong signal that local node is excluded, selected peers are unique, sample size is bounded, and selection is not obviously biased.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/cluster_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/debug.go -->
# sources/cloud-native/moby/daemon/libnetwork/networkdb/debug.go

## Purpose
Debug helpers for NetworkDB encryption key logging and table dumping.

## Important APIs, Types, And Functions
`logEncKeys(ctx, keys ...[]byte)` writes hex-encoded keys to the file named by `NETWORKDBKEYLOGFILE`. `DebugDumpTable(tname string)` returns a formatted dump of entries in a table prefix.

## Control Flow
Key logging no-ops when the env var is unset; otherwise it opens/creates the file mode `0600`, appends hex key lines, and logs any open/write/close errors. `DebugDumpTable` snapshots the table root under read lock and walks the prefix into a `strings.Builder`.

## State And Persistence
`logEncKeys` persists sensitive key material to a caller-selected file for debugging. `DebugDumpTable` only reads in-memory radix indexes.

## Dependencies And Integration Points
Called by key-management paths in `cluster.go`. Table dump supports diagnostics for NetworkDB tables.

## Risks
`NETWORKDBKEYLOGFILE` is intentionally dangerous: it writes encryption keys to disk and must only be used in controlled debug scenarios. Dump output may expose table values.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/delegate.go -->
# sources/cloud-native/moby/daemon/libnetwork/networkdb/delegate.go

## Purpose
Memberlist delegate implementation for NetworkDB message handling, push/pull state exchange, and event rebroadcast decisions.

## Important APIs, Types, And Functions
`delegate` implements `NodeMeta`, `NotifyMsg`, `GetBroadcasts`, `LocalState`, and `MergeRemoteState`. NetworkDB handlers include `handleNodeEvent`, `handleNetworkEvent`, `handleTableEvent`, `handleCompound`, `handleTableMessage`, `handleNodeMessage`, `handleNetworkMessage`, `handleBulkSync`, and `handleMessage`.

## Control Flow
Incoming gossip is decoded by `handleMessage` and dispatched by message type. Node/network events witness Lamport clocks, reject stale data, update membership/network maps, and rebroadcast fresh state. Table events are accepted only for locally joined, non-leaving networks where the owner is still a network participant; stale Lamport times are ignored. Watch events are synthesized from actual local state transitions rather than raw CREATE/UPDATE/DELETE type alone. Bulk sync handles compound payloads, closes ACK channels for responses, and replies to unsolicited syncs.

## State And Persistence
Mutates in-memory NetworkDB maps, radix indexes, Lamport clocks, broadcast queues, bulk sync ACK table, and local watcher broadcaster. No disk persistence.

## Dependencies And Integration Points
Integrates memberlist delegate hooks with protobuf message types, cluster bulk sync, node management helpers, and upper-layer watchers receiving `WatchEvent`.

## Risks
This is a convergence-critical path. Wrong stale checks can resurrect deleted entries or drop valid updates. Unknown delete handling is deliberately conservative and only rebroadcasts certain bulk-sync tombstones. Holding locks through watcher writes is intentional to avoid duplicate synthesized events, but any broadcaster blocking behavior would be risky. Mixed-version clusters with zero residual reap time are handled with warnings and default reap intervals.

## Test Signals
No direct tests in this subset; behavior is indirectly covered by broader NetworkDB tests outside this item.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/delegate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/event_delegate.go -->
# sources/cloud-native/moby/daemon/libnetwork/networkdb/event_delegate.go

## Purpose
Memberlist event delegate for node join/leave notifications and local watcher broadcasts.

## Important APIs, Types, And Functions
`eventDelegate` implements `NotifyJoin`, `NotifyLeave`, and `NotifyUpdate`. `broadcastNodeEvent` converts a node IP into a `NodeAddr` watch event. `nodeEventOp` distinguishes join and leave event payload direction.

## Control Flow
On join, it logs, broadcasts a node table add event, moves a known failed/left node back to active if present, purges reincarnations by IP, and inserts new active node state. On leave, it logs, broadcasts a node table delete event, finds the node, and moves active nodes to failed state; graceful left state is driven by node gossip events. `NotifyUpdate` is currently a no-op.

## State And Persistence
Mutates in-memory node state maps and `estNodes`; emits watcher events. No disk persistence.

## Dependencies And Integration Points
Used by memberlist config in `clusterInit`. Integrates with node management helpers, `NodeTable` watchers, and cluster reconnect/reap paths.

## Risks
Memberlist leave can indicate failure rather than graceful leave, so state transitions are conservative. Reincarnation handling is necessary when a new node ID appears at the same IP. Missing nodes on leave are logged but otherwise ignored.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/event_delegate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/message.go -->
# sources/cloud-native/moby/daemon/libnetwork/networkdb/message.go

## Purpose
Encoding/decoding helpers for NetworkDB protobuf gossip messages, including compound messages.

## Important APIs, Types, And Functions
Constants `compoundHeaderOverhead` and `compoundOverhead` estimate packet budget. `encodeRawMessage`, `encodeMessage`, `decodeMessage`, `makeCompoundMessage`, and `decodeCompoundMessage` wrap and unwrap `GossipMessage` and `CompoundMessage`.

## Control Flow
`encodeMessage` marshals a concrete `proto.Message`, wraps it with a `MessageType`, and marshals the envelope. Compound creation wraps each already-encoded message as a simple payload and then envelopes the compound. Decoding unmarshals the envelope, returns type/data, or splits compound payloads in order.

## State And Persistence
No state. The wire format is transient but compatibility-sensitive across cluster nodes.

## Dependencies And Integration Points
Used by broadcast senders, delegate handlers, bulk sync, gossip, and push/pull state exchange. Depends on gogo/protobuf generated NetworkDB message types.

## Risks
`encodeMessage` type-asserts `msg.(proto.Message)`, so wrong callers panic. `makeCompoundMessage` returns nil on marshal error rather than an error, relying on protobuf marshaling not to fail for expected message shapes. Wire format changes affect rolling upgrades.

## Test Signals
No direct tests in this subset; exercised indirectly by NetworkDB cluster behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/message.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.go -->
# sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.go

## Purpose
Defines the core NetworkDB data model and public API for cluster-scoped membership, per-network peer tracking, and distributed table entries used by libnetwork drivers and service discovery.

## Important APIs, Types, And Functions
Major types are `NetworkDB`, `Config`, `PeerInfo`, `PeerClusterInfo`, internal `node`, `network`, `thisNodeNetwork`, `entry`, and public `TableElem`. Public methods include `DefaultConfig`, `New`, `Join`, `Close`, `ClusterPeers`, `Peers`, `GetEntry`, `CreateEntry`, `UpdateEntry`, `GetTableByNetwork`, `DeleteEntry`, `WalkTable`, `JoinNetwork`, and `LeaveNetwork`. Internal helpers manage node/network membership and dual radix-tree entry indexes.

## Control Flow
`New` builds state and initializes memberlist. Table create/update/delete operations take the lock, validate existing state, increment Lamport table clock, update both radix indexes, unlock, and send table events. Deletes create tombstone entries with residual reap time. `JoinNetwork` increments the network clock, initializes local per-network queues, sends a network join event, records local membership, performs bulk sync with peers, and marks the network in sync. `LeaveNetwork` sends leave, removes local membership, tombstones local-owned entries, hard-deletes remote entries, broadcasts watch deletes, and marks the local network as leaving until reaped.

## State And Persistence
All state is in-memory. Entries are indexed by table path (`/table/network/key`) and network path (`/network/table/key`) in immutable radix trees. Membership is tracked in `nodes`, `failedNodes`, `leftNodes`, `networks`, `thisNodeNetworks`, and `networkNodes`. Atomic counters approximate node and per-network peer counts. Lamport clocks order node/network/table events. Tombstone `reapTime` fields control later garbage collection.

## Dependencies And Integration Points
Integrates with memberlist/serf, Docker logging, event broadcaster, immutable radix trees, string IDs, errdefs/types, and cluster/delegate files in the same package. Libnetwork `Network.Peers` uses this API for dynamic networks.

## Risks
This is concurrency-sensitive distributed state. Callers must join a network before table events are accepted. `GetEntry` intentionally panics if a nil entry exists. Path encoding uses slash-separated table/network/key strings, so keys containing slashes could confuse parsing if allowed by callers. Reap timing and Lamport comparisons must remain consistent to avoid stale resurrection or premature deletion.

## Test Signals
The subset includes random peer sampling tests; broader table, watch, and convergence behavior relies on other NetworkDB tests not listed here.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.go -->
