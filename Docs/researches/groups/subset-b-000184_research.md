# Research Group: subset-b-000184

This grouped report covers Moby libnetwork endpoint lifecycle, Windows HNS drivers, driver registries, host-file/firewall helpers, and internal utility packages. Each section is marker-wrapped for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/overlay_windows.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/overlay_windows.go

Purpose: registers the Windows overlay network driver and restores already-existing HNS overlay networks into Docker's in-memory overlay tables at daemon startup. Important APIs/types are `NetworkType`, `driver`, `Register`, `restoreHNSNetworks`, `convertToOverlayNetwork`, `Type`, and `IsBuiltIn`; the driver also satisfies `driverapi.TableWatcher` elsewhere in the package.

Control flow: `Register` constructs a driver with an empty `networkTable`, calls `restoreHNSNetworks`, then registers the driver with global data/connectivity scopes. Restore lists HNS networks, filters `Type == "overlay"`, converts subnets, VSID/VNI policy, gateway IP, HNS ID, and management IP into overlay `network`/`subnet` structs, and inserts them via `addNetwork`.

State and persistence: this file treats HNS as the startup source for existing Windows overlay networks; endpoint restore is intentionally skipped because networks are expected to be recreated on restart. Dependencies include `hcsshim`, `driverapi`, `scope`, JSON policy parsing, and libnetwork overlay tables. Risks include silently continuing past malformed subnet CIDRs and VSID policies defaulting if not present. Test signal is indirect; behavior depends on HNS integration rather than local unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/overlay_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/peerdb_windows.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/peerdb_windows.go

Purpose: wires Windows overlay peer discovery events into HNS remote endpoint records. Important functions are `peerAdd` and `peerDelete`; they are invoked by overlay/networkdb peer synchronization paths to add or remove remote container attachment information.

Control flow: both functions validate network and endpoint IDs, look up the overlay network in the driver's table, and no-op if the network is absent. `peerAdd` creates an `hcsshim.HNSEndpoint` marked `IsRemoteEndpoint`, attaches a PA policy carrying the VTEP/provider address, converts the peer IP to `/32`, removes any stale endpoint with that address, posts the HNS endpoint, then stores an overlay `endpoint` with `remote: true` and the returned HNS profile ID. `peerDelete` finds the endpoint, calls HNS delete by `profileID`, and removes it from the network table.

State and dependencies: state is split between HNS remote endpoints and the overlay network's endpoint table. Dependencies are `hcsshim`, JSON policy encoding, `types.ParseCIDR`, and package-local `validateID`/network lookup. Risks include errors when deleting unknown peers, reliance on HNS-generated IDs, and lack of IPv6 remote peer handling. Test coverage is not local in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/overlay/peerdb_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/port_mapping.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/port_mapping.go

Purpose: manages Windows host port allocation bookkeeping for HNS endpoint NAT policies, mainly for `l2bridge` and `l2tunnel` networks. Important APIs are `AllocatePorts`, internal `allocatePort`, `ReleasePorts`, and `maxAllocatePortAttempts`.

Control flow: `AllocatePorts` walks requested `types.PortBinding` values, allocates each through `portallocator.OSAllocator`, and rolls back all previously allocated bindings if any later allocation fails. `allocatePort` normalizes nil host IP to `0.0.0.0`, fills `HostPortEnd` for non-ranges, retries dynamic host-port allocation up to ten times, but does not retry explicit ports. Successful allocation collapses the host port range to the selected port. `ReleasePorts` attempts every deallocation and returns a joined error so cleanup is best-effort but visible.

State and dependencies: state lives in the supplied allocator, not in this file; operational HNS policies are built later in `windows.go`. Dependencies include `portallocator`, libnetwork `types`, and logging. Risks include Windows' lack of host-IP support, retry churn for ephemeral allocations, and errors during cleanup leaving allocator state inconsistent. Test signal is indirect through Windows driver endpoint creation tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/port_mapping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows.go

Purpose: implements builtin Windows local network drivers as a shim over Host Network Service for `transparent`, `l2bridge`, `l2tunnel`, `nat`, `internal`, `private`, and `ics`. Important types are `networkConfiguration`, `endpointOption`, `EndpointConnectivity`, `hnsEndpoint`, `hnsNetwork`, and `driver`; important APIs include `RegisterBuiltinLocalDrivers`, `CreateNetwork`, `DeleteNetwork`, `CreateEndpoint`, `DeleteEndpoint`, `EndpointOperInfo`, `Join`, and `Leave`.

Control flow: driver registration creates one `driver` per HNS network type, restores stored state, and registers local-scoped capabilities. `CreateNetwork` parses generic labels, rejects disabled IPv4 and IPv6 subnets, creates in-memory network state, posts an HNS network when no HNS ID was adopted, updates IPAM with HNS-returned gateway/subnets, deletes stale HNS endpoints for adopted networks, and persists config. `CreateEndpoint` parses endpoint options/connectivity, optionally allocates ports, converts NAT/QOS/outbound-NAT/ICC/DNS policies into HNS JSON, posts an endpoint, copies returned IP/MAC/gateway into libnetwork interface data, stores endpoint state, and rolls back ports on error. `Join` hot-attaches the endpoint to the container/sandbox key, sets gateway information, and disables libnetwork gateway service; `Leave` hot-detaches.

State/dependencies: HNS is operational authority; Docker stores network and endpoint metadata in `datastore.Store` and memory maps guarded by mutexes. Dependencies include `hcsshim`, `driverapi`, `netlabel`, `types`, `portallocator`, and OpenTelemetry. Risks include type assertions on generic data, Windows limitations for IPv6/host-IP/ranges, HNS error-string matching, and partial persistence failures after endpoint creation. Tests in `windows_test.go` are skipped integration-style NAT/transparent paths with a fake `InterfaceInfo`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows_store.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows_store.go

Purpose: provides datastore serialization, restore, update, and delete behavior for the Windows HNS driver. Important constants are `windowsPrefix` and `windowsEndpointPrefix`; important APIs are `initStore`, `populateNetworks`, `populateEndpoints`, `storeUpdate`, `storeDelete`, and `datastore.KVObject` implementations for `networkConfiguration` and `hnsEndpoint`.

Control flow: initialization first lists stored network configs for the driver's HNS type and recreates in-memory `hnsNetwork` records, then lists stored endpoints, attaches each to its restored network, and deletes stale endpoint records whose network is gone. Store updates use `PutObjectAtomic`; deletes call `DeleteObject`. JSON methods encode stable fields such as HNS IDs, names, VLAN/VSID, DNS, endpoint profile IDs, MAC/IP/gateway, endpoint options, connectivity, and port mappings.

