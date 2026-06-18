# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_rpc.c

## Purpose
`fbnic_rpc.c` manages receive packet classification and action programming: RSS tables/keys/action masks, BMC routing rules, host MAC filters, promiscuous/all-multicast handling, IP TCAM entries, action TCAM entries, TCE TCAM entries, and firmware MACDA synchronization flags.

## Important APIs, Types, And Functions
Public APIs include RSS helpers (`fbnic_reset_indir_tbl()`, `fbnic_rss_key_fill()`, `fbnic_rss_init_en_mask()`, `fbnic_flow_hash_2_rss_en_mask()`, `fbnic_rss_reinit()`, `fbnic_rss_reinit_hw()`, `fbnic_rss_disable_hw()`), BMC helpers (`fbnic_bmc_rpc_init()`, `fbnic_bmc_rpc_all_multi_config()`, `fbnic_bmc_rpc_check()`), MAC/IP sync helpers (`__fbnic_uc_sync()`, `__fbnic_mc_sync()`, `__fbnic_xc_unsync()`, `fbnic_promisc_sync()`, `fbnic_sift_macda()`, `__fbnic_ip4_sync()`, `__fbnic_ip6_sync()`, `__fbnic_ip_unsync()`), and hardware writers (`fbnic_write_macda()`, `fbnic_write_tce_tcam()`, `fbnic_write_ip_addr()`, `fbnic_write_rules()`, `fbnic_clear_rules()`, `fbnic_rpc_reset_valid_entries()`).

## Control Flow
Netdev allocation initializes RSS indirection, key, and hash options. Open calls BMC RPC init and RSS rule init; `fbnic_up()` writes RSS hardware and RX filters. RX mode changes use sync helpers to populate software shadow MACDA entries and set action bits for host/BMC/broadcast/multicast/promisc owners, then write action and address TCAMs.

RSS rule initialization creates 14 action TCAM rules split between host-unicast and xcast flows when BMC is present. Timestamp RX filter state adds TS enable bits to selected flow actions. BMC init consumes firmware BMC MAC capabilities, reserves MACDA indices, and creates action TCAM rules routing BMC traffic. Writers only flush shadow entries whose state has the update bit set; delete states clear hardware and zero software entries, while add/update states write hardware and mark valid.

## State And Persistence
The file manages shadow arrays in `fbnic_dev`: `mac_addr`, `ip_src`, `ip_dst`, `ipo_src`, `ipo_dst`, and `act_tcam`, plus `mac_addr_boundary`, `tce_tcam_last`, and firmware capability flags such as `need_bmc_tcam_reinit` and `need_bmc_macda_sync`. Hardware persistence lives in RPC RSS tables/key registers, MACDA/IP/action TCAMs, and TCE TCAM entries.

## Dependencies And Integration Points
It depends on netdev RSS/hash flags, ethtool hash option semantics, firmware capabilities and MACDA sync mailbox, BMC presence checks, CSR access, hwtstamp configuration from `fbnic_netdev.c`, and RX/TX descriptor constants for DMA hint/timestamp action fields.

## Risks
TCAM state transitions are subtle and shared with BMC rules. MACDA space is partitioned between BMC, broadcast, multicast, host unicast, and promisc entries; overflow silently changes host behavior through promisc/allmulti decisions in netdev code. IP prefix insertion attempts to preserve ordering by mask specificity; mistakes can make later rules unreachable. BMC MACDA sync is deferred by flags, so firmware and hardware may be temporarily inconsistent until service work runs.

## Test Signals
Test RSS table/key writes, hash option to RSS mask conversion, BMC present/absent paths, BMC all-multicast toggles, unicast/multicast overflow into promisc/allmulti, deletion of last owner bit causing TCAM delete, firmware MACDA sync request flagging, IPv4/IPv6 prefix insertion order, timestamp filter rule bits, and crash recovery via `fbnic_rpc_reset_valid_entries()`.
