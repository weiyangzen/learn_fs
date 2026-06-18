# Research Report: subset-b-000503

This grouped report covers the requested BeeGFS Go CTL and Remote source files. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/migrate.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/migrate.go

## Purpose
Implements entry migration for BeeGFS paths, supporting two migration mechanisms: background chunk rebalancing through metadata server RPCs and legacy temporary-file replacement. It determines source target or buddy-group placement from current entry metadata, maps user-provided source/destination entities through management mappings, optionally updates directory storage-pool assignment, and emits asynchronous `MigrateResult` values through `util.ProcessPaths`.

## Important APIs, Types, And Functions
Key public surface is `MigrateEntries(ctx, pm, cfg)`, `MigrateCfg`, `MigrateResult`, `MigrateStats`, and `MigrateStatus`. Internal execution is handled by `migrateEntry`, `tmpFileMigrate`, `tmpFileMigrateLink`, `tmpFileMigrationPossible`, `didFileChange`, and `chunkRebalanceMigrate`. The file depends on helper functions/types from the same package that are not defined here, notably `GetEntry`, `getMigrationForEntry`, `newPackedEntryMap`, and `SetEntryCfg`/`setEntry`.

## Control Flow
`MigrateEntries` validates rebalancing licensing when requested, globally sets process umask to zero, builds `util.Mappings`, expands configured source targets from targets, nodes, and pools, optionally maps storage targets to buddy groups, then resolves destination pool/targets/groups. If directory updates are enabled it validates a `SetEntryCfg` for destination pool updates. Each path is processed by `migrateEntry`.

`migrateEntry` rejects its own temp-file prefix, fetches verbose entry details, handles directories by either setting their pool or skipping them, tracks non-inlined hard-linked entries in a bounded recent-entry map, computes the source/destination ID pairs, and branches to rebalancing or temp-file migration. Rebalancing sends `StartChunkBalanceMsg` with exponential backoff and jitter on `OpsErr_AGAIN`. Temp-file migration creates a replacement file or symlink with the target pattern, copies xattrs/content/ownership, checks inode/mtime/ctime/size/link count just before rename, overwrites the original, and restores timestamps.

## State And Persistence
Persistent effects include metadata-server chunk-balance jobs, new stripe placement, temporary files named `.beegfs_tmp_migrate.<basename>`, overwritten files/symlinks, copied xattrs, ownership/mode, timestamps, and directory pattern changes. Process-global state includes `syscall.Umask(0)` with no local restore and random jitter via `math/rand`. In-memory state includes source/destination maps, the bounded `recentHardLinks` cache, and accumulated stats.

## Dependencies And Integration Points
Integrates with BeeGFS management (`VerifyLicense`), management/entity mappings (`util.GetMappings`), node store TCP BeeMsg RPCs (`MakeFileWithPattern`, `StartChunkBalance`), BeeGFS client filesystem provider methods (`Lstat`, copy helpers, `OverwriteFile`), ioctl symlink creation, and path streaming/filtering from `ctl/pkg/util`.

## Risks And Edge Cases
The global umask change affects the whole process and callers must reset it if needed. Temp-file migration refuses `000` permissions and hard links; rebalancing is required for hard-linked entries. The hard-link dedupe cache is bounded, so very large hard-link sets can still submit duplicates. Temp files from failed prior migrations are removed and retried, but paths matching the temp prefix are categorically refused. Symlink migration to specific IDs is unsupported without a destination pool. `didFileChange` compares only nanosecond components for mtime/ctime, not seconds, which may miss changes across second boundaries with equal nsec values. Rebalancing queue-full handling can retry indefinitely if configured with negative retries.

## Test Signals
No tests are present in this file. Behavior is high-risk because it mutates data placement and file contents; useful tests would cover `didFileChange`, temp-file preflight, rebalancing retry exhaustion, destination ID selection, and directory update behavior with mocked mappings/node-store/filesystem providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/migrate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/refresh.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/refresh.go

## Purpose
Refreshes metadata information for one or more BeeGFS entries by sending `RefreshEntryInfoRequest` to the owning metadata node. It is a path-processing wrapper around the metadata refresh RPC.

## Important APIs, Types, And Functions
Exports `RefreshEntryResult` and `RefreshEntriesInfo(ctx, paths)`. Internal helper `refreshEntryInfo` resolves an entry and owner with `GetEntryAndOwnerFromPath`, sends `msg.RefreshEntryInfoRequest`, and returns path, entry ID, and `beegfs.OpsErr` status.

## Control Flow
`RefreshEntriesInfo` gets a `NodeStore`, fetches entity mappings, tolerates `util.ErrMappingRSTs`, and delegates path iteration to `util.ProcessPaths`. For each path, `refreshEntryInfo` resolves entry ownership, sends the refresh request to `ownerNode.Uid`, converts transport errors into setup/processing errors, and returns server result status.

## State And Persistence
The function itself keeps no durable local state. The durable effect is on BeeGFS metadata, where the metadata node refreshes entry information. Results are streamed asynchronously and errors can terminate processing through `ProcessPaths`.

## Dependencies And Integration Points
Depends on `config.NodeStore`, `util.GetMappings`, entry lookup helpers in the same package, BeeMsg `RefreshEntryInfo*` messages, and path streaming/filtering infrastructure.

## Risks And Edge Cases
RST mapping errors are ignored, but other mapping failures abort setup. A non-success server status is returned both as a result and as an error, which may stop `ProcessPaths` after sending valid earlier results depending on pipeline timing. Returned empty `RefreshEntryResult{}` on lookup or transport error loses path context unless the error wraps it elsewhere.

## Test Signals
No direct tests. Mocked node-store tests should cover success, non-success `OpsErr`, owner lookup failure, and tolerance of unavailable RST mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/refresh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/set.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/set.go

## Purpose
Applies entry metadata updates such as directory stripe pattern, chunksize, pool, remote storage target settings, remote cooldown, and file access/data state. It centralizes validation and dispatches to directory, file, or file-state update paths.

## Important APIs, Types, And Functions
Exports `SetEntryCfg`, `SetEntryResult`, and `SetEntries`. Internal helpers include `setEntry`, `handleDirectory`, `handleFile`, and `handleFileStateUpdate`. `setFileStateIoctl` is a `probecache` used to avoid repeatedly trying unsupported client ioctls.

## Control Flow
`SetEntries` validates effective-user permissions once, fetches mappings while tolerating missing RST mappings, and streams paths through `util.ProcessPaths`. `setEntry` loads entry metadata and a node store. File state changes (`AccessFlags`/`DataState`) are routed separately and only allowed for regular files. Directories are updated with `SetDirPatternRequest` after merging requested changes into current pattern/RST config and validating pool/pattern compatibility unless forced. Non-directories can currently update only RST fields using `SetFilePatternRequest`.

