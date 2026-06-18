# sources/control-plane/external-snapshotter/client/config/crd/kustomization.yaml

Purpose: kustomize entry point for installing snapshot and group snapshot CRDs.
Important APIs/types/functions: `apiVersion: kustomize.config.k8s.io/v1beta1`, `kind: Kustomization`, and six resources: volume snapshot classes/contents/snapshots plus group snapshot classes/contents/snapshots.
Control flow: kustomize reads the resource list and emits all referenced CRD YAMLs in order.
State/persistence: no runtime state; applying the rendered output creates/updates CRDs in the cluster.
Dependencies/integration: used by deployment/install flows for the external-snapshotter client CRDs.
Risks/test signals: this work item researches five referenced CRDs but not `snapshot.storage.k8s.io_volumesnapshots.yaml`; kustomize still depends on that file at install time. Tests should run `kustomize build` or `kubectl kustomize` and server-side dry-run apply.
