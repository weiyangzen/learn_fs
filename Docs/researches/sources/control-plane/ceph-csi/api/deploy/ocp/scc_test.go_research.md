<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc_test.go -->
# sources/control-plane/ceph-csi/api/deploy/ocp/scc_test.go

Purpose: unit tests for OpenShift SCC rendering.
Important APIs/functions: `TestNewSecurityContextConstraints` subtests defaults and Rook deployer prefix; `TestNewSecurityContextConstraintsYAML` checks non-empty YAML.
Control flow/state: in-memory render/unmarshal only.
Dependencies/integration: OpenShift SCC API and testify.
Risks/test signals: tests check user prefixes but not all SCC privilege fields, so privilege drift can pass unless rendering breaks.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc_test.go -->
