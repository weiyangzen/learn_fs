<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver_test.go

Purpose: unit tests for NFS CSIDriver render helpers.
Important APIs/functions: `TestNewCSIDriver` and `TestNewCSIDriverYAML` verify defaults render without errors, object is non-nil, name matches, and YAML is non-empty.
Control flow/state: in-memory only.
Dependencies/integration: uses testify and embedded YAML.
Risks/test signals: tests do not assert CSIDriver spec fields, so behavioral spec regressions can pass unless unmarshal fails.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver_test.go -->
