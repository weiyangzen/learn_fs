# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_selftests.c

Purpose: ethtool offline selftests for STMMAC hardware. It synthesizes loopback packets, validates received frames, toggles MAC/PHY loopback, and exercises filters, VLAN, TC offloads, ARP offload, jumbo frames, split header, and TBS/ETF.

Important APIs and functions: `struct stmmac_packet_attrs` describes generated test frames. `stmmac_test_get_udp_skb()` and `stmmac_test_get_arp_skb()` create packets. `__stmmac_test_loopback()` registers a packet handler, transmits with `dev_direct_xmit()`, and waits for completion. Test functions cover MAC/PHY loopback, MMC, EEE, hash/perfect filters, multicast/unicast filters, flow control, RSS, VLAN/double-VLAN filtering, RX parser, SA insertion/replacement, VLAN insertion, L3/L4 flower filters, ARP offload, jumbo, multichannel jumbo, split-header, and TBS. `stmmac_selftest_run()`, `stmmac_selftest_get_strings()`, and `stmmac_selftest_get_count()` are exported to ethtool.

Control flow: `stmmac_selftest_run()` requires offline mode and carrier, clears results, drains queues, iterates the static test table, enables the requested PHY/MAC loopback mode, runs each test, stores return codes, marks failure for errors other than `-EOPNOTSUPP`, and disables loopback. Individual tests configure state, send frames, validate headers/magic IDs/counters, then restore state.

State and persistence: state is mostly temporary, but tests mutate device state while running: address lists, promiscuity, VLAN IDs, loopback, RSS enablement, TC filters, ARP offload, source-address replacement, ETF/TBS, stopped RX queues, and `stmmac_test_next_id`. Cleanup paths restore these settings.

Dependencies and integration: ethtool hooks, PHY APIs, packet handlers, netdev address/VLAN APIs, TC offload/action APIs under `CONFIG_NET_CLS_ACT`, STMMAC hardware operations, and PTP time for TBS.

Risks and test signals: tests are invasive and offline-only with valid carrier. Hardware capability checks produce `-EOPNOTSUPP`. Timeouts can be flaky on slow or congested systems. The ethtool selftest output is itself the strongest feature-level test signal for the files in this group.
