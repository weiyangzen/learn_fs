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
