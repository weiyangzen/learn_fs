# sources/cloud-native/cri-o/.github/workflows/test.yml

Purpose: broad build, unit, release-artifact, static-build, dependency, and security test workflow for CRI-O.

Important jobs and flow: `build` compiles CRI-O, docs, config, and cross Linux binary, then uploads artifacts. `build-freebsd` validates FreeBSD cross compilation. Validation jobs regenerate docs, completions, and NRI Bats tests from build artifacts and require clean tree status. `build-static` uses Nix/Cachix for static binaries across amd64, arm64, ppc64le, and s390x; upload jobs push static builds and VEX files to GCS on main/release/tags. `unit` runs mock generation and Ginkgo unit tests as root/rootless on amd64 and root on arm64 with coverage upload. Release jobs generate notes and GitHub releases. `dependencies`, `codeql-build`, `security-checks`, and `vex-upload` cover dependency reports, CodeQL, govulncheck, gosec, and OpenVEX artifacts.

State and persistence: produces build/docs/config/static/release/dependency/VEX artifacts, cache entries, release records, and GCS uploads.

Dependencies and integration: central integration point for Makefile targets, Nix, GCS credentials, Codecov, CodeQL, Go, and release scripts.

Risks: high workflow breadth means failures can stem from external services, credentials, Nix cache, or generated-file drift. Several jobs have write permissions and should remain guarded by branch/tag conditions.

Test signals: this is the primary CI signal for build reproducibility, generated artifacts, unit coverage, release packaging, and vulnerability checks.
