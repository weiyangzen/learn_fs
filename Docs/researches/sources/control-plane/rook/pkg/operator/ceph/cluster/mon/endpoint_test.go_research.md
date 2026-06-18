# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/endpoint_test.go

## Purpose

This file tests serialization of monitor endpoint maps into the ConfigMap string format and verifies that the result can be parsed back into monitor endpoint objects.

## Important APIs and Test Flow

`TestMonFlattening` starts with one monitor named `foo` at `1.2.3.4:5000`, calls `flattenMonEndpoints()`, expects the exact single-entry string, then parses it with `controller.ParseMonEndpoints()` and validates the parsed name and endpoint. It then adds `bar` at `2.3.4.5:6000`, flattens again, parses again, and validates that both monitors are present.

## State, Dependencies, and Integration

The test uses in-memory `map[string]*cephclient.MonInfo` values and the production parser from the controller package. This is an integration-style unit test for the writer and reader of the mon endpoints ConfigMap data format.

## Risks and Test Signals

The single-monitor assertion is exact because ordering is deterministic with one item. The multi-monitor part validates parsed map contents instead of raw string order, which is necessary because map iteration order is nondeterministic. The test would catch incompatible changes to the `name=endpoint` pair format or parser assumptions.
