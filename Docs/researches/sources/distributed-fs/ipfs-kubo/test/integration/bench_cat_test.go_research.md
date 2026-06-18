## sources/distributed-fs/ipfs-kubo/test/integration/bench_cat_test.go

Purpose: benchmark-only measurement of UnixFS cat/get throughput after content has already been added.

Important APIs and control flow: `BenchmarkCat1MB`, `BenchmarkCat2MB`, and `BenchmarkCat4MB` call `benchmarkVarCat`, which pre-generates deterministic bytes, sets benchmark bytes, and repeatedly calls `benchCat`. `benchCat` stops the timer while creating mocknet nodes, APIs, links, bootstrap records, and adding content, then starts the timer immediately before `catterAPI.Unixfs().Get` and the verification copy.

State and dependencies: all state is in-memory Kubo node state and mocknet links. Dependencies mirror `addcat_test.go`, with `testing.B` timer control.

Risks: the measured region includes both retrieval and verification copy, so it is a practical end-to-end cat benchmark rather than a pure exchange benchmark. Test signals are benchmark throughput and exact byte equality after retrieval.
