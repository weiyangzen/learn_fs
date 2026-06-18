# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30/destroy.sh

## Purpose
This script removes a hostpath CSI deployment by deleting all Kubernetes resources that carry the deployment's standard labels. It is intended to stay synchronized with the deploy scripts and provides a simple cleanup path for test clusters.

## Important APIs, Types, And Functions
There are no shell functions. The script uses two `kubectl delete` commands under `set -e` and `set -o pipefail`. Both select resources with `app.kubernetes.io/instance=hostpath.csi.k8s.io` and `app.kubernetes.io/part-of=csi-driver-host-path`.

## Control Flow
The first delete targets the Kubernetes `all` category across all namespaces and waits for deletion. The second delete explicitly removes `role`, `clusterrole`, `rolebinding`, `clusterrolebinding`, `serviceaccount`, `storageclass`, and `csidriver` resources across all namespaces with the same labels.

## State, Persistence, And Dependencies
The script mutates only Kubernetes API state. It does not remove host data directories like `/var/lib/csi-hostpath-data` or kubelet plugin directories from nodes. It depends on `bash` and a configured `kubectl` with permissions to delete namespaced and cluster-scoped resources.

## Integration Points
Its deletion contract relies on labels applied by `deploy-hostpath.sh` and the deployment manifests. It complements the hostpath deploy scripts for CI and local test cleanup.

## Risks
Resources missing the standard labels will survive. Persistent hostPath data on nodes is not cleaned. The command is broad across all namespaces for matching labels, so unrelated resources with the same labels would be deleted. If CRDs or snapshot metadata custom resources are introduced without labels or without explicit resource kinds here, cleanup can be incomplete.

## Test Signals
A good validation deploys the driver, runs this script, then checks that labeled `all`, RBAC, service account, storage class, and CSIDriver resources are gone. It should also verify repeated runs against an already-clean cluster fail or pass as expected for the chosen `kubectl delete` behavior.
