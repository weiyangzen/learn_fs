# sources/cloud-native/nydus/.github/workflows/smoke.yml

## Purpose
This is the main CI smoke and quality workflow for Nydus. It builds Rust and Go components across architectures, runs lint/unit/smoke/performance/takeover tests, produces Rust and Go coverage, uploads coverage to Codecov, and runs cargo-deny.

## Important APIs, Types, and Functions
Major jobs include `contrib-build`, `contrib-lint`, `nydus-build`, `nydusd-build-macos`, `nydus-integration-test`, `nydus-unit-test`, `contrib-unit-test-coverage`, `nydus-unit-test-coverage`, `nydus-integration-test-coverage`, `upload-coverage-to-codecov`, `upload-pr-coverage-to-codecov`, `nydus-cargo-deny`, `performance-test`, and `takeover-test`. It uses setup-go, rust-cache, rust-toolchain-file, cross builds, Docker Buildx, cargo-nextest, cargo-llvm-cov, golangci-lint, Codecov, cargo-deny, and smoke Makefile targets.

## Control Flow
Build jobs produce amd64 artifacts for later tests while still validating several architectures. Integration tests download current artifacts, fetch older release binaries, prepare the runtime environment, export `NYDUS_*` paths for old/stable/latest versions, and run `make smoke-only`. Unit tests run nextest with fscache setup. Coverage jobs generate Rust and Go coverage artifacts; PR coverage also builds instrumented Nydus and nydusify binaries, wraps them to set `LLVM_PROFILE_FILE`, runs smoke tests, validates raw coverage files exist, converts Go covdata, and emits cargo llvm-cov reports. Upload jobs aggregate coverage line states for preview and call Codecov. Performance and takeover jobs run smoke harness subsets with built artifacts.

## State and Persistence
Artifacts persist binaries and coverage files between jobs. Runtime state includes Docker layers, downloaded release tarballs, `/usr/bin/nydus-*` installs, workdir/cache dirs, coverage raw files, and step logs. Codecov receives uploaded reports externally.

## Dependencies and Integration Points
The workflow ties together Cargo workspace builds, contrib Go projects, Makefile targets, smoke test harnesses, external GitHub release API calls, Docker-based environment preparation, Codecov, cargo-deny policy, and architecture-specific cross-build support.

## Risks and Edge Cases
This workflow is resource-heavy and sensitive to disk pressure; it uses an explicit free-disk-space action for integration paths. External latest-release downloads can introduce nondeterminism. Only amd64 artifacts are uploaded for downstream tests, even though build matrices validate other arches. Coverage instrumentation is complex and can fail if wrappers, sudo environment preservation, or raw profile generation changes. Codecov upload requires secrets for non-PR unit upload but PR upload runs without that credentials gate.

## Test Signals
A passing smoke workflow gives broad confidence: multi-arch compile, Go lint, Rust nextest, smoke integration across versions, coverage generation, cargo-deny, performance, and takeover tests. The workflow also prints coverage previews before uploading.