`handleFileStateUpdate` computes the desired combined file state, returns success with no updates if unchanged, tries `ioctl.SetFileState` when the cached probe permits it, then falls back to `SetFileStateRequest` RPC and marks the ioctl unavailable after failures.

## State And Persistence
Persistent effects occur on metadata servers: directory pattern/pool/RST fields, file RST fields, and regular-file state. Local state includes `actorEUID` embedded into the config after validation and the global `setFileStateIoctl` availability cache with a five-minute reprobe window.

## Dependencies And Integration Points
Uses entry lookup helpers, `config.NodeStore`, `config.BeeGFSClient`, `util.Mappings`, management-derived pool config, BeeMsg metadata update requests, `common/ioctl`, `common/filesystem`, and `probecache`.

## Risks And Edge Cases
`SetEntryCfg` contains an internal `actorEUID` pointer and is unsafe to call through `setEntry` directly without `setAndValidateEUID`. Non-root local validation blocks root-only updates before server-side policy, while chunksize/pattern permissions are partly delegated to metadata server behavior. Directory pool/pattern compatibility uses mappings that may be stale. Ioctl fallback caches unavailability globally, so a transient mount/config error can force RPC use for up to five minutes. `handleDirectory` accepts `OpsErr_NOTADIR` as a non-error response even though the path was previously classified as a directory, which may reflect race handling.

## Test Signals
No direct tests in this file. Strong tests would mock metadata entry details, pool eligibility, non-root validation, unchanged file-state short-circuit, ioctl success/failure, and RPC fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/entry/set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/license/license.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/license/license.go

## Purpose
Fetches, interprets, and validates BeeGFS license state, including expiry warnings and capacity-limit violations. It provides reusable health-check logic distinct from CLI-specific license printing.

## Important APIs, Types, And Functions
Exports constants for license feature prefixes, `CheckResult`, `Check`, `GetLicense`, `TotalStorageCapacity`, `CheckIfOverStorageCapacityLimit`, and `GetTimeToExpiration`. `CheckResult.IsHealthy` is the main health predicate.

## Control Flow
`Check` calls `GetLicense`, returns an error result on fetch failure, returns invalid message for non-valid verify result, computes warning-window expiry text, then scans DNS names for `io.beegfs.capacity.*` constraints and validates them against total storage target capacity. Temporary licenses use a 14-day warning window; other licenses use 90 days.

## State And Persistence
No local persistence. It reads license data from management and target capacity from management-derived target information. It intentionally ignores malformed capacity limits and target-fetch failures after debug logging, so license health is not blocked by those secondary checks.

## Dependencies And Integration Points
Uses `config.ManagementClient`, protobuf management/license messages, `ctl/pkg/ctl/target.GetTargets`, BeeGFS entity types, `unitconv` for human-readable capacity, `strfmt.ExpirationString`, and zap debug logging.

## Risks And Edge Cases
`Check` only records the last capacity violation encountered because `ViolationsMsg` is overwritten in the DNS-name loop. Capacity totals require `TotalSpaceBytes` for every storage target and error if any is nil, but that error is ignored by capacity-limit checking. `GetTimeToExpiration` subtracts 12 hours from the certificate validity time, so callers must understand this grace-period adjustment. Floating conversion for huge byte values may lose precision in human-readable output.

## Test Signals
No direct tests. Valuable coverage would include valid/invalid license responses, temporary versus permanent expiry windows, unlimited/malformed/numeric capacity limits, nil target capacity, and multiple DNS capacity entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/license/license.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/delete.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/delete.go

## Purpose
Thin management RPC wrapper for deleting a BeeGFS node.

## Important APIs, Types, And Functions
Exports `Delete(ctx, req)` accepting a protobuf `pm.DeleteNodeRequest` and returning `pm.DeleteNodeResponse`.

## Control Flow
The function obtains a management client from `config.ManagementClient`, calls `DeleteNode`, and returns the response or error.

## State And Persistence
No local state. Persistent effects are entirely controlled by the management service's node deletion semantics.

## Dependencies And Integration Points
Depends on CTL global management client configuration and protobuf management API.

## Risks And Edge Cases
There is no local validation, idempotency handling, or response interpretation; callers must construct valid requests and handle service-level errors.

## Test Signals
No direct tests. A mock management client would be needed to test request pass-through and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/list.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/list.go

## Purpose
Lists BeeGFS nodes from the node store with optional node-type filtering, NIC inclusion, and UDP heartbeat reachability checks.

## Important APIs, Types, And Functions
Exports `GetNodes_Config`, `GetNodes_Nic`, `GetNodes_Node`, and `GetNodes`. Internal helpers are `checkReachability` and `recvDatagrams`.

## Control Flow
`GetNodes` fetches the `NodeStore`, filters nodes by `FilterByNodeType`, wraps their NICs, and stores NIC wrappers by address. If reachability is requested, it applies a timeout when the context has no existing deadline, sends a BeeMsg heartbeat UDP datagram to each NIC, and receives responses until all are marked reachable or the context expires.

## State And Persistence
No durable state. Reachability mutates the returned `GetNodes_Nic.Reachable` fields in memory. UDP socket lifetime is scoped to a single check.

## Dependencies And Integration Points
Uses `config.NodeStore`, BeeGFS node/NIC types, BeeMsg heartbeat assembly, UDP networking, and caller-supplied context deadlines.

## Risks And Edge Cases
`recvDatagrams` creates `buf := make([]byte, 0, util.MaxDatagramSize)` and passes it to `ReadFrom`; a zero-length buffer can prevent reading payload bytes, though source address may still be returned on some platforms. The socket itself does not set a read deadline; cancellation relies on context selection while the receiver goroutine may remain blocked in `ReadFrom` if not otherwise interrupted. NIC address strings must exactly match `from.String()` to mark reachability.

## Test Signals
No direct tests. Useful tests need UDP socket fakes or integration tests for heartbeat matching, context timeout, filtering, and invalid NIC addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/ping.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/ping.go

## Purpose
Pings management, metadata, and storage nodes through a BeeGFS client mount using the BeeGFS ping-node ioctl. It resolves an eligible local mount and streams per-node ping results and per-node errors.

## Important APIs, Types, And Functions
Exports `PingConfig`, `PingResult`, `PingError`, and `PingNodes`. The core work is a goroutine inside `PingNodes` that resolves target nodes and runs worker goroutines invoking `ioctl.PingNode`.

