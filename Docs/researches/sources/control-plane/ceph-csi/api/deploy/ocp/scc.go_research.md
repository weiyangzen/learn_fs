<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc.go -->
# sources/control-plane/ceph-csi/api/deploy/ocp/scc.go

Purpose: renders OpenShift SecurityContextConstraints for Ceph CSI service accounts.
Important APIs/functions: `SecurityContextConstraintsValues`, `SecurityContextConstraintsDefaults`, `NewSecurityContextConstraints`, `NewSecurityContextConstraintsYAML`, and internal value wrapper adding `Prefix` from optional `Deployer`.
Control flow/state: embeds `scc.yaml`, computes prefix when deployer is non-empty, templates YAML, and unmarshals into OpenShift `security/v1.SecurityContextConstraints`. No persistent state.
Dependencies/integration: requires OpenShift API dependency and is used by deployers such as Rook that need prefixed service accounts.
Risks/test signals: SCC is highly privileged and user list must stay aligned with chart/deployment service account names; tests verify default and rook prefixes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc.go -->
