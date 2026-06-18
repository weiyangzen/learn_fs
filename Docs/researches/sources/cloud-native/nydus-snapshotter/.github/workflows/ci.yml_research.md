# sources/cloud-native/nydus-snapshotter/.github/workflows/ci.yml

Purpose: primary CI for security, build/lint/test, optimizer build, smoke, cross-build, and coverage.

Flow: runs on push and PR across all/stable branches. Jobs install Go from `go.mod`, run `govulncheck` and OSV scanner, run golangci-lint via Go install, execute `make` and `make test`, build optimizer with Rust components, run smoke tests after downloading Nydus, cross-build converter for linux/windows/darwin amd64/arm64, and upload coverage.

State/dependencies: depends on GitHub Actions, Go, Rust, containerd, Nydus release assets, Codecov token.

Integration points: exercises Makefile targets and release-critical build paths.

Risks/tests: latest Nydus release download and external scanners can introduce nondeterminism. Build job calls race tests via `make test`.
