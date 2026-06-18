<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/resync.go -->
# sources/distributed-fs/beegfs-go/common/beemsg/msg/resync.go

Purpose: BeeMsg request/response definitions for storage and metadata buddy resync status.

Important APIs/types/functions: `GetStorageResyncStats`, `GetStorageResyncStatsResp`, `GetMetaResyncStats`, `GetMetaResyncStatsResp`, `BuddyResyncJobState`, and `BuddyResyncJobState.String`.

Control flow: request serializers write target IDs. Response deserializers read state, timestamps, counters, and error/session/modification metrics in fixed order. `String` maps known enum values to user-facing status strings.

State and persistence: no local state; response structs snapshot remote resync state from BeeGFS nodes.

Dependencies and integration points: depends on `beeserde`; used by management code that sends message IDs 2093/2117 and expects 2094/2118 responses via `NodeStore`/transport utilities.

Risks: counter ordering must match server definitions. `String` returns `<unspecified>` for unknown values rather than surfacing raw code. There are no sanity checks on timestamp or counter consistency.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/beemsg/msg/resync.go -->
