<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/doc.go

Purpose: package documentation for Kubernetes deployment artifact helpers. It frames this package as a Go API for automation that deploys Ceph CSI. No runtime logic or state is present; integration is through exported types like `ClusterInfo` and provisioner RBAC interfaces.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/doc.go -->
