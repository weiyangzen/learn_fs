# sources/cloud-native/moby/daemon/cluster/convert/node.go

## Purpose
Converts swarmkit nodes and node specs to Docker API swarm node types.

## Important APIs, Types, And Functions
Exports `NodeFromGRPC` and `NodeSpecToGRPC`.

## Control Flow
`NodeFromGRPC` copies ID, role, availability, status, metadata timestamps, annotations, platform/resources/generic resources, engine labels/plugins, TLS info, CSI info including topology, and manager status. `NodeSpecToGRPC` converts annotations and validates role/availability enum strings before constructing a swarmkit `NodeSpec`.

## State And Persistence
No local state. Converts data persisted in swarmkit raft.

## Dependencies And Integration Points
Used by node API handlers. Depends on shared `GenericResourcesFromGRPC`, annotations conversion, gogo timestamps, and swarmkit enum naming.

## Risks And Test Signals
Outbound invalid role or availability returns errors. Inbound enum strings are lower-cased, so unknown enum names can leak as API strings. `node_test.go` covers CSI info conversion.
