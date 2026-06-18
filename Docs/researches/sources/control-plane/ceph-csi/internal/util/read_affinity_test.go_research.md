<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/read_affinity_test.go -->
## sources/control-plane/ceph-csi/internal/util/read_affinity_test.go

**Purpose:** Tests read-affinity option string construction from CRUSH location maps.

**Important APIs and functions:** `TestReadAffinity_ConstructReadAffinityMapOption` checks nil/empty maps, a single `region:east` entry, and two-entry maps with either possible order accepted.

**Control flow, state, and persistence:** Pure parallel table tests with in-memory maps.

**Dependencies and integration points:** Uses `testify/require`. It protects the final string consumed by Ceph/RBD map options.

**Risks and test signals:** It intentionally accounts for map order nondeterminism. It does not cover `GetReadAffinityMapOptions`, CSI config enablement, CLI fallback, or node label mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/read_affinity_test.go -->
