# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/list.go

## Purpose
Lists BeeGFS nodes from the node store with optional node-type filtering, NIC inclusion, and UDP heartbeat reachability checks.

## Important APIs, Types, And Functions
Exports `GetNodes_Config`, `GetNodes_Nic`, `GetNodes_Node`, and `GetNodes`. Internal helpers are `checkReachability` and `recvDatagrams`.

## Control Flow
`GetNodes` fetches the `NodeStore`, filters nodes by `FilterByNodeType`, wraps their NICs, and stores NIC wrappers by address. If reachability is requested, it applies a timeout when the context has no existing deadline, sends a BeeMsg heartbeat UDP datagram to each NIC, and receives responses until all are marked reachable or the context expires.

## State And Persistence
No durable state. Reachability mutates the returned `GetNodes_Nic.Reachable` fields in memory. UDP socket lifetime is scoped to a single check.

## Dependencies And Integration Points
Uses `config.NodeStore`, BeeGFS node/NIC types, BeeMsg heartbeat assembly, UDP networking, and caller-supplied context deadlines.

## Risks And Edge Cases
`recvDatagrams` creates `buf := make([]byte, 0, util.MaxDatagramSize)` and passes it to `ReadFrom`; a zero-length buffer can prevent reading payload bytes, though source address may still be returned on some platforms. The socket itself does not set a read deadline; cancellation relies on context selection while the receiver goroutine may remain blocked in `ReadFrom` if not otherwise interrupted. NIC address strings must exactly match `from.String()` to mark reachability.

## Test Signals
No direct tests. Useful tests need UDP socket fakes or integration tests for heartbeat matching, context timeout, filtering, and invalid NIC addresses.
