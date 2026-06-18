<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/quota/system_id.rs -->
# sources/distributed-fs/beegfs-rust/mgmtd/src/quota/system_id.rs

Purpose: provides iterators over local system user and group IDs for quota collection.

Important APIs/types/functions: `user_ids()` returns `UserIDIter`, wrapping libc `setpwent/getpwent/endpwent`. `group_ids()` returns `GroupIDIter`, wrapping `setgrent/getgrent/endgrent`. A global `OnceLock<tokio::sync::Mutex<()>>` serializes all iteration.

Control flow: each async constructor acquires the global mutex, resets libc enumeration, and returns an iterator holding the guard. The iterator calls libc on each `next()` and drops by ending enumeration.

State and persistence: no persistence. It reads process-local libc/NSS user and group databases and holds a global async mutex during iteration.

Dependencies and integration points: used by `quota::fetch_and_update()` when configured minimum system user/group IDs are set.

Risks: libc enumeration APIs use global state; the mutex protects this module but cannot protect unrelated code calling `setpwent/getpwent` or group equivalents. Iteration can block other tasks waiting for system IDs until the iterator drops.

Test signals: multi-thread Tokio tests spawn 16 concurrent readers for users and groups and assert all collected lists are equal, guarding the mutex serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/mgmtd/src/quota/system_id.rs -->
