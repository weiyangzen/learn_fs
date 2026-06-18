# sources/cloud-native/cri-o/internal/runtimehandlerhooks/gomaxprocs_hooks_linux_test.go

Purpose: validates GOMAXPROCS environment injection and CPU-share calculation helpers.

Important APIs/types/functions: tests `injectGOMAXPROCS` and `calculateGOMAXPROCS`.

Control flow: table tests create Linux OCI generators, prepopulate env values, call injection, and compare whether a new env var appears. Calculation table tests feed shares/fallback pairs and expected results.

State and persistence behavior: in-memory OCI spec mutation only.

Dependencies and integration points: uses Ginkgo/Gomega and runtime-tools `generate`.

Risks: tests focus on helpers, not the full `PreCreate` skip logic for annotations, cgroup parent, or quota.

Test signals: covers pre-existing `GOMAXPROCS`, default env already merged into the spec, large values, value 1, fractional requests, and fallback floors.
