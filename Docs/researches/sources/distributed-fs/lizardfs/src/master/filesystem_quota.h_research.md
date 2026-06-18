# sources/distributed-fs/lizardfs/src/master/filesystem_quota.h

Purpose: declares the quota enforcement and accounting helpers used by the master filesystem outside the quota RPC implementation.

Important APIs/types/functions: exposes user/group checks by ids and by `FSNode *`, directory quota checks by node and by move destination/source directories, combined checks, quota usage updates, quota owner removal, and statfs-space adjustment.

Control flow: callers are expected to check quota with `fsnodes_quota_exceeded*()` before applying a metadata change, then call `fsnodes_quota_update()` after the change to keep user/group used counters in sync. Move callers can use the overload that accepts destination and previous directories to skip quotas already covered by a common ancestor.

State and persistence behavior: the header has no state. The declared functions mutate or read `gMetadata->quota_database`; quota persistence is handled by metadata store code, not by this interface.

Dependencies/integration: includes `filesystem_freenode.h` for `FSNode` and `FSNodeDirectory` and `quota_database.h` for `QuotaResource` and `QuotaOwnerType`. It is integrated by node, chunk, snapshot, and restore paths that need quota decisions.

Risks and test signals: the API takes initializer lists of signed deltas, so caller-side unit consistency matters. Tests should assert that every metadata operation that changes inode count or size uses matching check/update pairs, and that the unimplemented `fsnodes_quota_adjust_space()` behavior is accounted for by higher-level statfs tests.
