## sources/distributed-fs/lizardfs/src/mount/special_setattr.cc

Purpose: handles setattr attempts on special inodes.

Important APIs: masterinfo rejects all setattr with EPERM. Other implemented special inodes ignore requested changes, return their static attrs with 3600-second timeout, and log an OK entry through `printSetattrOplog`. `special_setattr` dispatches through a 16-entry table.

State and dependencies: no persistent mutation occurs; depends on `client_common`, static special attrs, and operation logging.

Risks: callers may interpret successful setattr on stats/oplog/tweaks/file-by-inode as mutation even though it is ignored. No range check before function-table indexing. Static attr return means requested chmod/chown/truncate has no effect.

Test signals: ensure masterinfo returns EPERM, other special inodes return unchanged attrs, invalid slots return EINVAL, and no dynamic state changes happen.
