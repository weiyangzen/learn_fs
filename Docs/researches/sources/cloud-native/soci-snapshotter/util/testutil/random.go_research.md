# sources/cloud-native/soci-snapshotter/util/testutil/random.go

## Purpose
`random.go` supplies deterministic pseudo-random data generation for tests.

## Important APIs, Types, and Functions
`TestRandomSeed` is the fixed global seed. `TestRand` wraps `*rand.Rand`. `NewTestRand(t)` combines the fixed seed with an FNV-1a hash of the test name and creates a PCG-backed `rand/v2.Rand`. Methods `Read`, `RandomByteData`, `RandomByteDataRange`, and `RandomDigest` generate deterministic bytes, bounded printable-ish data, and random digests.

## Control Flow, State, and Persistence
All state is in the `rand.Rand` instance. The helper is intentionally not thread-safe. Generated sequences vary by test name but are repeatable across runs.

## Dependencies and Integration Points
Dependencies are `hash/fnv`, `math/rand/v2`, Go testing, and `go-digest`. The ztoc tests use this package to generate repeatable tar file contents and gzip header data.

## Risks and Test Signals
`Read` converts `Int64()` to byte, which is deterministic but not byte-distribution focused. `RandomByteDataRange` treats `maxBytes` as exclusive and panics if `maxBytes <= minBytes` because of `IntN`. The deterministic seed is a strong reproducibility signal for large ztoc tests.