State and dependencies: this is the persistence bridge between libnetwork state and the generic datastore, while HNS remains the runtime source. Dependencies include JSON, `datastore`, `types.ParseCIDR`, and logging. Risks include unchecked type assertions during unmarshal, older saved records missing newer fields, and persistence warnings that do not always abort runtime changes. Test signal comes from Windows driver tests using a temp store.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows_test.go

Purpose: defines Windows-only integration-style tests and a fake endpoint interface for the HNS driver. Important pieces are `testNetwork`, `TestNAT`, `TestTransparent`, and `testEndpoint`, which implements `driverapi.InterfaceInfo`, `InterfaceNameInfo`, and join-info gateway methods.

Control flow: `testNetwork` creates a temp-store driver, configures an IPv4 IPAM pool/gateway, creates a Windows network, creates then deletes one endpoint, and finally deletes the network. The fake endpoint returns optional address/MAC data and rejects attempts to overwrite an already-present MAC or set nil IP/MAC values. Gateway, static route, namespace, and created-in-container hooks are no-ops except `DisableGatewayService`, which records the call.

State/dependencies: tests depend on `hcsshim` being usable on a Windows host, the libnetwork driver API, `types.ParseCIDR`, and `storeutils.NewTempStore`. Both NAT and transparent tests are skipped because they do not work in CI and historically did not run. Risk signal: real HNS behavior is under-tested by default; these tests mostly document expected driver lifecycle and fake-interface contracts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/windows/windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers_linux.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers_linux.go

Purpose: registers Linux network drivers and portmapper implementations during libnetwork controller initialization. Important APIs are `registerNetworkDrivers` and `registerPortMappers`.

Control flow: `registerNetworkDrivers` iterates fixed driver registrations for bridge, host, ipvlan, macvlan, null, and overlay, passing the datastore, bridge config, and portmapper registry where needed. It wraps each registration failure with the driver type for diagnostics. `registerPortMappers` optionally creates a rootlesskit port driver client when rootless mode is enabled, registers the NAT portmapper with that client, then registers the routed portmapper.

State/dependencies: this file is glue rather than stateful logic; it populates the driver registry and portmapper registry used by network creation and endpoint external connectivity. Dependencies include Linux driver packages, `drvregistry`, rootlesskit client support, and config data. Risks include startup failure if any builtin registration or rootless port driver initialization fails. Test signal is indirect through controller startup and driver package tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers_unsupported.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers_unsupported.go

Purpose: provides a non-Linux, non-Windows build-tag fallback for network driver registration. Its only API is `registerNetworkDrivers`, which returns nil and registers no builtin drivers on unsupported platforms.

Control flow: there is no runtime control flow beyond the no-op function. It exists to satisfy shared controller build requirements when neither Linux nor Windows driver implementations are compiled.

State/dependencies: the function signature references controller config, `driverapi.Registerer`, datastore, and portmapper registry types from the package imports expected in sibling platform files. As shown, the file relies on package-level imports not present in this snippet, so build correctness depends on the actual source context and build tags. Risk is platform skew: unsupported targets get no drivers and may fail later if callers assume at least the null driver exists. Test signal is only compile-time coverage on unsupported build targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers_windows.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drivers_windows.go

Purpose: registers Windows libnetwork drivers and provides a Windows no-op portmapper registration hook. Important APIs are `registerNetworkDrivers` and `registerPortMappers`.

Control flow: network registration first installs the null and Windows overlay drivers, wrapping errors with the network type, then delegates to `windows.RegisterBuiltinLocalDrivers` to register HNS-backed local drivers such as NAT and transparent. `registerPortMappers` returns nil because Windows port mapping is handled inside HNS endpoint policy creation rather than Linux-style pluggable portmappers.

State/dependencies: this file mutates the shared driver registry during controller startup and passes the datastore to Windows local drivers for persistence. Dependencies include `drivers/null`, `drivers/windows`, `drivers/windows/overlay`, `drvregistry`, and controller config types. Risks include HNS restore/register failures aborting startup and the lack of a portmapper registry on Windows requiring all port binding behavior to stay in the Windows driver. Test signal is indirect through Windows driver registration and skipped HNS tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/ipams.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/ipams.go

Purpose: implements the in-process registry for IPAM drivers. Important types and APIs are `ipamDriver`, `IPAMs`, `IPAM`, `RegisterIpamDriverWithCapabilities`, `RegisterIpamDriver`, `IPAMWalkFunc`, and `WalkIPAMs`.

Control flow: registration rejects blank names, locks the registry, blocks replacing an existing builtin driver, lazily initializes the map, and stores driver plus capability. Lookup returns the registered driver/capability pair for a name, with zero values if absent. Walking snapshots registered entries while locked, releases the lock, then invokes the callback until it returns true.

State/dependencies: state is an internal map protected by a mutex; it is not persisted. Dependencies are `ipamapi` and libnetwork `types` for forbidden duplicate errors. Integration points include builtin IPAM registration and controller address allocation. Risks include nil driver values being accepted, absent lookups returning nil without error, and iteration order being map-randomized. Tests verify default/null/windows registration visibility via `WalkIPAMs`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/ipams.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/ipams_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/ipams_test.go

Purpose: validates the IPAM driver registry after builtin IPAM registration. Important helper/API usage is `getNewIPAMs`, `IPAM`, and `WalkIPAMs`.

Control flow: `getNewIPAMs` constructs a zero-value registry and calls `ipams.Register`. The `IPAM` subtest checks that the `default` driver and capability can be retrieved. The `WalkIPAMs` subtest collects driver names through the callback, sorts them for deterministic comparison, and expects `default` and `null`, plus `windows` on Windows builds.

State/dependencies: tests rely on the registry's zero value being usable and on builtin IPAM registration being platform-sensitive. Dependencies include `runtime.GOOS`, `ipams.Register`, `ipamapi`, and `gotest.tools` assertions. Risks covered include missing builtin registration and callback walking. Risks not covered include duplicate registration, blank names, nil driver values, and concurrent registry use.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/ipams_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/networks.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/networks.go

Purpose: implements the registry for network drivers and network allocators. Important types and APIs are `Networks`, `DriverWalkFunc`, `RegisterDriver`, `Driver`, `WalkDrivers`, `RegisterNetworkAllocator`, `NetworkAllocator`, and `HasDriverOrNwAllocator`.

Control flow: registration rejects blank network types, checks whether an existing builtin driver/allocator blocks replacement, optionally forwards registration to `Notify`, then lazily initializes and updates the local map under lock. Lookup returns stored values without error if absent. Walking snapshots drivers under lock, releases the lock, and invokes the callback until it asks to stop.

