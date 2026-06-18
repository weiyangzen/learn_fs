<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Clients.hh -->
# sources/distributed-fs/eos/mgm/FuseServer/Clients.hh

Purpose: Declares `FuseServer::Clients`, the thread-safe registry of connected eosxd clients and the outbound control-message API used by MGM FUSE services.

Important APIs/types/functions: `Clients` inherits `eos::common::RWMutex` and embeds a nested `Client` class containing `heartbeat`, `statistics`, operation timestamp, and atomic status (`PENDING`, `EVICTED`, `OFFLINE`, `VOLATILE`, `ONLINE`). Main APIs include heartbeat `Dispatch()`, `MonitorHeartBeat()`, `ClientStats()`, diagnostics `Print()/Info()`, statistics ingestion, eviction, FUSE cache-message senders, interval setters, broadcast audience settings, and `client2app()`.

Control flow: Callers take read/write locks through the object itself. Inline helpers such as `nclients()` and `client2app()` lock internally. Message APIs are implemented in `Clients.cc` and generally look up UUID-to-identity, serialize a protobuf response, and send it over the ZeroMQ task channel.

State and persistence behavior: `mMap` stores live client identities and their heartbeat/statistics snapshots; `mUUIDView` maps stable client UUIDs to current ZeroMQ identities. Timing windows govern state transitions and eviction. No persistent registry exists; clients repopulate the map via heartbeats after reconnect/restart.

Dependencies and integration points: Includes `Caps.hh`, `mgm/fusex.pb.h`, timing and logging. It is accessed globally through `gOFS->zMQ->gFuseServer.Client()` by capability broadcasting, lock reporting, flush expiry, FUSE server request handlers, and admin commands.

Risks: The header exposes mutable `map()` and `uuidview()` references, so callers can mutate state outside documented lock discipline. The constructor initializes heartbeat/quota windows but not all private scalar fields. `Client` has an unused `mLockPidMap` member while real locking is handled by `FuseServer::Lock`. Tests should verify lock discipline around public helpers, client status transitions, UUID remapping, and default configuration values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Clients.hh -->
