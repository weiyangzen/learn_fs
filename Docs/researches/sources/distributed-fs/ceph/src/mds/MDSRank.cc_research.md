# sources/distributed-fs/ceph/src/mds/MDSRank.cc

## Purpose
Implements the running CephFS MDS rank service: subsystem construction, startup, message dispatch, state transitions, recovery, shutdown, admin socket commands, counters, client eviction, OSD fencing, metrics, scrub, quiesce, and table integration.

## Important APIs, Types, And Functions
Lifecycle functions include `init`, `tick`, `shutdown`, `handle_mds_map`, `handle_osd_map`, boot/replay/resolve/reconnect/rejoin/clientreplay/active/stopping transitions, and `recovery_done`. Dispatch flows through `ms_dispatch`, `_dispatch`, `is_valid_message`, `is_stale_message`, and `handle_message`. Service APIs include table accessors, `send_message_mds`, client send helpers, `forward_message_mds`, `evict_client`, `config_client`, `set_osd_epoch_barrier`, and admin command helpers. `C_Flush_Journal` and `C_Drop_Cache` implement multi-step admin workflows.

## Control Flow
Construction creates Objecter, MDCache, MDLog, balancer, scrub stack, inode/session/snap services, server, locker, purge queue, metrics, and quiesce manager. Messages are dropped if stale, deferred while beacon laggy, then routed by type/port. `handle_mds_map` is the main state-machine driver: it validates transitions, updates messenger identity/incarnation, detects failures/restarts/recovery, starts phase work, wakes waiters, updates snapserver, cache, metrics, and quiesce, and sets OSD epoch barriers when active.

## State And Persistence Behavior
Rank state combines monitor-driven `MDSMap` state, volatile queues, and durable RADOS/journal structures. Durable state is delegated to MDLog, SessionMap, InoTable, PurgeQueue, SnapServer, and subtree maps. Boot paths create/load/replay this state. Shutdown drains cache/purge queue and requests `STATE_STOPPED`. Client eviction can blocklist and set an OSD epoch barrier before session kill.

## Dependencies And Integration Points
This file is the integration hub for Beacon, MDSMap, MDCache, MDLog, Server, Locker, MDBalancer, Migrator, SnapServer/Client, ScrubStack, PurgeQueue, SessionMap, metrics, Objecter, Messenger, MonClient, MgrClient, admin socket parsing, quiesce code, and table messages.

## Risks
Ordering and lock discipline are critical. Invalid transitions, missed failure detection, stale peer messages, or incorrect OSD barriers can cause split-brain, hung recovery, or unsafe cap issuance. Many admin commands are async and may drop `mds_lock`; comments warn not to touch rank state after such drops.

## Test Signals
Boot-create/start/replay, standby-replay takeover, failover/rejoin, laggy deferral, stale message rejection, table routing, client reconnect/reclaim/replay, eviction blocklist/barrier, cache drop/flush journal, quiesce commands, scrub controls, OSD blocklist handling, counters, and invalid transition respawn.
