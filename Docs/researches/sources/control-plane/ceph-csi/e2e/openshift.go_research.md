# sources/control-plane/ceph-csi/e2e/openshift.go

## Purpose
`openshift.go` detects whether the e2e suite is running on OpenShift. It probes the OpenShift `clusterversion.config.openshift.io/version` resource and reports a boolean instead of forcing non-OpenShift clusters to fail.

## Important APIs, Types, And Functions
`detectOpenShift() (bool, error)` is the only function. It calls `e2ekubectl.RunKubectl` in the `openshift` namespace with a JSONPath query for `.status.desired.version`. It uses `isNoSuchResourceCLIError` to distinguish absence of the OpenShift API from other kubectl failures and logs the version through `framework.Logf` when detection succeeds.

## Control Flow
The function runs `kubectl get clusterversion.config.openshift.io/version`. If kubectl returns an error that means the resource type is unavailable, it returns `(false, nil)`. Any other error is returned as `(false, err)`. On success, the detected desired version is logged and the function returns `(true, nil)`.

## State, Persistence, And Dependencies
There is no local or persistent state. The function depends on the external kubectl command path used by Kubernetes e2e framework helpers, cluster RBAC permitting access to the clusterversion object, and the local `isNoSuchResourceCLIError` classifier defined elsewhere in the e2e package.

## Integration Points
Other e2e tests can use this helper to conditionally run OpenShift-specific assertions or skip behavior that differs between OpenShift and vanilla Kubernetes. It uses the same kubectl wrapper and logging approach as the rest of the Ceph-CSI e2e code.

## Risks
The command uses the namespace argument `openshift`, but `clusterversion` is a cluster-scoped OpenShift resource; this works with kubectl but may be confusing when diagnosing RBAC failures. Detection can return an error rather than `false` if kubectl is unavailable, credentials are invalid, or permissions deny the get request. The JSONPath includes shell-style quotes as part of the argument; this matches the wrapper's current usage but could be brittle if the wrapper changes quoting behavior.

## Test Signals
Useful signals are mocked kubectl success with a version string, "no such resource" errors producing `false, nil`, RBAC or connection errors being propagated, and caller behavior on non-OpenShift clusters. Integration tests should also validate detection against a real OpenShift cluster because the helper relies on kubectl's CRD/resource discovery behavior.
