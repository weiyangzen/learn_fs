<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/doc.go -->
# sources/control-plane/ceph-csi/api/doc.go

Purpose: root package documentation for the public Ceph CSI API module. It declares package `api` as the consumable surface for deployment artifacts across container platforms. There is no runtime control flow or persistent state. Integration is through Go documentation/import boundaries; risk is only stale package description if exported APIs expand.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/doc.go -->
