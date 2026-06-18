<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/nodeconns.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/nodeconns.go

Purpose: connection-pool wrapper for reusable BeeMsg TCP connections to one node.

Important APIs/types/functions: `NodeConns`, `NewNodeConns`, `TryGet`, `Put`, `CleanUp`, and `RequestTCP`.

Control flow: `RequestTCP` drains queued connections until one successfully completes `WriteRead`; write-related transport failures close the connection and retry, while non-write errors abort. If no pooled connection works, it opens a new TCP connection, performs the request, and puts the connection back on success.

State and persistence: maintains an in-memory thread-safe FIFO queue of `net.Conn`. `CleanUp` empties and closes all currently queued connections; checked-out connections are caller-owned until returned or closed.

Dependencies and integration points: depends on `queue`, `ConnectTCP`, `WriteRead`, message interfaces, and `ErrBeeMsgWrite`. Used by `NodeStore.RequestTCP`.

Risks: there is no connection limit despite comments noting infinite connection creation. Read-side protocol errors do not retry another connection. Connections can become stale while queued and are only detected on next use.

Test signals: `comm_test.go` verifies that two requests reuse the same accepted TCP connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/nodeconns.go -->
