# sources/distributed-fs/ceph/src/mds/MDSPinger.cc

## Purpose
Implements MDS rank ping/pong tracking. It sends `MMDSPing` messages, validates pong sequences, resets peer state, and reports lag based on `mds_ping_grace`.

## Important APIs, Types, And Functions
`send_ping` lazily creates `PingState`, records a sequence send time, increments `last_seq`, and sends the ping. `pong_received` checks rank and sequence, updates `last_acked_time`, and prunes older entries. `reset_ping` removes peer state. `is_rank_lagging` compares current time with last acknowledged ping time.

## Control Flow
All methods lock the pinger mutex before touching `ping_state_by_rank`. Unknown-rank and unknown-sequence pongs are ignored. Missing state in lag checks logs an error and returns false.

## State And Persistence Behavior
State is volatile: per rank `last_seq`, sequence timestamp map, and last acked time. It is neither encoded nor journaled. `pong_received` erases entries before the acknowledged sequence but leaves the acknowledged entry until a later ack prunes it.

## Dependencies And Integration Points
Depends on `MDSRank`, `MMDSPing`, Ceph config, coarse monotonic clock, and MDS logging. It integrates with rank health/liveness and peer address selection.

## Risks
The implementation sends while holding `MDSPinger::lock`, despite the header warning that sending under the lock can deadlock. Retained acknowledged entries can grow if pruning is not triggered by later pongs. Lag age is based on send time of last accepted ping.

## Test Signals
First-send initialization, sequence monotonicity, unknown pong handling, reset, lag threshold with controlled time, pruning behavior, and integration health changes after missing or received pongs.
