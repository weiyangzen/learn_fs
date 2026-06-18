# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/esw/bridge_debugfs.c

Purpose: Provides debugfs visibility into bridge offload FDB entries. It creates a per-eswitch `bridge` debugfs directory and a per-Linux-bridge `fdb` seq_file.

Important APIs/types/functions: `mlx5_esw_bridge_debugfs_offloads_init()` and cleanup manage the top-level debugfs directory. `mlx5_esw_bridge_debugfs_init()` and cleanup manage each bridge directory and `fdb` file. Seq operations iterate `bridge->fdb_list` and print device, MAC, VLAN, cached packets/bytes/lastuse, and flags.

Control flow: Opening the seq file starts under `rtnl_lock()`, returns a header token for position zero, iterates the FDB list using seq list helpers, queries cached counter values with `mlx5_fc_query_cached_raw()`, and releases RTNL in `stop`. Cleanup uses recursive debugfs removal.

State and persistence: Stores dentry pointers in `br_offloads->debugfs_root` and `bridge->debugfs_dir`. It does not own FDB entries but reads their list and counters while protected by RTNL.

Dependencies and risks: Depends on debugfs, seq_file, RTNL serialization, bridge private structs, and flow counter caching. Risks include exposing stale data if entries are mutated outside RTNL or dereferencing entries whose counters have been destroyed. Test signals include `debugfs` file creation/removal with bridge lifecycle and sensible FDB output after traffic.
