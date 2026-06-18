# sources/distributed-fs/lizardfs/src/protocol/lock_info.h

Purpose: Defines serializable lock-related constants and structures shared by FUSE lock operations and lock management packets.

Important APIs/types/functions: Lock flags `kUnlock`, `kShared`, `kExclusive`, `kInterrupt`, `kNonblock`, `kRelease`; enum class `lzfs_locks::Type`; serializable class `lzfs_locks::Info`; structs `InterruptData` and `FlockWrapper`.

Control flow: No runtime control flow beyond generated serialization. `FlockWrapper` captures Linux `struct flock` fields except `l_whence`, which FUSE normalizes to `SEEK_SET`.

State and persistence: Represents transient lock state on the wire: owner, inode, session id, range, type, request id, and flock fields. It is not a durable lock table implementation.

Dependencies and integration: Used by `matocl` lock responses including `fuseGetlk`, `manageLocksList`, and likely matching `cltoma` requests. It depends on serialization macros.

Risks and test signals: Wire compatibility depends on fixed integer widths and field ordering. Sign handling for offsets is preserved in `FlockWrapper`, but consumers must interpret zero length and inclusive/exclusive range semantics consistently. No direct tests in this subset isolate lock serialization.
