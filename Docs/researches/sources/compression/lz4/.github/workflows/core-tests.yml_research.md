<!-- BEGIN_FILE_RESEARCH: sources/compression/lz4/.github/workflows/core-tests.yml -->
# sources/compression/lz4/.github/workflows/core-tests.yml

## Purpose
Runs core lz4 correctness and regression suites.

## Important APIs, Types, And Functions
- Workflow/config name: Core Tests workflow.
- Defines triggers, jobs, runner images, package setup, checkout, and build/test commands for this CI lane.
- Uses repository make/build scripts rather than duplicating lz4 logic in the workflow.

## Control Flow
The CI system checks out source, prepares dependencies, executes the configured matrix or job steps, and reports failures through the platform. Concurrency settings in GitHub workflows cancel superseded runs for the same branch/PR.

## State And Persistence
State is ephemeral CI workspace data, package caches, build outputs, logs, and uploaded artifacts where configured. The repository is not modified by normal runs.

## Dependencies And Integration Points
Jobs cover benchmarks, fuzzers, version checks, ABI checks, frame tests, memory usage, custom distance, Makefile variable propagation, and block-device behavior. It integrates with GitHub Actions or CircleCI runners, system package managers, compilers, and project Make/CMake/Meson scripts.

## Risks And Edge Cases
CI can fail due to runner image changes, package availability, emulator instability, or matrix drift. Permissions and artifact upload settings matter for security-related workflows.

## Test Signals
Passing jobs indicate the covered build/test lane remains functional. Failures point to compiler, platform, sanitizer, build-system, dependency, or supply-chain regressions depending on the workflow.
<!-- END_FILE_RESEARCH: sources/compression/lz4/.github/workflows/core-tests.yml -->
