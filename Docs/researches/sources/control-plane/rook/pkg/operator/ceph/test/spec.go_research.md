# sources/control-plane/rook/pkg/operator/ceph/test/spec.go

Purpose: shared label assertions for Ceph operator resources.

Important APIs/types/functions: `AssertLabelsContainCephRequirements`.

Control flow: the helper first delegates generic Rook label checks to `optest.AssertLabelsContainRookRequirements`, then converts the label map to `key=value` strings and asserts it contains expected Kubernetes recommended app labels, Ceph daemon identity labels, operator namespace, and Rook cluster namespace.

State and persistence behavior: no persistence. Reads `POD_NAMESPACE` from the environment to validate the operator namespace label.

Dependencies/integration: depends on generic operator test helpers, `os.Getenv`, Kubernetes label conventions, and testify assertions.

Risks: environment dependence means tests must set `POD_NAMESPACE` consistently. It validates subset containment, so extra labels are allowed.

Test signals: no direct tests in this subset; consumers get consistency checks for Ceph pod/deployment/daemonset label generation.
