## sources/distributed-fs/lizardfs/src/mount/special_inode.cc

Purpose: defines static attributes and inode constants for mount internal special files.

Important data: `InodeMasterInfo::attr` is a read-only file of length 10 or 14 depending on `MASTERINFO_WITH_VERSION`; `InodeStats` and `InodeTweaks` are 0644 files; `InodeOplog` and `InodeOphistory` are 0400 files; `InodeFileByInode` is a 0755 directory. Each namespace also exposes `inode_` from `SPECIAL_INODE_*`.

State and dependencies: immutable process-global constants. Depends on `special_inode_defs`, `lizard_client` attributes, and stats include only indirectly.

Risks: encoded `Attributes` byte arrays are hard to audit and must stay aligned with `attr_to_stat` expectations. Size of dynamic files is mostly zero/static, so readers rely on direct IO and runtime read logic.

Test signals: compare `attr_to_stat` output for every special inode against intended file type, permissions, nlink, and size.
