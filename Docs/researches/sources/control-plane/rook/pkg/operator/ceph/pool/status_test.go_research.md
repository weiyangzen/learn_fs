# sources/control-plane/rook/pkg/operator/ceph/pool/status_test.go

Purpose: focused unit tests for the pool status info map generation logic.

Important APIs/types/functions: `TestUpdateStatusInfo` exercises `updateStatusInfo` directly with hand-built `CephBlockPool` objects.

Control flow: the test creates a replicated pool in Progressing state, verifies `type=Replicated`, default failure domain, and no mirror bootstrap key. It then creates an erasure-coded pool with failure domain `osd`, verifies `type=Erasure Coded`, the explicit failure domain, and no mirror info. Finally it enables mirroring while still Progressing, verifies mirror info is absent, then changes phase to Ready and verifies `opcontroller.RBDMirrorBootstrapPeerSecretName` appears.

State and persistence behavior: no Kubernetes client is used; state changes are in-memory mutations of `Status.Info`, `Status.Phase`, and `Spec.Mirroring`.

Dependencies/integration: imports Ceph API types and `opcontroller` constants so it validates the public keys consumed by mirroring status users.

Risks: does not test the full `updateStatus` retry/update path, observed generation, CephX token persistence, NotFound handling, conflict handling, or `updatePoolID` Ceph query behavior.

Test signals: confirms the most user-visible status info shape and guards against accidentally exposing mirroring bootstrap data before the pool is Ready.
