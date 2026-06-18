# sources/cloud-native/moby/daemon/cluster/executor/backend.go

## Purpose
Defines the daemon backend interfaces required by the swarm executor to manage networks, containers, images, volumes, plugins, events, attachments, and cluster membership.

## Important APIs, Types, And Functions
Defines `Backend`, `VolumeBackend`, and `ImageBackend` interfaces. Methods cover managed network lifecycle, ingress setup/release, managed container lifecycle/logs/wait/remove, service binding, dependency/secrets/config refs, system info, event subscriptions, attachment operations, plugin access, compatibility, and image pull/lookup.

## Control Flow
No implementation; this is an interface boundary.

## State And Persistence
No state. Implementations mutate daemon, container, network, image, and volume state.

## Dependencies And Integration Points
Bridges swarmkit agent controllers to the Docker daemon backend. Referenced by container adapters and cluster construction.

## Risks And Test Signals
Interface churn has broad compile impact. Because this is a large boundary, mocks and daemon implementations must stay synchronized. Tests in executor/container exercise selected methods.
