# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/hwtstamp.c

Purpose: implements DSA hardware timestamping for mv88e6xxx PTP-capable switches, including ethtool timestamp capabilities, per-port hwtstamp configuration, RX/TX skb timestamp matching, and PTP hardware setup.

Important APIs/types/functions: DSA entry points are `mv88e6xxx_get_ts_info()`, `mv88e6xxx_port_hwtstamp_set/get()`, `mv88e6xxx_port_rxtstamp()`, `mv88e6xxx_port_txtstamp()`, `mv88e6xxx_hwtstamp_work()`, setup/free, and per-family global/port enable/disable helpers. Internal state is `struct mv88e6xxx_port_hwtstamp`, RX queues, `tx_skb`, sequence IDs, and state bits.

Control flow: configuration clears the enabled bit, validates tx/rx filters, updates global/port PTP hardware enable counts under the register lock, then enables data-path checks. RX path classifies PTP, queues skb in arrival0/arrival1 queue, and schedules PTP worker. Worker reads latched timestamp blocks, matches sequence IDs, converts raw cycles through `chip->tstamp_tc`, stamps skbs, and releases them. TX path clones one skb, waits for departure timestamp, validates status/sequence, completes or drops on timeout/error.

State and persistence: runtime state includes per-port queues, config, enabled/TX-in-progress bits, `enable_count`, cloned TX skb, and timecounter. Hardware timestamp latches are transient.

Dependencies/integration: depends on Global2 AVB ops, PTP clock worker, `ptp_classify_raw()`, DSA RX/TX hooks, and `ptp_ops` register metadata.

Risks: `enable_count` is decremented on every disable path and can underflow if disabling an already disabled port. Only one TX timestamp per port is supported; excess timestampable packets are ignored. RX hardware holds one timestamp per arrival register, so queued extras may be unstamped.

Test signals: `ethtool -T`, `SIOCSHWTSTAMP` filter validation, ptp4l L2/L4 event traffic, TX timeout recovery, sequence mismatch warnings, RX PDelay response path using arrival1, and 6341 MAC timestamp mode setup.
