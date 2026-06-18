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
