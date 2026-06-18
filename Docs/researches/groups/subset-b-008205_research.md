# subset-b-008205 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication.go -->
# sources/object-store/minio/cmd/site-replication.go

## Purpose

`site-replication.go` implements MinIO's cluster-level site replication coordinator. It links multiple MinIO deployments into one replication set, persists the membership and service-account state, fans out bucket and IAM mutations to peer sites, reports cross-site replication health, periodically heals divergent metadata, and controls site-wide resync operations. The file sits behind admin APIs and internal peer APIs; local S3/admin operations apply locally first, then hooks replicate the resulting metadata changes to peer clusters.

## Important APIs, types, and functions

- `SiteReplicationSys` is the central manager. It protects `enabled`, persisted `srState`, and the IAM metadata cache with locks.
- `srStateV1` / `srStateData` are the JSON persistence contract for `.minio.sys/config/site-replication/state.json`: local site name, peer map keyed by deployment ID, the site-replicator service account access key, and `UpdatedAt`.
- `SRError` wraps site replication failures with an `APIErrorCode`; helper constructors classify invalid requests, peer failures, backend issues, service-account failures, bucket/IAM metadata failures, and missing config.
- `AddPeerClusters`, `PeerJoinReq`, `RemovePeerCluster`, `InternalRemoveReq`, `EditPeerCluster`, `PeerEditReq`, and `PeerStateEditReq` implement membership lifecycle.
- `MakeBucketHook`, `DeleteBucketHook`, `IAMChangeHook`, and `BucketMetaHook` are local mutation hooks that propagate bucket, IAM, and metadata changes to peers.
- Peer handlers such as `PeerBucketMakeWithVersioningHandler`, `PeerBucketConfigureReplHandler`, `PeerIAMUserChangeHandler`, `PeerSvcAccChangeHandler`, `PeerPolicyMappingHandler`, and the bucket metadata handlers apply inbound replicated changes locally.
- `SiteReplicationStatus`, `siteReplicationStatus`, and `SiteReplicationMetaInfo` collect per-site metadata and compare buckets, policies, users, groups, ILM expiry rules, peer state, and metrics.
- The healing loop is rooted at `startHealRoutine`, which calls `healIAMSystem` and `healBuckets`; specific healers repair bucket existence, versioning, object lock, SSE, replication config, policies, tags, quotas, ILM expiry, users, groups, and policy mappings.
- `startResync`, `cancelResync`, `newSiteResyncStatus`, `loadSiteResyncMetadata`, and `saveSiteResyncMetadata` manage explicit site resync to a peer deployment.
- Helpers `getAdminClient`, `getS3Client`, `getPeerCreds`, `concDo`, `toErrorFromErrMap`, `getMissingSiteNames`, `mergeWithCurrentLCConfig`, and `siteReplicatorCred` support peer I/O, fan-out, status text, lifecycle merging, and cached secret-key lookup.

## Control flow

Initialization starts a leader-locked healing goroutine, then retries `loadFromDisk` until the persisted state is loaded or confirmed absent. Adding peers first probes each supplied endpoint via admin and S3 clients, validates unique deployment IDs, ensures the local deployment is present, requires existing sites to be included when extending an existing set, rejects conflicting bucket ownership, and checks that IDP settings match. It creates or reuses the `site-replicator-0` service account, sends `SRPeerJoin` to peers, persists the common peer map locally, caches the service account secret, and performs an initial bucket/IAM sync.

Replication hooks are invoked after local state has already changed. Bucket creation creates the bucket and versioning on every site, then configures remote targets and site-replication rules. Bucket deletion sends delete operations to peers. IAM and bucket metadata hooks call madmin peer APIs concurrently. `concDo` runs a local action for the current deployment and peer actions for every other deployment, builds an ordered error summary, and marks remote targets offline when network/host-down errors are detected.

Peer handlers are idempotent where possible. Bucket make tolerates already-existing buckets, forces versioning, optionally object lock, saves bucket metadata, and reloads metadata. IAM and bucket metadata handlers skip stale inbound updates by comparing the incoming `updatedAt` with local update timestamps. Policy, tagging, SSE, quota, and lifecycle handlers treat nil payloads as deletes where the API supports deletion. STS credentials are accepted only if the session token validates with the local token-signing key.

Status collection first gathers `madmin.SRInfo` from the local site and every peer. It builds cross-site union sets for buckets, users, groups, policies, policy mappings, and ILM expiry rules, then computes mismatch booleans and per-site totals. Public `SiteReplicationStatus` filters detailed maps so normal output emphasizes mismatches unless a specific entity type is requested. Meta collection can return only a requested entity and caches full IAM meta responses for one healing interval.

