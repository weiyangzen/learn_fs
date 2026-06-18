# sources/cloud-native/moby/daemon/server/networkbackend/network.go

## Purpose
Defines request structs for connecting and disconnecting containers from networks.

## Important APIs, Types, And Functions
`ConnectRequest` includes a container identifier and optional `EndpointConfig`. `DisconnectRequest` includes a container identifier and force flag.

## Control Flow
Type definitions only.

## State And Persistence
No state is changed; daemon network backend methods consume these values to mutate network attachments.

## Dependencies And Integration Points
Used by network API routers. Depends on Docker API network endpoint settings.

## Risks And Edge Cases
Validation of container name, endpoint config, and force behavior is left to route/backends.

## Test Signals
Network route and daemon network integration tests validate these request shapes.
