# sources/cloud-native/cri-o/server/metrics/collectors/collectors.go

Purpose: defines the set of Prometheus collector identifiers and helpers for normalizing configured metric collector names.

Important APIs and functions: `Collector`, `Collectors`, constants for every CRI-O metric collector, `FromSlice`, `ToSlice`, `All`, `Contains`, `Stripped`, and `String`.

Control flow: collector names can arrive with `container_runtime_crio_`, `crio_`, or no prefix; `Stripped` removes recognized prefixes and all comparisons use stripped names.

State and persistence: no state; all helpers are deterministic pure transformations.

Dependencies and integration: consumed by `metrics.go` to decide which Prometheus collectors to register, and by config parsing to support prefixed and unprefixed names.

Risks: prefix stripping is broad and may make two differently prefixed strings equivalent. Adding a new metric requires updating the constants and `All()` list.

Test signals: `collectors_test.go` covers prefix stripping, `FromSlice`, `ToSlice`, and `Contains` behavior across prefixed and unprefixed variants.
