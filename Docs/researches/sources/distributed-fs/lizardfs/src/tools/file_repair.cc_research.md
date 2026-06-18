# sources/distributed-fs/lizardfs/src/tools/file_repair.cc

Purpose: Implements `lizardfs filerepair`, a mutation tool that asks the master to repair files, optionally only restoring previous versions and never erasing.

Important APIs/types/functions: `file_repair_run`; static `file_repair`; `CLTOMA_FUSE_REPAIR`; `MATOCL_FUSE_REPAIR`; option `-c`; number formatting flags.

Control flow: Parses formatting flags and `-c`, opens a read-write master connection for each file, sends a legacy repair request with inode, uid, gid, and correct-only flag, then expects either a status byte or three counters: not changed, erased, repaired. It prints the repair outcome counts.

State and persistence: Mutates file metadata/chunk state through the master. The usage text warns it may make files readable by filling missing data with zeros unless `-c` is used.

Dependencies and integration: Uses legacy packet packing, `mfserr`, and common master connection helpers. It integrates with master-side repair logic.

Risks and test signals: High operational risk because it can erase/fill data under some conditions. Manual response parsing and server-provided buffer length are additional risks. No direct tests in this subset.
