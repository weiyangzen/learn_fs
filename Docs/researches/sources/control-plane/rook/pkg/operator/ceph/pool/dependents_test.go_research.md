# sources/control-plane/rook/pkg/operator/ceph/pool/dependents_test.go

## Purpose

This file tests `cephBlockPoolDependents`, the helper that detects RADOS namespace CRs blocking `CephBlockPool` deletion.

## Important Test Cases

- No namespaces returns an empty dependent list.
- A namespace whose `spec.blockPoolName` does not match the target pool returns an empty dependent list.
- A namespace whose `spec.blockPoolName` matches returns a non-empty dependent list.

## Control Flow and Test Setup

The test creates a fake Rook clientset-backed `clusterd.Context`, `client.AdminTestClusterInfo`, and `CephBlockPool` target. Each subtest creates RADOS namespace CRs in the fake typed clientset as needed and calls `cephBlockPoolDependents`.

## State and Persistence Signals

All state is fake Rook API state. Assertions use `deps.Empty()` to confirm what the deletion-blocking path would see.

## Dependencies and Integration Points

The test depends on the Ceph API scheme, fake Rook clientset, `client.AdminTestClusterInfo`, and `testify/assert`.

## Risks and Gaps

The helper-local `newClusterdCtx` ignores its variadic `objects` parameter, which is harmless because subtests explicitly create resources afterward. The test does not assert the exact dependent names, list error behavior, or multiple namespace handling.

## Test Signals

The file confirms the primary match/no-match behavior for pool RADOS namespace dependents, sufficient for basic deletion-blocking confidence.
