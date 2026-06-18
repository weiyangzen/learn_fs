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
