<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/spec_test.go

## Purpose
This file validates generated CephNFS Deployment specs across base, SSSD, Kerberos, combined security, and liveness-probe cases.

## Important APIs and control flow
`newDeploymentSpecTest` creates a reconciler fixture with fake clients, Ceph version/image, and a daemon config. `TestDeploymentSpec` checks a base deployment's config hash annotation, labels, resource propagation, priority class, and service account. Additional subtests verify SSSD sidecar and init containers, Kerberos init container and absence of SSSD when only Kerberos is set, combined SSSD/Kerberos init and sidecar presence, volume/mount consistency through the pod-template test suite, and default liveness probe properties.

## State and persistence
The tests build Deployment objects in memory without creating them through Kubernetes. The important state is the expected pod template shape and annotations.

## Dependencies and integration points
The test uses Rook fake clientsets, Ceph version fixtures, Rook pod-template tester utilities, Kubernetes resource quantities, and CephNFS CRD security fields. It exercises integration between `spec.go` and `security.go`.

## Risks and test signals
These tests are strong for static pod shape but do not validate Service generation, actual container command execution, host-network/Multus behavior, or custom image pull policy in this file. They catch many regressions involving security mounts, duplicate volumes, resource propagation, and liveness probe defaults.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/spec_test.go -->
