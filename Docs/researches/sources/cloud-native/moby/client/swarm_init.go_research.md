# sources/cloud-native/moby/client/swarm_init.go

## Purpose
Implements swarm initialization, converting client options into daemon `swarm.InitRequest` payloads and returning the new node ID.

## APIs, Types, And Functions
`SwarmInitOptions` embeds `swarm.InitRequest`; `SwarmInitResult` contains the daemon response string; `Client.SwarmInit` performs the request. It depends on JSON decode and swarm types, including `net/netip` fields in init configuration.

## Control Flow, State, And Integration
The method posts the supplied init request to `/swarm/init`, decodes the daemon response as a string node ID, and closes the response body. It initializes persistent swarm cluster state in the daemon.

## Risks And Test Signals
Risks include request-shape drift with swarm API types, decode errors for the string response, and daemon-side irreversible cluster initialization. Integration is with swarm manager bootstrap and network address configuration.
