<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/client/diff.go -->
# sources/cloud-native/containerd/client/diff.go

Purpose: small adapter exposing the diff service as a combined comparer/applier interface.

Important APIs/types/functions: `DiffService` embeds `diff.Comparer` and `diff.Applier`; `NewDiffServiceFromClient` returns a proxy diff applier cast to `DiffService`.

Control flow: no complex flow; constructor delegates to core diff proxy.

State/persistence: diff operations performed through the returned service can create content and apply filesystem changes, but this file holds no state.

Dependencies/integration: diff gRPC API, core diff interfaces, diff proxy. Used by image unpack, checkpoint RW diff, and restore RW apply.

Risks: constructor uses a type assertion on proxy result; interface changes could panic. Behavior depends entirely on proxy implementation.

Test signals: compile-time/interface assertion through tests, compare/apply RPC error conversion, integration with unpack/checkpoint/restore.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/client/diff.go -->
