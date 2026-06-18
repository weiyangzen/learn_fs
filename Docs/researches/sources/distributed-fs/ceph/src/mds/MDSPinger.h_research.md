# sources/distributed-fs/ceph/src/mds/MDSPinger.h

## Purpose
Declares `MDSPinger`, the helper that tracks outstanding ping sequences to MDS ranks and detects lagging peers.

## Important APIs, Types, And Functions
Public methods are `send_ping`, `pong_received`, `reset_ping`, and `is_rank_lagging`. Internal `PingState` stores `last_seq`, `seq_time_map`, and `last_acked_time`, using Ceph coarse monotonic time. `MDS_PINGER_ISN` starts sequences at 1.

## Control Flow
State is initialized lazily on send, pongs are valid only for outstanding sequences, and lag checks compare time since last ack. A mutex protects the rank-state map.

## State And Persistence Behavior
All state is in-memory and per `MDSPinger` instance. It is lost on restart/failover and cleared per rank by `reset_ping`.

## Dependencies And Integration Points
Depends on rank ids, Ceph mutex/time utilities, `version_t`, address vectors, and a forward-declared `MDSRank`. The implementation integrates with `MMDSPing`.

## Risks
The header warns to drop the lock before `send_message_mds`; lock ordering must be enforced by implementations. Callers supply raw address vectors and must keep them current.

## Test Signals
Lazy creation, sequence validity, reset, lag decisions, and lock-order review around message sending.
