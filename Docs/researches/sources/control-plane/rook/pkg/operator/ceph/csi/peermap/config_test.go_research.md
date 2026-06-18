# sources/control-plane/rook/pkg/operator/ceph/csi/peermap/config_test.go

## Purpose
This test file validates peer-map data structure behavior, peer token decoding, peer pool ID discovery, and mapping ConfigMap creation/update.

## Important APIs, Types, and Functions
Tests include `TestAddClusterIDMapping`, `TestUpdateClusterPoolIDMap`, `TestAddPoolIDMapping`, `TestSinglePeerMappings`, `TestMultiPeerMappings`, `TestDecodePeerToken`, and `TestCreateOrUpdateConfig`. Helpers define fake peer tokens/secrets, fake mirrored pools, `saveMockDataInTempFile`, a `mockExecutor`, and `validateConfig`.

## Control Flow, State, and Persistence
The mock executor returns local pool details and writes peer pool details into temp output files that `getPeerPoolDetails` later reads. Tests use fake Kubernetes clientsets for peer Secrets and controller-runtime fake clients for the mapping ConfigMap. Env vars identify operator pod and namespace for owner reference creation.

## Dependencies and Integration Points
The tests use Rook Ceph API schemes, fake operator pods/replicasets, `exectest.MockExecutor`, Kubernetes fake clients, and base64-encoded peer tokens matching `cephclient.PeerToken`.

## Risks
The temp-file helper appends to any matching temp file by prefix, which is acceptable in a controlled unit test but could be flaky if stale temp files remain. `TestCreateOrUpdateConfig` comments out one validation after adding data, reducing coverage of the second create/update step.

## Test Signals
Signals cover idempotent cluster map adds, updating an existing peer pool ID, adding new pools and clusters, multi-peer mapping shape, invalid token rejection, and persisted ConfigMap JSON equivalence.