## Control Flow
`PingNodes` gets the management FS UUID, scans local BeeGFS client mounts via `procfs.GetBeeGFSClients`, filters by optional mountpoint and UUID, chooses the first equivalent mount, and loads the node store. The returned goroutine builds `toPing` from explicit IDs or all eligible nodes, chooses worker count based on `Parallel`, sorts nodes by type and numeric ID, sends them to workers, and closes result/error channels after workers finish.

## State And Persistence
No durable state. It emits transient ping timings and counters. It uses channel buffering of one for results and errors, and worker count from global Viper config when parallel.

## Dependencies And Integration Points
Integrates management gRPC (`GetFsUUID`), local `/proc/fs/beegfs` parsing, node store, BeeGFS ioctl ping, Viper global config, and zap logging.

## Risks And Edge Cases
If an ioctl error occurs in a worker, that worker sends an error and returns, leaving remaining queued nodes for other workers only; with a single worker, later nodes are skipped. Error channel buffer is one, so if multiple workers send errors before a caller drains, workers can block. The function treats the first matching client as equivalent, relying on earlier UUID filtering.

## Test Signals
No direct tests. Coverage should include mount discovery failure, explicit missing node IDs, sorted scheduling, parallel worker error behavior, and conversion of null-padded ioctl strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/ping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/setalias.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/setalias.go

## Purpose
Sets a management alias for a BeeGFS node entity.

## Important APIs, Types, And Functions
Exports `SetAlias(ctx, eid, newAlias)`.

## Control Flow
The function obtains a management client, converts the BeeGFS entity ID to protobuf form, and calls `SetAlias` with `EntityType_NODE`.

## State And Persistence
No local state. The persistent effect is the alias update stored by management.

## Dependencies And Integration Points
Depends on BeeGFS entity ID conversion, protobuf entity type constants, and CTL management client setup.

## Risks And Edge Cases
No local validation or normalization of alias input. Errors are passed through from client setup or management RPC.

## Test Signals
No direct tests. Mock pass-through tests would be sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/setalias.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/assign.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/assign.go

## Purpose
Thin management RPC wrapper for assigning storage targets or buddy groups to pools.

## Important APIs, Types, And Functions
Exports `Assign(ctx, req)` accepting `pm.AssignPoolRequest` and returning `pm.AssignPoolResponse`.

## Control Flow
Initializes a management client, calls `AssignPool`, and returns the service response.

## State And Persistence
No local state. Pool membership persistence is handled by the management service.

## Dependencies And Integration Points
Uses `config.ManagementClient` and protobuf management API.

## Risks And Edge Cases
No request validation or semantic checking in this layer; callers must handle partial or rejected assignments from management response semantics.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/assign.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/create.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/create.go

## Purpose
Thin management RPC wrapper for creating a storage pool.

## Important APIs, Types, And Functions
Exports `Create(ctx, req)` for `pm.CreatePoolRequest`.

## Control Flow
Gets the management client, calls `CreatePool`, and returns response/error unchanged.

## State And Persistence
No local state. Pool creation is persisted by the management service.

## Dependencies And Integration Points
Depends on CTL management client and protobuf management API.

## Risks And Edge Cases
No local validation or alias/id conflict handling.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/delete.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/delete.go

## Purpose
Thin management RPC wrapper for deleting a storage pool.

## Important APIs, Types, And Functions
Exports `Delete(ctx, req)` for `pm.DeletePoolRequest`.

## Control Flow
Gets the management client, calls `DeletePool`, and returns response/error.

## State And Persistence
No local state. Persistent deletion behavior is controlled by management.

## Dependencies And Integration Points
Depends on CTL management client and protobuf management API.

## Risks And Edge Cases
No local safety checks for non-empty or default pools.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/list.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/list.go

## Purpose
Retrieves and converts storage pool information from management into BeeGFS-native entity ID sets and quota-limit pointers for CTL display or downstream mapping.

## Important APIs, Types, And Functions
Exports `GetStoragePools_Result`, `GetStoragePools_Config`, and `GetStoragePools`.

## Control Flow
`GetStoragePools` obtains management client, calls `GetPools` with optional quota limits, converts each protobuf pool ID, target ID, and buddy-group ID using `beegfs.EntityIdSetFromProto`, and appends quota limit pointer fields directly from the response.

## State And Persistence
No local state. It reads management state and returns an in-memory snapshot.

## Dependencies And Integration Points
Used by utilities such as `util.GetMappings` and entry migration/set operations. Depends on management protobuf API and common BeeGFS entity conversion.

## Risks And Edge Cases
A single malformed entity ID aborts the entire list. Quota limit pointers use nil versus `-1` semantics from management; consumers must preserve this distinction. The local variable `buddy_groups` is stylistically non-Go but behaviorally harmless.

## Test Signals
No direct tests. Tests should cover conversion failures and `WithLimits` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/setalias.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/setalias.go

## Purpose
Sets a management alias for a storage pool entity.

## Important APIs, Types, And Functions
Exports `SetAlias(ctx, eid, newAlias)`.

## Control Flow
Obtains management client, converts entity ID to protobuf, and calls `SetAlias` with `EntityType_POOL`.

## State And Persistence
No local state. Alias persistence is handled by management.

## Dependencies And Integration Points
Uses common BeeGFS entity conversion and protobuf management API.

## Risks And Edge Cases
No local alias validation or conflict handling.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/setalias.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/procfs/procfs.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/procfs/procfs.go

## Purpose
Discovers local BeeGFS client mounts and parses `/proc/fs/beegfs*` client state, including config, management/meta/storage node connection info, filesystem UUID, and mountpoint mapping from `/proc/mounts`.

## Important APIs, Types, And Functions
Exports `GetBeeGFSClientsConfig`, `Client`, `Node`, `Peer`, `MountPoint`, `ErrEstablishingConnections`, and `GetBeeGFSClients`. Internal parsing helpers include `parseClient`, `parseClientFsUUIDFile`, `parseClientConfigFile`, `parseClientNodesFile`, `parseNodes`, `getBeeGFSMounts`, and `parseMounts`.

## Control Flow
`GetBeeGFSClients` parses BeeGFS mounts from `/proc/mounts`, optionally runs `df -t beegfs` to force client/server connections, walks `/proc/fs/<fstype>` directories, parses each client directory, and filters by FS UUID and/or mount paths. `parseClient` reads config and node files, derives client ID from directory name, associates mountpoint using `cfgFile`, and reads `fs_uuid`. `parseNodes` incrementally parses node headers, root markers, and semicolon-separated connection lines.

