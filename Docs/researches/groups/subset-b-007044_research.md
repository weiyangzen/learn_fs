# subset-b-007044 research

Grouped research for EOS MGM admin command sources. Each section is keyed by the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FsCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/FsCmd.cc

Purpose: Implements the protobuf-backed `fs` administrative command for EOS MGM. `FsCmd::ProcessRequest()` dispatches `FsProto` subcommands for filesystem registration, boot signaling, config, listing, removal, status/risk inspection, metadata dumping, replica deletion, filesystem comparison, and clone-style replica copy.

Important APIs/types/functions: `FsCmd::ProcessRequest()` maps proto oneof cases to private methods. `Add()` normalizes node queue or host:port input and calls `proc_fs_add()`. `Boot()` sets per-filesystem `bootcheck` and `bootsenttime` attributes for all filesystems, a node queue, or one fsid/uuid. `Config()`, `Mv()`, `Rm()`, `DropDeletion()`, `DropGhosts()`, and `DumpMd()` delegate to legacy `proc_fs_*` helpers. `List()` renders `FsView` space/filesystem formats and drain job info. `Status()` prints filesystem config and can scan namespace metadata for risk. `DropFiles()`, `Compare()`, and `Clone()` iterate `eosFsView` file lists and call `gOFS` stripe helpers. `SemaphoreProtectedProcDumpmd()` limits concurrent metadata dumps with static `mSemaphore`.

Control flow: Requests are decoded from `mReqProto.fs()` and return `ReplyProto` with `mOut`, `mErr`, and return code. Most mutating paths require root or `sss`, while list is generally readable. Filesystem view operations use `FsView::gFsView.ViewMutex`; namespace metadata scans use `gOFS->eosViewRWMutex` and prefetch. Add/move/remove update `mFsScheduler` cluster data after modifying topology.

State and persistence behavior: Topology and filesystem attributes live in `FsView`, shared hash configuration, and file-system config persisted through legacy proc helpers or `FsView::StoreFsConfig`. Boot writes transient MGM-side config members that FSTs observe. Dump/status/compare/clone read namespace metadata through `eosFsView`, `eosFileService`, and `eosView`. `DropFiles()` mutates file replica locations via `_dropstripe`; `Clone()` mutates replicas via `_copystripe`.

Dependencies and integration points: Integrates with `mgm/proc/proc_fs.hh`, `XrdMgmOfs`, `FsScheduler`, `FsView`, `LayoutId`, namespace `IView`/`IFsView`, `Prefetcher`, `MgmStats`, drain engine, and XRootD string/semaphore utilities. It is the protobuf command bridge replacing older opaque-param admin paths while still relying on legacy `proc_fs_*` implementation details.

Risks: `SemaphoreProtectedProcDumpmd()` returns early on invalid fsid or too many entries after `mSemaphore.Wait()` without posting, which can leak semaphore capacity. `Status()` risk analysis can be expensive because it prefetches and scans every file on a filesystem. `Rm()` parses node queue by `find("/fst")` and can produce surprising substrings if the marker is missing. `Compare()` and `Clone()` silently ignore metadata exceptions, so output can underreport failures. Many operations rely on global `gOFS` services and coarse locks, making concurrency and master/replica behavior important in tests.

Test signals: Exercise each proto oneof dispatch, root and non-root authorization, node queue normalization, scheduler refresh after add/move/remove, JSON monitor list conversion, drain job listing, dumpmd semaphore release on all error paths, dumpmd >100k rejection, status risk analysis for replica/plain layouts, drop/clone error accounting, and behavior under missing fsid, uuid, node, or namespace metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FsCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FsCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/FsCmd.hh

Purpose: Declares the protobuf `FsCmd` command object used by MGM admin processing for filesystem operations.

