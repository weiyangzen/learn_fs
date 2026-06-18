# File Research: sources/cow-pools/bcachefs-tools/fs/btree/init.h

## Purpose

`init.h` declares the btree subsystem lifecycle API.

## Public API

- `bch2_fs_btree_exit(struct bch_fs *)`
- `bch2_fs_btree_init_early(struct bch_fs *)`
- `bch2_fs_btree_init(struct bch_fs *)`
- `bch2_fs_btree_init_rw(struct bch_fs *)`

These correspond directly to the lifecycle functions implemented in `init.c`.

## Role

This header lets the broader filesystem mount/recovery/init code sequence btree setup and teardown in phases:

- early structure initialization,
- core btree resource allocation,
- RW resource allocation,
- final cleanup.
