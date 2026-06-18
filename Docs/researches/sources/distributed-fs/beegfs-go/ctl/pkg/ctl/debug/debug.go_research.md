# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/debug/debug.go

Purpose: sends generic debug commands to a BeeGFS node over the BeeMsg TCP path.

Important APIs/types/functions: `GenericDebugCmd`.

Control flow: gets the global node store, sends `msg.GenericDebug` with the command bytes to the selected node, receives `GenericDebugResp`, and returns the response as a string.

State and persistence: command effects depend entirely on the server-side debug command; this wrapper itself stores nothing.

Dependencies and integration points: depends on `config.NodeStore`, BeeGFS entity IDs, and BeeMsg generic debug request/response types.

Risks: generic debug commands may expose or mutate low-level server state depending on server support. No local allowlist or validation is present here.

Test signals: no direct tests. Mock node-store tests could assert command bytes and error propagation.
