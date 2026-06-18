<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crushlocation_test.go -->
## sources/control-plane/ceph-csi/internal/util/crushlocation_test.go

**Purpose:** Unit-tests CRUSH location map derivation from requested label names and node labels.

**Important APIs and functions:** `Test_getCrushLocationMap` covers empty configuration, empty node labels, single and multiple matches, no match, Ceph-compatible dot replacement, Kubernetes `hostname` to Ceph `host`, and skipping matching labels with empty values.

**Control flow, state, and persistence:** Pure table-driven tests using `require.Equal`. There is no external state.

**Dependencies and integration points:** Depends on `testify/require` and the unexported helper. It validates the input feeding read-affinity map construction.

**Risks and test signals:** Good signal for common topology labels. It does not cover labels without separators, whitespace-heavy label names, duplicate CRUSH types, or nondeterministic ordering downstream.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crushlocation_test.go -->
