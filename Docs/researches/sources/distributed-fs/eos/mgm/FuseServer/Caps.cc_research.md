<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Caps.cc -->
# sources/distributed-fs/eos/mgm/FuseServer/Caps.cc

Purpose: Implements the MGM FUSE capability registry and the broadcast fan-out logic that keeps eosxd clients' metadata/dentry state coherent after namespace mutations.

Important APIs/types/functions: `Store()` records an incoming `eos::fusex::cap` and indexes it by auth id, inode, client id, and client UUID. `Imply()` derives a new cap from an existing auth id for another inode/auth id and assigns a lease time from the owning client heartbeat. `Get()`, `GetBroadcastCapsTS()`, and `Delete()` provide lookup, filtered broadcast audience selection, and inode-wide cap removal. Broadcast methods call `Clients` methods: `BroadcastRefresh*()` sends refreshes, `BroadcastDeletion*()` sends dentry deletion notices, `BroadcastMD()` sends metadata updates, and `BroadcastCap()` sends a cap update.

Control flow: Storage is mutex-protected and updates all secondary indexes together. Broadcasts first snapshot relevant auth ids under lock, release the cap lock, then fetch/send per target to avoid holding the cap mutex during ZeroMQ replies. Suppression logic uses `Clients::BroadCastMaxAudience()` and a configured regex to skip matching client IDs when the audience is too large. `Print()` provides time, inode, or path-oriented diagnostic dumps, resolving paths through EOS namespace services for `option == "p"`.

State and persistence behavior: State is in-memory only: `mCaps`, `mTimeOrderedCap`, `mClientCaps`, `mClientInoCaps`, `mInodeCaps`, and `mClientIds`. Expiry removes stale lease caps based on `vtime`; `dropCaps()` removes all caps for a client UUID after eviction/unmount. No state survives MGM restart, which is why new clients are told to drop all caps on first heartbeat.

Dependencies and integration points: Depends on `gOFS`, `gOFS->zMQ->gFuseServer.Client()`, MGM stats/timing/logging, EOS namespace view services, and `eos::fusex` protobuf messages. `FuseServer/Server.cc` calls broadcasts after create/link/rename/unlink/metadata updates, and `XrdMgmOfs.cc` calls external refresh/MD broadcasts for non-FUSE mutations.

Risks: `Imply()` indexes the implied cap in `mClientInoCaps` under the source cap inode instead of `md_ino`, which may make per-client inode queries/removal inconsistent. `Store()` adds a new time-order entry for replaced caps without removing old time entries, relying on later cleanup. Several diagnostic paths read `mInodeCaps` without taking `mtx` for the whole iteration in non-`t` print modes. Regex compilation/fan-out happens on hot paths. Tests should exercise cap replacement, implied cap removal, audience suppression, self/same-client suppression, client eviction cleanup, and concurrent broadcast/delete races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/FuseServer/Caps.cc -->
