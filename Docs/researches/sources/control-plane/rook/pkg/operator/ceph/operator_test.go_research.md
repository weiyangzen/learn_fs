# sources/control-plane/rook/pkg/operator/ceph/operator_test.go

## Purpose

This file smoke-tests construction of the top-level Ceph `Operator`.

## Important Test Cases

- `TestOperator` creates a fake Kubernetes clientset, wraps it in a `clusterd.Context`, calls `New`, and asserts the operator, cluster controller, resource list, and stored context are initialized correctly.
- It verifies the only registered resource is `opcontroller.ClusterResource`.

## Control Flow and Test Setup

The test uses `operator/test.New(t, 3)` to create a fake clientset and passes empty image/service-account values to `New`. It iterates over `o.resources` and fails if any resource name differs from the cluster resource name.

## State and Persistence Signals

No Kubernetes objects are created by the operator in this test. It validates in-memory constructor state only.

## Dependencies and Integration Points

The test depends on `clusterd.Context`, `opcontroller.ClusterResource`, Rook operator test helpers, and `testify/assert`.

## Risks and Gaps

The test does not cover `Run`, `runCRDManager`, SIGHUP reload, shutdown signals, settings ConfigMap loading, namespace watch selection, or controller manager startup. It is useful as a constructor regression test but does not validate operator runtime behavior.

## Test Signals

The file confirms that `New` wires the basic operator structure and resource list. Runtime lifecycle correctness must be inferred from other tests or integration coverage.
