# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_fs.c

## Purpose
`ipoib_fs.c` implements optional debugfs visibility for IPoIB multicast groups and path records when debug support is enabled. It provides read-only seq_file views under a driver-level `ipoib` debugfs directory.

## Important APIs, Types, And Functions
`format_gid()` renders an InfiniBand GID as colon-separated 16-bit words. The multicast seq operations call `ipoib_mcast_iter_init()`, `ipoib_mcast_iter_next()`, and `ipoib_mcast_iter_read()` to show MGID, creation time, queue length, completion, and send-only state. The path seq operations call `ipoib_path_iter_init()`, `ipoib_path_iter_next()`, and `ipoib_path_iter_read()` to show DGID, completion, DLID, SL, and rate. `ipoib_create_debug_files()` creates per-netdev `<name>_mcg` and `<name>_path` files; `ipoib_delete_debug_files()` removes them; `ipoib_register_debugfs()` and `ipoib_unregister_debugfs()` manage the root directory.

## Control Flow And State
The file does not own driver state; it snapshots state through iterator helpers implemented in `ipoib_main.c` and `ipoib_multicast.c`. Each seq start allocates an iterator and advances to the requested offset. Iterators are freed when next reaches EOF; the stop methods intentionally do nothing. Per-device dentry pointers are stored in `priv->mcg_dentry` and `priv->path_dentry`.

## Dependencies And Integration Points
Dependencies are debugfs, seq_file, and the debug-only iterator APIs declared in `ipoib.h`. Registration is triggered by module init and netdev notifier events in `ipoib_main.c`, creating/removing files as IPoIB netdevices register, rename, and unregister.

## Risks And Test Signals
Risk is mostly diagnostic correctness and iterator lifetime. Because stop does not free the current iterator, the next/start EOF paths are relied on to free allocations; review should verify seq_file lifetime behavior for early close paths. Test signals include building with `CONFIG_INFINIBAND_IPOIB_DEBUG`, inspecting `/sys/kernel/debug/ipoib/*_mcg` and `*_path`, renaming netdevices, and unregistering devices while debugfs files are open.