Important APIs/types/functions: `FsCmd` derives from `IProcCommand`, constructs with `RequestProto` and `VirtualIdentity`, and overrides `ProcessRequest()`. Private helpers mirror all supported `FsProto` subcommands: `List`, `Config`, `Mv`, `Rm`, `DropDeletion`, `DropGhosts`, `Add`, `Boot`, `DumpMd`, `Status`, `DropFiles`, `Compare`, and `Clone`. `DisplayModeToString()` maps list display enums to `FsView` format selectors. `SemaphoreProtectedProcDumpmd()` wraps legacy dumpmd access. `SizeOfArray()` is a small constexpr helper. `mSemaphore`, `mOut`, `mErr`, and `mRetc` carry shared dump throttling and per-command response state.

Control flow: The header establishes a single command instance per request with private subcommand methods called by `ProcessRequest()`. The base constructor flag is `true`, indicating this command uses the asynchronous/proc command behavior configured by `IProcCommand`.

State and persistence behavior: The class itself owns only response buffers and return code. Persistent effects are implemented in the `.cc` via `FsView`, shared hashes, config engine, and namespace services. The static semaphore is process-wide and affects all `fs dumpmd` invocations.

Dependencies and integration points: Includes `IProcCommand`, `Namespace.hh`, and `ConsoleRequest.pb.h`, with XRootD types used in method signatures through included project headers. It is consumed by the MGM admin command factory for filesystem proto requests.

Risks: Because `mOut`, `mErr`, and `mRetc` are mutable command state, helper methods must consistently set them on all paths. Static semaphore lifecycle and early returns in the implementation are cross-request risks. Header declarations expose a broad private surface, so proto schema changes require synchronized updates here and in dispatch.

Test signals: Compile coverage for all proto subcommand signatures, construction through command factory, one response per command instance, and semaphore behavior across concurrent `DumpMd` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FsCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FsckCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/FsckCmd.cc

Purpose: Implements the protobuf-backed `fsck` admin command, including status, configuration, report generation, single-entry repair, and orphan cleanup on FST endpoints.

Important APIs/types/functions: `FsckCmd::ProcessRequest()` dispatches `FsckProto` oneof cases. `mFsckEngine->PrintOut()` returns engine state; `Config()` changes fsck settings; `Report()` renders selected tags and display modes; `RepairEntry()` repairs a fid with an error fsid and async option. `CleanOrphans` builds a `/ ?fst.pcmd=clean_orphans` query and uses `gOFS->BroadcastQuery()`. Under `EOS_GRPC_GATEWAY`, an overload streams the same logic through `grpc::ServerWriter<ReplyProto>`.

Control flow: Non-report subcommands require `mVid.uid == 0`. Global orphan cleanup (`fsid == 0`) collects all online node hostports from `FsView::mNodeView`; per-fsid cleanup resolves the filesystem and targets its host and locator port. Broadcast failures are summarized per endpoint. The gRPC version writes the reply after each branch and has mostly duplicated control flow.

State and persistence behavior: Configuration and repair state are delegated to `mFsckEngine`. `force_qdb_cleanup` can trigger `ForceCleanQdbOrphans()` independent of disk cleanup. Orphan cleanup mutates FST-local on-disk orphan state through remote queries, not directly through MGM metadata.

Dependencies and integration points: Depends on `XrdMgmOfs`, `FsView`, and `mgm/fsck/Fsck.hh`. Integrates with online FST discovery, MGM broadcast query plumbing, and optional EOS REST/gRPC gateway generated service headers.

Risks: The gRPC and unary implementations are duplicated and can drift. Broadcast returns are treated as aggregate failure, but only endpoints with nonzero per-endpoint codes are printed. Report is allowed for non-root users, so tag and output filtering must not leak unintended data. Force QDB cleanup on global clean can run even if endpoint cleanup later fails.

Test signals: Admin authorization for every branch, non-root report access, config failure message fallback, report tag set handling, repair success/failure, global and single-fsid orphan cleanup endpoint selection, missing fsid errors, broadcast partial failures, and parity between unary and gRPC implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FsckCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FsckCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/FsckCmd.hh

Purpose: Declares `FsckCmd`, the `IProcCommand` implementation for protobuf fsck administration.

Important APIs/types/functions: The class constructor accepts `RequestProto` and `VirtualIdentity` and passes `false` to the base command. `ProcessRequest()` returns a full `ReplyProto`. When `EOS_GRPC_GATEWAY` is enabled, a second `ProcessRequest()` writes streamed replies to a gRPC `ServerWriter`.

