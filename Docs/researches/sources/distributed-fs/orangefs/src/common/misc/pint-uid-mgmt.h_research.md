# sources/distributed-fs/orangefs/src/common/misc/pint-uid-mgmt.h

Purpose: Defines the UID management statistics structures, constants, encoding metadata, and API prototypes for OrangeFS UID activity tracking.

Important APIs and types: `UID_MGMT_MAX_HISTORY` fixes the history to 25 entries and `UID_HISTORY_HASH_TABLE_SIZE` sets the lookup table size. `PVFS_uid_info_s` stores a uid, count, first timestamp, and latest timestamp and has generated encode/decode descriptors. `PINT_uid_mgmt_s` wraps stats with LRU and hash links. `IN_UID_HISTORY(current, oldest)` compares timeval values in microseconds. Public functions initialize/finalize the subsystem, add a UID occurrence, and dump all stats.

Control flow and integration: Server paths call `PINT_add_user_to_uid_mgmt()` when recording per-user activity and management/reporting paths call `PINT_dump_all_uid_stats()` to export the fixed-size array. Encoding metadata allows stats to be serialized using OrangeFS request protocol helpers.

State and persistence behavior: The header declares types for in-memory history only. Persistent behavior is absent; the history is bounded and reset on subsystem initialization.

Dependencies and risks: Depends on quicklist, quickhash, PVFS uid/time types, and endecode macro availability. The `IN_UID_HISTORY` macro performs floating-point-like multiplication through `1e6`, which may introduce type surprises; integer constants would be safer. Test signals include encode/decode of `PVFS_uid_info_s`, fixed-size dump compatibility, and boundary timestamp comparisons.
