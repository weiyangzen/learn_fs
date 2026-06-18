<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/read_affinity.go -->
## sources/control-plane/ceph-csi/internal/util/read_affinity.go

**Purpose:** Builds Ceph read-affinity mount/map options from CSI config and node CRUSH location labels.

**Important APIs and functions:** `ConstructReadAffinityMapOption` converts a CRUSH location map into `read_from_replica=localize,crush_location=key:value|...`. `GetReadAffinityMapOptions` reads config enablement/labels, returns empty when disabled, falls back to CLI options when config labels are empty, otherwise derives node-label CRUSH locations and constructs the option string.

**Control flow, state, and persistence:** Functions are stateless except for reading CSI config through `GetCrushLocationLabels`. Map iteration order makes the constructed option order nondeterministic for multiple labels. If enabled labels produce no matching node labels, the returned string is empty.

**Dependencies and integration points:** Depends on CSI config helpers and CRUSH location mapping. It integrates with RBD map/mount option generation for localized replica reads.

**Risks and test signals:** Order nondeterminism is acceptable in tests but could complicate string comparisons/logging. Config enablement overrides CLI fallback: disabled returns empty even if CLI options exist. Tests cover option construction for nil, empty, single, and two-entry maps, but not full config integration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/read_affinity.go -->
