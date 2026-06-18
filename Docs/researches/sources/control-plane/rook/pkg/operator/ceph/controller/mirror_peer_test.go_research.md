# sources/control-plane/rook/pkg/operator/ceph/controller/mirror_peer_test.go

## Purpose
`mirror_peer_test.go` provides unit coverage for mirror peer token validation and token expansion.

## Important APIs, Types, and Functions
`TestValidatePeerToken` verifies empty data, missing `pool` for `CephRBDMirror`, and success for RBD and CephFS mirror objects. `TestGenerateStatusInfo` is a placeholder with no cases. `TestExpandBootstrapPeerToken` passes a base64-encoded peer token into `expandBootstrapPeerToken()` and checks the decoded result contains `namespace`.

## Control Flow, State, and Persistence
The tests do not persist Kubernetes Secrets or update CephCluster status. Token expansion is done fully in memory. A mock executor is present but not used by `expandBootstrapPeerToken()` in the current implementation.

## Dependencies and Integration Points
The tests depend on Ceph CR mirror types, `cephclient.AdminTestClusterInfo()`, base64 decoding, and testify assertions.

## Risks
`TestGenerateStatusInfo` provides no signal. The mock executor setup appears obsolete for token expansion and could mislead maintainers. The namespace assertion is substring-based rather than JSON-struct-based, so it would miss malformed JSON that happens to contain the word.

## Test Signals
Signals are basic validation rules and successful namespace injection. Missing signals include invalid base64, invalid JSON, exact token fields, Secret naming/status info, and cluster-level key rotation status.