## State And Persistence
No local persistence. It reads kernel procfs state and may trigger connection establishment through `df`. Returned structs are snapshots.

## Dependencies And Integration Points
Used by `node/ping` and BeeRemote startup validation. Depends on Linux `/proc/mounts`, `/proc/fs/beegfs*`, external `df`, zap-compatible logger, and common BeeGFS NIC aliases/types.

## Risks And Edge Cases
Errors while walking procfs or parsing individual clients are logged and ignored, which favors partial discovery over hard failure. `parseNodes` assumes a node header was seen before `Root:` or `Connections:`; malformed files could panic on nil `current`. It handles only aliases compatible with `fmt.Sscanf("%s [ID: %d]")`. Mount parsing rejects BeeGFS mounts without `cfgFile`. `ForceConnections` shells out to `df`, so environment/path and command behavior matter.

## Test Signals
`procfs_test.go` covers config parsing, node parsing, and mount parsing with representative successful inputs. Gaps include malformed node files, missing `cfgFile`, filesystem UUID filtering, procfs walk error handling, and `ForceConnections` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/procfs/procfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/procfs/procfs_test.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/procfs/procfs_test.go

## Purpose
Unit-tests the pure parsing portions of procfs discovery: client config key/value parsing, BeeGFS node connection parsing, and BeeGFS mount parsing.

## Important APIs, Types, And Functions
Tests `parseClientConfigFile`, `parseNodes`, and `parseMounts` using `strings.NewReader` inputs and `testify/assert`.

## Control Flow
`TestParseClientConfigFile` verifies simple config, whitespace-heavy config, and empty input. `TestParseNodes` verifies multiple node entries, root flag, TCP/RDMA/SDP peers, fallback route detection, no-connection nodes, and empty input. `TestParseMounts` verifies filtering BeeGFS mount lines from mixed `/proc/mounts` content, extracting `cfgFile`, mount path, options, and filesystem type.

## State And Persistence
No persistent state; tests construct in-memory readers and expected structs.

## Dependencies And Integration Points
Depends on `testing`, `testify/assert`, and common BeeGFS types. It indirectly documents expected procfs text formats consumed by `procfs.go`.

## Risks And Edge Cases
The tests cover happy-path parsing but not malformed input, scanner errors, missing node headers before connection lines, mounts without `cfgFile`, escaping in mount paths, or duplicate filesystem types beyond `ElementsMatch`.

## Test Signals
This file itself is the primary test signal for procfs parsing. It gives confidence for common formats but leaves operational discovery and error paths untested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/procfs/procfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/quota/quota.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/quota/quota.go

## Purpose
Provides thin management RPC wrappers for quota default limits, explicit quota limits, and streaming quota limit/usage retrieval.

## Important APIs, Types, And Functions
Exports `SetDefault`, `SetLimits`, `GetLimits`, and `GetUsage`.

## Control Flow
Each function obtains a management client. Set functions call unary RPCs and return only the error. Get functions call streaming RPCs and return the generated stream client.

## State And Persistence
No local state. Persistent quota state and usage data live in management/storage services.

## Dependencies And Integration Points
Depends on `config.ManagementClient` and protobuf management quota APIs. Consumers are expected to read from returned streams.

## Risks And Edge Cases
No local validation or stream draining. Callers must handle stream lifecycle, partial results, and service-level validation.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/quota/quota.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getjobs.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getjobs.go

## Purpose
Queries BeeRemote job records by job ID/path, exact path, or path prefix and streams grouped job results back to callers.

## Important APIs, Types, And Functions
Exports `GetJobsConfig`, `GetJobsResponse`, `ErrGetJobsStreamUnavailable`, and `GetJobs`. `exactPath` is intentionally package-private for internal status use.

## Control Flow
`GetJobs` resolves the input path to a BeeGFS mount-relative path, builds include flags from config/debug options, selects one protobuf query variant, obtains `BeeRemoteClient`, opens the `GetJobs` stream, then starts a goroutine that receives until EOF. gRPC `Unavailable` is mapped to `ErrGetJobsStreamUnavailable`; `NotFound` is mapped to `rst.ErrEntryNotFound`.

## State And Persistence
No local persistence. It reads BeeRemote's job database through streaming RPC. Response channel ownership remains with the caller; this function closes it when streaming ends.

## Dependencies And Integration Points
Depends on `config.BeeGFSClient`, `config.BeeRemoteClient`, Viper debug config, common filesystem mount helpers, BeeRemote protobuf API, and gRPC status codes.

## Risks And Edge Cases
The function calls `beegfs.GetRelativePathWithinMount` even when `config.BeeGFSClient` returned `filesystem.ErrUnmounted`; this assumes a non-nil provider is still returned for unmounted/deleted paths. `ByExactPath` uses mount-relative path except package-private `exactPath` in one branch assigns `cfg.Path` directly, so callers must be careful about absolute versus in-mount semantics. Stream errors are fatal and terminate the channel.

## Test Signals
No direct tests. Needed coverage includes query selection, unmounted path behavior, gRPC error mapping, and channel close semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getjobs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getrstconfig.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getrstconfig.go

## Purpose
Fetches BeeRemote remote storage target configuration.

## Important APIs, Types, And Functions
Exports `GetRSTCfg` with `ShowSecrets` and `GetRSTConfig(ctx)`.

## Control Flow
`GetRSTConfig` obtains a BeeRemote client and calls `GetRSTConfig` with an empty request.

## State And Persistence
No local state. It reads BeeRemote configuration.

## Dependencies And Integration Points
Depends on CTL BeeRemote client setup and BeeRemote protobuf API. `GetRSTCfg.ShowSecrets` is declared here but not used by the fetch function, likely consumed by CLI formatting elsewhere.

## Risks And Edge Cases
No local handling of redaction or `ShowSecrets`; consumers must enforce display policy.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getrstconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getstubcontents.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getstubcontents.go

## Purpose
Fetches the remote target ID and URL/path embedded in an offloaded stub file through BeeRemote.

## Important APIs, Types, And Functions
Exports `GetStubContents(ctx, path)`.

## Control Flow
Obtains a BeeRemote client and sends `GetStubContentsRequest{Path: path}`.

## State And Persistence
No local state; reads BeeRemote/service interpretation of a stub path.

## Dependencies And Integration Points
Used by `rst/status.go` when clients cannot directly read offloaded stubs. Depends on BeeRemote protobuf API.

## Risks And Edge Cases
No local path normalization; callers must supply the path form expected by BeeRemote. Errors are passed through and interpreted by callers.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/getstubcontents.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/orphaned.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/orphaned.go

