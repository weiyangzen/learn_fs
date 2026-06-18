# subset-b-007045 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/NsCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/NsCmd.cc

## Purpose
`NsCmd.cc` implements the protobuf-backed `ns` administrative command for the EOS MGM. It covers namespace statistics, HA status reporting, namespace tree and quota recomputation, cache management, drain/tracker/behavior controls, id reservation, and a built-in namespace performance benchmark.

## Important APIs, Types, And Functions
`NsCmd::ProcessRequest()` dispatches `NsProto` subcommands to private handlers declared in `NsCmd.hh`. Local helpers collect and format HA status: `HaClusterStatus`, `ParseRaftInfoReply()`, `CollectQdbHaStatus()`, and `BuildMgmHaStatus()`. High-impact handlers include `StatSubcmd()`, `TreeSizeSubcmd()`, `QuotaSizeSubcmd()`, `UpdateTreeSize()`, `CacheSubcmd()`, `DrainSubcmd()`, `ReserveIdsSubCmd()`, `BenchmarkSubCmd()`, `TrackerSubCmd()`, `BehaviourSubCmd()`, and `TextHighlight()`.

## Control Flow
The command first branches by protobuf oneof case. `StatSubcmd()` gathers counters from namespace services, process memory/stat/fd helpers, MGM master state, QDB raft status, FuseX client stats, cache stats, lock latency, drain/fsck/converter/balancer/tape-GC engines, and optional per-command counters. It emits either monitoring key-value output, human text with optional color highlighting, or JSON through `ResponseToJsonString()`. `TreeSizeSubcmd()` resolves a container, builds breadth-first container levels, then updates from leaves upward. `QuotaSizeSubcmd()` validates a quota node under a read lock, optionally recomputes quota core from QDB, then applies updates under a namespace write lock. `BenchmarkSubCmd()` runs mkdir/create/exist/read/write/delete phases with worker threads and root identity.

## State, Persistence, And Dependencies
This file mutates persistent namespace metadata through directory service `updateStore()`, quota node core replacement/update, namespace cache configuration, config engine cache values, id blacklisting, drain engine config, tracker state, and behavior config. It depends on global `gOFS`, `FsView`, namespace services, QuarkDB/qclient, quota, config, drain, fsck, converter, tape GC, monitoring, FuseX, and OS inspection helpers. Locks include `gOFS->eosViewRWMutex`, instrumented RWMutex controls, and internal service locks.

## Integration Points
The command is part of the asynchronous `IProcCommand` admin path and maps console protobuf requests to MGM services. Its stats output is consumed by monitoring and operational tooling. QDB HA parsing integrates namespace backend details into `ns stat`. FuseX refreshes are triggered after tree-size mutation.

## Risks
Several operations are invasive: tree and quota recomputation can traverse or rewrite large namespace regions, benchmark creates and deletes live namespace entries, and cache drops can affect latency. `QuotaSizeSubcmd()` uses `strtoul()` on uid/gid strings without rich validation. `BreadthFirstSearchContainers()` preallocates 256 levels and silently notices deeper hierarchies. `MutexSubcmd()` exists only under `EOS_INSTRUMENTED_RWMUTEX`, so behavior differs by build. The benchmark allocates raw `XrdMgmOfsFile` objects and ignores most per-file errors.