The heal routine runs every `siteHealTimeInterval` on the leader. It heals IAM before buckets, waits for low I/O between iterations, and logs slow refreshes. Healing is intentionally latest-wins: individual healers find the site with the most recent relevant timestamp, only act when the local site owns the latest value for IAM user/group/policy data, and push local latest metadata to peers. Bucket healing is special: only the local site that has the latest bucket create/delete timestamp coordinates make/delete/purge operations across sites.

Resync starts by validating that site replication is enabled, the peer exists, and the peer is not self. It creates a `SiteResyncStatus`, marks every bucket target for the peer with a reset ID and reset-before date, persists bucket target metadata, and starts the replication resyncer per bucket. Cancel clears matching reset IDs, updates bucket resync state, persists site metadata as canceled, and signals the resyncer.

## State and persistence behavior

Site membership persists as JSON under `getSRStateFilePath()` with an explicit format version. `saveToDisk` writes config, reloads site replication config across nodes through `globalNotificationSys`, then updates in-memory state. `removeFromDisk` deletes that config and clears the in-memory state. Because `saveToDisk` obtains the object layer dynamically, callers can fail with server-not-initialized if storage is not ready.

Bucket replication state is stored in bucket metadata: replication XML, target JSON, bucket policy JSON, tagging XML, versioning XML, object-lock XML, SSE XML, quota JSON, and lifecycle XML. Initial sync and healers update this metadata through `globalBucketMetadataSys` and `globalBucketTargetSys`, then rely on metadata reload/notification paths elsewhere in MinIO. Deleted bucket state uses `.minio.sys/buckets/.deleted/<bucket>` markers; `SRBucketDeleteOp` selects mark-delete, purge, or no-op behavior.

IAM state is stored in `globalIAMSys.store`, and replicated changes are applied through IAM system APIs. The site-replicator credential is both stored as a service account and cached in `globalSiteReplicatorCred`; `siteReplicatorCred.Get` lazily loads the secret key from the IAM store.

Resync state has two persistence layers: site-level msgp metadata under `siteResyncPrefix/<deployment-id>.meta` with a binary format/version header, and per-bucket replication target reset fields plus bucket resync status maintained by the replication pool. The code validates both file format and msgp version on load.

## Dependencies and integration points

This file is tightly integrated with MinIO globals: `globalIAMSys`, `globalBucketMetadataSys`, `globalBucketTargetSys`, `globalNotificationSys`, `globalReplicationPool`, `globalSiteResyncMetrics`, `globalLeaderLock`, `globalDeploymentID`, `globalRemoteTargetTransport`, `newObjectLayerFn`, DNS config, object-layer bucket APIs, and logger helpers. External APIs include `madmin-go/v3` for admin peer requests and DTOs, `minio-go/v7` for bucket listing during peer validation, MinIO internal lifecycle and replication packages for XML parsing/validation, LDAP helpers for DN validation, policy parsing/comparison, and `xsync` maps for IAM policy mapping loads.

Admin API integration is bidirectional: public admin calls invoke local `SiteReplicationSys` methods, and peer methods call madmin APIs such as `SRPeerJoin`, `SRPeerBucketOps`, `SRPeerReplicateIAMItem`, `SRPeerReplicateBucketMeta`, `SRPeerRemove`, `SRPeerEdit`, `SRStateEdit`, and `SRMetaInfo`. S3 replication integration occurs through generated bucket targets and replication rules with IDs prefixed `site-repl-<deployment-id>`.

## Risks and edge cases

- Add/join and edit/remove operations are multi-site and only partially transactional. Several paths return partial status after some peers were changed, and comments note manual cleanup may be needed after partial add failure.
- `AddPeerClusters` checks only some preconditions; a FIXME notes missing validation for global IAM policies and LDAP-created service accounts on peer clusters.
- Many healers choose the latest timestamp as authoritative. Clock skew or missing update timestamps can cause the wrong site to win.
- Several metadata healers ignore or log peer update failures and continue, so convergence may require repeated heal cycles.
- `concDo` requires callers to hold at least a read lock for stable `c.state`; misuse could race with state mutation.
- Status comparison helpers often skip parse failures and can under-report mismatches if malformed policy/lifecycle/replication data is ignored.
- The replication config status helper checks rule shape but does not deeply compare all destination semantics beyond rule count, prefix, and enabled features.
- `updateTargetEndpoints` ignores some per-bucket target list errors because healing should repair them later, which can leave edited endpoints partially applied until the heal loop succeeds.
- `mergeWithCurrentLCConfig` intentionally preserves transition actions while syncing expiry actions; this is subtle and can surprise callers expecting full lifecycle replication.
- Resync start can partially configure buckets; if every bucket fails it returns an error, otherwise failures are embedded in the operation status.

