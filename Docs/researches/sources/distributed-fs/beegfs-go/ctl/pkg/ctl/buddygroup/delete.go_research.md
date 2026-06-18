# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/delete.go

Purpose: deletes a buddy group through the management service.

Important APIs/types/functions: `Delete`.

Control flow: initializes management client, calls `DeleteBuddyGroup`, returns response or error.

State and persistence: mutates management buddy-group configuration.

Dependencies and integration points: depends on `config.ManagementClient` and management protobuf request/response types.

Risks: no local validation or safety gating; callers must construct safe requests and handle consequences. Returns `resp, err` after checking `err`, which is harmless but redundant.

Test signals: no direct tests. Mock management tests could assert request forwarding and error propagation.
