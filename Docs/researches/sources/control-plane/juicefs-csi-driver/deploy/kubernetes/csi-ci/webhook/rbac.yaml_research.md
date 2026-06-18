<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/rbac.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/rbac.yaml

## Purpose
JSON6902 patch that extends `juicefs-external-provisioner-role` for webhook-style controller operation.

## Important APIs, Types, and Resources
The document is a list of `op: add` operations appending to `/rules/-`. It grants wildcard `pods/exec` and, in most variants, read access for `statefulsets/replicasets get` in the `apps` API group.

## Control Flow
Kustomize applies these operations to the ClusterRole after loading the base role. The rendered controller can then exec into pods and inspect owning workloads while handling webhook/provisioner flows.

## State and Persistence
The patch has no independent state. Once applied, the persisted state is expanded ClusterRole permission in the cluster, bound to `juicefs-csi-controller-sa` by the base ClusterRoleBinding.

## Dependencies and Integration Points
Depends on Kubernetes RBAC JSON patch semantics and the exact base ClusterRole name. It integrates with admission-webhook code that needs pod exec or workload lookups.

## Risks
The main risk is privilege expansion: wildcard `pods/exec` is powerful and should be limited to deployment modes that need it. Duplicate application can append duplicate RBAC rules, which is noisy and may hide review errors.

## Test Signals
Validate by rendering the overlay, reviewing effective RBAC with `kubectl auth can-i`, and running webhook/provisioner tests that exercise pod exec and workload ownership checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-ci/webhook/rbac.yaml -->
