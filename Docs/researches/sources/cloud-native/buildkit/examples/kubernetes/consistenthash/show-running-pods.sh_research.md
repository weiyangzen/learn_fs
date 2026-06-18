# Research: sources/cloud-native/buildkit/examples/kubernetes/consistenthash/show-running-pods.sh

## Purpose
Shell helper that lists running Kubernetes BuildKit pods.

## Important APIs, Types, and Functions
Uses `kubectl get pods` with selector `app=buildkitd`, field selector `status.phase=Running`, Go template output, and name sorting.

## Control Flow
Sets strict shell flags, defines selector, and emits matching pod names one per line.

## State and Persistence
No state; reads current Kubernetes API state.

## Dependencies and Integration Points
Depends on kubectl, active context, and consistent labels. Feeds consistent-hash and scripting examples.

## Risks and Edge Cases
No namespace is specified, so active context/namespace mistakes matter.

## Test Signals
No tests; validate against a cluster with example manifests.
