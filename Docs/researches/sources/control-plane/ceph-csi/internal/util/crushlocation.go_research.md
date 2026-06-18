<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crushlocation.go -->
## sources/control-plane/ceph-csi/internal/util/crushlocation.go

**Purpose:** Converts configured Kubernetes node label names and actual node labels into a Ceph CRUSH location map used for localized read-affinity options.

**Important APIs and functions:** `GetCrushLocationMap` handles the empty-config fast path and calls `getCrushLocationMap`. The helper splits comma-separated label names, finds matching non-empty node label values, derives the CRUSH type from the suffix after `/`, maps `hostname` to `host`, trims whitespace, and replaces dots in values with hyphens.

**Control flow, state, and persistence:** The function is stateless and returns nil when there are no configured labels or no matching non-empty node labels. Output is a map from CRUSH bucket type to sanitized value.

**Dependencies and integration points:** Depends on `strings` and internal logging. It integrates with CSI config read-affinity settings, Kubernetes node label lookup, and `ConstructReadAffinityMapOption`.

**Risks and test signals:** If a configured label lacks `/`, `strings.IndexRune` returns -1 and the full key is used due to slicing at zero, which may be surprising but avoids panic. Map output order is nondeterministic. Tests cover empty inputs, matches, multiple labels, no match, dot replacement, hostname mapping, and empty values.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crushlocation.go -->
