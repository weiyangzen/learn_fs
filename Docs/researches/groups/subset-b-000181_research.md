# subset-b-000181 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbclient/ndbClient.go -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbclient/ndbClient.go

## Purpose
Command-side client for the `networkdb-test` image. It drives a cluster of test servers through diagnostic HTTP endpoints, creating joins/leaves, network table writes/deletes, peer-count checks, queue checks, and convergence assertions.

## Important APIs, Types, And Functions
`Client` dispatches subcommands after resolving `tasks.<service>` and storing the shared `servicePort`. HTTP helpers include `httpGet`, `httpGetFatalError`, `joinCluster`, `joinNetwork`, `leaveNetwork`, `writeTableKey`, and `deleteTableKey`. Measurement helpers include `clusterPeersNumber`, `networkPeersNumber`, `dbTableEntriesNumber`, `dbQueueLength`, `clientWatchTable`, `clientTableEntriesNumber`, `checkTable`, and `waitWriters`. Workload drivers include `doReady`, `doJoin`, `doClusterPeers`, `doWriteKeys`, `doDeleteKeys`, `doWriteUniqueKeys`, `doWriteDeleteUniqueKeys`, and leave/join stress variants.

## Control Flow
The client validates rough argument counts, handles `debug`/`fail`, DNS-resolves service task IPs, then dispatches to a command function. Most commands fan out goroutines across task IPs and collect `resultTuple` values on buffered channels. Write workloads first enable dummy-client watches, start writer goroutines for a bounded count or bounded duration, then repeatedly poll server or watched-client tables until all nodes show the expected count for a stable interval or the context times out.

## State And Persistence
There is no local persistent state. Runtime state is in goroutine channels, DNS-resolved task IPs, context timeouts, and networkdb table entries persisted by the remote servers. `servicePort` is a package global used by polling helpers.

## Dependencies And Integration Points
Integrates with Swarm DNS, diagnostic HTTP paths exposed by `networkdb.NetworkDB`, and dummy-client watch endpoints. It assumes response text contains fixed phrases such as `total entries`, `qlen`, and `total elements`.

## Risks And Edge Cases
Regex parsing indexes matches without nil/length checks, so unexpected responses can panic. Several subcommands are missing from `cmdArgCheck`, so malformed arguments may fail later. `cmdArgCheck` defaults unknown commands to zero required args before the switch rejects them. Writer counts index directly into `ips`, so asking for more writers/leavers than service tasks can panic. Fatal logging makes this appropriate for test orchestration, not reusable library code.

## Test Signals
Success is printed to stderr by each `do*` command with convergence timing. Failures are fatal when peer counts, queue thresholds, table sizes, writer activity, readiness, or HTTP `OK` responses do not match expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbclient/ndbClient.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbserver/ndbServer.go -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbserver/ndbServer.go

## Purpose
Runs a networkdb test node with an embedded diagnostic HTTP server. It binds networkdb to the task's `eth0` IPv4 address, exposes built-in networkdb diagnostics, and registers dummy-client watch endpoints.

## Important APIs, Types, And Functions
`Server(args []string)` is the entry point. It reads `TASK_ID`, resolves `eth0` via `getIPInterface`, initializes `networkdb.DefaultConfig`, creates `networkdb.New`, registers handlers with `diagnostic.New`, and starts `server.Enable`. `/myip` is handled by `ipaddress`.

## Control Flow
Startup parses the port, validates the task ID environment, finds the container IP, creates the networkdb instance, registers diagnostics, starts the HTTP server on the requested port, then blocks forever with `select {}`.

## State And Persistence
Package globals hold the networkdb instance, diagnostic server, and selected IP. Networkdb itself owns gossip/table state; this file does not persist local files.

## Dependencies And Integration Points
Depends on Docker/Swarm task environment, an up `eth0` with IPv4, `networkdb`, diagnostic server, and dummy-client handlers. It is launched by `testMain.go` in the `networkdb-test` command image.

## Risks And Edge Cases
Port parsing ignores conversion errors and can silently use port zero. The server requires interface name `eth0`, so nonstandard container networking breaks startup. Binding with empty IP in `server.Enable("", port)` listens broadly, which is suitable for test containers but not hardened diagnostics.

## Test Signals
Useful signals are successful `/ready`, `/myip`, networkdb diagnostic responses, and client workloads converging without fatal logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dbserver/ndbServer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dummyclient/dummyClient.go -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dummyclient/dummyClient.go

## Purpose
Adds lightweight client-side table-watch diagnostics to a networkdb test server. It lets tests watch a table and later compare the locally observed watch state against networkdb server state.

## Important APIs, Types, And Functions
`RegisterDiagnosticHandlers` registers `/watchtable` and `/watchedtableentries`. `watchTable` starts `nDB.Watch(tableName, "")` and records a `tableHandler`. `watchTableEntries` renders the currently observed entries. `handleTableEvents` consumes `networkdb.WatchEvent` values from a `go-events` channel.

## Control Flow
`/watchtable` validates `tname`, returns `OK` if already watched, otherwise starts a watcher goroutine. The goroutine loops until `ch.Done()` or an event arrives, adding entries when `Value` is non-nil and deleting on tombstone events. `/watchedtableentries` dumps the in-memory map size and entries.

## State And Persistence
`clientWatchTable` is a package-global map from table name to watched state. It is in-memory only and is reset when the server process exits.

## Dependencies And Integration Points
Integrates with `networkdb.Watch`, `diagnostic.HTTPReply`, and the test client parser for `total elements`. It intentionally mirrors networkdb table changes from the consumer side.

## Risks And Edge Cases
`clientWatchTable` and nested entry maps are accessed from HTTP handlers and watcher goroutines without locking, creating data-race risk under concurrent calls. The `cancelWatch` function is stored but never exposed or called. A non-`WatchEvent` is fatal, which is fine for tests but abruptly exits the server.

## Test Signals
The main signal is `/watchedtableentries?tname=...` returning the expected entry count after write/delete workloads. Race detector runs would be valuable because of unsynchronized global state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/dummyclient/dummyClient.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/testMain.go -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/testMain.go

## Purpose
Tiny command dispatcher for the `networkdb-test` binary. It starts either the server mode or the client mode used by Swarm/networkdb integration tests.

## Important APIs, Types, And Functions
`main` sets containerd log text formatting, logs `os.Args`, switches on `os.Args[1]`, and calls `dbserver.Server` or `dbclient.Client`.

## Control Flow
The process chooses mode from the first user argument and forwards the remaining arguments unchanged to that mode.

## State And Persistence
No persistent state. Process behavior is fully argument-driven.

## Dependencies And Integration Points
Links the `dbserver` and `dbclient` packages into one image entry point.

