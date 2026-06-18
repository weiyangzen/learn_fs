<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_mounts_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_mounts_command.cc

## Purpose
Implements `lizardfs-admin list-mounts`, reporting active client sessions/mounts and selected session policy flags.

## Important APIs, Types, and Functions
Defines local `OperationStats`, a serializable `MountEntry` class through `SERIALIZABLE_CLASS_*` macros, and command methods. `MountEntry` contains session ID, peer IP, version, mount info, root path, flags, root/mapall IDs, goal/trash limits, and current/hour operation stats.

## Control Flow, State, and Persistence
`run` sends legacy `CLTOMA_SESSION_LIST` with stats enabled, expects `MATOCL_SESSION_LIST`, skips the initial `uint16_t` stats count, deserializes mount entries, sorts by `sessionId`, derives booleans from `SESFLAG_*`, computes whether goal/trash limits are meaningful, and prints normal or porcelain output. Verbose output adds goal and trash-time constraints. It is read-only session-state inspection.

## Dependencies and Integration Points
Depends on MooseFS serialization macros, `MooseFsString`, `MooseFSVector`, `GoalId`, session flag constants, version formatting, IP conversion, and master session-list protocol.

## Risks and Test Signals
Risks include local serialization shape needing to match master protocol exactly, operation stats being deserialized but not printed, porcelain output not escaping mount info/path, goal/trash validity heuristics, and path/info fields containing spaces. Test signals are multiple sessions sorted by ID, every session flag, invalid/valid goal limits, trash time defaults, verbose and porcelain modes, and protocol compatibility across client versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_mounts_command.cc -->
