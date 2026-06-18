<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Clients.cc -->
# sources/distributed-fs/eos/mgm/FuseServer/Clients.cc

Purpose: Implements eosxd client tracking, heartbeat processing, client eviction, runtime statistics reporting, and ZeroMQ response messages sent from MGM back to FUSE clients.

Important APIs/types/functions: `ClientStats()` summarizes active/locked clients. `MonitorHeartBeat()` is the background lifecycle loop. `Dispatch()` stores heartbeats, processes client log/trace payloads, registers UUID mappings, handles first-mount configuration, and revokes requested auth caps. `Print()` and `Info()` render operator diagnostics. Message methods include `Evict()`, `DeleteEntry()`, `RefreshEntry()`, `SendMD()`, `SendCAP()`, `BroadcastConfig()`, and `BroadcastDropAllCaps()`. `HandleStatistics()` updates per-client performance counters, and `DeferClient()` implements dotted-version comparison.

Control flow: Heartbeats are accepted under a write lock unless they are older than the offline window. First-seen clients get a drop-all-caps response and a config response advertising heartbeat rate and feature flags. The monitor loop runs once per second, classifies clients as online, volatile, offline, or evicted based on heartbeat age/shutdown/protocol version, drops locks on offline transition, drops caps and removes map entries on eviction, expires flush records, and records MGM stats. Message-sending functions serialize `eos::fusex::response` protobufs and reply through `gOFS->zMQ->mTask`.

State and persistence behavior: State is volatile in `mMap` (`identity -> Client`) and `mUUIDView` (`uuid -> identity`). Heartbeat windows, heartbeat interval, quota interval, broadcast audience limit, and suppress regex are in-memory settings. Client logs/traces are forwarded to `mFusexLogTraces` and `mFusexStackTraces`; statistics are retained only in the client object.

Dependencies and integration points: Depends on `gOFS`, MGM stats, ZeroMQ task replies, `Locks`, `Caps`, and `Flush`. `Caps.cc` calls the message methods to fan out cache invalidations; admin fusex/evict commands call print/evict paths; `Server.cc` heartbeat handling calls `Dispatch()` and statistics handling.

Risks: `mMaxBroadCastAudience`, suppress-match string, and `terminate_` are not visibly initialized in the constructor. `Print()` uses a five-second `blockedms` threshold while the comment says five minutes. `SetHeartbeatInterval()` holds the write lock while calling `BroadcastConfig()`, which performs network replies. Version comparison collapses dotted components into base-1000 numbers and returns false if component counts differ. Tests should cover delayed heartbeat rejection, first mount setup, auth revocation, shutdown/offline/eviction transitions, protocol mismatch eviction, refresh suppression for protocol/version, and static/autofs eviction filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Clients.cc -->
