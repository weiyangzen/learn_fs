# sources/distributed-fs/juicefs/pkg/meta/tkv_bak.go

## Purpose
`tkv_bak.go` implements the newer KV-native metadata backup and restore path using protobuf batch segments. It complements the JSON `DumpMeta`/`LoadMeta` path in `tkv.go` with source-key scans and batched inserts.

## Important APIs, Types, and Functions
Primary entry points are `kvMeta.dump`, `prepareLoad`, and `LoadMetaV2`. Dump helpers include `dumpCounters`, `dumpMix`, `dumpSustained`, `dumpDelFiles`, `dumpSliceRef`, `dumpACL`, `dumpQuota`, `dumpDirStat`, and `dumpChangeLog`. Load helpers include `insertKVs`, `loadFormat`, `loadCounters`, `loadNodes`, `loadChunks`, `loadEdges`, `loadSymlinks`, `loadSustained`, `loadDelFiles`, `loadSliceRefs`, `loadAcl`, `loadXattrs`, `loadQuota`, `loadDirStats`, and `loadParents`.

## Control Flow and State
`dump` runs a fixed sequence of segment dumpers. For TiKV it requires a `startTS` from the backend config to ensure consistency and stores it in the context for snapshot reads. `dumpMix` parallelizes the `A...` inode keyspace by first byte ranges, decodes node/edge/chunk/symlink/xattr/parent records into pooled protobuf objects, and emits batches of up to `kvDumpBatchSize`. Other dumpers scan their specialized prefixes. `LoadMetaV2` checks that the target database is empty, reads `BakFormat` segments, converts each segment to KV pairs, and flushes sorted batches bounded by transaction count and byte size.

## State and Persistence Behavior
The backup format preserves counters, metadata graph records, sustained/deleted files, slice refs, ACLs, quotas, dir stats, and a tail of changelog entries. Slice refs are stored as exported refs and reloaded as internal `refs - 1` counters. ACL max id is recomputed from loaded ACL ids. Etcd uses a much smaller transaction batch limit than other backends.

## Dependencies and Integration Points
This file depends on `pkg/meta/pb`, protobuf, `BakFormat`, `dumpResult`, segment type constants, key encoders from `tkv.go`, and backend snapshot support through `tkvClient.config("startTS")`. It integrates with JuiceFS backup/load commands that prefer the V2 segment format.

## Risks and Test Signals
Risks include inconsistent dumps if a backend lacks a stable snapshot, goroutine/channel cancellation leaks, pool object reuse after emission, missing segment types during load, batch sizes exceeding backend transaction limits, and incorrect endian/key decoding. Tests should cover V2 dump/load round trips across backends, TiKV snapshot enforcement, ACL counter restoration, quota variants, changelog tails, and malformed keys/segments.
