## sources/distributed-fs/ipfs-kubo/test/integration/GNUmakefile

Purpose: legacy Docker-oriented benchmark harness for integration tests with CPU profiling.

Important targets and control flow: `all` aliases `collect`, which runs `clean`, `build_image`, `run_profiler`, and `cp_pprof_from_container`. It builds a Docker image from the repo root, runs `go test` inside the container with `--cpuprofile=cpu.out`, copies the profile and test binary into `./build/bench`, and provides `analyze` to open `go tool pprof`.

State and dependencies: writes `build/bench`, creates/removes Docker container `go-ipfs-bench`, and depends on Docker plus a configured `IMAGE` variable. The package path still references `go-ipfs` naming conventions.

Risks: stale naming and implicit `IMAGE` can break the makefile; container lifecycle is not robust if `docker run` fails before cleanup. Test signal is successful benchmark profile collection for integration package performance investigations.
