<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/comm.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/util/comm.go

Purpose: low-level UDP request and TCP connection establishment helpers for BeeMsg communication.

Important APIs/types/functions: `MaxDatagramSize`, `RequestUDP`, `recvResponse`, `ConnectTCP`, and `connectLoop`.

Control flow: UDP opens an ephemeral socket, assembles the request once, sends it to every resolvable address, fails only if all sends fail, then optionally reads one response and disassembles it based on header `MsgLen`. TCP starts `connectLoop` in a goroutine, tries addresses in order with per-attempt timeout, returns the first successful connection or accumulated errors, and optionally authenticates by writing `AuthenticateChannel`.

State and persistence: no persistence. TCP connections returned here are later pooled by `NodeConns`; UDP sockets are per-request.

Dependencies and integration points: depends on `net`, contexts, `msg`, `types.MultiError`, and `AssembleBeeMsg`/`DisassembleBeeMsg`/`WriteTo`. Used directly by `NodeStore.RequestUDP` and indirectly by `NodeConns.RequestTCP`.

Risks: UDP response goroutine can remain blocked until socket close when context cancels; defer close eventually unblocks it. UDP accepts the first datagram without checking sender. `RequestUDP` with an empty address slice returns an all-sends-failed error via equality with zero errors/zero addrs. TCP timeout is per address while context is global.

Test signals: `comm_test.go` covers successful TCP connect with/without auth, TCP request reuse through `NodeConns`, UDP echo, and cancellation for TCP/UDP requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/util/comm.go -->
