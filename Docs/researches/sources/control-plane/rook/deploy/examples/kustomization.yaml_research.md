<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/kustomization.yaml -->
# sources/control-plane/rook/deploy/examples/kustomization.yaml

Purpose: Kustomize entry point that composes Rook example manifests.
Important APIs/types/functions: `apiVersion: kustomize.config.k8s.io/v1beta1`, `kind: Kustomization`, and `resources` pointing at `crds.yaml`, `common.yaml`, `operator.yaml`, and `cluster.yaml`.
Control flow: `kubectl apply -k` or `kustomize build` expands the listed resources in order into a deployable Rook example stack. State is not held by this file; it controls apply composition. Dependencies are the referenced files in the examples directory and Kustomize support in the client. Risks: only the base cluster path is included, not CSI examples in this research item; referenced files must exist relative to this file. Test signals: `kubectl kustomize` renders successfully and applying the output creates CRDs, common RBAC, operator, and cluster resources.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/kustomization.yaml -->