## Test Signals
Useful signals include `ns stat` in human, monitoring, summary, and JSON modes; QDB-backed and in-memory namespace modes; tree-size recomputation on nested directories; quota recomputation and partial uid/gid updates; cache drop/set commands; root-gated mutex controls in instrumented builds; benchmark cleanup after failure; and regression checks for HA fields `ns.mgm.*` and `ns.qdb.*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/NsCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/NsCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/NsCmd.hh

## Purpose
`NsCmd.hh` declares the protobuf-backed namespace administration command class. It is the interface contract for the implementation in `NsCmd.cc`, exposing only `ProcessRequest()` publicly while keeping each namespace subcommand handler private.

## Important APIs, Types, And Functions
`class NsCmd : public IProcCommand` takes an rvalue `eos::console::RequestProto` and a `VirtualIdentity`, passes them to `IProcCommand`, and overrides `ProcessRequest() noexcept`. Private methods map directly to `NsProto` subcommands: `MutexSubcmd`, `StatSubcmd`, `MasterSubcmd`, `CompactSubcmd`, `TreeSizeSubcmd`, `QuotaSizeSubcmd`, `CacheSubcmd`, `DrainSubcmd`, `ReserveIdsSubCmd`, `BenchmarkSubCmd`, `TrackerSubCmd`, and `BehaviourSubCmd`. Helper methods are `BreadthFirstSearchContainers()`, `UpdateTreeSize()`, and `TextHighlight()`.

## Control Flow
The header establishes a single dispatch entry point. The implementation reads the request's namespace oneof case and calls the matching private method with the protobuf submessage and a mutable reply object. Tree-size repair uses the BFS helper to produce per-depth container id lists, then calls `UpdateTreeSize()` bottom-up.

## State, Persistence, And Dependencies
The declaration depends on `mgm/Namespace.hh`, generated `proto/Ns.pb.h`, `mgm/proc/ProcCommand.hh`, and namespace container metadata interfaces. It stores no command-specific members beyond inherited request and identity state. Persistence and locking obligations are implicit in helper comments, especially the note that `BreadthFirstSearchContainers()` assumes a write lock on `eosViewRWMutex`.

## Integration Points
`NsCmd` is consumed by the MGM proc command factory or dispatcher for console `ns` requests. Its protobuf signatures keep the command layer tied to `Ns.pb.h`, while its inheritance ties execution to the common asynchronous `IProcCommand` lifecycle and reply protocol.

## Risks
Because subcommands are private and broad in scope, testing has to enter through `ProcessRequest()` and build protobuf requests for every branch. The BFS helper comment says a write lock is assumed, but callers must enforce that convention; mismatch can produce metadata races. The header also exposes a large command surface in one class, increasing regression risk when generated protobuf fields change.

## Test Signals
Compile-time signals are generated protobuf compatibility and successful override of `ProcessRequest()`. Runtime signals are branch coverage for every `NsProto` subcommand, correct propagation of `retc/std_out/std_err`, and lock-sensitive tests around tree-size update helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/NsCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Quota.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/Quota.cc

## Purpose
`Quota.cc` implements the legacy opaque-parameter `ProcCommand::AdminQuota()` path for quota administration. In this file the only supported subcommand is quota node removal.

## Important APIs, Types, And Functions
`ProcCommand::AdminQuota()` reads `mSubCmd`, `pVid`, and `pOpaque`, sets inherited `retc/stdOut/stdErr`, and calls `Quota::RmSpaceQuota(path, msg, retc)` for `rmnode`.

## Control Flow
For `mSubCmd == "rmnode"`, the function requires uid 0, reads `mgm.quota.space` from the opaque request, rejects an empty path, and delegates removal to `Quota::RmSpaceQuota()`. Success places the returned message in `stdOut`; failure places it in `stdErr`. Unknown subcommands return `EINVAL` with an error string. The function always returns `SFS_OK` because proc command transport success is separated from command `retc`.

## State, Persistence, And Dependencies
The persistent effect is deletion of quota-node state through `Quota::RmSpaceQuota()`. The file depends on `ProcInterface`, the global MGM object include, and `mgm/quota/Quota.hh`. Authorization uses the virtual identity pointer from the legacy proc command object.

## Integration Points
This is the old admin command path, parallel to the newer protobuf `QuotaCmd::RmnodeSubcmd()`. It is reached by opaque proc requests rather than `QuotaProto`.

## Risks
The authorization rule here is stricter than `QuotaCmd.cc`, allowing only uid 0 while the protobuf path permits uid 0 or 3. Input is a raw opaque string and path normalization is not performed here. Only `rmnode` is implemented, so callers expecting parity with protobuf quota commands will get `EINVAL`.

## Test Signals
Exercise root and non-root `rmnode`, missing `mgm.quota.space`, successful and failed `Quota::RmSpaceQuota()` returns, and unknown subcommands. Regression tests should compare legacy and protobuf behavior intentionally because their authorization differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Quota.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/QuotaCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/QuotaCmd.cc

## Purpose
`QuotaCmd.cc` implements the protobuf-backed quota admin command. It lists quota usage, sets and removes user or group volume/inode limits, and removes quota nodes.

## Important APIs, Types, And Functions
`QuotaCmd::ProcessRequest()` dispatches `QuotaProto` oneof cases to `LsuserSubcmd()`, `LsSubcmd()`, `SetSubcmd()`, `RmSubcmd()`, and `RmnodeSubcmd()`. The implementation uses `Quota::PrintOut()`, `Quota::GetResponsibleSpaceQuotaPath()`, `Quota::SetQuotaTypeForId()`, `Quota::RmQuotaForId()`, `Quota::RmQuotaTypeForId()`, `Quota::RmSpaceQuota()`, `Acl::CanSetQuota()`, name mapping helpers, recycle-bin constants, and `ResponseToJsonString()`.

## Control Flow
List commands normalize a supplied space path through `_stat()`, optionally require it to exist, optionally verify it is the responsible quota node, and print uid/gid quota information. `lsuser` prints the caller's uid and gid views; `ls` can resolve explicit names and print one or both id types. `SetSubcmd()` and `RmSubcmd()` normalize the path, authorize root/admin or ACL quota admins, reject remote storage-node `sss` modification, validate uid-vs-gid exclusivity, translate names to numeric ids, then apply or remove quota types. `SetSubcmd()` has special recycle-bin handling and validates max bytes/inodes before calling quota setters. `RmnodeSubcmd()` is a privileged direct quota-node deletion path.

## State, Persistence, And Dependencies
Persistent changes happen in quota metadata through `Quota` APIs and may affect recycle-bin/project quota behavior. Listing reads namespace state under `eosViewRWMutex` when validating quota nodes. Dependencies include `gOFS`, ACL, stats, quota, recycle, path normalization, common constants, and user/group mapping caches. `MgmStats` records quota command usage.

## Integration Points
This command is the modern console path for `quota` protobuf requests and overlaps with the older `ProcCommand::AdminQuota()` for `rmnode`. It routes requests with `ShouldRoute(space, reply)` in `lsuser`, enabling master/namespace-aware routing before local quota printing.

## Risks
Path handling assumes non-empty strings before indexing `space[0]` in mutating ACL checks; malformed empty paths are mostly caught later but this branch is delicate. `errno`-based size parsing requires callers not to depend on stale `errno`. Authorization differs between rmnode legacy and protobuf paths. Recycle-bin quota changes intentionally allow localhost exceptions and warning-only paths.

## Test Signals
Cover list modes with existing, missing, and non-quota-node paths; JSON/monitoring output; uid/gid name translation failures; root/admin/quota-admin/non-admin authorization; remote `sss` denial; byte and inode quota validation; recycle-bin project quota behavior; removing whole quota records vs volume/inode-only records; and rmnode permissions for uid 0 and 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/QuotaCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/QuotaCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/QuotaCmd.hh

## Purpose
`QuotaCmd.hh` declares the protobuf-backed quota command wrapper. It defines the command class and the private handler surface implemented in `QuotaCmd.cc`.

## Important APIs, Types, And Functions
`class QuotaCmd : public IProcCommand` accepts a `RequestProto` and `VirtualIdentity`, disables the parent constructor's third flag by passing `false`, and overrides `ProcessRequest() noexcept`. Private handlers cover `LsuserSubcmd`, `LsSubcmd`, `SetSubcmd`, `RmSubcmd`, and `RmnodeSubcmd`, each taking the matching generated `QuotaProto_*` message plus a reply reference.

## Control Flow
The header's structure makes `ProcessRequest()` the only public entry. The implementation switches on `QuotaProto::subcmd_case()` and delegates to one private method per protobuf oneof branch.

## State, Persistence, And Dependencies
The class has no additional data members. It depends on generated quota protobuf types, the command base class, and MGM namespace macros. Persistence is performed by implementation calls into quota services, not by the header itself.

## Integration Points
`QuotaCmd` plugs the console protobuf quota API into the MGM proc command execution framework. The method signatures are tightly coupled to `proto/Quota.pb.h`, so protobuf schema changes are compile-time visible here.

## Risks
The command surface is narrow but privileged. Because handlers are private, unit tests generally need to exercise them through `ProcessRequest()` or use friend-style harnesses. Handler signatures return through mutable reply objects, so omissions in implementation can leave default success-looking fields if not set consistently.

## Test Signals
Compile generated protobuf compatibility and dispatch every `QuotaProto` oneof case. Runtime checks should verify non-supported cases return `EINVAL`, and every handler sets `retc`, `std_out`, and `std_err` consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/QuotaCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Rtlog.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/Rtlog.cc

## Purpose
`Rtlog.cc` implements the legacy `ProcCommand::Rtlog()` command for retrieving recent in-memory log lines from the current MGM and/or FST endpoints.

## Important APIs, Types, And Functions
`ProcCommand::Rtlog()` reads opaque keys `mgm.rtlog.queue`, `mgm.rtlog.lines`, `mgm.rtlog.tag`, and optional `mgm.rtlog.filter`. It uses `Logging::GetInstance()`, `GetPriorityByString()`, `gLogMemory`, `gLogCircularIndex`, `FsView::gFsView.CollectEndpoints()`, and `gOFS->BroadcastQuery()`.

## Control Flow
The command requires root. It validates required opaque parameters and log priority tag. For local MGM requests (`.`, `*`, or the MGM queue), it iterates log priority buckets up to the requested tag and scans backward through each circular buffer, appending matching lines. For FST requests (`*` or non-local queue), it resolves endpoints, builds a `fst.pcmd=rtlog` query, broadcasts with a 10-second timeout, and appends response payloads.

## State, Persistence, And Dependencies
The command is read-only except for inherited output fields and `mDoSort`. It depends on global in-memory logging buffers protected by `g_logging.gMutex`, filesystem endpoint discovery from `FsView`, and MGM broadcast query transport.

## Integration Points
This is an opaque proc admin command, not a protobuf command. It federates MGM-side log access with FST-side `rtlog` handling by issuing a query to storage endpoints.

## Risks
`lines` is parsed with `atoi()` and lacks range validation, so very large values can scan repeatedly until the circular buffer empties. The local log mutex is locked and unlocked once per priority bucket while building output. Filter defaulting to a single space means blank or unusual log lines can be skipped. Broadcast response aggregation does not annotate endpoint boundaries.

## Test Signals
Test root gating, missing parameters, invalid tags, local-only queues, wildcard queues, FST endpoint misses, broadcast failures, filter behavior, and line limits larger than the circular buffer. Concurrency tests should stress log access while writers append.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Rtlog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/SchedCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/SchedCmd.cc

## Purpose
`SchedCmd.cc` implements the protobuf-backed scheduler administration command for configuring and inspecting filesystem placement scheduler state.

## Important APIs, Types, And Functions
`SchedCmd::ProcessRequest()` dispatches `SchedProto` cases. `ConfigureSubcmd()` dispatches nested configure options to `SchedulerTypeSubcmd()`, `WeightSubCmd()`, `ShowSubCmd()`, and `RefreshSubCmd()`. `LsSubcmd()` emits scheduler state. The implementation calls `gOFS->mFsScheduler` methods such as `setPlacementStrategy()`, `getPlacementStrategy()`, `setDiskWeight()`, `getStateStr()`, and `updateClusterData()`, and formats strategy names through `placement::strategy_to_str()`.

## Control Flow
Top-level dispatch supports `config` and `ls`; unsupported top-level cases return `EINVAL`. Configure dispatch supports type, weight, show, and refresh. Type changes set the default scheduler strategy. Weight changes update a specific fsid weight in a space and fail on scheduler rejection. Listing maps enum options to `bucket`, `disk`, or `all` before requesting a scheduler state string. Show currently handles scheduler type display, optionally for a named space. Refresh forces cluster data refresh.

## State, Persistence, And Dependencies
The command mutates in-memory scheduler state through `mFsScheduler`; any persistence depends on scheduler internals or other config paths, not this file. It depends on the global MGM object, placement strategy definitions, and generated scheduler protobufs. There is no explicit authorization check or lock in this implementation.

## Integration Points
This command is the console protobuf entry point for scheduler inspection and limited configuration. It overlaps with `SpaceCmd`'s `space config ... scheduler.type` path, which sets per-space scheduler strategy and persists it as space config.

## Risks
The absence of local root/admin gating means safety depends on outer command authorization. `ShowSubCmd()` returns a default reply if the requested option is not `TYPE`, which can look successful with empty output. Scheduler state changes are made without explicit synchronization in this file. Formatting has minor spacing issues in success strings but no behavioral impact.

## Test Signals
Cover unsupported top-level and configure cases, default and per-space scheduler type changes, invalid disk weight updates, list modes for bucket/disk/all, refresh behavior, and authorization through the surrounding command dispatcher. Tests should also verify `ShowSubCmd()` behavior for non-`TYPE` options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/SchedCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/SchedCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/SchedCmd.hh

## Purpose
`SchedCmd.hh` declares the protobuf-backed scheduler command class under `namespace eos::mgm`.

## Important APIs, Types, And Functions
`class SchedCmd : public IProcCommand` stores no extra state, accepts a request and virtual identity, and overrides `ProcessRequest() noexcept`. Private helpers return `ReplyProto` by value: `ConfigureSubcmd()`, `SchedulerTypeSubcmd()`, `WeightSubCmd()`, `LsSubcmd()`, `ShowSubCmd()`, and `RefreshSubCmd()`.

## Control Flow
The declaration sets a two-level dispatch shape: `ProcessRequest()` handles top-level scheduler subcommands, and `ConfigureSubcmd()` handles nested configuration options. Unlike other admin command headers in this subset, helpers return reply objects directly instead of mutating a shared reply reference.

## State, Persistence, And Dependencies
The header depends on `proto/Sched.pb.h` and `mgm/proc/IProcCommand.hh`. It introduces no persistence behavior. The implementation mutates scheduler state through the global MGM scheduler pointer.

## Integration Points
This class plugs scheduler protobuf requests into the common `IProcCommand` execution framework and uses the modern C++ namespace declaration style rather than the `EOSMGMNAMESPACE_BEGIN` macro.

## Risks
Returning replies by value keeps subcommands isolated but can hide inconsistent default replies if a branch forgets to set `retc`. Generated protobuf schema changes are compile-time breaking at the private method signatures.

## Test Signals
Compile-time checks should catch protobuf and base-class compatibility. Runtime tests should build requests for each declared subcommand and assert returned reply fields rather than relying on mutated output parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/SchedCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/SpaceCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/SpaceCmd.cc

## Purpose
`SpaceCmd.cc` implements the protobuf-backed space administration command for EOS MGM filesystem spaces. It lists and inspects spaces, defines/removes spaces, toggles space and quota state, manages node and space config, resets operational caches, and exposes tracker, inspector, group balancer, and group drainer status/control.

## Important APIs, Types, And Functions
`SpaceCmd::ProcessRequest()` dispatches `SpaceProto` oneof cases to handlers declared in `SpaceCmd.hh`. Key handlers are `LsSubcmd()`, `StatusSubcmd()`, `SetSubcmd()`, `NodeSetSubcmd()`, `NodeGetSubcmd()`, `ResetSubcmd()`, `DefineSubcmd()`, `ConfigSubcmd()`, `QuotaSubcmd()`, `RmSubcmd()`, `TrackerSubcmd()`, `InspectorSubcmd()`, `GroupBalancerSubCmd()`, `GroupBalancerStatusCmd()`, and `GroupDrainerSubCmd()`.

## Control Flow
Read commands take `FsView::gFsView.ViewMutex` and print space state in listing, monitoring, IO, fsck, or JSON-compatible formats. Mutating commands generally require uid 0, validate the target space, and update `FsSpace`, `FsGroup`, `FsNode`, or `FileSystem` config members. `ConfigSubcmd()` is the largest branch: it handles REST tape switches, `space.` keys, policy keys, balancer/tracker/inspector/LRU/groupbalancer/groupdrainer toggles, attributes, numeric tuning values, and `fs.` keys that cascade to all filesystems in a space with config autosave disabled until the batch completes. Remove checks all filesystems are `empty`, deletes the shared hash config, then unregisters the space.

## State, Persistence, And Dependencies
State changes persist through `SetConfigMember()`, `DeleteConfigMember()`, `StoreFsConfig()`, config engine autosave, shared-hash deletion, and in-memory maps such as `gOFS->mSpaceAttributes`. Runtime engines are reconfigured or signaled: REST API manager, FS scheduler, replication tracker, file inspector, LRU engine, filesystem balancer, group balancer, and group drainer. Dependencies include `FsView`, namespace view services, ACL validation, Egroup refresh, token generation, tape GC constants, REST constants, and common scan/ALTXS constants.

## Integration Points
This command is a central bridge between console space operations and MGM runtime subsystems. It interacts with lower-level filesystem config from `proc_fs.cc` by applying space defaults and storing per-filesystem updates. It also overlaps with `SchedCmd` for scheduler type.

## Risks
`ConfigSubcmd()` is broad and string-key driven, making allow-list omissions or typo regressions likely. Some operations take a read lock while mutating config members, so safety depends on those member methods' own synchronization or historical lock semantics. `NodeSetSubcmd()` can load files only under `/var/eos/` and stores base64 content on every node. Numeric parsing relies on `errno` and accepts many size suffix forms. Root checks are local to most mutating handlers but not all read-side operational dumps.

## Test Signals
Cover list/status formats, root gating, defining spaces and invalid group products, toggling groups/nodes, node-set file loading and path rejection, all reset options, config remove/set for policies and attributes, REST tape activation rules, engine toggles and reconfiguration calls, cascading `fs.` config with autosave, quota toggle, removing non-empty vs empty spaces, inspector missing space, group balancer status options, and group drainer status/reset modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/SpaceCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/SpaceCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/admin/SpaceCmd.hh

## Purpose
`SpaceCmd.hh` declares the protobuf-backed EOS space administration command class and its private subcommand handler interface.

## Important APIs, Types, And Functions
`class SpaceCmd : public IProcCommand` accepts a request and virtual identity and overrides `ProcessRequest() noexcept`. Private methods cover space listing, tracker/status/set/node-set/node-get/reset/define/config/quota/rm/inspector/groupbalancer/groupdrainer operations. `FsSpace` is forward-declared for `GroupBalancerStatusCmd()`.

## Control Flow
The header establishes a one-handler-per-protobuf-subcommand layout. Most handlers mutate a shared `ReplyProto&`; a few stateless helpers are `static` (`TrackerSubcmd`, `ResetSubcmd`, `InspectorSubcmd`) because they do not need command instance fields. Group balancer and group drainer handling is split into a top-level command method plus a status helper.

## State, Persistence, And Dependencies
The class has no extra data members beyond `IProcCommand`. It depends on generated `Space.pb.h`, MGM namespace macros, and the proc command base. Persistence and subsystem reconfiguration are delegated to the implementation.

## Integration Points
`SpaceCmd` is the modern protobuf command layer for space operations. Its signatures couple console protobuf schema directly to MGM filesystem-space internals while hiding implementation detail from the dispatcher.

## Risks
The broad private handler list reflects a large operational surface in one class. Static handlers can still mutate globals, so their static-ness should not be read as safety. Generated protobuf changes affect this header directly.

## Test Signals
Compile every generated protobuf type referenced here. Runtime dispatch tests should verify every `SpaceProto` oneof reaches the expected handler and that static and non-static handlers produce consistent reply status fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/SpaceCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Vid.cc -->
# sources/distributed-fs/eos/mgm/proc/admin/Vid.cc

## Purpose
`Vid.cc` implements the legacy opaque-parameter `ProcCommand::Vid()` command for virtual identity mapping administration.

## Important APIs, Types, And Functions
`ProcCommand::Vid()` dispatches by `mSubCmd` and calls `Vid::Ls()`, `Vid::Set()`, or `Vid::Rm()` with the opaque request environment and inherited reply fields.

## Control Flow
`ls` is allowed for the caller and sets `mDoSort` after delegating to `Vid::Ls()`. `set` and `rm` require uid 0; root requests call the corresponding `Vid` static method, while non-root requests return `EPERM`. Unknown subcommands fall through and return `SFS_OK` without setting an explicit error in this file.

## State, Persistence, And Dependencies
The persistent behavior is delegated to `mgm/vid/Vid.hh` APIs, which manage virtual identity mappings. This file depends on the legacy `ProcInterface`, global MGM include, and opaque request state. It mutates only inherited command output/status and sort behavior directly.

## Integration Points
This is an old proc admin command path and complements newer protobuf command classes elsewhere. It is likely reached by `vid` console operations that still use opaque key/value parameters.

## Risks
Unknown `mSubCmd` values are not rejected here, which can produce an apparently transport-successful no-op if no outer layer validates them. `ls` is not root-gated, so sensitive output control depends on `Vid::Ls()` itself. `set`/`rm` authorization is uid 0 only.

## Test Signals
Test `ls`, root and non-root `set`, root and non-root `rm`, and an unsupported subcommand. Assertions should check both command `retc` and `stdErr` because the function always returns `SFS_OK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Vid.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/proc_fs.cc -->
# sources/distributed-fs/eos/mgm/proc/proc_fs.cc

