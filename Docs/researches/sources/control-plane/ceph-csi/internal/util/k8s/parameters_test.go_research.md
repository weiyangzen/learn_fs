<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/parameters_test.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/parameters_test.go

**Purpose:** Tests basic Kubernetes CSI parameter filtering and PVC namespace owner lookup.

**Important APIs and functions:** `TestRemoveCSIPrefixedParameters` checks that non-CSI keys are preserved and CSI-prefixed PVC/PV metadata keys are removed. `TestGetOwner` checks missing and present PVC namespace metadata.

**Control flow, state, and persistence:** Pure parallel table tests with in-memory maps.

**Dependencies and integration points:** Uses `reflect.DeepEqual` and testing. It protects request parameter cleanup before driver-specific option parsing.

**Risks and test signals:** It does not test `GetVolumeMetadata`, `PrepareVolumeMetadata`, snapshot metadata helpers, nil maps, or substring false positives.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/parameters_test.go -->
