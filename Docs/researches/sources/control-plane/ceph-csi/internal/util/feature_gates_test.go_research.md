<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/feature_gates_test.go -->
## sources/control-plane/ceph-csi/internal/util/feature_gates_test.go

**Purpose:** Tests process-wide feature gate parsing and default lookup behavior.

**Important APIs and functions:** Tests call `InitFeatureGates` with empty, true, false, unknown key, bad format, and bad bool values. `TestIsFeatureGateEnabledBeforeInit` temporarily nils `activeFeatureGates` and verifies default enablement.

**Control flow, state, and persistence:** Tests are deliberately not parallel because they mutate package-level state. One test saves and restores the original map.

**Dependencies and integration points:** Uses `testify/require`. It protects startup parsing behavior for gate strings.

**Risks and test signals:** Good signal for current one-gate parser. It does not test multiple comma-separated gates or duplicate entries, which will matter when more gates are added.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/feature_gates_test.go -->
