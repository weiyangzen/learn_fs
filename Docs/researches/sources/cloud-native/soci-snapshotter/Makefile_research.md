# sources/cloud-native/soci-snapshotter/Makefile

Purpose: central developer/CI build orchestration for SOCI Snapshotter binaries, flatbuffers, tests, coverage, integration tests, release artifacts, and benchmarks.

Important APIs/types/functions: targets `soci-snapshotter-grpc`, `soci`, `flatc`, `install`, `clean`, `tidy`, `vendor`, `gen-config`, `test`, `test-with-coverage`, `integration`, `integration-with-coverage`, `release`, `go-benchmarks`, `benchmarks-*`; variables for version/revision ldflags, static build tags, package lists, output/coverage dirs, benchmark binaries.

Control flow: default builds both commands. `soci-snapshotter-grpc` regenerates FlatBuffers first. Coverage targets compose Go build/test flags with `GOCOVERDIR`. Integration uses gotestsum with env gates. Release delegates to scripts. Benchmark targets build and run performance/comparison/stargz/parser tools.

State and persistence: writes binaries to `out/`, coverage to `cov/`, release artifacts to `release/`, generated FlatBuffer Go code, config files, and benchmark output. Clean removes these plus integration Docker leftovers.

Dependencies/integration: used by all GitHub workflows, Dockerfile, scripts, Go modules, flatc, Docker, and gotestsum.

Risks: static build ldflags and package-list shell commands are complex. Clean target includes Docker removal by name/reference. Generated FlatBuffer code can be stale if flatc version differs.

Test signals: CI invokes build, unit, coverage, integration, release, and benchmark targets.
