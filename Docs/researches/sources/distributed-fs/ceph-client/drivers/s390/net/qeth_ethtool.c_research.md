# sources/distributed-fs/ceph-client/drivers/s390/net/qeth_ethtool.c

Purpose: provides the qeth `ethtool_ops` implementation for driver information, link settings, queue stats, channel counts, IQD transmit coalescing, timestamp capability, ring parameters, and RX copybreak tuning.

Important APIs and functions: `qeth_ethtool_ops` wires callbacks for stats, strings, channels, coalescing, tunables, and link ksettings. `qeth_stats` descriptors map display names to offsets in `struct qeth_card_stats` and `struct qeth_out_q_stats`. Helpers `qeth_add_stat_data()` and `qeth_add_stat_strings()` build ethtool arrays. Coalescing flows through `__qeth_set_coalesce()`, `qeth_set_coalesce()`, `qeth_get_per_queue_coalesce()`, and `qeth_set_per_queue_coalesce()`.

Control flow: stats count is computed as card stats plus per-output-queue stats. Stats reads copy current u64 values from card and queue structures. Channel changes validate nonzero queue counts, enforce hardware queue limits, reject priority queueing conflicts, and impose IQD minimum/downgrade rules before calling `qeth_set_real_num_tx_queues()`. Link mode reporting builds supported and advertised bitmaps from cached link speed, port, duplex, and link mode.

State and persistence: no standalone persistence. It reads and updates live qeth state: queue coalescing fields, `qeth_priv.rx_copybreak`, wanted TX queue count, link info, and queue statistics. `WRITE_ONCE()` is used for coalescing and copybreak values that can be read concurrently by datapath code.

Dependencies and integration: integrates with Linux ethtool netlink/ioctl paths, qeth qdio output queues, netdev queue configuration, and standard ethtool link-mode helpers. IQD-only features return `-EOPNOTSUPP` on non-IQD devices.

Risks: queue count changes can disrupt flow mapping, especially IQD multicast queue conventions, so downgrades while running are blocked. Coalescing rejects both knobs being zero to avoid disabling all wakeup triggers. Stats use offsets into structures; changes to stats structure type or field width must keep the u64 assumption valid.

Test signals: `ethtool -S` string/count alignment, per-queue stat ordering across queue counts, `ethtool -L` failures for zero/too many queues and priority queueing, IQD coalescing global and per-queue set/get, RX copybreak set/get, and link-mode output for TP/fibre speeds and unknown ports.