## Purpose
`proc_fs.cc` implements lower-level filesystem administration helpers used by legacy and modern MGM admin commands. It classifies filesystem move operands, dumps filesystem metadata, configures/adds/removes filesystems, moves filesystems/groups/spaces/nodes, sorts target groups, and repairs filesystem-view deletion or ghost lists.

## Important APIs, Types, And Functions
Entity classification is handled by `get_entity_type()` and `get_operation_type()`. Permission helper `check_sss_hostname_match()` validates root or matching storage-node `sss` identity. Main exported functions include `proc_fs_dumpmd()`, `proc_fs_config()`, `proc_fs_add()`, `proc_fs_rm()`, `proc_fs_dropdeletion()`, `proc_fs_dropghosts()`, `proc_fs_mv()`, `proc_fs_can_mv()`, `proc_mv_fs_group()`, `proc_mv_fs_space()`, `proc_mv_grp_space()`, `proc_mv_space_space()`, `proc_mv_fs_node()`, and `proc_sort_groups_by_priority()`.

## Control Flow
`proc_fs_dumpmd()` prefetches file metadata, iterates filesystem file lists under namespace read lock, emits env/path/id/size output, reports ghost or missing-container warnings, and includes unlinked files in monitoring mode. `proc_fs_config()` resolves a filesystem by id, uuid, or node/path, allow-lists keys, checks host authorization, validates special values, then stores config. `proc_fs_add()` validates identity and queue path, checks duplicate mappings, chooses a scheduling group from explicit or priority candidates, creates/provides uuid mappings, registers the filesystem, and applies space defaults. `proc_fs_mv()` classifies the operation and calls specific move helpers under the FsView write lock. Move helpers enforce empty/online state unless forced, group capacity and same-host constraints, apply destination defaults, and store config. `proc_mv_fs_node()` snapshots, removes, unlocks, re-adds on the new node, then relocks. Drop helpers require root and mutate namespace filesystem-view lists.

