# sources/control-plane/longhorn-engine/app/cmd/sync_agent.go

## Purpose
Defines the `sync-agent` server command and `sync-agent-server-reset` control command used for replica rebuild/file sync workflows.

## Important APIs, Types, and Functions
- `SyncAgentCmd()` declares listen address, listen port range, replica address, and replica instance-name flags.
- `SyncAgentServerResetCmd()` resets sync agent state through a sync task.
- `startSyncAgent()` parses port range, listens on TCP, creates `sync/rpc.NewSyncAgentServer`, and serves.
- `doReset()` calls `sync.Task.Reset`.

## Control Flow
`startSyncAgent` splits `start-end`, parses both endpoints, creates a cancellable context, binds TCP, constructs a sync-agent RPC server with replica address and identity, then serves. `doReset` uses global controller URL/volume/engine identity to create a sync task and reset sync-agent server state.

## State and Persistence Behavior
The server maintains runtime sync-agent state and coordinates file sync/rebuild operations against the configured replica. Reset mutates sync-task/sync-agent runtime state. No direct disk writes occur here, but sync operations invoked via server affect replica files.

## Dependencies and Integration Points
Used by `replica.go` as an optional child process. Depends on `pkg/sync` and `pkg/sync/rpc`. Integration helpers call `sync_agent_server_reset` during cleanup and no-frontend reset flows.

## Risks and Edge Cases
Port range parsing accepts any two integers without verifying ordering or free ports. A listen failure aborts startup. Identity flags are important because `test_identity.py` verifies sync-agent volume/instance validation.

## Test Signals
`integration/core/test_identity.py` validates sync-agent identity failures and replica address mismatches. Many integration tests call reset as cleanup before controller/replica teardown.
