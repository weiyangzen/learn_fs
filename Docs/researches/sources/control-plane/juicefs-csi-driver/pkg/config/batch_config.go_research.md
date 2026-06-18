# sources/control-plane/juicefs-csi-driver/pkg/config/batch_config.go

Purpose: models batch upgrade plans for mount pods and persists them in a Kubernetes ConfigMap. It also provides a setting-diff helper for upgrade comparison.

Important types/functions: `BatchConfig` stores parallelism, error behavior, recreation policy, node/unique ID filters, batches, and status. `MountPodUpgrade` records pod name, node, CSI node pod, and status. `NewBatchConfig` sorts pods by node and `common.UniqueId`, then groups them into fixed-size batches. `LoadUpgradeConfig`, `LoadBatchConfig`, `CreateUpgradeConfig`, and `UpdateUpgradeConfig` manage the `upgrade` JSON payload in ConfigMaps. `GetDiffWithNode` computes old and renewed sanitized settings.

Control flow and persistence: upgrade state is serialized as JSON under `cm.Data["upgrade"]` in `config.Namespace`, labeled as a JuiceFS config object. Create refuses overwrite; update requires an existing ConfigMap.

Dependencies and integration: uses Kubernetes ConfigMaps/API errors, `pkg/k8sclient`, common labels, and `setting.go` reconstruction/renewal paths.

Risks: `parallel <= 0` is not guarded and can panic. Missing CSI node pods produce empty `CSINodePod`. Loading assumes the `upgrade` key exists and is valid JSON. ConfigMap CRUD error branches are mostly caller-facing.

Test signals: tests cover deterministic ordering/batching and node-aware diff labels, but not ConfigMap persistence or invalid parallel/JSON cases.