## State, Persistence, And Dependencies
Persistent state includes filesystem registration mappings, shared filesystem config, per-filesystem config keys, group/space membership, and namespace filesystem-view entries. Dependencies include `FsView`, `FileSystem`, `gOFS`, namespace views/services, prefetcher, common path/layout/constant utilities, messaging realm, and MGM master status. Locking uses `FsView::gFsView.ViewMutex` and `gOFS->eosViewRWMutex`.

## Integration Points
These helpers sit beneath admin commands such as fs add/rm/config/mv and interact with `SpaceCmd` via space default parameters. Storage nodes can call selected paths using `sss` when the authenticated host matches the target host.

## Risks
Move/remove paths are operationally dangerous because they rewrite registration state. `proc_mv_fs_node()` manually unlocks and relocks a write mutex mid-operation, so exception safety and lock ownership assumptions are critical. Group capacity checks use `>` rather than `>=` in some places. Environment variables can bypass same-host group or SSS hostname checks. `proc_fs_config()` has a suspicious condition around `max.ropen`/`max.wopen` that should be regression-tested. `stoi()`/`atoi()` conversions are not uniformly guarded.

## Test Signals
Cover operand classification, unsupported move combinations, root vs SSS host authorization, metadata dump modes with ghost and unlinked entries, config key allow-list and validation, empty filesystem checks before removal/configstatus empty, duplicate uuid/fsid/queue registration, automatic group selection, force behavior, same-host group rejection, space/group/node moves, failed reinsert during node move, and root-only ghost/deletion cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/proc_fs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/proc_fs.hh -->
# sources/distributed-fs/eos/mgm/proc/proc_fs.hh

