# sources/cloud-native/cri-o/test/mocks/oci/oci.go

## Purpose
Generated GoMock for CRI-O internal OCI `RuntimeImpl`.

## Important APIs, Types, And Functions
`MockRuntimeImpl` covers attach, exec, execsync, create/start/stop/delete, pause/unpause, checkpoint/restore, stats, port-forward, log reopen, monitor probe, streaming URL setup, status updates, and resource updates.

## Control Flow
Each runtime operation is a GoMock call with typed returns. Streaming and attach/exec methods include reader/writer and terminal-size channel parameters.

## State And Persistence
No real OCI runtime state. Expectations represent lifecycle outcomes.

## Dependencies And Integration Points
Used by server tests that need to isolate CRI-O logic from runc/crun/conmon. Imports CRI-O OCI containers, stats, OCI specs, CRI API, and CRI streaming remotecommand.

## Risks And Test Signals
Verifies server-to-runtime contracts but not runtime process behavior, conmon interaction, cgroup updates, or IO streaming correctness. Regenerate on `RuntimeImpl` changes.
