# sources/distributed-fs/eos/mgm/proc/admin/GroupCmd.cc

Purpose: Implements protobuf-backed group administration for listing, removing, creating, and changing EOS filesystem groups.

Important APIs/types/functions: `GroupCmd::ProcessRequest()` dispatches `GroupProto` oneof cases. `LsSubcmd()` chooses `FsView` group/filesystem formats for normal, listing, monitoring, and IO views, with optional JSON conversion. `RmSubcmd()` validates empty group state, deletes the group's shared hash config, and unregisters the group. `SetSubcmd()` creates missing groups except for drain, stores group `status`, adjusts per-filesystem `local.drainer`, and updates `GeoTreeEngine` disabled placement branches based on geotags.

Control flow: Listing takes a read lock and renders `FsView::PrintGroups()`. Remove and set require root and take a write lock. Removal refuses groups whose member filesystems are not `ConfigStatus::kEmpty`. Setting `on` re-enables placement branches and may enable local drainers if any filesystem is already draining. Setting `off` disables local drainers. Setting `drain` disables placement for all geotags represented in the group.

State and persistence behavior: Group membership and status live in `FsView::mGroupView`/`FsGroup` and shared hash config. Remove deletes `SharedHashLocator::makeForGroup()`. Set writes group config members and persists geotree disabled branch changes through `GeoTreeEngine`. It mutates filesystem local drain flags in memory/config member storage.

Dependencies and integration points: Depends on `FsView`, `mq::SharedHashWrapper`, `XrdMgmOfs`, and `GeoTreeEngine`. Interacts with filesystem drain status strings and placement geotags (`stat.geotag`, operation `plct`).

Risks: Group creation error constructs but does not use `groupconfigname`. Set returns success without a success message in several paths. Geotag branch updates can partially succeed before a later failure in drain mode. The command assumes geotag config members exist and are meaningful.

Test signals: Format selection and JSON output, root-only remove/set, missing/empty group errors, removal blocked by non-empty filesystems, shared-hash delete failure, create-on-set behavior, drain rejection for missing group, drainer flag recomputation for `on`/`off`, disabled placement branch updates, and partial geotag failure handling.
