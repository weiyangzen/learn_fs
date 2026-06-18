# sources/cloud-native/moby/daemon/network.go

## Purpose
This file implements daemon network management: lookup, create/delete, swarm ingress handling, plugin refcounting, IPAM validation/conversion, network listing/inspection projection, attachable cleanup, endpoint option construction, port mapping extraction, endpoint info persistence, and join options.

## Important APIs, Types, And Functions
Major APIs include `NetworkController`, `FindNetwork`, `GetNetworkByID`, `GetNetworkByName`, `CreateNetwork`, `createNetwork`, `DeleteNetwork`, `GetNetworks`, `GetNetworkSummaries`, `buildNetworkResource`, `buildCreateEndpointOptions`, `buildPortsRelatedCreateEndpointOptions`, `buildEndpointInfo`, and `buildJoinOptions`. `PredefinedNetworkError` is a forbidden error for attempts to create predefined networks. `ingressJob` and global ingress worker variables serialize ingress network operations.

## Control Flow
Network lookup scans libnetwork state by full ID, full name, or unambiguous partial ID. Creation runs in the network namespace, rejects predefined networks, resolves default driver, forbids non-manager overlay creation unless agent-driven, merges default driver options, resolves IPv4/IPv6 flags, validates and converts IPAM, appends internal/agent/config options, optionally attaches LB endpoint IPs, calls `libnetwork.NewNetwork`, acquires plugin refs, and emits create events. Deletion validates predefined/dynamic rules, calls `nw.Delete`, releases plugin refs, and emits destroy events. Listing filters networks and builds API resources including containers, services, peers, IPAM, and optional status.

## State, Persistence, And Dependencies
Persistent network state is owned by libnetwork. This file mutates plugin refcounts, cluster attachment store usage, container network settings, and daemon/network events. Dependencies include libnetwork controller/network/endpoint APIs, swarm cluster provider, networkdb peer info, driver/IPAM plugin endpoints, Docker API network/container types, filters, netip utilities, and OpenTelemetry baggage for ingress setup.

## Integration Points
This is the main integration boundary between Docker daemon API methods, swarm-managed networks, libnetwork, plugin management, network filters, container network settings, port mappings, endpoint driver info, and daemon events.

## Risks And Edge Cases
IPAM validation rejects host bits, out-of-subnet gateways/aux addresses, mismatched address families, and IP ranges larger than their subnet, but agent-created existing swarm networks log and continue for upgrade compatibility. `FindNetwork` must preserve libnetwork `ErrNoSuchNetwork` wrapping for controller retry behavior. Port mapping options are skipped for internal networks or sandboxes already carrying port map info. Build functions tolerate missing endpoint info. Ingress operations rely on global worker state and stale ID cleanup.

## Test Signals
`network_test.go` directly covers IPAM validation edge cases. `network/filter_test.go` covers filtering used by list/prune paths. Broader create/delete/endpoint behavior depends on daemon integration tests.