Control flow: The header defines the unary and optional streaming entry points only; subcommand branching is contained in the implementation. The streaming overload exists to support REST/gRPC gateway paths without changing the command object's request and identity inputs.

State and persistence behavior: The class has no own persistent members beyond inherited request/identity. All fsck state is maintained in `gOFS->mFsckEngine` and FST endpoints.

Dependencies and integration points: Includes `Fsck.pb.h`, `IProcCommand.hh`, EOS namespace definitions, and optionally gateway gRPC generated headers. Used by console/gateway command routing for `FsckProto` requests.

Risks: Conditional compilation means gateway builds can diverge from normal builds. Duplicated overload semantics require tests in both build configurations.

Test signals: Compile both with and without `EOS_GRPC_GATEWAY`, verify command factory construction, unary return values, and streamed reply emission for each subcommand.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FsckCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Fusex.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/Fusex.cc

Purpose: Implements the legacy opaque-parameter `fusex` admin command for inspecting and controlling the MGM FUSEX/ZMQ server state.

Important APIs/types/functions: `ProcCommand::Fusex()` supports `ls`, `conf`, `evict`, `droplocks`, and `caps`. It calls `gOFS->zMQ->gFuseServer.Print()`, adjusts client heartbeat/quota intervals and broadcast-audience controls, evicts clients by UUID and reason, drops locks by inode/pid, and prints capability state.

Control flow: Only root may execute. `conf` reads `mgm.fusex.*` opaque keys, applies provided values, reports current values when omitted, and persists selected settings under the default space. `evict` base64-decodes a reason before passing it to the FUSE server client. `droplocks` parses hex inode and decimal pid. Unknown subcommands return `EINVAL`.

State and persistence behavior: Runtime FUSEX server settings are changed in `gFuseServer.Client()`. Some configuration is persisted through `FsView::gFsView.mSpaceView["default"]->SetConfigMember()` for `fusex.bca`, `fusex.bca_match`, `fusex.hbi`, and `fusex.qti`. Eviction and lock dropping mutate active client/session state.

Dependencies and integration points: Depends on `ProcInterface`, `XrdMgmOfs`, `mgm/zmq/ZMQ.hh`, `FsView`, and common base64/string helpers. It is part of the older `ProcCommand` admin path rather than the protobuf `IProcCommand` path.

Risks: Assumes `mSpaceView["default"]` exists when persisting config. `atoi()` treats invalid numeric input as zero, which can convert bad input into "show current" behavior. Heartbeat typo in error text is harmless but visible. Root-only access is broad, and eviction/droplock actions immediately affect clients.

Test signals: Root authorization, config validation boundaries for heartbeat 1..15 and quota 1..60, persistence of broadcast and interval settings, invalid numeric strings, eviction of none/one/many clients, unknown UUID `ENOENT`, lock parsing and missing lock errors, and capability filtering with URL-unescaped filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Fusex.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/GeoSched.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/GeoSched.cc

Purpose: Implements the legacy `geosched` admin command for inspecting and tuning the `GeoTreeEngine` placement scheduler.

Important APIs/types/functions: `ProcCommand::GeoSched()` handles `showtree`, `showsnapshot`, `showstate`, `showparam`, `set`, updater pause/resume, force refresh, disabled-branch add/remove/show, direct access geotag mapping, and proxygroup access mapping. Operations are delegated to `gOFS->mGeoTreeEngine`.

Control flow: Root is required. Show commands gather schedgroup, operation type, color, and monitoring flags before `printInfo()`. `set` parses parameter/index/value and saves through `setParameter(..., true)`. Disabled branch and access commands use `mSubCmd.beginswith()` to group related actions and pass `true` when changes should be saved to config.

State and persistence behavior: Scheduler parameters, disabled branches, access geotag mappings, and proxygroup mappings are persisted through `GeoTreeEngine` when called with save enabled. Pause/resume/force refresh are runtime scheduler-control actions. Output is accumulated in legacy `stdOut`/`stdErr` fields.

