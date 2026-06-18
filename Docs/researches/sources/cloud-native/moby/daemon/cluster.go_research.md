# sources/cloud-native/moby/daemon/cluster.go

## Purpose
Defines narrow daemon-facing interfaces for swarm cluster status, events, and network management without importing the concrete cluster implementation everywhere.

## Important APIs, Types, And Functions
Defines interfaces `Cluster`, `ClusterStatus`, and `NetworkManager`. `Cluster` embeds status and network manager capabilities and adds `SendClusterEvent`.

## Control Flow
No executable control flow; this is a contract file.

## State And Persistence
No state. Implementations provide live swarm status and network mutations.

## Dependencies And Integration Points
References API network inspection types, libnetwork cluster event types, and daemon network filters. The concrete implementation is `daemon/cluster.Cluster`.

## Risks And Test Signals
Interface changes ripple into daemon wiring and mocks. No tests directly target this file; compile-time conformance across daemon packages is the signal.
