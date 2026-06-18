# sources/control-plane/csi-driver-smb/test/external-e2e/run.sh

## Purpose
This script runs Kubernetes external storage e2e tests against the SMB CSI driver using an alternate driver name.

## Important APIs, Types, And Functions
Shell functions are `install_ginkgo`, `setup_e2e_binaries`, and `print_logs`. Variables include `PROJECT_ROOT` from `git rev-parse` and `DRIVER=test`.

## Control Flow
The script installs Ginkgo v1.14.0, downloads Kubernetes v1.24.0 e2e binaries, mutates the example StorageClass and metrics service manifests for the alternate driver name, installs the SMB provisioner and driver, registers a trap to print logs, copies the StorageClass to `/tmp/csi/storageclass.yaml`, then runs `ginkgo -p` with external storage focus and selected skips.

## State, Persistence, And Dependencies
It downloads and extracts binaries in the workspace, modifies tracked example YAMLs in place with `sed -i`, creates cluster resources via `make`, and writes `/tmp/csi/storageclass.yaml`. Dependencies include curl, tar, Go, Ginkgo, Make, Kubernetes e2e binaries, kubeconfig, and a working cluster.

## Integration Points
It pairs with `testdriver.yaml`, `deploy/example/storageclass-smb.yaml`, deployment Make targets, and `smb_log.sh`.

## Risks And Test Signals
In-place manifest mutation can dirty the worktree or affect later tests. Pinned old Ginkgo/Kubernetes versions may drift from current dependencies. Signals are external e2e test results and teardown logs from `print_logs`.