## Purpose
Scans BeeRemote job database paths and marks entries deleted when the corresponding BeeGFS path no longer exists, supporting cleanup of orphaned Remote DB records.

## Important APIs, Types, And Functions
Exports `CleanupOrphanedCfg`, `CleanupOrphanedResult`, and `CleanupOrphaned`. Internal helpers are `cleanupOrphanedPath` and `isNotFoundErr`.

## Control Flow
`CleanupOrphaned` validates path prefix, gets a BeeGFS client and BeeRemote client, starts `GetJobs` streaming, then uses an `errgroup` pipeline: one goroutine converts job responses into a path channel and worker goroutines lstat paths and update jobs. Worker count is `num-workers - 1` with a minimum of one. It returns a results channel plus wait function.

`cleanupOrphanedPath` skips existing paths, treats not-exist and ENOTDIR as orphaned, calls `UpdateJobs` with `NewState=DELETED` and `ForceUpdate=true`, and converts not-found update errors into skipped results.

## State And Persistence
Persistent effect is BeeRemote job state updates to deleted. Local state is transient channels and worker goroutines.

## Dependencies And Integration Points
Depends on `GetJobs`, BeeGFS filesystem provider `Lstat`, BeeRemote `UpdateJobs`, Viper worker count, gRPC status codes, and common RST not-found errors.

## Risks And Edge Cases
The scan only considers database paths returned by `GetJobs`; it does not reconcile filesystem paths absent from the DB. Race conditions are inherent: a path can be recreated after `Lstat` failure but before update. If `GetJobs` returns an error, the pipeline aborts. Results may be unordered due to parallel workers.

## Test Signals
No direct tests. Valuable tests would cover path exists, not exists, ENOTDIR, update not found, update false-ok response, streaming error, and worker cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/orphaned.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/status.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/status.go

## Purpose
Computes remote synchronization status for paths either from BeeRemote job database state or by verifying remote storage targets directly. It supports iterative/list input, recursive path/database merge, and remote verification modes.

## Important APIs, Types, And Functions
Exports `GetStatusCfg`, `GetStatusResult`, `PathStatus`, status constants, `PathStatus.String`, and `GetStatus`. Internal flow is split across `statusInfoVerifyRemoteWalk`, `statusInfoIterativeWalk`, `statusInfoRecursiveWalk`, `runWorkers`, `worker`, `getPathStatusFromTarget`, and `getPathStatusFromDatabase`.

## Control Flow
`GetStatus` streams paths lexicographically through `util.StreamPaths`, consumes the first path for setup, then starts a status-info stage and worker stage. Verification mode passes each path directly to workers. Iterative mode calls `GetJobs` once per path. Recursive mode opens one prefix stream from BeeRemote and merge-walks sorted filesystem paths with sorted database paths, producing matched or unmatched status info.

Workers load cached mappings, a BeeGFS client, and optionally RST provider clients. Database status checks lstat the path, reject directories/non-regular files, resolve remote targets either from config or entry metadata, compare latest relevant job per target against current file mtime, and produce synchronized/offloaded/unsynchronized/no-target/not-attempted statuses. Remote verification uses `rst.GetLockedInfo`, optional configured targets, stub-content fallback for offloaded unreadable files, and `rst.Provider.GetRemotePathInfo` to compare remote size/mtime.

## State And Persistence
No persistent mutations. It reads filesystem metadata, entry metadata, BeeRemote job DB, and remote object metadata. It uses Viper when converting status to emoji/text and uses cached mappings through `util.GetCachedMappings`.

## Dependencies And Integration Points
Integrates `ctl/pkg/util` path pipelines, `rst/getjobs.go`, `rst/getstubcontents.go`, `entry.GetEntry`, BeeGFS filesystem provider, common RST helper functions, remote storage providers, gRPC code handling, protobuf timestamps, and Viper debug/emoji flags.

## Risks And Edge Cases
Recursive status requires sorted filesystem and database paths; violating that ordering produces false not-found outcomes. In `getPathStatusFromDatabase`, `job := jobResult.GetJob()` is executed before checking `jobResult == nil`; a configured target with no matching job can panic instead of returning the intended "Path has no jobs" message. Mtime comparison uses exact `time.Equal`, which may be sensitive to precision differences. `PathStatus.String` depends on global Viper state. Remote verification returns a warning offloaded state for older BeeRemote services missing `GetStubContents`.

## Test Signals
No direct tests. This file needs focused tests for recursive merge ordering, no-job target handling, offloaded stubs, remote verification not-found handling, directory/non-regular classification, and debug versus non-debug reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/updatejob.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/updatejob.go

## Purpose
Updates BeeRemote job state for a single path/job or recursively for a path prefix.

## Important APIs, Types, And Functions
Exports `UpdateJobCfg`, `UpdateJobsResponse`, and `UpdateJobsByPaths`.

## Control Flow
Validates that recursive update is not combined with a specific job ID, resolves the path relative to the BeeGFS mount, builds `UpdateJobsRequest` with new state, force flag, path, optional job ID, and optional remote-target filter. For non-recursive updates it launches a goroutine that sends a unary `UpdateJobs` RPC and emits one response. For recursive updates it opens `UpdatePaths` stream and emits each update result until EOF.

## State And Persistence
Persistent effect is BeeRemote job DB state changes. Local state is the response channel and request-local remote target map.

## Dependencies And Integration Points
Depends on BeeGFS mount path resolution, BeeRemote client, BeeRemote update protobuf builders, and remote target IDs fitting uint32.

## Risks And Edge Cases
Like `GetJobs`, it tolerates `filesystem.ErrUnmounted` from client acquisition but still uses the returned provider. Recursive streaming errors terminate the channel after one error response. Remote targets are deduplicated into a map and values above `math.MaxUint32` are rejected.

## Test Signals
No direct tests. Tests should cover mutually exclusive options, path conversion, job ID setting, remote target bounds, unary and stream error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/rst/updatejob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/client.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/client.go

## Purpose
Fetches, normalizes, diffs, and aggregates per-client or per-user operation counters from metadata and storage servers.

## Important APIs, Types, And Functions
Exports operation-name slices, `ClientOps`, methods `Sub`/`Add`, `Diff`, `SumAllOpsFromSingleServer`, `SingleNodeClients`, and `PerNodeType`. Internal helpers include `sumEachOpFromAllServers` and `getClientStats`.

