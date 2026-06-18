<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.cc -->
# sources/distributed-fs/coda/coda-src/resolution/rescomm.cc

Purpose: manages resolution RPC communication state: server entries, replicated resolution groups, connection metadata, and background probing for down servers.

Important APIs/control flow: `ResCommInit` initializes global tables. `srvent` represents a server, resolves names, binds with RPC2 to `RESOLUTIONSUBSYSID`, maps RPC2 errors in `ServerError`, and resets dependent groups/connection info when down. `res_mgrpent` represents a VSG resolution group, maintains canonical host membership, creates/kills member connections, reports incomplete VSGs, and checks multicast results. `GetResMgroup`/`PutResMgroup` lease reusable groups. `conninfo` captures peer host/port/security for inbound RPC handles. `ResCheckServerLWP` periodically signals `ResCheckServerLWP_worker`, which probes down servers.

State/persistence: all state is transient process memory: global server list, resolution-group list, connection-info list, in-use/dying flags, handles, return codes, and server up/down state.

Dependencies/integration: depends on RPC2, LWP condition emulation, service lookup for `codasrv/udp`, `rescomm.private.h`, and public `resolution.h` worker declarations.

Risks/test signals: synchronization is cooperative LWP waiting on raw addresses, not modern locks. `GetHostSet` ignores individual `CreateMember` failures except via final `HowMany`. Error mapping drives retry and membership pruning. Test concurrent binds, server timeout/NAK reset, incomplete VSG detection, group reuse after failures, and connection-info cleanup on reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/rescomm.cc -->
