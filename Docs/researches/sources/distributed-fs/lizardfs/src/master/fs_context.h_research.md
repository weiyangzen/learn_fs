# sources/distributed-fs/lizardfs/src/master/fs_context.h

Purpose: defines `FsContext`, the immutable operation context carrying timestamp, process personality, optional session data, and optional remapped/original user and group credentials for filesystem operations.

Important APIs/types/functions: static factories create contexts for restore/shadow, master without session, master with session, and master with secondary groups. Accessors expose `ts()`, `personality()`, `isPersonalityMaster()`, `isPersonalityShadow()`, `rootinode()`, `sesflags()`, `uid()`, `gid()`, `groups()`, `hasGroup()`, `auid()`, `agid()`, and booleans indicating whether permission checks are possible.

Control flow: operation code receives a context and asserts/accesses only the fields relevant to its path. `canCheckPermissions()` is true only for master contexts that have both session and credential data.

State and persistence behavior: no persistence; it is per-operation in-memory state. Timestamp is used for metadata changelog/checksum operations.

Dependencies/integration: depends on protocol credential containers, session flags from client/master protocol, special inode constants, and master personality. Used broadly by filesystem operation modules.

Risks and test signals: many accessors use `assert()` rather than runtime errors, so release builds can hide misuse only if fields are read incorrectly elsewhere. The overload taking `const GroupsContainer &` uses `std::move(gids)` in the factory call but copies in the constructor, which is harmless but confusing. Tests should cover factory field presence, `hasGroup()`, meta-root contexts, and permission-check gating.
