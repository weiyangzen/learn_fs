# sources/control-plane/csi-driver-smb/test/utils/deploy-minikube.sh

## Purpose
This script provisions a local minikube cluster and installs the SMB CSI driver and example Samba server.

## Important APIs, Types, And Functions
It exports minikube environment variables, sets `KUBECONFIG`, and pins Kubernetes v1.18.1 plus minikube v1.8.1.

## Control Flow
The script downloads kubectl and minikube, initializes kube/minikube directories, starts minikube with `--vm-driver=none`, updates context, adjusts ownership for Travis, waits for DNS, creates SMB credentials and server, installs the driver, and waits for controller/node readiness.

## State, Persistence, And Dependencies
It mutates host binaries, `$HOME/.kube`, `$HOME/.minikube`, local minikube state, and cluster resources. Dependencies include sudo, curl, minikube, kubectl, and Travis-style filesystem assumptions.

## Integration Points
It is an older CI/local setup path for the same e2e environment used by SMB tests.

## Risks And Test Signals
The script assumes a `travis` user, rootless none-driver behavior, and old Kubernetes versions. Infinite readiness loops can hang. Signals are command exit codes and readiness loops reaching Ready.