## Risks And Edge Cases
The length check uses `len(os.Args) < 1`, but `os.Args[1]` requires at least two entries; running without a mode can panic. Unknown modes silently fall through and exit successfully.

## Test Signals
Successful mode dispatch is visible through startup logs and the downstream server/client behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/networkdb-test/testMain.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/Dockerfile -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/Dockerfile

## Purpose
Builds the legacy `docker/ssd` service-state diagnostic image used by `ssd.py` to inspect swarm service discovery, ingress NAT, and IPVS programming.

## Important APIs, Types, And Functions
The Dockerfile is Alpine-based, installs networking/debug tools, Python 2, `pip`, Docker Python client from Git, adds `ssd.py`, and sets `ENTRYPOINT ["python", "/ssd.py"]`.

## Control Flow
Image build installs packages, creates Python 2 compatibility symlinks, bootstraps pip with `easy_install`, installs docker-py from Git, and then runs the script at container startup.

## State And Persistence
The image has no runtime persistence by itself. Diagnostics depend on a mounted Docker socket and host/network namespace files.

## Dependencies And Integration Points
Depends on Alpine `apk`, Python 2 packages, `ipvsadm`, `iproute2`, `iptables`, `nsenter`, `bash`, and a reachable Git repository for docker-py during build.

## Risks And Edge Cases
Python 2 and `easy_install` are obsolete, and `git://` is unauthenticated and often blocked. `pip install --upgrade pip` on Python 2 can select unsupported versions unless constrained by package indexes. The image needs privileged host access to be useful.

## Test Signals
A successful build and `docker/ssd <network>` run that can import `docker`, access `/var/run/docker.sock`, and invoke host namespace tools are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/ssd.py -->
# sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/ssd.py

## Purpose
Python 2 diagnostic utility for swarm service discovery. It compares Docker daemon network/service data with per-namespace IPVS state, validates ingress iptables DNAT, and can compare gossip hashes across nodes.

## Important APIs, Types, And Functions
`which` locates binaries. `check_iptables` checks `DOCKER-INGRESS` NAT rules for published ports. `get_namespaces` maps containers or ingress sandbox to netns paths. `check_network` inspects a network, builds service fwmark-to-task mappings, enters namespaces, parses `ipvsadm -ln`, and compares real backends. Main modes are `default`, `gossip-consistency`, and `gossip-hash`.

## Control Flow
Default mode checks the requested network and ingress. Gossip-consistency creates a global `gossip-hash` service running the same image, waits, reads service logs, prints hashes, and removes the service. Gossip-hash inspects network service/task metadata, builds a sorted entry list, prints an MD5, flushes stdout, then waits forever.

## State And Persistence
State is external: Docker service definitions, task logs, kernel IPVS tables, iptables rules, and network namespaces. The script itself keeps transient dictionaries of fwmarks, expected tasks, and observed IPVS backends.

## Dependencies And Integration Points
Requires Docker Engine API over the Unix socket, docker-py, `nsenter`, `ipvsadm`, `iptables`, `bash`, and historical output formats such as `ifconfig eth1` with `inet addr`.

## Risks And Edge Cases
The script is Python 2-only, uses old docker-py APIs, and hashes strings without explicit byte encoding. `which` can return `None`; command construction often assumes valid paths. `get_namespaces` has awkward loop state but ultimately uses container IDs from inspect data. It prints mismatches rather than exiting nonzero for many failures, so automation must parse output.

## Test Signals
Expected output includes `service ... OK` for matching IPVS backends, printed ingress DNAT-missing messages when NAT is wrong, and matching gossip hashes across nodes for consistent control-plane state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cmd/ssd/ssd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/allocator_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/allocator_test.go

## Purpose
Delegates generic SwarmKit allocator conformance tests to the CNM network allocator provider.

## Important APIs, Types, And Functions
`TestAllocator` calls `allocator.RunAllocatorTests(t, NewProvider(nil))` and skips on Windows because the generic test suite uses Linux driver names.

## Control Flow
The test is a single wrapper: skip condition first, then SwarmKit-provided allocator tests exercise provider/allocator behavior.

## State And Persistence
No persistent state; allocator instances are created inside the test suite.

## Dependencies And Integration Points
Integrates `cnmallocator.Provider` with SwarmKit manager allocator tests.

## Risks And Edge Cases
Coverage depends on SwarmKit's external test suite and is skipped on Windows, leaving Windows-specific predefined network names to separate tests.

## Test Signals
Passing this test shows CNM provider behavior remains compatible with SwarmKit allocator expectations on non-Windows platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/allocator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_ipam.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_ipam.go

## Purpose
Initializes IPAM drivers for the Swarm CNM allocator, including optional swarm default address pool configuration.

## Important APIs, Types, And Functions
`initIPAMDrivers(r ipamapi.Registerer, netConfig *networkallocator.Config)` parses `DefaultAddrPool` prefixes into `ipamutils.NetworkToSplit`, logs configured defaults, and calls `ipams.Register`.

## Control Flow
If a network allocator config is present, each default pool string is parsed with `netip.ParsePrefix`; invalid prefixes fail allocator initialization. The parsed base and subnet size are collected and passed to libnetwork IPAM registration.

## State And Persistence
No local persistence. It configures the IPAM registry with in-memory driver instances and default address-pool inputs used by later pool allocation.

## Dependencies And Integration Points
Connects SwarmKit `networkallocator.Config` to libnetwork IPAM registration and default pool splitting.

## Risks And Edge Cases
The logging string leaves a trailing comma and only logs when pools are present. Invalid prefixes fail fast. Passing `nil` plugin getter means only built-in IPAMs are registered here; remote IPAM plugins are registered later by `NewAllocator`.

## Test Signals
Allocator tests that allocate empty-config networks and custom pool configs exercise this path indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_ipam.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_linux.go

## Purpose
Defines Linux CNM allocator driver availability: global overlay allocation plus local built-in drivers that can be referenced from Swarm-scoped networks without manager-side driver allocation.

## Important APIs, Types, And Functions
`globalDrivers` registers `overlay` through `ovmanager.Register`. `localDrivers` lists `bridge`, `host`, `ipvlan`, and `macvlan`. `PredefinedNetworks` returns predefined `bridge` and `host` network data.

## Control Flow
`NewAllocator` iterates `globalDrivers` and uses `localDrivers` through `resolveDriver`/`IsBuiltInDriver`.

## State And Persistence
No persistence; this file provides platform-specific static driver maps.

## Dependencies And Integration Points
Integrates bridge, host, ipvlan, macvlan, overlay manager, and SwarmKit predefined network data on Linux.

