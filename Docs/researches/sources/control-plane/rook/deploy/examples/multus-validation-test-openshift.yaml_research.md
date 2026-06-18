# sources/control-plane/rook/deploy/examples/multus-validation-test-openshift.yaml

Purpose: creates minimal OpenShift namespace RBAC for a Multus validation test service account.

Important APIs/types/functions: `ServiceAccount/multus-validation-test`, `Role/multus-validation-test`, and `RoleBinding/multus-validation-test` in `openshift-storage`.

Control flow: the role allows the validation pod or test workflow to interact with the namespace resources it needs while running Multus validation on OpenShift.

State and persistence: persists only service account and RBAC policy.

Dependencies/integration: integrates with OpenShift storage namespace conventions and Multus validation jobs/tests outside this file.

Risks: namespace is hard-coded to `openshift-storage`; applying in vanilla Kubernetes or a differently named OpenShift namespace needs edits.

Test signals: `kubectl auth can-i` for the service account and successful Multus validation pod execution.
