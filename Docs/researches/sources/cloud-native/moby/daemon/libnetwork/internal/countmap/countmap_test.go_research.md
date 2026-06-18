# Research: sources/cloud-native/moby/daemon/libnetwork/internal/countmap/countmap_test.go

Purpose: tests generic counter-map add and zero-deletion semantics. Important test is `TestMap`.

Control flow: the test starts with counters for `foo`, `bar`, and `zeroed`, applies deltas that produce negative values, a new positive key, and a zeroed key deletion, then asserts the resulting map. It then applies inverse deltas to bring all remaining keys to zero and asserts the map is empty.

State/dependencies: no external state; tests use a concrete `Map[string]`. Dependencies include `gotest.tools` deep equality. Risks covered include negative counts being retained, zero counts being deleted, and new key creation. Gaps include nil map behavior, non-string comparable keys, and concurrent use.
