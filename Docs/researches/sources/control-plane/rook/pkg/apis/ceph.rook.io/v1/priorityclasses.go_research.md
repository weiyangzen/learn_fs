# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/priorityclasses.go

Purpose: provides lookup helpers for daemon-specific Kubernetes priority class names stored in a Rook `PriorityClassNamesSpec` map.

Important APIs/types/functions: `PriorityClassNamesSpec.All`, `GetMgrPriorityClassName`, `GetMonPriorityClassName`, `GetOSDPriorityClassName`, `GetCleanupPriorityClassName`, `GetCrashCollectorPriorityClassName`, and `GetCephExporterPriorityClassName`. Key constants such as `KeyAll`, `KeyMgr`, `KeyMon`, `KeyOSD`, `KeyCleanup`, `KeyCrashCollector`, and `KeyCephExporter` are defined elsewhere in the package.

Control flow: `All` returns the class configured for `all`, or empty string. Every daemon-specific getter checks whether its daemon key exists; if not, it falls back to `All`; if it exists, it returns the daemon-specific value, including an explicit empty string.

State and persistence: no persistence or mutation. The map is read-only from these helpers.

Dependencies/integration: no external imports. Reconciler code uses these helpers to populate pod specs for Ceph manager, monitor, OSD, cleanup, crashcollector, and exporter workloads.

Risks: explicit empty daemon entries suppress fallback to `all`. There are no helpers here for every resource key in `resources.go`, so missing daemon types require separate handling. Map lookup on a nil map is safe and returns empty fallback.

Test signals: `priorityclasses_test.go` verifies YAML unmarshalling and `All` fallback behavior. Daemon-specific getter fallback/override behavior is not exhaustively tested.
