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
