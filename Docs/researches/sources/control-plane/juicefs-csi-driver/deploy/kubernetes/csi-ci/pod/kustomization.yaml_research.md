<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/kustomization.yaml

## Purpose
Defines a Kustomize overlay for the JuiceFS CSI driver deployment in `kube-system`. It composes `../../release` and applies deployment-mode-specific patches rather than defining runtime resources from scratch. This CI variant exercises `pod` behavior.

## Important APIs, Types, and Resources
The important API is `kustomize.config.k8s.io/v1beta1` `Kustomization`. Key fields are `namespace: kube-system`, `resources`, and `patches`; patches target Kubernetes workload or RBAC kinds by kind/name.

## Control Flow
`kustomize build` first loads `../../release`, then applies the listed patch files or inline `$patch: delete` documents. This file is therefore control-plane assembly logic: changing patch order or target selectors changes the rendered manifests used by CI or release installs.

## State and Persistence
The file stores no runtime state itself. Its effects persist only when rendered into Kubernetes YAML and applied to the cluster; then the resulting StatefulSet, DaemonSet, RBAC, service, or webhook resources become cluster state.

## Dependencies and Integration Points
Depends on Kustomize strategic merge and JSON6902 patch semantics, Kubernetes API object identity, and the base/release manifests in neighboring directories. It integrates with generated top-level deploy YAMLs and install scripts.

## Risks
Risks are stale patch targets after base resource renames, namespace mismatches with system priority classes, and silent behavioral drift if `pod/daemonset.yaml and pod/statefulset.yaml` no longer matches the intended deployment mode.

## Test Signals
Useful checks are `kustomize build` for this overlay, schema validation with `kubectl apply --dry-run=server`, and diffing rendered output against the committed generated deploy YAML where applicable.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/pod/kustomization.yaml -->
