# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/util.go

## Purpose
This file contains small monitor utility functions for quorum lookup, monitor ID parsing, and service port construction.

## Important APIs, Types, And Functions
`monInQuorum(monitor, quorum)` checks whether a monitor map entry's rank appears in a quorum rank slice. `getMonByID(monID, monMap)` returns the monitor map entry and in-quorum flag for a named monitor. `fullNameToIndex(name)` converts monitor names such as `rook-ceph-mon-a` or `b` into numeric indices using `k8sutil.NameToIndex()`. `addServicePort(service, name, port)` appends a TCP service port unless the port is zero.

## Control Flow And State
All functions are pure or local-object mutators. `getMonByID` scans the Ceph monitor status response and uses `slices.Contains` on quorum ranks. `fullNameToIndex` trims the monitor app prefix and separator before converting. `addServicePort` mutates only the passed `Service` object before it is submitted to Kubernetes.

## Dependencies And Integration Points
The utilities depend on Ceph client monitor status structures, Kubernetes Service types, Rook name conversion, and `intstr` target ports. They are used by monitor health/quorum code and service creation.

## Risks And Test Signals
The main risk is monitor name parsing: legacy numeric resource names are intentionally invalid for the new alphabetic index conversion path. `mon_test.go` covers `monInQuorum` and `fullNameToIndex`. Service port behavior is indirectly exercised through service and monitor startup paths.
