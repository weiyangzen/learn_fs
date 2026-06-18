# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/resync/start.go

Purpose: starts buddy group resynchronization through management.

Important APIs/types/functions: `StartResync(ctx context.Context, group beegfs.EntityId, timestampSec int64, restart bool) error`.

Control flow: obtains management client, converts the buddy group ID to protobuf, sends `StartResyncRequest` with timestamp and restart pointers, discards the response, and returns any error.

State and persistence: triggers server-side resync work for buddy groups.

Dependencies and integration points: uses `config.ManagementClient` and management protobuf resync API.

Risks: no local validation; callers own target/group selection and user confirmation. Errors are direct from management/gRPC.

Test signals: no direct tests. Mock management tests could verify request forwarding.
