<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/doc.go

Purpose: package documentation for deployment artifact helpers. It defines `deploy` as the namespace for functions returning standard/recommended manifests for container platforms. No functions or state live here; it integrates through subpackages such as Kubernetes and OCP. Test signal is documentation/build inclusion.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/doc.go -->
