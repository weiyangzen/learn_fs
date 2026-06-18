## sources/cloud-native/buildkit/util/network/netpool/pool.go

Purpose: generic reusable pool for expensive network namespace-like resources with target prefill and delayed shrink.

Important APIs/types: `Opt[T]`, `Pool[T]`, `New`, `Fill`, `Get`, `Put`, `Discard`, `Close`.

Control flow: `Fill` creates and returns new resources until `actualSize >= targetSize` or an error occurs. `Get` pops an available resource or calls `getNew`. `Put` appends available resource with last-used time; if actual size exceeds target it schedules cleanup after five minutes. `cleanupToTargetSize` releases oldest available entries older than the grace period. `Close` marks closed, releases currently available resources, and later returned resources are released in `Put`.

State/persistence: in-memory counts and available slice protected by mutex. Underlying `Release` may delete OS resources. Dependencies: BuildKit logger, `sync`, `time`, `pkg/errors`.

Integration points: CNI and proxy network namespace pools. Risks: checked-out resources are not forcibly released on `Close` until returned; cleanup timer ignores release errors; `actualSize` accounting depends on every checked-out item eventually being `Put` or `Discard`. Test signals: `pool_test.go` covers reuse and close behavior for available/returned values.
