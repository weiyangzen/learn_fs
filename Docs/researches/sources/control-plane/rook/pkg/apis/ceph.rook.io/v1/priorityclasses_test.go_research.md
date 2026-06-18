# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/priorityclasses_test.go

Purpose: tests priority-class map unmarshalling and default `all` lookup behavior.

Important APIs/types/functions: exercises `PriorityClassNamesSpec` JSON/YAML unmarshalling and `PriorityClassNamesSpec.All`.

Control flow: `TestPriorityClassNamesSpec` converts YAML with `all`, `mgr`, `mon`, `osd`, and `crashcollector` entries into JSON, unmarshals into `PriorityClassNamesSpec`, and compares the resulting map. `TestPriorityClassNamesDefaultToAll` constructs a map with `all` and `mon` entries and asserts that `All` returns the global class.

State and persistence: test-only local maps; no persistence.

Dependencies/integration: depends on testify and Kubernetes YAML conversion. It protects the CRD map shape used by cluster specs.

Risks: despite its name, `TestPriorityClassNamesDefaultToAll` only tests `All()`, not daemon-specific fallback to `all`. It does not cover explicit empty daemon-specific entries, cleanup/exporter getters, or nil maps.

Test signals: confirms YAML keys map into the expected `PriorityClassNamesSpec` and that the global `all` key can be read.
