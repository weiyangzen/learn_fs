# sources/control-plane/juicefs-csi-driver/Makefile

## Purpose
The root Makefile centralizes build, test, dashboard, manifest generation, dev deployment, image, mock generation, npm install, and documentation-check commands for the JuiceFS CSI driver.

## Important Targets and Variables
Key variables include `IMAGE`, `REGISTRY`, `DASHBOARD_IMAGE`, `TARGETARCH`, `VERSION`, `GIT_BRANCH`, `GIT_COMMIT`, `DEV_TAG`, `BUILD_DATE`, `PKG`, `CLIENT_GO_PKG`, and `LDFLAGS`. The `juicefs-csi-driver` target builds `./cmd/` for Linux with embedded version metadata. `test` runs Go package tests under `./pkg/...`; `test-sanity` runs CSI sanity tests. Dashboard targets build UI dist, lint UI, build `cmd/dashboard`, and build dashboard images. `yaml` regenerates deploy manifests through kustomize and updates install scripts. Dev targets build images, import or push them to local clusters, generate kustomize overlays, and deploy with `kapp`.

## Control Flow
Targets compose build steps through dependencies. `install-dev` chains verify, tests, dev image build/push, and deployment. The `push-dev` target branches on `DEV_K8S` to support microk8s image import, kubeadm registry push, or minikube cache add. Manifest generation uses `kustomize build`, `sed` substitutions, and script updates.

## State and Persistence Behavior
The Makefile writes binaries under `bin/`, generated manifests under `deploy/`, dev overlays under `deploy-dev/`, coverage files through test targets, image tarballs transiently in microk8s flows, and Docker images in local/remote registries. It can mutate generated YAML files in the source tree.

## Dependencies and Integration Points
It depends on Go, Docker, pnpm/npm, kustomize, kubectl, kapp, minikube or microk8s tooling, mockgen, and repository scripts under `hack/`. GitHub workflows call `make`, `make verify`, `make test`, `make test-sanity`, `make dashboard-dist`, and several Docker Makefile targets.

## Risks
Many targets assume specific local tools and cluster types. Generated manifest targets use `sed -i.orig` for macOS compatibility but can leave `.orig` artifacts. Version metadata depends on git state and can produce dirty tags. Image target behavior varies by `DEV_K8S`, so local and CI flows can diverge.

## Test Signals
`make verify`, `make test`, `make test-sanity`, `make dashboard-lint`, and `make check-docs` are the primary local signals. CI workflows exercise these targets and image build paths.
