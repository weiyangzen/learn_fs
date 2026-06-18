## sources/distributed-fs/ipfs-kubo/test/integration/bench_test.go

Purpose: benchmark matrix for complete add-and-cat flows across content sizes and latency profiles.

Important APIs and control flow: `benchmarkAddCat` pre-generates deterministic data outside the timed section, sets bytes, then repeatedly calls `DirectAddCat`. Benchmark functions cover instantaneous 1KB through 256MB, slow routing through 512MB, slow network through 256MB, and slow blockstore sizes using latency presets from `go-libp2p-testing/net`.

State and dependencies: uses the shared `RandomBytes` and `DirectAddCat` from `addcat_test.go`; every iteration creates fresh in-memory nodes and mocknet state.

Risks: larger benchmarks are resource-intensive and include node construction/bootstrap/add/retrieve costs, so results are system-sensitive and not isolated microbenchmarks. Test signals are benchmark throughput and failure if any add/get byte verification fails.
