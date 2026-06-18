# sources/cloud-native/containers-storage/pkg/truncindex/truncindex_test.go

Purpose: behavioral and performance tests for the truncated ID index.

Important APIs/types/functions: `TestTruncIndex`, helper assertions for get and iteration, and benchmarks for add, get, delete, construct, and add+get at 100/250/500-size labels.

Control flow: the main test creates an index, exercises empty/nonexistent/illegal IDs, verifies exact and prefix lookups, introduces a conflicting ID, checks ambiguity, deletes the conflict, and checks iteration. Benchmarks generate random non-crypto IDs and measure core operations.

State/persistence: in-memory test indexes only.

Dependencies/integration: uses `pkg/stringid`, `math/rand/v2`, `slices`, and `testify/require`.

Risks: benchmark names for `BenchmarkTruncIndexAddGet100/250/500` all generate 500 IDs, so labels do not match workload size. Iteration concurrency test only asserts no panic/error, not timing or absence of deadlock beyond the test's natural completion.

Test signals: strong coverage for prefix uniqueness semantics and basic lock behavior.
