# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/init.h

This header declares the btree subsystem lifecycle API.

Core responsibilities:
- Declares `bch2_fs_btree_exit()` for teardown.
- Declares `bch2_fs_btree_init_early()` for early field/list/cache initialization.
- Declares `bch2_fs_btree_init()` for common btree resource allocation.
- Declares `bch2_fs_btree_init_rw()` for read-write btree resources.

Dependencies:
- Assumes `struct bch_fs` is declared by the including context.
- Implemented by `init.c` and called by broader filesystem initialization/shutdown code.

Risk points:
- The API split matters: callers must run early init before common init, and RW init only when writes are permitted.
