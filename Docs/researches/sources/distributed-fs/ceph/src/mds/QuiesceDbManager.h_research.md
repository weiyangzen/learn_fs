# sources/distributed-fs/ceph/src/mds/QuiesceDbManager.h

Purpose: declares `QuiesceDbManager`, the threaded coordinator for quiesce DB leadership, replication, client request submission, peer acknowledgments, peer listings, and agent callback notification.

Important APIs and types: `QuiesceClusterMembership` describes epoch, filesystem identity, local/leader peer ids, members, and courier callbacks. `RequestContext` carries a `QuiesceDbRequest` and `QuiesceDbListing` response. Public APIs include `update_membership()`, `submit_request()`, `submit_peer_ack()`, `submit_peer_listing()`, `submit_agent_ack()`, and `reset_agent_callback()` overloads. Protected structures model the thread-owned DB, peer info, await contexts, and request completion map.

State and persistence: all manager state is in-memory and protected by `submit_mutex`/`agent_mutex`. The authoritative DB is reset on membership loss and versioned by epoch/set version. Peer state records last known root diff maps and last sent versions; awaits are local and complete when DB state changes or timeouts fire.

Dependencies and integration: depends on `QuiesceDb.h`, Ceph `Context`, `Thread`, filesystem id types, STL queues/deques/maps, and callback-based message transport. Only the leader accepts client requests and peer acks; replicas accept peer listings and forward agent acks to the leader.

Risks and test signals: public methods return `-ENOTTY`, `-EPERM`, or `-ESTALE` for role/epoch mismatches, so callers must not treat all failures as retryable. `shutdown()` first clears membership then joins the thread. Tests should verify role gating, epoch checks, local-vs-remote agent ack paths, callback reset version filtering, and clean thread exit.
