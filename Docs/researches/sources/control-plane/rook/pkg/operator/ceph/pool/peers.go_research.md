# sources/control-plane/rook/pkg/operator/ceph/pool/peers.go

## Purpose

This file implements bootstrap peer import for RBD mirroring on `CephBlockPool`. It reads configured peer-token Secrets and imports each token into the Ceph pool's mirroring configuration.

## Important APIs and Functions

- `(*ReconcileCephBlockPool) reconcileAddBootstrapPeer(pool, namespacedName) (reconcile.Result, error)` is called from `configurePoolMirroring` when mirroring is enabled.

## Control Flow

If `pool.Spec.Mirroring.Peers` is nil, the function returns success without action. Otherwise it loops over `Peers.SecretNames`. For each Secret, it reads the Secret from `r.clusterInfo.Namespace` using the core clientset and the operator manager context. Missing or failed Secret reads return `opcontroller.ImmediateRetryResult`. Secret data is validated with `opcontroller.ValidatePeerToken`, and then imported with `client.ImportRBDMirrorBootstrapPeer`, passing pool name, direction, and token data.

## State and Persistence Behavior

Kubernetes Secret state is read-only. Ceph mirroring peer state is mutated by `ImportRBDMirrorBootstrapPeer`, which imports remote bootstrap tokens into the local pool's RBD mirroring config.

## Dependencies and Integration Points

The function depends on the pool controller's clusterd context and cluster info, Kubernetes Secrets, `opcontroller.ValidatePeerToken`, `client.ImportRBDMirrorBootstrapPeer`, Rook logging, and controller-runtime reconcile results. It is integrated into `controller.go` after the local bootstrap peer Secret is created.

## Risks and Edge Cases

- Secrets are always read from `r.clusterInfo.Namespace`, not necessarily `pool.Namespace`; for normal pool/cluster scope this should match, but it is an important namespace contract.
- All Secret read errors, including not-found, are treated as retryable failures.
- The function imports all listed Secrets on every reconcile; idempotency depends on Ceph import behavior.
- Direction is passed from `s.Data["direction"]`; validation must ensure it exists and is valid.

## Test Signals

`controller_test.go` indirectly covers missing peer Secret failure and existing peer Secret success through the full pool reconcile path. There is no direct unit test for this function with multiple peers, invalid token data, or import command failure.
