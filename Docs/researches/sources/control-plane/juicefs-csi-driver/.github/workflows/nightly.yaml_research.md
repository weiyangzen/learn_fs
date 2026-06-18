# sources/control-plane/juicefs-csi-driver/.github/workflows/nightly.yaml

## Purpose
This nightly workflow builds the CSI driver nightly image, runs CE and EE E2E matrices, and publishes nightly CSI and mount images after successful full E2E validation.

## Important Jobs and Steps
`build-matrix` emits full and without-kubelet test mode matrices. The CE/EE E2E jobs build `docker image-nightly`, import `juicedata/juicefs-csi-driver:nightly` into microk8s, deploy CSI with `dev_tag=nightly`, and run `.github/scripts/e2e-test.py`. `success-all-test` checks the workflow conclusion, builds dashboard dist, logs into Docker Hub, builds and pushes nightly CSI/dashboard/mount images, syncs selected images, and prints success.

## Control Flow
The workflow runs on manual dispatch, pushes to `master`, and daily schedule. E2E jobs fan out by matrix. Publishing happens after the full CE and EE E2E jobs complete successfully according to the conclusion action.

## State and Persistence Behavior
It builds and imports local images during tests, then publishes nightly images to Docker Hub and syncs them to Alibaba Cloud registries. It does not modify repo files.

## Dependencies and Integration Points
It depends on the Docker Makefile nightly targets, dashboard UI build, microk8s setup scripts, E2E Python tests, Docker Hub credentials, ACR credentials, and image sync script.

## Risks
Because it runs on every push to master and schedule, it can consume significant CI resources. It duplicates much of `go.yaml` E2E logic but uses nightly image paths. Publishing is tied to workflow conclusion logic and selected dependencies; without-kubelet lanes are not listed in the `success-all-test` needs array. External registry and secret failures can make test-passing builds fail at publish time.

## Test Signals
Passing E2E jobs validate nightly images in microk8s across CE/EE and supported mount modes. Passing final publish steps indicates nightly artifacts are available in registries.
