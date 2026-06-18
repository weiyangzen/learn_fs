# sources/control-plane/csi-driver-smb/hack/verify-examples.sh

## Purpose
Runtime smoke test for example Kubernetes manifests.

## Important APIs, Types, and Functions
Defines `rollout_and_wait`, runs `kubectl apply`, parses created app resource names, then uses `kubectl rollout status` or `kubectl wait`.

## Control Flow
Applies the SMB StorageClass, then deploys example Deployment and StatefulSets and waits up to five minutes for readiness.

## State and Persistence
Creates real Kubernetes resources in the default namespace and storage classes in the cluster.

## Dependencies
Requires kubectl, a reachable cluster, working SMB CSI driver, and example manifests.

## Integration Points
Validates deploy/example workloads against the installed driver.

## Risks and Edge Cases
Resource parsing from `kubectl apply` output is brittle. It does not clean up created resources. Namespace is hard-coded to default.

## Test Signals
All examples reach rollout/ready status and script prints completion.
