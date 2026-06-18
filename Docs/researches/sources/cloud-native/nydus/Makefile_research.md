# sources/cloud-native/nydus/Makefile

## Purpose
This Makefile is the main developer and CI command surface for building, testing, installing, cleaning, coverage, smoke tests, and Go contrib components.

## Important APIs, Types, and Functions
Top-level targets include `all`, `all-build`, `all-release`, `all-static-release`, `all-install`, `build`, `release`, `static-release`, `clean`, `install`, `ut`, `ut-nextest`, `miri-ut-nextest`, `smoke-only`, `smoke-performance`, `smoke-benchmark`, `smoke-takeover`, coverage targets, and contrib build/test/lint/install targets. Variables include `TEST_WORKDIR_PREFIX`, `INSTALL_DIR_PREFIX`, `DOCKER`, `CARGO`, `RUSTUP`, `CARGO_COMMON`, `STATIC_TARGET`, `RUST_TARGET_STATIC`, and coverage-related env values.

## Control Flow
The Makefile derives OS/architecture, adjusts Cargo features and static targets, and dispatches Rust builds through Cargo. `build` first checks formatting, then builds and runs clippy with warnings denied and a small allowlist. `release` wraps `build`; `static-release` cleans stale libz-sys, selects a target, and builds. Test targets run Cargo test/nextest/Miri. Contrib targets call `build_golang`, which either runs Go make targets in Docker or directly with `make -C`.

## State and Persistence
Build artifacts are written under Cargo target directories, contrib output directories, coverage directories, and optional install prefix. Some test targets create workdirs under `/tmp` or configured prefixes. `clean` removes coverage and Cargo artifacts.

## Dependencies and Integration Points
This file is invoked by nearly every workflow in this subset. It integrates Cargo, rustup, nextest, cargo llvm-cov, grcov, Go contrib Makefiles, Docker, and smoke sub-Makefile targets.

## Risks and Edge Cases
`build` always runs formatting and clippy, so release builds include lint policy. `DOCKER` defaults to `"true"` for Go contrib builds, which can surprise local users. Static target selection has architecture-specific branches for ppc64le/riscv64/Darwin. Coverage flags are injected through environment-variable string expansion and must be preserved under `sudo -E` in workflows.

## Test Signals
The Makefile itself is validated by CI: smoke, release, benchmark, convert, miri, and coverage workflows all call these targets. Local signals are successful `make build`, `make ut-nextest`, and relevant smoke targets.
