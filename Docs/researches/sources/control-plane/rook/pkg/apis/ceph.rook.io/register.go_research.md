# sources/control-plane/rook/pkg/apis/ceph.rook.io/register.go

Purpose: defines the root API group name for Rook Ceph APIs.

Important APIs/types/functions: package `cephrookio` and constant `CustomResourceGroupName = "ceph.rook.io"`.

Control flow: no runtime control flow; other packages import this constant when registering or referring to the API group.

State and persistence: no mutable state or persistence.

Dependencies/integration: integrates with Kubernetes API registration and generated CRD group naming.

Risks: changing this value would be a breaking API group migration for all Ceph CRDs.

Test signals: generated CRDs and clients use `ceph.rook.io` consistently.
