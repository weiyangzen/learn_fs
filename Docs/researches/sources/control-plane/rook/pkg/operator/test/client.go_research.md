# sources/control-plane/rook/pkg/operator/test/client.go

## Purpose
`client.go` provides reusable fake Kubernetes client helpers for Rook operator unit tests.

## Important APIs, Types, and Functions
`New()` creates a fake clientset with ready nodes. `AddReadyNode()` and `AddSomeReadyNodes()` seed nodes with hostname labels, ready conditions, and internal IPs. `SetFakeKubernetesVersion()` configures fake discovery version info. `NewComplexClientset()` adds a generateName reactor. `PrependComplexJobReactor()` mirrors job-to-pod creation/deletion and optional node assignment. `PrependFailReactor()` injects failures. `FakeOperatorPod()`, `FakeReplicaSet()`, and `FakeCustomisePodCreate()` build common test objects.

## Control Flow, State, and Persistence
All state is in client-go fake object trackers and reactors. `pickNodeIdx` is package-global and advances round-robin across calls. Reactors mutate objects before default handling or manipulate the tracker directly to avoid fake-client locks.

## Dependencies and Integration Points
It depends on Kubernetes fake clientsets, testing reactors, metadata accessors, UUID/base32 generation, and core/apps/batch APIs. It is used broadly by operator unit tests that need more realistic fake cluster behavior.

## Risks
`AddReadyNode()` logs already-exists but still panics because the panic is unconditional after the log. Global `pickNodeIdx` can leak ordering between tests. Generated names are random, so tests should not assert exact suffixes. Reactor logic only approximates Kubernetes behavior.

## Test Signals
No direct tests are mapped for this helper. Downstream tests exercise ready-node creation, job pod creation/deletion, version discovery, and failure reactors.
