## sources/distributed-fs/lizardfs/src/mount/special_inode.h

Purpose: central declaration point for special inode constants, per-namespace attributes, and operation dispatch functions.

Important APIs/types: declares namespace attrs/inode ids for masterinfo, stats, oplog, ophistory, tweaks, and file-by-inode. `InodeStats::sinfo` stores a stats snapshot buffer, length, reset flag, and mutex. Declares `special_lookup`, `special_getattr`, `special_setattr`, `special_open`, `special_read`, `special_write`, and `special_release`.

Integration: included by all special operation implementation files and pulls in `mastercomm`, `masterproxy`, `oplog`, `tweaks`, and client context types.

Risks: broad includes create coupling; dispatch functions assume `ino` is in the special range. `sinfo` uses C allocation and pthread mutex, so open/release symmetry is required.