State/dependencies: state is mutex-protected maps for drivers and allocators plus optional cascading registration via `Notify`; it is not persisted. Dependencies are `driverapi` for driver, allocator, capability, and active-registration errors. Integration points include platform driver registration and plugin forwarding. Risks include nil driver registration, race windows between duplicate check and final store if another goroutine registers the same key, and randomized walk order. Tests cover basic registration, duplicate builtin rejection, lookup, and walking.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/networks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/networks_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/networks_test.go

Purpose: verifies core behavior of the network driver registry with a builtin mock driver. Important test fixtures are `mockDriverName`, `mockDriver`, `mockDriverCaps`, and `md`.

Control flow: subtests register the mock driver, attempt duplicate builtin registration, look up the stored driver/capability, and walk registered drivers to observe the inserted name. The mock implements `Type` and `IsBuiltIn`, which is important because duplicate rejection only blocks existing builtin drivers.

State/dependencies: tests use zero-value `Networks`, the `driverapi.Driver` interface, local-scope capability, and `gotest.tools` assertions. They confirm lazy map initialization and capability preservation. Gaps include no coverage for allocator registration, `Notify` forwarding, blank names, non-builtin replacement, nil driver handling, or concurrent registration. The duplicate test asserts only that an error exists, not the exact `ErrActiveRegistration` type.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/networks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/portmappers.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/portmappers.go

Purpose: provides a small registry for libnetwork portmapper backends. Important APIs are `PortMappers.Register` and `PortMappers.Get`.

Control flow: `Register` rejects blank names, checks for duplicate names, lazily creates the driver map, and stores the given `portmapperapi.PortMapper`. Unlike network/IPAM registries, there is no mutex and no builtin override logic. `Get` returns the mapped implementation or an error naming the missing portmapper.

State/dependencies: state is an in-memory map from name to portmapper implementation. Dependencies include `portmapperapi` and standard errors/formatting. Integration points include Linux `registerPortMappers`, bridge/external connectivity code that asks for NAT or routed mappers, and rootless port driver setup. Risks include no synchronization, nil portmapper acceptance, and duplicate errors being generic strings. Tests cover normal register/get, blank names, duplicates, and missing lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/portmappers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/portmappers_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/portmappers_test.go

Purpose: tests the simple portmapper registry contract. Important fixture is `fakePortMapper`, which implements `MapPorts` and `UnmapPorts` with no-op success.

Control flow: registration tests cover a successful registration, blank-name rejection, and duplicate-name rejection. Lookup tests register a fake mapper and assert `Get` returns the same value, then check that a missing name returns an error containing `portmapper nonexistent not found`.

State/dependencies: tests rely on the zero-value `PortMappers` map being lazily initialized. Dependencies include `portmapperapi`, context, and `gotest.tools`. The suite validates the main happy/error paths but does not cover nil mapper values, concurrent access, or integration with Linux NAT/routed portmapper registration. Because `PortMappers` has no lock, these tests are single-threaded and do not exercise data-race risks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drvregistry/portmappers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint.go

Purpose: implements libnetwork endpoint identity, persistence, options, sandbox join/leave/delete lifecycle, DNS/service updates, external connectivity programming, IPAM assignment/release, and cleanup of stale local endpoints. Important types/APIs include `Endpoint`, `EndpointOption`, `ByNetworkType`, JSON/KV methods, `Join`, `sbJoin`, `updateExternalConnectivity`, `Leave`, `sbLeave`, `Delete`, endpoint option constructors, `assignAddress`, `releaseIPAddresses`, `releaseIPv6Address`, and `Controller.cleanupLocalEndpoints`.

Control flow: endpoints are loaded from network/controller store before join/leave/delete to avoid stale in-memory copies. `Join` validates the sandbox, serializes join/leave with `sb.joinLeaveMu`, marks sandbox ownership, invokes the network driver `Join`, adds the endpoint to the sandbox, populates OS network resources when possible, recalculates gateway endpoints, programs external connectivity through `driverapi.ExtConner`, and persists the endpoint. Error defers roll back driver join and sandbox attachment. `Leave` revokes external connectivity, driver attachment, service/resolver state, OS resources, gateway/default route state, host entries, store state, and cluster driver info. `Delete` refuses active endpoints unless forced, removes store state first with rollback if non-forced driver deletion fails, updates service records, calls driver deletion, and releases IPAM addresses.

State/dependencies: endpoint state is mutex-protected and persisted as datastore KV JSON under network endpoint keys; it also references controller caches, sandbox maps, IPAM pools, driver APIs, service discovery, and `/etc/hosts`. Risks include many unchecked JSON unmarshal migrations, complex rollback gaps, force-mode masking, store/driver partial failure, and gateway race sensitivity. Tests in this subset cover network-type sorting and host entry behavior; most lifecycle behavior is integration-tested elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_cnt.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_cnt.go

Purpose: preserves the legacy `endpointCnt` datastore object for downgrade compatibility after endpoint reference counting became unused in v28.1. Important pieces are `endpointCnt`, `epCntKeyPrefix`, and its `datastore.KVObject` methods.

Control flow: methods expose key construction under `endpoint_count/<network-id>`, JSON value encoding/decoding, index/existence tracking, skip behavior based on `Network.persist`, object construction, and copy semantics. There is no active counter mutation logic here; `Count` is only serialized if old state is read or rewritten.

State/dependencies: state is a count plus datastore index/existence flags guarded by an embedded mutex and tied to a `Network` pointer. Dependencies include JSON and `datastore`. Integration point is backward/downgrade compatibility with previously persisted endpoint count records. Risks include `SetValue` unmarshalling into `&ec`, which changes a local pointer target rather than fields as a typical value receiver would, but this is legacy-only. Test signal is not local; behavior is mostly retained to avoid breaking old data.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_cnt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_info.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_info.go

Purpose: defines endpoint operational metadata interfaces and the driver-facing `EndpointInterface`/join-info APIs used during endpoint creation and sandbox join. Important APIs include `EndpointInfo`, `EndpointInterface` JSON/copy/accessors, `Info`, `Iface`, `SetMacAddress`, `SetIPAddress`, `SetNames`, `InterfaceName`, `AddStaticRoute`, `AddTableEntry`, gateway getters/setters, `ForceGw4/6`, `hasGatewayOrDefaultRoute`, `retrieveFromStore`, and join-info JSON methods.

