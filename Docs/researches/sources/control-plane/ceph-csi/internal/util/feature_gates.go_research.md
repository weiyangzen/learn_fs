<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/feature_gates.go -->
## sources/control-plane/ceph-csi/internal/util/feature_gates.go

**Purpose:** Implements simple process-wide feature gate parsing and lookup, currently for `SlowGRPCRestart`.

**Important APIs and types:** `FeatureGate` is a string alias. `SlowGRPCRestart` is enabled by default in `defaultFeatureGates`. `InitFeatureGates` parses comma-separated `Key=bool` entries into `activeFeatureGates`. `IsFeatureGateEnabled` returns active values or defaults.

**Control flow, state, and persistence:** `InitFeatureGates` copies defaults on every call, rejects malformed entries, unknown gates, and non-bool values, and mutates the package-level `activeFeatureGates` map. State is in-memory only and affects subsequent lookups.

**Dependencies and integration points:** Uses `maps.Copy`, `strconv.ParseBool`, and string splitting. It integrates with process startup/config parsing and gRPC restart behavior.

**Risks and test signals:** The package-level map is not synchronized, so initialization should happen before concurrent use. `IsFeatureGateEnabled` returns the zero value for unknown gates because it indexes `defaultFeatureGates`. Tests intentionally do not run in parallel and cover defaults, enable/disable, unknown keys, bad format, and lookup before init.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/feature_gates.go -->
