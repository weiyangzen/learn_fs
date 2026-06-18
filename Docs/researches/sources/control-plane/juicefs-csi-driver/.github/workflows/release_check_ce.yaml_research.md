# sources/control-plane/juicefs-csi-driver/.github/workflows/release_check_ce.yaml

## Purpose
This workflow validates a candidate CE JuiceFS version against the CSI driver E2E suite before release.

## Important Jobs and Steps
It accepts `ce_juicefs_version` on manual dispatch and also runs on `release_check*` branch pushes. `build-matrix` produces mount mode matrices. `e2e-ce-test` prepares microk8s, logs into Docker Hub, builds dashboard dist, builds a CE mount image with `CEJUICEFS_VERSION`, builds/imports release-check CSI images, deploys CSI, and runs `e2e-test.py` in CE mode. `success-all-test` fails the workflow if the matrix failed.

## Control Flow
The test matrix covers `pod`, `pod-mount-share`, `pod-provisioner`, `webhook`, `webhook-provisioner`, and `process`. All matrix cells share the provided CE version and local release-check image tags.

## State and Persistence Behavior
Images are built/imported into microk8s for validation. No files are committed. External Docker Hub login is used for image pulls/builds.

## Dependencies and Integration Points
It depends on Docker Makefile release-check targets, dashboard build, microk8s setup, E2E scripts, and CE environment variables for MinIO/Redis-backed JuiceFS.

## Risks
Only CE paths are covered. The workflow assumes the supplied CE version can be consumed by Docker targets. Runner disk pressure is mitigated by cleanup, but image builds remain expensive.

## Test Signals
Success means the supplied CE JuiceFS version works with CSI E2E scenarios in the configured microk8s matrix.