Control flow: drivers receive endpoint interface/join info through interfaces and populate MAC, IPv4/IPv6, routes, gateways, table entries, and gateway-service flags. `Info` hydrates from store when needed, then returns the sandbox's active endpoint copy if joined. Address setters reject nil and existing values; getters clone most mutable fields. Gateway/default-route detection checks explicit gateways, forced gateway flags, join static routes, and interface connected routes. JSON marshaling stores `netip.Prefix` forms for addresses and routes, plus join gateway strings and static routes.

State/dependencies: endpoint interface/join state is embedded in persisted endpoint JSON and active sandbox endpoint objects. Dependencies include `driverapi`, `types`, `netiputil`, slices, and JSON. Risks include some returned slices not deeply cloned (`LinkLocalAddresses`, static routes), unchecked join-info unmarshal assumptions, and nil `joinInfo` sensitivity when drivers call setters outside join. Tests are indirect through endpoint lifecycle and driver tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_info_unix.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_info_unix.go

Purpose: provides Unix implementation of `Endpoint.DriverInfo`, returning operational endpoint data directly from the endpoint's network driver. Important API is `DriverInfo`.

Control flow: the method retrieves the latest endpoint from the store, retrieves the latest network, obtains the driver with strict lookup, and returns `driver.EndpointOperInfo(networkID, endpointID)`. Errors are wrapped to identify whether endpoint hydration, network lookup, or driver lookup failed.

State/dependencies: this is a read-only bridge from persisted endpoint/network state to driver operational data. Dependencies include platform build tags, network driver interface, and endpoint store helpers. Integration points include Docker inspect-style queries needing MAC/port/driver-specific data. Risks include returning stale or failed data if the store is out of sync with the driver, and requiring the driver to be present even for historical endpoint records. Test signal is indirect; Windows has a separate gateway-info merge path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_info_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_info_windows.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_info_windows.go

Purpose: provides Windows-specific `Endpoint.DriverInfo`, augmenting endpoint driver operational data with gateway-network endpoint information. Important API is `DriverInfo`.

Control flow: the method retrieves the latest endpoint, checks whether it is attached to a sandbox, finds the sandbox gateway-network endpoint if different from the target endpoint, recursively retrieves that gateway endpoint's driver info, then retrieves the target network driver and endpoint operational info. If endpoint info exists, it injects `GW_INFO`; otherwise it returns gateway info alone.

State/dependencies: this is read-only but depends on persisted endpoint/network state, controller sandbox maps, and driver `EndpointOperInfo`. It integrates with Windows NAT/gateway behavior where gateway endpoint data may be needed for inspect/operational consumers. Risks include recursive driver-info failures, nil `GW_INFO` values, and reliance on sandbox state being present for gateway merge. Test coverage is indirect; no local unit test covers this merge behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_info_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_store.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_store.go

Purpose: centralizes endpoint persistence and the controller's in-memory endpoint cache. Important APIs are `Controller.storeEndpoint`, `deleteStoredEndpoint`, `cacheEndpoint`, `findEndpoints`, and `filterEndpointByNetworkId`.

Control flow: `storeEndpoint` writes the endpoint to the datastore through `updateToStore`, then caches the same pointer. `deleteStoredEndpoint` deletes from store, then removes the cache entry under `endpointsMu`. `findEndpoints` locks the cache and returns values filtered through `maputil.FilterValues`; the comment warns callers that returned endpoint pointers are not copies. `filterEndpointByNetworkId` matches endpoints whose network pointer has the expected ID.

State/dependencies: persistent state is in the controller datastore, while runtime state is `Controller.endpoints` guarded by `endpointsMu`. Dependencies include `context` and internal `maputil`. Risks include cache/store divergence if store updates fail, callers mutating returned pointers without endpoint locks, and filter functions dereferencing partially hydrated endpoints. Tests validate insert/find/delete/cache behavior with a temp controller datastore.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_store_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_store_test.go

Purpose: tests controller endpoint store/cache synchronization. Important test is `TestEndpointStore`.

Control flow: the test creates a controller with a temp data directory, stores two endpoints belonging to a synthetic network, finds endpoints by network ID, sorts them for deterministic assertions, deletes one endpoint, confirms only the second remains, and stores the second again. It asserts that found endpoints are the same pointers, not copies.

State/dependencies: the test exercises real controller datastore plumbing via `New`, `storeEndpoint`, `findEndpoints`, and `deleteStoredEndpoint`, plus in-memory cache behavior. Dependencies include `config.OptionDataDir`, slices sorting, and `gotest.tools` comparisons. Risks covered include cache deletion and idempotent-ish re-store of an existing endpoint. Gaps include datastore failure paths, concurrent access, and filter behavior with nil networks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_test.go

Purpose: tests endpoint sorting by network type for DNS/service name resolution priority. Important test is `TestSortByNetworkType`.

Control flow: the test creates local, dynamic overlay-like, and ingress networks, wraps each in an endpoint, sorts using `ByNetworkType`, and compares the endpoint names to the expected ordering: dynamic networks first, ingress next, local networks last. It uses `sort.Sort`, so equal categories may preserve no guaranteed stable order beyond this sample.

State/dependencies: no persistence or external network driver state is involved; the test directly sets `Network.dynamic` and `Network.ingress` fields. Integration point is `Sandbox.ResolveName` behavior in swarm mode, where endpoints attached to user overlay, ingress, and local gateway networks should prefer user overlay VIP/IPs. Risk covered is priority regression; gaps include stable sorting behavior, nil network handling, and mixed service aliases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_unix_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/endpoint_unix_test.go

Purpose: Unix-only integration test for `/etc/hosts` entries generated when a sandbox joins a dual-stack network endpoint. Important test is `TestHostsEntries`.

Control flow: the test sets up an isolated OS network namespace context, creates an IPv4/IPv6-enabled test network with default IPAM pools, creates a temp hosts file, creates a sandbox with that hosts path and hostname `somehost.example.com`, creates and joins an endpoint, then reads the hosts file. Expected content includes default IPv4/IPv6 localhost lines plus the endpoint's IPv4 and IPv6 addresses mapped to FQDN and short hostname. It then deletes the sandbox and asserts controller sandbox cleanup.

State/dependencies: dependencies include default IPAM, `getTestEnv`, netns test utilities, sandbox hosts-file options, and real file IO. Risks covered include host entry ordering and dual-stack address inclusion. Gaps include multi-network deletion behavior and Windows behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/endpoint_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/error.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/error.go

Purpose: defines libnetwork-specific error types with marker methods used by containerd/libnetwork error classification. Important types are `ErrNoSuchNetwork`, `NetworkNameError`, `ActiveEndpointsError`, `ActiveContainerError`, and `ManagerRedirectError`.