## Control Flow
`SingleNodeClients` resolves one node and reads one stats result. `PerNodeType` gets eligible nodes, starts one stats goroutine per node, reads their results, and aggregates by client/user ID. `getClientStats` probes whether a node supports `GetClientStatsV2`, then pages through stats using a cookie until `moreData` is false. It validates minimum response size, protocol version, and record layout, normalizes old IPv4 and V2 ID byte ordering for client stats, appends operation slices, updates cookie, and sorts results.

## State And Persistence
No persistent state. It reads server counters since server start and produces snapshots or interval diffs. `Diff` and aggregation mutate copies or map values in memory.

## Dependencies And Integration Points
Depends on node store, BeeMsg request/response types for metadata/storage stats, global node filtering in `server.go`, and common BeeGFS entity types.

## Risks And Edge Cases
Several error sends in `getClientStats` do not immediately return after protocol/layout validation, so a goroutine may continue and attempt to send more results into a buffered size-one channel, risking block or confusing consumers. `PerNodeType` initializes `statsList` with length `len(nodes)` and then appends each node's stats, leaving leading nil entries that are harmless for aggregation but wasteful and misleading. The loop condition for records uses `l < len(stats)` while indexing `opsSlice`, which deserves close review for off-by-one behavior.

## Test Signals
No direct tests. Needed tests include V1/V2 normalization, multi-page cookies, malformed response sizes, protocol mismatch, aggregation, and diff behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/rebalancing.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/rebalancing.go

## Purpose
Retrieves chunk-balance job statistics from metadata or storage nodes, used to observe rebalancing work.

## Important APIs, Types, And Functions
Exports `ChunkBalanceNodeStatus`, `ChunkBalanceStatusForNodes`, and `ChunkBalanceStatusForNode`. Internal helper `chunkBalanceStatusForNode` sends the BeeMsg request.

## Control Flow
The multi-node function gets a node store and filtered node list, then queries each node sequentially. The single-node function resolves one node by entity ID. The helper rejects non-meta/non-storage node types, sends `GetChunkBalanceJobStatsMsg`, wraps transport errors with a version-support hint, and returns the node, stats response, and per-node error field.

## State And Persistence
No local state or mutations. It reads active server-side rebalancing stats.

## Dependencies And Integration Points
Depends on `config.NodeStore`, shared `getNodeList`, BeeMsg chunk-balance stats messages, and common BeeGFS node types.

## Risks And Edge Cases
`ChunkBalanceStatusForNodes` aborts on helper errors that are returned as hard errors, but transport errors are embedded in `ChunkBalanceNodeStatus.Err`; consumers must inspect both function error and per-node error. Multi-node queries are sequential, unlike other stats collection.

## Test Signals
No direct tests. Coverage should verify node-type rejection, version-hint wrapping, and per-node error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/rebalancing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/server.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/server.go

## Purpose
Fetches high-resolution server stats from metadata/storage nodes and returns single-node, per-node latest, or aggregate time-series views.

## Important APIs, Types, And Functions
Exports `NodeStats`, `Stats`, `SingleServerNode`, `MultiServerNodes`, and `MultiServerNodesAggregated`. Internal helpers include `Stats.add`, `statsFromHighResolutionStats`, `getNodeList`, and `getServerStats`.

## Control Flow
`SingleServerNode` resolves one node, reads stats, reverses them into chronological order, and returns all entries. `MultiServerNodes` starts one goroutine per node and returns the second stats entry (`stats[1]`) as the latest stable sample when available. `MultiServerNodesAggregated` starts one goroutine per node, skips the two latest samples for inaccuracy, sums entries by timestamp, sorts by timestamp, and returns aggregate series plus node count. `getServerStats` sends `GetHighResStats{LastStatTime:0}` to a node.

## State And Persistence
No persistent state. It reads server counters/time-series snapshots and aggregates them in memory.

## Dependencies And Integration Points
Depends on node store, BeeMsg high-resolution stats, and common BeeGFS node filtering. Used by stats command frontends.

## Risks And Edge Cases
`MultiServerNodesAggregated` returns `err` from outer scope when `sRes.err != nil`, but that variable may be nil; it should likely return `sRes.err`. `Stats.add` assigns `StatsTime` from the other sample, which is fine for same-timestamp aggregation but would hide mismatches if misused. `MultiServerNodes` silently returns zero-value stats for nodes with errors or fewer than two samples.

## Test Signals
No direct tests. Tests should cover aggregation error propagation, short stat slices, sorting, and timestamp summing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/util/mapper.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/util/mapper.go

## Purpose
Builds and caches common BeeGFS entity mappings used throughout CTL, including targets, nodes, storage pools, buddy groups, mirrored targets, metadata buddy primaries, and Remote Storage Target configs.

## Important APIs, Types, And Functions
Exports errors (`ErrMappingRSTs`, `ErrMapperNotInitialized`, `ErrMapperNotFound`), `Mappings`, generic `Mapper[T]`, cache functions `GetCachedMappings` and `GetMappings`, mapper methods `Get`, `Len`, `UIDs`, `Aliases`, `LegacyIDs`, and mapping constructors such as `MapNodeToTargets`, `MapTargetToNode`, `MapStoragePoolToConfig`, `MapStorageTargetsToBuddyGroup`, and `MapRstIdToConfig`.

## Control Flow
`GetMappings` fetches targets, pools, node store, buddy groups, and BeeRemote RST config in sequence, building mapper structs after each source. RST mapping is initialized last so callers can choose to ignore `ErrMappingRSTs` while retaining other mappings. `GetCachedMappings` returns an existing clean cache, triggers background refresh if stale, or serializes a blocking refresh when cache is missing, errored, or force-updated.

`Mapper.Get` dispatches by concrete entity ID type and resolves UID, legacy ID, alias, or prioritized fields in `EntityIdSet`. Constructors populate three maps for each supported lookup type.

## State And Persistence
No disk persistence. Global mutable cache state includes cached mappings/error, force-update flag, update-in-progress flag, timestamps, mutexes, and injectable `getMappingsFunc` for tests.

## Dependencies And Integration Points
Central integration point for `ctl/pkg/ctl/target`, `pool`, `buddygroup`, node store, BeeRemote config, protobuf RST config, gRPC status handling, and many entry/RST commands.

## Risks And Edge Cases
`mappingsForceUpdate` is written outside a mutex before lock acquisition, creating a data-race risk under concurrent callers. Cached `Mappings` are mutable and documented as immutable-by-convention only. Background refresh uses the caller's context, so cancellation may poison the cache with an error. RST unavailability is returned as an error with partial mappings, and callers must intentionally tolerate it.

