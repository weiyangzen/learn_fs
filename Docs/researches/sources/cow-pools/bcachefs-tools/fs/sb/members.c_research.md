# File Research: sources/cow-pools/bcachefs-tools/fs/sb/members.c

Implements superblock member-device metadata handling. It reports missing/removed devices referenced by keys, tracks member error string tables, migrates `members_v1` to `members_v2`, resizes v2 entries to the current `struct bch_member`, and writes compatibility v1 copies while old metadata versions require them.

Validation enforces bucket count limits, first-bucket minimums, bucket size relative to block and btree-node size, valid btree bitmap shift, and consistency between freespace initialization and allocation-info features. Text output prints full and short device identity, size, errors, IOPS estimates, bucket geometry, state, data masks, durability, discard/freespace flags, hardware strings, and flush errors.

Runtime sync functions copy atomic device error counters into the superblock and convert member records into `bch_member_cpu` cache entries. It also implements IO error reset persistence, btree-allocation bitmap marking/checking/GC, scheduled bitmap GC heuristics, member slot allocation, deleted-member cleanup, and device identity/rotational-field upgrades.