Control flow: each type formats a user-facing error string and exposes marker methods such as `NotFound`, `Conflict`, `Forbidden`, or `Maskable`. These marker methods let shared error helpers classify errors without wrapping every return site in a common struct. `ActiveEndpointsError` joins active endpoint names in its message; `ActiveContainerError` reports endpoint name and ID; `ManagerRedirectError` tells callers to redirect manager-only requests.

State/dependencies: there is no persistent state. Dependencies are standard formatting and string joining. Integration points include endpoint/network delete paths and swarm manager redirection. Risks are mostly API compatibility: marker method changes would alter HTTP/API error classification. Tests verify selected marker interfaces using containerd errdefs and libnetwork `types.MaskableError`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/errors_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/errors_test.go

Purpose: validates that libnetwork error types satisfy expected classification interfaces. Important test is `TestErrorInterfaces`.

Control flow: the test checks `ManagerRedirectError` against `types.MaskableError`, `ErrNoSuchNetwork` against `cerrdefs.IsNotFound`, and `ActiveContainerError` against `cerrdefs.IsPermissionDenied`. It uses type switches and `gotest.tools` error-type comparisons.

State/dependencies: no runtime state is involved. Dependencies include containerd errdefs, libnetwork `types`, and assertion helpers. The test guards API behavior expected by higher-level error handling and API response mapping. Gaps include `NetworkNameError` conflict classification and `ActiveEndpointsError` forbidden classification, although their marker methods are present in the source. It also does not verify error message text.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/etchosts/etchosts.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/etchosts/etchosts.go

Purpose: builds and mutates container `/etc/hosts` files. Important types/APIs are `Record`, `Record.WriteTo`, `Build`, `BuildNoIPv6`, `Add`, `Delete`, `Update`, `Drop`, and the internal path-level lock cache.

Control flow: `Build` writes default IPv4/IPv6 localhost records plus extras; `BuildNoIPv6` filters IPv6 extra records and writes IPv4-only defaults. `Add` appends formatted records. `Delete` scans the file, preserves comments and nonmatching lines, and removes only records whose parsed address and exact tab-suffixed host string match. `Update` uses a hostname-bound regular expression to replace IPs for matching hostnames without matching prefixed names. All mutating operations acquire a lock unique to the file path.

State/dependencies: state is only the lock map; persistence is the hosts file itself. Dependencies include `netip`, `bufio`, regex, and OS file IO. Risks include lock map growth unless `Drop` is called, exact tab-format dependency in deletion, and regex behavior around unusual hostnames. Tests cover default ordering, no-IPv6 filtering, update/delete prefix regressions, empty inputs, newline handling, concurrency, and fuzzing `Add`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/etchosts/etchosts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/etchosts/etchosts_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/etchosts/etchosts_test.go

Purpose: tests host-file build, append, delete, update, concurrency, and benchmark behavior for the `etchosts` package. Important tests include `TestBuildDefault`, `TestBuildNoIPv6`, `TestUpdate`, prefix-regression tests for update/delete, `TestAdd`, `TestDelete`, `TestConcurrentWrites`, and `BenchmarkDelete`.

Control flow: tests use temporary files, compare exact default output ordering, verify IPv6 exclusion, update FQDN/short hostname records, ensure names with shared prefixes are not modified or removed, append and delete records, tolerate empty inputs and blank lines, and run concurrent add/delete loops through an errgroup. The benchmark builds a large host file and deletes selected records.

State/dependencies: tests exercise real file persistence and package path locks. Dependencies include `netip`, temp files, errgroup, and `gotest.tools`. Risks covered include ordering regressions, exact-match deletion, concurrent write corruption, and the historical hostname-prefix bug. Gaps include malformed file content beyond fuzzing, lock cache cleanup through `Drop`, and Windows path behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/etchosts/etchosts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/etchosts/fuzz_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/etchosts/fuzz_test.go

Purpose: fuzzes `etchosts.Add` against arbitrary initial file bytes and generated record slices. Important entry point is `FuzzAdd`.

Control flow: the fuzzer consumes input bytes as initial file content, an integer record count, and up to 40 generated `Record` structs. It writes the bytes to a temp file and calls `Add`, ignoring the returned error. This is designed to find panics or data-race style crashes rather than assert semantic output.

State/dependencies: fuzz state is isolated per test temp directory and uses actual file writes. Dependencies include AdaLogics go-fuzz-headers, OS file IO, and the package `Record` type. Integration point is robustness of append formatting for arbitrary `netip.Addr`/host data. Risks covered include panics from malformed generated records or unusual initial content. Gaps include `Build`, `Delete`, and `Update` fuzzing, plus assertions about resulting file validity.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/etchosts/fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/firewall_linux.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/firewall_linux.go

Purpose: selects Linux firewall backend setup and restores libnetwork-managed firewall state after reloads. Important APIs are `Controller.selectFirewallBackend`, `setupPlatformFirewall`, `setupUserChains`, `setupUserChain`, `handleFirewalldReload`, and `handleFirewallReloadService`; constant `userChain` is `DOCKER-USER`.

Control flow: backend selection honors explicit `iptables`, requires successful `nftables.Enable` for explicit `nftables`, and otherwise leaves defaults unchanged. Platform setup creates user chains and registers firewalld reload handlers. `setupUserChains` skips when nftables is enabled, otherwise ensures `DOCKER-USER` exists and `FORWARD` jumps to it for every enabled iptables version, both at setup and reload. Firewalld reload handling snapshots ingress service bindings and restores ingress ports via load-balancer endpoint sandbox/gateway information.

State/dependencies: firewall state lives in iptables/nftables and service binding maps guarded by controller/service locks. Dependencies include `iptables`, internal `nftables`, ingress service/load-balancer helpers, and logging. Risks include reload races, partial IPv4/IPv6 setup errors, and nftables lacking an exact `DOCKER-USER` equivalent. Tests cover iptables user-chain ordering and absence when iptables is disabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/firewall_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/firewall_linux_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/firewall_linux_test.go

Purpose: integration-tests `DOCKER-USER` chain creation and ordering under Linux iptables. Important tests/helpers are `TestUserChain`, `getRules`, `resetIptables`, and `versionLt`.

Control flow: the test creates isolated network namespace context, resets iptables, starts a controller with iptables enabled or disabled, optionally appends existing `DROP` rules to `FORWARD`, calls `setupUserChains`, and compares chain state to golden files for IPv4/IPv6. It adapts expected "chain missing" error text for older iptables-nft versions. It skips the iptables assertions if nftables backend is enabled.

