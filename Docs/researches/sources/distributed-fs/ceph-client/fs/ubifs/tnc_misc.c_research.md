# sources/distributed-fs/ceph-client/fs/ubifs/tnc_misc.c

## Purpose
`tnc_misc.c` contains shared TNC support code that does not belong to one logical TNC submodule. It provides znode traversal, zbranch binary search, subtree destruction, znode loading from flash, and leaf-node reads with key/hash validation.

## Important APIs, Types, And Functions
Traversal helpers are `ubifs_tnc_levelorder_next()`, `ubifs_tnc_postorder_first()`, and `ubifs_tnc_postorder_next()`. `ubifs_search_zbranch()` performs binary search inside one znode and returns exact match or closest-left slot. Destruction helpers are `ubifs_destroy_tnc_subtree()` and `ubifs_destroy_tnc_tree()`, used by the shrinker and unmount cleanup.

`read_znode()` reads and validates one on-flash index node into an allocated znode: it checks hash, child count, level, branch address bounds, key types, leaf target lengths, and sorted key order. `ubifs_load_znode()` allocates a znode, calls `read_znode()`, increments clean-znode counters, attaches parent/iip/time metadata, and stores the pointer in the zbranch. `ubifs_tnc_read_node()` reads a leaf node either through an overlapping write buffer or normal media IO, validates the key, and checks the node hash.

## Control Flow
Lookup code in `tnc.c` calls `ubifs_search_zbranch()` while descending. When a child znode is absent from memory, it calls `ubifs_load_znode()`, which reads the index node from the branch's LEB/offset/length, validates it, attaches it to the parent branch, and records it as a clean znode. Reclaim and teardown use traversal helpers to walk and free znodes without touching cached leaf nodes directly.

## State And Persistence
This file reads persistent index and leaf nodes but does not write flash. It mutates in-memory zbranch pointers, znode parent/index metadata, access timestamps, and clean-znode counters. `ubifs_destroy_tnc_tree()` subtracts the destroyed clean count from the global counter and clears `c->zroot.znode`.

## Dependencies And Integration Points
It depends on `ubifs_read_node()`, `ubifs_read_node_wbuf()`, `ubifs_get_wbuf()`, key helpers, node hash helpers, znode flag helpers, and the global shrinker counter from `shrinker.c`. The main TNC lookup/mutation code relies on znode loading and searching here; the shrinker relies on level-order traversal and subtree destruction; commit and unmount cleanup depend on postorder destruction semantics.

## Risks And Edge Cases
Index-node validation is a security boundary for malformed media: bad branch addresses, invalid key types, impossible child counts, bad target lengths, unsorted keys, and non-hash duplicate keys must reject the mount/read path. Clean counter increments must match later destruction or shrinker accounting drifts. `ubifs_tnc_read_node()` must read through write buffers when a node is still buffered in a bud; normal media reads would otherwise miss recent journal data. Traversal code must handle sparse loaded subtrees because not every child znode is resident.

## Test Signals
Tests should include loading valid and malformed index nodes, hash mismatch detection, branch bounds checks, sorted-key enforcement including duplicate hash keys, lazy load during lookup, write-buffer-overlapping leaf reads, subtree destruction counts, full TNC destruction at unmount, shrinker level-order traversal over partially loaded trees, and postorder traversal over sparse child pointers.
