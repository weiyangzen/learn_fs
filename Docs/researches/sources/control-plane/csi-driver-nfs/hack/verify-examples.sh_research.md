<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-examples.sh -->
# sources/control-plane/csi-driver-nfs/hack/verify-examples.sh

## Purpose
Smoke-tests example Kubernetes workloads that use the NFS CSI driver.

## Important APIs, Types, and Functions
The script defines `rollout_and_wait()`, uses `kubectl apply`, parses applied resource names with `grep`/`awk`, calls `kubectl rollout status` for workload resources, and otherwise waits for readiness. It applies `deploy/example/storageclass-nfs.yaml`, then deployment and statefulset examples, with optional ephemeral daemonset when the first argument contains `ephemeral`.

## Control Flow, State, and Persistence
It applies the example storage class and workloads to the current Kubernetes context, waits up to five minutes per resource in namespace `default`, and leaves created resources in the cluster. Failures exit due to `set -euo pipefail`.

## Dependencies and Integration Points
It depends on a configured cluster, `kubectl`, a working CSI NFS installation, default namespace access, and example manifests. It is an integration smoke test rather than a unit test.

## Risks and Test Signals
Risks include mutating the active cluster, brittle parsing of `kubectl apply` output, namespace assumptions, and no cleanup. Signals are successful rollout/wait completion for deployment, statefulset, and optional ephemeral daemonset examples.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/hack/verify-examples.sh -->