## Risks And Edge Cases
Driver names are compile-time platform policy. Adding a Linux driver requires updating this list if it should be valid for swarm allocator validation or node-local handling.

## Test Signals
Provider validation, generic allocator tests, and network allocation tests depend on these driver names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_windows.go

## Purpose
Defines Windows CNM allocator driver availability and predefined networks.

## Important APIs, Types, And Functions
`globalDrivers` still exposes overlay allocation through `ovmanager.Register`. `localDrivers` lists Windows drivers `internal`, `l2bridge`, and `nat`. `PredefinedNetworks` returns the predefined `nat` network.

## Control Flow
The same allocator logic uses these platform-specific maps at build time on Windows.

## State And Persistence
No persistence; the data is static.

## Dependencies And Integration Points
Connects SwarmKit allocation policy to Windows libnetwork driver names.

## Risks And Edge Cases
Linux-focused allocator tests are skipped because expected driver names differ. Validation depends on this list staying aligned with Windows driver registration.

## Test Signals
Windows-specific allocator/provider tests should validate `nat`, `internal`, and `l2bridge` behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/drivers_network_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/extra_status.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/extra_status.go

## Purpose
Adds optional IPAM operational status to Swarm network objects when callers request it through network extra options.

## Important APIs, Types, And Functions
`OnGetNetwork(ctx, swarmnet, typeurl, appdata)` implements `networkallocator.OnGetNetworker`. It parses `netextra.OptionsFrom`, resolves the local allocator network and IPAM driver, optionally uses `ipamapi.PoolStatuser`, constructs `networktypes.Status`, and marshals it back into `swarmnet.Extra`.

## Control Flow
If `WithIPAMStatus` is not set, it returns without mutation. Otherwise it loads local network pool IDs, calls `PoolStatus` for each pool, builds subnet status with `IPsInUse` and `DynamicIPsAvailable`, and writes marshaled status into the Swarm API object.

## State And Persistence
Reads allocator in-memory pool state and IPAM driver status. Mutates only the provided `api.Network` response object.

## Dependencies And Integration Points
Integrates SwarmKit network get hooks, Moby network API status types, `netextra` appdata encoding, and optional IPAM driver status support.

## Risks And Edge Cases
Status is unavailable if allocator state is missing or the IPAM driver does not implement `PoolStatuser`. Errors while reading one pool abort the entire status response.

## Test Signals
Useful tests would mock `PoolStatuser` and assert `swarmnet.Extra` contains per-subnet status only when requested.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/extra_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator.go

## Purpose
Core Swarm CNM network allocator. It allocates network IPAM pools/gateways, driver state, service VIPs, task endpoint IPs, and node attachment addresses while tracking enough local state to release them.

## Important APIs, Types, And Functions
`cnmNetworkAllocator` holds plugin getter, IPAM/network registries, allocated networks, services, tasks, and node attachments. Public allocator methods include `Allocate`, `Deallocate`, `AllocateService`, `DeallocateService`, `IsAllocated`, `IsTaskAllocated`, `IsServiceAllocated`, `AllocateTask`, `DeallocateTask`, `IsAttachmentAllocated`, `AllocateAttachment`, and `DeallocateAttachment`. Internal helpers include `allocateVIP`, `deallocateVIP`, `allocateNetworkIPs`, `allocatePools`, `freePools`, `allocateDriverState`, `freeDriverState`, `resolveDriver`, `resolveIPAM`, and `setIPAMSerialAlloc`.

## Control Flow
`NewAllocator` registers global and remote network drivers plus built-in and remote IPAM drivers. Network allocation resolves the driver; node-local networks get minimal driver/IPAM state, while global networks allocate pools/gateways, then driver state, with rollback on failure. Services reconcile desired networks against existing VIPs, allocate missing VIPs, and release stale VIPs, with DNSRR mode freeing all VIPs. Task and node attachment allocation requests addresses per network attachment and rolls back earlier attachments if later allocation fails.

## State And Persistence
Allocator state is in-memory maps keyed by network, service, task, and node IDs. It mutates SwarmKit API objects by writing `IPAM`, `DriverState`, `Endpoint.VirtualIPs`, and attachment `Addresses`. Real persistence is delegated to IPAM/network drivers and the Swarm manager object store outside this file.

## Dependencies And Integration Points
Integrates SwarmKit `networkallocator`, libnetwork driver registries, overlay network allocator, local driver lists, default and remote IPAM, plugin getter, netlabel gateway metadata, and containerd logging.

## Risks And Edge Cases
There is no explicit mutex, so callers must serialize allocator access as SwarmKit expects. `allocateNetworkIPs` returns after allocating one address even if multiple addresses were supplied. `releaseEndpoints` deletes endpoint mappings before IPAM release succeeds, risking local accounting drift on release failures. `dOptions` is mutated during gateway allocation. Pool release logs errors but continues.

## Test Signals
`networkallocator_test.go` covers invalid drivers/IPAMs, deterministic subnet allocation, gateway handling, small subnets, task allocation/free, service VIP updates, ingress VIP reuse, and IPAM option passing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator_test.go

## Purpose
Unit tests for the CNM Swarm network allocator's network, service, task, and IPAM option behavior.

## Important APIs, Types, And Functions
`newNetworkAllocator` constructs a provider allocator. Tests cover invalid IPAM/driver names, double allocation, empty config default pool determinism, explicit subnet/gateway allocation, invalid gateways, `/32` support, multiple subnets, deallocation/reallocation, task address allocation/free, service VIP allocation, ingress VIP handling, service network updates, and custom `mockIpam`.

## Control Flow
Tests construct SwarmKit `api.Network`, `api.Task`, and `api.Service` objects, call allocator methods, and assert mutations to `IPAM.Configs`, `Gateway`, `Addresses`, `Endpoint.VirtualIPs`, and allocation predicates.

## State And Persistence
All state is in-memory. Some tests create two allocator instances to assert deterministic allocation order from identical inputs.

## Dependencies And Integration Points
Uses libnetwork default IPAM, SwarmKit API types, SwarmKit allocator interfaces, and `gotest.tools` assertions.

## Risks And Edge Cases
The tests mostly assert success/error presence rather than exact error types. They do not exercise concurrent allocation, remote plugins, release failure behavior, or node attachment allocation deeply. The mock IPAM's `RequestAddress` returns nil values, limiting coverage to pool option propagation.

## Test Signals
Passing tests strongly signal stable allocator mutation semantics and compatibility with SwarmKit service/task/network allocation flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/networkallocator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider.go

## Purpose
Implements the SwarmKit network allocator provider for CNM/libnetwork, including driver validation and VXLAN port configuration.

