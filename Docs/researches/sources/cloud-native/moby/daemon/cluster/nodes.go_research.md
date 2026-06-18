# Research: sources/cloud-native/moby/daemon/cluster/nodes.go

## sources/cloud-native/moby/daemon/cluster/nodes.go

Purpose: implements node list, inspect, update, and remove operations for the swarm backend API.

Important APIs: `GetNodes`, `GetNode`, `UpdateNode`, and `RemoveNode`. Control flow validates/list-builds filters with `newListNodesFilters`, calls SwarmKit control RPCs under `lockedManagerAction`, converts returned nodes with `convert.NodeFromGRPC`, resolves node names/IDs through `getNode`, converts API node specs to protobuf specs, applies versioned updates, and removes nodes with optional force.

State is remote SwarmKit node store state; there is no local persistence. Dependencies are daemon swarm backend option types, cluster convert helpers, errdefs, SwarmKit control client, and gRPC receive-size limits. Risks include manager-availability requirements from `lockedManagerAction`, ambiguous name/prefix resolution, and update conflicts through version mismatches. Test coverage is indirect.