State/dependencies: tests manipulate real iptables state in a test netns and depend on golden files. Dependencies include bridge config, iptables helpers, nftables enabled state, netns utilities, and `icmd`. Risks covered include preserving user rules, correct jump insertion, no Docker chain creation when iptables disabled, and version-specific error handling. Gaps include firewalld reload service restoration and explicit nftables backend selection errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/firewall_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/firewall_others.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/firewall_others.go

Purpose: provides non-Linux stubs for platform firewall setup. Important APIs are `Controller.selectFirewallBackend` and `Controller.setupPlatformFirewall`.

Control flow: `selectFirewallBackend` always returns nil and `setupPlatformFirewall` does nothing. This keeps shared controller initialization portable while Linux-specific iptables/nftables logic is excluded by build tags.

State/dependencies: there is no state and no external dependency. Integration point is controller startup on Windows or other non-Linux platforms, where firewall behavior is delegated to platform drivers/HNS or omitted. Risk is that config values such as an explicit nftables backend are silently ignored on non-Linux builds, which may be acceptable because those backends are Linux-specific. Test signal is compile-time; no local unit test is needed for these stubs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/firewall_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/addrset/addrset.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/addrset/addrset.go

Purpose: implements an address set over `netip.Prefix` using one or more bitmaps, including huge IPv6 ranges. Important types/APIs are `AddrSet`, `New`, `Add`, `AddAny`, `AddAnyInRange`, `Remove`, `Len`, `AddrsInPrefix`, `String`, and errors `ErrNotAvailable`/`ErrAllocated`.

Control flow: `New` masks the pool and initializes bitmap storage. `Add` validates containment, locates/creates the relevant bitmap, computes host offset, and sets the bit. `AddAny` allocates from the first bitmap; `AddAnyInRange` validates the requested subrange and allocates either whole-bitmap or subrange bits. `Remove` unsets the bit and deletes empty bitmaps. `Len` returns a 128-bit count split into high/low uint64 values; `AddrsInPrefix` counts selected bits that overlap a prefix.

State/dependencies: state is in-memory bitmap maps keyed by prefix. Dependencies include internal `bitmap`, `ipbits`, `netiputil`, and math/bits. Risks include no internal locking, `AddAny` only searching the first bitmap for pools larger than 2^63 addresses, and panic on impossible `OnesCount` errors. Tests cover IPv4, IPv6, full pools, invalid pools, and >64-bit counts.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/addrset/addrset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/addrset/addrset_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/addrset/addrset_test.go

Purpose: thoroughly exercises `AddrSet` allocation, removal, counting, range counting, and error mapping. Important tests include `TestIPv4Pool`, `TestIPv6Pool`, `Test64BitIPv6Range`, `Test32BitIPv6Range`, `TestFullPool`, `TestNotInPool`, `TestInvalidPool`, and `Test64BitPlusAllocation`.

Control flow: tests add first/last addresses, duplicate addresses, remove absent and present entries, allocate serial addresses, allocate within subranges, and count addresses in overlapping/non-overlapping prefixes. Large IPv6 tests ensure pools wider than one bitmap split correctly and 2^64 counts are represented with high/low uint64 values. A helper `uint128Equal` compares split counts using `big.Int`.

State/dependencies: tests inspect internal bitmap maps directly, including synthetic binary bitmap setup to avoid expensive allocation loops. Dependencies include `netip`, encoding/binary, big integers, and `gotest.tools`. Risks covered include host bits in prefixes, bitmap cleanup, duplicate errors, invalid prefixes, full-pool exhaustion, and overflow. Gaps include concurrent access and randomized non-serial allocation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/addrset/addrset_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/caller/caller.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/caller/caller.go

Purpose: provides a small helper for retrieving caller function names for diagnostics. Important APIs are internal `callerInfo` and exported `Name`.

Control flow: `callerInfo` calls `runtime.Caller`, obtains `runtime.FuncForPC`, splits the fully qualified function name on `.`, and returns the final segment, falling back to `unknown` if stack lookup fails. `Name(level)` offsets by two stack frames so `level == 0` returns the caller of `Name`, not `Name` itself.

State/dependencies: no persistent state. Dependencies are `runtime` and strings. Integration points are logging/tracing or error messages that want a lightweight function-name label without full file/line data. Risks include method names with dots or compiler-inserted wrappers producing unexpected suffixes, and stack depth changing if wrapper helpers are added. Tests cover direct and nested calls with level 0 and 1.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/caller/caller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/caller/caller_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/caller/caller_test.go

Purpose: verifies `caller.Name` stack-level behavior. Important fixtures are helper functions `fun1` through `fun6` and `TestCaller`.

Control flow: `fun1` returns `Name(0)` and should resolve to `fun1`; `fun2` returns `Name(1)` and should resolve to `TestCaller`; `fun3`/`fun4` validate an indirect `Name(0)` call; `fun5`/`fun6` validate an indirect `Name(1)` call. Failures use fatal assertions with the unexpected name.

State/dependencies: no external state or persistence. Dependencies are the runtime call stack and testing package. The test protects the hard-coded frame offset in `Name`. Risks not covered include compiler inlining effects, method receivers, anonymous functions, and out-of-range stack levels returning `unknown`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/caller/caller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/countmap/countmap.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/countmap/countmap.go

Purpose: defines a generic map-of-counters helper. Important type/API is `Map[T comparable]` with method `Add`.

Control flow: `Add` increments the counter for key `v` by `delta`, returns the new value, and deletes the key when the new count is zero. It allows negative counts and does not enforce non-negative reference semantics.

State/dependencies: state is the caller-owned Go map; there is no locking or persistence. Dependencies are only Go generics and comparable keys. Integration points are places needing compact reference counts without retaining zero entries. Risks include nil map panics when adding to an uninitialized nil map, no synchronization, and negative count semantics being caller-dependent. Tests verify positive, negative, and zero-removal behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/countmap/countmap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/countmap/countmap_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/countmap/countmap_test.go

Purpose: tests generic counter-map add and zero-deletion semantics. Important test is `TestMap`.

Control flow: the test starts with counters for `foo`, `bar`, and `zeroed`, applies deltas that produce negative values, a new positive key, and a zeroed key deletion, then asserts the resulting map. It then applies inverse deltas to bring all remaining keys to zero and asserts the map is empty.

State/dependencies: no external state; tests use a concrete `Map[string]`. Dependencies include `gotest.tools` deep equality. Risks covered include negative counts being retained, zero counts being deleted, and new key creation. Gaps include nil map behavior, non-string comparable keys, and concurrent use.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/countmap/countmap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/hashable/net.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/hashable/net.go

