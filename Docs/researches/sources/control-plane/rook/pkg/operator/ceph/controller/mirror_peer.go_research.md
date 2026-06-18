# sources/control-plane/rook/pkg/operator/ceph/controller/mirror_peer.go

## Purpose
`mirror_peer.go` creates, validates, names, and stores bootstrap peer tokens used for RBD and CephFS mirroring. It also manages cluster-level RBD mirror peer cephx rotation status.

## Important APIs, Types, and Functions
`CreateBootstrapPeerSecret()` dispatches by object type: `CephBlockPool` creates a pool-scoped RBD peer token, `CephCluster` creates a cluster-wide RBD token with optional key rotation, and `CephFilesystem` creates a CephFS peer token. `GenerateBootstrapPeerSecret()` builds the Kubernetes Secret with `token` and entity key (`pool`, `fs`, or `cluster`). `buildBootstrapPeerSecretName()` creates deterministic names. `GenerateStatusInfo()` reports Secret names for pool/filesystem status. `ValidatePeerToken()` checks required Secret data. `expandBootstrapPeerToken()` base64-decodes the token JSON, injects cluster namespace, and re-encodes it. `shouldRotateMirrorPeerKeys()` and `updateCephClusterCephxRbdMirrorStatus()` integrate with cephx rotation policy and status.

## Control Flow, State, and Persistence
Token creation starts with Ceph CLI/client calls, then the token is optionally expanded and stored in a `v1.Secret` via `k8sutil.CreateOrUpdateSecret()`. Owner references are set before persistence. Cluster-level RBD peer creation fetches the current CephCluster, decides whether to rotate keys, creates a token, then updates `Status.Cephx.RBDMirrorPeer` with conflict retry.

## Dependencies and Integration Points
The file integrates with `cephclient` mirror bootstrap APIs, Kubernetes Secrets, Ceph CR types, owner references, `keyring` cephx rotation helpers, `reporting.UpdateStatus()`, controller-runtime clients, and `WatchPeerTokenSecretPredicate()` in `predicate.go`.

## Risks
The default case wraps a nil `err`, producing an unclear error for unsupported object types. `ValidatePeerToken()` only requires `pool` for `CephRBDMirror`; CephFS mirror validation only requires `token`. Token expansion assumes valid base64 JSON matching `cephclient.PeerToken`. Secret creation ignores `AlreadyExists` even though `CreateOrUpdateSecret` should normally handle updates. Status update and token creation are separate operations, so partial success can leave token/status skew.

## Test Signals
`mirror_peer_test.go` covers token validation requirements and namespace injection in expanded tokens. It leaves status info tests empty and does not cover Secret creation, Ceph client failures, unsupported object types, key rotation decisions, or status conflict retries.
