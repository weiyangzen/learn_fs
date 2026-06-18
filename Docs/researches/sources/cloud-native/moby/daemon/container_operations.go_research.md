# sources/cloud-native/moby/daemon/container_operations.go

## Purpose
Implements common daemon container networking operations: sandbox option construction, network setting normalization, endpoint validation, network attach/detach, sandbox initialization and release, service-binding activation, and connect/disconnect API behavior.

## Important APIs, Types, And Functions
- `buildSandboxOptions` builds libnetwork sandbox options from host config, daemon DNS settings, extra hosts, exposed ports, port bindings, publish-all settings, and platform options.
- `updateNetworkSettings`, `updateContainerNetworkSettings`, `updateNetworkConfig`, and `buildEndpointDNSNames` maintain container endpoint maps and DNS names.
- `findAndAttachNetwork`, `connectToNetwork`, `disconnectFromNetwork`, and `tryDetachContainerFromClusterNetwork` integrate local libnetwork state with swarm attachable networks.
- `initializeNetworking`, `allocateNetwork`, `updateNetwork`, and `releaseNetwork` manage sandbox lifecycle.
- `validateEndpointSettings`, `normalizeEndpointIPAMConfig`, and `validateIPAMConfigIsInRange` enforce IPAM rules.
- Public methods include `ConnectToNetwork`, `DisconnectFromNetwork`, `ForceEndpointDelete`, and service-binding activation/deactivation wrappers.

## Control Flow
Creation/start calls initialize networking, destroy stale sandboxes, handle `--network container:` path sharing, set hostnames for host networking, create a sandbox, and later connect endpoint configs. Runtime connect resolves or attaches dynamic networks, normalizes host network restrictions, validates static IP/MAC/sysctl settings, creates an endpoint, joins it to the sandbox, updates operational endpoint data, activates DNS/service binding for unmanaged containers, writes port info, logs events, and checkpoints container state. Disconnect reverses endpoint membership, updates port info, removes endpoint settings, detaches cluster networks, logs events, and checkpoints.

## State And Persistence
Mutates `ctr.NetworkSettings`, including sandbox ID/key, endpoint maps, operational IP/MAC/gateway fields, swarm endpoint flags, port maps, and desired MAC addresses. `ConnectToNetwork` and `DisconnectFromNetwork` persist changes through `CheckpointTo(daemon.containersReplica)`. Operational endpoint data is cleaned before reallocation and on release.

## Dependencies And Integration Points
Depends on libnetwork, daemon network lookup, swarm `clusterProvider`, daemon config, Moby network API types, metrics, events, OpenTelemetry spans, and platform helpers from `container_operations_unix.go`/`_windows.go`. It is central to `docker run`, `start`, `network connect`, `network disconnect`, live restore cleanup, and service discovery.

## Risks And Edge Cases
Rollback paths must keep libnetwork endpoints, swarm attachments, and container maps consistent after partial failures. Extra-host `host-gateway` requires daemon-level gateway IPs. Default/predefined network IP and alias support differs by platform. Dynamic network attach races are retried only for a bounded set of no-such-network cases. Platform deletion with force and namespace-sharing modes require careful restriction to avoid connecting host/container namespace users to extra networks.

## Test Signals
`container_operations_test.go` covers DNS name ordering and IPAM validation. Wider coverage is expected from integration tests for network connect/disconnect, swarm attachable networks, links, port mappings, and host/container namespace modes.
