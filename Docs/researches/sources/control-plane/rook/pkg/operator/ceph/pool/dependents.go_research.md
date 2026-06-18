# sources/control-plane/rook/pkg/operator/ceph/pool/dependents.go

## Purpose

This helper finds Kubernetes resources that depend on a `CephBlockPool`, currently `CephBlockPoolRadosNamespace` CRs that reference the pool. The block pool controller uses it to block pool deletion when namespaces still exist.

## Important APIs and Functions

- `const radosNamespacesKeyName = "CephBlockPoolRadosNamespaces"` is the dependent kind key used in status and deletion messages.
- `cephBlockPoolDependents(clusterdCtx, clusterInfo, blockpool) (*dependents.DependentList, error)` lists RADOS namespace CRs and returns those whose `spec.blockPoolName` matches the pool name.

## Control Flow

The function creates an empty dependent list, lists `CephBlockPoolRadosNamespaces` in the pool namespace through the Rook clientset, and iterates through results. Matching namespaces are added using `cephv1.GetRadosNamespaceName`, which captures the user-visible namespace name. List failures are wrapped with context.

## State and Persistence Behavior

The function is read-only. Its returned `DependentList` is used by `handleDeletionBlocked` to create status conditions and prevent finalizer removal when namespace dependents exist.

## Dependencies and Integration Points

It depends on Rook typed clientsets, `client.ClusterInfo.Context`, `dependents.DependentList`, Rook controller namespace/name formatting, and logging. It is private to the pool package and called by `controller.go`.

## Risks and Edge Cases

- Only same-namespace `CephBlockPoolRadosNamespace` CRs are considered.
- The debug log currently says a namespace does not depend on the pool even after a matching namespace is added, because the log statement is outside the `if` block. This is a logging bug, not a functional dependency bug.
- If `GetRadosNamespaceName` behavior changes, deletion-blocked messages and emptiness checks may change.

## Test Signals

`dependents_test.go` covers no namespaces, a namespace for a different pool, and one matching namespace. It does not cover list errors or multiple matching namespaces.