Dependencies and integration points: Depends on `ProcInterface`, `XrdMgmOfs`, and `GeoTreeEngine`. Group state changes in `GroupCmd` also manipulate disabled placement branches, so this file is part of the same placement-control surface.

Risks: Multiple independent `if` blocks rather than `else if` rely on non-overlapping subcommand names. Parameter parsing is thin and validation is delegated to the engine. Access mapping commands can persist broad changes such as clearing all direct mappings when geotag is `all`.

Test signals: Authorization, each show mode with monitoring/color flags, parameter set success/failure, pause failure path, force refresh, disabled branch add/remove/show persistence, direct and proxygroup access mapping set/clear/show, and ambiguous or unknown subcommand return code behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/GeoSched.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/GroupCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/GroupCmd.cc

Purpose: Implements protobuf-backed group administration for listing, removing, creating, and changing EOS filesystem groups.

Important APIs/types/functions: `GroupCmd::ProcessRequest()` dispatches `GroupProto` oneof cases. `LsSubcmd()` chooses `FsView` group/filesystem formats for normal, listing, monitoring, and IO views, with optional JSON conversion. `RmSubcmd()` validates empty group state, deletes the group's shared hash config, and unregisters the group. `SetSubcmd()` creates missing groups except for drain, stores group `status`, adjusts per-filesystem `local.drainer`, and updates `GeoTreeEngine` disabled placement branches based on geotags.

Control flow: Listing takes a read lock and renders `FsView::PrintGroups()`. Remove and set require root and take a write lock. Removal refuses groups whose member filesystems are not `ConfigStatus::kEmpty`. Setting `on` re-enables placement branches and may enable local drainers if any filesystem is already draining. Setting `off` disables local drainers. Setting `drain` disables placement for all geotags represented in the group.

State and persistence behavior: Group membership and status live in `FsView::mGroupView`/`FsGroup` and shared hash config. Remove deletes `SharedHashLocator::makeForGroup()`. Set writes group config members and persists geotree disabled branch changes through `GeoTreeEngine`. It mutates filesystem local drain flags in memory/config member storage.

Dependencies and integration points: Depends on `FsView`, `mq::SharedHashWrapper`, `XrdMgmOfs`, and `GeoTreeEngine`. Interacts with filesystem drain status strings and placement geotags (`stat.geotag`, operation `plct`).

Risks: Group creation error constructs but does not use `groupconfigname`. Set returns success without a success message in several paths. Geotag branch updates can partially succeed before a later failure in drain mode. The command assumes geotag config members exist and are meaningful.

Test signals: Format selection and JSON output, root-only remove/set, missing/empty group errors, removal blocked by non-empty filesystems, shared-hash delete failure, create-on-set behavior, drain rejection for missing group, drainer flag recomputation for `on`/`off`, disabled placement branch updates, and partial geotag failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/GroupCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/GroupCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/GroupCmd.hh

Purpose: Declares `GroupCmd`, the protobuf command wrapper for EOS MGM group administration.

Important APIs/types/functions: `GroupCmd` derives from `IProcCommand`, overrides `ProcessRequest()`, and declares private `LsSubcmd()`, `RmSubcmd()`, and `SetSubcmd()` helpers that accept generated `GroupProto` submessage types plus a mutable `ReplyProto`.

Control flow: The header defines a request-scoped command object with all behavior funneled through `ProcessRequest()` and helper branches. The constructor passes `false` to the base command, matching other protobuf admin commands that do not use the special filesystem-command flag.

State and persistence behavior: No direct persistent state is stored in the object. The implementation mutates `FsView`, shared hashes, and geotree placement config.

Dependencies and integration points: Includes `Namespace.hh`, `Group.pb.h`, and `ProcCommand.hh` for `IProcCommand`/reply helpers. It is used by MGM admin routing for `GroupProto` requests.

Risks: Any proto schema changes for group subcommands require synchronized signature and dispatch changes. The command exposes only three subcommands, so unsupported future oneof cases will return `EINVAL` until implemented.

