# sources/cloud-native/nydus/smoke/Makefile

Purpose: provides build and test entry points for the Go smoke suite, including ordinary smoke tests, performance, benchmark, compatibility, and takeover modes.

Important targets: `build` compiles `./tests` into `smoke.test` with `-race`; `test` builds, runs golangci-lint, then executes `sudo -E ./smoke.test` with configurable `TESTS`; `test-performance`, `test-benchmark`, `test-compatibility`, and `test-takeover` set environment gates and run selected tests.

Control flow/state: environment variables supply binary paths, work dirs, stable versions, image names, snapshotter sockets, and coverage flags. `PACKAGES`, `GOPROXY`, `GO_TEST_BUILD_FLAGS`, and `TESTS` are configurable, though `PACKAGES` is not used by the visible targets.

Dependencies and integration: depends on Go tooling, golangci-lint, sudo, compiled Nydus binaries, and smoke test helper environment. It coordinates with `tests/*_test.go` environment gates such as `BENCHMARK_TEST`, `PERFORMANCE_TEST`, and `TAKEOVER_TEST`.

Risks: `sudo -E` must preserve the required environment; race build can slow tests; lint is coupled to golangci-lint config compatibility; root privileges are needed for mount/cache tests.

Test signals: successful targets produce the `smoke.test` binary and run selected Go tests with timeouts and parallelism controls.
