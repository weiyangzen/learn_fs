# sources/distributed-fs/lizardfs/src/uraft/uraft.h

## Purpose
`uraft.h` declares the micro-Raft election engine used by LizardFS metadata HA. It exposes a reduced consensus API whose only responsibility is selecting a single President with a metadata version at least as fresh as the quorum that elected it.

## Important APIs, Types, and Functions
`uRaft::Options` configures local id, UDP port, server list, election timeout range, heartbeat period, and quorum. Protected enums define node roles (`kFollower`, `kCandidate`, `kLeader`) and raw RPC packet types (`kRpcAppendEntries`, `kRpcRequestVote`, response types). `NodeInfo`, `RaftState`, `RpcHeader`, `RpcRequest`, and `RpcResponse` define the in-memory state and wire packet layout. Public APIs are `init()`, `demoteLeader()`, `set_block_promotion()`, `set_options()`, and the virtual callbacks `nodePromote()`, `nodeDemote()`, `nodeLeader(int)`, and `nodeGetVersion()`.

## Control Flow
Consumers configure options, optionally subclass callbacks, then call `init()` to bind sockets and start timers. The protected methods model the full event loop: timer starts, receive dispatch, heartbeat/vote sends, election timeout, heartbeat tick, RPC handlers, socket send, and local interface scanning.

## State and Persistence Behavior
The header stores no persistence, but it defines the runtime ownership: Boost.Asio `io_service`, UDP socket, election/heartbeat/loyalty timers, packet buffer, sender endpoint, per-node vector, local `RaftState`, promotion block flag, and options. Any persistence must be implemented by subclasses through callback side effects.

## Dependencies and Integration Points
It includes platform setup plus Boost.Asio and Boost.Array. `uRaftStatus` inherits it to expose state over TCP, and `uRaftController` inherits that status layer to manage LizardFS metadata server roles.

## Risks and Edge Cases
The wire protocol structs are not explicitly packed or endian-normalized, so the cluster assumes homogeneous ABI. The API requires callbacks to return quickly because they run on the Asio event loop. `Options::quorum` is public but `init()` recomputes it from server count, so external quorum overrides are not effective in the current implementation.

## Test Signals
Compile tests should verify subclass overrides and access to protected state through derived classes. Behavioral tests should cover callback ordering, timer-driven role transitions, and raw packet size assumptions.
