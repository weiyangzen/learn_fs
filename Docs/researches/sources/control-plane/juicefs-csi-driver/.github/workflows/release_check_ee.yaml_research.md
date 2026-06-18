# sources/control-plane/juicefs-csi-driver/.github/workflows/release_check_ee.yaml

## Purpose
This workflow validates an EE release-check mount image against CSI E2E tests.

## Important Jobs and Steps
`build-matrix` emits the standard release-check test modes. `e2e-ee-test` cleans disk, prepares microk8s, logs into Docker Hub, builds dashboard dist, builds EE and CSI release-check images with `JFSCHAN=beta`, imports them, deploys CSI, and runs `.github/scripts/e2e-test.py` with EE token credentials. `success-all-test` gates the final conclusion.

## Control Flow
It runs on manual dispatch and pushes to the `release_check` branch. The E2E matrix covers pod, shared pod mount, pod provisioner, webhook, webhook provisioner, and process modes.

## State and Persistence Behavior
It builds and imports local images into microk8s and uses secrets for Docker Hub and EE volume token. It does not persist repo changes.

## Dependencies and Integration Points
Dependencies include Docker Makefile targets, dashboard UI, microk8s setup, E2E scripts, EE JuiceFS credentials, and the CSI deploy script.

## Risks
The push trigger is narrower than CE (`release_check` exactly). Upterm failure sessions are shorter than other workflows but still expose a live debugging environment. The workflow assumes beta-channel EE assets and secrets are available.

## Test Signals
Success indicates the EE candidate image works with the CSI E2E matrix.
