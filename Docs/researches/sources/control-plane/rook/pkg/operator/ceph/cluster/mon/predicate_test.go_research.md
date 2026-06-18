# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/predicate_test.go

## Purpose
This file provides focused table-driven tests for monitor endpoint mapping change detection.

## Important APIs, Types, And Functions
`TestWereMonEndpointsUpdated` calls `wereMonEndpointsUpdated("ns", oldCMData, newCMData)` directly with ConfigMap-like data maps. Test cases cover absent old mapping, absent new mapping, identical JSON content, identical schedules in different JSON/map order, same number of monitors with one changed IP address, and different schedule length.

## Control Flow And State
The tests do not create Kubernetes objects. They provide raw map data to isolate the JSON comparison helper. State is represented entirely by the `mapping` key containing serialized `opcontroller.Mapping` JSON.

## Dependencies And Integration Points
The file depends only on Go testing and package-local monitor code. It indirectly validates the data format produced by monitor endpoint persistence because it uses JSON strings shaped like `{"node":{...}}`.

## Risks And Test Signals
The tests confirm order-insensitive comparison and ensure missing mapping fields do not trigger endpoint updates. They also show that endpoint update detection is scoped to the schedule mapping, not the endpoint string. Malformed JSON is not covered here, though the implementation logs and returns false in that path.
