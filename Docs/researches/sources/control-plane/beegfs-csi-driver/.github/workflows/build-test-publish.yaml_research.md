<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/.github/workflows/build-test-publish.yaml -->
# sources/control-plane/beegfs-csi-driver/.github/workflows/build-test-publish.yaml

## Purpose
This GitHub Actions workflow builds, tests, publishes, signs, end-to-end tests, and cleans up BeeGFS CSI driver and operator container images. It runs on pushes to `master`, version tags, manual dispatch, and pull requests affecting non-documentation paths.

## Important Jobs and Steps
`build-test-and-push-images` checks out the repository, sets up Go, builds multi-arch binaries and `chwrap` tarballs, verifies license notices, runs unit tests, builds/pushes/signs the driver image, installs Operator SDK, builds/tests/generates the operator bundle, builds/pushes/signs the operator image, and publishes a test bundle. `e2e-tests` runs on PRs across Kubernetes 1.29.15 through 1.34.1 and BeeGFS 7.4.6/8.2, deploying direct Kustomize driver manifests and examples. `operator-e2e-tests` runs a similar PR matrix through OLM and a `BeeGFSDriver` custom resource. `cleanup-test-images` prunes old GHCR test packages.

## Control Flow
Image names are selected by event type: PRs publish test images, while non-PR events publish retained images. Docker metadata tags are generated from refs, semver tags, and full commit SHA. Downstream e2e jobs depend on the build job and use the SHA-tagged images. Cleanup runs with `always()` after all test jobs.

## State and Persistence
Persistent state includes GHCR images, image signatures, test bundles, and uploaded scorecard artifacts. The workflow mutates the checked-out deployment overlay during e2e tests to inject secrets, TLS certs, and image replacements. It also creates live Minikube clusters and BeeGFS test deployments during job execution.

## Dependencies and Integration Points
The workflow integrates GitHub Actions, Go, project Makefile targets, release-tools build platform variables, Docker Buildx, GHCR, Cosign secrets, Operator SDK, OLM, Minikube, kubectl, BeeGFS package repositories, test environment YAMLs, examples, and Kubernetes CSI sidecars.

## Risks
Timeouts are tight for multi-arch builds and broad e2e matrices. External dependencies include GHCR, package repositories, Minikube downloads, Operator SDK, OLM, and BeeGFS package availability. Cosign signing depends on configured private key secrets. The cleanup job's bundle package extraction uses `OPERATOR_TEST_IMAGE_NAME` for the bundle variable, which looks like a potential package-name bug because `OPERATOR_TEST_BUNDLE_NAME` exists separately.

## Test Signals
Signals include successful binary builds for amd64/arm64, license and NOTICE verification, Go unit tests, generated-code diff checks, image build/push digest outputs, Cosign signing, direct CSI deployment validation by running example pods, operator scorecard, OLM deployment, and final pod-running checks with debug output on failure.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/.github/workflows/build-test-publish.yaml -->