Purpose: provides hashable encodings for MAC addresses and IP/MAC tuples so they can be map keys. Important APIs are `MACAddr`, `MACAddrFromSlice`, `MACAddrFrom6`, `ParseMAC`, `MACAddr.AsSlice`, `MACAddr.String`, `IPMAC`, `IPMACFrom`, and accessors.

Control flow: MAC conversion packs six bytes into a uint64, rejecting non-MAC-48 slice lengths. `ParseMAC` delegates to `net.ParseMAC` then rejects parsed hardware addresses that are not six bytes. `AsSlice` reconstructs the six-byte hardware address, and `String` formats it through `net.HardwareAddr`. `IPMAC` stores a `netip.Addr` plus `MACAddr` and exposes string/accessor methods.

State/dependencies: values are immutable by convention and fully comparable. Dependencies include `net` and `netip`. Integration points include deduplicating or indexing neighbor/endpoint records by IP/MAC. Risks include returning a slice backed by a local array whose escape is handled by Go, zero value formatting as `00:00:00:00:00:00`, and only supporting MAC-48. Tests cover hashability, parsing, invalid lengths, string form, and tuple accessors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/hashable/net.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/hashable/net_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/hashable/net_test.go

Purpose: verifies hashable MAC/IP tuple helpers. Important tests are compile-time map-key assertions, `TestMACAddrFrom6`, `TestMACAddrFromSlice`, `TestParseMAC`, `TestMACAddr_String`, and `TestIPMACFrom`.

Control flow: tests assert MAC packing/unpacking, reject invalid slice lengths, parse valid and too-long MAC strings, check string formatting including zero value, and confirm `IPMAC` stores and returns the given IP and MAC. Compile-time variables ensure `MACAddr` and `IPMAC` remain comparable.

State/dependencies: no external state. Dependencies are `net`, `netip`, and `gotest.tools`. Risks covered include MAC-48 enforcement, stable string formatting, and tuple accessor correctness. Gaps include unusual accepted `net.ParseMAC` formats, invalid textual MACs other than too-long values, and mutation safety of returned slices.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/hashable/net_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/kvstore/boltdb/boltdb.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/kvstore/boltdb/boltdb.go

Purpose: implements libnetwork's internal KV store interface using bbolt. Important type/API are `BoltDB`, `New`, `Put`, `Exists`, `List`, `AtomicPut`, `AtomicDelete`, `Delete`, and `Close`; stored values have an eight-byte little-endian index prefix.

Control flow: `New` creates parent directories and opens bbolt with a nanosecond timeout to fail fast when the DB is already locked. `Put` creates the bucket, increments an atomic index, prefixes it, and writes. `Exists` and `List` view the bucket and return `ErrKeyNotFound` for absent keys/prefixes. Atomic operations compare the stored index against `previous.LastIndex`, handling create-if-absent for nil previous in `AtomicPut`. `Delete` removes without CAS.

State/dependencies: state is the bbolt file, bucket, mutex, and monotonic in-process `dbIndex`. Dependencies include bbolt, internal `kvstore`, atomic counters, and binary encoding. Risks include index reset on process restart, value-prefix assumptions requiring at least eight bytes, serialized access through a coarse mutex, and fast failure on lock contention. Tests are outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/kvstore/boltdb/boltdb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/kvstore/kvstore.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/kvstore/kvstore.go

Purpose: defines the storage abstraction used by libnetwork datastore backends. Important pieces are errors `ErrKeyModified`, `ErrKeyNotFound`, `ErrPreviousNotSpecified`, `ErrKeyExists`, interface `Store`, and struct `KVPair`.

Control flow: there is no implementation logic; the interface requires plain put/delete/list/exists plus compare-and-swap style `AtomicPut` and `AtomicDelete`, and a `Close` method. `KVPair` carries key, raw value, and last modification index used by atomic methods.

State/dependencies: no state in this file. Dependencies are standard errors. Integration points include the bbolt backend and higher-level libnetwork datastore object persistence. Risks are contract-level: backends must consistently map missing keys, modified indices, and create-vs-update behavior to these sentinel errors, or datastore CAS logic may mis-handle concurrent updates. Test signal is indirect through backend/datastore tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/kvstore/kvstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/l2disco/unsol_arp_linux.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/l2disco/unsol_arp_linux.go

Purpose: constructs and sends unsolicited IPv4 ARP announcements on Linux. Important type/API are `UnsolARP`, `NewUnsolARP`, `Send`, `Close`, and helper `htons`.

Control flow: constructor opens an `AF_PACKET` datagram socket, clones a static ARP request template, copies sender MAC and IP into sender and target fields, builds a broadcast `SockaddrLinklayer` for the interface index and ARP protocol, and returns a sender object. `Send` calls `unix.Sendto`; `Close` closes the socket once and marks it invalid. `htons` converts protocol constants using native-endian interpretation of big-endian bytes.

State/dependencies: state is the raw packet bytes, socket descriptor, and link-layer sockaddr. Dependencies include Linux `unix`, standard net types, and slices. Integration point is L2 neighbor discovery/announcement after endpoint address changes. Risks include requiring Linux capabilities, no IP/MAC length validation beyond copy behavior, and no retry/backoff. Test signal is not local, likely integration-only because raw sockets need privileges.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/l2disco/unsol_arp_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/l2disco/unsol_na_linux.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/l2disco/unsol_na_linux.go

Purpose: constructs and sends unsolicited IPv6 Neighbor Advertisements. Important type/API are `UnsolNA`, `NewUnsolNA`, `Send`, and `Close`.

Control flow: constructor opens an IPv6 ICMP packet socket bound to `::1`, wraps it in `ipv6.PacketConn`, blocks incoming ICMP with a filter, sets a control message with hop limit 255, source IP, and interface index, clones an NA template, and inserts target IP and MAC. `Send` writes the packet to the link-local all-nodes multicast address and verifies the full packet length was sent. `Close` closes the packet connection once.

State/dependencies: state is packet bytes, IPv6 packet connection, and control message. Dependencies include `golang.org/x/net/ipv6`, containerd logging, and net types. Integration point is IPv6 L2 discovery for container endpoints. Risks include requiring raw ICMP privileges, logging but not failing on ICMP filter setup errors, and the misleading comment saying `Send` sends ARP. Test signal is not local because real socket behavior is environment-dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/l2disco/unsol_na_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/maputil/maputil.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/maputil/maputil.go

Purpose: provides a generic helper for filtering map values. Important API is `FilterValues[K comparable, V any]`.

Control flow: the function iterates all map values, applies the predicate, and appends matching values to a slice. It returns nil or an empty slice depending on whether any append occurs and does not preserve any deterministic order because Go map iteration is randomized.

