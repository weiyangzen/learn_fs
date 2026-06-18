# sources/distributed-fs/ipfs-kubo/test/bench/bench_cli_ipfs_add/main.go

Purpose: benchmark utility for measuring `ipfs add` CLI performance over generated random files.

Important APIs and control flow: `main` calls `compareResults`, which repeatedly benchmarks increasing sizes starting at 10 MB. `benchmarkAdd` uses `testing.Benchmark`; each iteration creates a temp repo via `IPFS_PATH`, runs `ipfs init`, writes deterministic random data to a temp file, optionally starts an `ipfs daemon`, times `ipfs add`, and returns the benchmark result.

State and persistence: creates temp repos and temp input files, runs external `ipfs` processes, and optionally starts/stops a daemon. Debug mode streams command output to console.

Dependencies and integration: depends on `ipfs` binary in PATH, Kubo config env var, go-test random, and Kubo unit constants.

Risks and test signals: `compareResults` loop condition grows `amount` while `amount > 0`, which depends on integer overflow to terminate and can run many sizes. Online mode is marked broken due to datastore locking. It is a benchmark, not a correctness test.
