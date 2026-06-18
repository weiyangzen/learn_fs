# sources/control-plane/rook/pkg/operator/ceph/config/store.go

## Purpose
`store.go` manages the Kubernetes-backed Ceph config data that every Ceph daemon needs at runtime, especially the current monitor host list and initial monitor members. Although `Store` still owns a `ConfigMapKVStore`, the active behavior in this file persists monitor settings in the `rook-ceph-config` Secret because CSI consumers require Secret-backed data.

## Important APIs, Types, and Functions
`StoreName` is the shared object name for both the historical ConfigMap store and the Secret. `GetStore()` wires namespace, `clusterd.Context`, Kubernetes clientset, and owner info. `CreateOrUpdate()` delegates to `createOrUpdateMonHostSecrets()`. That helper calls `cephclient.PopulateMonHostMembers()` to derive monitor IDs and host endpoints, writes `mon_host` and `mon_initial_members`, sets the controller reference, creates the Secret if missing, and updates it. `StoredMonHostEnvVars()` exposes `ROOK_CEPH_MON_HOST` and `ROOK_CEPH_MON_INITIAL_MEMBERS` from Secret keys. `StoredMonHostEnvVarFlags()` converts those env refs to Ceph CLI flags with `config.NewFlag`.

## Control Flow, State, and Persistence
The state is persisted in a namespace-scoped `v1.Secret` named `rook-ceph-config` with type `k8sutil.RookType`. Consumers mount or reference it via env vars, then Ceph commands receive `--mon-host=$(ROOK_CEPH_MON_HOST)` and `--mon-initial-members=$(ROOK_CEPH_MON_INITIAL_MEMBERS)`. The update path is deliberately simple: compute from the current `ClusterInfo`, create on not found, then issue an update. Ownership is anchored through `OwnerInfo.SetControllerReference()`.

## Dependencies and Integration Points
This integrates with `cephclient.ClusterInfo`, monitor endpoint formatting, Kubernetes Secrets, `clusterd.Context.Clientset`, `k8sutil.OwnerInfo`, daemon env construction in `controller/spec.go`, and all Ceph daemon argument builders that include stored monitor flags.

## Risks
The create path falls through to an update after creating the Secret. Fake clients tolerate this in tests, but real Kubernetes updates usually require a current `resourceVersion`; this path relies on client behavior or may be fragile if the newly created object is not reused. Error text contains a typo (`moh host`). `Store.configMapStore` is retained but unused here, which can confuse readers. Since daemons consume these Secret keys dynamically as env vars, missing or malformed monitor endpoints can break every daemon startup.

## Test Signals
`store_test.go` verifies create and update across one- and three-monitor cluster infos and both msgr2-only and v1/v2 endpoint strings. It also validates env var and CLI flag pairing.
