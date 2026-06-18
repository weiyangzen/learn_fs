# sources/distributed-fs/coda/coda-src/partition/tests/deletemany.c

Purpose: companion helper to decrement/delete a range of synthetic inodes from a test partition.

Flow: initializes local `vicetab`, expects directory, first inode, and last inode. It finds the partition, loops through the inclusive range, calls `idec`, prints each result, and fails on the first nonzero return.

Risks/test signals: exercises link-count decrement and payload/header deletion paths after `createmany`. It returns an uninitialized `rc` on success and uses historical API names. No post-delete scan is performed.