## Important APIs, Types, And Functions
`Provider` holds a plugin getter. `NewProvider` constructs it. `ValidateIPAMDriver`, `ValidateIngressNetworkDriver`, and `ValidateNetworkDriver` validate nil/default, built-in, overlay ingress, and plugin drivers. `validatePluginDriver` rejects missing plugin stores, lookup failures, and legacy v1 plugins. `SetDefaultVXLANUDPPort` delegates to overlay utilities.

## Control Flow
Validation allows nil drivers, requires a name when a driver object is present, accepts known built-ins/default IPAMs, otherwise performs plugin lookup by endpoint type and rejects v1 plugins.

## State And Persistence
Provider state is just the plugin getter reference. VXLAN port changes affect overlay utility configuration outside this file.

## Dependencies And Integration Points
Bridges SwarmKit provider interfaces with libnetwork driver/IPAM plugin types, default IPAM, overlay utils, and gRPC status codes.

## Risks And Edge Cases
Without a plugin getter, only built-in drivers validate. Validation proves lookup and version only; it does not prove plugin runtime correctness or allocator support. Ingress remains restricted to overlay.

## Test Signals
`provider_test.go` checks nil and empty-name validation status. Broader behavior is covered by SwarmKit allocator tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider_test.go

## Purpose
Tests minimal validation behavior for CNM allocator provider driver validation methods.

## Important APIs, Types, And Functions
`TestValidateDriver` runs both `ValidateIPAMDriver` and `ValidateNetworkDriver`, asserting nil is accepted and an empty-name driver returns `codes.InvalidArgument`.

## Control Flow
The table-driven test creates a provider without plugin getter and applies each validator to nil and empty driver values.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Uses SwarmKit API driver objects, SwarmKit testutils error-code extraction, gRPC codes, and gotest assertions.

## Risks And Edge Cases
It does not cover built-in driver acceptance, plugin lookup, legacy plugin rejection, or ingress-specific validation.

## Test Signals
Passing confirms the provider preserves the required nil/default and empty-name validation contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/provider_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config.go -->
# sources/cloud-native/moby/daemon/libnetwork/config/config.go

## Purpose
Defines the central libnetwork controller configuration object and option setters used during controller construction.

## Important APIs, Types, And Functions
`Config` embeds `PlatformConfig` and holds data directory, exec root, defaults, labels, cluster provider, control-plane MTU, default address pools, datastore bucket, active sandboxes, plugin getter, firewall backend, rootless flag, and userland proxy settings. `New` applies variadic `Option`s. Option setters configure default network/driver, address pools, data dir, exec root, plugin getter, MTU, active sandboxes, firewall backend, rootless mode, and userland proxy.

## Control Flow
`New` starts with default datastore bucket and applies non-nil options in order. `OptionNetworkControlPlaneMTU` warns for low MTU values and clamps below the hard minimum.

## State And Persistence
This file creates in-memory boot configuration. The data directory and datastore bucket influence persistent libnetwork state opened later by `controller.New`.

## Dependencies And Integration Points
Used by `libnetwork.New`, platform config files, datastore, cluster provider, IPAM default pools, plugin discovery, and bridge/firewall setup.

## Risks And Edge Cases
Options mutate shared config without validation beyond MTU clamping and trimming. Some fields are platform-specific but live in the common struct. Option order matters when multiple setters target the same field.

## Test Signals
Controller initialization and platform-specific tests are the main signals; direct config tests would assert default bucket, trimming, and MTU clamping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/config/config_linux.go

## Purpose
Adds Linux-specific libnetwork configuration, especially bridge driver configuration and OSL base-path setup.

## Important APIs, Types, And Functions
`PlatformConfig` contains `BridgeConfig bridge.Configuration`. `OptionBridgeConfig` sets bridge driver settings. `optionExecRoot` sets both `Config.ExecRoot` and `osl.SetBasePath`.

## Control Flow
The common `OptionExecRoot` delegates here on Linux, so controller config and namespace path setup stay in sync.

## State And Persistence
No direct persistence. Exec root determines runtime paths for OSL namespace metadata and external key listeners.

## Dependencies And Integration Points
Connects common config to bridge driver and `osl` Linux namespace handling.

## Risks And Edge Cases
Exec-root changes after namespaces are created would not retroactively move existing state. Bridge configuration is Linux-only, so common callers must account for platform builds.

## Test Signals
Linux controller startup, bridge driver registration, and namespace creation depend on these options.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/config/config_windows.go

## Purpose
Provides non-Unix/Windows platform config stubs for libnetwork.

## Important APIs, Types, And Functions
`PlatformConfig` is empty. `optionExecRoot` returns a no-op option.

## Control Flow
Common `OptionExecRoot` compiles but has no effect on this platform file.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Keeps the common config API portable across platform builds where Linux OSL/bridge config is absent.

## Risks And Edge Cases
Callers expecting `ExecRoot` to be recorded on Windows will not get that behavior from this file.

## Test Signals
Cross-platform build success is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/config/config_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller.go -->
# sources/cloud-native/moby/daemon/libnetwork/controller.go

## Purpose
Central libnetwork controller implementation. It owns driver/IPAM registries, datastore, sandbox/network/endpoint caches, cluster agent integration, diagnostic server, and creation/lookup lifecycle for networks and sandboxes.

## Important APIs, Types, And Functions
`Controller` holds registries, store, config, sandboxes, networks, endpoints, service discovery state, cluster agent channels, locks, keys, diagnostics, and default OSL sandbox. Key APIs include `New`, `SetClusterProvider`, `SetKeys`, `AgentInitWait`, `AgentStopWait`, `BuiltinDrivers`, `BuiltinIPAMDrivers`, `NewNetwork`, `reservePools`, `addNetwork`, `Networks`, `WalkNetworks`, `NetworkByName`, `NetworkByID`, `NewSandbox`, `GetSandbox`, `SandboxByID`, `SandboxDestroy`, `resolveDriver`, `loadDriver`, `getIPAMDriver`, `Stop`, and diagnostic controls.

## Control Flow
`New` builds config/store, initializes registries, chooses firewall backend, registers port mappers before drivers, registers remote and built-in network/IPAM drivers, restores special networks, reserves IPAM pools, restores/cleans sandboxes/endpoints/networks, starts external key listener, and sets up platform firewall. `NewNetwork` serializes by ID/name, validates names and scope, resolves drivers, applies config-only networks, applies config-from networks, enforces swarm manager/worker rules, allocates IPAM, creates driver state, stores endpoint count and network, joins cluster gossip, and creates load-balancer sandbox when needed. `NewSandbox` reuses stub sandboxes or creates new ones, applies options, sets ingress/lb IDs, creates resolution files and OSL sandbox, stores it, and rolls back on errors.

