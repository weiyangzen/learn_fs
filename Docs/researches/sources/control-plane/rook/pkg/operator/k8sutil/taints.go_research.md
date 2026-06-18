# sources/control-plane/rook/pkg/operator/k8sutil/taints.go

## Purpose
`taints.go` identifies Kubernetes-managed taints that Rook may choose to ignore when evaluating node placement.

## Important APIs, Types, and Functions
`WellKnownTaints` lists node not-ready, unreachable, unschedulable, pressure, network unavailable, external cloud provider, and shutdown taints. `TaintIsWellKnown()` checks whether a `v1.Taint` key is in that list.

## Control Flow, State, and Persistence
The logic is a simple in-memory linear scan over a package-level slice. There is no external state.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 taint constants and cloud-provider taint constants. `NodeIsTolerable()` in `node.go` uses it when `ignoreWellKnownTaints` is true.

## Risks
The well-known list can drift as Kubernetes adds taints. Effects and values are ignored; only the key matters. Linear scan is fine for the small list.

## Test Signals
Coverage is indirect through `node_test.go`, which creates all `WellKnownTaints` and checks toleration behavior with and without ignore mode. There is no standalone test for `TaintIsWellKnown()`.