Test signals: Construction, dispatch for ls/rm/set, unsupported oneof handling, and compile compatibility with generated `Group.pb.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/GroupCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/IoCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/IoCmd.cc

Purpose: Implements the protobuf-backed `io` command for IO statistics, collection toggles, namespace popularity reports, namespace report reads, and dispatch into traffic shaping.

Important APIs/types/functions: `IoCmd::ProcessRequest()` dispatches `IoProto` oneof cases. `StatSubcmd()` calls `mIoStats->PrintOut()` with summary/detail/top/domain/app/sample/time options. `EnableSubcmd()` starts/stops IO collection, popularity collection, report store, namespace reporting, or UDP targets. `ReportSubcmd()` prints a namespace report for root. `NsSubcmd()` translates proto options into legacy flag strings for `PrintNsPopularity()`. `ShapingSubcommand()` is implemented in `IoShapingCmd.cc`.

Control flow: Stat defaults to summary output if no detail selectors are enabled and converts monitoring output to JSON when requested. Enable/disable branches are selected by `switchx()` and secondary booleans for reports/namespace/popularity/UDP. Report requires root. Namespace popularity builds compact flags for ranking, hotfiles, week scope, and count before rendering.

State and persistence behavior: IO collection/report/popularity state is managed by `gOFS->mIoStats`. UDP targets are added/removed from the IO stats subsystem. This file mostly toggles runtime services and reads report state; traffic shaping persistence is in `IoShapingCmd.cc` and its engine.

Dependencies and integration points: Depends on `Iostat`, `XrdMgmOfs`, `ProcInterface`, generated `Io.pb.h`, ZMQ headers, and the `IoCmd.hh` shaping declaration. Integrates older `Iostat` formatting with protobuf console requests.

Risks: Most enable/disable actions do not check root, so authorization must be enforced by higher-level routing if intended. Output messages can concatenate when enabling reports and namespace reporting together. `ReportSubcmd()` guards `mIoStats` but still returns success with empty output if it is null. Legacy flag string construction in `NsSubcmd()` is compact but not type-safe.

Test signals: Dispatch for every subcommand, stat default summary behavior, JSON conversion, enable/disable idempotency errors, UDP target add/remove, popularity requiring collection start, root-only report, namespace option flag mapping, count enum handling, and shaping dispatch into `IoShapingCmd.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/IoCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/IoCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/IoCmd.hh

Purpose: Declares `IoCmd` and the traffic shaping report builder API used by EOS MGM IO administration.

Important APIs/types/functions: Forward declares `TrafficShapingRateRequest` and `TrafficShapingRateResponse`, and declares `BuildTrafficShapingRateReport()` for external report construction. `IoCmd` derives from `IProcCommand`, overrides `ProcessRequest()`, and declares helpers for stat, enable, report, namespace popularity, shaping dispatch, and older monitor shaping helpers (`MonitorSet`, `MonitorSetLs`, `MonitorSetRm`, `MonitorAdd`, `MonitorRm`).

Control flow: The command object's `.cc` dispatches generated `IoProto` submessages into these helpers. Shaping helper declarations split the larger implementation into `IoShapingCmd.cc` while keeping command state and access to `WantsJsonOutput()` in `IoCmd`.

State and persistence behavior: The header owns no persistent state. Runtime and persistent effects occur in `gOFS->mIoStats` and `gOFS->mTrafficShapingEngine`.

Dependencies and integration points: Includes `Namespace.hh`, `ProcCommand.hh`, and standard string. It is the common declaration shared by normal IO stats code, traffic shaping implementation, and any component that needs `BuildTrafficShapingRateReport()`.

Risks: Some monitor helper declarations appear legacy and are not implemented in the read file set, so stale declarations should be checked during refactors. Shaping implementation depends on generated proto names in method signatures, so proto evolution has high compile impact here.

Test signals: Build linkage for `IoCmd.cc` plus `IoShapingCmd.cc`, external use of `BuildTrafficShapingRateReport()`, dispatch into shaping, and absence of stale undefined helper references in linked targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/IoCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/IoShapingCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/IoShapingCmd.cc

