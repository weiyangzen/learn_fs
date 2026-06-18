# sources/control-plane/csi-driver-smb/test/utils/deploy-kind.sh

## Purpose
This script provisions a local kind cluster, deploys a Samba server, and installs the SMB CSI driver for tests.

## Important APIs, Types, And Functions
Variables are `KUBERNETES_VERSION=v1.18.8` and `KUBECONFIG=$HOME/.kube/config`. It downloads kind v0.9.0 and kubectl for the configured Kubernetes version.

## Control Flow
The script installs binaries with sudo, creates a kind cluster, writes kubeconfig, waits for DNS, creates `smbcreds`, deploys the example SMB server, waits for it, installs the driver, and waits for controller and node pods to become Ready.

## State, Persistence, And Dependencies
It mutates `/usr/local/bin`, creates a kind cluster, changes `$HOME/.kube`, and creates Kubernetes resources. Dependencies include curl, sudo, kind, kubectl, and repository deployment manifests.

## Integration Points
It prepares the environment expected by SMB e2e tests and example storage classes.

## Risks And Test Signals
Pinned old Kubernetes/kind versions may be incompatible with current host tooling. Readiness waits parse JSONPath strings and loop indefinitely. Signals are kubectl readiness checks and final installation log.
