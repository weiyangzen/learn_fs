# sources/cloud-native/moby/daemon/cluster/convert/node_test.go

## Purpose
Tests conversion of swarmkit `NodeCSIInfo` entries into Docker API `NodeCSIInfo` structures.

## Important APIs, Types, And Functions
Defines `TestNodeCSIInfoFromGRPC`, targeting `NodeFromGRPC`.

## Control Flow
The test builds a swarmkit node with two CSI entries, one with accessible topology, converts it, and deep-compares the resulting Docker API slice.

## State And Persistence
No state.

## Dependencies And Integration Points
Direct coverage for CSI node description conversion used by `docker node inspect`.

## Risks And Test Signals
Does not test nil entries, manager status, resources, or spec conversion. Failure indicates loss of CSI plugin/node/topology fields.
