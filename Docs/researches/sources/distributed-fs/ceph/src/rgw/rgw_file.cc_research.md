# sources/distributed-fs/ceph/src/rgw/rgw_file.cc

## Purpose
Implements the C librgw file API that presents RGW buckets and objects as a POSIX/NFS-like filesystem. It maps mount, lookup, readdir, create, mkdir, unlink, rename, read, write, stat, and xattr operations onto RGW frontend requests and SAL objects.

## Important APIs, Types, And Functions
Internal methods on `RGWLibFS` implement object discovery and mutation: `stat_bucket()`, `stat_leaf()`, `fake_leaf()`, `read()`, `readlink()`, `unlink()`, `rename()`, `mkdir()`, `create()`, `symlink()`, `getattr()`, `setattr()`, xattr operations, `update_fh()`, `close()`, and `gc()`. `RGWFileHandle` methods implement encoding/decoding Unix attrs, readdir state, writes, close, invalidation, and cache reclamation. The `extern "C"` section exports `rgw_mount*`, `rgw_umount`, `rgw_statfs`, `rgw_lookup*`, `rgw_fh_rele`, `rgw_getattr`, `rgw_setattr`, `rgw_open`, `rgw_close`, `rgw_readdir*`, `rgw_read*`, `rgw_write*`, `rgw_commit`, and xattr APIs.

## Control Flow
Mount allocates `RGWLibFS`, authorizes access keys, registers the FS with the lib frontend process, and exposes the root handle. Lookup distinguishes root bucket lookup from object lookup. Bucket and object stats are fetched through synthetic RGW op requests, then materialized as cached `RGWFileHandle`s. Readdir issues either `RGWListBucketsRequest` or `RGWReaddirRequest`, updates link counts, markers, and invalidation events. Writes start a continued `RGWWriteRequest`, stream contiguous chunks through `exec_continue()`, and complete on close or stateless write timeout.

## State And Persistence Behavior
Persistent file metadata is stored as RGW object attrs `RGW_ATTR_UNIX_KEY1` and `RGW_ATTR_UNIX1`; etag and ACL attrs are preserved across setattr/write flows. `fh_key` values are deterministic hashes of tenant/bucket/object names. `RGWLibFS` maintains an intrusive FH cache plus LRU, close flags, invalidate callback, queued readdir events, and a write timer. Directory entries are not persistent handles by themselves; placeholder directory objects use trailing slash names.

## Dependencies And Integration Points
This file is deeply integrated with RGW REST/op classes, SAL driver/user/bucket/object APIs, `RGWLibFrontend`, RADOS cluster stat ops, xattrs, compression, checksums, perf counters, Ceph timers, and Ganesha-style librgw file structs from `include/rados/rgw_file.h`.

## Risks
Several operations are explicitly non-atomic: rename is copy-then-delete, stat of leaf directory/file can require multiple round trips, and fast attrs can synthesize handles from readdir data. Initial writes must be contiguous from offset zero unless stateless V3 overlap handling applies. `rgw_truncate()`, `rgw_fsync()`, and vector read/write are effectively unsupported or stubs. `tmp_fh` decode comments note unsound historical versioning logic. Xattrs are rejected on root/buckets, and exposed attrs are special-cased.

## Test Signals
Coverage should exercise mount authorization, bucket root lookup, object and directory lookup with/without fast attrs, create/mkdir/symlink conflicts, delete non-empty directories, copy-delete rename failure modes, contiguous and non-contiguous writes, close-triggered completion, readdir marker continuation, namespace GC invalidation callback, xattr prefix/exposed attr behavior, statfs cluster stats, and stale/deleted handle returns.
