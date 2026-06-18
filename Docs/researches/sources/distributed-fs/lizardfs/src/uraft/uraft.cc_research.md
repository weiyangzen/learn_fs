# sources/distributed-fs/lizardfs/src/uraft/uraft.cc

## Purpose
`uraft.cc` implements LizardFS' reduced Raft election engine. It elects one local "President" from configured metadata-server peers using UDP RPCs, heartbeat timers, vote requests, a data-version freshness check, and a loyalty window that prevents immediate split-brain after a leader heartbeat. It deliberately omits log replication and only decides leadership.

## Important APIs, Types, and Functions
The implementation backs the `uRaft` class declared in `uraft.h`. Public lifecycle and control APIs are `init()`, `set_options()`, `demoteLeader()`, and `set_block_promotion()`. Derived classes receive `nodePromote()`, `nodeDemote()`, `nodeLeader(int)`, and `nodeGetVersion()` callbacks. Internal election/RPC functions include `startElectionTimer()`, `startHearbeatTimer()`, `heartbeat()`, `electionTimeout()`, `sendHeartbeat()`, `sendRequestForVotes()`, `rpcAppend()`, `rpcAppendResponse()`, `rpcReqVote()`, `rpcReqVoteResponse()`, and `receivePacket()`. Address resolution and automatic local identity use `findNodeID()`, `findMatchingAddress()`, and `scanLocalInterfaces()`.

## Control Flow
Construction sets default election and heartbeat timing, node id/port, term, leader id, vote state, and promotion blocking. `init()` resolves every configured peer endpoint, chooses `state_.id` from options or local interfaces, computes quorum, binds the UDP socket to this node's endpoint, starts election and heartbeat timers, starts async receive, and signs an initial loyalty agreement for fast restarts. Election timeout moves the node to candidate, increments term, self-votes, refreshes `data_version` via `nodeGetVersion()`, sends vote requests, and either waits for quorum or immediately becomes leader in a one-node cluster. Heartbeat ticks advance logical local time, refresh self heartbeat, demote a president that loses loyal quorum, resend candidate vote requests, and send append-entry heartbeats as leader. A leader only calls `nodePromote()` after loyal heartbeat responses reach quorum.

## State and Persistence Behavior
All Raft state is runtime memory: `state_` tracks id, role, term, vote, leader, logical time, president flag, loyalty flag, and current data version; `node_` stores each peer endpoint plus vote, response, heartbeat, and version observations. No term or vote is persisted to disk here. The only persistent signal is indirect: derived `nodeGetVersion()` can read metadata version from the metadata server, and promotion/demotion side effects happen in `uRaftController`.

## Dependencies and Integration Points
The file depends on Boost.Asio UDP sockets and timers, Boost.Bind/date-time/lexical-cast, optional `getifaddrs`, and platform wrappers. It is extended by `uRaftStatus` for TCP status output and by `uRaftController` for LizardFS master/shadow transitions. It also depends on the configured server list matching actual bindable addresses or explicit ids.

## Risks and Edge Cases
The algorithm is intentionally not full Raft: terms/votes are volatile, there is no replicated log, and packet structs are sent as raw in-memory layouts. Safety rests on quorum, version comparison, heartbeat loyalty, and controller-side promotion blocking. Timing is sensitive because `rand()` election jitter is simple and `voteCount(true)` interprets heartbeat age from local ticks. `validPacket()` indexes `data[0]` before checking an empty packet, so callers must keep the current `bytes_recvd > 0` guard. Address auto-detection fails if zero or multiple local interfaces match configured peers.

## Test Signals
Useful tests simulate UDP packets with stale/newer terms, vote denial on lower data versions, loyalty agreement behavior, leader demotion on lost quorum, single-node promotion, id auto-detection failures, blocked promotion, and restart behavior. Integration signals come from HA cluster tests that promote/demote metadata servers and from status output showing term, leader, vote, and heartbeat transitions.
