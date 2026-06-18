## sources/distributed-fs/ceph-client/fs/isofs/rock.c

Purpose: parses Rock Ridge/SUSP system-use fields for POSIX metadata, alternate names, symlinks, relocated directories, timestamps, device numbers, and zisofs compression metadata.

Important types/APIs: `struct rock_state` tracks the current system-use buffer, continuation extent/offset/size, loop count, and inode. Key functions are `get_rock_ridge_filename`, `parse_rock_ridge_inode`, and symlink aops `isofs_symlink_aops`. Helpers include `check_sp`, `setup_rock_ridge`, `rock_continue`, `rock_check_overflow`, and `get_symlink_chunk`.

Control flow: each parser initializes a rock state from the directory record's system-use area, applies a discovered SP skip offset, then loops SUSP records by signature. CE records trigger bounded continuation reads with strict offset/size/volume checks and a 32-continuation limit. Name parsing consumes NM records, ignores dot/dotdot flags, truncates overlong names, and returns `-1` for relocated entries. Inode parsing processes PX/PN/TF/SL/CL/ZF records, optionally retries after XA attributes, and handles relocated directories by reading the relocation target inode. Symlink reads reconstruct SL components into a folio.

State and persistence: no disk writes. Runtime effects include overriding VFS inode mode, nlink, uid/gid, rdev, times, size, first extent, compressed-file format parameters, and symlink page contents. It also updates superblock Rock Ridge detection state and system-use skip offset.

Dependencies and integration points: depends on `rock.h` record layouts, ISO numeric helpers, `iso_date`, `isofs_iget_reloc`, page-cache symlink read, and optional zisofs support. It is central to POSIX semantics on ISOFS.

Risks and test signals: this is a high-risk untrusted-metadata parser. Risks include record overflow, CE loops, out-of-volume extents, symlink buffer overflow, recursive relocation, malformed ER/NM/TF/SL/ZF lengths, and disabling Rock Ridge incorrectly. Test RRIP media with long NM continuations, symlinks with all component flags, relocated directories, device nodes, timestamps, zisofs ZF records, XA-offset media, corrupt CE extents, and unsupported flags.
