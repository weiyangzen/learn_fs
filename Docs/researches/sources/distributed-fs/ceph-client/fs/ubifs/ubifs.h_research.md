# sources/distributed-fs/ceph-client/fs/ubifs/ubifs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/ubifs/ubifs.h` is UBIFS's central private header. It connects the on-media ABI to Linux VFS, UBI, crypto, fscrypt, xattr, sysfs, journal, recovery, TNC, LPT, budgeting, and garbage-collection code. The source was read as a complete 2159-line header.

## Important APIs, Types, and Functions

Important constants include implementation and VFS magic values, page/block ratios, sequence and inode watermarks, journal head aliases, budgeting size macros, znode aging thresholds, authentication array sizing, and map/scan/commit return values. Important types include `union ubifs_key`, scan descriptors, `ubifs_inode`, `ubifs_lprops`, LPT cnodes/pnodes/nnodes/heaps, write buffers, buds, journal heads, TNC znodes/zbranches, bulk-read state, node ranges, compressor descriptors, budget requests, orphan records, mount options, budget/stat structures, and the large per-superblock `ubifs_info`.

Inline helpers gate authentication operations (`ubifs_authenticated`, hash descriptor/init/update/final helpers, node hash/HMAC helpers, branch hash access, hash copy, auth-node sizing, encryption fallbacks). The prototype surface covers UBIFS I/O, scan, log, journal, budget, free-space find, TNC, TNC commit/misc, shrinker, commit, master, superblock, replay, GC, orphan, LPT, lprops, file, dir, xattr, security, recovery, ioctl, compressor, sysfs, crypto, and message helpers.

## Control Flow

This file does not implement the main algorithms but defines how all UBIFS modules call each other. Mount code fills `ubifs_info` from the superblock/master/LPT; VFS operations use `ubifs_inode`; writes budget space, create journal nodes, update TNC, and later commit dirty znodes/LPT state; recovery scans logs/buds and reconstructs state; GC and budgeting query LPT/lprops; xattr and security paths enter through the exported xattr prototypes. Authentication inlines short-circuit crypto work when the filesystem is not authenticated.

## State and Persistence Behavior

`ubifs_inode` holds in-memory inode state not directly represented by VFS, including UBIFS dirty state, xattr accounting, compression type, writeback locks, fscrypt state, and shadow size fields. `ubifs_info` is the authoritative mounted-filesystem state: UBI geometry, log pointers, buds, commit state, TNC root and dirty lists, master node, bulk-read buffers, journal heads, LPT geometry and caches, lprops lists/heaps, orphan tracking, GC state, authentication transforms, recovery lists, mount options, stats, and sysfs kobject state. Persistence happens through other modules using the media structs and prototypes defined here.

## Dependencies and Integration Points

The header depends on Linux VFS, locking, UBI, page cache, backing device, security, xattr, sysfs, completion, fscrypt, and crypto APIs, plus `ubifs-media.h`, `debug.h`, `misc.h`, and `key.h`. It is included by most UBIFS implementation files, making it the cross-module contract for mount, read/write, commit, recovery, and user-visible operations.

## Risks and Edge Cases

The largest risk is cross-module invariant drift: lock ordering, shadow size handling, budget accounting, TNC/LPT dirty state, and authentication lengths are all shared through this header. Conditional compilation for xattrs, security, authentication, and encryption changes available APIs and array sizes. `ubifs_info` contains many fields with narrow lock ownership documented in comments; using a field without the intended lock can race commit, GC, shrinker, or recovery. Hash/HMAC helpers return success without doing work on unauthenticated filesystems, so callers must not assume output buffers changed.

## Test Signals

Signals include allmodconfig/allyesconfig build coverage across UBIFS feature combinations, mount/remount/recovery tests, fstests for UBIFS file/xattr/security/encryption paths, power-cut journal replay tests, authentication/HMAC negative tests, TNC/LPT commit and GC stress, shrinker tests under memory pressure, and sysfs/stat accounting checks.
