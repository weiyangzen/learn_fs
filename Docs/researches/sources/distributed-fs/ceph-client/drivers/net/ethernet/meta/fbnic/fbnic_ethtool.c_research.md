# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_ethtool.c

## Purpose

`fbnic_ethtool.c` implements the netdev `ethtool_ops` surface for FBNIC. It exposes driver/firmware info, register dumps, coalescing, ring sizes, channel counts, RSS key/table/context management, RSS hash-field selection, RXNFC classifier rules, statistics, self-tests, timestamping, module EEPROM reads, PFC prevention tunables, pause/FEC/PHY/MAC/RMON stats, and link settings delegated to phylink. It is the main userspace control surface for changing live queue topology and receive steering state.

## Important APIs, Types, And Functions

The exported entry point is `fbnic_set_ethtool_ops()`, assigning `fbnic_ethtool_ops` to the netdev. `struct fbnic_stat` describes ethtool string, size, and offset for stats extraction. Static stats arrays cover fixed hardware stats, RXB enqueue/fifo/dequeue groups, per-Rx-queue hardware counters, and XDP queue counters. Self-test strings map to register, MSI-X, and mailbox tests.

Configuration callbacks include `fbnic_get_coalesce()`/`fbnic_set_coalesce()`, `fbnic_get_ringparam()`/`fbnic_set_ringparam()`, `fbnic_get_channels()`/`fbnic_set_channels()`, `fbnic_get_rxfh()`/`fbnic_set_rxfh()`, RXFH context create/modify/remove, `fbnic_get_rss_hash_opts()`/`fbnic_set_rss_hash_opts()`, and RXNFC get/set helpers. Live ring/channel changes use clone helpers (`fbnic_clone_create()`, `fbnic_clone_swap_cfg()`, `fbnic_clone_swap()`, `fbnic_clone_free()`) to allocate a replacement configuration before stopping the current datapath.

Classifier helpers include `fbnic_get_cls_rule_all()`, `fbnic_get_cls_rule()`, `fbnic_set_cls_rule_ins()`, `fbnic_set_cls_rule_del()`, `fbnic_clear_nfc_macda()`, and `fbnic_clear_nfc_ip_addr()`. They translate ethtool flow specs to/from FBNIC action TCAM, MAC DA TCAM, and IP TCAM state.

## Control Flow

Simple getters read cached `struct fbnic_net` or `struct fbnic_dev` state and format ethtool output. Stats collection calls `fbnic_get_hw_stats()`, snapshots `fbd->hw_stats` under its spinlock, then appends XDP ring counters with per-ring u64 stats synchronization.

Coalescing setters validate rx/tx usec and Rx frame limits against CSR field maxima, update `fbn` fields, and if the netdev is running, reprogram every NAPI vector with `fbnic_config_txrx_usecs()` and `fbnic_config_rx_frames()`.

Ring and channel setters have a two-path model. If the device is down, they update sizes/counts directly. If running, they allocate a clone, set requested config on the clone, allocate NAPI vectors/resources, stop the current datapath with `fbnic_down_noidle()`, wait for queues idle, set netif queue counts, flush old rings, swap clone and original pointers/config, bring the original netdev back up, and free old resources through the clone. Error paths restart the original stack and free partial clone resources.

RXNFC insertion only accepts `RX_CLS_LOC_ANY`, finds an unused action TCAM slot, rejects overwrites, translates supported IPv4/IPv6 TCP/UDP/user and Ethernet flows, allocates referenced MAC/IP TCAM entries through sync helpers, fills action TCAM value/mask words and destination bits, marks the rule `FBNIC_TCAM_S_UPDATE`, and writes rules/MAC/IP tables if running. Deletion marks the action TCAM for delete, unsyncs referenced MAC/IP entries, and writes updated hardware tables if running.

RSS key/table setters validate Toeplitz hash only, update packed driver key/table state, and reinitialize RSS hardware if live. Hash-field setters validate allowed RXH bits by flow category and refresh RSS/rules if live.

## State And Persistence

All state is in memory and device hardware. `struct fbnic_net` stores queue sizes, queue counts, NAPI count, coalescing values, HDS threshold, RSS key, RSS indirection tables, RSS flow hash fields, XDP program/rings, and timestamp stats. `struct fbnic_dev` stores hardware stats and TCAM arrays. Live setters persist changes to hardware registers/TCAM/RSS tables when the netdev is running; otherwise changes remain cached until open/reinit. No filesystem persistence exists.

## Dependencies And Integration Points

Dependencies include Linux ethtool netlink and classic APIs, netdevice, PCI, IPv6 helpers, phylink callbacks, FBNIC netdev lifecycle, Tx/Rx resource allocation, RSS/RPC/TCAM writers, hardware stats, firmware mailbox QSFP EEPROM reads, PTP clock, MAC pause/FEC/stats helpers, and register/MSI-X/mailbox self-tests. This file is tightly coupled to `fbnic_netdev.h`, `fbnic_txrx.h`, `fbnic_hw_stats.*`, `fbnic_fw.*`, `fbnic_mac.h`, `fbnic_rpc.c`, and phylink/time support.

## Risks And Edge Cases

Live queue reconfiguration is the highest-risk path: it must allocate all replacement resources before stopping traffic and must not fail after the "nothing can fail" point. RSS table and queue count changes interact; channel changes reset the indirection table. RXNFC insertion mutates auxiliary MAC/IP TCAM state before final action TCAM installation and must roll back newly added IP entries on allocation failure. IPv6 outer-IP handling uses `IPPROTO_IPV6` as a special user-flow signal. Overwrite is intentionally rejected until old referenced TCAM cleanup is implemented. The stats extractor assumes fields are u64-sized where registered; wrong `fbnic_stat` metadata would read invalid offsets. Module EEPROM reads only support I2C address `0x50` and rely on firmware response validation.

## Test Signals

Useful tests include `ethtool -i`, register dump, coalesce get/set including max-boundary failures, ring resizing while down and while traffic is running, channel resizing with queue-count/RSS reset checks, stats string/count alignment, XDP stats with absent rings, RXFH key/table/context create/modify/remove, RSS hash-field validation, RXNFC insert/list/get/delete for supported flow types and invalid masks/queues, offline self-tests, timestamp stats/info, QSFP EEPROM reads and timeout handling, pause/FEC/MAC/PHY/RMON stats. No executable tests were run for this research item.