## Test Signals
`mapper_test.go` covers mapper length, cache first call, refresh on error, force update, fresh-cache hit, background update, already-active update, and entity-id-set lookup. Gaps include race tests, mapping constructors for buddy/pool/RST cases, and partial RST failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/util/mapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/util/mapper_test.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/util/mapper_test.go

## Purpose
Tests the generic mapper and cached mapping refresh behavior.

## Important APIs, Types, And Functions
Tests `Mapper.Len`, `GetCachedMappings`, `updateCachedMappingsInBackground` behavior through public calls, and `Mapper.Get` with `beegfs.EntityIdSet` against `MapTargetToNode`.

## Control Flow
Tests mutate package globals (`cachedMappings`, `cachedMappingsErr`, `cachedMappingsLastModified`, `activeCachedMappingsUpdate`, `getMappingsFunc`) to simulate cache states. Assertions verify immediate refresh, retry after previous error, forced refresh, no background update for fresh cache, background update for stale cache, suppression while an update is active, and UID/legacy/alias lookup from an `EntityIdSet`.

## State And Persistence
No persistence, but tests share and mutate global package state. They do not restore `getMappingsFunc` to the production function at the end of each test, which is acceptable inside package test order only if no later tests depend on default behavior.

## Dependencies And Integration Points
Uses `testify/assert` and `require`, common BeeGFS entity types, and `ctl/pkg/ctl/target` result structs.

## Risks And Edge Cases
The stale-cache test uses a very short sleep to wait for a goroutine and may be timing-sensitive on slow systems. The expression `time.Now().Add(-cachedMappingsUpdateDelay * time.Second)` multiplies a duration by `time.Second`, making the intended stale duration much larger than necessary but still stale. No tests run with the race detector assumptions around unsynchronized force-update state.

## Test Signals
Provides meaningful coverage for happy-path cache behavior and mapper lookup. Missing coverage includes constructor maps beyond target-to-node, concurrent callers, error from background refresh, and RST mapping error tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/util/mapper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/util/paths.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/util/paths.go

## Purpose
Provides common path input handling and concurrent path-processing pipelines for CTL commands. It supports explicit path lists, recursive directory walks, and delimited stdin.

## Important APIs, Types, And Functions
Exports `PathInputType`, `PathInputMethod`, `DeterminePathInputMethod`, `ProcessPathOpts`, option helpers `RecurseLexicographically` and `FilterExpr`, `ProcessPaths`, `StreamPaths`, and `WaitForLastStage`. Internal helpers include `startProcessing`, `walkStdin`, `walkList`, `walkDir`, and `pushFilterInMountPath`.

## Control Flow
`DeterminePathInputMethod` interprets path arguments and recursion/stdin flags. `ProcessPaths` starts a path-streaming errgroup and a processing errgroup, reserving one worker for walking unless single-worker mode is requested. `StreamPaths` compiles optional filesystem filter expressions and delegates to stdin/list/recursive walkers. Walkers convert paths to mount-relative paths, apply filters, and send accepted paths with context cancellation support. `WaitForLastStage` drains upstream channels before combining upstream/downstream errors into `types.MultiError`.

## State And Persistence
No persistence. State is confined to goroutines, channels, compiled filters, and a reused filesystem provider during list/stdin walking.

## Dependencies And Integration Points
Used by many CTL commands including entry set/migrate/refresh and RST status. Depends on Viper `num-workers`, BeeGFS client provider, common filesystem filtering/walking, stdin delimiter utilities, and `errgroup`.

## Risks And Edge Cases
For list/stdin processing, the first successful/failed provider is reused for subsequent paths; mixed mount inputs may be mishandled if a single client cannot resolve all paths. When `config.BeeGFSClient` returns `filesystem.ErrUnmounted`, code still calls methods on `client`, assuming it is usable. `WaitForLastStage` drains channels in goroutines and can block forever if an upstream stage does not close. Recursive walking always converts start path into mount-relative paths before walking.

## Test Signals
No direct tests in this file. Good tests would cover input-method selection, mixed mount list handling, filter behavior, cancellation, worker errors, recursive lexicographic ordering, and multi-error composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/util/paths.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/util/stdin.go -->
# sources/distributed-fs/beegfs-go/ctl/pkg/util/stdin.go

## Purpose
Handles delimiter parsing and scanner setup for CTL commands that read path or string input from stdin.

## Important APIs, Types, And Functions
Exports `GetStdinDelimiterFromString`, `GetWalkStdinScanner`, and `ReadFromStdin`.

## Control Flow
`GetStdinDelimiterFromString` converts user-provided strings into a single byte using `strconv.Unquote`, with special handling for the default newline display string. `GetWalkStdinScanner` builds a `bufio.Scanner` with a custom split function that returns tokens separated by the delimiter and emits trailing data at EOF. `ReadFromStdin` scans, sends tokens to a channel respecting context cancellation, reports scanner errors to `errChan`, and closes the output channel.

## State And Persistence
No persistence. It reads process stdin and sends transient channel values.

## Dependencies And Integration Points
Used by `paths.go` and any command needing delimited stdin. Depends on `os.Stdin`, `bufio.Scanner`, context cancellation, and byte delimiters.

## Risks And Edge Cases
`bufio.Scanner` retains its default token size limit, so very long paths/input records can fail. `ReadFromStdin` checks `scanner.Err()` inside the scan loop, where it is normally only meaningful after scanning completes; final scanner errors after the loop are not reported. Delimiters are restricted to one byte, not full runes.

## Test Signals
No direct tests. Needed coverage includes escape parsing, invalid delimiters, NUL delimiter scanning, long token behavior, cancellation, and scanner error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/pkg/util/stdin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/cmd/beegfs-remote/main.go -->
# sources/distributed-fs/beegfs-go/rst/remote/cmd/beegfs-remote/main.go

## Purpose
Main entrypoint for the BeeRemote service. It parses configuration, initializes logging and CTL globals, verifies the BeeGFS mount and license, starts worker/job/server components, and coordinates graceful shutdown.

## Important APIs, Types, And Functions
Defines build metadata variables (`binaryName`, `version`, `commit`, `buildTime`), constants including `FeatureLicenseStr`, capability map, and `main`. There are no exported library APIs.

## Control Flow
`main` registers CLI flags, handles version/help/dump-config/perf-profiling options, builds `configmgr.ConfigManager` with `config.AppConfig` and RST decode hook, initializes logger and CTL config, obtains BeeGFS mountpoint, sets signal cancellation, validates procfs mount config for `sysBypassFileAccessCheckOnMeta`, reads management TLS/auth material, creates a temporary management gRPC client for license verification, builds a `flex.BeeRemoteNode`, starts worker manager, job manager, and gRPC server, then waits for component error or OS signal before stopping components in reverse order.

