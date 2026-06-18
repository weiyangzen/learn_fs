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