## State And Persistence
Persistent state is stored in `datastore.Store` under the libnetwork data directory. In-memory maps cache networks, endpoints, sandboxes, service records, and bindings. Comments warn that store loads can create multiple instances for the same logical object, so lock ordering matters.

## Dependencies And Integration Points
Integrates with config, datastore, diagnostic server, cluster provider/agent, driver registries, remote plugins, IPAMs, OSL namespaces, netlabel options, scope checks, and OpenTelemetry tracing.

## Risks And Edge Cases
Concurrency is complex: multiple locks protect overlapping maps and comments warn about stale object instances. `NewNetwork` has many rollback defers where partial cleanup can fail. Manager/worker redirection depends on cluster state. Driver loading can fall back to legacy plugin APIs when no plugin getter exists.

## Test Signals
Signals include controller startup tests, network creation/deletion, sandbox restore/live-restore, driver/IPAM plugin tests, swarm-scope network validation, datastore rollback behavior, and diagnostic enable/disable checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/controller_linux.go

## Purpose
Linux-specific controller support for firewall reporting, enabled iptables versions, and OSL sandbox setup.

## Important APIs, Types, And Functions
`FirewallBackend` returns Docker info firewall metadata, including iptables/nftables, firewalld reload timestamp, and userland proxy fields. `enabledIptablesVersions` reports IPv4/IPv6 settings. `getDefaultOSLSandbox` lazily creates a shared namespace. `setupOSLSandbox` creates or attaches an OSL namespace and applies OS tweaks.

## Control Flow
Firewall reporting checks nftables and firewalld runtime state. Sandbox setup uses the default namespace when requested, creates a new sandbox unless an external key is used, then invokes OSL tweak application inside the namespace and again outside for compatibility/performance.

## State And Persistence
Stores a lazily initialized default OSL namespace in the controller. OSL namespace creation affects runtime namespace files under configured exec root.

## Dependencies And Integration Points
Integrates with Docker system info, nftables, iptables/firewalld, OSL namespace implementation, and sandbox configuration.

## Risks And Edge Cases
If default namespace creation fails, the `sync.Once` is reset for retry. Applying OS tweaks twice is intentional but non-obvious. Firewall info combines backend and firewalld state into a string consumed by Docker info users.

## Test Signals
Linux sandbox tests, Docker info firewall assertions, and live-restore namespace behavior exercise this code.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller_others.go -->
# sources/cloud-native/moby/daemon/libnetwork/controller_others.go

## Purpose
Non-Linux stubs for controller firewall and OSL sandbox functionality.

## Important APIs, Types, And Functions
`FirewallBackend` returns nil, `enabledIptablesVersions` returns nil, and `setupOSLSandbox` is a no-op.

## Control Flow
These methods intentionally do nothing on non-Linux builds.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Allows common controller code to compile on platforms without Linux iptables/nftables/OSL namespace behavior.

## Risks And Edge Cases
Callers must tolerate nil firewall info and no OSL sandbox setup on non-Linux.

## Test Signals
Cross-platform build and non-Linux controller tests are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/controller_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/cache.go -->
# sources/cloud-native/moby/daemon/libnetwork/datastore/cache.go

## Purpose
In-memory cache layer for libnetwork datastore objects, keyed by KV object prefix and full key.

## Important APIs, Types, And Functions
`cache` holds `kmm map[string]kvMap` and a backing `store.Store`. `kmap` lazily populates a prefix map from the backing store. `add`, `del`, `get`, and `list` mutate or read cached objects and optionally emulate atomic indexing for skipped persistence.

## Control Flow
On first access for a key prefix, `kmap` lists the backing store, unmarshals objects through `KVObject.New` and `SetValue`, records DB indexes, and installs the map with first-writer-wins behavior if concurrent goroutines race. Atomic cache operations compare indexes when persistence is skipped and increment indexes on add.

## State And Persistence
Cache state is in-memory only. It mirrors persisted objects and also sequences `KVObject.Skip()` objects that never hit disk.

## Dependencies And Integration Points
Used exclusively by `datastore.Store` to back `PutObjectAtomic`, `GetObject`, `List`, and deletes. Depends on the internal kvstore interface and datastore `KVObject` contract.

## Risks And Edge Cases
Objects are cached by reference, so callers mutating returned objects can affect cache unless `CopyTo` is used on reads. `list` returns cached object instances directly. Lazy population relies on prefix listing semantics and ignores empty values.

## Test Signals
Datastore tests validate flat-key reads, atomic updates, cache population, and mock-store behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/datastore.go -->
# sources/cloud-native/moby/daemon/libnetwork/datastore/datastore.go

## Purpose
Provides libnetwork's local persistent key/value datastore wrapper over BoltDB plus an in-memory cache and optimistic atomic operations.

## Important APIs, Types, And Functions
`Store` wraps `store.Store` and `cache`. `KVObject` defines key, prefix, value marshal/unmarshal, index, existence, skip, new, and copy behavior. `Key` builds rooted keys. `New` opens `local-kv.db` in the configured bucket. Store APIs include `PutObjectAtomic`, `GetObject`, `List`, `Map`, `DeleteObject`, and `DeleteObjectAtomic`.

## Control Flow
Atomic put validates object/value, uses previous index when the object exists, writes via `AtomicPut`, records returned index, then updates cache. Deletes either bypass or enforce optimistic index checks. `Map` walks raw store keys under a prefix and unmarshals objects into a trimmed-key map.

## State And Persistence
Persistent state is BoltDB under `<dir>/local-kv.db` and bucket `libnetwork` by default. Cache mirrors store content and tracks skipped objects in memory.

## Dependencies And Integration Points
Used by controller, networks, endpoints, bridge driver, and sandbox stores. Depends on internal kvstore/boltdb and libnetwork typed errors.

## Risks And Edge Cases
`PutObjectAtomic` maps `store.ErrKeyExists` to `ErrKeyModified` but other stale-index errors depend on backing store behavior. `DeleteObject` updates cache only after store delete succeeds, so missing persisted keys can leave cache entries. All store operations are serialized by one mutex.

## Test Signals
`datastore_test.go` and mock store tests cover key construction, atomic object update, value validation, and cache interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/datastore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/datastore_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/datastore/datastore_test.go

## Purpose
Unit tests and dummy objects for libnetwork datastore/cache behavior.

## Important APIs, Types, And Functions
`NewTestDataStore` builds a `Store` with `MockStore`. `TestKey`, `TestKVObjectFlatKey`, and `TestAtomicKVObjectFlatKey` verify key formatting, object storage, retrieval, existence/index updates, and repeated atomic updates. `dummyObject`, `recStruct`, and `dummyKVObject` implement `KVObject` behavior and JSON marshaling.

