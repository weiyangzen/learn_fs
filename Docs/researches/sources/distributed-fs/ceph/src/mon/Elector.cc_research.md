<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Elector.cc -->
# sources/distributed-fs/ceph/src/mon/Elector.cc

## Purpose
`Elector.cc` connects `ElectionLogic` to real monitor runtime. It persists election/connectivity state, sends and receives election messages, validates peer features/releases, manages election expiry timers, handles connectivity pings, assimilates connection reports, updates ping state across monmap rank changes, and calls monitor win/lose/bootstrap hooks.

## Important APIs, types, and functions
Constructor `Elector::Elector()` initializes `ElectionLogic`, `ConnectionTracker`, timeouts, and loads persisted connectivity scores. `ElectionOwner` methods implemented here include `persist_epoch()`, `read_persisted_epoch()`, `validate_store()`, `notify_bump_epoch()`, `trigger_new_election()`, `propose_to_peers()`, `_start()`, `_defer_to()`, `message_victory()`, and membership/rank helpers. Connectivity persistence uses `persist_connectivity_scores()`.

Message handlers are `dispatch()`, `handle_propose()`, `handle_ack()`, `handle_victory()`, `nak_old_peer()`, `handle_nak()`, and `handle_ping()`. Timer and ping machinery lives in `reset_timer()`, `cancel_timer()`, `begin_peer_ping()`, `send_peer_ping()`, `ping_check()`, `begin_dead_ping()`, `dead_ping()`, and `process_pending_pings()`. Monmap updates use `notify_clear_peer_state()`, `notify_rank_changed()`, `notify_rank_removed()`, and `notify_strategy_maybe_changed()`.

## Control flow
Election start clears peer info, records local features/release/metadata, and arms a timeout. Proposals are broadcast to all other monitors with encoded connection scores, local monmap, strategy, and supported features. Deferral sends an `OP_ACK` to the chosen leader and extends the timer. Victory computes intersection of cluster and monitor features across acked peers, selects minimum monitor release, sends `OP_VICTORY` plus leader command payload to quorum members, and calls `Monitor::win_election()`.

`dispatch()` validates message type, participation, sender rank, fsid, sender monmap membership, monmap epoch freshness, strategy consistency, and optional scoring data. If a peer has a newer monmap, the elector persists it locally, cancels election, notifies the monitor, and bootstraps. Propose messages are handled before old-epoch dropping so old out-of-quorum proposals can trigger elections. Ack/victory/nak messages with old epochs are dropped.

Ping flow starts only when quorum features support monitor pinging. Live pinging sends `MMonPing`, schedules periodic checks, marks missed acknowledgements dead, and degrades scores. Dead pinging continues degrading until a ping reply or later begin-peer-ping moves the peer back live. Ping messages always carry tracker data, so monitors exchange connectivity state opportunistically.

## State and persistence behavior
`persist_epoch()` writes `election_epoch` and `connectivity_scores` to `MonitorDBStore`; score-only persistence writes just `connectivity_scores`. Runtime state includes the expire timer, peer feature metadata for victory, pending pings before quorum features are known, sent/acked ping timestamps, live/dead ping sets, timeout settings, disallowed leader set, and the owned connection tracker.

## Dependencies and integration points
This file depends on `Monitor`, `MonitorDBStore`, `Timer`, `Messenger`, `MonMap`, `MMonElection`, `MMonPing`, Ceph feature sets, and `ElectionLogic`/`ConnectionTracker`. It calls monitor methods for election lifecycle (`join_election`, `start_election`, `bootstrap`, `win_election`, `lose_election`, `notify_new_monmap`) and command sharing.

## Risks and edge cases
Feature/release mismatches can trigger NAK and process exit for an outdated monitor. Monmap replacement during election must be durable before bootstrap. Pinging is gated by quorum features; pending pings must be drained after quorum forms. Rank removal rewrites ping sets manually and can leave scheduled callbacks racing with changed ranks. `handle_ping()` maps source address to rank and drops unknown removed monitors. Connectivity data from messages must match strategy expectations, especially in mixed or transitioning clusters.

## Test signals
Tests should cover proposal/ack/victory message handling, feature and release NAKs, newer/older monmap paths, timer expiry callbacks, win/lose monitor calls, leader command sharing, ping live/dead transitions, pending pings before quorum feature establishment, rank change/removal cleanup, persisted epoch/connectivity store keys, strategy mismatch dropping, and unknown ping source drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/Elector.cc -->
