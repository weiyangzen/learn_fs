# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd_debugfs.c

## Purpose
This file exposes EFALND debugfs diagnostics for peer-NI metadata, primarily cached GID/QP mappings used for small-NID EFA connection discovery.

## Important APIs, Types, And Functions
`kefalnd_debugfs_init()` creates the `kefalnd` debugfs directory, `peerni_count`, and read-only `gidmap`. `kefalnd_debugfs_exit()` removes the tree. `gidmap_seq_show()` walks `kefalnd.peer_ni` and prints peer address, GID, CM QP number, and QKEY. `LDEBUGFS_SEQ_FOPS_RO(gidmap)` declares the seq-file operations.

## Control Flow
On module init, debugfs entries are created if debugfs allows it. Reading `gidmap` takes RCU read lock, skips output when EFALND is shutdown or uninitialized, starts an rhashtable walk, formats each non-error peer entry, and releases the iterator and RCU lock. Module exit removes the directory recursively.

## State, Persistence, And Dependencies
No separate state is stored except the root `dentry *`. Output reflects live peer-NI rhashtable state and `peer_ni_count`. Data is transient debug state, not persistent configuration. Dependencies include debugfs, seq_file through Lustre debugfs macros, rhashtable iteration, RCU, and EFALND globals.

## Integration Points
The debug entries are initialized from `efalnd.c` module init and removed from module exit. Peer mappings are populated by `efalnd_peerni.c` and consumed by connection setup.

## Risks
The rhashtable walk runs under RCU and reads peer fields without taking each peer's rwlock, so it is diagnostic best-effort and can observe concurrent updates. `debugfs_create_atomic_t()` is called before global startup initializes peer count for first NI, but the atomic object is global and zeroed at module init. Output address formatting uses `remote_nid_addr` byte shifts and must match small-NID encoding expectations.

## Test Signals
Tests should load/unload with debugfs enabled and disabled, read empty `gidmap`, populate peer mappings through TCP discovery, verify `peerni_count`, and stress reads while peer entries are inserted, updated, and freed.