## Test signals

The paired test file in this subset only covers `getMissingSiteNames`, asserting that existing replicated sites missing from a new add request are reported by site name and that unrelated new deployments or no current sites do not produce names. There is no direct unit coverage here for add/join/remove transactions, replication hook fan-out, stale update handling, status mismatch computation, healing, lifecycle merge, or resync persistence. Most behavior likely depends on integration tests elsewhere because this file relies heavily on MinIO global systems and peer admin clients.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication_test.go -->
# sources/object-store/minio/cmd/site-replication_test.go

## Purpose

`site-replication_test.go` provides a focused unit test for one helper in the site replication subsystem: `getMissingSiteNames`. That helper is used by `AddPeerClusters` to produce a user-facing list of already-replicated sites omitted when extending an existing site replication setup.

## Important APIs, types, and functions

- `TestGetMissingSiteNames` is the only test function.
- The table uses `madmin.PeerInfo` values to model current replicated sites and `set.StringSet` values to model old and new deployment ID sets.
- The function under test, `getMissingSiteNames(oldDeps, newDeps, currSites)`, computes `oldDeps.Difference(newDeps)` and maps missing deployment IDs back to peer names from `currSites`.

## Control flow

The test defines three cases: an existing three-site setup where a new request includes only one deployment and should report the two omitted site names; a request that adds an unrelated new deployment while preserving all existing deployments and should report no missing names; and a non-replicated current setup with no current sites and should also report no names. Each case calls `getMissingSiteNames` and compares only the returned length with the expected length.

## State and persistence behavior

The test is pure and has no persistence, network, or global MinIO state. It constructs all peer and set data in memory. It does not verify ordering, string content, or mutation of input sets.

## Dependencies and integration points

The test imports Go's `testing` package, `madmin-go/v3` for `PeerInfo`, and `minio-go/v7/pkg/set` for deployment ID sets. Its production integration point is the validation branch in `SiteReplicationSys.AddPeerClusters` that rejects add requests missing currently replicated sites.

## Risks and edge cases

- The assertion checks only length, so a regression returning the wrong site names in the right count would pass.
- It does not check stable ordering of returned names, though the production helper follows `currSites` order.
- It does not test unknown deployment IDs in `oldDeps`, duplicate `currSites` names, nil sets, or nil current-site slices.
- It does not cover the wrapping error message in `AddPeerClusters`, so formatting regressions can slip through.

## Test signals

The test signals that `getMissingSiteNames` is expected to report only deployments that were in the old replicated set but absent from the new requested set, and to ignore new deployments that were not part of the prior replicated configuration. Coverage is narrow and helper-level only.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/site-replication_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/speedtest.go -->
# sources/object-store/minio/cmd/speedtest.go

## Purpose

`speedtest.go` implements MinIO admin speed tests for object I/O and local drive I/O. Object speed tests coordinate PUT/GET measurements across the cluster and optionally auto-tune concurrency. Drive speed tests run local disk throughput probes on formatted drives and return admin-facing performance summaries.

## Important APIs, types, and functions

- `speedTest` is the operation label constant.
- `speedTestOpts` carries object size, starting and current concurrency, duration, auto-tune flag, storage class, bucket name, checksum/multipart toggles, and credentials.
- `objectSpeedTest(ctx, opts)` returns a channel of `madmin.SpeedTestResult` and runs asynchronously.
- `driveSpeedTest(ctx, opts)` returns one `madmin.DriveSpeedTestResult` for the local node using `dperf.DrivePerf`.

## Control flow

`objectSpeedTest` starts a goroutine and closes its result channel safely. It initializes concurrency from `opts.concurrencyStart`; when auto-tune is enabled it caps the starting point by endpoint count, local disks per pool, a minimum of four operations, and `GOMAXPROCS`. The goroutine repeatedly asks `globalNotificationSys.SpeedTest` for per-node results at the current concurrency, sorts server results by endpoint, totals uploads and downloads, and tracks the highest GET throughput observed along with the corresponding PUT throughput.

Each iteration sends an aggregate result through `sendResult`. The aggregate computes per-second GET and PUT throughput and object rates from the best total byte counts and configured duration/object size, copies per-server upload/download stats, merges upload/download/TTFB timing samples, and annotates missing first-attempt downloads or uploads as errors. The loop stops when context is canceled, throughput drops, growth is below 2.5 percent, any server returns an error, or auto-tune is disabled. Auto-tune raises concurrency by roughly 50 percent per iteration.