## State And Persistence
Persistent interactions include logs, job DB path configured in lower layers, worker/remote activity, and server listening socket. This file reads cert/auth files and may start pprof HTTP server. It initializes global CTL logger and Viper state for reuse by lower packages.

## Dependencies And Integration Points
Integrates pflag, config manager, logger, CTL config, procfs parser, BeeGFS mount provider, mgmtd gRPC, license verification, worker manager, job manager, Remote server, OS signal handling, and pprof.

## Risks And Edge Cases
Startup uses fatal exits for configuration, mount, license, and component initialization failures. The pprof server ignores `ListenAndServe` errors. Procfs validation is warning-only except when a supported config key is present and set incorrectly. Management client is intentionally short-lived for license verification, so future management use must create its own client. Startup may block while resolving an inaccessible BeeGFS mount before mgmtd client setup.

## Test Signals
No direct tests. Integration or command tests would need dependency injection or process-level harnesses for config parsing, dump/version modes, procfs validation, license failure, component startup failure, and graceful shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/cmd/beegfs-remote/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/config/config.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/config/config.go

## Purpose
Defines BeeRemote application configuration, validation, and a mapstructure decode hook for protobuf oneof-based Remote Storage Target type configuration.

## Important APIs, Types, And Functions
Exports `AppConfig`, `MgmtdConfig`, `AppConfig.NewEmptyInstance`, `AppConfig.UpdateAllowed`, `AppConfig.ValidateConfig`, and `SetRSTTypeHook`.

## Control Flow
`AppConfig` aggregates mount, management, server, logger, job, worker-manager, worker, RST, and developer config. `ValidateConfig` checks job DB path presence, minimum retained job entries, and max/min retention consistency. `SetRSTTypeHook` intercepts decoding into `flex.RemoteStorageTarget`, finds a supported RST type key, constructs the proper protobuf oneof wrapper, decodes kebab-case-compatible type-specific config with unknown-key errors, sets `Type`, and deletes the type key.

## State And Persistence
No persistence here. Config values are consumed by the service and may point to durable paths such as job DB and logs. `UpdateAllowed` currently permits all updates, although comments note RST dynamic update policy is incomplete.

## Dependencies And Integration Points
Used by `beegfs-remote/main.go` and `configmgr`. Depends on server/job/worker/workermgr config structs, common logger config, RST supported type registry, mapstructure, protobuf `flex.RemoteStorageTarget`, and common `types.MultiError`.

## Risks And Edge Cases
`ValidateConfig` appends a multi-error for missing `PathDBPath` but returns immediately for retention errors, so multiple validation issues may not all be reported. The error message says `job.path-db-path`, while the flag is `job.path-db` in main. Decode hook mutates the input map in place and rejects mixing multiple RST types when `Type` already exists. Kebab/camel duplicate keys can produce ambiguous results as documented.

## Test Signals
No direct tests. Needed coverage includes validation combinations, supported/unsupported RST type decoding, unknown keys, duplicate type fields, kebab-case matching, and dynamic update expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/job.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/job/job.go

## Purpose
Defines BeeRemote job persistence and work-submission behavior. A `Job` wraps the protobuf job, stores regenerated transfer segments, tracks worker results, creates new jobs from requests, and serializes/deserializes jobs for Badger/gob storage.

## Important APIs, Types, And Functions
Exports `Job`, `Job.Get`, `Job.GetSegments`, `Job.InTerminalState`, `Job.InActiveState`, `Job.GenerateSubmission`, `Job.Complete`, `New`, `Job.GobEncode`, `Job.GobDecode`, `Segment`, `Segment.GobEncode`, and `Segment.GobDecode`.

## Control Flow
`New` creates a UUID, normalizes request path to absolute mount-relative form, initializes state `UNASSIGNED`, and accepts builder/sync/mock requests. `GenerateSubmission` calls the RST provider to generate work requests only when segments are absent; it stores cloned segments and later recreates requests from persisted segments for idempotence. `Complete` converts stored worker results into protobuf work records and delegates completion/abort cleanup to the RST provider. Gob encoding marshals the protobuf job separately, gob-encodes segments and work results, and prefixes the job bytes with a two-byte length.

## State And Persistence
Persistent job state includes protobuf job metadata/status, generated segments, and work results. Individual work requests are intentionally not persisted; they are regenerated from job plus segments. Job IDs are UUID strings. Gob serialization is the on-disk contract and must be updated when `Job` fields change.

## Dependencies And Integration Points
Integrates BeeRemote protobuf jobs, flex work requests, common RST provider interfaces, worker result types, worker manager job submissions, UUID generation, protobuf clone/marshal/unmarshal, gob, and timestamp generation.

## Risks And Edge Cases
`Get` returns the underlying protobuf pointer, so callers can mutate job state directly. The two-byte job-data length prefix limits marshaled job size to 65535 bytes; larger jobs would truncate length. `GobDecode` returns nil if segment decode fails, silently ignoring that error before decoding work results. Comments mention duplicate UUID consequences but probability is low. Segment regeneration intentionally does not re-check file size, so resumed submissions preserve original segmentation even if the file changed.

## Test Signals
`job_test.go` covers terminal-state classification. Missing tests include path normalization, accepted/rejected request types, idempotent submission generation, complete/abort delegation, gob round trip, large serialized job failure behavior, and decode error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/job_test.go -->
# sources/distributed-fs/beegfs-go/rst/remote/internal/job/job_test.go

## Purpose
Tests terminal-state classification for BeeRemote jobs.

## Important APIs, Types, And Functions
Defines `TestInTerminalState`, which exercises `Job.InTerminalState` using protobuf builder APIs.

## Control Flow
The test creates a job with status `COMPLETED`, asserts terminal, mutates the status to `CANCELLED`, asserts terminal, then mutates to `RUNNING` and asserts non-terminal.

## State And Persistence
No persistence. It mutates the in-memory protobuf status returned from the job.

## Dependencies And Integration Points
Uses `testify/assert` and BeeRemote protobuf job builders. It indirectly confirms that `Job.GetStatus()` mutations are reflected in the wrapped protobuf job.

## Risks And Edge Cases
It does not test `OFFLOADED`, even though `InTerminalState` treats it as terminal. It does not cover `InActiveState`, nil job/status handling, or other job lifecycle states.

## Test Signals
Provides minimal lifecycle classification coverage. It should be extended alongside job manager behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/rst/remote/internal/job/job_test.go -->
