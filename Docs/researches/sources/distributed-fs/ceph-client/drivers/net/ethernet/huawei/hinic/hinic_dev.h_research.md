# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_dev.h

Defines the central HiNIC netdev runtime state. `struct hinic_dev` stores netdev/hwdev pointers, queue counts/depths, flags, management lock, VLAN bitmap, RX mode work, TX/RX queue arrays, RSS template/hash/key/indirection state, interrupt coalescing arrays, SR-IOV info, loopback test buffers, debugfs dentries, devlink pointer, and link extended state booleans.

Other key definitions are `HINIC_DRV_NAME`, MTU limits, `enum hinic_flags`, `struct hinic_rx_mode_work`, `struct hinic_rss_type`, `enum hinic_rss_hash_type`, `struct hinic_intr_coal_info`, debug types, and `struct hinic_devlink_priv`. There is no executable flow, but all netdev, ethtool, devlink, debugfs, SR-IOV, TX/RX, and workqueue code shares this layout.

Risks are lifecycle mismatches across subsystems, non-atomic flag updates in mixed contexts, and loopback/debugfs pointer validity. Test probe/open/close/remove, ethtool operations, debugfs lifecycle, devlink reporters, SR-IOV, and diagnostics.
