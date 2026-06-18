# sources/control-plane/rook/pkg/operator/ceph/pool/status.go

Purpose: status helper logic for `ReconcileCephBlockPool`, centralizing status phase, info map, observed generation, CephX peer token, and pool ID updates.

Important APIs/types/functions: `updateStatus`, `updateStatusInfo`, and `updatePoolID`. `updateStatus` is a method on `ReconcileCephBlockPool`; `updateStatusInfo` is a pure-ish helper over a `CephBlockPool`; `updatePoolID` queries Ceph pool details.

Control flow: `updateStatus` retries on Kubernetes update conflicts. It fetches the latest pool, initializes status when nil, populates pool ID when transitioning to Ready and `PoolID` is unset, updates `Phase`, rebuilds status `Info`, records observed generation when available, stores CephX peer token when provided, and writes through `reporting.UpdateStatus`. `updateStatusInfo` adds mirroring bootstrap info only when the pool is Ready and mirroring enabled, then records type and failure domain. `updatePoolID` calls `cephclient.GetPoolDetails` and logs rather than returning on failure.

State and persistence: persists status subresource fields on `CephBlockPool`: `Phase`, `Info`, `ObservedGeneration`, `Cephx.PeerToken`, and `PoolID`. It reads Ceph cluster state to fill the numeric pool ID.

Dependencies/integration: depends on controller-runtime client, retry-on-conflict, `cephclient.GetPoolDetails`, `opcontroller.GenerateStatusInfo`, `k8sutil.ObservedGenerationNotAvailable`, and `reporting.UpdateStatus`.

Risks: the method logs any final retry error but always returns nil, which can hide failed status persistence from callers. Pool ID retrieval failure does not fail reconcile. Status `Info` is rebuilt from scratch, so consumers must not expect arbitrary existing keys to survive.

Test signals: `status_test.go` focuses on `updateStatusInfo` for replicated vs erasure-coded pools, default vs explicit failure domain, and mirroring info only when Ready.
