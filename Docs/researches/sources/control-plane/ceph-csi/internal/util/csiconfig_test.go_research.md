<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/csiconfig_test.go -->
## sources/control-plane/ceph-csi/internal/util/csiconfig_test.go

**Purpose:** Exercises CSI config accessors against temporary JSON configs, including malformed input and optional per-cluster fields.

**Important APIs and functions:** Tests cover `Mons`, `GetRBDNetNamespaceFilePath`, `GetCephFSNetNamespaceFilePath`, `GetNFSNetNamespaceFilePath`, `GetCrushLocationLabels`, `GetCephFSMountOptions`, `GetRBDMirrorDaemonCount`, `GetRBDControllerPublishSecretRef`, and `GetCephFSControllerPublishSecretRef`.

**Control flow, state, and persistence:** Each test writes a temp config file and runs parallel subtests for independent cluster IDs. `TestCSIConfig` sequentially rewrites one file to check missing, empty, malformed, missing monitors, wrong monitor type, absent cluster, and valid monitor cases.

**Dependencies and integration points:** Uses deployment `ClusterInfo`, Kubernetes `corev1.SecretReference`, JSON, temp files, and `testify/require`. It validates the config schema consumed by controller/node startup and request handling.

**Risks and test signals:** Good signal for many optional fields and defaults. It does not cover `GetCephFSRadosNamespace`, `CephFSSubvolumeGroup`, `GetClusterID`, `GetMonsAndClusterID` with mapping, or `GetRBDNodePublishSecretRef`. Parallel subtests are safe because each reads immutable temp content.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/csiconfig_test.go -->
