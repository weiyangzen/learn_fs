<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_remove_test.go -->
# sources/cloud-native/moby/client/checkpoint_remove_test.go

Purpose: validates the checkpoint delete client path for the experimental checkpoint API. The file does not define production APIs; it exercises `Client.CheckpointRemove`, `CheckpointRemoveOptions`, and the shared mock client helpers.

Control flow and dependencies: tests construct a client with `New(WithMockClient(...))`, call `CheckpointRemove` with a container id and checkpoint id, and assert either containerd `cerrdefs` error classes or the generated HTTP request. The success case expects `DELETE /containers/container_id/checkpoints/checkpoint_id`; error cases cover daemon 500 and empty or whitespace container ids through `trimID`.

State and integration behavior: no persistent state is modified in the test process beyond the mock transport. The test integrates with `client_mock_test.go` helpers, the versioned request path logic in `Client.getAPIPath`, and status-code-to-error mapping in the request layer.

Risks and test signals: the main risk covered is accidental route or method drift for checkpoint removal. It does not assert the optional `CheckpointDir` query, so that behavior depends on implementation coverage elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_remove_test.go -->
