<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/comm_test.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/comm_test.go

Purpose: socket-level tests for TCP connection/authentication, pooled TCP requests, UDP requests, and cancellation.

Important APIs/types/functions: `TestConnect`, `TestRequestTCP`, `TestRequestTCPCancel`, `TestRequestUDP`, and `TestRequestUDPCancel`.

Control flow: tests create local TCP/UDP listeners, run server goroutines that accept/read/write BeeMsgs, then call client helpers with invalid and valid addresses. Cancellation tests cancel contexts before long operations and require prompt error return.

State and persistence: in-memory sockets and `NodeConns` queues only.

Dependencies and integration points: depends on local network stack, `testify/assert`, `msg.AuthenticateChannel`, `ReadFrom`, `WriteTo`, and `NodeConns`.

Risks: tests use goroutines with timeouts and can be sensitive to scheduling. They do not verify UDP sender validation, multiple-address duplicate responses, authentication failure behavior, or pooled connection cleanup.

Test signals: strong basic transport signal for local loopback behavior and context cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/comm_test.go -->
