<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec_test.go

## Purpose
This test verifies the Deployment/pod spec produced for the CephFS mirror daemon. It is a focused contract test for `makeDeployment`.

## Important APIs and control flow
`TestPodSpec` builds a fake `CephFilesystemMirror`, `CephCluster` spec, fake controller-runtime client, and `ReconcileFilesystemMirror`, then calls `makeDeployment`. It asserts the Deployment name, daemon volume and mount counts, projected volume source count, default service account, Ceph daemon labels, and the common pod-template suite provided by Rook test helpers.

## State and persistence
The test uses only in-memory runtime objects and a fake client. It does not create real Kubernetes resources or Ceph state. Its persistent signal is the expected shape of generated Kubernetes specs.

## Dependencies and integration points
The test uses Rook's scheme, fake controller-runtime client, Ceph version fixtures, resource quantity APIs, and `test.NewPodTemplateSpecTester`. It checks that mirror resources integrate with Rook's label and pod-template conventions.

## Risks and test signals
Coverage is strong for static Deployment construction but does not cover `start`, keyring generation, Kubernetes create/update behavior, Multus, host networking, or log collector injection. Failures here are likely to indicate label, resource propagation, volume, or service account regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/file/mirror/spec_test.go -->