Purpose: Implements traffic shaping subcommands under `io shaping`, plus a reusable protobuf rate report builder for live IO rates, policies, pressure, and engine configuration.

Important APIs/types/functions: Formatting helpers render rates, pressures, durations, booleans, and table labels. `ParseAutomaticDetailCardinalityConfig()` parses `auto-cardinality:low:high[:enabled|disabled]`. `Rates`, `ExtractWindowRates()`, `SetRateStats()`, and `BuildReport()` aggregate `TrafficShapingManager` snapshots into `TrafficShapingRateResponse`. `BuildTrafficShapingRateReport()` exposes that aggregation. Command helpers include `ShapingPolicySet()`, `ShapingPolicyDelete()`, `ShapingTrafficEnable()`, `ShapingTrafficDisable()`, `ShapingList()`, `ShapingPolicyList()`, `ShapingPressureList()`, `ShapingConfig()`, and `IoCmd::ShapingSubcommand()`.

Control flow: The public `IoCmd::ShapingSubcommand()` dispatches list, enable, disable, policy list/set/remove, config list/set, and pressure list. Most helpers first resolve `gOFS->mTrafficShapingEngine.GetManager()` and fail if unavailable. Listing selects app/user/group/node/fs/all aggregation, chooses an SMA window, resolves IDs unless JSON disables it, optionally includes system stats, and emits either compact JSON or aligned tables. Policy set merges requested fields into an existing or default policy for app/uid/gid. Config set validates detail level and thresholds before mutating engine settings.

State and persistence behavior: Runtime state lives in `gOFS->mTrafficShapingEngine` and its `TrafficShapingManager`: enabled flag, policy maps, detail level, controller/reservation/limit settings, update periods, pressure thresholds, idle GC, and system stats windows. The file calls engine setters and manager policy setters/removers; actual persistence, if any, is owned by the engine/config layer outside this file.

Dependencies and integration points: Uses `common/shaping` identity and key helpers, `mgm/shaping/TrafficShaping.hh`, `FsView` constants for detail-level strings, JSONCPP, generated `TrafficShaping.pb.h`, generated console reply types, and global `XrdMgmOfs`. It bridges console protos, REST/report consumers via `BuildTrafficShapingRateReport()`, and the background traffic shaping manager.

Risks: No explicit admin check is visible in shaping helpers, so authorization depends on callers or command routing. Numeric setters accept zero and very small periods unless the engine rejects them. `ShapingList()` uses `std::stoul(name)` for resolved uid/gid output and assumes map keys are numeric strings. Detail-level and policy changes have immediate cluster-wide scheduling impact. JSON and table output contain similar but not identical fields, so client compatibility needs coverage.

Test signals: Manager-uninitialized failures, rate report estimator selection/top sorting/include types, app/user/group/node/fs/all list modes, filesystem-detail-disabled response, JSON vs table output, ID resolution on/off, system stats fields, policy set/update/delete/list for app/uid/gid, config validation for detail and pressure thresholds, automatic cardinality parsing, enable/disable idempotent behavior, pressure list empty and populated output, and authorization at routing level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/IoShapingCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Monit.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/Monit.cc

Purpose: Implements the legacy opaque-parameter monitoring admin command for Prometheus endpoint configuration.

Important APIs/types/functions: `ProcCommand::Monit()` reads `mgm.subcmd`, `mgm.monit.service`, `mgm.monit.port`, and `mgm.monit.cache_ttl`. It uses monitoring helpers `ParsePortConfig()`, `ParseUint32Config()`, `IsValidCacheTtl()`, and constants for Prometheus global config keys. It calls `gOFS->GetMonitoringConfig()` and `gOFS->ApplyMonitoringConfig()`.

Control flow: Only service `prometheus` is accepted. `ls`, `list`, and `status` return current config. Mutating commands require master MGM. `enable` validates or requires a configured port, optionally validates cache TTL, sets the enabled flag, and applies the config. `disable` clears the enabled flag and applies. Unsupported subcommands return `EINVAL`.

