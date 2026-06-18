# sources/distributed-fs/ceph/src/mds/MDSRank.h

## Purpose
Declares the MDS rank interface and dispatcher-facing service. It exposes rank state, subsystem ownership, message-sending helpers, wait queues, recovery state-machine hooks, admin commands, performance counters, and config observation.

## Important APIs, Types, And Functions
`MDSRank` owns server, cache, locker, log, balancer, scrub stack, damage table, inode/snap/session services, purge queue, metrics, quiesce manager/agent, objecter, messenger, monitor/manager clients, and finisher. Public APIs cover state predicates, table access, sessions, queue/waiter management, MDS/client message sends, OSD barriers, status, export targets, eviction/configuration, and inode/path helpers. `MDSRankDispatcher` adds init/tick/shutdown, map handling, admin socket dispatch, config observer methods, and `ms_dispatch`.

## Control Flow
Daemon code enters through dispatcher methods; subsystems use public `MDSRank` services. MDS map changes call protected transition methods. `ProgressThread` drains finished contexts and lag-deferred messages. Admin commands route through helper methods, sometimes synchronously under `mds_lock`, sometimes via finisher.

## State And Persistence Behavior
The header declares volatile state: current/last state, incarnation, degraded flag, wait queues, replay queue, OSD epoch barrier, peer map epochs, export decay counters, internal request map, heartbeat handle, stop flag, and active atomic. Persistence is delegated to owned subsystems.

## Dependencies And Integration Points
Includes or forward-declares most MDS subsystems plus admin socket, log client, tracked ops, perf counters, timers, Objecter, Messenger, MonClient, MgrClient, and Boost.Asio.

## Risks
Many raw subsystem pointers are public, so lifetime and lock discipline are important. Comments distinguish methods requiring or forbidding `mds_lock`. Public surface area makes refactors broad. State predicates assume synchronized monitor map updates.

## Test Signals
Dispatcher lifecycle, state predicates across all states, waiter queue behavior, admin routing, config propagation, message dispatch, active atomic visibility, and shutdown with outstanding contexts.