## Control Flow
Tests store dummy objects atomically, retrieve copies by key, mutate return-value behavior, and assert successful updates using current indexes.

## State And Persistence
State lives in the in-memory mock store and cache. Dummy objects model DB index/existence flags.

## Dependencies And Integration Points
Exercises datastore against the same `KVObject` interface used by libnetwork runtime objects.

## Risks And Edge Cases
Coverage is narrow: it does not assert stale-index failure paths, delete behavior, list/map behavior, skipped persistence, or concurrent cache population.

## Test Signals
Passing tests confirm basic key contract and optimistic update happy paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/datastore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/mockstore_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/datastore/mockstore_test.go

## Purpose
In-memory kvstore implementation used by datastore tests.

## Important APIs, Types, And Functions
`MockStore` holds `db map[string]*MockData`. It implements `Put`, `Exists`, `List`, `AtomicPut`, `AtomicDelete`, `Delete`, and `Close` for the internal kvstore interface.

## Control Flow
`Put` increments per-key indexes. `List` returns keys with the requested prefix or `ErrKeyNotFound`. `AtomicPut` checks absence or matching `LastIndex`, then delegates to `Put`. `AtomicDelete` checks matching index before deleting.

## State And Persistence
All state is in-memory and process-local.

## Dependencies And Integration Points
Used by `NewTestDataStore` to test `datastore.Store` without BoltDB.

## Risks And Edge Cases
The mock returns `types.InvalidParameterErrorf` for atomic conflicts rather than the same sentinel errors a real store may return, so it may not exercise wrapper error mapping exactly. It is not synchronized and is only safe under the datastore's external mutex in tests.

## Test Signals
Datastore unit tests indirectly validate mock behavior; additional tests could cover conflict and deletion paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/datastore/mockstore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway.go -->
# sources/cloud-native/moby/daemon/libnetwork/default_gateway.go

## Purpose
Manages libnetwork's dynamic default gateway endpoint for sandboxes whose attached networks do not provide external connectivity.

## Important APIs, Types, And Functions
`Sandbox.setupDefaultGW`, `clearDefaultGW`, `needDefaultGW`, `getEndpointInGWNetwork`, `isGatewayEndpoint`, and `getGatewayEndpoint` coordinate gateway endpoint creation/removal and gateway selection. `Controller.defaultGwNetwork` serializes creation through `procGwNetwork`.

## Control Flow
When needed, a sandbox finds or creates the platform default gateway network, builds a `gateway_` endpoint name, propagates port mappings/exposed ports, applies platform endpoint options, creates the endpoint, and joins it to the sandbox. Clearing leaves and deletes that endpoint. Gateway need is calculated by scanning non-null, non-host, non-internal endpoints for gateways/default routes or disabled gateway service.

## State And Persistence
Gateway endpoints and gateway network are normal libnetwork objects and can be stored through network/endpoint persistence. `procGwNetwork` is a process-local semaphore for creation serialization.

## Dependencies And Integration Points
Works with sandbox endpoint ordering, network labels, port mapping labels, platform-specific `createGWNetwork` and `getPlatformOption`, and driver gateway reporting.

## Risks And Edge Cases
Endpoint names depend on sandbox/container ID truncation. Gateway selection uses sorted endpoint order and first IPv4/IPv6 connectivity. Cleanup failures can leave gateway endpoints. Static-route detection only checks IPv4 default route string.

## Test Signals
Sandbox join/leave tests, default gateway network creation, port mapping through gateway endpoint, and multi-network gateway selection are key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_freebsd.go -->
# sources/cloud-native/moby/daemon/libnetwork/default_gateway_freebsd.go

## Purpose
FreeBSD implementation hooks for libnetwork default gateway network.

## Important APIs, Types, And Functions
Defines `libnGWNetwork = "docker_gwbridge"`, returns no platform endpoint option, and leaves `Controller.createGWNetwork` unimplemented with `errdefs.NotImplemented`.

## Control Flow
Calls that require gateway network creation fail with not implemented on FreeBSD.

## State And Persistence
No state is created by this file.

## Dependencies And Integration Points
Allows common gateway code to compile while signaling unsupported behavior.

## Risks And Edge Cases
Sandboxes that require a dynamically created default gateway network will fail on FreeBSD.

## Test Signals
FreeBSD build and expected not-implemented behavior are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/default_gateway_linux.go

## Purpose
Linux implementation for creating the `docker_gwbridge` default gateway network.

## Important APIs, Types, And Functions
Defines `libnGWNetwork`, `getPlatformOption` returning nil, and `Controller.createGWNetwork`, which calls `NewNetwork` with bridge options `BridgeName=docker_gwbridge`, `EnableICC=false`, `EnableIPMasquerade=true`, IPv4 enabled, and IPv6 disabled.

## Control Flow
When common gateway code cannot find the gateway network, it enters this function and creates a bridge-backed network with tracing baggage identifying the trigger.

## State And Persistence
Creates a normal libnetwork bridge network persisted by controller network storage and realized by the bridge driver.

## Dependencies And Integration Points
Depends on bridge driver labels, controller `NewNetwork`, and OpenTelemetry baggage utilities.

## Risks And Edge Cases
Hardcoded IPv6 disabled means default gateway service is IPv4-only here. Bridge creation failures propagate to sandbox default gateway setup.

## Test Signals
Linux sandbox tests and daemon startup/live-restore behavior around `docker_gwbridge` exercise this path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_windows.go -->
# sources/cloud-native/moby/daemon/libnetwork/default_gateway_windows.go

## Purpose
Windows default gateway support using the built-in `nat` network and endpoint options that disable ICC and DNS.

## Important APIs, Types, And Functions
Defines `libnGWNetwork = "nat"`. `getPlatformOption` returns `CreateOptionGeneric` with Windows driver `DisableICC` and `DisableDNS`. `createGWNetwork` delegates to `NetworkByName("nat")`.

## Control Flow
Common gateway setup uses the existing Windows NAT network rather than creating a new bridge network.

## State And Persistence
No new network is created; gateway endpoints attach to the existing NAT network.

## Dependencies And Integration Points
Depends on Windows libnetwork driver labels, generic endpoint options, and a preexisting NAT network.

## Risks And Edge Cases
If `nat` does not exist, gateway setup fails. Behavior differs from Linux because DNS and ICC are explicitly disabled on the endpoint.

## Test Signals
Windows networking tests should verify default gateway endpoint attachment to NAT and correct DNS/ICC option propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/default_gateway_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/diagnostic/server.go -->
# sources/cloud-native/moby/daemon/libnetwork/diagnostic/server.go

