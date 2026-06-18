# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/endpoint.go

## Purpose

This file provides the string serialization helper for monitor endpoints stored in Rook's mon endpoint ConfigMap and consumed by other Rook/Ceph components.

## Important APIs and Behavior

`flattenMonEndpoints(mons map[string]*cephclient.MonInfo)` iterates over monitor info values and returns a comma-delimited string of `name=endpoint` pairs. Each endpoint uses the `MonInfo.Name` and `MonInfo.Endpoint` fields. The format is the inverse of `controller.ParseMonEndpoints()` used elsewhere in the operator.

## State, Persistence, and Dependencies

The helper itself is stateless, but its output becomes persistent data in `rook-ceph-mon-endpoints` under the `data` key. That ConfigMap is then used for daemon connection config, env vars, CSI config, and reconciliation. Dependencies are minimal: standard string formatting/joining and the Ceph client's `MonInfo` type.

## Risks and Test Signals

Because Go map iteration order is intentionally nondeterministic, callers and tests must treat the endpoint list as an unordered set. The format is also delimiter-sensitive: monitor names and endpoints must not contain comma or equals characters in unexpected positions. `endpoint_test.go` validates round-tripping through `controller.ParseMonEndpoints()` for one and two monitors without assuming ordering for the multi-monitor case.
