# sources/control-plane/external-snapshotter/.github/workflows/trivy.yaml

## Purpose
Daily and master-branch vulnerability scanning workflow for external-snapshotter container images.

## Important APIs, Types, and Functions
- Triggered on pushes to `master` and daily cron at midnight UTC.
- Parses Go version from `release-tools/prow.sh` and writes `.go-version`.
- Uses pinned checkout, setup-go, and `aquasecurity/trivy-action`.
- Builds three images: `csi-snapshotter`, `snapshot-controller`, and `snapshot-conversion-webhook`.
- Runs Trivy against all three images with `exit-code: 1`, `ignore-unfixed: true`, and all severity classes included.

## Control Flow
The workflow checks out code, derives the Go version, installs Go, runs `make`, builds Docker images from each component Dockerfile, then scans each built image. Any Trivy finding that matches the configured policy fails the job.

## State and Persistence Behavior
The workflow creates temporary runner-local build outputs, Docker images, and `.go-version`; it does not persist repo changes. Vulnerability database state is fetched from the configured public ECR mirror.

## Dependencies and Integration Points
Integrates with GitHub Actions, Docker, Makefile/release tooling, component Dockerfiles, and Trivy. It depends on the format of `release-tools/prow.sh` containing `configvar CSI_PROW_GO_VERSION_BUILD`.

## Risks
The Go-version parser is shell text processing and can break if release-tools changes format. Trivy DB availability can affect scan reliability. `ignore-unfixed: true` intentionally suppresses vulnerabilities without fixes.

## Test Signals
Signals include successful image builds and Trivy runs for all three images. Failures should be triaged as either build regressions, scanner infrastructure issues, or actionable vulnerabilities.