`driveSpeedTest` builds a `dperf.DrivePerf` from serial/block/file sizes, filters `globalEndpoints.LocalDisksPaths()` to only paths containing the MinIO format config, and runs `perf.Run` against each formatted path's `.minio.sys/tmp` path. It returns a local endpoint URL using TLS state and node name, maps each `dperf` result to `madmin.DrivePerf`, appends ignored unformatted paths with `errFaultyDisk`, and surfaces the overall run error as a string.

## State and persistence behavior

Object speed testing does not persist data in this file; actual temporary objects and cleanup are delegated to the notification-system speed test implementation. It reads global endpoint topology, peer count, server version, and runtime settings. Results are streamed over a channel and stop respecting `ctx.Done()`.

Drive testing writes temporary performance data through `dperf` under formatted drives' MinIO tmp areas, but this file itself only selects paths and reports measurements. It reads disk format presence with `Lstat(pathJoin(localPath, minioMetaBucket, formatConfigFile))` and treats missing format config as a faulty/ignored disk in the result.

## Dependencies and integration points

The file depends on `globalNotificationSys.SpeedTest`, `globalEndpoints`, `globalNotificationSys.peerClients`, `Version`, `globalIsTLS`, `globalLocalNodeName`, MinIO path helpers, `Lstat`, and `errFaultyDisk`. External packages are `madmin-go/v3` result DTOs, `github.com/minio/dperf/pkg/dperf` for drive benchmarks, MinIO auth credentials, and `xioutil.SafeClose`.

Object tests integrate with cluster peer notification rather than directly calling S3 APIs here. Drive tests integrate with local storage layout and the admin drive speed test endpoint.

## Risks and edge cases

- Throughput division assumes nonzero duration and object size; invalid options could panic or divide by zero if validation elsewhere fails.
- The auto-tune minimum of four can exceed very small local resources, although it is later capped by `GOMAXPROCS`.
- The "best" result is selected primarily by GET throughput; a special path accepts lower GET if PUT improves, which can make reported best results reflect a hardware anomaly rather than a clean peak.
- If the first attempt yields zero uploads or downloads, the result embeds error strings but still reports the aggregate.
- `driveSpeedTest` indexes `localPaths[idx]` while iterating over `perfs`, but `perfs` corresponds to filtered `paths`; if ignored paths appear before formatted paths, reported paths can be misaligned unless `dperf` preserves a shape matching `localPaths`.
- Both tests depend on global cluster state, so unit testing requires substantial mocking or integration setup.

## Test signals

No tests for this file are included in this subset. Expected coverage should exercise auto-tune stopping conditions, zero-result error strings, context cancellation, server result sorting, invalid duration/object-size validation in callers, and drive path mapping with mixed formatted/unformatted disks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/speedtest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/storage-datatypes.go -->
# sources/object-store/minio/cmd/storage-datatypes.go

## Purpose

`storage-datatypes.go` defines message-pack-serializable data structures and small helpers used by MinIO's storage layer and storage REST/grid APIs. The types describe disk information, volume and file metadata, object version metadata, bulk read/write/delete/rename request parameters, and low-level storage responses. The file also includes `go:generate msgp` annotations, so field shape and ordering are part of the internode compatibility contract.

## Important APIs, types, and functions

- Option structs: `BaseOptions`, `DeleteOptions`, `RenameOptions`, `DiskInfoOptions`, and `UpdateMetadataOpts`.
- Disk and metric structs: `DiskInfo` and `DiskMetrics`.
- Volume/listing structs: `VolsInfo`, `VolInfo`, and `FilesInfo`.
- Object metadata structs: `FileInfoVersions`, `RawFileInfo`, and `FileInfo`.
- `FileInfoVersions.Size` sums all version sizes, and `findVersionIndex` resolves normal and `nullVersionID` versions.
- `FileInfo` helpers include `shardSize`, `ShardFileSize`, `ShallowCopy`, `WriteQuorum`, `ReadQuorum`, `Equals`, `GetDataDir`, `IsCompressed`, `InlineData`, `SetInlineData`, and `newFileInfo`.
- Request/response structs include `ReadMultipleReq`, `ReadMultipleResp`, `DeleteVersionHandlerParams`, `MetadataHandlerParams`, `CheckPartsHandlerParams`, `DeleteFileHandlerParams`, `RenameDataHandlerParams`, `RenameDataInlineHandlerParams`, `RenameFileHandlerParams`, `RenamePartHandlerParams`, `ReadAllHandlerParams`, `WriteAllHandlerParams`, `RenameDataResp`, `CheckPartsResp`, `LocalDiskIDs`, `ListDirResult`, `ReadPartsReq`, `ReadPartsResp`, `DeleteBulkReq`, and `DeleteVersionsErrsResp`.
- `newRenameDataInlineHandlerParams` and `Recycle` manage a reusable inline data buffer for rename operations.