State/dependencies: no state or external dependencies. Integration point in this subset is `Controller.findEndpoints`, which filters the controller endpoint cache by network ID. Risks include callers assuming stable ordering or copies; the helper returns the original values. It performs no locking, so callers must guard the input map if concurrent writes are possible. Test signal is indirect via endpoint store tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/maputil/maputil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/modprobe/modprobe_linux.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/modprobe/modprobe_linux.go

Purpose: attempts to load Linux kernel modules with a docker-in-docker-friendly fallback strategy. Important APIs/types are `LoadModules`, internal `tryLoad`, `loader`, `ioctlLoader`, and `modprobeLoader`.

Control flow: `LoadModules` first calls `isLoaded`; if already loaded it logs and returns. Otherwise it tries `ioctlLoader`, which opens an AF_INET datagram socket and issues `SIOCGIFINDEX` on an ifreq named after each module, relying on kernel autoload behavior and ignoring the ioctl error. If `isLoaded` still fails, it tries `modprobeLoader`, which runs `modprobe -va` for each module. `tryLoad` logs load errors and final check result; the returned error is the last `isLoaded` failure.

State/dependencies: no persistent state. Dependencies include Linux unix syscalls, `os/exec`, context logging, and caller-supplied loaded checks. Integration points are firewall/network features that need kernel modules. Risks include CAP_SYS_MODULE requirements, external command availability, module names doubling as interface names, and losing individual load errors if final check succeeds. Test signal is not local.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/modprobe/modprobe_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nft_cgo_linux.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nft_cgo_linux.go

Purpose: provides the cgo/libnftables backend for applying nftables command buffers. It is built when cgo, dynamic build, and libnftables are available. Important APIs are `preflight`, `nftCtx.Apply`, `newNftCtx`, and `nftCtx.Close`.

Control flow: `preflight` succeeds because cgo linkage is the capability check. `newNftCtx` allocates a libnftables context, enables output and error buffers, and frees the context on setup failure. `Apply` starts an OTEL span, converts command bytes to a C string, runs `nft_run_cmd_from_buffer`, reads buffered stdout/stderr, returns a formatted error on nonzero status, and logs successful output. `Close` frees the C context.

State/dependencies: state is the libnftables context held by `Table` under an apply lock. Dependencies include cgo, `libnftables`, unsafe pointers, logging, and OTEL. Risks include C string conversion of command bytes, libnftables availability at build/runtime, and memory lifetime across C calls. Tests for nftables behavior exercise this backend when built with cgo/libnftables.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nft_cgo_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nft_exec_linux.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nft_exec_linux.go

Purpose: provides the external `nft` command backend when cgo/libnftables is unavailable or disabled. Important APIs are `preflight`, `newNftCtx`, `nftCtx.Apply`, and `Close`, plus cached `lookPathNft`/`lookPathNSEnter`.

Control flow: preflight and context creation require `nft` in PATH. `Apply` starts an OTEL span, builds `nft -f -`, detects rootless detached netns and wraps the command in `nsenter` when needed, starts the command, writes the nft command buffer to stdin, closes stdin, drains stdout/stderr, waits, and returns stderr-enhanced errors. Successful runs log stdout/stderr. `Close` is a no-op because no persistent process exists.

State/dependencies: state is limited to cached executable lookups. Dependencies include `exec`, rootless netns helpers, logging, and OTEL. Integration point is the same `Table.nftApply` path as cgo. Risks include command deadlocks if stdout/stderr handling changes, missing `nsenter` in rootless detached mode, and external command syntax/version differences. Tests use this backend in non-cgo/static/no-libnftables builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nft_exec_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nftables_linux.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nftables_linux.go

Purpose: implements a write-only nftables table model for libnetwork chains, rules, maps, sets, and incremental/reload application. Important APIs/types include `Enable`, `Enabled`, `Disable`, `RunCmd`, `Table`, `NewTable`, `Close`, `Reload`, `SetBaseChainPolicy`, `Modifier`, `Obj`, `BaseChain`, `Chain`, `Rule`, `Map`, `MapElement`, `Set`, `SetElement`, `RuleGroup`, `SetType`, `Typeof`, and map/set type builders.

Control flow: `Enable` runs backend preflight and parses command templates once. `NewTable` creates an in-memory table that will flush on first apply. A `Modifier` records create/delete commands with caller file/line, supports `Reverse`, and is applied under a table lock. `Apply` validates and mutates the in-memory model, builds an incremental nft command file, sends it through cgo or exec backend, and rolls back in-memory changes on validation/apply failure. If nft apply fails after generating commands, it logs line-numbered input and attempts a full table reload from the in-memory model. Objects enforce logical constraints such as no duplicate rules/elements and no deletion of non-empty chains/maps/sets. `updatesApplied` clears pending deltas and flush flags.

State/dependencies: in-memory state mirrors the intended table but does not read host state; host nftables is mutated atomically through generated command files. Dependencies include text/template, logging, slices/iter, backend `nftCtx`, and runtime caller metadata. Risks include write-only drift from external nft changes, limited syntax validation before apply, rollback failures after destructive host changes, no object reference checking, and rule ordering by internal groups. Tests cover creation, grouping, idempotent rule behavior, maps/sets, reload recovery, and validation errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nftables_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nftables_linux_test.go -->
# Research: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nftables_linux_test.go

Purpose: integration-tests the nftables table abstraction against a real `nft` command in an isolated test network namespace. Important helpers/tests are `testSetup`, `applyAndCheck`, `reloadAndCheck`, `TestTable`, `TestChain`, `TestChainRuleGroups`, `TestIgnoreExist`, `TestVMap`, `TestSet`, `TestReload`, and `TestValidation`.

Control flow: setup enables nftables, skips locally if nft is unavailable, fails in CI if enable fails, then creates an isolated OS context and resets `Disable` afterward. Tests create tables, base/regular chains, rules, grouped rule ordering, verdict maps, interval sets, reverse modifiers, full reloads after deleting the underlying table, and many invalid command sequences. Golden files compare `nft list table` output. Validation tests ensure failed applies do not leave a created table and that the in-memory `Table` remains usable afterward.

State/dependencies: tests mutate real nftables state and depend on golden files, `icmd`, and netns utilities. Risks covered include syntax propagation, rollback, reload recovery, duplicate/missing object errors, idempotent rule handling, and rule-group ordering. Gaps include concurrent `Apply`, rootless detached namespace behavior, cgo-vs-exec backend differences beyond common behavior, and external modifications other than deleted tables.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/internal/nftables/nftables_linux_test.go -->
