## sources/distributed-fs/lizardfs/src/mount/special_getattr.cc

Purpose: implements `getattr` dispatch for LizardFS special inodes.

Important APIs: namespace-local `getattr` functions for `MASTERINFO`, `STATS`, `OPLOG`, `OPHISTORY`, `TWEAKS_FILE`, and `FILE_BY_INODE_FILE` convert static `Attributes` into `struct stat`, increment stats, format attr strings, log to oplog, and return `AttrReply` with 3600-second timeout. `special_getattr` indexes a 16-entry function table by `ino - SPECIAL_INODE_BASE`.

State and dependencies: uses static attrs from `special_inode.cc`, `client_common` conversion helpers, `stats`, and `oplog`.

Risks: no bounds check before indexing the function array; callers must pass a valid special inode. Unimplemented table entries throw EINVAL after logging. All attrs are static and do not reflect dynamic size of stats/oplog/tweaks.

Test signals: verify every defined special inode maps to correct mode/type, invalid reserved slots return EINVAL, and logged attr strings match expected stat conversion.