## Control flow

Most of the file is declarative. `FileInfoVersions.Size` iterates version entries and sums `Size`. `findVersionIndex` returns `-1` for nil receivers, empty IDs, missing versions, or missing null versions; `nullVersionID` matches entries whose `VersionID` is empty. `ShardFileSize` handles special zero and unknown-length values, then computes erasure shard size for full blocks plus the final partial block. `WriteQuorum` and `ReadQuorum` return delete quorum for delete markers, otherwise data-block quorum with an extra write quorum when data and parity blocks are equal.

`FileInfo.Equals` compares encryption type, compression state, transition info, modification time, and erasure layout. `GetDataDir` normalizes delete markers and legacy XLv1 objects. Inline data helpers use reserved internal metadata keys and suppress inline status for remote/tiered objects. `newFileInfo` initializes erasure algorithm, data/parity counts, block size, and hash distribution for a new object.

`newRenameDataInlineHandlerParams` obtains a byte buffer from `grid.GetByteBufferCap` and embeds it in `FileInfo.Data` so inline data can travel with rename parameters. `Recycle` returns large enough buffers to the grid pool and clears `FI.Data`.

## State and persistence behavior

These structs are serialized across internode storage APIs and persisted in object metadata such as `xl.meta`. Comments repeatedly warn that adding or deleting fields is incompatible and may require bumping internode storage REST versions. `msg` tags encode compact wire names; `msgp:tuple` annotations make selected structs positional, increasing compatibility risk if fields are reordered.

`FileInfo` carries persistent object-version state: bucket volume, object name, version ID, latest/delete markers, transition status and remote-tier identity, data directory, XLv1 flag, modification time, size, mode, writer version, user/internal metadata, part list, erasure layout, replication state, optional inline data, version counts, successor time, write freshness, delete index, checksum, and versioned flag. `RawFileInfo` can carry the entire `xl.meta` byte content.

Rename/delete/request parameter structs carry disk IDs, volumes, paths, options, and `FileInfo` snapshots across storage handlers. `RenameDataResp` returns a signature and old data directory to support two-phase cleanup of previous object data after metadata rename.

## Dependencies and integration points

The file depends on MinIO internal crypto detection, grid byte-buffer pooling, internal ioutil sizing constants, erasure metadata types, object part metadata, replication state, lifecycle/tiering helpers referenced by `FileInfo` methods defined elsewhere, and global constants such as `ReservedMetadataPrefix`, `ReservedMetadataPrefixLower`, `nullVersionID`, `erasureAlgorithm`, and `blockSizeV2`.

Integration points include storage REST/grid handlers, erasure set object operations, healing and quorum logic, metadata read/write/update/delete paths, multi-object delete, part verification, bulk delete, inline data rename paths, and msgp code generation. Because these structs are shared wire contracts, they are consumed by generated marshal/unmarshal code and by remote peers that may be running compatible but not identical versions.

## Risks and edge cases

- Field additions, deletions, or reordering in tuple-encoded structs can break internode compatibility and persisted metadata parsing.
- `FileInfo.Equals` intentionally compares selected semantic fields, not every field; callers must not use it as a full object metadata equality check.
- `InlineData` depends on metadata keys and remote-tier state; stale inline metadata from older versions is explicitly masked by `!fi.IsRemote()`.
- Buffer pooling in `RenameDataInlineHandlerParams.Recycle` requires callers to recycle once and avoid using `FI.Data` afterward.
- `findVersionIndex` treats empty requested version as invalid but `nullVersionID` as a special lookup for empty stored version IDs.
- Quorum helpers assume erasure fields are valid; malformed `FileInfo` could yield incorrect quorum or shard-size results.
- Request structs expose low-level file paths and disk IDs; validation must happen in handler code outside this file.

## Test signals

No tests for this file are included in this subset. Useful tests would cover `FileInfoVersions.Size`, null-version lookup, shard-size math for full/partial/zero/unknown lengths, quorum behavior for delete markers and equal data/parity layouts, inline data masking for remote objects, `GetDataDir` legacy/delete-marker cases, and buffer recycling behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/storage-datatypes.go -->