## Purpose
Provides an opt-in HTTP diagnostic server for libnetwork and networkdb commands.

## Important APIs, Types, And Functions
`Server` holds enable state, `http.Server`, mux, port, and dynamic handler map. `New` registers `/`, `/help`, and `/ready`. `Handle` and `HandleFunc` support handler replacement without re-registering mux patterns. `Enable`, `Shutdown`, `Enabled`, `ParseHTTPFormOptions`, and `HTTPReply` manage lifecycle and response formatting.

## Control Flow
`Enable` records the port, avoids double-start, creates an HTTP server with the diagnostic server as handler, and starts `ListenAndServe` in a goroutine. Registered mux wrappers lock and fetch the current handler. Default handlers parse form options, audit-log the command, and return plain text or JSON responses.

## State And Persistence
State is in-memory. No diagnostic data is persisted; handlers may expose state from other components.

## Dependencies And Integration Points
Used by libnetwork controller diagnostics and `networkdb-test`. Integrates with Go `net/http`, containerd logging, and diagnostic result types.

## Risks And Edge Cases
The server has no authentication and should remain bound to safe addresses; controller uses localhost while test server can listen broadly. Re-enabling on a new port while already enabled does not reconfigure. Read header timeout is intentionally long.

## Test Signals
Signals include `/ready` returning `OK`, `/help` listing handlers, JSON/plain formatting, handler replacement, enable/disable lifecycle, and audit logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/diagnostic/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/diagnostic/types.go -->
# sources/cloud-native/moby/daemon/libnetwork/diagnostic/types.go

## Purpose
Defines diagnostic response payloads and string renderers for libnetwork/networkdb HTTP diagnostics.

## Important APIs, Types, And Functions
`StringInterface` is the render contract. Constructors are `CommandSucceed`, `FailCommand`, and `WrongCommand`. Types include `HTTPResult`, `UsageCmd`, `StringCmd`, `ErrorCmd`, `TableObj`, `PeerEntryObj`, `TableEntryObj`, `TableEndpointsResult`, `TablePeersResult`, and `NetworkStatsResult`.

## Control Flow
Handlers create typed result objects, and `HTTPReply` in `server.go` renders either JSON or each object's `String` output. Table renderers print total counts plus entry lines.

## State And Persistence
No state; pure data structures.

## Dependencies And Integration Points
Used by diagnostic handlers and test clients that parse text phrases like `total entries` and `qlen`.

## Risks And Edge Cases
`NetworkStatsResult` has a typo in the JSON tag (`jsoin:"qlen"`), so JSON output will not use the intended `qlen` tag. `PeerEntryObj.Name` has an unusual tag `json:"-=name"`. The interface-typed `Details` can complicate JSON unmarshaling.

## Test Signals
Tests should cover plain text formatting, JSON tags, and compatibility with networkdb-test regex parsers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/diagnostic/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/discoverapi/discoverapi.go -->
# sources/cloud-native/moby/daemon/libnetwork/discoverapi/discoverapi.go

## Purpose
Defines the discovery notification interface and payload types used by network drivers to receive cluster node and encryption-key events.

## Important APIs, Types, And Functions
`Discover` exposes `DiscoverNew` and `DiscoverDelete`. `DiscoveryType` includes `NodeDiscovery`, `EncryptionKeysConfig`, and `EncryptionKeysUpdate`. Payloads include `NodeDiscoveryData`, `DriverEncryptionConfig`, and `DriverEncryptionUpdate`.

## Control Flow
There is no executable flow. Controller code detects drivers implementing `Discover` and sends add/delete events with these typed payloads.

## State And Persistence
No state; pure interface and data contracts.

## Dependencies And Integration Points
Used by controller node discovery and overlay/encryption integrations.

## Risks And Edge Cases
Payload fields are loosely typed through `any` in the interface, so drivers must type-assert correctly. Encryption key semantics rely on positional primary key/tag fields.

## Test Signals
Driver tests should assert expected discovery event types and payloads are delivered on cluster membership and key changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/discoverapi/discoverapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/docs/vagrant-systemd/docker.service -->
# sources/cloud-native/moby/daemon/libnetwork/docs/vagrant-systemd/docker.service

## Purpose
Systemd unit file used by libnetwork Vagrant documentation to run the Docker daemon with socket activation and optional `/etc/default/docker` options.

## Important APIs, Types, And Functions
The unit declares `After=network.target docker.socket`, `Requires=docker.socket`, `EnvironmentFile=-/etc/default/docker`, `ExecStart=/usr/bin/docker daemon -H fd:// $DOCKER_OPTS`, `MountFlags=slave`, and high process/file/core limits.

## Control Flow
Systemd starts Docker after the network target and required socket, passes file descriptor socket activation with `-H fd://`, and enables the unit under `multi-user.target`.

## State And Persistence
No repository state. Runtime daemon state is managed by Docker and systemd on the Vagrant host.

## Dependencies And Integration Points
Depends on systemd, `docker.socket`, `/usr/bin/docker`, and optional `/etc/default/docker`.

## Risks And Edge Cases
`docker daemon` is historical syntax and may be obsolete in newer Docker versions. `MountFlags=slave` is legacy systemd behavior. This is documentation support, not production packaging.

## Test Signals
In the documented Vagrant environment, `systemctl start docker` should launch the daemon and socket activation should work.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/docs/vagrant-systemd/docker.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi.go -->
# sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi.go

## Purpose
Defines libnetwork's Go interfaces between the controller and network drivers, optional driver capabilities, and network/endpoint information contracts.

## Important APIs, Types, And Functions
`Driver` covers network/endpoint create/delete, operational info, join/leave, type, and built-in status. Optional interfaces include `NetworkAllocator`, `TableWatcher`, `ExtConner`, `IPv6Releaser`, and `GwAllocChecker`. Info interfaces include `NetworkInfo`, `InterfaceInfo`, `InterfaceNameInfo`, and `JoinInfo`. `Registerer`, `Capability`, `IPAMData`, `ObjectType`, and `IsValidType` define registration and metadata contracts.

## Control Flow
The controller calls these interfaces during network creation, endpoint creation, sandbox join/leave, external connectivity changes, IPv6 release, and swarm allocation. Drivers call back into info interfaces to set MAC/IP/interface names, gateways, routes, and gossip table entries.

## State And Persistence
No direct state. Implementations may persist through driver stores, networkdb table entries, or controller datastore.

## Dependencies And Integration Points
This is the integration boundary for bridge, overlay, remote plugins, CNM allocator, networkdb table watching, and IPAM data exchange.

## Risks And Edge Cases
Interfaces are broad and some optional behavior is discovered by type assertion. Drivers must honor call ordering and rollback assumptions. `NetworkPluginEndpointType` ties Go contracts to plugin endpoint naming.

