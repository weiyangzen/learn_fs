# sources/distributed-fs/beegfs-go/ctl/internal/cmd/benchmark/benchmark_test.go

Purpose: tests aggregation logic for benchmark performance summaries.

Important test is `TestStorageBenchSummary`, which appends five target throughput observations from two nodes to `benchPerfResults`.

Control flow: the test appends throughput values including zero and a high maximum, calls `summarize`, and asserts slowest target/node, fastest target/node, average throughput, and aggregate throughput.

State behavior under test is the incremental `benchPerfResults.summary`, `initializedFastest`, `initializedSlowest`, and target count behavior. Persistence and backend benchmark execution are not involved.

Dependencies are `testing`, `testify/assert`, and common BeeGFS entity ID types.

Integration point is `printResultsSummary`, which relies on `benchPerfResults` to compute rows for CLI output.

Risks: this test does not cover table rendering, unit normalization, mixed benchmark-type handling, no-results handling, verbose sorting, status summaries, or command flags. It also does not test overflow/large throughput values.

Test signals: useful focused coverage for min/max/average/aggregate math, including zero throughput as a valid slowest result.
