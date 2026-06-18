<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/doc.go

Purpose: package documentation for RBD Kubernetes deployment artifact helpers. It exposes the package as a Go-consumable way to get recommended RBD CSI manifests. No runtime logic or state is present; integration is through generated ConfigMap, CSIDriver, and for NFS RBAC helpers.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/doc.go -->
