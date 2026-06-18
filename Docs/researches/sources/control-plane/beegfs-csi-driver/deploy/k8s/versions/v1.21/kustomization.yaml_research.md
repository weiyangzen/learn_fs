<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/versions/v1.21/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/versions/v1.21/kustomization.yaml

Purpose: version-specific Kustomize entry point for Kubernetes v1.21-compatible deployment manifests.

Important APIs and flow: declares `apiVersion: kustomize.config.k8s.io/v1beta1`, `kind: Kustomization`, and includes `../../bases` as its only base. It delegates all object content to the shared base tree.

State and persistence: no direct cluster state beyond the rendered base resources; this file selects a render path.

Dependencies and integration points: depends on Kustomize and the relative `deploy/k8s/bases` directory remaining compatible with v1.21.

Risks and test signals: the file warns not to modify because version overlays may be regenerated. Test with `kustomize build deploy/k8s/versions/v1.21` and Kubernetes v1.21 server dry-run.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/versions/v1.21/kustomization.yaml -->
