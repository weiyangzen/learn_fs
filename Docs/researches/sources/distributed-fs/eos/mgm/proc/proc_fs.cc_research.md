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
