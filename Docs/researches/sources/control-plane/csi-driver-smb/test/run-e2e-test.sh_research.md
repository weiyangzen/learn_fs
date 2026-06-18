# sources/control-plane/csi-driver-smb/test/run-e2e-test.sh

## Purpose
This script prepares and runs SMB CSI e2e tests for Windows-enabled environments, especially GCE/GKE-style CI.

## Important APIs, Types, And Functions
Functions are `configure_docker` and `setup_e2e`. Variables are `PROJECT_ROOT`, `GCE_PROJECT`, `TEST_WINDOWS=true`, and `REGISTRY=gcr.io/$GCE_PROJECT`.

## Control Flow
The script reads the active gcloud project, configures Docker auth, runs `make e2e-bootstrap`, `make install-smb-provisioner`, and `make create-metrics-svc`, then runs `make e2e-test`.

## State, Persistence, And Dependencies
It changes cluster state by installing the driver/provisioner and metrics service, and changes local Docker auth state. Dependencies include gcloud, Docker, Make, kubeconfig, and a cluster with Windows nodes.

## Integration Points
The script feeds `TEST_WINDOWS` into the Go e2e suite and uses Make targets from the SMB driver repository.

## Risks And Test Signals
It assumes `gcloud config get-value project` is valid and that Docker auth is safe to mutate. Signals are make target exit codes and the downstream Ginkgo/JUnit results.