## Purpose
`proc_fs.hh` declares the filesystem administration helper API implemented in `proc_fs.cc`. It defines operand and move-operation enums and exposes functions for filesystem metadata dump, config, add/remove, move, validation, sorting, and namespace view cleanup.

## Important APIs, Types, And Functions
`enum EntityType` classifies inputs as unknown, filesystem, group, space, or node. `enum class MvOpType` encodes supported move pairs. Exported functions include `proc_fs_dumpmd`, `proc_fs_config`, `proc_fs_add`, `proc_fs_rm`, `proc_fs_dropdeletion`, `proc_fs_dropghosts`, `get_entity_type`, `get_operation_type`, `proc_fs_mv`, `proc_fs_can_mv`, `proc_mv_fs_group`, `proc_mv_fs_space`, `proc_mv_grp_space`, `proc_mv_space_space`, `proc_mv_fs_node`, and `proc_sort_groups_by_priority`.

## Control Flow
Callers typically parse command input, then call `proc_fs_mv()` or specific helpers. `proc_fs_mv()` derives `MvOpType` from the two string operands and dispatches to lower-level move functions. Add/config/remove helpers take mutable output/error strings and a virtual identity, returning errno-style integers while callers separately map those into command replies.

## State, Persistence, And Dependencies
The header depends on MGM namespace macros, logging/mapping utilities, filesystem and FsView classes, file metadata interfaces, XRootD security entity declarations, STL sets/lists, and forward-declared `eos::mq::MessagingRealm`. Notes document that several move helpers require `FsView::ViewMutex` to already be locked.

## Integration Points
This is a shared procedural API for MGM admin code. It bridges command parsing layers to `FsView`, filesystem registration, namespace filesystem-view maintenance, and messaging-backed filesystem objects.

## Risks
Many functions accept mutable string references for both inputs and outputs, so callers must not assume inputs remain semantically immutable. Locking preconditions are documented but not enforced by types. The enum names/comments have a small mismatch for `GROUP` and `SPACE` descriptions, which can confuse maintainers even though values are used consistently in code.

## Test Signals
Compile users against the declared signatures, especially after changes to `FileSystem`, `FsView`, or messaging realm types. Runtime tests should assert errno-style return codes, output/error mutation, and caller-held lock expectations for the lower-level move helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/proc_fs.hh -->
