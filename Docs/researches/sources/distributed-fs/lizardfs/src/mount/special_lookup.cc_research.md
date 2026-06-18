## sources/distributed-fs/lizardfs/src/mount/special_lookup.cc

Purpose: implements lookup responses for internal special inode directory entries.

Important APIs: one static lookup per special inode fills `EntryParam` with inode id, 3600-second attr/entry timeouts, stat-converted static attrs, increments `OP_LOOKUP_INTERNAL`, builds attrstr, and writes an operation log entry. `special_lookup` dispatches through a 16-entry table.

State and dependencies: no mutable state besides stats/oplog. Depends on `client_common` and `special_inode`.

Risks: indexes `funcs[ino - SPECIAL_INODE_BASE]` without range validation. The table comments contain repeated/misaligned slot labels in some related files; actual initializer position is what matters. Name is only logged, not validated here.

Test signals: lookup each supported internal name through caller path, verify returned inode/attrs/timeouts and stats increment. Invalid reserved slots should throw EINVAL.
