# sources/control-plane/juicefs-csi-driver/pkg/config/batch_config_test.go

Purpose: verifies batch upgrade ordering and node-selector-aware setting diffs.

Important tests: `TestNewBatchConfig` checks batching by `Parallel` and deterministic sorting by node then `common.UniqueId`. Scenarios cover normal two-pod input, multiple nodes, and different unique IDs. `TestGetDiffWithNodeRespectsNodeSelector` saves/restores `GlobalConfig`, applies a node selector patch, and verifies labels appear only for matching node context.

Control flow/state: fixtures are direct `corev1.Pod` and `corev1.Node` objects. No Kubernetes API calls are made. Process-global `GlobalConfig` is the only mutated state and is restored.

Dependencies/integration: uses `testify/assert`, Kubernetes core/meta types, and common constants. It indirectly exercises `RevertSettingWithNode`, `ReNew`, and patch matching.

Risks/gaps: does not test `ignoreError`, `NoRecreate`, node/unique filters, CSI node mapping, empty input, invalid `parallel`, ConfigMap CRUD, or malformed upgrade JSON.

Test signal: good for ordering and recent node selector behavior; limited for persistence.