## Test Signals
Driver conformance tests, bridge/overlay integration tests, and remote plugin tests validate correct contract implementation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi_test.go -->
# sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi_test.go

## Purpose
Tests `IPAMData` JSON round-trip, validation, and IPv6 detection behavior.

## Important APIs, Types, And Functions
`TestIPDataMarshalling` marshals/unmarshals an `IPAMData` with pool, gateway, and aux addresses. `compareAddresses` compares aux address maps. `TestValidateAndIsV6` checks `IsV6` and validation failures for mismatched IP versions and out-of-pool gateway/aux addresses.

## Control Flow
Tests construct IPv4 and IPv6 CIDRs, mutate fields to invalid states, and expect `Validate` to fail or pass at each step.

## State And Persistence
No state beyond test objects.

## Dependencies And Integration Points
Exercises `types.ParseCIDR`, `types.CompareIPNet`, JSON methods in `ipamdata.go`, and driver API validation semantics used by drivers.

## Risks And Edge Cases
Coverage does not check nil pool/gateway error messages, JSON type assertion panics on malformed JSON, or `IPAMConfig` conversion.

## Test Signals
Passing tests show stable IPAMData serialization and validation for the main IPv4/IPv6 congruence cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/driverapi_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/errors.go -->
# sources/cloud-native/moby/daemon/libnetwork/driverapi/errors.go

## Purpose
Defines typed driver API errors that participate in Moby error classification through marker methods.

## Important APIs, Types, And Functions
`ErrNoNetwork` and `ErrNoEndpoint` implement `NotFound`. `ErrEndpointExists` and `ErrActiveRegistration` implement `Forbidden`. `ErrNotImplemented` implements `NotImplemented`. Each has an `Error` string.

## Control Flow
Driver and registry code return these errors; higher layers classify them through marker methods rather than string matching.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by network drivers, controller, and error-response layers that understand Moby error marker interfaces.

## Risks And Edge Cases
Error messages are human-readable but not structured. `ErrEndpointExists` says only one endpoint allowed, which may not describe every driver.

## Test Signals
Error classification tests should assert marker methods produce expected HTTP/API categories.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/ipamdata.go -->
# sources/cloud-native/moby/daemon/libnetwork/driverapi/ipamdata.go

## Purpose
Implements serialization, validation, string rendering, and API conversion for `driverapi.IPAMData`.

## Important APIs, Types, And Functions
`MarshalJSON`, `UnmarshalJSON`, `Validate`, `IsV6`, `String`, and `IPAMConfig` convert between internal `net.IPNet` data, JSON strings, and public `network.IPAMConfig` using `netip` addresses.

## Control Flow
Marshal omits nil fields and stringifies networks. Unmarshal decodes a map, parses CIDR strings, and rebuilds aux address maps. Validate requires pool and gateway, checks gateway/aux address IP versions match the pool, and ensures gateway/aux addresses belong to the pool. `IPAMConfig` converts pool/gateway/aux data to API netip form.

## State And Persistence
Pure value transformations; no persistent state.

## Dependencies And Integration Points
Used by driver API JSON exchange, network inspect output conversion, and tests in `driverapi_test.go`.

## Risks And Edge Cases
`UnmarshalJSON` uses unchecked type assertions for expected JSON field types, so malformed input can panic. The validation error for aux address outside pool formats the gateway instead of the offending aux address in one message.

## Test Signals
Round-trip, validation, and API conversion tests are the key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/driverapi/ipamdata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux.go -->
# sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux.go

## Purpose
Linux bridge network driver implementation. It creates bridge networks and veth endpoints, configures IPv4/IPv6 gateway behavior, programs firewall/NAT/port mappings, persists bridge state, and integrates with libnetwork driver APIs.

## Important APIs, Types, And Functions
Key types are `Configuration`, `networkConfiguration`, `bridgeEndpoint`, `bridgeNetwork`, `driver`, and `gwMode`. Registration and setup functions include `Register`, `newDriver`, `newFirewaller`, `parseNetworkOptions`, `processIPAM`, `Validate`, `Conflicts`, `CreateNetwork`, `createNetwork`, and `DeleteNetwork`. Endpoint and connectivity APIs include `CreateEndpoint`, `createVeth`, `Join`, `Leave`, `DeleteEndpoint`, `EndpointOperInfo`, `ProgramExternalConnectivity`, `ReleaseIPv6`, `trimPortBindings`, `clearConntrackEntries`, `handleFirewalldReload`, and legacy `link` handling.

## Control Flow
Driver registration optionally runs in a RootlessKit netns, initializes firewaller backend, restores store state, and registers reload callbacks. Network creation parses labels/options, validates subnets/gateway modes, checks conflicts under a config lock, creates or reuses a bridge interface, queues setup steps for devices, MTU, sysctls, IPv4/IPv6, forwarding, bridge netfilter, firewall network, and device up, then persists config. Endpoint creation creates host/container veth names, tries to place the peer in the container netns, sets MTU, enslaves host veth to the bridge, enables hairpin when proxy is disabled, sets MAC/IP data, adds endpoint firewall rules, brings the link up, and stores endpoint state. External connectivity computes gateway roles, trims stale bindings, maps ports, clears conntrack, and stores operational bindings.

## State And Persistence
In-memory driver state maps network IDs to `bridgeNetwork` objects and endpoint maps. Persistent state is stored through `datastore.Store` for network configurations and endpoints. Kernel/network state includes bridge devices, veth links, sysctls, forwarding, firewall rules, conntrack entries, firewalld zone membership, and portmapper allocations.

## Dependencies And Integration Points
Integrates with libnetwork `driverapi`, datastore, bridge firewaller implementations (`iptabler` or `nftabler`), iptables/firewalld, netlink/netns, RootlessKit, portmapper registry, network labels, IPAM data, OpenTelemetry tracing, and OSL namespace setup.

## Risks And Edge Cases
This file has high privilege and cleanup risk: partial failures must unwind kernel links, firewall rules, port bindings, and store records. Lock ordering across `driver.mu`, `configNetwork`, and per-network locks matters. Existing user-created bridges are not deleted. Firewalld reload reapplication must avoid races with network deletion and port updates. Rootless netns fallback and failed container-netns placement create host-netns peer behavior that callers must handle.

## Test Signals
Bridge driver tests should cover network option parsing, IPv6 CIDR validation, conflict detection, bridge creation/reuse/delete, endpoint create/delete, port mapping, routed/NAT gateway modes, firewalld reload, conntrack cleanup, live-restore persistence, and rootless behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/drivers/bridge/bridge_linux.go -->