State and persistence behavior: Monitoring settings are stored as global `FsView` config values (`kPrometheusPortConfig`, `kPrometheusCacheTtlConfig`, `kPrometheusEnabledConfig`). `ApplyMonitoringConfig()` applies them to the running MGM monitoring service. Persistence is through the global config mechanism, not local members.

Dependencies and integration points: Depends on `FsView`, `MonitoringConfig.hh`, `XrdMgmOfs`, and legacy `ProcCommand`. It coexists with the newer protobuf `MonitCmd` implementation and should remain behavior-compatible where possible.

Risks: Legacy enable requires an existing or supplied port, while `MonitCmd::EnableSubcmd()` defaults the port if missing. Only master checks protect mutation; read access is open. Cache TTL parse accepts string input and must be kept aligned with protobuf validation.

Test signals: Unsupported service, list aliases, master-only mutation, enable with missing port, port range validation, cache TTL range validation, disable, apply failure propagation, and compatibility with protobuf monitoring command output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Monit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/MonitCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/MonitCmd.cc

Purpose: Implements protobuf-backed monitoring administration for listing, setting, enabling, and disabling the Prometheus monitoring endpoint.

Important APIs/types/functions: `MonitCmd::ProcessRequest()` dispatches `MonitProto` oneof cases. `ConfigSubcmd()` dispatches config `ls` and `set`. `ConfigLsSubcmd()` returns `gOFS->GetMonitoringConfig()`. `ConfigSetSubcmd()` validates port and cache TTL, updates global config, and applies. `EnableSubcmd()` ensures a default Prometheus port when absent, sets enabled, and applies. `DisableSubcmd()` clears enabled and applies.

Control flow: Unsupported command or config oneof cases return `EINVAL`. All mutations require `gOFS->mMaster->IsMaster()`. Each mutating path updates `FsView::gFsView` global config first, then calls `ApplyMonitoringConfig()` and returns the refreshed configuration on success.

State and persistence behavior: State is global MGM monitoring config in `FsView` using `MonitoringConfig.hh` keys and defaults. Runtime application is delegated to `XrdMgmOfs::ApplyMonitoringConfig()`. The command object is stateless apart from inherited request identity.

Dependencies and integration points: Depends on generated `Monit.pb.h`, `FsView`, `MonitoringConfig.hh`, and `XrdMgmOfs`. It is the protobuf counterpart to `ProcCommand::Monit()`.

Risks: Behavior differs from legacy `Monit.cc` by auto-populating `kDefaultPrometheusPort` on enable. `DisableSubcmd()` ignores its proto payload, so future fields would need explicit handling. Applying after partial config changes can leave global config updated even when runtime apply fails.

Test signals: Dispatch errors, config list, master authorization, port/cache TTL validation, default port creation on enable, disable, apply failure, output shape after each success, and compatibility with legacy command state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/MonitCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/MonitCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/MonitCmd.hh

Purpose: Declares `MonitCmd`, the protobuf `IProcCommand` for MGM monitoring configuration.

Important APIs/types/functions: The class constructor stores `RequestProto` and `VirtualIdentity` through the base. `ProcessRequest()` is the public command entry point. Private helpers return `ReplyProto` by value for config dispatch, config list/set, enable, and disable.

Control flow: The declaration models monitoring as a small command tree with nested config subcommands. Returning `ReplyProto` by value lets helper methods short-circuit validation failures cleanly.

State and persistence behavior: The class has no own persistent state. Implementation reads and writes global monitoring config through `FsView` and applies it through `gOFS`.

Dependencies and integration points: Includes `IProcCommand.hh` and generated `Monit.pb.h`. It is used by MGM protobuf command routing for monitoring requests.

Risks: Header and proto oneof schema must evolve together. The small helper surface makes unsupported future subcommands return `EINVAL` until implemented.

