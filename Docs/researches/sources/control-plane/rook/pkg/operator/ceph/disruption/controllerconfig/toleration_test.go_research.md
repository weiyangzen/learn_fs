# sources/control-plane/rook/pkg/operator/ceph/disruption/controllerconfig/toleration_test.go

## Purpose
This test validates the `controllerconfig.TolerationSet` helper used by disruption-controller configuration. It confirms that Kubernetes `corev1.Toleration` values are treated as unique by their full comparable struct value and that duplicates can be collapsed without losing semantically distinct tolerations.

## Important APIs, Types, and Functions
The only test entry point is `TestTolerationSet`. It builds two identical manual slices of `corev1.Toleration`, injects duplicates in shuffled adjacency, calls `(*TolerationSet).Add` repeatedly, and inspects `TolerationSet.ToList()`. The cases cover different keys, `Exists` versus `Equal` operators, different `Value` fields, and different taint effects including `NoSchedule`, `PreferNoSchedule`, and `NoExecute`.

## Control Flow, State, and Persistence
The test constructs an in-memory duplicate list by alternating each unique toleration with another toleration from the matching reference slice. It inserts all values into a fresh `TolerationSet`, converts the set back to a list, asserts the unique count, and does an order-independent membership check. No Kubernetes API state or persisted artifacts are involved.

## Dependencies and Integration Points
The file depends on Kubernetes core API toleration structs and `testify/assert`. It indirectly protects any controller code that stores tolerations through `TolerationSet`, especially code that merges tolerations from disruption or controller configuration.

## Risks
The test assumes `corev1.Toleration` remains Go-comparable. If future Kubernetes fields make the struct non-comparable, both the implementation and this equality-based test will need redesign. The test does not assert deterministic output ordering, which is appropriate for set semantics but means consumers must not rely on ordering from `ToList()`.

## Test Signals
Useful signals are exact unique cardinality and presence of every manual reference toleration after duplicate insertion. The test is strongest for full-struct uniqueness and weaker for serialization or ordering behavior.
