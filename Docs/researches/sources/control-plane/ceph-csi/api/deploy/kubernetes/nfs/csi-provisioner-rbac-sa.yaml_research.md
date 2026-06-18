<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-sa.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-sa.yaml

Purpose: embedded ServiceAccount manifest for the NFS provisioner. It templates metadata name and namespace. It is used by YAML output while `NewCSIProvisionerRBAC` constructs an equivalent object directly. Risk is direct-construction/template drift; tests do not call `newServiceAccount`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-sa.yaml -->