Test signals: Construction, dispatch to config/enable/disable, unsupported oneof handling, and compile compatibility with `Monit.pb.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/MonitCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/NodeCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/NodeCmd.cc

Purpose: Implements protobuf-backed node administration for listing, removing, status inspection, configuration, state changes, and proxygroup membership.

Important APIs/types/functions: `NodeCmd::ProcessRequest()` dispatches `NodeProto` oneof cases. `FormatNodeStatusValue()` masks base64/zbase64, very long, and binary values for status output. `LsSubcmd()` renders `FsView::PrintNodes()` in listing, monitoring, IO, SYS, or FSCK formats. `RmSubcmd()` normalizes node names, verifies heartbeat silence and empty filesystems, deletes shared hash config, unregisters the node, and removes config entries. `StatusSubcmd()` prints sorted node config keys. `ConfigSubcmd()` applies selected node keys or delegates `configstatus` to `ConfigFsSpecific()`. `SetSubcmd()` registers/sets node status with root or same-node `sss` identity. `ProxygroupSubcmd()` adds/removes/clears comma-separated proxy groups.

Control flow: Node names are normalized to `/eos/host:port/fst`, defaulting port 1095. Mutations require root or `sss`; `SetSubcmd()` and `ProxygroupSubcmd()` also compare the authenticated `tident` host to the target node unless `EOS_SKIP_SSS_HOSTNAME_MATCH` is set. Config with wildcard node name applies to all nodes. Filesystem-specific config gathers fsids under a node then stores per-filesystem config and autosaves.

State and persistence behavior: Node and filesystem state live in `FsView::mNodeView`, `mIdView`, shared hashes, and the config engine. Remove deletes node shared hash and matching global config values then autosaves. Config writes node config members for known keys or per-filesystem `configstatus` through `StoreFsConfig()`. Set/proxygroup also write the current master id as node `manager`.

Dependencies and integration points: Depends on `common/Constants.hh`, `IConfigEngine`, `XrdMgmOfs`, `ProcInterface`, `MessagingRealm`, namespace `IFsView`, and `FsView` globals. It coordinates with FST heartbeats, filesystem config status, MGM master identity, and CBOX sync constants.

Risks: `StatusSubcmd()` checks `mNodeView` before taking the lock, then takes a write lock for read-only output. Several success paths set no explicit `retc`, relying on default zero. `ConfigSubcmd()` takes a read lock while calling `SetConfigMember()` for node configs, which may be a locking/design concern depending on `FsNode`. The hostname match bypass environment variable is operationally useful but weakens same-node `sss` protection. Comma-list proxygroup editing is manual string parsing.

Test signals: Name normalization, listing formats and JSON conversion, root/sss authorization, same-host `sss` match and bypass, remove blocked by recent heartbeat or non-empty filesystem, shared hash delete failure, config key validation and persistence, `configstatus=empty` blocked by remaining files, CBOX forbid sync remove/set validation, node registration on set/proxygroup, manager field update, status masking for base64/binary/long values, and proxygroup add/remove/clear with invalid characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/NodeCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/NodeCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/NodeCmd.hh

Purpose: Declares `NodeCmd`, the protobuf command object for MGM node administration.

Important APIs/types/functions: `NodeCmd` derives from `IProcCommand`, overrides `ProcessRequest()`, and declares helpers for `LsSubcmd`, `RmSubcmd`, static `StatusSubcmd`, `ConfigSubcmd`, `ConfigFsSpecific`, `SetSubcmd`, and `ProxygroupSubcmd`.

Control flow: The header captures the command tree represented by `NodeProto`: list, remove, status, config, set, and proxygroup. `ConfigFsSpecific()` separates node-level config from filesystem config changes that must be applied to every filesystem under selected nodes.

State and persistence behavior: No persistent members are declared. The implementation mutates global `FsView`, shared hashes, config engine, and filesystem config.

Dependencies and integration points: Includes `Namespace.hh`, generated `Node.pb.h`, and `ProcCommand.hh`. It is consumed by protobuf admin command routing and interacts with FST node state through the implementation.

Risks: Static `StatusSubcmd()` cannot use instance identity or JSON helpers unless passed explicitly, so status behavior is intentionally limited. Header signatures must track proto submessage names and generated namespace changes.

Test signals: Dispatch coverage for all declared helpers, static status behavior, config filesystem-specific path, unsupported oneof handling, and compile compatibility with generated `Node.pb.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/NodeCmd.hh -->
