<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.go

Purpose: renders the RBD CSI `ceph-csi-config` ConfigMap from an embedded YAML template.
Important APIs/functions: `CSIConfigMapValues`, `CSIConfigMapDefaults`, `NewCSIConfigMap`, and `NewCSIConfigMapYAML`; uses Go `text/template`, `//go:embed`, and `ghodss/yaml` to unmarshal into `corev1.ConfigMap`.
Control flow/state: `NewCSIConfigMapYAML` parses the embedded template and executes it with provided name/cluster info; `NewCSIConfigMap` converts the YAML string to a typed object. It holds no persistent state.
Dependencies/integration: depends on shared `kubernetes.ClusterInfo` and the adjacent `csi-config-map.yaml` fixture.
Risks/test signals: `.ClusterInfo` is inserted using default Go formatting, so callers must verify produced JSON semantics; tests only assert non-empty YAML/name, not full config content.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.go -->
