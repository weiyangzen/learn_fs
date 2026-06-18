# sources/control-plane/csi-driver-nfs/.github/workflows/linux.yaml

Purpose: primary Linux CI for verification, tests, coverage, and container build.

Important APIs and types: triggers on pushes and PRs. Uses setup-go `^1.17`, checkout, `make verify`, `go test -race -covermode=atomic -coverprofile=profile.cov ./pkg/...`, `make container`, installs `goveralls`, and uploads coverage with `GITHUB_TOKEN`.

Control flow: a build step performs verification, race coverage tests, and Docker buildx container creation; a later step sends coverage.

State and persistence: creates coverage profile and local container images; writes coverage to Coveralls.

Dependencies and integration: depends on Makefile targets, Docker buildx, release-tools, hack verifiers, Go, and Coveralls.

Risks: building multi-arch containers in generic GitHub runners can be slow or flaky due to QEMU/binfmt. Go version differs from Trivy and Makefile release version.

Test signals: verify target, race coverage, container build, and Coveralls upload.
