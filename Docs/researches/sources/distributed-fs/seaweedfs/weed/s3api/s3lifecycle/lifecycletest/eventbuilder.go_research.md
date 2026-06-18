# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder.go

Purpose: supplies reusable test builders for `reader.Event` fixtures that look like production filer meta-log events.

Important APIs: `EventOption`, `WithSize`, `WithModTime`, `WithTtlSec`, `WithVersionID`, `WithExtended`, `WithChunks`, `WithOldSize`, `WithOldChunks`, `WithOldModTime`, `WithBootstrapVersion`, `WithShardID`, `NewCreate`, `NewDelete`, `NewUpdate`, `MetaLogClock`, and `leafOf`.

Control flow: constructors populate only new, old, or both entries depending on create/delete/update shape, derive shard id from bucket/key, set default mtime to event timestamp, and then apply options in order. Generic options target `NewEntry` when present or `OldEntry` for deletes; `WithOld*` options target old entry on updates. `leafOf` strips trailing slashes and parent prefixes to mimic filer entry names.

State/persistence: test-only. `MetaLogClock` holds mutex-protected current time and step to produce monotonic fixture timestamps.

Dependencies/integration: uses filer protobufs, S3 extended metadata constants, lifecycle shard hashing, and reader bootstrap version structures. These helpers are used by lifecycle router/dispatcher/daily-run tests.

Risks: if fixture shape diverges from real filer events, tests may become misleading. Options silently no-op on missing target entries by design.

Test signals: eventbuilder tests cover constructor shapes, leaf names, shard derivation, option targeting and override order, old-entry branches, bootstrap version attachment, panic safety, and concurrent clock uniqueness.
