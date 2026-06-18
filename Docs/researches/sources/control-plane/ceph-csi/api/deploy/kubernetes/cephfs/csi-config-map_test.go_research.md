<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map_test.go

Purpose: unit tests for CephFS ConfigMap render helpers.
Important APIs/functions: `TestNewCSIConfigMap` and `TestNewCSIConfigMapYAML` call defaults and assert no error, non-nil object, expected name, and non-empty YAML.
Control flow/state: no external state; test creates objects in memory.
Dependencies/integration: uses `stretchr/testify/require` and the embedded template.
Risks/test signals: coverage is shallow and does not parse or validate `config.json` semantics; failure signals template parsing/unmarshal/name regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map_test.go -->
