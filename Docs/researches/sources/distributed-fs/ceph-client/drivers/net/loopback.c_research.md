# sources/distributed-fs/ceph-client/drivers/net/loopback.c

Purpose: Implements the per-network-namespace loopback netdevice and the global `blackhole_netdev` used for expired or discard destinations. Loopback reinjects transmitted packets into receive processing with local statistics, while blackhole drops packets through transmit and neighbor output paths.

Important APIs and functions: `loopback_xmit()` timestamps, scrubs, forces dst references, converts Ethernet protocol metadata, and calls `__netif_rx()`. `dev_lstats_read()` is exported for reading per-CPU lightweight stats. `loopback_get_stats64()` mirrors loopback RX and TX counters from the same local stats. `gen_lo_setup()` initializes common loopback-like device fields and is reused for `blackhole_netdev_setup()`. `loopback_net_init()` allocates and registers one `lo` device per net namespace. `blackhole_netdev_init()` allocates and activates the global dummy discard device.

Control flow: pernet init allocates `lo` with predictable name, binds it to the namespace, registers it, verifies `LOOPBACK_IFINDEX`, and stores it as `net->loopback_dev`; init-net failure panics because networking cannot proceed without loopback. Transmit uses `NETDEV_TX_OK` regardless of upper-layer reinjection result, with stats incremented only on successful receive enqueue. The blackhole device is initialized at `device_initcall`, scheduler-activated under the init-net RTNL lock, and marked up/running without normal registration.

State and persistence: Loopback stats use `NETDEV_PCPU_STAT_LSTATS` and are read with `u64_stats_fetch_begin/retry`. `loopback_dev_free()` clears the namespace's loopback pointer. `blackhole_netdev` is a global exported pointer, not per namespace, and intentionally persists for the boot lifetime.

Dependencies and integration: Uses core netdevice allocation/registration, pernet operations registered from `net/core/dev.c`, skb timestamp/dst helpers, Ethernet header ops, ethtool timestamp info, scheduler activation, and neighbor output hooks.

Risks and test signals: Risks are fundamental networking boot failure, incorrect skb timestamp/dst handling before reinjection, stats races, and the unusual manually activated blackhole device lifecycle. Test namespace creation/destruction, loopback traffic counters, packet timestamp clearing, dst ref behavior, init-net failure handling where injectable, and blackhole route/neighbour drops with ratelimited warnings.
