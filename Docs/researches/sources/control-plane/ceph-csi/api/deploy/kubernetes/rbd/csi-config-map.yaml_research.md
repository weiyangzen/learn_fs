<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.yaml

Purpose: embedded YAML template for the RBD CSI ConfigMap.
Important surface: creates `apiVersion: v1`, `kind: ConfigMap`, metadata name from `.Name`, and `data.config.json` from `.ClusterInfo`.
Control flow/state: rendered by the package's `NewCSIConfigMapYAML` with no state of its own.
Dependencies/integration: must remain parseable by `ghodss/yaml` after template substitution and compatible with driver config loading.
Risks/test signals: incorrect indentation or non-JSON rendering of `.ClusterInfo` can produce a ConfigMap that exists but is semantically invalid. Unit tests cover render/non-empty only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.yaml -->
