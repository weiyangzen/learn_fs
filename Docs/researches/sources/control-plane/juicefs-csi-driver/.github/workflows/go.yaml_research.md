# sources/control-plane/juicefs-csi-driver/.github/workflows/go.yaml

## Purpose
This is the main CI workflow for Go, Python, shell, module, Docker, and Makefile changes. It builds the CSI driver, runs verification and unit/sanity tests, then runs broad CE and EE E2E matrices across mount modes with and without kubelet integration.

## Important Jobs and Steps
The `test` job sets up Go 1.25, builds with `make`, runs `make verify`, `make test`, `make test-sanity`, combines coverage, and uploads it to Codecov. `build-matrix` produces two JSON matrices: full modes (`pod`, `pod-mount-share`, `fs-mount-share`, `pod-provisioner`, `webhook`, `webhook-provisioner`, `process`) and without-kubelet modes. Four E2E jobs run CE/EE and kubelet/without-kubelet combinations. Each E2E job cleans runner disk, prepares microk8s, builds dashboard dist and dev images, deploys CSI, and runs `.github/scripts/e2e-test.py` with mode-specific environment variables.

## Control Flow
Path filters trigger CI for code and build script changes. Concurrency cancels superseded runs per ref. The matrix job fans out E2E jobs. `success-all-test` depends on CE and EE full E2E jobs and fails if the workflow conclusion action reports failure.

## State and Persistence Behavior
The workflow builds Docker images locally, imports them into microk8s or pushes/caches them depending on Makefile settings, and uses MinIO/Redis services installed by scripts. No repository files are committed, but Codecov receives coverage output.

## Dependencies and Integration Points
It depends on Go, Docker, pnpm, microk8s setup scripts, root and Docker Makefile targets, dashboard UI build, E2E Python scripts, Docker Hub or local image handling, Codecov, and secrets for EE tests. It is the main integration point for `test_case.py` and `util.py`.

## Risks
This workflow is expensive and fragile because it builds images and runs full Kubernetes E2E matrices on GitHub-hosted runners. The disk cleanup step removes large preinstalled directories, which is necessary but runner-image dependent. The `success-all-test` only needs full CE/EE E2E jobs, not the without-kubelet jobs, so it may not aggregate every matrix lane. Action versions are mixed and some are old.

## Test Signals
Passing `test` gives build, verify, unit, sanity, and coverage signals. Passing E2E jobs gives the strongest signal that CSI controller/node/webhook/process modes work in microk8s for CE and EE.
