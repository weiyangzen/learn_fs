# sources/cloud-native/cri-o/.github/workflows/integration.yml

Purpose: GitHub Actions workflow for CRI-O integration and CRI conformance-style tests.

Important jobs and flow: triggered on manual dispatch, tags, main/release/update-nixpkgs branches, and PRs. `test-binaries` builds instrumented CRI-O and helper binaries for amd64 and arm64, uploads artifacts, and caches Go dependencies. The `integration` matrix downloads those artifacts, installs packages and runtime setup, optionally swaps runtimes, then runs `sudo -E test/test_runner.sh` with matrix-controlled runtime type, critest flag, userns flag, jobs, and timeout. It converts `GOCOVERDIR` coverage data to a text profile and uploads to Codecov.

State and persistence: artifacts hold built binaries; cache stores Go build/module data; coverage files are written under `build/coverage`.

Dependencies and integration: depends on GitHub Actions, setup-go, cosign installer, CRI-O scripts, conmon/crun/runc setup, Codecov, and privileged host capabilities.

Risks: integration tests run with sudo and host-level container runtime setup, so runner environment drift matters. Several runc lanes are disabled due to nested AppArmor issues, reducing coverage.

Test signals: matrix success, coverage conversion, and Codecov upload provide strong end-to-end signals for runtime behavior.
